---
name: searching-sourcegraph
description: Use when the user needs to search or navigate code with Sourcegraph MCP tools. Provides disciplined search workflows for finding implementations, understanding systems, debugging issues, fixing bugs, and reviewing code.
---

# Searching Sourcegraph

Search before you build. Existing patterns reduce tokens, ensure consistency, and surface tested solutions.

## Tool Selection Logic

**Start here:**

1. **Know the exact symbol or pattern?** → `keyword_search`
2. **Know the concept, not the code?** → `nls_search`
3. **Need to understand how/why?** → `deepsearch` → `deepsearch_read`
4. **Tracing a symbol's usage?** → `find_references`
5. **Need full implementation?** → `go_to_definition` → `read_file`
6. **Need to know what repos a user has worked on?** → `get_contributor_repos`

| Goal | Tool |
|------|------|
| Concepts/semantic search | `nls_search` |
| Exact code patterns | `keyword_search` |
| Trace usage | `find_references` |
| See implementation | `go_to_definition` |
| Initiate a deep search | `deepsearch` |
| Read deep search results | `deepsearch_read` |
| Read files | `read_file` |
| Browse structure | `list_files` |
| Find repos | `list_repos` |
| Search commits | `commit_search` |
| Track changes | `diff_search` |
| Compare versions | `compare_revisions` |
| Find repos a user has worked on | `get_contributor_repos` |

## Scoping (Always Do This)

```
repo:^github.com/ORG/REPO$           # Exact repo (preferred)
repo:github.com/ORG/                 # All repos in org
file:.*\.ts$                         # TypeScript only
file:src/api/                        # Specific directory
file:.*\.test\.ts$ -file:__mocks__   # Tests, exclude mocks
```

Start narrow. Expand only if results are empty.

Combine filters: `repo:^github.com/myorg/backend$ file:src/handlers lang:typescript`

## Context-Aware Behaviour

**When the user provides a file path or error message:**
- Extract symbols, function names, or error codes
- Search for those exact terms first
- Trace references if the error involves a known symbol

**When the user asks "how does X work":**
- Use `deepsearch` to initiate the search, then `deepsearch_read` to retrieve results
- Follow up with `read_file` on key files mentioned in the response

**When the user asks who worked on something or what repos a contributor has touched:**
- Use `get_contributor_repos` with one or more usernames to discover their active repositories
- Then scope subsequent searches to those repos

**When the user is implementing a new feature:**
- Search for similar existing implementations first
- Read tests for usage examples
- Check for shared utilities before creating new ones

**When troubleshooting an error, build failure, or runtime exception:**
- Extract exact symbols, error codes, or log lines from the stack trace or build output
- Search for the error site, then trace the full call chain with `find_references`
- Check recent changes with `diff_search` and `commit_search` early — regressions are common
- Identify all affected code paths and services before proposing a fix

**When fixing a bug:**
- Extract exact symbols from the error message or stack trace
- Search for the error site, then trace the full call chain with `find_references`
- Check recent changes with `diff_search` and `commit_search` early — regressions are common
- Find all affected code paths before writing the fix
- Read existing tests to understand intended behaviour

## Workflows

For detailed step-by-step workflows, see:
- `workflows/implementing-feature.md` — when building new features
- `workflows/understanding-code.md` — when exploring unfamiliar systems
- `workflows/debugging-issue.md` — when troubleshooting errors, build failures, stack traces, support issues, or runtime exceptions
- `workflows/fixing-bug.md` — when fixing bugs with extensive Sourcegraph search
- `workflows/code-review.md` — when reviewing a pull request or changeset

## Efficiency Rules

**Minimise tool calls:**
- Chain searches logically: search → read → references → definition
- Don't re-search for the same pattern; use results from prior calls
- Prefer `keyword_search` over `nls_search` when you have exact terms (faster, more precise)

**Batch your understanding:**
- Read 2-3 related files before synthesising, rather than reading one and asking questions
- Use `deepsearch` + `deepsearch_read` for "how does X work" instead of multiple keyword searches

**Avoid common token waste:**
- Don't search all repos when you know the target repo
- Don't use `deepsearch` for simple "find all" queries — `keyword_search` is faster
- Don't re-read files you've already seen in this conversation

## Query Patterns

| Intent | Query |
|--------|-------|
| React hooks | `file:.*\.tsx$ use[A-Z].*= \(` |
| API routes | `file:src/api app\.(get\|post\|put\|delete)` |
| Error handling | `catch.*Error\|\.catch\(` |
| Type definitions | `file:types/ export (interface\|type)` |
| Test setup | `file:.*\.test\. beforeEach\|beforeAll` |
| Config files | `file:(webpack\|vite\|rollup)\.config` |
| CI/CD | `file:\.github/workflows deploy` |

For more patterns, see `query-patterns.md`.

## Output Formatting

**Search results:**
- Present as a brief summary, not raw tool output
- Highlight the most relevant file and line
- Include a code snippet only if it directly answers the question

**Code explanations:**
- Start with a one-sentence summary
- Use the codebase's own terminology
- Reference specific files and functions

**Recommendations:**
- Present as numbered steps if actionable
- Link to specific patterns found in the codebase
- Note any existing utilities that should be reused

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Searching all repos | Add `repo:^github.com/org/repo$` |
| Too many results | Add `file:` pattern or keywords |
| Missing relevant code | Try `nls_search` for semantic matching |
| Not understanding context | Use `deepsearch_read` |
| Guessing patterns | Read implementations with `read_file` |

## Principles

- Start narrow, expand if needed
- Chain tools: search → read → find references → definition
- Check tests for usage examples
- Read before generating
