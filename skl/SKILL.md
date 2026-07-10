---
name: skl
description: |-
  Use the skl CLI to publish, install, and manage reusable Agent Skills across
  AI coding agents (Claude, Copilot, Cursor, Gemini, Junie, Kiro, plus the
  cross-agent .agents/skills standard used by Codex, Zed, Goose, Amp, OpenCode,
  Roo, pi, and Grok) — "the Agent Skills manager." Trigger whenever the user
  wants to install/add/remove/publish/save/share or "set up" Agent Skills
  (packaged skills in folders like .claude/skills, .cursor/skills,
  .agents/skills), or check installed-skill health — even if they never type
  `skl`.

  Typical intents:
  - land/install the skills a skl.json manifest lists (e.g. after cloning a repo)
  - add/remove a named skill (often user/skill-name) + update the manifest and
    each agent's skills folder
  - install a skill for the whole machine (user-level, `-g`) instead of one project
  - publish/push a local skill folder so others can grab it, or save it privately
  - install a skill straight from a GitHub repo URL
  - log in to useskl.com or a skl server to publish/fetch
  - scan a project for out-of-date or modified skills

  Not for writing a skill's content (use skill-creator) or unrelated package
  managers (npm/pip/etc.).
license: MIT
metadata:
  version: "3"
---

# skl — the Agent Skills manager

`skl` is an npm-style CLI for **managing Agent Skills across agents**. It
publishes a skill folder to a registry, installs skills into a project (copying
them into each agent's skills dir), and records what's installed in a
`skl.json` manifest so any machine can rebuild the same set.

Think **npm, for skills**:

| npm | skl | meaning |
|---|---|---|
| `npm publish` | `skl publish <folder>` | push a skill to the registry (public) |
| — | `skl save <folder>` | same, but **private** (only you see it) |
| `npm install <pkg>` | `skl install <name>` | add one new skill + record it |
| `npm ci` | `skl install` (no name) | rebuild everything from the manifest |
| `npm i -g <pkg>` | `skl install <name> -g` | user-level install (whole machine) |
| `npm uninstall <pkg>` | `skl uninstall <name>` | remove one skill |
| `npm ls` | `skl list` | what this project installed |
| `npm view <pkg>` | `skl info <name>` | registry view of one skill |
| `package.json` | `skl.json` | the project manifest |

## Mental model (read this first)

Three command families, never mixed:

- **Project-facing** (`init`, `install`, `uninstall`, `list`, `scan`) —
  anchored to the **current directory** (no walk-up), read/write `./skl.json`,
  and land skills into the project's agent dirs.
- **Registry-facing** (`publish`, `save`, `info`) — talk to a server by
  **path or name**, independent of any project.
- **Machine-facing** (`login`, `logout`, `config`, `upgrade`) — manage
  credentials in `~/.skl/` and the binary itself.

Key facts that trip people up:

- **Use `skl install <name>` to add one skill** (mirrors `npm install <pkg>`).
  `skl add <name>` is just an alias for the same thing.
- **Bare `skl install`** (no name) re-lands everything in `skl.json` — the
  `npm ci` move. So `install` does double duty: with a name it adds one skill,
  without one it rebuilds the whole manifest.
- **`-g`/`--global` installs are untracked.** They land into each agent's
  *personal* dir under `$HOME` (e.g. `~/.claude/skills/`), touch no `skl.json`,
  and can't be rebuilt or `uninstall -g`'d — delete the folder to remove one.
- Skills are **copied**, not symlinked, into each agent dir.
- Versions are **manual and immutable**: you bump `metadata.version` by hand;
  re-publishing the same `(skill, version)` is a hard conflict.
- The landing folder is always the skill's **last name segment**
  (`loopdoop/asc815-memo` → `asc815-memo/`). Two skills sharing a last segment
  collide.
- **Seven target ids**: `claude`, `copilot`, `cursor`, `gemini`, `junie`,
  `kiro`, `agents`. `agents` is the cross-agent `.agents/skills/` standard
  (Codex, Zed, Goose, Amp, OpenCode, Roo, pi, Grok — one id covers them all).
  Legacy `codex`/`grok` ids still parse and mean `agents`.

## Before running skl on someone's behalf

- **Confirm it's installed:** `skl --version`. If missing, the binary comes from
  the install script / Homebrew / npm (`useskl`) — don't guess; ask or check.
- **Prefer `--json` when you need to parse the result.** Every command emits a
  single object: `{ "ok": true, "command": "install", ... }` on success, or
  `{ "ok": false, "error": { "code": "...", "exit": N, "message": "..." } }` on
  failure. Human (no `--json`) output is for the user to read; JSON is for you.
- **Run from the project root.** Project commands act on `./skl.json` with **no
  walk-up** — `cd` to the right directory, or pass `--cwd <path>`.
- **Don't invent versions or tokens.** Versions are author-chosen (`metadata.version`
  in `SKILL.md`); tokens come only from `skl login` / `~/.skl/` / `SKL_TOKEN`.

## Aliases (npm muscle-memory)

`install`→`i`,`in`,`a`,`add` · `uninstall`→`remove`,`rm`,`un`,`r` ·
`list`→`ls`,`la`,`ll` · `publish`→`pub` · `info`→`view`,`show` · `scan`→`outdated`
· `config`→`c` · `login`→`adduser`,`add-user` · `upgrade`→`up` (`save` and
`logout` have no aliases)

The removal verb is **`uninstall`** (npm's canonical name); `remove`/`rm`/`un`/`r`
are its aliases. There is deliberately **no `update`→`upgrade` alias**:
`skl upgrade` updates the *binary*; updating *skills* is `skl install`.

## Global flags (work on any command)

`--json` (machine-readable, single JSON object) · `--server <name>` (pick a
named server) · `--registry <url>` (one-shot registry override) · `--cwd <path>`
(treat path as project root, still no walk-up) · `-q/--quiet` · `--verbose` ·
`--no-color` · `-h/--help` · `-v/--version`.

> There is **no `--token` flag** (it would leak into shell history). Tokens come
> only from `skl login`, `~/.skl/`, or the `SKL_TOKEN` env var.

Exit codes: `0` success · `1` runtime error · `2` usage error. (CI-friendly
semantic subdivisions exist: `3` auth/config, `4` not-found, `5` conflict.)

After a successful command on a TTY, skl may print a one-line **update notice**
on stderr (a passive daily check of `~/.skl/update-check.json`). It's
informational only — suppressed under `--json`/`--quiet`/CI/non-TTY, or set
`SKL_NO_UPDATE_CHECK=1` to disable it entirely.

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
redeem. A bare interactive `skl login` offers the password-vs-code picker.
`skl logout` is the local inverse: it forgets the stored login (never touches
the network — revoke a token from the web UI instead).

Reading/installing a **public** skill needs no login (anonymous works). A
**private** skill always needs a token.

### Publish (public) or save (private) a skill

```bash
skl publish ./my-skill              # public — folder must contain SKILL.md
skl publish ./my-skill --private    # publish as private instead
skl publish ./my-skill --dry-run    # validate + pack, no upload, no token needed
skl save ./my-skill                 # same as publish --private (friendlier verb)
```

The published name is `<your-username>/<name-in-SKILL.md>` — the **folder name
is ignored**. `SKILL.md` frontmatter must have `name`, `description`, and
`metadata.version` (quote it: `metadata.version: "1.10"`). To release an
update, **bump `metadata.version` by hand** and publish again — re-publishing an
existing version fails (immutable). On a TTY, publish helps: a missing version
offers a suggestion (`1` for a new skill, or the next after your last publish)
and lets you type your own; a version conflict offers to bump to the next
suggestion — both require your consent (non-TTY/`--json` just error).

`skl save` is the privacy-first spelling of `skl publish --private`: it uploads
the skill visible **only to you**. Make it public later from the website.

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

`skl init` shows a **detection-first picker**: only agents it detects in the
project/home dir (with `claude` always pre-checked), plus a "Show all…"
expander for the full list of seven.

The argument can also be a **GitHub URL**
(`https://github.com/<owner>/<repo>[/tree/<ref>/<path>]`). On a TTY `skl` asks
whether to **save it to your registry as a private skill** (`--private`, needs a
logged-in account) or **install it locally only** (`--local`, no account — the
URL itself is recorded in `skl.json` and re-fetched on every rebuild).
Non-TTY / `--json` defaults to local.

### Install for the whole machine (user-level, `-g`)

```bash
skl install loopdoop/asc815-memo -g                    # into ~/.claude/skills/ etc.
skl install loopdoop/asc815-memo -g --targets claude   # skip the target prompt
```

`-g`/`--global` lands the skill into each agent's **personal** skills dir under
`$HOME` (`~/.claude/skills/`, `~/.agents/skills/`, `~/.cursor/skills/`, …;
copilot's global root is `~/.copilot/skills/`, unlike its project root) so every
project on the machine sees it — the `npm i -g` move. On a TTY it prompts for
targets with the same detection-first picker as `init`; `--targets` skips the
prompt; non-TTY falls back to `claude`. Global installs are **untracked**: no
`skl.json` is read or written, so there's no rebuild and no `uninstall -g` —
remove one by deleting its folder. GitHub URLs and bare `skl install -g` are
not supported globally.

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
`skl uninstall` refuses to destroy a landed copy you've **edited since install**
(your edits may be unpublished) — re-run with `--force` to discard them.

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

Created by `skl init` (or bootstrapped by the first `skl install <name>`).
Lives at the project root; portable and **credential-free** (no server/token in
it).

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

- `targets` — which agents skills land into. Seven ids:
  `claude`, `copilot`, `cursor`, `gemini`, `junie`, `kiro`, `agents`.
  `agents` is the shared `.agents/skills/` standard (Codex, Zed, Goose, Amp,
  OpenCode, Roo, pi, Grok). Legacy `codex`/`grok` entries still parse and mean
  `agents`. Project-wide, **not** a per-install flag; change it by re-running
  `skl init`, then `skl install`.
- `skills` — a **string array** of `"username/skill[@version]"`. With `@version`
  the entry is **pinned**; bare it **floats** to latest (the default). There is
  **no `@latest`** suffix — float by omitting `@version`. An entry may also be a
  **GitHub URL** (recorded by `skl install <url> --local`); those float and are
  re-fetched from GitHub on every rebuild.

Landing roots per target (project-level): `claude`→`.claude/skills/`,
`copilot`→`.github/skills/`, `cursor`→`.cursor/skills/`,
`gemini`→`.gemini/skills/`, `junie`→`.junie/skills/`, `kiro`→`.kiro/skills/`,
`agents`→`.agents/skills/`. Each skill lands at `<root>/<last-name-segment>/`.
(User-level `-g` roots are the same under `$HOME`, except copilot →
`~/.copilot/skills/`.)

---

## Command reference

| Command | What it does | Notes |
|---|---|---|
| `skl init [--targets <csv>] [-y]` | Create/reconfigure `skl.json` | re-run = reconfigure targets only |
| `skl publish <folder> [--dry-run] [--private\|--public]` | Publish a skill folder (public by default) | needs login; version immutable |
| `skl save <folder> [--dry-run]` | Publish as **private** | = `publish --private`; no aliases |
| `skl install <name>[@<ver>] [--lock-version] [-g]` | Add one skill + record it (preferred) | floats to latest by default; bootstraps `skl.json` if absent; arg may be a GitHub URL; `add` is an alias; `-g` = user-level, untracked |
| `skl install [--prune] [--force]` | Re-land everything from `skl.json` (no name) | the `npm ci` equivalent; skips hand-edited copies unless `--force` |
| `skl uninstall <name> [--force]` | Delete a skill's dirs + drop from manifest | local only, no network (aliases `remove`/`rm`); `--force` discards local edits |
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
| `VERSION_EXISTS` (exit 5) | re-publishing an existing `(skill, version)` | bump `metadata.version` in `SKILL.md`, publish again (TTY offers the bump) |
| `MISSING_VERSION` | `SKILL.md` has no `metadata.version` | add `metadata.version: "1"` (quoted; TTY offers to add it) |
| `DIR_COLLISION` | another skill already owns that landing folder | `skl uninstall` the conflicting skill first |
| `LOCAL_MODIFIED` (exit 1) | a landed copy was hand-edited after install (`install`/`uninstall` won't clobber it) | publish/save your edits first, or re-run with `--force`/`-f` to discard them |
| auth failed / 401 / 403 (exit 3) | no/invalid token, or wrong namespace | `skl login <username>`; publish only under your own username |
| `DEVICE_MISMATCH` | `servers.json` copied from another machine | run `skl login` again on **this** machine |
| not found / 404 (exit 4) | skill missing, private, or deleted | check the name; private skills need an authorized login |
| `INVALID_TARGET` (exit 2) | unknown id in `--targets` | valid: claude, copilot, cursor, gemini, junie, kiro, agents (legacy codex/grok accepted) |

## Gotchas & tips

- **Prefer `skl install <name>` to add a skill** — `skl add <name>` is just an
  alias for it. Watch the positional: `skl install <name>` adds that one skill,
  while **bare** `skl install` (no name) rebuilds everything from `skl.json`.
- **Codex/Grok/Zed/Goose/etc. are all the `agents` target.** They read the
  shared `.agents/skills/` dir — one target id covers the whole family. Don't
  look for a `codex` or `zed` target; legacy `codex`/`grok` ids just map to it.
- **Folder-name collisions are hard errors** (no overwrite prompt) — two skills
  sharing a last name segment can't coexist.
- **`skl` never touches git.** Whether landed skill files enter the repo is the
  user's own `.gitignore`/commit decision — don't assume either way.
- **Immutability is the rule, not a bug.** Releasing an update = bump the
  version by hand, then publish. There's no overwrite.
- **Private-first when unsure.** `skl save` uploads a skill only you can see;
  flip it public later on the website. Website-side saves default private too.
- **Global (`-g`) installs leave no manifest.** Nothing records them; `scan`,
  `list`, and rebuilds don't see them. Use project installs for anything a team
  should reproduce.
- **Scriptable everywhere.** Every command runs non-interactively with stable
  exit codes and `--json`; safe to use in CI without a TTY.
