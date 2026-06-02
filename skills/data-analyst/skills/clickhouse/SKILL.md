---
name: clickhouse
description: Connect to and query ClickHouse (a local server or a ClickHouse Cloud service) from the terminal using the official clickhousectl CLI, including the browser OAuth login flow. Use when the user wants to run SQL against ClickHouse, explore schemas and tables, inspect Cloud services, or authenticate clickhousectl. For building a local dev environment or deploying to Cloud, defer to the official ClickHouse skills (see Scope).
---

# ClickHouse via clickhousectl

Connect to ClickHouse and run queries using `clickhousectl`, the official ClickHouse CLI. This skill covers the parts a data analyst needs: authenticating, pointing at the right server, and running safe SQL. It does not use the ClickHouse MCP server; everything goes through the CLI.

## Scope

This skill is for connecting and querying. For these other flows, use the bundled official ClickHouse skills (siblings in this directory) instead of reinventing them:

- Setting up a local dev environment from scratch (install ClickHouse, init a project, start a server, create schema): `../clickhousectl-local-dev/`.
- Deploying to or migrating into ClickHouse Cloud (create a service, migrate schema, provision an app user): `../clickhousectl-cloud-deploy/`.
- Writing or optimizing non-trivial SQL, or the agent schema-discovery and query-safety workflow: `../clickhouse-best-practices/`.
- Running SQL on local files or remote sources without a server: `../chdb-sql/`.

These are vendored from https://github.com/ClickHouse/agent-skills (Apache-2.0). They can also be installed standalone with `clickhousectl skills` or `npx skills add clickhouse/agent-skills`.

## Step 1: Ensure clickhousectl is installed

```bash
which clickhousectl
```

If not found, install it (downloads the right build for the OS, installs to `~/.local/bin/clickhousectl`, and creates a `chctl` alias):

```bash
curl -fsSL https://clickhouse.com/cli | sh
```

If the command is still not found after install, `~/.local/bin` is not on PATH for this session:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

## Step 2: Identify the target

Decide what you are querying before authenticating. There are three cases:

- A local ClickHouse server managed by `clickhousectl` (started via `clickhousectl local server start`). Query it by name. No cloud auth needed.
- Any reachable ClickHouse over host/port (local or remote). No cloud auth needed.
- A ClickHouse Cloud service. Requires cloud authentication (Step 3).

List local servers and their ports:

```bash
clickhousectl local server list
```

## Step 3: Authenticate to ClickHouse Cloud (only for Cloud targets)

Skip this entirely for local or host/port targets.

`clickhousectl` has two cloud auth modes. The distinction matters:

- OAuth login (browser device flow), read-only. The agent can run this directly; it opens the user's browser. It can list and inspect resources (orgs, services, service details) but cannot create, modify, or delete.

  ```bash
  clickhousectl cloud auth login
  ```

- API key login, read and write. Needed for any write, and also for running SQL via `cloud service query` on first use (see the note in Step 4). Keep the secret out of the chat: ask the user to run this in a separate terminal in the same directory, or set the env vars themselves.

  ```bash
  # Either: run in a separate terminal (keeps the secret out of this session)
  clickhousectl cloud auth login --api-key <KEY> --api-secret <SECRET>

  # Or: environment variables (good for scripts/agents)
  export CLICKHOUSE_CLOUD_API_KEY=<KEY>
  export CLICKHOUSE_CLOUD_API_SECRET=<SECRET>
  ```

If the user has no account yet, `clickhousectl cloud auth signup` opens the sign-up page.

Verify auth and list what you can reach:

```bash
clickhousectl cloud auth status
clickhousectl cloud org list
clickhousectl cloud service list          # get the service name / id you will query
```

Credential resolution order: CLI flags > OAuth tokens > `.clickhousectl/credentials.json` > environment variables. Credentials are stored project-locally under `.clickhousectl/`.

## Step 4: Run queries

Prefer `--format` (e.g. `JSONEachRow`, `CSV`, `TabSeparated`) or `--json` when you need to parse results in a later step. SQL precedence for the query commands is `--query` > `--queries-file` > stdin.

Cloud service (over HTTP, no local binary or service password required):

```bash
clickhousectl cloud service query --name <service> -q "SHOW DATABASES"
clickhousectl cloud service query --id <service-id> -q "SELECT count() FROM events" --format JSONEachRow
clickhousectl cloud service query --name <service> --database analytics --queries-file query.sql
```

Note on Cloud auth and querying: `cloud service query` uses a per-service query-endpoint API key that is auto-provisioned on first use and stored in `.clickhousectl/credentials.json`. Provisioning is a write, so a read-only OAuth login is not sufficient for the first query against a service. Use API key auth (Step 3) to run SQL, or pass `--no-auto-enable` to fail fast instead of attempting to provision. Once provisioned, later queries reuse the stored key.

Local or host/port server (uses `clickhouse-client`):

```bash
clickhousectl local client --name <server> -q "SHOW TABLES"        # named local server
clickhousectl local client --host myhost --port 9000 -q "SELECT 1"  # any reachable server
clickhousectl local client --name <server> --queries-file query.sql
```

## Safe query practices

Keep queries safe, explainable, and bounded.

1. Discover schema/table shape if unknown: `SHOW DATABASES`, `SHOW TABLES`, `DESCRIBE TABLE <t>`.
2. Draft SQL using documented definitions when available (see `../reading-data-dict/`).
3. Explain what the SQL does before expensive execution.
4. Preview first when returning rows: `LIMIT 10` or `LIMIT 100`.
5. Prefer aggregate queries for metrics; avoid dumping high-cardinality raw data.
6. Confirm with the user before long-running, broad, or expensive scans.
7. Return the SQL with results so the user can inspect and reuse it.

Safety checks:

- Avoid accidental cross joins; use explicit join keys and know why the join is valid.
- Filter by time window whenever possible.
- Avoid `SELECT *` except tiny schema previews.
- Check row counts before exporting large result sets.
- Add `--json` or a `--format` for machine-readable output you intend to parse downstream.

## Bounded queries and large tables

Large fact tables can time out or exceed memory even for seemingly simple sanity checks. Keep exploratory and validation queries bounded unless there is strong evidence the table is small.

- Avoid unbounded freshness checks such as full-table `count()`, `uniqExact(...)`, or broad `min/max` scans on large fact tables. Prefer bounded recent-window checks, partition-aware filters, table metadata, or known date/key ranges, for example `WHERE report_date >= today() - 7`.
- For a quick metric over "last N days" from a daily aggregate table, default to completed report dates when appropriate and state that assumption; mention alternatives such as rolling N hours or including today if ambiguous.
- If an exact aggregate exceeds memory or times out, retry with smaller bounded chunks only when chunking preserves correctness. Daily counts can be queried week-by-week and concatenated because each date belongs to exactly one chunk.
- Do not chunk-and-sum distinct users across chunks unless the requested grain makes chunks independent. Weekly unique users cannot be produced by summing daily unique users, because a user can appear on multiple days.
- Document chunk boundaries, why the combined result remains exact, and the original failure mode in the SQL notes or artifact metadata.
- If no exact bounded fallback is safe, ask whether an approximate aggregate such as `uniq(...)`, a shorter window, or a different grain is acceptable.

## Result package

When returning query results, include:

- the SQL executed
- row count or aggregate count
- sample output or artifact path
- data freshness or observed time range
- caveats and the next query if needed

## Auth and secret handling

- Never print API keys, secrets, or passwords into the conversation or commit them.
- Prefer the browser OAuth flow for read-only exploration; it puts no secret in the chat.
- When write access or SQL querying requires an API key, prefer a separate terminal or environment variables over pasting the secret into this session.
- `clickhousectl cloud auth logout` clears all saved credentials (OAuth tokens and API keys).
