import json
import socket
import threading
import time
import unittest

from axm_p2p.invite import InviteError, create_invite, decode_invite
from axm_p2p.udp import P2PHost, HandshakeError, _mac, join_host


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

    def test_corruption_rejected(self):
        token = create_invite(game_id="g", build="b", host="127.0.0.1", port=29993, lifetime_seconds=10, now=100)
        index = len("AXMP2P1.") + 4
        replacement = "A" if token[index] != "A" else "B"
        with self.assertRaises(InviteError):
            decode_invite(token[:index] + replacement + token[index + 1 :], now=101)


class HandshakeTests(unittest.TestCase):
    def test_direct_local_handshake(self):
        token = create_invite(game_id="axm.game", build="build-1", host="127.0.0.1", port=29994, lifetime_seconds=30)
        inv = decode_invite(token)
        with P2PHost(inv):
            time.sleep(0.05)
            peer = join_host(token, timeout=1.0, expected_game_id="axm.game", expected_build="build-1")
            self.assertEqual(peer.address[0], "127.0.0.1")

    def test_wrong_build_rejected_before_network(self):
        token = create_invite(game_id="axm.game", build="build-1", host="127.0.0.1", port=29995, lifetime_seconds=30)
        with self.assertRaises(HandshakeError):
            join_host(token, expected_build="build-2")

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
