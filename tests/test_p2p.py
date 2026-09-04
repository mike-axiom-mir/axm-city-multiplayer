import time
import unittest

from axm_p2p.invite import InviteError, create_invite, decode_invite
from axm_p2p.udp import P2PHost, HandshakeError, join_host


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
        replacement = "A" if token[-1] != "A" else "B"
        with self.assertRaises(InviteError):
            decode_invite(token[:-1] + replacement, now=101)


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


if __name__ == "__main__":
    unittest.main()
