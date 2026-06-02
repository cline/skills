# Linear SDK recipes

Copy-paste building blocks for the canonical execution pattern in SKILL.md. Each snippet assumes:

```js
import { LinearClient } from "@linear/sdk"
const linear = new LinearClient({ apiKey: process.env.LINEAR_API_KEY })
```

Write the snippet into `"$LINEAR_DIR/task.mjs"` and run `node "$LINEAR_DIR/task.mjs"`.

## Resolve human inputs to IDs

Most mutations need UUIDs, but humans give you team keys, names, and emails. Look them up first.

```js
// Team by key (e.g. "ENG")
const teamConn = await linear.teams({ filter: { key: { eq: "ENG" } } })
const team = teamConn.nodes[0]

// User by email
const userConn = await linear.users({ filter: { email: { eq: "person@example.com" } } })
const user = userConn.nodes[0]

// Label by name within a team
const labels = await team.labels()
const bugLabel = labels.nodes.find((l) => l.name === "Bug")
```

## Find an issue by its human identifier (e.g. ENG-123)

`linear.issue(id)` expects a UUID. To resolve a human identifier, split it and filter:

```js
const identifier = "ENG-123"
const [key, numStr] = identifier.split("-")
const conn = await linear.issues({
  first: 1,
  filter: { team: { key: { eq: key } }, number: { eq: Number(numStr) } },
})
const issue = conn.nodes[0]
```

## List and filter issues

See the Filtering doc for the full comparator set. Common filters:

```js
// Open issues assigned to me, updated recently first
const me = await linear.viewer
const mine = await me.assignedIssues({
  first: 50,
  filter: { state: { type: { nin: ["completed", "canceled"] } } },
})

// Issues in a team with a given label
const byLabel = await linear.issues({
  first: 50,
  filter: { team: { key: { eq: "ENG" } }, labels: { name: { eq: "Bug" } } },
})

// Text search
const found = await linear.searchIssues("login crash")
```

Workflow state `type` values you can filter on: `backlog`, `unstarted`, `started`, `completed`, `canceled`, `triage`.

## Paginate through all results

Connections return one page at a time. Loop with `fetchNext`:

```js
const all = []
let page = await linear.issues({ first: 100, filter: { team: { key: { eq: "ENG" } } } })
all.push(...page.nodes)
while (page.pageInfo.hasNextPage) {
  page = await page.fetchNext()
  all.push(...page.nodes)
}
console.log(`fetched ${all.length} issues`)
```

## Read nested fields (async)

Relations are promises; await them.

```js
const issue = (await linear.issues({ first: 1 })).nodes[0]
const [state, assignee, team, comments] = await Promise.all([
  issue.state,
  issue.assignee,
  issue.team,
  issue.comments(),
])
console.log(issue.identifier, await state?.name, assignee ? assignee.displayName : "unassigned")
```

## Create an issue

```js
const team = (await linear.teams({ filter: { key: { eq: "ENG" } } })).nodes[0]
const payload = await linear.createIssue({
  teamId: team.id,
  title: "Fix flaky login test",
  description: "Repro steps...\n\n- one\n- two",
  // optional: assigneeId, priority (0-4), labelIds: [...], projectId, stateId
})
if (payload.success) {
  const created = await payload.issue
  console.log("created", created.identifier)
}
```

## Update an issue

```js
await linear.updateIssue("ISSUE_UUID", {
  title: "New title",
  assigneeId: "USER_UUID",
  priority: 2,
})
```

## Close (complete) or cancel an issue

There is no single "close" call. Set the issue's `stateId` to a workflow state whose `type` is `completed` (or `canceled`). States are per team.

```js
const issue = (await linear.issues({ first: 1, filter: { team: { key: { eq: "ENG" } }, number: { eq: 123 } } })).nodes[0]
const team = await issue.team
const states = await team.states()
const done = states.nodes.find((s) => s.type === "completed")
if (done) {
  await linear.updateIssue(issue.id, { stateId: done.id })
  console.log("closed", issue.identifier)
}
```

## Comment on an issue

```js
const payload = await linear.createComment({ issueId: "ISSUE_UUID", body: "Looking into this." })
if (payload.success) console.log("comment added")
```

## List teams, projects, cycles, users

```js
const teams = await linear.teams()
const projects = await linear.projects({ first: 50 })
const users = await linear.users()

// Cycles for a team
const team = teams.nodes[0]
const cycles = await team.cycles()
```

## Error handling

```js
try {
  // ... SDK calls ...
} catch (e) {
  const name = e?.constructor?.name
  if (e?.status === 401 || name === "AuthenticationLinearError") {
    console.error("AUTH_FAILED")
    process.exit(2)
  }
  if (e?.status === 429 || name === "RatelimitedLinearError") {
    console.error("RATE_LIMITED: back off and retry")
    process.exit(3)
  }
  console.error("LINEAR_ERROR:", name, e?.message)
  process.exit(1)
}
```

When a field, filter, or method name is uncertain, read the page noted in `docs-index.md` (Filtering, Pagination, SDK fetching and modifying data, or the GraphQL schema reference) and use the exact names from it.
