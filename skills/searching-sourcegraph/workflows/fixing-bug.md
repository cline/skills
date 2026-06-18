# Fixing a Bug

When fixing bugs, use Sourcegraph MCP to extensively search for the root cause before touching any code.

## Checklist

```
Task Progress:
- [ ] Reproduce and extract symptoms
- [ ] Search for error / failure site
- [ ] Trace the call chain
- [ ] Find all affected code paths
- [ ] Check recent changes
- [ ] Understand the intended behaviour
- [ ] Validate the fix against similar patterns
```

## Steps

### 1. Extract Symptoms

Before searching, collect everything available from the bug report:
- Exact error message or log line
- Stack trace symbols (function names, file paths, line numbers)
- Error codes or constants
- Relevant request/response data

The more precise your search terms, the fewer tool calls you need.

### 2. Search for the Error Site

```
keyword_search: "repo:^github.com/org/repo$ 'ExactErrorMessageHere'"
```

Also search for:
- The error class or constant name
- Any unique string from the stack trace
- Log statement nearest the failure

```
keyword_search: "repo:X file:src/ ErrTokenExpired"
nls_search: "repo:X token validation failure handling"
```

Run multiple searches in parallel when you have several candidate terms.

### 3. Find Where the Error Originates

```
find_references: <error symbol or throwing function>
```

Locate every site that can produce this error:
- Direct `throw` / `panic` / `return err` statements
- Error factory functions
- Middleware or interceptors that wrap errors

Read each throw site with `read_file` to understand the exact condition.

### 4. Trace the Full Call Chain

```
go_to_definition: <function at the throw site>
find_references: <caller of that function>
```

Walk the chain upward until you reach the entry point (HTTP handler, queue consumer, CLI command, etc.).

For complex chains, use:
```
deepsearch_read: "How does the X flow work from entry point to error site?"
```

### 5. Find All Affected Code Paths

Bugs often affect more than one path. Search broadly:

```
keyword_search: "repo:X <shared utility or function involved>"
find_references: <the function being fixed>
```

Confirm whether:
- Other callers rely on the current (buggy) behaviour
- Tests exist that cover these paths
- The same bug can surface elsewhere

### 6. Check Recent Changes

Recent commits are the most common source of regressions:

```
diff_search: "repo:X <function or symbol name>"
commit_search: repos=["org/repo"] messageTerms=["keyword related to bug area"]
```

Use `compare_revisions` if you want to diff a specific before/after window:
```
compare_revisions: repo="org/repo" base="main~30" head="main" path="src/auth/"
```

### 7. Understand the Intended Behaviour

Before writing the fix, confirm what correct behaviour looks like:

```
nls_search: "repo:X how should <feature> behave when <condition>"
read_file: <relevant test files>
```

Read existing tests to understand invariants. If tests are missing, that is part of the bug.

### 8. Find a Reference Fix or Pattern

Search for similar bugs that were already fixed in the codebase:

```
commit_search: repos=["org/repo"] messageTerms=["fix", "bug keyword"]
nls_search: "repo:X handle <edge case similar to the bug>"
```

Match your fix to the established pattern so it stays consistent with the codebase.

## Tips

- Search extensively before writing a single line of code — most fix time should be spent understanding, not coding
- Never assume the first throw site is the only one; always use `find_references`
- Check tests first: a failing test often tells you more than the code does
- Recent diffs narrow suspects dramatically — check them early
- If `keyword_search` returns too many results, scope with `file:` or `lang:` filters
- Use `deepsearch_read` when the bug spans multiple layers and you need architectural context
