import asyncio
import contextlib
import io
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock

import httpx
from openai import NotFoundError

from store import cleanup, ingest, load_state, ready_store_id, save_state, StoreState


def fake_client():
    return SimpleNamespace(
        vector_stores=SimpleNamespace(
            create=AsyncMock(return_value=SimpleNamespace(id="vs_lab")),
            delete=AsyncMock(return_value=SimpleNamespace(deleted=True)),
            files=SimpleNamespace(
                create_and_poll=AsyncMock(
                    return_value=SimpleNamespace(status="completed", last_error=None)
                )
            ),
        ),
        files=SimpleNamespace(
            create=AsyncMock(side_effect=[SimpleNamespace(id=f"file-{i}") for i in range(3)]),
            delete=AsyncMock(return_value=SimpleNamespace(deleted=True)),
        ),
    )


class StoreTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "state.json"
        self.client = fake_client()
        self.output = io.StringIO()
        self.enterContext(contextlib.redirect_stdout(self.output))

    async def test_ingest_waits_for_every_file_and_records_attributes(self):
        state = await ingest(self.client, self.path)
        self.assertEqual(ready_store_id(self.path), "vs_lab")
        self.assertEqual(state.file_ids, ["file-0", "file-1", "file-2"])
        calls = self.client.vector_stores.files.create_and_poll.await_args_list
        self.assertEqual(
            [call.kwargs["attributes"] for call in calls],
            [{"category": category} for category in ("delivery", "returns", "support")],
        )
        self.assertTrue(all(call.kwargs["vector_store_id"] == "vs_lab" for call in calls))
        self.assertEqual(
            self.client.vector_stores.create.call_args.kwargs["expires_after"],
            {"anchor": "last_active_at", "days": 1},
        )
        self.assertTrue(all(call.kwargs["purpose"] == "assistants"
                            for call in self.client.files.create.await_args_list))

    async def test_failed_or_cancelled_indexing_preserves_uploaded_id(self):
        for status in ("failed", "cancelled"):
            with self.subTest(status=status):
                client = fake_client()
                client.vector_stores.files.create_and_poll.return_value = SimpleNamespace(
                    status=status, last_error="invalid_file"
                )
                with self.assertRaisesRegex(RuntimeError, status):
                    await ingest(client, self.path)
                state = load_state(self.path)
                self.assertEqual(state.file_ids, ["file-0"])
                self.assertFalse(state.ready)
                await cleanup(client, self.path)

    async def test_indexing_timeout_keeps_partial_state(self):
        async def pending(**kwargs):
            await asyncio.Future()

        self.client.vector_stores.files.create_and_poll.side_effect = pending
        with self.assertRaises(TimeoutError):
            await ingest(self.client, self.path, poll_timeout=0.01)
        self.assertEqual(load_state(self.path).file_ids, ["file-0"])
        self.assertFalse(load_state(self.path).ready)

    async def test_upload_failure_keeps_store_and_previous_uploads(self):
        self.client.files.create.side_effect = [SimpleNamespace(id="file-0"), RuntimeError("upload")]
        with self.assertRaisesRegex(RuntimeError, "upload"):
            await ingest(self.client, self.path)
        self.assertEqual(load_state(self.path).file_ids, ["file-0"])
        self.assertEqual(load_state(self.path).vector_store_id, "vs_lab")

    async def test_repeated_ingest_refuses_to_overwrite_existing_state(self):
        await ingest(self.client, self.path)
        previous = self.path.read_bytes()
        with self.assertRaisesRegex(ValueError, "already exists"):
            await ingest(self.client, self.path)
        self.assertEqual(previous, self.path.read_bytes())
        self.client.vector_stores.create.assert_awaited_once()

    async def test_cleanup_deletes_only_recorded_resources(self):
        await ingest(self.client, self.path)
        await cleanup(self.client, self.path)
        self.client.vector_stores.delete.assert_awaited_once_with("vs_lab")
        self.assertEqual([call.args[0] for call in self.client.files.delete.await_args_list],
                         ["file-0", "file-1", "file-2"])
        self.assertFalse(self.path.exists())
        await cleanup(self.client, self.path)  # A second cleanup makes no extra calls.
        self.assertEqual(self.client.files.delete.await_count, 3)

    async def test_cleanup_failure_keeps_remaining_ids_for_retry(self):
        await ingest(self.client, self.path)
        self.client.files.delete.side_effect = [SimpleNamespace(deleted=True), RuntimeError("retry")]
        with self.assertRaisesRegex(RuntimeError, "retry"):
            await cleanup(self.client, self.path)
        state = load_state(self.path)
        self.assertIsNone(state.vector_store_id)
        self.assertEqual(state.file_ids, ["file-1", "file-2"])
        self.assertFalse(state.ready)
        self.client.files.delete.side_effect = None
        await cleanup(self.client, self.path)
        self.assertFalse(self.path.exists())
        self.client.vector_stores.delete.assert_awaited_once()

    async def test_store_delete_failure_retains_every_id(self):
        await ingest(self.client, self.path)
        self.client.vector_stores.delete.side_effect = RuntimeError("retry")
        with self.assertRaisesRegex(RuntimeError, "retry"):
            await cleanup(self.client, self.path)
        self.assertEqual(load_state(self.path).vector_store_id, "vs_lab")
        self.assertEqual(len(load_state(self.path).file_ids), 3)
        self.client.files.delete.assert_not_awaited()

    async def test_cleanup_treats_not_found_as_already_deleted(self):
        await ingest(self.client, self.path)
        missing = NotFoundError(
            "gone", response=httpx.Response(404, request=httpx.Request("DELETE", "https://example.com")),
            body=None,
        )
        self.client.vector_stores.delete.side_effect = missing
        self.client.files.delete.side_effect = missing
        await cleanup(self.client, self.path)
        self.assertFalse(self.path.exists())

    def test_readiness_rejects_partial_state(self):
        save_state(self.path, StoreState(vector_store_id="vs_lab", file_ids=["file-0"]))
        with self.assertRaisesRegex(ValueError, "incomplete"):
            ready_store_id(self.path)

    async def test_invalid_manifest_is_rejected_before_deletion(self):
        self.path.write_text('{"vector_store_id": "not-a-store"}')
        with self.assertRaises(ValueError):
            await cleanup(self.client, self.path)
        self.client.vector_stores.delete.assert_not_awaited()
        self.client.files.delete.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
