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
.vendor/
  sdk-skill/        Submodule of https://github.com/cline/sdk-skill
```

`skills/cline-sdk` is a symlink into the [`cline/sdk-skill`](https://github.com/cline/sdk-skill) submodule, which is maintained in its own repo. To pull the latest:

```
git submodule update --remote .vendor/sdk-skill
```

## Contributing

Open a PR. New skills should follow the [Agent Skills spec](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills): a `SKILL.md` at the skill directory root with a frontmatter `name` and `description`, plus any supporting reference files.

## License

[Apache 2.0](./LICENSE)
