# Contributing to the `skl` skill

Thanks for helping improve this skill! It teaches AI agents how to drive the
[`skl`](https://useskl.com) CLI correctly. Because agents read it literally,
**accuracy matters more than prose** — a wrong flag or command name here turns
into a wrong action by every agent that loads the skill.

## What this repo is

A single Agent Skill:

```
skl/SKILL.md            # the skill itself (frontmatter + instructions)
docs/reference/cli.md   # detailed CLI reference linked from SKILL.md
README.md               # human-facing overview
```

It documents the `skl` CLI's behavior — it does **not** contain the CLI's source.

## Ground rules

- **Match the CLI's real behavior.** Every command, flag, alias, exit code, and
  error code in `SKILL.md` / `docs/reference/cli.md` must reflect what `skl`
  actually does. If you change one, update the other so they stay in sync.
- **Keep the frontmatter valid.** `skl/SKILL.md` must keep `name`,
  `description`, and `metadata.version` (quoted). CI enforces this.
- **Bump `metadata.version`** in `skl/SKILL.md` for any change to the skill's
  content. Versions are immutable once published.
- **Keep links live.** Don't reference files that don't exist; CI checks
  relative markdown links.
- **Prefer the simplest change** that fixes the issue — small, reviewable diffs.

## Before you open a PR

Run the checks locally (same as CI):

```bash
# markdown lint (needs Node)
npx markdownlint-cli2 "**/*.md"

# SKILL.md frontmatter validation (needs Python 3)
python3 scripts/validate_skill.py
```

## Submitting changes

1. Fork and create a branch.
2. Make your change; update both `SKILL.md` and `cli.md` if behavior changed.
3. Bump `metadata.version` and add a `CHANGELOG.md` entry.
4. Open a PR using the template; describe what CLI behavior you verified.

By contributing you agree your contributions are licensed under the repo's
[MIT License](LICENSE).
