# Implementing a Feature

When building new features, search for similar patterns first to ensure consistency.

## Checklist

```
Task Progress:
- [ ] Find similar implementations
- [ ] Read file structure
- [ ] Study a good example
- [ ] Check shared utilities
```

## Steps

### 1. Find Similar Implementations

```
nls_search: "repo:^github.com/org/repo$ user settings CRUD"
```

Look for features that solve similar problems. Note the patterns used.

### 2. Explore File Structure

```
keyword_search: "repo:^github.com/org/repo$ file:src/features/ index.ts"
```

Understand how features are organised in this codebase.

### 3. Study a Representative Example

```
read_file: Read 2-3 files from a well-implemented similar feature
```

Pay attention to:
- Naming conventions
- File organisation
- Import patterns
- Error handling approach

### 4. Check for Shared Utilities

```
find_references: Trace usage of common utilities
```

Before creating new helpers, check if reusable utilities exist:
- Validation functions
- API wrappers
- UI components
- Type definitions

## Tips

- Don't create new patterns when existing ones work
- Match the style of surrounding code
- Check tests for usage examples of utilities
- Look at recent PRs for similar features
