# Load optional headless install config and CLI flags.
# Sourced early from setup/start.sh.
#
# Config search order (first existing file wins):
#   1. --config=PATH
#   2. $MAILINABOX_CONFIG
#   3. $REPO_ROOT/install.conf   (next to setup/, recommended for agents)
#   4. $HOME/mailinabox-install.conf
#
# No config file → interactive prompts (default).
# Complete config → no prompts.
# --noninteractive / --headless → never prompt; fail if required values missing.
#
# See conf/install.conf.example.

show_install_usage() {
	cat <<'EOF'
Mail-in-a-Box setup

Usage:
  sudo setup/start.sh
  sudo setup/start.sh --noninteractive
  sudo setup/start.sh --noninteractive --config=/path/to/install.conf

Options:
  --noninteractive, --headless
      Do not prompt. Fail if required settings are missing.
  --config=PATH
      Load KEY=VALUE install settings from PATH.
  -h, --help
      Show this help.

Config file search order (first existing file wins):
  1. --config=PATH
  2. $MAILINABOX_CONFIG
  3. ./install.conf                 (repository root; recommended)
  4. $HOME/mailinabox-install.conf

Copy conf/install.conf.example to install.conf and fill in values.
Required for first-time headless install:
  PRIMARY_HOSTNAME  (explicit FQDN; "auto" is not allowed)
  PUBLIC_IP         (IPv4 address, or "auto" to detect)
  EMAIL_ADDR, EMAIL_PW
Optional:
  PUBLIC_IPV6, STORAGE_USER, STORAGE_ROOT, TIMEZONE, SKIP_NETWORK_CHECKS
EOF
}

# Repository root = parent of setup/ (this file lives in setup/).
_MIAB_SETUP_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
_MIAB_REPO_ROOT=$(cd "$_MIAB_SETUP_DIR/.." && pwd)

_MIAB_CONFIG_FROM_FLAG=
for _miab_arg in "$@"; do
	case "$_miab_arg" in
		--noninteractive|--headless)
			export NONINTERACTIVE=1
			INSTALL_CONFIG_STRICT=1
			;;
		--config=*)
			_MIAB_CONFIG_FROM_FLAG="${_miab_arg#--config=}"
			;;
		-h|--help)
			show_install_usage
			exit 0
			;;
	esac
done
unset _miab_arg

# Resolve which config file to load (explicit paths first, then defaults).
MAILINABOX_CONFIG_RESOLVED=
if [ -n "$_MIAB_CONFIG_FROM_FLAG" ]; then
	MAILINABOX_CONFIG_RESOLVED="$_MIAB_CONFIG_FROM_FLAG"
elif [ -n "${MAILINABOX_CONFIG:-}" ]; then
	MAILINABOX_CONFIG_RESOLVED="$MAILINABOX_CONFIG"
elif [ -f "$_MIAB_REPO_ROOT/install.conf" ]; then
	MAILINABOX_CONFIG_RESOLVED="$_MIAB_REPO_ROOT/install.conf"
elif [ -n "${HOME:-}" ] && [ -f "$HOME/mailinabox-install.conf" ]; then
	MAILINABOX_CONFIG_RESOLVED="$HOME/mailinabox-install.conf"
fi
unset _MIAB_CONFIG_FROM_FLAG

if [ -n "$MAILINABOX_CONFIG_RESOLVED" ]; then
	if [ ! -f "$MAILINABOX_CONFIG_RESOLVED" ]; then
		echo "Install config '$MAILINABOX_CONFIG_RESOLVED' does not exist." >&2
		exit 1
	fi

	echo "Loading install config from $MAILINABOX_CONFIG_RESOLVED"
	export MAILINABOX_CONFIG="$MAILINABOX_CONFIG_RESOLVED"

	# Only accept simple KEY=VALUE lines. Reject shell metacharacters so a
	# mistaken file cannot run commands when sourced.
	_miab_tmp=$(mktemp)
	_miab_line_no=0
	while IFS= read -r _miab_line || [ -n "$_miab_line" ]; do
		_miab_line_no=$((_miab_line_no + 1))
		_miab_line="${_miab_line%%#*}"
		_miab_line="${_miab_line#"${_miab_line%%[![:space:]]*}"}"
		_miab_line="${_miab_line%"${_miab_line##*[![:space:]]}"}"
		[ -z "$_miab_line" ] && continue

		case "$_miab_line" in
			export\ *) _miab_line="${_miab_line#export }" ;;
		esac

		if ! [[ "$_miab_line" =~ ^[A-Za-z_][A-Za-z0-9_]*= ]]; then
			echo "Invalid line $_miab_line_no in $MAILINABOX_CONFIG_RESOLVED (expected KEY=VALUE)." >&2
			rm -f "$_miab_tmp"
			exit 1
		fi

		_miab_key="${_miab_line%%=*}"
		_miab_val="${_miab_line#*=}"
		if [[ "$_miab_val" =~ ^\".*\"$ ]]; then
			_miab_val="${_miab_val:1:${#_miab_val}-2}"
		elif [[ "$_miab_val" =~ ^\'.*\'$ ]]; then
			_miab_val="${_miab_val:1:${#_miab_val}-2}"
		fi

		if [[ "$_miab_val" == *'`'* || "$_miab_val" == *'$('* || "$_miab_val" == *$'\n'* ]]; then
			echo "Unsafe value for $_miab_key in $MAILINABOX_CONFIG_RESOLVED line $_miab_line_no." >&2
			rm -f "$_miab_tmp"
			exit 1
		fi

		case "$_miab_key" in
			PRIMARY_HOSTNAME|PUBLIC_IP|PUBLIC_IPV6|PRIVATE_IP|PRIVATE_IPV6|\
			EMAIL_ADDR|EMAIL_PW|STORAGE_USER|STORAGE_ROOT|TIMEZONE|\
			SKIP_NETWORK_CHECKS|NONINTERACTIVE|DISABLE_FIREWALL|MTA_STS_MODE)
				# Environment already set wins over the file.
				if [ -z "${!_miab_key+x}" ] || [ -z "${!_miab_key}" ]; then
					printf '%s=%q\n' "$_miab_key" "$_miab_val" >> "$_miab_tmp"
				fi
				;;
			*)
				echo "Warning: ignoring unknown key '$_miab_key' in $MAILINABOX_CONFIG_RESOLVED" >&2
				;;
		esac
	done < "$MAILINABOX_CONFIG_RESOLVED"

	# shellcheck disable=SC1090
	source "$_miab_tmp"
	rm -f "$_miab_tmp"
	unset _miab_tmp _miab_line _miab_line_no _miab_key _miab_val

	# A complete first-time config implies noninteractive (no prompts).
	# Incomplete config without --noninteractive falls back to prompts later.
	if [ -n "${PRIMARY_HOSTNAME:-}" ] && [ -n "${PUBLIC_IP:-}" ] \
		&& [ -n "${EMAIL_ADDR:-}" ] && [ -n "${EMAIL_PW:-}" ]; then
		export NONINTERACTIVE=1
	elif [ -n "${INSTALL_CONFIG_STRICT:-}" ]; then
		: # strict mode validates below / in firstuser
	else
		echo "Install config is incomplete; falling back to interactive prompts for missing values."
	fi
fi

export INSTALL_CONFIG_STRICT="${INSTALL_CONFIG_STRICT:-}"
if [ -n "${NONINTERACTIVE:-}" ]; then
	export NONINTERACTIVE
fi

require_install_var() {
	local name="$1"
	local hint="$2"
	if [ -z "${!name:-}" ]; then
		echo "Headless install requires $name${hint:+ ($hint)}." >&2
		echo "Set it in install.conf (see conf/install.conf.example)." >&2
		exit 1
	fi
}

# Strict headless: fail before any dialog when required keys are missing.
# On re-runs, /etc/mailinabox.conf supplies hostname/IP; EMAIL_* only needed
# when creating the first user (checked in firstuser.sh).
if [ -n "${INSTALL_CONFIG_STRICT:-}" ] && [ ! -f /etc/mailinabox.conf ]; then
	if [ -z "${MAILINABOX_CONFIG:-}" ] && [ -z "${PRIMARY_HOSTNAME:-}" ] && [ -z "${PUBLIC_IP:-}" ]; then
		echo "Headless install needs a config file or environment variables." >&2
		echo "Copy conf/install.conf.example to $_MIAB_REPO_ROOT/install.conf" >&2
		echo "or pass --config=PATH. See: setup/start.sh --help" >&2
		exit 1
	fi
	require_install_var PRIMARY_HOSTNAME "explicit FQDN, e.g. box.example.com"
	require_install_var PUBLIC_IP "IPv4 address or auto"
	require_install_var EMAIL_ADDR "first admin email"
	require_install_var EMAIL_PW "password, min 8 characters"
	if [ "${PRIMARY_HOSTNAME}" = "auto" ]; then
		echo "PRIMARY_HOSTNAME must be an explicit FQDN (e.g. box.example.com)." >&2
		echo "The value \"auto\" is not allowed for headless/agent installs." >&2
		exit 1
	fi
	if [ "${#EMAIL_PW}" -lt 8 ]; then
		echo "EMAIL_PW must be at least 8 characters." >&2
		exit 1
	fi
fi

# Config-file / agent path: reject PRIMARY_HOSTNAME=auto even without --noninteractive.
# Vagrant may still set PRIMARY_HOSTNAME=auto via the environment without a config file.
if [ -n "${MAILINABOX_CONFIG:-}" ] && [ "${PRIMARY_HOSTNAME:-}" = "auto" ]; then
	echo "PRIMARY_HOSTNAME must be an explicit FQDN (e.g. box.example.com)." >&2
	echo "The value \"auto\" is not allowed in install.conf." >&2
	exit 1
fi

unset _MIAB_SETUP_DIR _MIAB_REPO_ROOT MAILINABOX_CONFIG_RESOLVED
