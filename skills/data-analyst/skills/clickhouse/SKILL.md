---
name: clickhouse
description: Connect to and query ClickHouse (a local server or a ClickHouse Cloud service) from the terminal using the official clickhousectl CLI, including the browser OAuth login flow. Use when the user wants to run SQL against ClickHouse, explore schemas and tables, inspect Cloud services, or authenticate clickhousectl. For building a local dev environment or deploying to Cloud, defer to the official ClickHouse skills (see Scope).
---

# ClickHouse via clickhousectl

Connect to ClickHouse and run queries using `clickhousectl`, the official ClickHouse CLI. This skill covers the parts a data analyst needs: authenticating, pointing at the right server, and running safe SQL. It does not use the ClickHouse MCP server; everything goes through the CLI.

## Scope

This skill is for connecting and querying. For these other flows, use the official ClickHouse skills instead of reinventing them:

- Setting up a local dev environment from scratch (install ClickHouse, init a project, start a server, create schema): official `clickhousectl-local-dev` skill.
- Deploying to or migrating into ClickHouse Cloud (create a service, migrate schema, provision an app user): official `clickhousectl-cloud-deploy` skill.

Install the official ClickHouse Agent Skills with `clickhousectl skills`, or `npx skills add clickhouse/agent-skills`. Repo: https://github.com/ClickHouse/agent-skills

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

- Discover before you compute: `SHOW DATABASES`, `SHOW TABLES`, `DESCRIBE TABLE <t>`, then a small `SELECT ... LIMIT n` preview.
- Always bound exploratory queries with `LIMIT`. Avoid unbounded scans, `SELECT *` on wide or large tables, and high-cardinality `GROUP BY` until you know the data size.
- Ask before running expensive, long-running, or high-cardinality queries.
- Add `--json` or a `--format` for machine-readable output you intend to parse downstream.

## Auth and secret handling

- Never print API keys, secrets, or passwords into the conversation or commit them.
- Prefer the browser OAuth flow for read-only exploration; it puts no secret in the chat.
- When write access or SQL querying requires an API key, prefer a separate terminal or environment variables over pasting the secret into this session.
- `clickhousectl cloud auth logout` clears all saved credentials (OAuth tokens and API keys).
