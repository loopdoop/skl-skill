# skl skill

An [Agent Skill](https://useskl.com/docs) that teaches AI coding agents how to
drive the **[skl](https://useskl.com)** CLI — the Agent Skills manager.

With this skill loaded, an agent can run `skl` correctly the first time: it
knows the command surface, the project-vs-registry mental model, the `skl.json`
manifest, and how to recover from the common errors — so you can say things
like *"install the skills this repo needs"* or *"publish this skill folder"*
and get the right commands, not guesses.

## What is skl?

[skl](https://useskl.com) is an npm-style CLI for managing Agent Skills across
AI coding agents. It publishes a skill folder to a registry, installs skills
into a project (copying them into each agent's skills directory), and records
what's installed in a `skl.json` manifest so any machine can rebuild the same
set. It works across Claude, Copilot, Cursor, Gemini, Junie, Kiro, and the
cross-agent `.agents/skills/` standard (Codex, Zed, Goose, Amp, OpenCode, Roo,
pi, Grok).

## Install this skill

The skill is published on the registry as
[`skl/skl`](https://useskl.com/skills/skl/skl) — so skl can install it, into
whichever agents you use:

```bash
# into this project (records it in skl.json)
skl install skl/skl

# or for the whole machine (e.g. ~/.claude/skills/)
skl install skl/skl -g
```

No skl yet? Grab it first at [useskl.com](https://useskl.com), or copy
[`skl/SKILL.md`](skl/SKILL.md) into your agent's skills directory by hand —
the skill is plain Markdown any agent can load.

## What the agent learns

- **The mental model** — project-facing commands (`init`, `install`,
  `uninstall`, `list`, `scan`) vs registry-facing (`publish`, `save`, `info`)
  vs machine-facing (`login`, `logout`, `config`, `upgrade`), and why bare
  `skl install` rebuilds everything while `skl install <name>` adds one skill.
- **The `skl.json` manifest** — targets, pinned vs floating versions, GitHub
  URL entries, and where each agent's skills actually land on disk.
- **Safe automation habits** — use `--json` for parseable output, respect
  stable exit codes, never invent versions or tokens, run from the project
  root.
- **Error recovery** — what `VERSION_EXISTS`, `DIR_COLLISION`,
  `LOCAL_MODIFIED`, `DEVICE_MISMATCH`, and friends mean, and the exact command
  that fixes each.

## Repo layout

| Path | What it is |
|---|---|
| [`skl/SKILL.md`](skl/SKILL.md) | The skill itself — frontmatter + instructions agents load |
| [`docs/reference/cli.md`](docs/reference/cli.md) | The detailed CLI reference the skill links to |
| [`scripts/validate_skill.py`](scripts/validate_skill.py) | CI check that the skill's frontmatter stays valid |
| [`CHANGELOG.md`](CHANGELOG.md) | What changed in each published version |

## Contributing

Agents read this skill literally, so **accuracy beats prose** — a wrong flag
here becomes a wrong command in every agent that loads it. See
[`CONTRIBUTING.md`](CONTRIBUTING.md) for the ground rules and how to run the
CI checks locally.

## License

[MIT](LICENSE)
