# Common Search Examples

Real-world search examples for common tasks.

## Finding Implementations

**"Where is authentication handled?"**
```
nls_search: "repo:^github.com/org/repo$ authentication middleware validation"
```

**"How do we make API calls?"**
```
keyword_search: "repo:^github.com/org/repo$ fetch\|axios\|http\.request"
```

**"Find all database queries"**
```
keyword_search: "repo:^github.com/org/repo$ \.query\(\|\.execute\("
```

## Understanding Flow

**"How does user signup work end-to-end?"**
```
deepsearch_read: "Trace the user signup flow from form submission to database creation"
```

**"What happens when a payment fails?"**
```
deepsearch_read: "How does the system handle failed payment attempts?"
```

## Debugging

**"Find where this error is thrown"**
```
keyword_search: "repo:^github.com/org/repo$ 'User not found'"
find_references: Find all usages of the error constant
```

**"What changed in authentication recently?"**
```
diff_search: repos=["github.com/org/repo"] pattern="auth" after="2 weeks ago"
```

## Finding Patterns

**"How do other features handle validation?"**
```
nls_search: "repo:^github.com/org/repo$ input validation schema"
```

**"Find examples of pagination"**
```
keyword_search: "repo:^github.com/org/repo$ offset\|limit\|cursor\|pageToken"
```

## Tracing Dependencies

**"What uses this utility function?"**
```
find_references: repo="github.com/org/repo" path="src/utils/format.ts" symbol="formatDate"
```

**"Where is this type defined?"**
```
go_to_definition: repo="github.com/org/repo" path="src/api/handler.ts" symbol="UserResponse"
```
