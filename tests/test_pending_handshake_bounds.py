import json
import unittest

from axm_p2p.invite import create_invite, decode_invite
from axm_p2p.udp import HANDSHAKE_PROTOCOL_VERSION, P2PHost, _mac


class _FakeSocket:
    def __init__(self):
        self.sent: list[tuple[dict, tuple[str, int]]] = []

    def sendto(self, payload: bytes, addr) -> None:
        self.sent.append((json.loads(payload.decode("utf-8")), addr))


class PendingHandshakeBoundsTests(unittest.TestCase):
    def _fixture(self, *, max_pending: int = 2, ttl: float = 5.0):
        now = [1000.0]
        token = create_invite(
            game_id="axm.game",
            build="build-1",
            host="127.0.0.1",
            port=29991,
            lifetime_seconds=60,
            now=1000,
        )
        invite = decode_invite(token, now=1000)
        host = P2PHost(
            invite,
            bind_host="127.0.0.1",
            clock=lambda: now[0],
            max_pending_handshakes=max_pending,
            pending_handshake_ttl_seconds=ttl,
        )
        fake = _FakeSocket()
        host._sock = fake
        return invite, host, fake, now

    @staticmethod
    def _hello(invite, guest_nonce: str) -> dict:
        return {
            "t": "HELLO",
            "pv": HANDSHAKE_PROTOCOL_VERSION,
            "s": invite.session_id,
            "g": invite.game_id,
            "b": invite.build,
            "n": guest_nonce,
            "m": _mac(
                invite.session_key,
                "hello",
                str(HANDSHAKE_PROTOCOL_VERSION),
                invite.session_id,
                guest_nonce,
                invite.game_id,
                invite.build,
            ),
        }

    @staticmethod
    def _ack(invite, guest_nonce: str, host_nonce: str) -> dict:
        return {
            "t": "ACK",
            "pv": HANDSHAKE_PROTOCOL_VERSION,
            "s": invite.session_id,
            "gn": guest_nonce,
            "hn": host_nonce,
            "m": _mac(
                invite.session_key,
                "ack",
                str(HANDSHAKE_PROTOCOL_VERSION),
                invite.session_id,
                guest_nonce,
                host_nonce,
            ),
        }

    def test_pending_handshakes_are_bounded(self):
        invite, host, fake, _ = self._fixture(max_pending=2)

        host._handle(self._hello(invite, "guest-a"), ("127.0.0.1", 41001))
        host._handle(self._hello(invite, "guest-b"), ("127.0.0.1", 41002))
        host._handle(self._hello(invite, "guest-c"), ("127.0.0.1", 41003))

        self.assertEqual(len(host._pending), 2)
        self.assertEqual(len(fake.sent), 2)
        self.assertEqual(host.peer_count, 0)

    def test_retry_reuses_welcome_without_extending_pending_lifetime(self):
        invite, host, fake, now = self._fixture(max_pending=1, ttl=5.0)
        addr_a = ("127.0.0.1", 42001)
        addr_b = ("127.0.0.1", 42002)
        hello_a = self._hello(invite, "guest-a")

        host._handle(hello_a, addr_a)
        first_welcome = fake.sent[-1][0]

        now[0] = 1004.0
        host._handle(hello_a, addr_a)
        second_welcome = fake.sent[-1][0]
        host._handle(self._hello(invite, "guest-b"), addr_b)

        self.assertEqual(len(host._pending), 1)
        self.assertEqual(len(fake.sent), 2)
        self.assertEqual(second_welcome["hn"], first_welcome["hn"])

        now[0] = 1005.0
        host._handle(self._hello(invite, "guest-b"), addr_b)

        self.assertEqual(len(host._pending), 1)
        self.assertEqual(len(fake.sent), 3)
        self.assertEqual(fake.sent[-1][0]["gn"], "guest-b")

    def test_expired_pending_slot_is_reclaimed_and_late_ack_cannot_admit(self):
        invite, host, fake, now = self._fixture(max_pending=1, ttl=5.0)
        addr_a = ("127.0.0.1", 43001)
        addr_b = ("127.0.0.1", 43002)

        host._handle(self._hello(invite, "guest-a"), addr_a)
        welcome_a = fake.sent[-1][0]
        now[0] = 1005.0
        host._handle(self._hello(invite, "guest-b"), addr_b)
        welcome_b = fake.sent[-1][0]

        self.assertEqual(len(host._pending), 1)
        self.assertEqual(len(fake.sent), 2)

        host._handle(self._ack(invite, "guest-a", welcome_a["hn"]), addr_a)
        self.assertEqual(host.peer_count, 0)

        host._handle(self._ack(invite, "guest-b", welcome_b["hn"]), addr_b)
        self.assertEqual(host.peer_count, 1)
        self.assertEqual(len(host._pending), 0)

    def test_invalid_pending_limits_fail_closed(self):
        token = create_invite(
            game_id="axm.game",
            build="build-1",
            host="127.0.0.1",
            port=29991,
            lifetime_seconds=60,
            now=1000,
        )
        invite = decode_invite(token, now=1000)

        with self.assertRaises(ValueError):
            P2PHost(invite, max_pending_handshakes=0)
        with self.assertRaises(ValueError):
            P2PHost(invite, max_pending_handshakes=True)
        with self.assertRaises(ValueError):
            P2PHost(invite, pending_handshake_ttl_seconds=0)
        with self.assertRaises(ValueError):
            P2PHost(invite, pending_handshake_ttl_seconds=True)


if __name__ == "__main__":
    unittest.main()
