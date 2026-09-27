#!/usr/bin/env bash
# Verify that the chrony client synchronized to the direct-link NTP server.
# Run scripts/install-chrony-client.sh first.
set -euo pipefail

# Wait up to 30 s (30 tries, 1 s apart) for a source to be selected with the
# remaining correction below 50 ms and the skew below 1 ppm.
printf 'waiting for synchronization...\n'
if ! chronyc -n waitsync 30 0.05 1.0 1; then
    printf '\nnot synchronized; current sources:\n' >&2
    chronyc -n sources -v >&2 || true
    printf 'error: no usable time from the NTP server\n' >&2
    exit 1
fi

chronyc -n tracking
chronyc -n sources -v
