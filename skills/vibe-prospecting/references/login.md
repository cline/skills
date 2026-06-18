# vpai CLI — Login & Setup

Authenticate `npx @vibeprospecting/vpai@latest` in a Cowork sandbox session. Run before any vpai tool.

## Fast Path

Most sessions only need:

```bash
mcp__cowork__request_cowork_directory path=~/.config/vpai
API_KEY=$(python3 -c "import json;print(json.load(open('/sessions/<session-id>/mnt/vpai/config.json'))['api_key'])")
npx @vibeprospecting/vpai@latest config --api-key "$API_KEY"
npx @vibeprospecting/vpai@latest --help   # verify
```

If the mount fails or `config.json` is missing, follow the full flow below.

## Key facts

- Durable auth lives at `~/.config/vpai/config.json` on the **local machine** (not in the sandbox).
- The sandbox cannot reach it directly — mount via `request_cowork_directory`.
- `~/.config/vpai/` is for `config.json` only. Never write exports, logs, or temp files there.
- For CSV in restricted sandboxes, set a writable `TMPDIR`:
  ```bash
  export TMPDIR=/sessions/<session-id>/tmp-vpai
  mkdir -p "$TMPDIR"
  ```

## Full Flow

### 1. Mount the local config dir

```
mcp__cowork__request_cowork_directory  path: ~/.config/vpai
```

Available at `/sessions/<session-id>/mnt/vpai/`.

If that mount fails, fall back to mounting the parent:

```
mcp__cowork__request_cowork_directory  path: ~/.config
mkdir -p /sessions/<session-id>/mnt/.config/vpai
```

Available at `/sessions/<session-id>/mnt/.config/vpai/`.

### 2. Check for an existing key

```bash
cat /sessions/<session-id>/mnt/vpai/config.json
# or, if ~/.config was mounted:
cat /sessions/<session-id>/mnt/.config/vpai/config.json
```

### 3a. Path A — key exists

```bash
API_KEY=$(python3 -c "import json;print(json.load(open('/sessions/<session-id>/mnt/vpai/config.json'))['api_key'])")
npx @vibeprospecting/vpai@latest config --api-key "$API_KEY"
```

### 3b. Path B — no key (first-time / post-logout)

```bash
npx @vibeprospecting/vpai@latest login
# Prints a browser URL (Auth0 / Explorium tenant) and optional user_code — use exactly what the CLI prints.
```

Tell the user to open the URL and approve. Do **not** wait for an explicit "I approved" reply — proceed immediately to polling.

```bash
npx @vibeprospecting/vpai@latest login --poll
```

Loop the `--poll` call until sign-in completes. Do not ask between polls. Cap total wait at ~2 minutes; if it doesn't complete, tell the user to approve at the URL.

If you need the key on stdout:

```bash
npx @vibeprospecting/vpai@latest login --poll-show
```

Persist the key to the mounted local path so future sessions skip the browser:

```bash
echo '{"api_key":"<key>"}' > /sessions/<session-id>/mnt/vpai/config.json
# or, if ~/.config was mounted:
echo '{"api_key":"<key>"}' > /sessions/<session-id>/mnt/.config/vpai/config.json
```

Then rehydrate the CLI:

```bash
API_KEY=$(python3 -c "import json;print(json.load(open('/sessions/<session-id>/mnt/vpai/config.json'))['api_key'])")
npx @vibeprospecting/vpai@latest config --api-key "$API_KEY"
```

### 4. Verify

```bash
npx @vibeprospecting/vpai@latest --help
```

If tools list, the CLI is ready.

## Direct API key (no browser)

```bash
npx @vibeprospecting/vpai@latest config --api-key "<tenant-api-key>"
```

## Sign out / switch account

```bash
npx @vibeprospecting/vpai@latest logout
# then repeat Path B
```

## Troubleshooting

| Problem | Fix |
|---|---|
| `npx ... vpai` won't run | Verify `npx` can reach npm; retry |
| `Not authenticated` | Re-run Step 3 — sandbox config doesn't persist between sessions |
| Can't find `config.json` | Try `request_cowork_directory` with `path: ~/.config/vpai`; if it fails, mount `~/.config` and create `/sessions/<session-id>/mnt/.config/vpai` |
| Need to switch tenants | `npx @vibeprospecting/vpai@latest logout`, then Path B |
| `--csv` write fails (`EACCES`) | Set `TMPDIR=/sessions/<session-id>/tmp-vpai` |
