# Autocomplete

Run before any search that uses controlled-vocabulary fields. Returns standardized values to use verbatim in the next `fetch-entities` / `fetch-entities-statistics` call.

Use the examples below when the planned autocomplete call matches them. Before the first real `--args` for `autocomplete`, run `npx @vibeprospecting/vpai@latest autocomplete --all-parameters` once (mandatory, not only when uncertain). That prints `{ name, description, inputSchema }` to stdout; use **`inputSchema`** for argument shapes. Never invent parameters.

Output may include `session_id` — pass as `--session-id` to the next tool.

## Fields that require autocomplete

- `linkedin_category`
- `naics_category`
- `company_tech_stack_tech`
- `job_title`
- `business_intent_topics`
- `city_region`

## Fields that do NOT require autocomplete

- `company_country_code` — ISO Alpha-2 (e.g. `"US"`, `"GB"`)
- `company_region_country_code` — ISO 3166-2 (e.g. `"US-NY"`)
- `company_size`, `company_revenue`, `company_age`, `job_level`, `job_department` — fixed buckets (use `--all-parameters` on `fetch-entities` / `fetch-entities-statistics` for exact allowed enum strings)
- `website_keywords` — free text

## Mutual exclusions

- `linkedin_category` and `naics_category` — use one, not both.
- `company_region_country_code` and `company_country_code` — use one.
- `job_title` requires autocomplete; `job_level` and `job_department` do not.

## Picking values

- Autocomplete may return noisy variants (misspellings, spacing, compound titles). Pick the canonical clean value, usually the first clean result.
- Multiple values broaden matching with OR logic. Don't include near-duplicates unless you want a wider search.
- For executive title searches, prefer `job_level` plus the cleanest single `job_title` value.

## Examples

```bash
npx @vibeprospecting/vpai@latest autocomplete --args '{"field":"linkedin_category","query":"software"}' --tool-reasoning '<user request>'
npx @vibeprospecting/vpai@latest autocomplete --args '{"field":"company_tech_stack_tech","query":"salesforce"}' --tool-reasoning '<user request>'
npx @vibeprospecting/vpai@latest autocomplete --args '{"field":"job_title","query":"data scientist"}' --tool-reasoning '<user request>'
npx @vibeprospecting/vpai@latest autocomplete --args '{"field":"business_intent_topics","query":"cloud security"}' --tool-reasoning '<user request>'

# Reuse session_id on the following fetch
npx @vibeprospecting/vpai@latest fetch-entities --args '{"entity_type":"businesses","filters":{"linkedin_category":{"values":["Software Development"]}}}' --session-id <session_id> --number-of-results 50 --tool-reasoning '<user request>'
```
