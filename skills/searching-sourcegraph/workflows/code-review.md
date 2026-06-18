# Code Review

When reviewing a pull request or changeset, use Sourcegraph MCP to verify correctness, spot risks, and check consistency — before leaving comments.

## Checklist

```
Task Progress:
- [ ] Understand the scope of changes
- [ ] Verify changed code against existing patterns
- [ ] Check for similar prior implementations or fixes
- [ ] Trace impact on callers and dependents
- [ ] Review test coverage
- [ ] Inspect recent changes in the same area
- [ ] Flag inconsistencies or missing conventions
```

## Steps

### 1. Understand the Scope of Changes

Start by reading the diff or changed files to extract the key symbols, functions, and modules being modified.

Collect:
- New or modified function/class names
- Files touched
- Any new dependencies or imports introduced
- Error handling paths added or changed

### 2. Verify Against Existing Patterns

Check that the new code follows established conventions in the codebase:

```
nls_search: "repo:^github.com/org/repo$ how is <concept> typically implemented"
keyword_search: "repo:^github.com/org/repo$ file:src/<area>/ <pattern or function name>"
```

Look for:
- Naming style (snake_case vs camelCase, verb prefixes, etc.)
- File organisation conventions
- How similar functionality is already implemented elsewhere
- Whether shared utilities exist that should be reused

```
read_file: <2-3 representative files from the same area>
```

### 3. Search for Prior Art on the Same Problem

Confirm the approach isn't reinventing something already solved:

```
nls_search: "repo:^github.com/org/repo$ <feature or problem the PR solves>"
commit_search: repos=["org/repo"] messageTerms=["<keyword related to the change>"]
```

If a similar feature exists, compare the approaches and flag divergence if it reduces consistency.

### 4. Trace Impact on Callers and Dependents

For any modified public symbol (function, type, constant), check its usage:

```
find_references: <modified function or type>
```

Verify:
- All call sites are compatible with the new signature or behaviour
- No implicit contracts are broken (return value shape, error semantics, etc.)
- If a shared utility is changed, all consumers are safe

For deeper impact analysis:

```
deepsearch_read: "How is <changed component> used across the system?"
```

### 5. Review Test Coverage

Read the existing tests for the affected area:

```
keyword_search: "repo:^github.com/org/repo$ file:.*\.test\. <function or module name>"
read_file: <relevant test files>
```

Check:
- Are the new code paths covered?
- Do existing tests still match the updated behaviour?
- Are edge cases (empty inputs, errors, boundary values) tested?
- Are tests missing for non-trivial logic introduced in the PR?

### 6. Inspect Recent Changes in the Same Area

Recent activity reveals context and potential conflicts:

```
diff_search: "repo:^github.com/org/repo$ <file path or function name>"
commit_search: repos=["org/repo"] messageTerms=["<area keyword>"]
```

Use `compare_revisions` to see what changed in the area recently:

```
compare_revisions: repo="org/repo" base="main~30" head="main" path="src/<affected area>/"
```

Look for:
- Parallel changes that could conflict
- Recent fixes the PR might accidentally revert
- Patterns established in nearby recent work

### 7. Flag Inconsistencies and Missing Conventions

After searching, compile review comments around:

- **Pattern divergence**: Code that works but differs from established style without reason
- **Missing reuse**: New helpers that duplicate existing utilities
- **Untested paths**: Non-trivial logic without coverage
- **Broken contracts**: Changed behaviour that affects undiscovered callers
- **Risk surface**: Error handling gaps, missing validation, or unsafe assumptions

## Tips

- Search before commenting — many apparent issues are intentional deviations with prior art
- Use `find_references` before flagging a changed signature as breaking; verify actual impact
- Read tests first — they often clarify the intended contract faster than the implementation
- Check recent commits in the same path; the PR may be part of a larger sequence of changes
- Use `deepsearch_read` when the change touches a system you're unfamiliar with before reviewing it
- Scope searches to the affected directory or module to reduce noise
