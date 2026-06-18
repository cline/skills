# Troubleshooting Issues

When investigating errors, build failures, stack traces, support issues, or runtime exceptions in production, search systematically from symptom to root cause.

## Checklist

```
Task Progress:
- [ ] Collect symptoms (error, stack trace, logs)
- [ ] Search for the error message or code
- [ ] Find where the error originates
- [ ] Understand the context and conditions
- [ ] Check recent changes for regressions
- [ ] Identify impact and affected paths
```

## Steps

### 1. Collect Symptoms

Before searching, extract all available signal:
- Exact error message or exception text
- Stack trace symbols (function names, file paths, line numbers)
- Error codes, constants, or exit codes
- Build output or log lines near the failure
- Environment details (service name, version, deployment context)

The more precise your search terms, the fewer tool calls you need.

### 2. Search for the Error

```
keyword_search: "repo:X 'ExactErrorMessageHere'"
```

Search for:
- Exact error message text or substrings
- Exception class names or error constants
- Log message patterns near the failure
- Build task names or compiler error codes

```
keyword_search: "repo:X ErrBuildFailed"
nls_search: "repo:X compilation failure during asset bundling"
```

Run multiple searches in parallel when you have several candidate terms.

### 3. Find Where It Originates

```
find_references: <error symbol or throwing function>
```

Locate all sites that produce this error:
- Direct `throw` / `panic` / `return err` statements
- Build scripts or CI steps that emit the failure
- Middleware or interceptors that wrap errors
- Error factory functions

Read each throw site with `read_file` to understand the exact trigger condition.

### 4. Understand the Context

```
deepsearch_read: "When does <error> occur and what are the expected conditions?"
```

Get a deeper understanding of:
- Conditions that trigger the error or failure
- Expected handling or recovery patterns
- Related error types or failure modes
- How this path behaves under normal operation

### 5. Check Recent Changes

Recent commits are the most common source of regressions:

```
diff_search: "repo:X <function or symbol name>"
commit_search: repos=["org/repo"] messageTerms=["keyword related to failure area"]
```

Use `compare_revisions` to diff a specific before/after window:
```
compare_revisions: repo="org/repo" base="main~30" head="main" path="src/affected/"
```

### 6. Identify Impact and Affected Paths

Check how broadly the issue affects the system:

```
find_references: <the failing function or error symbol>
keyword_search: "repo:X <shared utility involved in the failure>"
```

Confirm whether:
- Other callers or services are affected
- The same failure can surface in other environments (staging, canary)
- There are existing error handling paths that should have caught this

## Tips

- Extract exact symbols from stack traces — they are the fastest search terms
- Build failures often reference a specific task, target, or step name — search for that
- Errors frequently have multiple throw sites; always use `find_references` to find all of them
- Recent diffs narrow suspects dramatically — check them early
- For runtime exceptions in production, search for the error constant and its callers before looking at logs
- Use `deepsearch_read` when the failure spans multiple layers and you need architectural context
