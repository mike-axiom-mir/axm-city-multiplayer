import json
import socket
import threading
import time
import unittest
from unittest import mock

from axm_p2p.invite import InviteError, create_invite, decode_invite
from axm_p2p.udp import P2PHost, HandshakeError, _mac, join_host


def free_udp_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


class InviteTests(unittest.TestCase):
    def test_round_trip(self):
        token = create_invite(game_id="axm.test", build="abc123", host="127.0.0.1", port=29991, lifetime_seconds=30, now=100)
        inv = decode_invite(token, now=101)
        self.assertEqual(inv.game_id, "axm.test")
        self.assertEqual(inv.build, "abc123")
        self.assertEqual(inv.host, "127.0.0.1")
        self.assertEqual(inv.port, 29991)

    def test_expired_rejected(self):
        token = create_invite(game_id="g", build="b", host="127.0.0.1", port=29992, lifetime_seconds=1, now=100)
        with self.assertRaises(InviteError):
            decode_invite(token, now=102)

    def test_expiry_boundary_is_shared(self):
        token = create_invite(game_id="g", build="b", host="127.0.0.1", port=29992, lifetime_seconds=1, now=100)
        inv = decode_invite(token, now=101)
        self.assertFalse(inv.is_expired(now=101))
        self.assertTrue(inv.is_expired(now=102))

    def test_corruption_rejected(self):
        token = create_invite(game_id="g", build="b", host="127.0.0.1", port=29993, lifetime_seconds=10, now=100)
        index = len("AXMP2P1.") + 4
        replacement = "A" if token[index] != "A" else "B"
        with self.assertRaises(InviteError):
            decode_invite(token[:index] + replacement + token[index + 1 :], now=101)


class HandshakeTests(unittest.TestCase):
    def test_direct_local_handshake(self):
        port = free_udp_port()
        token = create_invite(game_id="axm.game", build="build-1", host="127.0.0.1", port=port, lifetime_seconds=30)
        inv = decode_invite(token)
        with P2PHost(inv, bind_host="127.0.0.1"):
            peer = join_host(token, timeout=1.0, expected_game_id="axm.game", expected_build="build-1")
            self.assertEqual(peer.address[0], "127.0.0.1")

    def test_wrong_build_rejected_before_network(self):
        token = create_invite(game_id="axm.game", build="build-1", host="127.0.0.1", port=free_udp_port(), lifetime_seconds=30)
        with self.assertRaises(HandshakeError):
            join_host(token, expected_build="build-2")

    def test_expired_host_refuses_to_start(self):
        token = create_invite(game_id="axm.game", build="build-1", host="127.0.0.1", port=free_udp_port(), lifetime_seconds=1, now=100)
        inv = decode_invite(token, now=100)
        host = P2PHost(inv, bind_host="127.0.0.1", clock=lambda: 102)
        with self.assertRaisesRegex(HandshakeError, "INVITE_EXPIRED"):
            host.start()
        self.assertEqual(host.peer_count, 0)

    def test_running_host_does_not_admit_after_expiry(self):
        base = int(time.time())
        port = free_udp_port()
        token = create_invite(game_id="axm.game", build="build-1", host="127.0.0.1", port=port, lifetime_seconds=30, now=base)
        inv = decode_invite(token, now=base)
        host_now = [base]
        with P2PHost(inv, bind_host="127.0.0.1", clock=lambda: host_now[0]) as host:
            host_now[0] = inv.expires_at + 1
            # Model a skewed/stale guest that still considers the token valid.
            # The host must enforce its own admission boundary rather than trusting guests.
            with mock.patch("axm_p2p.invite.time.time", return_value=base):
                with self.assertRaisesRegex(HandshakeError, "DIRECT_CONNECTION_UNAVAILABLE"):
                    join_host(token, timeout=0.2, expected_game_id="axm.game", expected_build="build-1")
            self.assertEqual(host.peer_count, 0)
            self.assertIsNone(host.wait_for_peer(timeout=0.05))

    def test_welcome_from_uninvited_endpoint_is_ignored(self):
        intended = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        attacker = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        intended.bind(("127.0.0.1", 0))
        attacker.bind(("127.0.0.1", 0))
        intended.settimeout(1.0)

        token = create_invite(
            game_id="axm.game",
            build="build-1",
            host="127.0.0.1",
            port=intended.getsockname()[1],
            lifetime_seconds=30,
        )
        invite = decode_invite(token)

        def race_welcome_from_wrong_port():
            data, guest_address = intended.recvfrom(4096)
            hello = json.loads(data.decode("utf-8"))
            host_nonce = "attacker-host-nonce"
            reply = {
                "t": "WELCOME",
                "s": invite.session_id,
                "gn": hello["n"],
                "hn": host_nonce,
                "m": _mac(
                    invite.session_key,
                    "welcome",
                    invite.session_id,
                    hello["n"],
                    host_nonce,
                ),
            }
            attacker.sendto(
                json.dumps(reply, separators=(",", ":")).encode("utf-8"),
                guest_address,
            )

        racer = threading.Thread(target=race_welcome_from_wrong_port)
        racer.start()
        try:
            with self.assertRaisesRegex(HandshakeError, "DIRECT_CONNECTION_UNAVAILABLE"):
                join_host(
                    token,
                    timeout=0.2,
                    expected_game_id="axm.game",
                    expected_build="build-1",
                )
        finally:
            racer.join(timeout=1.0)
            intended.close()
            attacker.close()
        self.assertFalse(racer.is_alive())


if __name__ == "__main__":
    unittest.main()
