#!/usr/bin/env python3
"""PreToolUse guard: block edits to vault internals and Untitled cruft."""
import json
import re
import sys

try:
    payload = json.load(sys.stdin)
except Exception:
    sys.exit(0)

tool_input = payload.get("tool_input", {}) or {}
path = tool_input.get("file_path") or tool_input.get("path") or ""
if not path:
    sys.exit(0)

norm = path.replace("\\", "/")
basename = norm.rsplit("/", 1)[-1]

blocked_patterns = [
    (r"(^|/)\.obsidian(/|$)", "edits to .obsidian/ are blocked (Obsidian config)"),
    (r"(^|/)\.obsidian-skills(/|$)", "edits to .obsidian-skills/ are blocked"),
    (r"(^|/)\.git(/|$)", "edits to .git/ are blocked"),
]
for pattern, reason in blocked_patterns:
    if re.search(pattern, norm):
        print(f"BLOCKED: {reason}", file=sys.stderr)
        sys.exit(2)

if re.match(r"^Untitled.*\.(md|canvas)$", basename, re.IGNORECASE):
    print(
        f"BLOCKED: refusing to edit '{basename}' — Untitled* files are Obsidian cruft. "
        "Create a properly named file instead, or ask the user to rename first.",
        file=sys.stderr,
    )
    sys.exit(2)

sys.exit(0)
