---
name: linear-sdk-scripting
description: Perform actions in Linear (read, create, update, search issues, projects, comments, teams, cycles, labels, etc.) by writing and running small Node scripts against the official @linear/sdk TypeScript SDK with a personal API key. Use this when the user wants to do Linear work from the terminal without the Linear MCP server, or asks to list/open/create/update/close Linear issues, leave comments, or query teams, projects, users, or workflow states.
---

# Linear SDK Scripting

Drive Linear through the official TypeScript SDK (`@linear/sdk`) by writing throwaway Node scripts and executing them. This replaces the Linear MCP server: anything the MCP can do (read issues, create issues, comment, change status, query teams/projects/cycles) you do here by calling SDK methods.

The SDK is preferred over hand-written GraphQL because pagination, relationship traversal, and mutation payloads are normalized, and method and input names are predictable. When you need a field or filter you do not know, consult the docs index in `references/docs-index.md` and fetch the specific page rather than guessing.

## Workflow at a glance

1. Make sure setup is done (API key in env + SDK installed in the working dir). See Setup.
2. Write a small `.mjs` script into the working dir that imports `LinearClient` and does the task.
3. Run it with `node`.
4. If it fails with a 401 / `AuthenticationLinearError`, the key is missing or invalid: run the API key setup flow with the user.

## Setup

### 1. Personal API key

The SDK authenticates with a Linear personal API key read from the `LINEAR_API_KEY` environment variable.

Check whether it is already available:

```sh
test -n "$LINEAR_API_KEY" && echo "LINEAR_API_KEY is set" || echo "LINEAR_API_KEY is NOT set"
```

If it is not set, guide the user:

1. Open Security and access settings: https://linear.app/settings/account/security
2. Under Personal API keys, create a new key. Copy it (it starts with `lin_api_`).
3. Persist it to the shell profile so future sessions have it. Pick the file for the user's shell:
   - zsh: `~/.zshrc`
   - bash: `~/.bashrc` (or `~/.bash_profile` on macOS login shells)
   - fish: `~/.config/fish/config.fish` (syntax is `set -gx LINEAR_API_KEY ...`)

   For zsh or bash, append an export line. Ask the user to paste their key, then run something like:

   ```sh
   echo 'export LINEAR_API_KEY="lin_api_REPLACE_ME"' >> ~/.zshrc
   ```

4. Load it into the current session so you can use it immediately without a new terminal:

   ```sh
   export LINEAR_API_KEY="lin_api_REPLACE_ME"
   ```

Never print the key value back to the transcript or commit it anywhere. Treat it as a secret.

### 2. Install the SDK in a working directory

Keep a dedicated working directory with its own `node_modules`. Running scripts from inside it lets you use plain `import` with top-level await and no `NODE_PATH` tricks. Requires Node 18 or newer.

```sh
LINEAR_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/linear-sdk-scripting"
mkdir -p "$LINEAR_DIR"
cd "$LINEAR_DIR"
[ -f package.json ] || npm init -y >/dev/null
npm ls @linear/sdk >/dev/null 2>&1 || npm install @linear/sdk
```

This is a one-time setup; reuse the directory afterwards.

## Execution pattern (canonical)

For each task, write a script into the working directory and run it. Use the env var; do not inline the key.

```sh
LINEAR_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/linear-sdk-scripting"
cat > "$LINEAR_DIR/task.mjs" <<'EOF'
import { LinearClient } from "@linear/sdk"

const linear = new LinearClient({ apiKey: process.env.LINEAR_API_KEY })

const me = await linear.viewer
const myIssues = await me.assignedIssues({ first: 20 })
for (const issue of myIssues.nodes) {
  console.log(`${issue.identifier}  ${issue.title}`)
}
EOF
node "$LINEAR_DIR/task.mjs"
```

Notes:
- The script file lives in the working dir, so `import "@linear/sdk"` resolves against that dir's `node_modules`.
- `.mjs` gives you top-level `await`, so no async wrapper is needed.
- Emit machine-readable output (`console.log(JSON.stringify(...))`) when you need to parse results in a later step.

## Handling auth failures

A missing or invalid key surfaces as an `AuthenticationLinearError` with `status` 401. Detect it and route to the key setup flow:

```js
try {
  const me = await linear.viewer
  console.log(me.displayName)
} catch (e) {
  if (e?.status === 401 || e?.constructor?.name === "AuthenticationLinearError") {
    console.error("AUTH_FAILED: set up LINEAR_API_KEY")
    process.exit(2)
  }
  throw e
}
```

If you see `AUTH_FAILED` (or the script crashes before any data), do the Personal API key setup with the user, then rerun.

## Common operations

Concise recipes are inline below. Fuller examples (filtering, pagination loops, closing issues via workflow states, batch operations) are in `references/recipes.md`. The doc index is in `references/docs-index.md`.

Read:

```js
// Current user
const me = await linear.viewer

// List issues (newest first), with a filter
const issues = await linear.issues({
  first: 25,
  filter: { state: { type: { eq: "started" } } },
})

// A single issue by UUID
const issue = await linear.issue("UUID")

// Teams, users, projects
const teams = await linear.teams()
const users = await linear.users()
const projects = await linear.projects({ first: 50 })
```

Write (mutations return a payload with `success` and the entity, often as a promise):

```js
// Create
const created = await linear.createIssue({
  teamId: "TEAM_UUID",
  title: "Title",
  description: "Markdown body",
})
const newIssue = await created.issue

// Update (e.g. retitle, reassign)
await linear.updateIssue("ISSUE_UUID", { title: "New title", assigneeId: "USER_UUID" })

// Comment
await linear.createComment({ issueId: "ISSUE_UUID", body: "Comment text" })
```

To resolve human inputs to IDs (team key like `ENG`, a workflow state name like `Done`, an assignee email), look them up first. See `references/recipes.md` for the lookup-then-mutate patterns, including how to close an issue by finding the team's completed workflow state.

## When you need something not covered here

The Linear schema is large. Instead of guessing field or filter names:

1. Open `references/docs-index.md` and pick the relevant page.
2. Fetch that page (filtering, pagination, SDK fetching and modifying data, or the GraphQL schema reference) and use the exact names from it.

## Gotchas

- Run scripts from the working dir (or point at a script inside it) so `@linear/sdk` resolves. `NODE_PATH` does not resolve packages for ESM `import`; it only works for CommonJS `require`.
- Many SDK properties and nested relations are async and return promises or connections. Await them (`await issue.state`, `await issue.assignee`).
- Connections paginate. Use `connection.pageInfo.hasNextPage` and `await connection.fetchNext()`, or iterate. See `references/recipes.md`.
- Mutation results expose `success` and the mutated entity; the entity accessor is usually a promise (`await payload.issue`).
- Personal API key auth uses no `Bearer` prefix. The SDK handles the header for you; this matters only if you ever drop down to raw GraphQL.
- Never echo the API key into the transcript, scripts committed to a repo, or logs.
