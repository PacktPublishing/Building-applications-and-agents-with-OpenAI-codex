---
name: debug-failing-tests
description: Reproduce a failing test, make the smallest supported fix, verify it, and summarize the change.
---

# Debug Failing Tests

Use this workflow when asked to debug a repository with failing tests:

1. Inspect the relevant files and repository instructions before changing code.
2. Run the focused test (or smallest relevant test command) to reproduce the
   failure. Record the observed failure and identify its cause.
3. Make the smallest code change that addresses that cause. Avoid unrelated
   refactors or behavior changes.
4. Run the relevant tests again. If they still fail, inspect the new output and
   continue with a focused correction.
5. Summarize the failure, the change, and the test command and result.
