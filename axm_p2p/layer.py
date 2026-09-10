from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable

from .invite import InviteError, create_invite, decode_invite
from .udp import HandshakeError, P2PHost, Peer, join_host


class LayerState(str, Enum):
    IDLE = "IDLE"
    HOSTING = "HOSTING"
    JOINING = "JOINING"
    CONNECTED = "CONNECTED"
    FAILED = "FAILED"
    CLOSED = "CLOSED"


@dataclass(frozen=True)
class JoinResult:
    state: LayerState
    code: str
    peer: Peer | None = None
    detail: str = ""

    @property
    def connected(self) -> bool:
        return self.state is LayerState.CONNECTED and self.peer is not None


class HostSession:
    """Game-facing host handle.

    Games can display `invite_token`, copy it to the clipboard, and poll/wait
    for admitted guests without depending on the UDP implementation details.
    Closing the handle also releases its owning layer's HOSTING state when the
    layer created it.
    """

    def __init__(
        self,
        invite_token: str,
        transport: P2PHost,
        *,
        on_close: Callable[["HostSession"], None] | None = None,
    ):
        self.invite_token = invite_token
        self._transport = transport
        self._on_close = on_close
        self.state = LayerState.HOSTING

    @property
    def peer_count(self) -> int:
        return self._transport.peer_count

    def wait_for_guest(self, timeout: float | None = None) -> Peer | None:
        if self.state is not LayerState.HOSTING:
            return None
        return self._transport.wait_for_peer(timeout=timeout)

    def close(self) -> None:
        if self.state is LayerState.CLOSED:
            return
        self._transport.close()
        self.state = LayerState.CLOSED
        if self._on_close is not None:
            self._on_close(self)

    def __enter__(self) -> "HostSession":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


class AXMP2PLayer:
    """Small stable integration seam for AXM games.

    The shooter or another game should call this layer instead of importing
    invite/HMAC/UDP implementation details directly. A future native or browser
    transport adapter can live behind the same high-level flow.

    One layer instance owns at most one active host session. This keeps the
    singular `state` value truthful and prevents a game from accidentally
    leaking a second listener while the first host handle is still active.
    """

    def __init__(self, *, game_id: str, build: str):
        if not game_id or not build:
            raise ValueError("game_id and build are required")
        self.game_id = game_id
        self.build = build
        self.state = LayerState.IDLE
        self._active_host_session: HostSession | None = None

    def _host_session_closed(self, session: HostSession) -> None:
        if self._active_host_session is session:
            self._active_host_session = None
            self.state = LayerState.CLOSED

    def host(
        self,
        *,
        public_host: str,
        port: int,
        bind_host: str = "0.0.0.0",
        lifetime_seconds: int = 3600,
    ) -> HostSession:
        if self._active_host_session is not None:
            raise HandshakeError("HOST_SESSION_ALREADY_ACTIVE")

        token = create_invite(
            game_id=self.game_id,
            build=self.build,
            host=public_host,
            port=port,
            lifetime_seconds=lifetime_seconds,
        )
        invite = decode_invite(token)
        transport = P2PHost(invite, bind_host=bind_host)
        transport.start()
        session = HostSession(token, transport, on_close=self._host_session_closed)
        self._active_host_session = session
        self.state = LayerState.HOSTING
        return session

    def join(self, invite_token: str, *, timeout: float = 2.0) -> JoinResult:
        if self._active_host_session is not None:
            return JoinResult(
                LayerState.FAILED,
                "HOST_SESSION_ALREADY_ACTIVE",
                detail="close the active host session before joining",
            )

        self.state = LayerState.JOINING
        try:
            peer = join_host(
                invite_token,
                timeout=timeout,
                expected_game_id=self.game_id,
                expected_build=self.build,
            )
        except InviteError as exc:
            self.state = LayerState.FAILED
            return JoinResult(LayerState.FAILED, "INVALID_INVITE", detail=str(exc))
        except HandshakeError as exc:
            self.state = LayerState.FAILED
            code = str(exc) or "DIRECT_CONNECTION_UNAVAILABLE"
            return JoinResult(LayerState.FAILED, code, detail=code)

        self.state = LayerState.CONNECTED
        return JoinResult(LayerState.CONNECTED, "DIRECT_CONNECTED", peer=peer)
