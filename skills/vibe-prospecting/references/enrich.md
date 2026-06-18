# Enrich

Run after you have business or prospect IDs.

Use the examples below when the planned enrich call matches them. Before the first real `--args` for that enrich tool, run `npx @vibeprospecting/vpai@latest <tool> --all-parameters` once (mandatory per tool, not only when uncertain). That prints `{ name, description, inputSchema }`; use **`inputSchema`** for argument shapes. Never invent parameters.

## Rules

- Pass **`--session-id`** from the previous step. The CLI loads IDs from the session SQLite DB (`db_path` in prior output).
- **`--table-name`** is **required** with **`--session-id`** for both enrich tools — pass the prior step's **`table_name`** exactly (no automatic table pick).
- **`--csv`** only on the final step. Intermediate enrich steps that feed another tool emit JSON only.
- Both tools batch large ID lists automatically (chunks of 50).
- **`business_ids` / `prospect_ids`** do not need to appear in **`--args`** when IDs come from the session DB via **`--session-id`**.

## `enrich-business`

```bash
# Full company intelligence
npx @vibeprospecting/vpai@latest match-business --args '{"businesses_to_match":[{"name":"Stripe","domain":"stripe.com"}]}' --tool-reasoning '<user request>'
npx @vibeprospecting/vpai@latest enrich-business --args '{"enrichments":["firmographics","technographics","funding-and-acquisitions","workforce-trends"]}' --session-id <session_id> --table-name <match_business_table_name> --tool-reasoning '<user request>'

# Tech stack + keyword check
npx @vibeprospecting/vpai@latest enrich-business --args '{
  "enrichments": ["technographics","webstack","website-keywords"],
  "parameters": {"keywords": ["AI","machine learning","LLM"]}
}' --session-id <session_id> --table-name <match_business_table_name> --tool-reasoning '<user request>'

# Public company financials
npx @vibeprospecting/vpai@latest enrich-business --args '{
  "enrichments": ["financial-metrics","competitive-landscape","strategic-insights"],
  "parameters": {"date": "2024-01-01T00:00"}
}' --session-id <session_id> --table-name <match_business_table_name> --tool-reasoning '<user request>'
```

Enrichment types: `firmographics`, `technographics`, `company-ratings`, `financial-metrics`, `funding-and-acquisitions`, `challenges`, `competitive-landscape`, `strategic-insights`, `workforce-trends`, `linkedin-posts`, `website-changes`, `website-keywords`, `webstack`, `company-hierarchies`.

Caveats:
- `financial-metrics` requires `parameters.date`.
- `website-keywords` requires `parameters.keywords`.
- For finding people at a company, use `fetch-entities` with `entity_type: prospects` + `business_id` filter (or businesses reference flow), not enrichment alone.

## `enrich-prospects`

Combine all needed enrichments in one call.

```bash
# Profile + contacts
npx @vibeprospecting/vpai@latest fetch-entities --args '{"entity_type":"prospects","filters":{"job_level":{"values":["director"]},"job_department":{"values":["engineering"]}}}' --number-of-results 50 --tool-reasoning '<user request>'
npx @vibeprospecting/vpai@latest enrich-prospects --args '{"enrichments":["profiles","contacts"]}' --session-id <session_id> --table-name <fetch_entities_table_name> --csv --tool-reasoning '<user request>'
```

Enrichment types: `contacts` (emails, phones), `profiles` (name, role, work history, education), `linkedin-posts`.

When **`--csv`** is used on the final step, output includes **`csv_path`** alongside **`db_path`**, **`table_name`**, and **`session_id`**.
