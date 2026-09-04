from __future__ import annotations

import hashlib
import hmac
import json
import secrets
import socket
import threading
from dataclasses import dataclass

from .invite import Invite, decode_invite


class HandshakeError(RuntimeError):
    pass


def _mac(key: str, *parts: str) -> str:
    message = "|".join(parts).encode("utf-8")
    return hmac.new(key.encode("utf-8"), message, hashlib.sha256).hexdigest()


@dataclass(frozen=True)
class Peer:
    address: tuple[str, int]
    guest_nonce: str
    host_nonce: str


class P2PHost:
    """Small UDP reference host for validating AXM direct-invite semantics.

    This is a handshake/reference layer, not a full production game transport.
    Engines may replace the data transport while retaining the invite contract.
    """

    def __init__(self, invite: Invite, bind_host: str = "0.0.0.0"):
        self.invite = invite
        self.bind_host = bind_host
        self._sock: socket.socket | None = None
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self.peers: list[Peer] = []

    def start(self) -> None:
        if self._sock is not None:
            return
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.bind_host, self.invite.port))
        sock.settimeout(0.2)
        self._sock = sock
        self._thread = threading.Thread(target=self._serve, daemon=True)
        self._thread.start()

    def close(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=1.0)
        if self._sock:
            self._sock.close()
        self._sock = None
        self._thread = None

    def __enter__(self) -> "P2PHost":
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def _serve(self) -> None:
        assert self._sock is not None
        while not self._stop.is_set():
            try:
                data, addr = self._sock.recvfrom(4096)
            except socket.timeout:
                continue
            except OSError:
                return
            try:
                self._handle(json.loads(data.decode("utf-8")), addr)
            except Exception:
                continue

    def _handle(self, msg: dict, addr: tuple[str, int]) -> None:
        if msg.get("t") != "HELLO":
            return
        if msg.get("s") != self.invite.session_id:
            return
        if msg.get("g") != self.invite.game_id or msg.get("b") != self.invite.build:
            return

        guest_nonce = str(msg.get("n", ""))
        expected = _mac(self.invite.session_key, "hello", self.invite.session_id, guest_nonce, self.invite.game_id, self.invite.build)
        if not hmac.compare_digest(str(msg.get("m", "")), expected):
            return

        host_nonce = secrets.token_urlsafe(12)
        reply = {
            "t": "WELCOME",
            "s": self.invite.session_id,
            "gn": guest_nonce,
            "hn": host_nonce,
            "m": _mac(self.invite.session_key, "welcome", self.invite.session_id, guest_nonce, host_nonce),
        }
        self._sock.sendto(json.dumps(reply, separators=(",", ":")).encode("utf-8"), addr)
        self.peers.append(Peer(addr, guest_nonce, host_nonce))


def join_host(invite_token: str, *, timeout: float = 2.0, expected_game_id: str | None = None, expected_build: str | None = None) -> Peer:
    invite = decode_invite(invite_token)
    if expected_game_id is not None and invite.game_id != expected_game_id:
        raise HandshakeError("invite belongs to a different game")
    if expected_build is not None and invite.build != expected_build:
        raise HandshakeError("invite belongs to an incompatible build")

    guest_nonce = secrets.token_urlsafe(12)
    hello = {
        "t": "HELLO",
        "s": invite.session_id,
        "g": invite.game_id,
        "b": invite.build,
        "n": guest_nonce,
        "m": _mac(invite.session_key, "hello", invite.session_id, guest_nonce, invite.game_id, invite.build),
    }

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    try:
        sock.sendto(json.dumps(hello, separators=(",", ":")).encode("utf-8"), (invite.host, invite.port))
        try:
            data, addr = sock.recvfrom(4096)
        except socket.timeout as exc:
            raise HandshakeError("DIRECT_CONNECTION_UNAVAILABLE") from exc

        try:
            reply = json.loads(data.decode("utf-8"))
        except Exception as exc:
            raise HandshakeError("invalid host response") from exc

        if reply.get("t") != "WELCOME" or reply.get("s") != invite.session_id:
            raise HandshakeError("unexpected host response")
        if reply.get("gn") != guest_nonce:
            raise HandshakeError("host response does not match this join attempt")

        host_nonce = str(reply.get("hn", ""))
        expected = _mac(invite.session_key, "welcome", invite.session_id, guest_nonce, host_nonce)
        if not hmac.compare_digest(str(reply.get("m", "")), expected):
            raise HandshakeError("host authentication failed")

        return Peer(address=addr, guest_nonce=guest_nonce, host_nonce=host_nonce)
    finally:
        sock.close()
