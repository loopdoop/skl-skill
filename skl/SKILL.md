---
name: skl
description: |-
  Use the skl CLI to publish, install, and manage reusable Agent Skills across
  AI coding agents (Claude, Codex, Copilot, Cursor, Gemini, Grok) — "npm for
  skills." Trigger whenever the user wants to install/add/remove/publish/share
  or "set up" Agent Skills (packaged skills in folders like .claude/skills,
  .cursor/skills, .gemini/skills), or check installed-skill health — even if
  they never type `skl`.

  Typical intents:
  - land/install the skills a skl.json manifest lists (e.g. after cloning a repo)
  - add/remove a named skill (often user/skill-name) + update the manifest and
    each agent's skills folder
  - publish/push a local skill folder so others can grab it
  - log in to useskl.com or a skl server to publish/fetch
  - scan a project for out-of-date or modified skills

  Not for writing a skill's content (use skill-creator) or unrelated package
  managers (npm/pip/etc.).
license: MIT
metadata:
  version: "1"
---

# skl — cross-harness skill distribution & management

`skl` is an npm-style CLI for **distributing and managing Agent Skills**. It
publishes a skill folder to a registry, installs skills into a project (copying
them into each agent's skills dir), and records what's installed in a
`skl.json` manifest so any machine can rebuild the same set.

Think **npm, for skills**:

| npm | skl | meaning |
|---|---|---|
| `npm publish` | `skl publish <folder>` | push a skill to the registry |
| `npm install <pkg>` | `skl add <name>` | add one new skill + record it |
| `npm ci` | `skl install` | rebuild everything from the manifest |
| `npm uninstall <pkg>` | `skl remove <name>` | remove one skill |
| `npm ls` | `skl list` | what this project installed |
| `npm view <pkg>` | `skl info <name>` | registry view of one skill |
| `package.json` | `skl.json` | the project manifest |

## Mental model (read this first)

Two command families, never mixed:

- **Project-facing** (`init`, `add`, `install`, `remove`, `list`, `scan`) —
  anchored to the **current directory** (no walk-up), read/write `./skl.json`,
  and land skills into the project's agent dirs.
- **Registry-facing** (`publish`, `info`, `fork`) — talk to a server by
  **name**, independent of any project.
- **Machine-facing** (`login`, `config`, `upgrade`) — manage credentials in
  `~/.skl/` and the binary itself.

Key facts that trip people up:
- `skl install` takes **no skill name** — it re-lands everything in `skl.json`.
  To add one skill use `skl add <name>` (npm's single `install` is split in two).
- Skills are **copied**, not symlinked, into each agent dir.
- Versions are **manual and immutable**: you bump `metadata.version` by hand;
  re-publishing the same `(skill, version)` is a hard conflict.
- The landing folder is always the skill's **last name segment**
  (`loopdoop/asc815-memo` → `asc815-memo/`). Two skills sharing a last segment
  collide.

## Before running skl on someone's behalf

- **Confirm it's installed:** `skl --version`. If missing, the binary comes from
  the install script / Homebrew / npm (`useskl`) — don't guess; ask or check.
- **Prefer `--json` when you need to parse the result.** Every command emits a
  single object: `{ "ok": true, "command": "add", ... }` on success, or
  `{ "ok": false, "error": { "code": "...", "exit": N, "message": "..." } }` on
  failure. Human (no `--json`) output is for the user to read; JSON is for you.
- **Run from the project root.** Project commands act on `./skl.json` with **no
  walk-up** — `cd` to the right directory, or pass `--cwd <path>`.
- **Don't invent versions or tokens.** Versions are author-chosen (`metadata.version`
  in `SKILL.md`); tokens come only from `skl login` / `~/.skl/` / `SKL_TOKEN`.

## Aliases (npm muscle-memory)

`add`→`a` · `install`→`i`,`in` · `remove`→`rm`,`un`,`uninstall` · `list`→`ls`
· `publish`→`pub` · `info`→`view`,`show` · `upgrade`→`up`

## Global flags (work on any command)

`--json` (machine-readable, single JSON object) · `--server <name>` (pick a
named server) · `--registry <url>` (one-shot registry override) · `--cwd <path>`
(treat path as project root, still no walk-up) · `-q/--quiet` · `--verbose` ·
`--no-color` · `-h/--help` · `-v/--version`.

> There is **no `--token` flag** (it would leak into shell history). Tokens come
> only from `skl login`, `~/.skl/`, or the `SKL_TOKEN` env var.

Exit codes: `0` success · `1` runtime error · `2` usage error. (CI-friendly
semantic subdivisions exist: `3` auth/config, `4` not-found, `5` conflict.)

---

## Common workflows

### Authenticate (needed for publishing and private skills)

```bash
skl login <username>          # prompts for password, mints a device-bound key
skl login alice --registry https://skl.example.dev
```

`login` signs in, mints a **device-bound** API key for *this machine*, and
stores it. Copying `~/.skl/servers.json` to another box won't work — the server
rejects it with `DEVICE_MISMATCH`; run `skl login` again there.

Reading/installing a **public** skill needs no login (anonymous works). A
**private** skill always needs a token.

### Publish a skill

```bash
skl publish ./my-skill              # folder must contain SKILL.md
skl publish ./my-skill --dry-run    # validate + pack, no upload, no token needed
```

The published name is `<your-username>/<name-in-SKILL.md>` — the **folder name
is ignored**. `SKILL.md` frontmatter must have `name`, `description`, and
`metadata.version` (quote it: `metadata.version: "1.10"`). To release an
update, **bump `metadata.version` by hand** and publish again — re-publishing an
existing version fails (immutable).

### Start a project & add skills

```bash
skl init                                  # pick target agents (detected ones pre-checked)
skl init --targets claude,cursor          # non-interactive
skl add loopdoop/asc815-memo              # add + record (bootstraps skl.json if missing)
skl add loopdoop/asc815-memo@2.3.1        # pin an exact version
skl add loopdoop/asc815-memo --latest     # track latest (floating)
```

`add` lands the skill into **every** agent in `skl.json`'s `targets` and records
it. Bare `add` (interactive) asks whether to **pin** the resolved version or
track **latest**; non-interactive runs **pin by default**.

### Rebuild on another machine

```bash
skl install            # re-land every skill from skl.json (the `npm ci` move)
skl install --prune    # also delete skill dirs under targets you've dropped
```

Pinned entries rebuild byte-identically; floating entries re-resolve to the
current version (install warns, since that isn't reproducible).

### Inspect & maintain

```bash
skl list                 # what THIS project installed (reads skl.json)
skl info loopdoop/asc815-memo   # registry view: description, current + all versions
skl scan                 # read-only health check (drift, updates, orphans)
skl scan --offline       # fast local-only scan
skl remove loopdoop/asc815-memo
```

`skl scan` mutates nothing — it reports local edits (digest drift), available
registry updates, missing/orphan folders, and prints the command to fix each.

### Manage servers / upgrade

```bash
skl config                                   # show active server + effective config
skl config add lan --registry http://skl.lan:8787   # prompts for a pasted token
skl config use lan                           # switch active server
skl config list
skl upgrade                                  # update the skl binary to latest
skl upgrade --check                          # report current vs latest only
```

`skl login` is the normal way to authenticate (mints a key). `skl config` only
**stores a token you paste** — the advanced / self-hosted path.

---

## `skl.json` — the project manifest

Created by `skl init` (or bootstrapped by the first `skl add`). Lives at the
project root; portable and **credential-free** (no server/token in it).

```json
{
  "schemaVersion": 1,
  "targets": ["claude", "cursor"],
  "skills": [
    "loopdoop/asc815-memo@2.3.1",
    "tanker/x-tract"
  ]
}
```

- `targets` — which agents skills land into. Six ids:
  `claude`, `codex`, `copilot`, `cursor`, `gemini`, `grok`.
  (codex and grok share `.agents/skills/`.) Project-wide, **not** a per-`add`
  flag; change it by re-running `skl init`, then `skl install`.
- `skills` — a **string array** of `"username/skill[@version]"`. With `@version`
  the entry is **pinned**; bare it **floats** to latest. There is **no
  `@latest`** suffix — float by omitting `@version`.

Landing roots per target: `claude`→`.claude/skills/`, `cursor`→`.cursor/skills/`,
`copilot`→`.github/skills/`, `gemini`→`.gemini/skills/`, codex & grok →
`.agents/skills/`. Each skill lands at `<root>/<last-name-segment>/`.

---

## Command reference

| Command | What it does | Notes |
|---|---|---|
| `skl init [--targets <csv>] [-y]` | Create/reconfigure `skl.json` | re-run = reconfigure targets only |
| `skl publish <folder> [--dry-run]` | Publish a skill folder | needs login; version immutable |
| `skl add <name>[@<ver>] [--latest]` | Add one skill + record it | bootstraps `skl.json` if absent |
| `skl install [--prune]` | Re-land everything from `skl.json` | the `npm ci` equivalent; no name arg |
| `skl remove <name>` | Delete a skill's dirs + drop from manifest | local only, no network |
| `skl info <name>` | Registry details + versions | works logged-out for public skills |
| `skl list` | What this project installed | local only |
| `skl scan [--offline]` | Read-only health check | reports drift, never mutates |
| `skl fork <name>` | Fork a skill into your namespace | server-side, needs login |
| `skl login [username]` | Authenticate (mints device-bound key) | the normal auth path |
| `skl config [use\|add\|set\|rm\|list]` | Manage named servers | stores pasted tokens only |
| `skl upgrade [--check]` | Update the `skl` binary | detects install method |

Run `skl <command> --help` for the full per-command help, and add `--json` to
any command for scriptable output (`{ "ok": true, ... }` / `{ "ok": false,
"error": {...} }`).

## When a command fails — what to do

`skl` errors are designed to hand you the next action. Common ones:

| Error / `code` | What it means | Fix |
|---|---|---|
| `No skl.json in this directory` | project command run outside a project | `skl init` here, or `cd` / `--cwd` to the root |
| `VERSION_EXISTS` (exit 5) | re-publishing an existing `(skill, version)` | bump `metadata.version` in `SKILL.md`, publish again |
| `MISSING_VERSION` | `SKILL.md` has no `metadata.version` | add `metadata.version: "1"` (quoted) |
| `DIR_COLLISION` | another skill already owns that landing folder | `skl remove` the conflicting skill first |
| auth failed / 401 / 403 (exit 3) | no/invalid token, or wrong namespace | `skl login <username>`; publish only under your own username |
| `DEVICE_MISMATCH` | `servers.json` copied from another machine | run `skl login` again on **this** machine |
| not found / 404 (exit 4) | skill missing, private, or deleted | check the name; private skills need an authorized login |

## Gotchas & tips

- **`skl i <name>` does nothing useful** — `install` takes no positional. Use
  `skl add <name>` to add one skill; `skl install` rebuilds everything.
- **Folder-name collisions are hard errors** (no overwrite prompt) — two skills
  sharing a last name segment can't coexist.
- **`skl` never touches git.** Whether landed skill files enter the repo is the
  user's own `.gitignore`/commit decision — don't assume either way.
- **Immutability is the rule, not a bug.** Releasing an update = bump the
  version by hand, then publish. There's no overwrite.
- **Scriptable everywhere.** Every command runs non-interactively with stable
  exit codes and `--json`; safe to use in CI without a TTY.
