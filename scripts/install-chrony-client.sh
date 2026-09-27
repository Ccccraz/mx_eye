#!/usr/bin/env bash
# Install and configure chrony as the NTP client of the consumer device on the
# direct Ethernet link. See AGENTS.md, "Clock synchronization (direct link)".
set -euo pipefail

CONF=/etc/chrony/chrony.conf
USAGE='usage: sudo install-chrony-client.sh [--dry-run] <NTP-SERVER>'
MARKER='# Managed by mx_eye'

DRY_RUN=0
if [ "${1:-}" = --dry-run ]; then
    DRY_RUN=1
    shift
fi

if [ $# -ne 1 ]; then
    printf '%s\n' "$USAGE" >&2
    exit 2
fi
SERVER="$1"

# The argument becomes a line of chrony configuration: accept an IPv4/IPv6
# address or hostname, nothing else.
case "$SERVER" in
-*)
    printf 'error: unknown option %s\n%s\n' "$SERVER" "$USAGE" >&2
    exit 2
    ;;
*[!A-Za-z0-9.:_-]*)
    printf 'error: %s is not an IPv4/IPv6 address or hostname\n' "$SERVER" >&2
    exit 2
    ;;
esac

config() {
    cat <<EOF
$MARKER: clock client for a direct-link NTP server.
# Re-run install-chrony-client.sh after editing; local edits are lost.
server $SERVER iburst minpoll 0 maxpoll 3 prefer
driftfile /var/lib/chrony/chrony.drift
makestep 1.0 3
rtcsync
EOF
}

if [ "$DRY_RUN" -eq 1 ]; then
    printf 'would write %s:\n\n' "$CONF"
    config
    exit 0
fi

if [ "$(id -u)" -ne 0 ]; then
    printf 'error: run this script as root, for example with sudo\n' >&2
    exit 1
fi

if ! command -v chronyd >/dev/null 2>&1; then
    if ! command -v apt-get >/dev/null 2>&1; then
        printf 'error: install chrony first; this script uses apt-get\n' >&2
        exit 1
    fi
    printf 'installing chrony...\n'
    apt-get install -y --no-install-recommends chrony
fi

# chrony must be the only time daemon on this host.
systemctl disable --now systemd-timesyncd 2>/dev/null || true

if [ -f "$CONF" ] && ! grep -qF "$MARKER" "$CONF"; then
    cp -a "$CONF" "$CONF.bak"
    printf 'kept the previous configuration at %s.bak\n' "$CONF"
fi

config >"$CONF"
printf 'wrote %s:\n\n' "$CONF"
config

systemctl enable chrony
systemctl restart chrony
printf '\nchrony restarted; verify with scripts/check-chrony-client.sh\n'
