import time
import unittest
from unittest.mock import patch

from axm_p2p.invite import Invite, InviteError, create_invite, decode_invite
from axm_p2p.udp import P2PHost, HandshakeError, _mac, join_host


class RecordingSocket:
    def __init__(self):
        self.sent = []

    def sendto(self, data, address):
        self.sent.append((data, address))


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

    def test_running_host_rejects_authenticated_hello_after_invite_expiry(self):
        invite = Invite(
            game_id="axm.game",
            build="build-1",
            host="127.0.0.1",
            port=29996,
            session_id="session-1",
            session_key="session-key-1",
            expires_at=100,
        )
        host = P2PHost(invite)
        recording_socket = RecordingSocket()
        host._sock = recording_socket
        guest_nonce = "guest-nonce-1"
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

        with patch("axm_p2p.udp.time.time", return_value=101):
            host._handle(hello, ("127.0.0.1", 40000))

        self.assertEqual(recording_socket.sent, [])
        self.assertEqual(host.peer_count, 0)
        self.assertIsNone(host.wait_for_peer(timeout=0))


if __name__ == "__main__":
    unittest.main()
