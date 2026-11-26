#!/bin/bash
# Compile .po → .mo and emit browser JSON catalogs under locale/json/.
set -euo pipefail

LOCALE_DIR="$(cd "$(dirname "$0")" && pwd)"
MGMT_DIR="$(cd "$LOCALE_DIR/.." && pwd)"
cd "$MGMT_DIR"

PYBABEL="${PYBABEL:-}"
if [ -z "$PYBABEL" ]; then
	if command -v pybabel >/dev/null 2>&1; then
		PYBABEL=pybabel
	elif [ -x /usr/local/lib/mailinabox/env/bin/pybabel ]; then
		PYBABEL=/usr/local/lib/mailinabox/env/bin/pybabel
	else
		echo "pybabel not found. Install Babel or set PYBABEL=." >&2
		exit 1
	fi
fi

"$PYBABEL" compile -d locale -D messages

python3 <<'PY'
"""Emit locale/json/<lang>.json from each messages.po (msgid → msgstr)."""
import json
import os
from pathlib import Path

try:
	from babel.messages.pofile import read_po
except ImportError:
	raise SystemExit("Babel is required to compile JSON catalogs")

locale_dir = Path(__file__).resolve().parent if False else Path("locale")
# __file__ unavailable in heredoc; use cwd-relative locale/
locale_dir = Path("locale")
json_dir = locale_dir / "json"
json_dir.mkdir(parents=True, exist_ok=True)

for po_path in sorted(locale_dir.glob("*/LC_MESSAGES/messages.po")):
	lang = po_path.parts[-3]
	with po_path.open(encoding="utf-8") as f:
		catalog = read_po(f)
	out = {}
	for message in catalog:
		if not message.id or message.id == "":
			continue
		# Skip plural forms for the simple JSON map; tn() falls back to English
		# plural selection client-side when msgstr is missing.
		if isinstance(message.id, tuple):
			# Store singular → first plural translation when available.
			msgid = message.id[0]
			if message.string and message.string[0]:
				out[msgid] = message.string[0]
			# Also store a plural key for tn lookup: "singular\x00plural"
			key = "\x00".join(message.id)
			if message.string and any(message.string):
				out[key] = list(message.string)
			continue
		if message.string:
			out[message.id] = message.string
	dest = json_dir / f"{lang}.json"
	with dest.open("w", encoding="utf-8") as f:
		json.dump(out, f, ensure_ascii=False, indent=2, sort_keys=True)
		f.write("\n")
	print(f"Wrote {dest} ({len(out)} strings)")
PY

echo "Compiled catalogs under $LOCALE_DIR"
