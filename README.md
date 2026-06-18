# Cline Skills

A collection of [Agent Skills](https://docs.cline.bot/customization/skills) we use at [Cline](https://cline.bot) and want to share with the community.

## Installing

These skills work with any agent that supports the Agent Skills standard, including Cline, Claude Code, Cursor, OpenCode, OpenAI Codex, and Pi.

### npx skills

Install using the [`npx skills`](https://skills.sh) CLI:

```
npx skills add https://github.com/cline/skills
```

### Claude Code

Install using the [plugin marketplace](https://code.claude.com/docs/en/discover-plugins#add-from-github):

```
/plugin marketplace add cline/skills
/plugin install cline@cline
```

### Cursor

Install from the Cursor Marketplace or add manually via `Settings > Rules > Add Rule > Remote Rule (Github)` with `cline/skills`.

### Clone / Copy

Clone this repo (with submodules) and copy the skill folders into the appropriate directory for your agent:

```
git clone --recurse-submodules https://github.com/cline/skills
```

| Agent | Skill Directory | Docs |
|-------|-----------------|------|
| Cline | `~/.cline/skills/` | [docs](https://docs.cline.bot/customization/skills) |
| Claude Code | `~/.claude/skills/` | [docs](https://code.claude.com/docs/en/skills) |
| Cursor | `~/.cursor/skills/` | [docs](https://cursor.com/docs/context/skills) |
| OpenCode | `~/.config/opencode/skills/` | [docs](https://opencode.ai/docs/skills/) |
| OpenAI Codex | `~/.codex/skills/` | [docs](https://developers.openai.com/codex/skills/) |
| Pi | `~/.pi/agent/skills/` | [docs](https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent#skills) |

## Skills

Skills are contextual and auto-loaded based on your conversation. When a request matches a skill's triggers, the agent loads and applies the relevant skill to provide accurate, up-to-date guidance.

| Skill | Useful for |
|-------|------------|
| [cline-sdk](https://github.com/cline/sdk-skill) | Building AI agents with the Cline SDK: Agent runtime, ClineCore sessions, custom tools, plugins, events, LLM providers, scheduling, multi-agent teams, and production deployment |
| [review-team](./skills/review-team) | Running a fleet of specialized reviewer subagents (correctness, security, architecture, conventions, simplicity, UX, reliability, telemetry, testing, compatibility, docs) against the same change, single-pass or iterate-until-clean |
| [linear-sdk-scripting](./skills/linear-sdk-scripting) | Doing Linear work from the terminal without the Linear MCP: list, open, create, update, close, and comment on issues, and query teams, projects, cycles, users, and workflow states by writing small Node scripts against the official `@linear/sdk` with a personal API key |
| [amazon-location-service](./skills/amazon-location-service) | Building AWS location-aware apps with maps, places, geocoding, routing, geofences, and trackers using Amazon Location Service |
| [amplify-workflow](./skills/amplify-workflow) | Building and deploying full-stack web and mobile apps with AWS Amplify Gen2, including auth, data, storage, functions, APIs, and AI Kit patterns |
| [attorney-assist](./skills/attorney-assist) | Connecting users with LegalZoom attorney consultation workflows, including plan checks, matter context gathering, topic matching, scheduling, and failure guardrails |
| [building-pydantic-ai-agents](./skills/building-pydantic-ai-agents) | Building Pydantic AI agents with tools, capabilities, structured output, streaming, YAML-defined agents, testing, hooks, and multi-agent patterns |
| [convex-design](./skills/convex-design) | Designing and building reactive, type-safe Convex backends with schemas, queries, mutations, actions, auth, storage, scheduling, real-time features, and agent workflows |
| [cosmosdb-best-practices](./skills/cosmosdb-best-practices) | Designing, reviewing, and optimizing Azure Cosmos DB NoSQL data models, partition keys, queries, SDK usage, throughput, and vector search |
| [dataproc-skills](./skills/dataproc-skills) | Managing Google Cloud Dataproc clusters and jobs through bundled Node scripts for listing, inspection, job submission, and cancellation |
| [desktop-commander-overview](./skills/desktop-commander-overview) | Using Desktop Commander MCP capabilities for persistent shells, long-running processes, broader filesystem access, structured files, search, SSH, and process management |
| [dsql](./skills/dsql) | Building with Amazon Aurora DSQL, including schemas, SQL execution, migrations, query plans, IAM auth, ORM migration, bulk loading, MCP tools, and distributed SQL patterns |
| [exa-search](./skills/exa-search) | Running Exa-powered research workflows for deep dives, lead generation, literature reviews, competitive analysis, and multi-step search synthesis |
| [firestore-data](./skills/firestore-data) | Working with Firestore collections and documents through bundled Node scripts for CRUD, data retrieval, and collection hierarchy exploration |
| [frontend-design](./skills/frontend-design) | Creating distinctive, production-grade frontend interfaces with strong visual direction, refined typography, cohesive color, motion, and polished implementation details |
| [data-analyst](./skills/data-analyst) | Acting as an interactive data analyst over ClickHouse: clarify the actual question first, then connect (local or ClickHouse Cloud) and run safe, bounded SQL via the `clickhousectl` CLI. Includes a `clickhouse` sub-skill for CLI auth (browser OAuth) and querying |

## Repository Layout

```
skills/
  cline-sdk/        -> .vendor/sdk-skill/skill/cline-sdk   (git submodule, see below)
  review-team/      Multi-reviewer code review fleet
  linear-sdk-scripting/   Drive Linear via the @linear/sdk in Node scripts
  data-analyst/           Interactive ClickHouse data analyst
    skills/clickhouse/              Sub-skill: connect + query via clickhousectl
    skills/reading-data-dict/       Sub-skill: resolve metric definitions
    skills/steering-user-elicitation/  Sub-skill: clarify before querying
    skills/analyzer/                Sub-skill: turn results into findings
    skills/plotting/                Sub-skill: charts and visual artifacts
    skills/artifact-management/     Sub-skill: save and describe outputs
    skills/clickhouse-best-practices/  -> .vendor/clickhouse-agent-skills (official, see below)
    skills/chdb-sql/                   -> .vendor/clickhouse-agent-skills
    skills/chdb-datastore/             -> .vendor/clickhouse-agent-skills
    skills/clickhousectl-local-dev/    -> .vendor/clickhouse-agent-skills
    skills/clickhousectl-cloud-deploy/ -> .vendor/clickhouse-agent-skills
    skills/clickhouse-architecture-advisor/      -> .vendor/clickhouse-agent-skills
    skills/clickhouse-js-node-coding/            -> .vendor/clickhouse-agent-skills
    skills/clickhouse-js-node-troubleshooting/   -> .vendor/clickhouse-agent-skills
.vendor/
  sdk-skill/                 Submodule of https://github.com/cline/sdk-skill
  clickhouse-agent-skills/   Submodule of https://github.com/ClickHouse/agent-skills (Apache-2.0)
```

`skills/cline-sdk` is a symlink into the [`cline/sdk-skill`](https://github.com/cline/sdk-skill) submodule, which is maintained in its own repo. The official ClickHouse skills under `skills/data-analyst/skills/` are symlinks into the [`ClickHouse/agent-skills`](https://github.com/ClickHouse/agent-skills) submodule (Apache-2.0). To pull the latest:

```
git submodule update --remote .vendor/sdk-skill
git submodule update --remote .vendor/clickhouse-agent-skills
```

## Contributing

Open a PR. New skills should follow the [Agent Skills spec](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills): a `SKILL.md` at the skill directory root with a frontmatter `name` and `description`, plus any supporting reference files.

## License

[Apache 2.0](./LICENSE)
