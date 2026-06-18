# Fetch Stats

Counts and breakdowns without fetching individual records. In cowork mode, `fetch-entities-statistics` covers both business and prospect counts — set `entity_type` accordingly.

Use the examples below when the planned stats call matches them. Before the first real `--args` for `fetch-entities-statistics`, run `npx @vibeprospecting/vpai@latest fetch-entities-statistics --all-parameters` once (mandatory, not only when uncertain). That prints `{ name, description, inputSchema }`; use **`inputSchema`** for argument shapes. Never invent parameters.

`--session-id` is a CLI flag. Filter shape matches `fetch-entities`.

## Examples

```bash
# US SaaS, 51-200
npx @vibeprospecting/vpai@latest fetch-entities-statistics --args '{"entity_type":"businesses","filters":{"company_country_code":{"values":["US"]},"company_size":{"values":["51-200"]},"linkedin_category":{"values":["Software Development"]}}}' --tool-reasoning '<user request>'

# Fintech across Europe
npx @vibeprospecting/vpai@latest fetch-entities-statistics --args '{"entity_type":"businesses","filters":{"linkedin_category":{"values":["Financial Services"]},"company_country_code":{"values":["GB","DE","FR","NL","SE"]}}}' --tool-reasoning '<user request>'

# Marketing directors in fintech
npx @vibeprospecting/vpai@latest fetch-entities-statistics --args '{"entity_type":"prospects","filters":{"job_level":{"values":["director"]},"job_department":{"values":["marketing"]},"linkedin_category":{"values":["Financial Services"]}}}' --tool-reasoning '<user request>'
```
