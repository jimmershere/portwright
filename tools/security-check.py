#!/usr/bin/env python3
"""Static security scan for the portwright.io site (stdlib only).

Fails the build on committed secrets, mixed-content (http://) resources, and
javascript: URIs. Warns on CSP-unfriendly inline event handlers. Runs before
anything is allowed near the deploy gate.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", "node_modules", ".github"}
TEXT_SUFFIXES = {".html", ".htm", ".css", ".js", ".json", ".md", ".txt", ".yml", ".yaml", ".svg"}

SECRET_PATTERNS = [
    ("GitHub token", re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}")),
    ("AWS access key id", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("Private key block", re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA |PGP )?PRIVATE KEY-----")),
    ("OpenAI key", re.compile(r"sk-[A-Za-z0-9]{20,}")),
    ("Slack token", re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}")),
    ("Generic secret assignment", re.compile(r"(?i)(secret|password|passwd|api[_-]?key|token)\s*[:=]\s*['\"][^'\"]{12,}['\"]")),
]
MIXED_CONTENT = re.compile(r"""(?:src|href)\s*=\s*["']http://[^"']+""", re.I)
JS_URI = re.compile(r"""(?:src|href)\s*=\s*["']javascript:""", re.I)
INLINE_HANDLER = re.compile(r"""\son[a-z]+\s*=\s*["']""", re.I)


def _iter_text_files():
    for path in ROOT.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
            yield path


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    for path in _iter_text_files():
        rel = path.relative_to(ROOT)
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        is_html = path.suffix.lower() in {".html", ".htm"}
        for line_no, line in enumerate(text.splitlines(), 1):
            for name, pattern in SECRET_PATTERNS:
                if pattern.search(line):
                    errors.append(f"{rel}:{line_no}: possible {name} committed")
            if is_html:
                if MIXED_CONTENT.search(line):
                    errors.append(f"{rel}:{line_no}: insecure http:// resource (mixed content)")
                if JS_URI.search(line):
                    errors.append(f"{rel}:{line_no}: javascript: URI")
                if INLINE_HANDLER.search(line):
                    warnings.append(f"{rel}:{line_no}: inline event handler (CSP-unfriendly)")

    for warning in warnings:
        print(f"::warning::{warning}")
    if errors:
        print("Security check FAILED:")
        for error in errors:
            print(f"  - {error}")
        return 1
    suffix = "no warnings" if not warnings else f"{len(warnings)} warning(s)"
    print(f"Security check passed ({suffix}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
