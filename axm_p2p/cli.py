from __future__ import annotations

import argparse
import sys
import time

from .invite import create_invite, decode_invite
from .udp import P2PHost, join_host, HandshakeError


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="axm-p2p")
    sub = p.add_subparsers(dest="command", required=True)

    host = sub.add_parser("host", help="create an invite and wait for direct UDP guests")
    host.add_argument("--game", required=True)
    host.add_argument("--build", required=True)
    host.add_argument("--public-host", required=True, help="IP/DNS guests can reach directly")
    host.add_argument("--port", type=int, default=28741)
    host.add_argument("--minutes", type=int, default=60)

    join = sub.add_parser("join", help="paste an AXM P2P invite and connect directly")
    join.add_argument("invite")
    join.add_argument("--game")
    join.add_argument("--build")
    join.add_argument("--timeout", type=float, default=3.0)

    show = sub.add_parser("show", help="decode an invite locally")
    show.add_argument("invite")
    return p


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)

    if args.command == "host":
        token = create_invite(game_id=args.game, build=args.build, host=args.public_host, port=args.port, lifetime_seconds=args.minutes * 60)
        inv = decode_invite(token)
        print("COPY THIS INVITE:")
        print(token)
        print()
        print(f"Listening on UDP {args.port}. Keep this game open.")
        print("No AXM relay exists. If the guest cannot reach this port, the connection fails.")
        try:
            with P2PHost(inv):
                while True:
                    time.sleep(0.5)
        except KeyboardInterrupt:
            return 0

    if args.command == "join":
        try:
            peer = join_host(args.invite, timeout=args.timeout, expected_game_id=args.game, expected_build=args.build)
        except HandshakeError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        print(f"DIRECT_CONNECTED {peer.address[0]}:{peer.address[1]}")
        return 0

    if args.command == "show":
        print(decode_invite(args.invite))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
