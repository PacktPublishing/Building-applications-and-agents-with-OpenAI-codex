# OpenAI source verification — Lab 07

Verified on 2026-09-03 using the OpenAI Docs MCP, the installed libraries,
and the repo-local official SDK checkout.

| Source | What it establishes for this lab |
|---|---|
| [File search](https://developers.openai.com/api/docs/guides/tools-file-search) | Hosted retrieval over uploaded vector stores, result limits, metadata filters, file citation annotations, and explicit inclusion of search results. |
| [Retrieval](https://developers.openai.com/api/docs/guides/retrieval) | Direct `vector_stores.search`, automatic indexing, per-file attributes, polling helpers, distinct file/store objects, and expiration policies. |
| [Official SDK file search example](https://github.com/openai/openai-agents-python/blob/9411cee8e2fc8e3656e4f9b8f7eec370a943f2ea/examples/tools/file_search.py) | Visible `Agent`, `FileSearchTool(include_search_results=True)`, `Runner.run`, and `result.new_items`; upload followed by `create_and_poll`. |

The SDK checkout is at
`replay-environment/.agents/skills/openai-agents-sdk/openai-agents-python`
relative to the repository root, commit
`9411cee8e2fc8e3656e4f9b8f7eec370a943f2ea`.

The runnable reference was checked with `openai-agents==0.17.2` and
`openai==2.36.0` on Python 3.12. The upstream checkout was used as source
material, not installed in place of the repository's pinned dependencies.

Additional installed-source checks:

- `agents.tool.FileSearchTool`: result inclusion, result limit, and filters.
- `openai.resources.vector_stores.files.AsyncFiles.create_and_poll`: returns
  terminal failed/cancelled states as well as completed states. The lab checks
  the returned status and bounds the wait.
- `ResponseFileSearchToolCall.results`, `ResponseOutputMessage` annotations,
  and `VectorStoreSearchResponse.content`: parsed using the actual SDK models.
- `OpenAIProvider(openai_client=..., use_responses=True)`, `RunConfig` tracing
  options, and `result.context_wrapper.usage`: used directly by the reference.

The public guide contains Responses API snippets; the lab uses the Agents SDK
for the model run and the OpenAI client for resource management/direct search.
No custom runner or local retrieval substitute is introduced. No exact cost
estimate or claim of live model verification is made.
