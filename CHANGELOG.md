# Changelog

All notable changes to the `skl` skill are documented here. The skill's own
version lives in `skl/SKILL.md` frontmatter (`metadata.version`).

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [2] — 2026-07-10

### Changed

- Targets updated to the seven canonical ids (`claude`, `copilot`, `cursor`,
  `gemini`, `junie`, `kiro`, `agents`): `agents` is the cross-agent
  `.agents/skills/` standard covering Codex, Zed, Goose, Amp, OpenCode, Roo,
  pi, and Grok; legacy `codex`/`grok` ids canonicalize to it (ADR-0078).
  Landing-roots table and `INVALID_TARGET` guidance updated to match.
- Repositioned from "npm for skills" to "the Agent Skills manager" (matches the
  CLI's own help header).
- `skl init` / bootstrap / `-g` target selection described as the
  detection-first picker (detected agents + "Show all…" expander).
- Publish flow now covers the interactive helpers (offer to add a missing
  `metadata.version`, offer to bump on a version conflict) and the
  `--private`/`--public` flags.
- `docs/reference/cli.md` resynced with the upstream skl reference
  (2026-07-09 state).

### Added

- `skl save <folder>` — publish-as-private — in the command table, workflows,
  and npm-mapping table.
- User-level installs: `skl install <name> -g/--global` into the harness
  personal dirs (`~/.claude/skills/`, …; copilot → `~/.copilot/skills/`),
  untracked (ADR-0074/0075).
- `skl uninstall --force` and the `LOCAL_MODIFIED` uninstall guard.
- The passive daily update notice and `SKL_NO_UPDATE_CHECK` opt-out (ADR-0080).
- Gotchas for the `agents` target family, private-first saving, and untracked
  global installs.
- `docs/reference/cli.md` — full CLI reference linked from `SKILL.md` and `README.md`.
- Repo scaffolding for public release: `.gitignore`, `CONTRIBUTING.md`,
  GitHub issue/PR templates, and a CI workflow that lints markdown and validates
  `SKILL.md` frontmatter.

## [1] — initial

### Added

- `skl/SKILL.md` — the skill: command surface, project-vs-registry model,
  `skl.json` manifest, error recovery.
- `README.md`, `LICENSE` (MIT).
