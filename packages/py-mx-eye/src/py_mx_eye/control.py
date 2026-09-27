"""Control-plane access to the tracker command endpoint.

One request/response per connection on the tracker command port; the endpoint
serves status, start and stop. Timing arithmetic is left to the data plane.
"""

import socket
from collections.abc import Callable

from mx_eye_protocol.control import Command, Reply, Request, StatusSnapshot
from mx_eye_protocol.json_io import receive_json, send_json

Connector = Callable[[tuple[str, int], float], socket.socket]


class ControlClient:
    """One request per connection against the tracker command endpoint."""

    def __init__(
        self,
        host: str,
        port: int,
        timeout: float,
        *,
        connect: Connector = socket.create_connection,
    ) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout
        self._connect = connect

    def rpc(self, request: Request, timeout: float | None = None) -> Reply:
        """Send one typed request and return its validated reply."""
        timeout = self.timeout if timeout is None else timeout
        try:
            with self._connect((self.host, self.port), timeout) as sock:
                sock.settimeout(timeout)
                send_json(sock, request)
                reply = receive_json(sock, Reply)
                if not reply.ok:
                    raise RuntimeError(reply.error or "Tracker rejected command")
                return reply
        except (TimeoutError, ConnectionError, OSError) as exc:
            raise TimeoutError(
                f"Tracker did not reply at {self.host}:{self.port}: {exc}"
            ) from exc

    def request_status(
        self, command: Command, timeout: float | None = None
    ) -> StatusSnapshot:
        reply = self.rpc(Request(command=command), timeout=timeout)
        if reply.status is None:
            raise ValueError("Expected a status response")
        return reply.status
