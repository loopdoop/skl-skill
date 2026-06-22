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
| `npm install <pkg>` | `skl install <name>` | add one new skill + record it |
| `npm ci` | `skl install` (no name) | rebuild everything from the manifest |
| `npm uninstall <pkg>` | `skl uninstall <name>` | remove one skill |
| `npm ls` | `skl list` | what this project installed |
| `npm view <pkg>` | `skl info <name>` | registry view of one skill |
| `package.json` | `skl.json` | the project manifest |

## Mental model (read this first)

Two command families, never mixed:

- **Project-facing** (`init`, `add`, `install`, `uninstall`, `list`, `scan`) —
  anchored to the **current directory** (no walk-up), read/write `./skl.json`,
  and land skills into the project's agent dirs.
- **Registry-facing** (`publish`, `info`) — talk to a server by **name**,
  independent of any project.
- **Machine-facing** (`login`, `logout`, `config`, `upgrade`) — manage
  credentials in `~/.skl/` and the binary itself.

Key facts that trip people up:

- **Use `skl install <name>` to add one skill** (the preferred form — mirrors
  `npm install <pkg>`). `skl add <name>` is just an alias for the same thing.
- **Bare `skl install`** (no name) re-lands everything in `skl.json` — the
  `npm ci` move. So `install` does double duty: with a name it adds one skill,
  without one it rebuilds the whole manifest.
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

`install`→`i`,`in` (and `add`,`a`) · `uninstall`→`remove`,`rm`,`un`,`r` ·
`list`→`ls`,`la`,`ll` · `publish`→`pub` · `info`→`view`,`show` · `scan`→`outdated`
· `config`→`c` · `login`→`adduser`,`add-user` · `upgrade`→`up` (`logout` has no
aliases)

The removal verb is **`uninstall`** (npm's canonical name); `remove`/`rm`/`un`/`r`
are its aliases.

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
skl login --code              # redeem a website pairing code (GitHub/Google sign-ins)
skl logout                    # forget the stored login (local only)
```

`login` signs in, mints a **device-bound** API key for *this machine*, and
stores it. Copying `~/.skl/servers.json` to another box won't work — the server
rejects it with `DEVICE_MISMATCH`; run `skl login` again there.

Passwordless social accounts (GitHub/Google) have no password to sign in with —
use `--code` to redeem a one-time **pairing code** generated on the website
(Settings → Devices → "Link a new device"); the username comes back from the
redeem. `skl logout` is the local inverse: it forgets the stored login (never
touches the network — revoke a token from the web UI instead).

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
skl init                                          # pick target agents (detected ones pre-checked)
skl init --targets claude,cursor                  # non-interactive
skl install loopdoop/asc815-memo                  # add + record, floats to latest (bootstraps skl.json if missing)
skl install loopdoop/asc815-memo@2.3.1            # pin an exact version
skl install loopdoop/asc815-memo --lock-version   # pin the resolved current version
skl install https://github.com/owner/repo         # install straight from a GitHub repo
```

Prefer `skl install <name>` to add a skill (`skl add <name>` is just an alias).
It lands the skill into **every** agent in `skl.json`'s `targets` and records
it. By default the entry **floats to latest** — there is **no prompt** about
versioning (same in CI / non-TTY). Pin instead with `--lock-version`/`-l` (pins
the resolved current version) or an explicit `@version`; `--latest` is the
explicit form of the default.

The argument can also be a **GitHub URL**
(`https://github.com/<owner>/<repo>[/tree/<ref>/<path>]`). On a TTY `skl` asks
whether to **save it to your registry as a private skill** (`--private`, needs a
logged-in account) or **install it locally only** (`--local`, no account — the
URL itself is recorded in `skl.json` and re-fetched on every rebuild).
Non-TTY / `--json` defaults to local.

### Rebuild on another machine

```bash
skl install            # re-land every skill from skl.json (the `npm ci` move)
skl install --prune    # also delete skill dirs under targets you've dropped
skl install --force    # overwrite locally-modified copies instead of skipping them
```

Pinned entries rebuild byte-identically; floating entries re-resolve to the
current version (install warns, since that isn't reproducible). Copies that are
already up to date are a no-op, and copies you've **hand-edited are skipped with
a warning** (not clobbered) unless you pass `--force`/`-f`. **Bare** `install`
(no name) is the full rebuild; passing a **name** adds that one skill (see
above).

### Inspect & maintain

```bash
skl list                 # what THIS project installed (reads skl.json)
skl info loopdoop/asc815-memo   # registry view: description, current + all versions
skl scan                 # read-only health check (drift, updates, orphans)
skl scan --offline       # fast local-only scan
skl uninstall loopdoop/asc815-memo   # (skl remove / rm also work)
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
  the entry is **pinned**; bare it **floats** to latest (the default). There is
  **no `@latest`** suffix — float by omitting `@version`. An entry may also be a
  **GitHub URL** (recorded by `skl install <url> --local`); those float and are
  re-fetched from GitHub on every rebuild.

Landing roots per target: `claude`→`.claude/skills/`, `cursor`→`.cursor/skills/`,
`copilot`→`.github/skills/`, `gemini`→`.gemini/skills/`, codex & grok →
`.agents/skills/`. Each skill lands at `<root>/<last-name-segment>/`.

---

## Command reference

| Command | What it does | Notes |
|---|---|---|
| `skl init [--targets <csv>] [-y]` | Create/reconfigure `skl.json` | re-run = reconfigure targets only |
| `skl publish <folder> [--dry-run]` | Publish a skill folder | needs login; version immutable |
| `skl install <name>[@<ver>] [--lock-version]` | Add one skill + record it (preferred) | floats to latest by default; bootstraps `skl.json` if absent; arg may be a GitHub URL; `add` is an alias |
| `skl install [--prune]` | Re-land everything from `skl.json` (no name) | the `npm ci` equivalent |
| `skl uninstall <name>` | Delete a skill's dirs + drop from manifest | local only, no network (aliases `remove`/`rm`) |
| `skl info <name>` | Registry details + versions | works logged-out for public skills |
| `skl list` | What this project installed | local only |
| `skl scan [--offline]` | Read-only health check | reports drift, never mutates (alias `outdated`) |
| `skl login [username]` | Authenticate (mints device-bound key) | the normal auth path; `--code` for GitHub/Google |
| `skl logout [username]` | Forget the stored login | local only, no network |
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
| `LOCAL_MODIFIED` (exit 1) | a landed copy was hand-edited after install (`install`/`uninstall`/`add` won't clobber it) | publish your edits first, or re-run with `--force`/`-f` to discard them |
| auth failed / 401 / 403 (exit 3) | no/invalid token, or wrong namespace | `skl login <username>`; publish only under your own username |
| `DEVICE_MISMATCH` | `servers.json` copied from another machine | run `skl login` again on **this** machine |
| not found / 404 (exit 4) | skill missing, private, or deleted | check the name; private skills need an authorized login |

## Gotchas & tips

- **Prefer `skl install <name>` to add a skill** — `skl add <name>` is just an
  alias for it. Watch the positional: `skl install <name>` adds that one skill,
  while **bare** `skl install` (no name) rebuilds everything from `skl.json`.
- **Folder-name collisions are hard errors** (no overwrite prompt) — two skills
  sharing a last name segment can't coexist.
- **`skl` never touches git.** Whether landed skill files enter the repo is the
  user's own `.gitignore`/commit decision — don't assume either way.
- **Immutability is the rule, not a bug.** Releasing an update = bump the
  version by hand, then publish. There's no overwrite.
- **Scriptable everywhere.** Every command runs non-interactively with stable
  exit codes and `--json`; safe to use in CI without a TTY.
