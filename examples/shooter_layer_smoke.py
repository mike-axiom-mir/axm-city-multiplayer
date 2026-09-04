"""Minimal future shooter integration smoke test.

This deliberately proves only the reusable lobby/direct-admission layer.
Gameplay replication remains the shooter's own transport/state concern.
"""

import socket

from axm_p2p import AXMP2PLayer


def free_udp_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def main() -> None:
    port = free_udp_port()
    host_game = AXMP2PLayer(game_id="axm.shooter", build="layer-smoke-1")
    guest_game = AXMP2PLayer(game_id="axm.shooter", build="layer-smoke-1")

    with host_game.host(public_host="127.0.0.1", bind_host="127.0.0.1", port=port) as host:
        print("HOST_UI_COPY_INVITE", host.invite_token)
        result = guest_game.join(host.invite_token, timeout=1.0)
        print("GUEST_UI_RESULT", result.code)
        peer = host.wait_for_guest(timeout=1.0)
        print("HOST_UI_GUEST_JOINED", peer is not None)


if __name__ == "__main__":
    main()
