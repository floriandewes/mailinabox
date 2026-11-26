#!/bin/bash
# Extract gettext messages from the control panel into messages.pot.
# Run from repo root or this directory. Requires Babel (pybabel) in PATH
# or the management venv: /usr/local/lib/mailinabox/env/bin/pybabel
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

"$PYBABEL" extract \
	-F locale/babel.cfg \
	-k _ -k gettext -k ngettext:1,2 -k lazy_gettext \
	-o locale/messages.pot \
	--project="Trixie Mail" \
	--copyright-holder="Trixie Mail" \
	--msgid-bugs-address="https://github.com/quantenland-ai/trixiemail" \
	.

echo "Wrote $LOCALE_DIR/messages.pot"
