"""Small, dependency-free Minecraft RCON client for the local dashboard."""

from __future__ import annotations

import socket
import struct
from dataclasses import dataclass


class RconError(RuntimeError):
    """Raised when RCON authentication or command exchange fails."""


@dataclass(frozen=True)
class _Packet:
    request_id: int
    packet_type: int
    body: bytes


class RconClient:
    """Open one authenticated RCON connection for one command."""

    SERVERDATA_RESPONSE_VALUE = 0
    SERVERDATA_EXECCOMMAND = 2
    SERVERDATA_AUTH_RESPONSE = 2
    SERVERDATA_AUTH = 3
    MAX_PACKET_SIZE = 4 * 1024 * 1024

    def __init__(self, host: str, port: int, password: str, timeout: float = 3.0):
        if not password:
            raise RconError("RCON password is not configured")
        self.host = host
        self.port = port
        self.password = password
        self.timeout = timeout

    @staticmethod
    def _encode(request_id: int, packet_type: int, body: str) -> bytes:
        payload = struct.pack("<ii", request_id, packet_type) + body.encode("utf-8") + b"\0\0"
        return struct.pack("<i", len(payload)) + payload

    @staticmethod
    def _recv_exact(sock: socket.socket, size: int) -> bytes:
        chunks = bytearray()
        while len(chunks) < size:
            chunk = sock.recv(size - len(chunks))
            if not chunk:
                raise RconError("RCON closed the connection unexpectedly")
            chunks.extend(chunk)
        return bytes(chunks)

    def _recv_packet(self, sock: socket.socket) -> _Packet:
        length = struct.unpack("<i", self._recv_exact(sock, 4))[0]
        if length < 10 or length > self.MAX_PACKET_SIZE:
            raise RconError("RCON returned an invalid packet length")
        payload = self._recv_exact(sock, length)
        request_id, packet_type = struct.unpack("<ii", payload[:8])
        return _Packet(request_id, packet_type, payload[8:-2])

    def run(self, command: str) -> str:
        if not command or "\0" in command or "\n" in command or "\r" in command:
            raise RconError("Command must be a single non-empty line")
        if len(command.encode("utf-8")) > 2048:
            raise RconError("Command is too long")

        try:
            with socket.create_connection((self.host, self.port), timeout=self.timeout) as sock:
                sock.settimeout(self.timeout)
                sock.sendall(self._encode(1, self.SERVERDATA_AUTH, self.password))
                auth = self._recv_packet(sock)
                if auth.request_id == -1:
                    raise RconError("RCON rejected authentication")
                if auth.request_id != 1 or auth.packet_type != self.SERVERDATA_AUTH_RESPONSE:
                    raise RconError("RCON returned an unexpected authentication response")

                sock.sendall(self._encode(2, self.SERVERDATA_EXECCOMMAND, command))
                chunks: list[bytes] = []
                sock.settimeout(0.25)
                while True:
                    try:
                        packet = self._recv_packet(sock)
                    except socket.timeout:
                        if chunks:
                            break
                        raise RconError("RCON command timed out") from None
                    if packet.request_id != 2:
                        continue
                    chunks.append(packet.body)
                    # RCON responses may be split into several packets. Continue
                    # collecting packets until the server has no more to send.
                return b"".join(chunks).decode("utf-8", errors="replace").strip()
        except (OSError, struct.error) as exc:
            raise RconError("Could not connect to the local RCON service") from exc
