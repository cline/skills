# Fetch

Search for businesses or prospects, retrieve event details. In cowork mode, `fetch-entities` covers both — set `entity_type` to `businesses` or `prospects`.

Use the examples below when the planned fetch call matches them. Before the first real `--args` for each fetch-related tool, run `npx @vibeprospecting/vpai@latest <tool> --all-parameters` once (mandatory per tool, not only when uncertain). That prints `{ name, description, inputSchema }`; use **`inputSchema`** for argument shapes. Never invent parameters.

## Rules

- **`--session-id`** is a CLI flag (not inside `--args`). Pass the **`session_id`** from the previous tool JSON so the CLI reuses the same session SQLite DB (`db_path`).
- **`--csv`** only on the **final step**. Intermediate steps emit JSON for chaining.
- **Chain IDs:** There is no `--input-file`. After match/fetch, pass **`--session-id`**; the CLI reads `business_id` or `prospect_id` from tables under that session. Use **`--table-name`** with the prior step's **`table_name`** — **required** for **`fetch-businesses-events`** / **`fetch-prospects-events`** (and for **`enrich-*`**); optional for **`match-*`** when disambiguating multiple tables.
- **Prospects at prior companies:** For `fetch-entities` with `entity_type: prospects` scoped to businesses from an earlier step, pass **`--session-id`**, **`--businesses-table-name`** (table containing those `business_id` rows), and optional **`--table-name`** only if you need to disambiguate.
- **`--number-of-results N`** collects N rows across pages automatically. Omit for one raw page.

## `fetch-entities` for businesses

```bash
# US software, 51-200 employees
npx @vibeprospecting/vpai@latest fetch-entities --args '{
  "entity_type": "businesses",
  "filters": {
    "company_country_code": {"values": ["US"]},
    "company_size": {"values": ["51-200"]},
    "linkedin_category": {"values": ["Software Development"]}
  }
}' --number-of-results 50 --tool-reasoning '<user request>'

# Salesforce users, exclude UK
npx @vibeprospecting/vpai@latest fetch-entities --args '{
  "entity_type": "businesses",
  "filters": {
    "company_tech_stack_tech": {"values": ["Salesforce"]},
    "company_country_code": {"values": ["GB"], "negate": true}
  }
}' --number-of-results 50 --tool-reasoning '<user request>'

# Recently funded private US, 3-6 yrs old
npx @vibeprospecting/vpai@latest fetch-entities --args '{
  "entity_type": "businesses",
  "filters": {
    "company_country_code": {"values": ["US"]},
    "company_age": {"values": ["3-6"]},
    "is_public_company": false,
    "events": {"values": ["new_funding_round"], "last_occurrence": 60}
  }
}' --number-of-results 50 --tool-reasoning '<user request>'
```

## `fetch-entities` for prospects

```bash
# C-suite engineering at mid-size
npx @vibeprospecting/vpai@latest fetch-entities --args '{
  "entity_type": "prospects",
  "filters": {
    "job_level": {"values": ["c-suite"]},
    "job_department": {"values": ["engineering"]},
    "company_size": {"values": ["201-500"]}
  }
}' --number-of-results 50 --tool-reasoning '<user request>'
```

## Job filter rules

- `job_title` is **substring-match**, not exact-match.
- For executive searches, always combine `job_title` with `job_level` (usually `c-suite`) to remove assistants, advisors, office-of roles.

```bash
npx @vibeprospecting/vpai@latest fetch-entities --args '{
  "entity_type": "prospects",
  "filters": {
    "job_title": {"values": ["chief executive officer"]},
    "job_level": {"values": ["c-suite"]}
  }
}' --number-of-results 20 --tool-reasoning '<user request>'
```

## Company size pitfall

`company_size` uses fixed buckets (`1-10`, `11-50`, `51-200`, `201-500`, ...). No exact `>100` cutoff. For "over 100 employees", approximate with adjacent buckets (`51-200` + `201-500`) or enrich with `firmographics` for exact headcount.

## Chaining business IDs into a prospect fetch

Use **`--session-id`** from the match/fetch-business step, **`--businesses-table-name`** set to the table that holds **`business_id`** (from prior JSON **`table_name`**), and filters for the prospect query inside **`--args`**.

```bash
# 1. Resolve companies
npx @vibeprospecting/vpai@latest match-business --args '{"businesses_to_match":[{"name":"Acme","domain":"acme.com"}]}' --tool-reasoning '<user request>'
# 2. Leaders at those companies (reuse session; inject business IDs via businesses table)
npx @vibeprospecting/vpai@latest fetch-entities --args '{"entity_type":"prospects","filters":{"job_level":{"values":["director","vice president","c-suite"]}}}' --session-id <session_id> --businesses-table-name <match_business_table_name> --number-of-results 50 --tool-reasoning '<user request>'
# 3. Enrich — pass session + fetch table name for prospect rows
npx @vibeprospecting/vpai@latest enrich-prospects --args '{"enrichments":["contacts"]}' --session-id <session_id> --table-name <fetch_entities_table_name> --csv --tool-reasoning '<user request>'
```

## `fetch-businesses-events` / `fetch-prospects-events`

Session-based bulk events for companies or prospects you already have in the session DB (from **`match-*`**, **`fetch-entities`**, etc.).

### Rules

- **`--session-id`** and **`--table-name`** are **required** together. **`--table-name`** must be the prior step's **`table_name`** whose rows include **`business_id`** (business events) or **`prospect_id`** (prospect events).
- Do **not** put **`business_ids`** / **`prospect_ids`** inside **`--args`**. The CLI reads IDs from the SQLite table only; this avoids oversized requests and enables chunking.
- The CLI calls MCP with **up to 20 IDs per request**, runs batches concurrently (bounded), appends Partner **`output_events`** rows, then **pivots** into one output row per source entity. Output columns are **`event_<event_type>`** (for example **`event_new_product`**, **`event_new_funding_round`**): each cell is a **JSON array** string for that type (newest-first, capped per type), or an **empty CSV cell** when there are no events for that type.
- **`--csv`** on this step writes a flattened CSV **next to the session DB**; the JSON manifest includes **`csv_path`** and **`columns`**.
- **Resume:** If a run times out, **re-run the same command** (same **`--session-id`**, **`--table-name`**, **`--args`**). Completed ID batches are skipped until the job finishes.

Before the first real events call, inspect allowed **`event_types`** and **`--args`** shape from the **input** JSON Schema via **`fetch-businesses-events --all-parameters`** / **`fetch-prospects-events --all-parameters`** (routine pull, not only when uncertain).

### Examples

```bash
# Funding + product signals for companies from a prior fetch
npx @vibeprospecting/vpai@latest fetch-entities --args '{"entity_type":"businesses","filters":{"events":{"values":["new_funding_round"],"last_occurrence":60}}}' --number-of-results 20 --tool-reasoning '<user request>'
npx @vibeprospecting/vpai@latest fetch-businesses-events --args '{"event_types":["new_funding_round","new_product"],"timestamp_from":"2024-10-01"}' --session-id <session_id> --table-name <fetch_entities_table_name> --tool-reasoning '<user request>'

# Match file → events (same session chain)
npx @vibeprospecting/vpai@latest match-business --file-path ./companies.csv --schema '{"Company":"name"}' --tool-reasoning '<user request>'
npx @vibeprospecting/vpai@latest fetch-businesses-events --args '{"event_types":["new_partnership"],"timestamp_from":"2023-01-01"}' --session-id <session_id> --table-name <match_business_table_name> --csv --tool-reasoning '<user request>'

# Prospect-level events
npx @vibeprospecting/vpai@latest fetch-prospects-events --args '{"event_types":["prospect_changed_role"],"timestamp_from":"2024-07-01"}' --session-id <session_id> --table-name <fetch_entities_table_name> --tool-reasoning '<user request>'
```
