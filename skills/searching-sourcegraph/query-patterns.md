# Query Patterns Reference

Common regex patterns for Sourcegraph searches.

## Language-Specific Patterns

### TypeScript/JavaScript

| Intent | Query |
|--------|-------|
| React hooks | `file:.*\.tsx$ use[A-Z].*= \(` |
| React components | `file:.*\.tsx$ export (default )?function [A-Z]` |
| API routes (Express) | `file:src/api app\.(get\|post\|put\|delete)` |
| API routes (Next.js) | `file:app/api export async function (GET\|POST)` |
| Type definitions | `file:types/ export (interface\|type)` |
| Error handling | `catch.*Error\|\.catch\(` |
| Async functions | `async function\|async \(` |
| Class definitions | `export class [A-Z]` |
| Constants | `export const [A-Z_]+` |

### Python

| Intent | Query |
|--------|-------|
| Class definitions | `class [A-Z].*:` |
| Function definitions | `def [a-z_]+\(` |
| Decorators | `@[a-z_]+` |
| FastAPI routes | `@app\.(get\|post\|put\|delete)` |
| Django views | `class.*View\|def.*request` |
| Exception handling | `except.*:` |

### Go

| Intent | Query |
|--------|-------|
| Function definitions | `func [A-Z]` |
| Method definitions | `func \(.*\) [A-Z]` |
| Interface definitions | `type.*interface` |
| Struct definitions | `type.*struct` |
| Error handling | `if err != nil` |
| HTTP handlers | `func.*http\.ResponseWriter` |

## Project Structure Patterns

| Intent | Query |
|--------|-------|
| Test files | `file:.*\.(test\|spec)\.(ts\|js\|tsx)$` |
| Test setup | `file:.*\.test\. beforeEach\|beforeAll` |
| Config files | `file:(webpack\|vite\|rollup)\.config` |
| Package definitions | `file:package\.json "name":` |
| CI/CD workflows | `file:\.github/workflows deploy` |
| Docker files | `file:Dockerfile FROM` |
| Environment config | `file:\.env\. [A-Z_]+=` |

## Common Search Scopes

```
# Single repo
repo:^github.com/org/repo$

# All repos in org
repo:github.com/myorg/

# Specific file types
file:.*\.ts$ lang:typescript

# Specific directories
file:src/api/ file:.*\.ts$

# Exclude patterns
file:.*\.ts$ -file:.*\.test\.ts$ -file:__mocks__

# Multiple file types
file:\.(ts|tsx|js|jsx)$
```

## Tips

- Use `\|` for OR in regex patterns
- Use `^` and `$` for exact repo matching
- Escape special regex chars: `\.` `\(` `\)`
- Combine `file:` and `repo:` for precise scoping
