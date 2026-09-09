from __future__ import annotations

import hashlib
import hmac
import json
import queue
import secrets
import socket
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass

from .invite import Invite, decode_invite


HANDSHAKE_PROTOCOL_VERSION = 2


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
    """Reference direct-invite host handshake.

    Host admission is authoritative only after an authenticated guest ACK proves
    the guest received this host's WELCOME. HELLO alone never emits a peer.
    """

    def __init__(
        self,
        invite: Invite,
        bind_host: str = "0.0.0.0",
        *,
        clock: Callable[[], float] = time.time,
    ):
        self.invite = invite
        self.bind_host = bind_host
        self._clock = clock
        self._sock: socket.socket | None = None
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self._peer_queue: queue.Queue[Peer] = queue.Queue()
        self._pending: dict[tuple[str, int, str], str] = {}
        self._seen_guest_nonces: set[str] = set()
        self._lock = threading.Lock()
        self.peers: list[Peer] = []

    def _invite_expired(self) -> bool:
        return self.invite.expires_at < int(self._clock())

    def start(self) -> None:
        if self._sock is not None:
            return
        if self._invite_expired():
            raise HandshakeError("INVITE_EXPIRED")
        try:
            info = socket.getaddrinfo(self.bind_host, self.invite.port, family=socket.AF_UNSPEC, type=socket.SOCK_DGRAM, flags=socket.AI_PASSIVE)[0]
        except OSError as exc:
            raise HandshakeError(f"cannot bind host endpoint: {exc}") from exc
        family, socktype, proto, _, sockaddr = info
        sock = socket.socket(family, socktype, proto)
        sock.bind(sockaddr)
        sock.settimeout(0.2)
        self._sock = sock
        self._stop.clear()
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
        with self._lock:
            self._pending.clear()

    def wait_for_peer(self, timeout: float | None = None) -> Peer | None:
        try:
            return self._peer_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    @property
    def peer_count(self) -> int:
        with self._lock:
            return len(self.peers)

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
                message = json.loads(data.decode("utf-8"))
                if isinstance(message, dict):
                    self._handle(message, addr)
            except Exception:
                continue

    @staticmethod
    def _address_key(addr) -> tuple[str, int]:
        return (str(addr[0]), int(addr[1]))

    def _handle(self, msg: dict, addr) -> None:
        if self._invite_expired():
            return
        message_type = msg.get("t")
        if message_type == "HELLO":
            self._handle_hello(msg, addr)
        elif message_type == "ACK":
            self._handle_ack(msg, addr)

    def _handle_hello(self, msg: dict, addr) -> None:
        if msg.get("pv") != HANDSHAKE_PROTOCOL_VERSION:
            return
        if msg.get("s") != self.invite.session_id:
            return
        if msg.get("g") != self.invite.game_id or msg.get("b") != self.invite.build:
            return

        guest_nonce = str(msg.get("n", ""))
        if not guest_nonce:
            return
        address = self._address_key(addr)
        pending_key = (address[0], address[1], guest_nonce)
        with self._lock:
            if guest_nonce in self._seen_guest_nonces:
                return
            host_nonce = self._pending.get(pending_key)

        expected = _mac(self.invite.session_key, "hello", str(HANDSHAKE_PROTOCOL_VERSION), self.invite.session_id, guest_nonce, self.invite.game_id, self.invite.build)
        if not hmac.compare_digest(str(msg.get("m", "")), expected):
            return

        if host_nonce is None:
            host_nonce = secrets.token_urlsafe(12)
            with self._lock:
                self._pending[pending_key] = host_nonce

        reply = {
            "t": "WELCOME",
            "pv": HANDSHAKE_PROTOCOL_VERSION,
            "s": self.invite.session_id,
            "gn": guest_nonce,
            "hn": host_nonce,
            "m": _mac(self.invite.session_key, "welcome", str(HANDSHAKE_PROTOCOL_VERSION), self.invite.session_id, guest_nonce, host_nonce),
        }
        assert self._sock is not None
        self._sock.sendto(json.dumps(reply, separators=(",", ":")).encode("utf-8"), addr)

    def _handle_ack(self, msg: dict, addr) -> None:
        if msg.get("pv") != HANDSHAKE_PROTOCOL_VERSION or msg.get("s") != self.invite.session_id:
            return
        guest_nonce = str(msg.get("gn", ""))
        host_nonce = str(msg.get("hn", ""))
        if not guest_nonce or not host_nonce:
            return
        address = self._address_key(addr)
        pending_key = (address[0], address[1], guest_nonce)
        with self._lock:
            if guest_nonce in self._seen_guest_nonces:
                return
            expected_host_nonce = self._pending.get(pending_key)
        if expected_host_nonce != host_nonce:
            return
        expected = _mac(self.invite.session_key, "ack", str(HANDSHAKE_PROTOCOL_VERSION), self.invite.session_id, guest_nonce, host_nonce)
        if not hmac.compare_digest(str(msg.get("m", "")), expected):
            return

        peer = Peer(address, guest_nonce, host_nonce)
        with self._lock:
            if guest_nonce in self._seen_guest_nonces:
                return
            self._seen_guest_nonces.add(guest_nonce)
            self._pending.pop(pending_key, None)
            self.peers.append(peer)
        self._peer_queue.put(peer)


def join_host(invite_token: str, *, timeout: float = 2.0, expected_game_id: str | None = None, expected_build: str | None = None) -> Peer:
    invite = decode_invite(invite_token)
    if expected_game_id is not None and invite.game_id != expected_game_id:
        raise HandshakeError("WRONG_GAME")
    if expected_build is not None and invite.build != expected_build:
        raise HandshakeError("INCOMPATIBLE_BUILD")
    if timeout <= 0:
        raise HandshakeError("DIRECT_CONNECTION_UNAVAILABLE")

    guest_nonce = secrets.token_urlsafe(12)
    hello = {
        "t": "HELLO",
        "pv": HANDSHAKE_PROTOCOL_VERSION,
        "s": invite.session_id,
        "g": invite.game_id,
        "b": invite.build,
        "n": guest_nonce,
        "m": _mac(invite.session_key, "hello", str(HANDSHAKE_PROTOCOL_VERSION), invite.session_id, guest_nonce, invite.game_id, invite.build),
    }
    payload = json.dumps(hello, separators=(",", ":")).encode("utf-8")

    try:
        endpoints = socket.getaddrinfo(invite.host, invite.port, family=socket.AF_UNSPEC, type=socket.SOCK_DGRAM)
    except OSError as exc:
        raise HandshakeError("DIRECT_CONNECTION_UNAVAILABLE") from exc

    deadline = time.monotonic() + timeout
    last_error: Exception | None = None
    for index, (family, socktype, proto, _, sockaddr) in enumerate(endpoints):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        candidates_left = max(1, len(endpoints) - index)
        per_candidate_timeout = max(0.05, remaining / candidates_left)

        sock = socket.socket(family, socktype, proto)
        sock.settimeout(per_candidate_timeout)
        try:
            sock.sendto(payload, sockaddr)
            data, addr = sock.recvfrom(4096)
            try:
                reply = json.loads(data.decode("utf-8"))
            except Exception as exc:
                raise HandshakeError("INVALID_HOST_RESPONSE") from exc
            if not isinstance(reply, dict):
                raise HandshakeError("INVALID_HOST_RESPONSE")
            if reply.get("pv") != HANDSHAKE_PROTOCOL_VERSION:
                raise HandshakeError("INCOMPATIBLE_HANDSHAKE")
            if reply.get("t") != "WELCOME" or reply.get("s") != invite.session_id:
                raise HandshakeError("UNEXPECTED_HOST_RESPONSE")
            if reply.get("gn") != guest_nonce:
                raise HandshakeError("UNEXPECTED_HOST_RESPONSE")

            host_nonce = str(reply.get("hn", ""))
            if not host_nonce:
                raise HandshakeError("UNEXPECTED_HOST_RESPONSE")
            expected = _mac(invite.session_key, "welcome", str(HANDSHAKE_PROTOCOL_VERSION), invite.session_id, guest_nonce, host_nonce)
            if not hmac.compare_digest(str(reply.get("m", "")), expected):
                raise HandshakeError("HOST_AUTHENTICATION_FAILED")

            ack = {
                "t": "ACK",
                "pv": HANDSHAKE_PROTOCOL_VERSION,
                "s": invite.session_id,
                "gn": guest_nonce,
                "hn": host_nonce,
                "m": _mac(invite.session_key, "ack", str(HANDSHAKE_PROTOCOL_VERSION), invite.session_id, guest_nonce, host_nonce),
            }
            sock.sendto(json.dumps(ack, separators=(",", ":")).encode("utf-8"), sockaddr)
            return Peer(address=(str(addr[0]), int(addr[1])), guest_nonce=guest_nonce, host_nonce=host_nonce)
        except (socket.timeout, OSError, HandshakeError) as exc:
            last_error = exc
        finally:
            sock.close()

    if isinstance(last_error, HandshakeError) and str(last_error) == "INCOMPATIBLE_HANDSHAKE":
        raise last_error
    raise HandshakeError("DIRECT_CONNECTION_UNAVAILABLE") from last_error
