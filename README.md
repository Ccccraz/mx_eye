# mx_eye

English | [中文](README.zh.md)

First integrated MXBI pupil / corneal-reflection tracker, with a separate receiver SDK and client.
Python 3.11+; desktop UI for Windows/Linux.

The repository is a uv workspace with four packages: `mx-eye` (the tracker),
`mx-eye-client` (the remote client), `py-mx-eye` (the Python SDK) and
`mx-eye-protocol` (the wire formats they share).

## Install and run

Install everything once, in the repository root:

```bash
uv sync --all-extras
```

Start the tracker and, in a second terminal, the remote client:

```bash
uv run mx-eye
uv run mx-eye-receiver
```

For a camera-free first check:

```bash
uv run mx-eye --demo
```

Click **Start** in the tracker. In the client, click **Connect**; its
**Start tracker** and **Stop tracker** buttons control the same session.
START is idempotent when a session is already running. Alternatively, connect the
client first and start the session from there.

## Clock synchronization

The eyetracker and the consumer device share one time base through system-level
NTP; delay and age readouts compare packet timestamps directly. On a direct
Ethernet link with the consumer device as NTP server, run this once on the
mx_eye host (Raspberry Pi OS/Debian, chrony):

```bash
sudo scripts/install-chrony-client.sh 192.168.50.1   # consumer-device address
scripts/check-chrony-client.sh                       # wait and verify
```

More detail in AGENTS.md.

## SDK

The SDK is the `py-mx-eye` package; `uv sync --all-extras` installs it.

```python
from py_mx_eye import Client

with Client("127.0.0.1") as eye:
    eye.start()
    # Inside your behavioral-task loop:
    sample = eye.latest(max_age_ms=50)
    if sample is not None:
        x, y = sample.frame.payload.x, sample.frame.payload.y
    # At the end of the session:
    eye.stop()
```

`latest()` returns None until the tracker produces its first valid sample, and
coordinates are uncalibrated source-image pixels. A runnable example:
`uv run python -m mx_eye_client.receive_minimal`. More detail in AGENTS.md.
