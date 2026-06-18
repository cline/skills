---
name: "vibe-prospecting"
description: "Find company & contact data. Turn your agent into a prospecting platform. Get contact information, roles, tech stack, business events, website changes, intent data. Build lead lists, research prospects, identify talent. 150M+ companies, 800M+ professionals, 50+ data sources."
compatibility: Run with `npx @vibeprospecting/vpai@latest`. If the CLI does not work and the user's agent environment supports connectors, suggest the Vibe Prospecting connector to the user.
metadata:
  version: "0.1.62"
---

# Vibe Prospecting CLI

Use the CLI: `npx @vibeprospecting/vpai@latest`. Treat every tool response as JSON.

**Cowork mode: always use this connector flow.** Before doing any work in Cowork mode, check whether the Vibe Prospecting MCP connector tools are available in your tool list (look for a tool matching the pattern `mcp__*__fetch-entities`).

If those tools are present, use the connector directly and follow its tool descriptions and schemas. If those tools are NOT present:
1. Call `mcp__mcp-registry__search_mcp_registry` with keywords `["vibe prospecting", "explorium"]`
2. Call `mcp__mcp-registry__suggest_connectors` with the UUID `1bdcb159-b6f0-4f13-bc08-fdb40b007828` and keywords `["prospecting"]`
3. Tell the user to click **Connect** on the card — the tools unlock automatically once authorized
4. **Poll until connected.** On every subsequent turn, re-check your tool list for `mcp__*__fetch-entities`. Do not start prospecting work until those tools appear. **Never** fall back to the CLI, the npm `vpai` tool, or an OAuth URL in Cowork mode — the Cowork connector store is the only path. If the user cannot connect from the suggested card, tell them to open the **connector store** and install Vibe Prospecting from there, then poll again. If tools are still missing, remind the user to connect and wait; repeat until the connector is available.

**If the CLI does not work** outside Cowork mode (e.g. `npx` unavailable, sandboxed environment, permission denied), and the user's agent environment supports connectors, suggest the Vibe Prospecting connector to the user. The rest of this file is CLI-only. In Cowork mode, use the connector store flow above.

## Hard Rules

1. **Sample first, always.** Run the COMPLETE workflow on exactly 5 entities (`--number-of-results 5`) before any full run. That cap is a **quality gate only**: Explorium can match **many more** rows for the same filters. **Never** describe those 5 rows as the full dataset, "all results," or "what the database has." Show the sample, state clearly that it is a preview and the index has more, then after explicit approval **re-run the same CLI tool(s)** you used in the sample chain with full-scale parameters (same `--args`, session, and filters; raise caps such as **`--number-of-results`** to the user's real target where that flag applies). Run **`fetch-entities-statistics`** only when **all** of your discovery **`fetch-entities`** filters (and any supported scope flags) are valid for statistics too — see rule 8. Never auto-export. "Find 100" still means sample 5 first, then scale up after approval.
2. **`--tool-reasoning '<user wording>'`** on every real call. Use the user's request verbatim. Reuse across the whole workflow. Skip ONLY when running `<tool> --all-parameters` with no `--args`.
3. **Chain via session DB, never paste IDs.** Each step prints `session_id`, `db_path`, and `table_name`. Pass **`--session-id`** with the **`session_id`** from the prior JSON output so the next command uses the same SQLite session store. With **`--session-id`**, **`--table-name`** is **required** for **`enrich-business`**, **`enrich-prospects`**, **`fetch-businesses-events`**, and **`fetch-prospects-events`** — pass the prior step's **`table_name`** exactly. For **`match-*`** only, **`--table-name`** is optional (CLI can pick the first table with the right ID column when omitted). For **`fetch-entities`** prospects scoped to earlier companies, use **`--businesses-table-name`** plus **`--session-id`**.
4. **`--csv` only on the final step.** Intermediate steps emit JSON for chaining. Add `--csv` once, at the end.
5. **`autocomplete` first** for: `naics_category`, `linkedin_category`, `company_tech_stack_tech`, `job_title`, `business_intent_topics`, `city_region`. Use returned standardized values, not raw user wording.
6. **Never invent tool parameters.** Before the **first** `--args` execution of each distinct tool in a workflow, run `npx @vibeprospecting/vpai@latest <tool> --all-parameters` for that tool (once per tool per task unless you already printed its schema earlier in the same workflow). That command prints one JSON object to stdout: **`name`**, **`description`**, and **`inputSchema`** (the tool **input** JSON Schema). **Do this even when** the planned call matches the examples and you are not uncertain—examples can drift; the printed schema is authoritative. Run `--all-parameters` again if you change tools, filters, or shapes materially, or if anything still feels ambiguous. You may use examples and reference docs as shortcuts only **after** they align with that live schema. Build `--args` only from fields and shapes confirmed by **`inputSchema`** from `--all-parameters` (and examples when they match it).
7. **`--session-id`** is a CLI flag (not inside `--args`). Use the **`session_id`** value returned by the MCP in each prior step's JSON. Omit only on the first call in a chain.
8. **`fetch-entities-statistics` only when stats supports the full fetch.** Compare your planned **`fetch-entities`** payload to the **input schema** from **`fetch-entities-statistics --all-parameters`**. Call statistics **only if every** filter key, value shape, **`entity_type`**, and any scope you rely on (e.g. **`--session-id`** / **`--businesses-table-name`**) is accepted by the statistics tool the same way it is for **`fetch-entities`**. If any part of the discovery query is missing from the stats schema, unsupported, or would require a different shape, **skip stats** — do not call it with a partial or guessed subset. When you do call it, reuse the **same** **`--args`** filter object (and supported flags) as **`fetch-entities`**, plus **`--tool-reasoning`**. Prefer running stats **before** presenting the sample so you can headline **5 of [total]** when the response includes a usable count. When you **did not** run statistics (or stats had no usable total), present **Sample preview (5 rows)** and tell the user Explorium has **much more** matching the same filters—**do not** quote how many remain, **do not** say statistics failed or a total was unavailable, and **never** invent a number. Call stats again before a full-scale fetch **if** filters or scope changed **and** the full fetch filter set still fits statistics.

## Auth

```bash
mcp__cowork__request_cowork_directory path=~/.config/vpai
API_KEY=$(python3 -c "import json;print(json.load(open('/sessions/<session-id>/mnt/vpai/config.json'))['api_key'])")
npx @vibeprospecting/vpai@latest config --api-key "$API_KEY"
```

If the mount fails or `config.json` is missing, follow [`login.md`](references/login.md).

## Sample Gate

The sample is the **complete workflow on 5 entities**, not a fetch preview.

**Universe vs sample:** The 5 rows are a **small fixed preview** so the user can validate filters and enrichment before spending quota. The underlying match set is typically **much larger** (often thousands or more). Do not equate "we returned 5" with "only 5 exist." Ground volume with **`fetch-entities-statistics`** only when the **entire** planned **`fetch-entities`** filter set is valid for stats (rule 8); never guess a total.

1. **When the full fetch filter set is supported by statistics**, run **`fetch-entities-statistics`** with the same discovery **`entity_type`**, **`filters`**, and supported CLI flags as the upcoming **`fetch-entities`** (per rule 8). Otherwise skip stats; still tell the user Explorium has **much more** for the same filters (no numeric total, no mention of statistics gaps).
2. Fetch exactly 5 (`--number-of-results 5`).
3. Run **every** subsequent step (`match-*`, `enrich-*`, `fetch-*-events`) on those 5.
4. Show the **fully enriched final rows** as a markdown table with all useful columns.
5. Stop. Wait for approval in a new message. Then run at full scale.

NEVER stop after the fetch to ask for approval. Complete the full chain on 5 first.

Example — user says "find 100 Israeli companies, get 30 CEOs, find contact info":
- WRONG: fetch 5 companies → show table → ask "continue?"
- RIGHT: when the **full** **`fetch-entities`** filter set is supported by **`fetch-entities-statistics`**, run stats first (same **`--args`** filters) → fetch 5 companies → fetch CEOs at those 5 → enrich CEOs with contacts → show final table (**5 of [total]** when stats gave a total; otherwise **Sample preview (5 rows)** plus a short line that **much more** matches exist for these filters—no count, no stats apology) → ask "run full 100?"

### Presenting the sample

Always frame the table as a **sample**, not the full population.

- **When statistics returned a usable total** (you only called stats because **every** **`fetch-entities`** filter was valid for **`fetch-entities-statistics`**): **Sample preview (5 of [total] matches)** — **[total]** must come from **`fetch-entities-statistics`**, never from counting the 5 rows.
- **When you did not use a numeric total** (no stats, or no usable total): **Sample preview (5 rows)** and one plain sentence that Explorium has **much more** matching these filters—**do not** say how many more, **do not** mention statistics or missing totals, **never** invent **[total]**.

`Results Found: [X] [entity type] from [Y] [companies/sources] [qualifier]` (optional context line)

**Headline:** **Sample preview (5 of [total] matches):** only with a stats-backed **[total]**; otherwise **Sample preview (5 rows):** then a single framing line that **much more** records exist for the same filters (qualitative only).

End with an explicit next step, for example: **After you confirm**, I will re-run the same tool(s) with full-scale limits (e.g. **`--number-of-results [user's N]`** where you used `fetch-entities`) to pull the real batch.

When the preview is a subset of what the user asked for (more rows or fields available at scale), add:

- With a stats-backed **[total]**: `More data available: Preview shows [n] of [total]. Confirm before I run the full export.`
- Without a numeric **[total]**: say the preview is five rows, **much more** exists in Explorium for the same filters, and ask to confirm a full export—**do not** give a remaining count or mention why no total was shown.

Do **not** mention export when everything the user asked for is already in chat.

### Before the full export, confirm

- Export size (cap on records).
- Filter narrowing: industry, size, revenue, region, tech.
- For prospects: title variants, dedupe by company.
- For contacts: professional emails only or also personal/phones.

## Workflow

```
0. Auth — see Auth section above (or login.md)
1. npx @vibeprospecting/vpai@latest --help                    Discover tools
2. Read references/<tool>.md for workflow + caveats
3. Before the first real `--args` for each tool: `npx @vibeprospecting/vpai@latest <tool> --all-parameters` (mandatory per tool, not only when uncertain). Prints the tool **input** schema as JSON. Run again if the planned call diverges from what you already validated.
4. Build `--args` only from fields confirmed by that printed input schema (examples count only when they match it). If a parameter is not confirmed there, do not use it.
5. When the **entire** planned **`fetch-entities`** filter set (and supported flags) matches **`fetch-entities-statistics`** input schema per **`--all-parameters`**: run **`fetch-entities-statistics`**, then sample (5 entities, full chain) — see Sample Gate
6. npx @vibeprospecting/vpai@latest <tool> --args '<json>' --tool-reasoning '<user request>'
7. Chain: --session-id <session_id> [--table-name <table_name>] [--businesses-table-name <name> for prospect fetch from businesses]
8. Final step only: add --csv
```

Reference docs:

- [`autocomplete.md`](references/autocomplete.md) — controlled-vocab lookups
- [`fetch.md`](references/fetch.md) — `fetch-entities`, `fetch-*-events`
- [`match.md`](references/match.md) — resolve known entities to IDs
- [`enrich.md`](references/enrich.md) — enrichment after IDs
- [`fetch-stats.md`](references/fetch-stats.md) — counts and market sizing
- [`login.md`](references/login.md) — auth fallback flow

## Flags

| Flag | Description |
|------|-------------|
| `--help` | List tools |
| `--all-parameters` | Print `{ name, description, inputSchema }` to stdout (pretty-printed JSON). Run before the first `--args` for each tool in a workflow (and again if the tool or payload changes materially). Routine, not only when uncertain—the **`inputSchema`** field is authoritative. |
| `--args '<json>'` | Tool arguments |
| `--session-id <id>` | Same workflow: pass **`session_id`** from the previous tool's JSON (opens the shared SQLite DB under `db_path`). |
| `--table-name <name>` | **Required** with `--session-id` for **`enrich-business`**, **`enrich-prospects`**, **`fetch-businesses-events`**, and **`fetch-prospects-events`** (prior step's `table_name`). Optional for **`match-*`** only (disambiguate when multiple tables). |
| `--businesses-table-name <name>` | For `fetch-entities` + `entity_type: prospects`: table whose rows supply `business_id` for the filter (with `--session-id`). |
| `--number-of-results <n>` | For `fetch-entities`: total rows across pages (CLI paginates). Omit for one raw page. |
| `--file-path <path>` | For `match-business` / `match-prospects`: path to a CSV file to match. Each row becomes one candidate. Requires `--schema`. |
| `--schema '<json>'` | Required with `--file-path`. JSON dict mapping CSV column headers to API field names. Business fields: `name`, `domain`. Prospect fields: `full_name`, `first_name`, `last_name`, `email`, `phone_number`, `linkedin`, `company_name`, `business_id`. |
| `--csv` | Also write flattened CSV. **Final step only.** |

## Filter Pattern

```json
{ "values": ["v1", "v2"], "negate": false }   // include or exclude
{ "gte": 6, "lte": 24 }                       // range
true | false | null                           // boolean (not wrapped)
```

## Limits

| Tool | Limit |
|------|-------|
| `match-business` | 50 per call |
| `match-prospects` | 40 per call |
| `enrich-business` | 50 IDs per call |
| `enrich-prospects` | 50 IDs per call |
| `fetch-businesses-events` / `fetch-prospects-events` | Up to **20** IDs per MCP request (CLI chunks + merges). Pass **`event_types`** and **`timestamp_from`** in **`--args`**. Do not put **`business_ids`** / **`prospect_ids`** in **`--args`** — IDs come only from **`--table-name`**. |
| `fetch-entities` | use `--number-of-results`; CLI paginates. Don't pass `next_cursor` or `page_size` manually |

## Common Workflows

Replace `SESSION_ID` with the `session_id` from the previous step.

### VP Engineering at SaaS in NY

```bash
npx @vibeprospecting/vpai@latest autocomplete --args '{"field":"linkedin_category","query":"software"}' --tool-reasoning 'find VP Eng at SaaS in NY'
# When every fetch-entities filter (and flags) is valid for fetch-entities-statistics (--all-parameters):
npx @vibeprospecting/vpai@latest fetch-entities-statistics --args '{"entity_type":"prospects","filters":{"job_level":{"values":["vice president"]},"job_department":{"values":["engineering"]},"linkedin_category":{"values":["Software Development"]},"company_region_country_code":{"values":["US-NY"]},"has_email":true}}' --tool-reasoning 'find VP Eng at SaaS in NY'
npx @vibeprospecting/vpai@latest fetch-entities --args '{"entity_type":"prospects","filters":{"job_level":{"values":["vice president"]},"job_department":{"values":["engineering"]},"linkedin_category":{"values":["Software Development"]},"company_region_country_code":{"values":["US-NY"]},"has_email":true}}' --number-of-results 50 --tool-reasoning 'find VP Eng at SaaS in NY'
npx @vibeprospecting/vpai@latest enrich-prospects --args '{"enrichments":["contacts","profiles"]}' --session-id <session_id> --table-name <fetch_entities_table_from_prior_step> --csv --tool-reasoning 'find VP Eng at SaaS in NY'
```

### Companies that raised + use Salesforce

```bash
npx @vibeprospecting/vpai@latest autocomplete --args '{"field":"company_tech_stack_tech","query":"salesforce"}' --tool-reasoning 'companies that raised and use Salesforce'
# When every fetch-entities filter (and flags) is valid for fetch-entities-statistics (--all-parameters):
npx @vibeprospecting/vpai@latest fetch-entities-statistics --args '{"entity_type":"businesses","filters":{"company_tech_stack_tech":{"values":["Salesforce"]},"events":{"values":["new_funding_round"],"last_occurrence":60}}}' --tool-reasoning 'companies that raised and use Salesforce'
npx @vibeprospecting/vpai@latest fetch-entities --args '{"entity_type":"businesses","filters":{"company_tech_stack_tech":{"values":["Salesforce"]},"events":{"values":["new_funding_round"],"last_occurrence":60}}}' --number-of-results 50 --tool-reasoning 'companies that raised and use Salesforce'
npx @vibeprospecting/vpai@latest fetch-businesses-events --args '{"event_types":["new_funding_round"],"timestamp_from":"2024-10-01"}' --session-id <session_id> --table-name <fetch_entities_table_from_prior_step> --csv --tool-reasoning 'companies that raised and use Salesforce'
```

### Market sizing

```bash
npx @vibeprospecting/vpai@latest fetch-entities-statistics --args '{"entity_type":"businesses","filters":{"linkedin_category":{"values":["Hospital & Health Care"]},"company_country_code":{"values":["US"]}}}' --tool-reasoning 'market sizing US healthcare'
```

## Troubleshooting

| Error | Solution |
|-------|----------|
| CLI install fails (`npx` unavailable, sandbox, permission denied) | Switch to the bundled Vibe Prospecting MCP connector and follow its tool descriptions; the rest of this file no longer applies. |
| Auth / 401 (connector / Cowork) | Run Auth section above; if mount fails, follow [`login.md`](references/login.md) |
| Auth / 401 (OpenClaw) | Run `npx @vibeprospecting/vpai@latest login` then `login --poll`. Or set `VP_API_KEY`. Restart gateway after. See Auth section above. |
| `Not authenticated` (OpenClaw) | Neither `~/.config/vpai/config.json` nor `VP_API_KEY` env var is present. Follow the OpenClaw Auth section. |
| Plugin not showing tools in OpenClaw | Run `openclaw plugins list` — confirm `vpai` is listed. Re-install if needed: `openclaw plugins install ./vpai-plugin`. |
| Tools missing after OpenClaw install | Gateway must restart: `openclaw gateway restart`. |
| Missing **`session_id`** in JSON / CLI refuses to chain | The MCP must return **`session_id`**; ensure you target production **`https://vibeprospecting.explorium.ai/mcp`** (embedded in the npm CLI). Pass **`--session-id`** with that exact string on the next step. |
| Wrong rows used when chaining | Pass **`--table-name`** matching the prior step's **`table_name`**. |
| **`enrich-*` or `fetch-*-events` with `--session-id` but no `--table-name`** | **`--table-name`** is required for **`enrich-business`**, **`enrich-prospects`**, **`fetch-businesses-events`**, and **`fetch-prospects-events`** whenever you pass **`--session-id`**. |
| Empty results | Check filter values; run `autocomplete` for controlled-vocab fields; re-check the relevant live **input** schema with `<tool> --all-parameters` |
| `linkedin_category` + `naics_category` together | Mutually exclusive — use one |
| JSON parse error | Validate JSON; check shell quoting |
| Timeout on `fetch-entities`, `enrich-*`, `fetch-*-events`, or `match-*` with `--file-path` | **Re-run the exact same command** with the same `--session-id`, `--table-name`, `--args`, and (for match) `--file-path` / `--schema`. The CLI resumes from the last checkpoint — completed ID batches are skipped, no work is repeated. If the job already completed on a prior run, the stored manifest is returned instantly with no API calls. |
| Timeout without `--session-id` | Add `--session-id <any-stable-id>` to enable checkpointing, then retry. Without a session ID the CLI cannot resume. |
