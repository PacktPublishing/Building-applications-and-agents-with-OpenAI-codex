# Lab 07 — OpenAI Vector Store: Document Q&A

**Status:** Reference implementation built; offline checks pass. Live API
verification requires credentials and has not been run for this build.

**Time:** 35–45 minutes. **Prerequisite:** Lab 01 or familiarity with `Agent`
and `Runner.run`. Python 3.11+; an OpenAI API key for the hosted exercises.

Build a knowledge assistant for the fictional Northstar Market. Upload three
policy documents to an OpenAI vector store, inspect retrieved passages, and
ask a real SDK agent to answer questions with file citations.

## What you will learn

- Distinguish an uploaded file, its indexed vector store association, and the store.
- Wait for indexing before querying and handle failed ingestion.
- Compare `client.vector_stores.search` with hosted `FileSearchTool`.
- Configure result limits and file attribute filters.
- Inspect `result.new_items`, file citation annotations, usage, and tracing metadata.
- Reuse a store across runs and remove both the store and its uploaded files.

## Start here

- [Codex prompt pack](prompt-pack.md): rebuild the lab from VS-01 through VS-05.
- [Reference setup and commands](reference-solution/README.md).
- [Guided learner exercises](reference-solution/lab-guide.md).
- [Build and verification record](reference-solution/BUILD-LOG.md).

The agent uses `Agent`, `FileSearchTool`, `ModelSettings`, `Runner.run`, and
`RunConfig` directly. Search and indexing are hosted by OpenAI. Offline tests
mock the API boundaries; they do not replace retrieval in the actual demo.
