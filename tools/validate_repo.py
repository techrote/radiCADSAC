#!/usr/bin/env python3
"""Lightweight deterministic validation for the radiCADSAC genesis repository."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "README.md",
    "AGENTS.md",
    "docs/00-FOUNDING-BRIEF.md",
    "docs/01-MSAC-GEOMETRY-CONTRACT.md",
    "docs/04-REVISED-RESEARCH-ROADMAP.md",
    "docs/06-RESEARCH-METHOD.md",
]

errors: list[str] = []

for rel in REQUIRED:
    if not (ROOT / rel).is_file():
        errors.append(f"missing required file: {rel}")

markdown_files = sorted(ROOT.rglob("*.md"))
if not markdown_files:
    errors.append("repository contains no Markdown research corpus")

local_link = re.compile(r"\[[^\]]+\]\((?!https?://|mailto:|#)([^)#]+)(?:#[^)]+)?\)")

for path in markdown_files:
    rel = path.relative_to(ROOT)
    text = path.read_text(encoding="utf-8")
    if "\t" in text:
        errors.append(f"{rel}: contains tab characters")
    for lineno, line in enumerate(text.splitlines(), 1):
        trailing_spaces = len(line) - len(line.rstrip(" "))
        # Two trailing spaces are the standard Markdown hard-line-break syntax.
        if trailing_spaces not in (0, 2):
            errors.append(
                f"{rel}:{lineno}: accidental trailing whitespace "
                f"({trailing_spaces} spaces)"
            )
    for match in local_link.finditer(text):
        target = match.group(1).strip()
        if not target or target.startswith(("plugin://", "sandbox:")):
            continue
        resolved = (path.parent / target).resolve()
        try:
            resolved.relative_to(ROOT.resolve())
        except ValueError:
            errors.append(f"{rel}: local link escapes repository: {target}")
            continue
        if not resolved.exists():
            errors.append(f"{rel}: broken local link: {target}")

if errors:
    print("radiCADSAC validation failed:")
    for error in errors:
        print(f" - {error}")
    sys.exit(1)

print(f"radiCADSAC validation passed ({len(markdown_files)} Markdown files checked)")
