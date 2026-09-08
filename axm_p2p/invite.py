from __future__ import annotations

import base64
import hashlib
import json
import secrets
import time
from dataclasses import dataclass

PREFIX = "AXMP2P1."


class InviteError(ValueError):
    pass


@dataclass(frozen=True)
class Invite:
    game_id: str
    build: str
    host: str
    port: int
    session_id: str
    session_key: str
    expires_at: int
    protocol: int = 1

    def as_payload(self) -> dict:
        return {
            "v": self.protocol,
            "g": self.game_id,
            "b": self.build,
            "h": self.host,
            "p": self.port,
            "s": self.session_id,
            "k": self.session_key,
            "e": self.expires_at,
        }


def _canonical(payload: dict) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _b64e(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _b64d(text: str) -> bytes:
    pad = "=" * (-len(text) % 4)
    try:
        return base64.urlsafe_b64decode(text + pad)
    except Exception as exc:
        raise InviteError("invite is not valid base64url") from exc


def create_invite(*, game_id: str, build: str, host: str, port: int, lifetime_seconds: int = 3600, now: int | None = None) -> str:
    if not game_id or not build or not host:
        raise InviteError("game_id, build, and host are required")
    if not (1 <= port <= 65535):
        raise InviteError("port must be between 1 and 65535")
    if lifetime_seconds <= 0:
        raise InviteError("lifetime_seconds must be positive")

    now = int(time.time() if now is None else now)
    invite = Invite(
        game_id=game_id,
        build=build,
        host=host,
        port=port,
        session_id=secrets.token_urlsafe(12),
        session_key=secrets.token_urlsafe(32),
        expires_at=now + lifetime_seconds,
    )
    payload = invite.as_payload()
    body = _canonical(payload)
    checksum = hashlib.sha256(body).digest()[:10]
    return PREFIX + _b64e(body + checksum)


def decode_invite(token: str, *, now: int | None = None) -> Invite:
    if not token.startswith(PREFIX):
        raise InviteError("unsupported invite prefix")

    raw = _b64d(token[len(PREFIX):])
    if len(raw) <= 10:
        raise InviteError("invite is truncated")

    body, checksum = raw[:-10], raw[-10:]
    expected = hashlib.sha256(body).digest()[:10]
    if not secrets.compare_digest(checksum, expected):
        raise InviteError("invite checksum mismatch")

    try:
        payload = json.loads(body.decode("utf-8"))
    except Exception as exc:
        raise InviteError("invite payload is invalid JSON") from exc

    required = {"v", "g", "b", "h", "p", "s", "k", "e"}
    if set(payload) != required:
        raise InviteError("invite payload shape is invalid")
    if payload["v"] != 1:
        raise InviteError("unsupported protocol version")
    if not isinstance(payload["p"], int) or not (1 <= payload["p"] <= 65535):
        raise InviteError("invalid port")

    now = int(time.time() if now is None else now)
    if int(payload["e"]) < now:
        raise InviteError("invite has expired")

    return Invite(
        game_id=str(payload["g"]),
        build=str(payload["b"]),
        host=str(payload["h"]),
        port=int(payload["p"]),
        session_id=str(payload["s"]),
        session_key=str(payload["k"]),
        expires_at=int(payload["e"]),
        protocol=1,
    )
