from __future__ import annotations

import hashlib
import hmac
import json
import queue
import secrets
import socket
import threading
import time
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
    """Reference direct-invite host handshake.

    This owns only the admission handshake. The game remains responsible for
    its production gameplay transport after a peer is admitted.
    """

    def __init__(self, invite: Invite, bind_host: str = "0.0.0.0"):
        self.invite = invite
        self.bind_host = bind_host
        self._sock: socket.socket | None = None
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self._peer_queue: queue.Queue[Peer] = queue.Queue()
        self._seen_guest_nonces: set[str] = set()
        self._lock = threading.Lock()
        self.peers: list[Peer] = []

    def start(self) -> None:
        if self._sock is not None:
            return

        try:
            info = socket.getaddrinfo(
                self.bind_host,
                self.invite.port,
                family=socket.AF_UNSPEC,
                type=socket.SOCK_DGRAM,
                flags=socket.AI_PASSIVE,
            )[0]
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

    def wait_for_peer(self, timeout: float | None = None) -> Peer | None:
        """Return the next newly admitted peer, or None on timeout."""
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
                self._handle(json.loads(data.decode("utf-8")), addr)
            except Exception:
                continue

    def _handle(self, msg: dict, addr) -> None:
        if msg.get("t") != "HELLO":
            return
        if msg.get("s") != self.invite.session_id:
            return
        if msg.get("g") != self.invite.game_id or msg.get("b") != self.invite.build:
            return

        guest_nonce = str(msg.get("n", ""))
        if not guest_nonce:
            return
        with self._lock:
            if guest_nonce in self._seen_guest_nonces:
                return

        expected = _mac(
            self.invite.session_key,
            "hello",
            self.invite.session_id,
            guest_nonce,
            self.invite.game_id,
            self.invite.build,
        )
        if not hmac.compare_digest(str(msg.get("m", "")), expected):
            return

        host_nonce = secrets.token_urlsafe(12)
        reply = {
            "t": "WELCOME",
            "s": self.invite.session_id,
            "gn": guest_nonce,
            "hn": host_nonce,
            "m": _mac(
                self.invite.session_key,
                "welcome",
                self.invite.session_id,
                guest_nonce,
                host_nonce,
            ),
        }
        assert self._sock is not None
        self._sock.sendto(json.dumps(reply, separators=(",", ":")).encode("utf-8"), addr)
        peer = Peer((str(addr[0]), int(addr[1])), guest_nonce, host_nonce)
        with self._lock:
            self._seen_guest_nonces.add(guest_nonce)
            self.peers.append(peer)
        self._peer_queue.put(peer)


def join_host(
    invite_token: str,
    *,
    timeout: float = 2.0,
    expected_game_id: str | None = None,
    expected_build: str | None = None,
) -> Peer:
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
        "s": invite.session_id,
        "g": invite.game_id,
        "b": invite.build,
        "n": guest_nonce,
        "m": _mac(
            invite.session_key,
            "hello",
            invite.session_id,
            guest_nonce,
            invite.game_id,
            invite.build,
        ),
    }
    payload = json.dumps(hello, separators=(",", ":")).encode("utf-8")

    try:
        endpoints = socket.getaddrinfo(
            invite.host,
            invite.port,
            family=socket.AF_UNSPEC,
            type=socket.SOCK_DGRAM,
        )
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

            if reply.get("t") != "WELCOME" or reply.get("s") != invite.session_id:
                raise HandshakeError("UNEXPECTED_HOST_RESPONSE")
            if reply.get("gn") != guest_nonce:
                raise HandshakeError("UNEXPECTED_HOST_RESPONSE")

            host_nonce = str(reply.get("hn", ""))
            expected = _mac(
                invite.session_key,
                "welcome",
                invite.session_id,
                guest_nonce,
                host_nonce,
            )
            if not hmac.compare_digest(str(reply.get("m", "")), expected):
                raise HandshakeError("HOST_AUTHENTICATION_FAILED")

            return Peer(
                address=(str(addr[0]), int(addr[1])),
                guest_nonce=guest_nonce,
                host_nonce=host_nonce,
            )
        except (socket.timeout, OSError, HandshakeError) as exc:
            last_error = exc
        finally:
            sock.close()

    raise HandshakeError("DIRECT_CONNECTION_UNAVAILABLE") from last_error
