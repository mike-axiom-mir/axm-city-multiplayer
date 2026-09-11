from __future__ import annotations

import base64
import hashlib
import json
import secrets
import time
from dataclasses import dataclass

PREFIX = "AXMP2P1."
MAX_INVITE_TOKEN_CHARS = 4096


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
    if not text:
        raise InviteError("invite is not valid base64url")
    pad = "=" * (-len(text) % 4)
    try:
        decoded = base64.b64decode(text + pad, altchars=b"-_", validate=True)
    except Exception as exc:
        raise InviteError("invite is not valid base64url") from exc
    if _b64e(decoded) != text:
        raise InviteError("invite is not canonical base64url")
    return decoded


def _require_text(payload: dict, field: str) -> str:
    value = payload[field]
    if type(value) is not str or not value:
        raise InviteError(f"invalid {field} field")
    return value


def _require_bounded_token(token: str) -> str:
    if len(token) > MAX_INVITE_TOKEN_CHARS:
        raise InviteError("invite exceeds maximum size")
    return token


def create_invite(*, game_id: str, build: str, host: str, port: int, lifetime_seconds: int = 3600, now: int | None = None) -> str:
    if any(type(value) is not str or not value for value in (game_id, build, host)):
        raise InviteError("game_id, build, and host must be non-empty strings")
    if type(port) is not int or not (1 <= port <= 65535):
        raise InviteError("port must be an integer between 1 and 65535")
    if type(lifetime_seconds) is not int or lifetime_seconds <= 0:
        raise InviteError("lifetime_seconds must be a positive integer")

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
    return _require_bounded_token(PREFIX + _b64e(body + checksum))


def decode_invite(token: str, *, now: int | None = None) -> Invite:
    if type(token) is not str or not token.startswith(PREFIX):
        raise InviteError("unsupported invite prefix")
    _require_bounded_token(token)

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
    if type(payload) is not dict or set(payload) != required:
        raise InviteError("invite payload shape is invalid")
    if body != _canonical(payload):
        raise InviteError("invite payload is not canonical JSON")
    if type(payload["v"]) is not int or payload["v"] != 1:
        raise InviteError("unsupported protocol version")

    game_id = _require_text(payload, "g")
    build = _require_text(payload, "b")
    host = _require_text(payload, "h")
    session_id = _require_text(payload, "s")
    session_key = _require_text(payload, "k")

    port = payload["p"]
    if type(port) is not int or not (1 <= port <= 65535):
        raise InviteError("invalid port")
    expires_at = payload["e"]
    if type(expires_at) is not int:
        raise InviteError("invalid expiry")

    now = int(time.time() if now is None else now)
    if expires_at < now:
        raise InviteError("invite has expired")

    return Invite(
        game_id=game_id,
        build=build,
        host=host,
        port=port,
        session_id=session_id,
        session_key=session_key,
        expires_at=expires_at,
        protocol=1,
    )
