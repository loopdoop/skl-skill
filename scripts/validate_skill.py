#!/usr/bin/env python3
"""Validate every SKILL.md's YAML frontmatter.

A skill is only publishable if its frontmatter carries `name`, `description`,
and a *quoted* `metadata.version`. This catches the MISSING_VERSION / invalid
-name class of `skl publish` failures before they ship. Run from the repo root:

    python3 scripts/validate_skill.py
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - surfaced as a clear CI message
    sys.exit("PyYAML is required: pip install pyyaml")

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("validate_skill")

REPO_ROOT = Path(__file__).resolve().parent.parent
NAME_MAX_LEN = 64
RESERVED_SEGMENT = "col"


def extract_frontmatter(text: str) -> dict | None:
    """Return the parsed YAML frontmatter block, or None if absent/malformed."""
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    loaded = yaml.safe_load(parts[1])
    return loaded if isinstance(loaded, dict) else None


def validate(path: Path) -> list[str]:
    """Return a list of human-readable problems for one SKILL.md (empty == ok)."""
    log.debug("checking %s", path)
    fm = extract_frontmatter(path.read_text(encoding="utf-8"))
    if fm is None:
        return ["no valid YAML frontmatter block (--- ... ---)"]

    problems: list[str] = []

    name = fm.get("name")
    if not name or not isinstance(name, str):
        problems.append("missing 'name'")
    elif len(name) > NAME_MAX_LEN or name == RESERVED_SEGMENT:
        problems.append(f"invalid 'name': {name!r}")

    if not fm.get("description"):
        problems.append("missing 'description'")

    metadata = fm.get("metadata")
    version = metadata.get("version") if isinstance(metadata, dict) else None
    if version is None:
        problems.append("missing 'metadata.version'")
    elif not isinstance(version, str):
        # YAML loaded it as a number -> it wasn't quoted ("1.10" became 1.1).
        problems.append(f"'metadata.version' must be quoted (got {version!r})")

    return problems


def main() -> int:
    skill_files = sorted(REPO_ROOT.glob("**/SKILL.md"))
    if not skill_files:
        log.error("✗ no SKILL.md found under %s", REPO_ROOT)
        return 1

    failed = False
    for path in skill_files:
        rel = path.relative_to(REPO_ROOT)
        problems = validate(path)
        if problems:
            failed = True
            log.error("✗ %s", rel)
            for problem in problems:
                log.error("    - %s", problem)
        else:
            log.info("✓ %s", rel)

    if failed:
        log.error("\nFrontmatter validation failed.")
        return 1
    log.info("\nAll SKILL.md frontmatter is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
