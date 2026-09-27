"""The direct-link chrony scripts stay parseable and reviewable."""

import shutil
import subprocess
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
INSTALL = SCRIPTS / "install-chrony-client.sh"
CHECK = SCRIPTS / "check-chrony-client.sh"
BASH = shutil.which("bash")

pytestmark = pytest.mark.skipif(BASH is None, reason="bash is not available")


def run_script(script, *arguments):
    return subprocess.run(
        [BASH, str(script), *arguments],
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.parametrize("script", [INSTALL, CHECK])
def test_script_is_executable_and_parses(script):
    assert script.is_file()
    assert script.stat().st_mode & 0o111
    parsed = subprocess.run([BASH, "-n", str(script)], capture_output=True, check=False)
    assert parsed.returncode == 0


def test_dry_run_prints_the_chrony_config():
    result = run_script(INSTALL, "--dry-run", "192.0.2.10")
    assert result.returncode == 0
    assert "would write" in result.stdout
    # The generated file must select our peer and nothing else.
    assert "server 192.0.2.10 iburst minpoll 0 maxpoll 3 prefer" in result.stdout
    assert "driftfile /var/lib/chrony/chrony.drift" in result.stdout
    assert "makestep 1.0 3" in result.stdout
    assert "pool" not in result.stdout


@pytest.mark.parametrize("server", ["bad;host", "1.2.3.4 5", "a$(id)"])
def test_dry_run_rejects_a_server_that_is_config_syntax(server):
    result = run_script(INSTALL, "--dry-run", server)
    assert result.returncode != 0
    assert "error:" in result.stderr


@pytest.mark.parametrize("server", ["192.0.2.10", "fe80::1", "ntp.lab.local"])
def test_dry_run_accepts_addresses_and_hostnames(server):
    assert run_script(INSTALL, "--dry-run", server).returncode == 0


@pytest.mark.parametrize(
    "arguments",
    [(), ("--nope", "192.0.2.10"), ("--nope",), ("--dry-run",), ("a", "b")],
)
def test_usage_errors(arguments):
    result = run_script(INSTALL, *arguments)
    assert result.returncode != 0
    assert "usage:" in result.stderr
