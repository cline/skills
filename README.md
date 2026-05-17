# Cline Skills

A collection of [Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) we use at [Cline](https://cline.bot) and want to share with the community. Skills cover the Cline SDK, code review workflows, and more.

## Installing

These skills work with any agent that supports the Agent Skills standard, including Claude Code, Cursor, OpenCode, OpenAI Codex, and Pi.

### Claude Code

Install using the [plugin marketplace](https://code.claude.com/docs/en/discover-plugins#add-from-github):

```
/plugin marketplace add cline/skills
/plugin install cline@cline
```

### Cursor

Install from the Cursor Marketplace or add manually via `Settings > Rules > Add Rule > Remote Rule (Github)` with `cline/skills`.

### npx skills

Install using the [`npx skills`](https://skills.sh) CLI:

```
npx skills add https://github.com/cline/skills
```

### Clone / Copy

Clone this repo (with submodules) and copy the skill folders into the appropriate directory for your agent:

```
git clone --recurse-submodules https://github.com/cline/skills
```

| Agent | Skill Directory | Docs |
|-------|-----------------|------|
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

## Repository Layout

```
skills/
  cline-sdk/        -> vendor/sdk-skill/skill/cline-sdk   (git submodule, see below)
  review-team/      Multi-reviewer code review fleet
vendor/
  sdk-skill/        Submodule of https://github.com/cline/sdk-skill
```

`skills/cline-sdk` is a symlink into the [`cline/sdk-skill`](https://github.com/cline/sdk-skill) submodule, which is maintained in its own repo. To pull the latest:

```
git submodule update --remote vendor/sdk-skill
```

## Contributing

Open a PR. New skills should follow the [Agent Skills spec](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills): a `SKILL.md` at the skill directory root with a frontmatter `name` and `description`, plus any supporting reference files.

## License

[Apache 2.0](./LICENSE)
