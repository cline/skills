# Vendored third-party skills

The sub-skills listed below are copied from [ClickHouse/agent-skills](https://github.com/ClickHouse/agent-skills).
They are committed as plain files (not a submodule or symlinks) so that every
installer that copies this repository (GitHub tarballs, `npx skills`, the Cline
marketplace) delivers them.

Only the skills the data-analyst workflow uses are vendored. ClickHouse's full
set can be installed directly with `npx skills add clickhouse/agent-skills`.
The list lives in `scripts/sync-vendored-skills.sh`.

- Source: https://github.com/ClickHouse/agent-skills
- Commit: `356a8c1b9a7392adb389a132f5ad3fec38532a03` (committed upstream 2026-09-28)
- Licence: Apache License 2.0, see `LICENSE-clickhouse-agent-skills` and `NOTICE-clickhouse-agent-skills` in this directory
- Vendored on: 2026-10-13

Skills, each copied from `skills/<name>/` upstream:

- `chdb-datastore/`
- `chdb-sql/`
- `clickhouse-best-practices/`
- `infra-clickhouse/`

Upstream files are unmodified. Omitted from each skill: its top-level `README.md`
and `metadata.json`, plus `rules/_*.md` (repo/registry metadata and build
templates that the skills do not read).

To refresh, run from the repository root:

```
scripts/sync-vendored-skills.sh          # re-copy the commit above
scripts/sync-vendored-skills.sh main     # update to the latest upstream
```
