#!/usr/bin/env python3
"""PostToolUse reminder: nudge memory updates after edits to thesis-critical paths."""
import json
import sys

try:
    payload = json.load(sys.stdin)
except Exception:
    sys.exit(0)

tool_input = payload.get("tool_input", {}) or {}
path = (tool_input.get("file_path") or tool_input.get("path") or "").replace("\\", "/")
if not path:
    sys.exit(0)

thesis_critical = (
    "01 - Research Foundations/" in path
    or "02 - Novel Architecture/" in path
    or "07 - Paper Draft/" in path
)
if thesis_critical:
    print(
        "[reminder] thesis-critical edit detected — if this changes the active "
        "architecture, contributions, or venue strategy, update MEMORY.md."
    )
sys.exit(0)
