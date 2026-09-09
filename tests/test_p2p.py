import json
import socket
import time
import unittest

from axm_p2p.invite import InviteError, create_invite, decode_invite
from axm_p2p.udp import (
    HANDSHAKE_PROTOCOL_VERSION,
    HandshakeError,
    P2PHost,
    _mac,
    join_host,
)


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

    def test_corruption_rejected(self):
        token = create_invite(game_id="g", build="b", host="127.0.0.1", port=29993, lifetime_seconds=10, now=100)
        index = token.index(".") + 5
        replacement = "A" if token[index] != "A" else "B"
        corrupted = token[:index] + replacement + token[index + 1:]
        with self.assertRaises(InviteError):
            decode_invite(corrupted, now=101)


class _FakeSocket:
    def __init__(self):
        self.sent: list[tuple[dict, tuple[str, int]]] = []

    def sendto(self, payload: bytes, addr) -> None:
        self.sent.append((json.loads(payload.decode("utf-8")), addr))


class HandshakeTests(unittest.TestCase):
    def test_direct_local_handshake(self):
        port = free_udp_port()
        token = create_invite(game_id="axm.game", build="build-1", host="127.0.0.1", port=port, lifetime_seconds=30)
        inv = decode_invite(token)
        with P2PHost(inv, bind_host="127.0.0.1") as host:
            time.sleep(0.05)
            peer = join_host(token, timeout=1.0, expected_game_id="axm.game", expected_build="build-1")
            self.assertEqual(peer.address[0], "127.0.0.1")
            admitted = host.wait_for_peer(timeout=1.0)
            self.assertIsNotNone(admitted)
            self.assertEqual(host.peer_count, 1)

    def test_wrong_build_rejected_before_network(self):
        token = create_invite(game_id="axm.game", build="build-1", host="127.0.0.1", port=29995, lifetime_seconds=30)
        with self.assertRaises(HandshakeError):
            join_host(token, expected_build="build-2")

    def test_host_rejects_admission_after_invite_expiry(self):
        port = free_udp_port()
        token = create_invite(game_id="axm.game", build="build-1", host="127.0.0.1", port=port, lifetime_seconds=30)
        invite = decode_invite(token)
        expired_clock = lambda: invite.expires_at + 1

        with self.assertRaisesRegex(HandshakeError, "INVITE_EXPIRED"):
            P2PHost(invite, bind_host="127.0.0.1", clock=expired_clock).start()

        live_clock = [invite.expires_at]
        with P2PHost(invite, bind_host="127.0.0.1", clock=lambda: live_clock[0]) as host:
            live_clock[0] = invite.expires_at + 1
            with self.assertRaisesRegex(HandshakeError, "DIRECT_CONNECTION_UNAVAILABLE"):
                join_host(token, timeout=0.2, expected_game_id="axm.game", expected_build="build-1")
            self.assertEqual(host.peer_count, 0)

    def test_round_trip_ack_is_required_before_host_admission(self):
        token = create_invite(game_id="axm.game", build="build-1", host="127.0.0.1", port=29996, lifetime_seconds=30)
        invite = decode_invite(token)
        host = P2PHost(invite)
        fake = _FakeSocket()
        host._sock = fake
        addr = ("127.0.0.1", 40000)
        guest_nonce = "guest-nonce"
        hello = {
            "t": "HELLO",
            "pv": HANDSHAKE_PROTOCOL_VERSION,
            "s": invite.session_id,
            "g": invite.game_id,
            "b": invite.build,
            "n": guest_nonce,
            "m": _mac(invite.session_key, "hello", str(HANDSHAKE_PROTOCOL_VERSION), invite.session_id, guest_nonce, invite.game_id, invite.build),
        }

        host._handle(hello, addr)
        self.assertEqual(host.peer_count, 0)
        self.assertIsNone(host.wait_for_peer(timeout=0))

        welcome = fake.sent[-1][0]
        ack = {
            "t": "ACK",
            "pv": HANDSHAKE_PROTOCOL_VERSION,
            "s": invite.session_id,
            "gn": guest_nonce,
            "hn": welcome["hn"],
            "m": _mac(invite.session_key, "ack", str(HANDSHAKE_PROTOCOL_VERSION), invite.session_id, guest_nonce, welcome["hn"]),
        }
        host._handle(ack, addr)
        self.assertEqual(host.peer_count, 1)
        self.assertIsNotNone(host.wait_for_peer(timeout=0))

        host._handle(ack, addr)
        self.assertEqual(host.peer_count, 1)

    def test_wrong_handshake_version_is_not_admitted(self):
        token = create_invite(game_id="axm.game", build="build-1", host="127.0.0.1", port=29997, lifetime_seconds=30)
        invite = decode_invite(token)
        host = P2PHost(invite)
        fake = _FakeSocket()
        host._sock = fake
        guest_nonce = "old-guest"
        hello = {
            "t": "HELLO",
            "pv": 1,
            "s": invite.session_id,
            "g": invite.game_id,
            "b": invite.build,
            "n": guest_nonce,
            "m": _mac(invite.session_key, "hello", "1", invite.session_id, guest_nonce, invite.game_id, invite.build),
        }

        host._handle(hello, ("127.0.0.1", 40001))
        self.assertEqual(host.peer_count, 0)
        self.assertEqual(host._pending, {})
        self.assertEqual(fake.sent, [])

    def test_bad_ack_does_not_admit_or_consume_pending_handshake(self):
        token = create_invite(game_id="axm.game", build="build-1", host="127.0.0.1", port=29998, lifetime_seconds=30)
        invite = decode_invite(token)
        host = P2PHost(invite)
        fake = _FakeSocket()
        host._sock = fake
        addr = ("127.0.0.1", 40002)
        guest_nonce = "guest-bad-ack"
        hello = {
            "t": "HELLO",
            "pv": HANDSHAKE_PROTOCOL_VERSION,
            "s": invite.session_id,
            "g": invite.game_id,
            "b": invite.build,
            "n": guest_nonce,
            "m": _mac(invite.session_key, "hello", str(HANDSHAKE_PROTOCOL_VERSION), invite.session_id, guest_nonce, invite.game_id, invite.build),
        }
        host._handle(hello, addr)
        welcome = fake.sent[-1][0]
        bad_ack = {
            "t": "ACK",
            "pv": HANDSHAKE_PROTOCOL_VERSION,
            "s": invite.session_id,
            "gn": guest_nonce,
            "hn": welcome["hn"],
            "m": "not-valid",
        }
        host._handle(bad_ack, addr)
        self.assertEqual(host.peer_count, 0)
        self.assertEqual(len(host._pending), 1)


if __name__ == "__main__":
    unittest.main()
