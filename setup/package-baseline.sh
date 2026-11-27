#!/bin/bash
# Package baseline helpers for Trixiemail uninstall.
# Sourced from setup/start.sh and setup/uninstall.sh.
#
# Captures the set of installed packages before setup mutates the system,
# so a later uninstall can purge only what Trixiemail added.

# Relative to STORAGE_ROOT. Kept under user-data so it survives across
# re-runs of setup on the same data directory.
PACKAGE_BASELINE_RELPATH="installer/dpkg-selections-baseline.txt"

function package_baseline_path {
	# package_baseline_path [STORAGE_ROOT]
	local root="${1:-${STORAGE_ROOT:-}}"
	if [ -z "$root" ]; then
		echo "package_baseline_path: STORAGE_ROOT is not set" >&2
		return 1
	fi
	printf '%s/%s\n' "$root" "$PACKAGE_BASELINE_RELPATH"
}

function capture_package_baseline {
	# capture_package_baseline [STORAGE_ROOT] [--force]
	# Writes dpkg --get-selections to $STORAGE_ROOT/installer/... unless a
	# baseline already exists (unless --force).
	local root="${1:-${STORAGE_ROOT:-}}"
	local force=0
	if [ "${2:-}" = "--force" ] || [ "${1:-}" = "--force" ]; then
		force=1
		if [ "${1:-}" = "--force" ]; then
			root="${STORAGE_ROOT:-}"
		fi
	fi
	if [ -z "$root" ]; then
		echo "capture_package_baseline: STORAGE_ROOT is not set" >&2
		return 1
	fi

	local path
	path=$(package_baseline_path "$root")
	mkdir -p "$(dirname "$path")"

	if [ -f "$path" ] && [ "$force" -eq 0 ]; then
		return 0
	fi

	# Record both the raw selections and a short header for operators.
	{
		echo "# Trixiemail package baseline"
		echo "# Captured: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
		echo "# Host: $(hostname -f 2>/dev/null || hostname)"
		echo "# Format: dpkg --get-selections"
		echo "#"
		dpkg --get-selections
	} > "$path"

	# Prefer the storage user when that account already exists.
	if [ -n "${STORAGE_USER:-}" ] && id -u "$STORAGE_USER" >/dev/null 2>&1; then
		chown "$STORAGE_USER:$STORAGE_USER" "$(dirname "$path")" "$path" 2>/dev/null || true
	fi
	chmod 644 "$path"
	echo "Saved package baseline to $path"
}

function list_installed_package_names {
	# Prints installed package names (one per line), excluding deinstall.
	dpkg --get-selections | awk '$2 == "install" || $2 == "hold" { print $1 }' | sort -u
}

function list_baseline_package_names {
	# list_baseline_package_names BASELINE_FILE
	# Skips comment/header lines from our baseline file.
	local file="$1"
	awk '
		/^#/ { next }
		NF == 0 { next }
		$2 == "install" || $2 == "hold" { print $1 }
	' "$file" | sort -u
}
