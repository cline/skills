# Understanding Unfamiliar Code

When exploring systems you don't know, start broad and narrow down.

## Checklist

```
Task Progress:
- [ ] Get big picture via Deep Search
- [ ] Find entry points
- [ ] Trace implementation
- [ ] Review related tests
```

## Steps

### 1. Get the Big Picture

```
deepsearch_read: "How does order fulfillment work in this codebase?"
```

Deep Search provides architectural understanding. Ask "how" and "why" questions.

### 2. Find Entry Points

```
keyword_search: "repo:X file:src/routes export.*order"
```

Look for:
- API route handlers
- Event listeners
- CLI commands
- UI component entry points

### 3. Trace the Implementation

```
go_to_definition: Jump to main handler
find_references: See how it's used
```

Follow the code path from entry point through business logic.

### 4. Review Related Tests

```
keyword_search: "repo:X file:.*\.test\.ts describe.*order"
```

Tests reveal:
- Expected behaviour
- Edge cases
- Usage patterns
- Integration points

## Tips

- Read 2-3 related files before synthesising
- Tests are documentation—read them
- Check for architecture docs in `docs/` or README files
