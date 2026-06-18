# Match

Resolve known entities to canonical IDs for follow-up enrichment or events.

Use the examples below when the planned match call matches them. Before the first real `--args` for that match tool, run `npx @vibeprospecting/vpai@latest <tool> --all-parameters` once (mandatory per tool, not only when uncertain). That prints `{ name, description, inputSchema }`; use **`inputSchema`** for argument shapes. Never invent parameters.

## Rules

- **`--session-id`** is a CLI flag. Omit on first call; pass the **`session_id`** returned in JSON from each prior step.
- **`--csv`** only on the final step. Intermediate steps emit JSON.
- **Chain IDs:** Pass **`--session-id`** so the CLI reads from the session SQLite DB. Use **`--table-name`** when multiple tables exist. Do not paste raw IDs into `--args`.
- Limits: `match-business` 50/call, `match-prospects` 40/call.

Skip match if you already ran `fetch-entities` — those results include IDs.

## CSV Upload (`--file-path` + `--schema`)

Use when the user provides a CSV file of companies or people to resolve to Explorium IDs.

- **`--file-path <path>`** — path to the CSV file.
- **`--schema '<json>'`** — required. JSON dict mapping CSV column headers to API field names. Build this by inspecting the CSV headers, then map each to the correct API field below.

**Business API fields:** `name`, `domain`

**Prospect API fields:** `full_name`, `first_name`, `last_name` (combined into `full_name`), `email`, `phone_number`, `linkedin`, `company_name`, `business_id`

The output merges all original CSV columns with the matched ID. Chain into enrich with the returned `session_id` and `table_name`.

## `match-business`

```bash
# Name + domain (most accurate)
npx @vibeprospecting/vpai@latest match-business --args '{"businesses_to_match":[{"name":"Salesforce","domain":"salesforce.com"}]}' --tool-reasoning '<user request>'

# Multiple
npx @vibeprospecting/vpai@latest match-business --args '{"businesses_to_match":[{"domain":"stripe.com"},{"name":"OpenAI"},{"name":"HubSpot","domain":"hubspot.com"}]}' --tool-reasoning '<user request>'

# From CSV (user provides a file)
npx @vibeprospecting/vpai@latest match-business --file-path /path/to/companies.csv --schema '{"Company Name":"name","Website":"domain"}' --tool-reasoning '<user request>'

# Chain into enrich (same session + table from match output)
npx @vibeprospecting/vpai@latest enrich-business --args '{"enrichments":["firmographics"]}' --session-id <session_id> --table-name <match_business_table_name> --tool-reasoning '<user request>'
```

## `match-prospects`

```bash
# By email (most reliable)
npx @vibeprospecting/vpai@latest match-prospects --args '{"prospects_to_match":[{"email":"jane.smith@acme.com"}]}' --tool-reasoning '<user request>'

# By LinkedIn
npx @vibeprospecting/vpai@latest match-prospects --args '{"prospects_to_match":[{"linkedin":"https://linkedin.com/in/janesmith"}]}' --tool-reasoning '<user request>'

# By name + company
npx @vibeprospecting/vpai@latest match-prospects --args '{"prospects_to_match":[{"full_name":"Jane Smith","company_name":"Acme Corp"}]}' --tool-reasoning '<user request>'

# From CSV (user provides a file)
npx @vibeprospecting/vpai@latest match-prospects --file-path /path/to/people.csv --schema '{"First Name":"first_name","Last Name":"last_name","Email":"email","Company":"company_name"}' --tool-reasoning '<user request>'

# Chain into enrich
npx @vibeprospecting/vpai@latest enrich-prospects --args '{"enrichments":["contacts"]}' --session-id <session_id> --table-name <match_prospects_table_name> --tool-reasoning '<user request>'
```
