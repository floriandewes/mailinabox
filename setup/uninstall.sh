#!/bin/bash
# Mail-in-a-Box uninstaller
# -------------------------
#
# Removes the mail stack this repository's setup scripts install, using a
# package baseline captured at the start of setup when available.
#
# Usage (from the repository root, as root):
#   setup/uninstall.sh
#   setup/uninstall.sh --yes
#   setup/uninstall.sh --yes --purge-data
#   setup/uninstall.sh --record-baseline
#   setup/uninstall.sh --dry-run
#
# By default /home/user-data (STORAGE_ROOT) is kept. Pass --purge-data to
# delete mailboxes, SSL material, DNSSEC keys, Nextcloud data, and the rest.

# Move to the repository root (parent of setup/), matching other setup scripts.
cd "$(dirname "$0")/.." || exit 1

source setup/functions.sh
source setup/package-baseline.sh

ASSUME_YES=0
PURGE_DATA=0
RECORD_BASELINE_ONLY=0
DRY_RUN=0

function usage {
	cat <<EOF
Usage: setup/uninstall.sh [options]

Remove Mail-in-a-Box packages, services, and configuration written by setup/.

Options:
  --yes               Do not ask for interactive confirmation
  --purge-data        Also delete STORAGE_ROOT (mail, SSL, users, etc.)
  --record-baseline   Only save a package baseline (for a fresh box before
                      install, or after uninstall before reinstalling)
  --dry-run           Print actions without changing the system
  -h, --help          Show this help

Package removal:
  If \$STORAGE_ROOT/installer/dpkg-selections-baseline.txt exists (written
  automatically near the start of setup), packages installed since that
  snapshot are candidates for purge, excluding a small protected set
  (ssh, sudo, apt, kernel, …).

  If no baseline exists (boxes installed before this feature), only a
  curated list of packages known to be installed by setup/*.sh is purged.

Data:
  STORAGE_ROOT is kept unless --purge-data is passed. Mailboxes are never
  deleted silently.
EOF
}

while [ $# -gt 0 ]; do
	case "$1" in
		--yes|-y) ASSUME_YES=1 ;;
		--purge-data) PURGE_DATA=1 ;;
		--record-baseline) RECORD_BASELINE_ONLY=1 ;;
		--dry-run) DRY_RUN=1 ;;
		-h|--help) usage; exit 0 ;;
		*)
			echo "Unknown option: $1" >&2
			usage >&2
			exit 1
			;;
	esac
	shift
done

if [[ $EUID -ne 0 ]]; then
	echo "This script must be run as root. Did you leave out sudo?"
	exit 1
fi

function run {
	if [ "$DRY_RUN" -eq 1 ]; then
		echo "DRY-RUN: $*"
		return 0
	fi
	"$@"
}

function run_sh {
	# run_sh 'shell code'
	if [ "$DRY_RUN" -eq 1 ]; then
		echo "DRY-RUN: $1"
		return 0
	fi
	eval "$1"
}

# --- Load install location -------------------------------------------------

STORAGE_USER="user-data"
STORAGE_ROOT="/home/user-data"
PRIMARY_HOSTNAME=""
if [ -f /etc/mailinabox.conf ]; then
	# shellcheck disable=SC1091
	source /etc/mailinabox.conf
fi

if [ "$RECORD_BASELINE_ONLY" -eq 1 ]; then
	if [ ! -d "$STORAGE_ROOT" ]; then
		mkdir -p "$STORAGE_ROOT"
	fi
	capture_package_baseline "$STORAGE_ROOT" --force
	echo
	echo "Baseline recorded. Run setup/start.sh to install, or keep this"
	echo "file so a future uninstall can diff against it."
	exit 0
fi

BASELINE_FILE=$(package_baseline_path "$STORAGE_ROOT" 2>/dev/null || true)
HAS_BASELINE=0
if [ -n "${BASELINE_FILE:-}" ] && [ -f "$BASELINE_FILE" ]; then
	HAS_BASELINE=1
fi

# --- Warnings / confirmation -----------------------------------------------

cat <<EOF

========================================
  Mail-in-a-Box UNINSTALL
========================================

This is DESTRUCTIVE. It will:

  * Stop Mail-in-a-Box related services
  * Purge apt packages the installer added
  * Remove MIAB configuration under /etc, systemd units, cron jobs,
    nginx site fragments, fail2ban jails, and software under
    /usr/local/lib/{mailinabox,roundcubemail,owncloud,z-push}

EOF

if [ "$PURGE_DATA" -eq 1 ]; then
	cat <<EOF
  * DELETE all data in: $STORAGE_ROOT
    (mailboxes, SSL certificates, DNSSEC keys, Nextcloud, backups, …)

EOF
else
	cat <<EOF
  * KEEP user data in: $STORAGE_ROOT
    Pass --purge-data if you also want mailboxes and SSL material removed.

EOF
fi

if [ "$HAS_BASELINE" -eq 1 ]; then
	echo "Package baseline: $BASELINE_FILE"
	echo "Package removal will use: current packages minus baseline (minus protected)."
else
	cat <<EOF
WARNING: No package baseline found at:
  $STORAGE_ROOT/installer/dpkg-selections-baseline.txt

This box was likely installed before baseline capture existed. Package
removal will use a curated list of Mail-in-a-Box packages from setup/*.sh
only. Packages the installer pulled in as dependencies that are not on
that list may remain. After uninstall you can run:

  sudo setup/uninstall.sh --record-baseline

on a clean system (or after this uninstall) before the next install so
future uninstalls can use a full package diff.
EOF
fi

echo
if [ "$DRY_RUN" -eq 1 ]; then
	echo "(dry-run mode: no changes will be made)"
	echo
fi

if [ "$ASSUME_YES" -eq 0 ]; then
	if [ ! -t 0 ]; then
		echo "stdin is not a TTY. Re-run with --yes for non-interactive uninstall."
		exit 1
	fi
	printf "Type YES to continue: "
	read -r confirm
	if [ "$confirm" != "YES" ]; then
		echo "Aborted."
		exit 1
	fi
fi

# --- Curated MIAB packages (from setup/*.sh) --------------------------------
# Used as the sole removal set when no baseline exists, and as a hint when
# reporting. Keep this aligned with apt_install calls in setup/.

function curated_miab_packages {
	# Conservative fallback when no baseline exists: only packages that are
	# clearly part of the mail appliance. General tools (curl, git, python3,
	# sudo, rsync, …) are omitted here; with a baseline, the diff still
	# removes whatever setup added.
	local php="php${PHP_VER}"

	cat <<EOF
postfix
postfix-sqlite
postfix-pcre
postgrey
dovecot-core
dovecot-imapd
dovecot-pop3d
dovecot-lmtpd
dovecot-sqlite
dovecot-sieve
dovecot-managesieved
dovecot-antispam
nginx
nsd
ldnsutils
opendkim
opendkim-tools
opendmarc
spampd
razor
pyzor
libmail-dkim-perl
spamassassin
fail2ban
munin
munin-node
libcgi-fast-perl
bind9
certbot
duplicity
${php}
${php}-cli
${php}-fpm
${php}-sqlite3
${php}-intl
${php}-common
${php}-curl
${php}-imap
${php}-gd
${php}-pspell
${php}-mbstring
${php}-xml
${php}-soap
${php}-dev
${php}-zip
${php}-apcu
${php}-imagick
${php}-gmp
${php}-bcmath
idn2
libawl-php
libjs-jquery
libjs-jquery-mousewheel
dbconfig-common
python3-b2sdk
python3-boto3
debsuryorg-archive-keyring
EOF
}

function is_protected_package {
	# Never purge these even if they appear in a baseline diff.
	local pkg="$1"
	case "$pkg" in
		apt|apt-utils|base-files|base-passwd|bash|bsdutils|coreutils|\
		dash|debconf|debianutils|diffutils|dpkg|e2fsprogs|\
		findutils|grep|gzip|hostname|init|init-system-helpers|libc-bin|\
		login|mount|ncurses-base|ncurses-bin|passwd|perl-base|\
		sed|sensible-utils|systemd|systemd-sysv|sysvinit-utils|tar|\
		util-linux|sudo|openssh-server|openssh-client|openssh-sftp-server|\
		rsyslog|cron|cron-daemon-common|wget|curl|ca-certificates|\
		gnupg|gpgv|adduser|netbase|tzdata|locales|netcat-openbsd|\
		git|file|bc|unzip|openssl|python3|python3-minimal|libpython3*)
			return 0
			;;
		linux-*|grub-*|shim-*|firmware-*|initramfs-*|udev|libudev*)
			return 0
			;;
	esac
	return 1
}

function packages_to_purge {
	local current baseline_pkgs curated
	current=$(mktemp)
	list_installed_package_names > "$current"

	if [ "$HAS_BASELINE" -eq 1 ]; then
		baseline_pkgs=$(mktemp)
		list_baseline_package_names "$BASELINE_FILE" > "$baseline_pkgs"
		# Packages installed now that were not in the baseline.
		comm -13 "$baseline_pkgs" "$current" | while read -r pkg; do
			[ -z "$pkg" ] && continue
			if is_protected_package "$pkg"; then
				continue
			fi
			printf '%s\n' "$pkg"
		done
		rm -f "$baseline_pkgs"
	else
		curated=$(mktemp)
		curated_miab_packages | sort -u > "$curated"
		comm -12 "$curated" "$current"
		rm -f "$curated"
	fi
	rm -f "$current"
}

# --- Stop services ---------------------------------------------------------

echo
echo "Stopping Mail-in-a-Box services..."

MIAB_SERVICES=(
	mailinabox
	munin
	munin-node
	nginx
	"php${PHP_VER}-fpm"
	postfix
	postgrey
	dovecot
	opendkim
	opendmarc
	spampd
	spamassassin
	fail2ban
	nsd
	bind9
	named
)

for svc in "${MIAB_SERVICES[@]}"; do
	if systemctl list-unit-files "${svc}.service" >/dev/null 2>&1 || \
	   systemctl status "$svc" >/dev/null 2>&1; then
		run systemctl stop "$svc" 2>/dev/null || true
		run systemctl disable "$svc" 2>/dev/null || true
	fi
done

if systemctl list-unit-files spamassassin-maintenance.timer >/dev/null 2>&1; then
	run systemctl stop spamassassin-maintenance.timer 2>/dev/null || true
	run systemctl disable spamassassin-maintenance.timer 2>/dev/null || true
fi

# --- Remove non-package side effects ---------------------------------------

echo "Removing Mail-in-a-Box configuration and locally installed software..."

# systemd units installed by management.sh / munin.sh
run rm -f /lib/systemd/system/mailinabox.service
run rm -f /lib/systemd/system/munin.service
run rm -f /etc/systemd/system/mailinabox.service
run rm -f /etc/systemd/system/munin.service
run systemctl daemon-reload 2>/dev/null || true

# Cron
run rm -f /etc/cron.d/mailinabox-nightly
run rm -f /etc/cron.d/mailinabox-nextcloud
run rm -f /etc/cron.daily/mailinabox-ssl-cleanup
run rm -f /etc/cron.daily/mailinabox-dnssec
run rm -f /etc/cron.daily/mailinabox-postgrey-whitelist

# fail2ban
run rm -f /etc/fail2ban/jail.d/mailinabox.conf
# filters copied from conf/fail2ban/filter.d/ — remove only ones we ship
if [ -d conf/fail2ban/filter.d ]; then
	for f in conf/fail2ban/filter.d/*; do
		[ -f "$f" ] || continue
		run rm -f "/etc/fail2ban/filter.d/$(basename "$f")"
	done
fi

# nginx fragments written by setup / management daemon
run rm -f /etc/nginx/conf.d/ssl.conf
run rm -f /etc/nginx/conf.d/local.conf
run rm -f /etc/nginx/nginx-ssl.conf

# nsd
run rm -f /etc/nsd/nsd.conf
run rm -rf /etc/nsd/nsd.conf.d
run rm -rf /etc/nsd/zones
run rm -f /etc/logrotate.d/nsd

# dovecot local overlays
run rm -f /etc/dovecot/conf.d/99-local.conf
run rm -f /etc/dovecot/conf.d/99-mailinabox.conf
run rm -f /etc/dovecot/conf.d/99-local-auth.conf
run rm -f /etc/dovecot/conf.d/99-local-sieve.conf
run rm -f /etc/dovecot/conf.d/99-local-spampd.conf
run rm -f /etc/dovecot/conf.d/15-mailboxes.conf
run rm -f /etc/dovecot/conf.d/90-quota.conf
run rm -f /etc/dovecot/conf.d/auth-sql.conf.ext
run rm -f /etc/dovecot/dovecot-sql.conf.ext

# postfix sqlite maps / filters we dropped in
run rm -f /etc/postfix/outgoing_mail_header_filters
run rm -f /etc/postfix/sender-login-maps.cf
run rm -f /etc/postfix/virtual-mailbox-domains.cf
run rm -f /etc/postfix/virtual-mailbox-maps.cf
run rm -f /etc/postfix/virtual-alias-maps.cf

# opendkim helpers
run rm -rf /etc/opendkim

# spamassassin MIAB bits
run rm -f /etc/spamassassin/miab_spf_dmarc.cf
run rm -rf /etc/spamassassin/pyzor

# sysctl
run rm -f /etc/sysctl.d/99-mailinabox.conf

# apt sources / preferences added for PHP on Debian
run rm -f /etc/apt/sources.list.d/php.list
run rm -f /etc/apt/preferences.d/mailinabox-php
run rm -f /etc/apt/apt.conf.d/02periodic

# logrotate
run rm -f /etc/logrotate.d/z-push
run rm -f /etc/logrotate.d/nextcloud

# management / webmail / nextcloud / z-push trees
run rm -rf /usr/local/lib/mailinabox
run rm -rf /usr/local/lib/roundcubemail
run rm -rf /usr/local/lib/owncloud
run rm -rf /usr/local/lib/nextcloud
run rm -rf /usr/local/lib/z-push
run rm -rf /var/lib/mailinabox
run rm -rf /var/lib/z-push
run rm -rf /var/log/z-push
run rm -rf /var/tmp/roundcubemail

# wrapper scripts
run rm -f /usr/local/bin/mailinabox
run rm -f /usr/local/bin/sa-learn-pipe.sh
run rm -f /usr/sbin/z-push-admin
run rm -f /usr/sbin/z-push-top

# SSH key created solely for MIAB backups
run rm -f /root/.ssh/id_rsa_miab /root/.ssh/id_rsa_miab.pub

# Main config last among configs (needed above for paths)
# Kept until after data decision; removed near the end.

# --- Purge packages --------------------------------------------------------

echo "Computing packages to purge..."
mapfile -t PURGE_ARRAY < <(packages_to_purge | sort -u)
if [ "${#PURGE_ARRAY[@]}" -eq 0 ] || [ -z "${PURGE_ARRAY[0]:-}" ]; then
	echo "No matching packages to purge."
else
	echo "Packages to purge:"
	printf '  %s\n' "${PURGE_ARRAY[@]}"
	echo
	if [ "$DRY_RUN" -eq 1 ]; then
		echo "DRY-RUN: apt-get -y purge --auto-remove ${PURGE_ARRAY[*]}"
	else
		set +e
		DEBIAN_FRONTEND=noninteractive apt-get -y purge --auto-remove "${PURGE_ARRAY[@]}"
		APT_STATUS=$?
		set -e
		if [ "$APT_STATUS" -ne 0 ]; then
			echo "Warning: apt purge exited with status $APT_STATUS (some packages may remain)."
		fi
		apt_get_quiet autoremove || true
		apt_get_quiet autoclean || true
	fi
fi

# --- DNS resolver recovery -------------------------------------------------
# setup/system.sh replaced resolv.conf with nameserver 127.0.0.1 (bind9).
# After purge, restore a usable resolver only when that loopback stub remains
# and named is gone.

if [ -e /etc/resolv.conf ] && grep -Eq '^[[:space:]]*nameserver[[:space:]]+127\.0\.0\.1' /etc/resolv.conf \
	&& [ ! -e /usr/sbin/named ] && [ ! -x /usr/sbin/named ]; then
	echo "Restoring DNS resolver configuration..."
	if [ -e /usr/lib/systemd/system/systemd-resolved.service ] || \
	   [ -e /lib/systemd/system/systemd-resolved.service ]; then
		run_sh 'tools/editconf.py /etc/systemd/resolved.conf DNSStubListener=yes 2>/dev/null || true'
		run rm -f /etc/resolv.conf
		run ln -sf /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf
		run systemctl restart systemd-resolved 2>/dev/null || true
	else
		run_sh 'printf "nameserver 1.1.1.1\nnameserver 9.9.9.9\n" > /etc/resolv.conf'
	fi
fi

# --- Optional data purge ---------------------------------------------------

if [ "$PURGE_DATA" -eq 1 ]; then
	echo "Deleting STORAGE_ROOT: $STORAGE_ROOT"
	run rm -rf "$STORAGE_ROOT"
	# Remove the storage user only when it looks like the MIAB default and
	# its home was STORAGE_ROOT (do not touch unrelated accounts).
	if [ -n "${STORAGE_USER:-}" ] && id -u "$STORAGE_USER" >/dev/null 2>&1; then
		home=$(getent passwd "$STORAGE_USER" | cut -d: -f6)
		if [ "$STORAGE_USER" = "user-data" ] || [ "$home" = "$STORAGE_ROOT" ]; then
			# Kill leftover processes then remove the account.
			run_sh "pkill -u \"$STORAGE_USER\" 2>/dev/null || true"
			run userdel "$STORAGE_USER" 2>/dev/null || true
		else
			echo "Note: left system user '$STORAGE_USER' in place (not safe to auto-delete)."
		fi
	fi
else
	echo "Kept STORAGE_ROOT: $STORAGE_ROOT"
fi

# Drop the install marker after everything else.
run rm -f /etc/mailinabox.conf

# --- Residual state report -------------------------------------------------

cat <<EOF

----------------------------------------
Uninstall finished.
EOF

if [ "$DRY_RUN" -eq 1 ]; then
	echo "(dry-run: nothing was changed)"
fi

cat <<EOF

Preserved by default:
  * $STORAGE_ROOT  (use --purge-data to delete)
  * System hostname (/etc/hostname)
  * SSH host keys and general SSH configuration
  * ufw may still be installed/enabled if it was not purged; review: ufw status
  * Any packages you installed yourself after the baseline was taken that are
    not in the protected set may have been purged when a baseline was used.

Likely residual / manual follow-up:
  * Review /etc/postfix /etc/dovecot /etc/nginx /etc/bind /etc/fail2ban for
    locally edited remnants if those packages were not fully purged
  * Review firewall: ufw status
  * Review DNS: cat /etc/resolv.conf
  * The Mail-in-a-Box git checkout itself was not deleted
  * Swap file /swapfile (if setup created one) was left in place

To reinstall cleanly on this machine:
  1. Prefer a fresh OS image when possible
  2. Or: keep/restore data under $STORAGE_ROOT, then run setup/start.sh again
     from this repository (existing data directories are reused)
  3. On a cleaned system, optionally:
       sudo setup/uninstall.sh --record-baseline
     before the next install so uninstall can use a full package diff later

EOF
