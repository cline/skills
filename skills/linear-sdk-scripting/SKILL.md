---
name: linear-sdk-scripting
description: Perform actions in Linear (read, create, update, search issues, projects, comments, teams, cycles, labels, etc.) by writing and running small Node scripts against the official @linear/sdk TypeScript SDK with a personal API key. Use this when the user wants to do Linear work from the terminal without the Linear MCP server, or asks to list/open/create/update/close Linear issues, leave comments, or query teams, projects, users, or workflow states.
---

# Linear SDK Scripting

Drive Linear through the official TypeScript SDK (`@linear/sdk`) by writing throwaway Node scripts and executing them. This replaces the Linear MCP server: anything the MCP can do (read issues, create issues, comment, change status, query teams/projects/cycles) you do here by calling SDK methods.

The SDK is preferred over hand-written GraphQL because pagination, relationship traversal, and mutation payloads are normalized, and method and input names are predictable. When you need a field or filter you do not know, consult the docs index in `references/docs-index.md` and fetch the specific page rather than guessing.

## Workflow at a glance

Be reactive: try the script first, recover on auth failure, and only create a key as a last resort. Do not gate on `$LINEAR_API_KEY` being set in the current shell, that variable is almost always empty here even when a valid key is already persisted (see Setup).

1. Make sure the SDK is installed in the working dir. See Setup.
2. Write a small `.mjs` script into the working dir that imports `LinearClient` and does the task.
3. Run it with `node`, sourcing the shell profiles first so a persisted key is picked up (see Execution pattern).
4. If it fails with a 401 / `AuthenticationLinearError`, source the shell profiles and retry once. Only if it still fails is the key actually missing or invalid: run the API key setup flow with the user.

## Setup

### 1. Personal API key

The SDK authenticates with a Linear personal API key read from the `LINEAR_API_KEY` environment variable.

Do not decide whether a key exists by checking the env var up front. Scripts here run in a non-interactive, non-login shell that does not source `~/.zshrc`, `~/.zshenv`, `~/.bashrc`, etc., so `$LINEAR_API_KEY` reads as empty even when a valid key is already persisted in one of those files. An empty variable in this shell does not mean the key is unconfigured.

Instead, let the script attempt the work (the Execution pattern sources the profiles first), and only treat the key as missing if it still auth-fails after that. See Handling auth failures.

Only when the key is genuinely missing, guide the user through creating one:

1. Open Security and access settings: https://linear.app/settings/account/security
2. Under Personal API keys, create a new key. Copy it (it starts with `lin_api_`).
3. Ask the user to paste their key, then load it into the current session so you can use it immediately without a new terminal:

   ```sh
   export LINEAR_API_KEY="lin_api_REPLACE_ME"
   ```

4. Ask before persisting. The key is a secret and persisting it writes to a file the user owns, so do not do it on your own initiative. Explicitly ask first, for example: "Do you want me to persist this key to your shell profile (`~/.zshrc`) so it's available in future sessions?" Wait for a clear yes.

   Only after the user confirms, perform the write yourself using the command for the user's shell:

   - zsh:
     ```sh
     echo 'export LINEAR_API_KEY="lin_api_REPLACE_ME"' >> ~/.zshrc
     ```
   - bash (or `~/.bash_profile` on macOS login shells):
     ```sh
     echo 'export LINEAR_API_KEY="lin_api_REPLACE_ME"' >> ~/.bashrc
     ```
   - fish:
     ```sh
     echo 'set -gx LINEAR_API_KEY "lin_api_REPLACE_ME"' >> ~/.config/fish/config.fish
     ```

   This explicit in-conversation approval is what makes the write a user-requested action rather than an agent-initiated one. If the user declines or does not answer, do not persist the key; it will simply need to be re-set next session.

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

Source the common shell profiles before invoking `node` so a persisted key is pulled into the environment (this shell does not source them automatically). This preamble is harmless when no key is persisted, so use it as the standard way to run every script:

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
for f in ~/.zshenv ~/.zshrc ~/.zprofile ~/.profile ~/.bashrc ~/.bash_profile; do
  [ -f "$f" ] && source "$f"
done
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

If you see `AUTH_FAILED` (or the script crashes before any data), recover in this order rather than jumping straight to creating a key:

1. Source the shell profiles and retry once. The key may already be persisted in a profile file that this shell never sourced. Pull it in and re-run the same script:

   ```sh
   for f in ~/.zshenv ~/.zshrc ~/.zprofile ~/.profile ~/.bashrc ~/.bash_profile; do
     [ -f "$f" ] && source "$f"
   done
   node "$LINEAR_DIR/task.mjs"
   ```

   (If you already ran with the canonical Execution pattern preamble, the profiles were sourced, so this retry will only help if you ran without it.)

2. Only if it still auth-fails, the key is genuinely missing or invalid. Now do the Personal API key setup with the user (create and persist a new key), then rerun.

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
