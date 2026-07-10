# skl skill

An Agent Skill for driving the **skl** CLI — the Agent Skills manager: an
npm-style tool for publishing, installing, and managing Agent Skills across
harnesses (Claude, Copilot, Cursor, Gemini, Junie, Kiro, and the cross-agent
`.agents/skills/` standard used by Codex, Zed, Goose, Amp, OpenCode, Roo, pi,
and Grok). The skill is itself harness-agnostic: it's plain `SKILL.md`
instructions any of those agents can load.

It teaches an agent the command surface, the project-vs-registry mental model,
the `skl.json` manifest, and how to recover from the common errors so `skl`
commands run correctly the first time.

See [`skl/SKILL.md`](skl/SKILL.md) for the full instructions.
Reference: [`docs/reference/cli.md`](docs/reference/cli.md).
