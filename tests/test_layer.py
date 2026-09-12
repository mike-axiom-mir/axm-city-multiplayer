import socket
import threading
import unittest
from unittest.mock import patch

from axm_p2p import AXMP2PLayer, HandshakeError, LayerState, Peer


def free_udp_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


class LayerTests(unittest.TestCase):
    def test_game_facing_host_join_flow(self):
        port = free_udp_port()
        host_layer = AXMP2PLayer(game_id="axm.shooter", build="test-build")
        guest_layer = AXMP2PLayer(game_id="axm.shooter", build="test-build")

        with host_layer.host(public_host="127.0.0.1", bind_host="127.0.0.1", port=port) as host:
            result = guest_layer.join(host.invite_token, timeout=1.0)
            self.assertTrue(result.connected)
            self.assertEqual(result.code, "DIRECT_CONNECTED")
            admitted = host.wait_for_guest(timeout=1.0)
            self.assertIsNotNone(admitted)
            self.assertEqual(host.peer_count, 1)
            self.assertEqual(host_layer.state, LayerState.HOSTING)

        self.assertEqual(host.state, LayerState.CLOSED)
        self.assertEqual(host_layer.state, LayerState.CLOSED)

    def test_host_session_close_releases_layer_for_rehost(self):
        layer = AXMP2PLayer(game_id="axm.shooter", build="build-a")
        first = layer.host(
            public_host="127.0.0.1",
            bind_host="127.0.0.1",
            port=free_udp_port(),
        )
        self.assertEqual(layer.state, LayerState.HOSTING)

        first.close()
        self.assertEqual(first.state, LayerState.CLOSED)
        self.assertEqual(layer.state, LayerState.CLOSED)

        second = layer.host(
            public_host="127.0.0.1",
            bind_host="127.0.0.1",
            port=free_udp_port(),
        )
        try:
            self.assertEqual(layer.state, LayerState.HOSTING)
        finally:
            second.close()
        self.assertEqual(layer.state, LayerState.CLOSED)

    def test_second_host_is_refused_while_session_is_active(self):
        layer = AXMP2PLayer(game_id="axm.shooter", build="build-a")
        host = layer.host(
            public_host="127.0.0.1",
            bind_host="127.0.0.1",
            port=free_udp_port(),
        )
        try:
            with self.assertRaisesRegex(HandshakeError, "^HOST_SESSION_ALREADY_ACTIVE$"):
                layer.host(
                    public_host="127.0.0.1",
                    bind_host="127.0.0.1",
                    port=free_udp_port(),
                )
            self.assertEqual(layer.state, LayerState.HOSTING)
            self.assertEqual(host.state, LayerState.HOSTING)
        finally:
            host.close()

    def test_join_is_held_without_network_attempt_while_hosting(self):
        layer = AXMP2PLayer(game_id="axm.shooter", build="build-a")
        host = layer.host(
            public_host="127.0.0.1",
            bind_host="127.0.0.1",
            port=free_udp_port(),
        )
        try:
            result = layer.join("not-an-axm-invite", timeout=0.1)
            self.assertFalse(result.connected)
            self.assertEqual(result.code, "HOST_SESSION_ALREADY_ACTIVE")
            self.assertEqual(result.state, LayerState.FAILED)
            self.assertEqual(layer.state, LayerState.HOSTING)
        finally:
            host.close()

    def test_wrong_build_has_stable_result_code(self):
        port = free_udp_port()
        host_layer = AXMP2PLayer(game_id="axm.shooter", build="build-a")
        guest_layer = AXMP2PLayer(game_id="axm.shooter", build="build-b")
        with host_layer.host(public_host="127.0.0.1", bind_host="127.0.0.1", port=port) as host:
            result = guest_layer.join(host.invite_token, timeout=0.2)
            self.assertFalse(result.connected)
            self.assertEqual(result.code, "INCOMPATIBLE_BUILD")
            self.assertEqual(result.state, LayerState.FAILED)

    def test_bad_invite_is_not_network_attempt(self):
        layer = AXMP2PLayer(game_id="axm.shooter", build="build-a")
        result = layer.join("not-an-axm-invite", timeout=0.1)
        self.assertFalse(result.connected)
        self.assertEqual(result.code, "INVALID_INVITE")

    def test_second_join_is_held_while_first_join_is_in_flight(self):
        layer = AXMP2PLayer(game_id="axm.shooter", build="build-a")
        first_started = threading.Event()
        release_first = threading.Event()
        first_result = []
        calls = 0

        def controlled_join(*args, **kwargs):
            nonlocal calls
            calls += 1
            if calls == 1:
                first_started.set()
                self.assertTrue(release_first.wait(timeout=2.0))
            return Peer(("127.0.0.1", 28741), f"guest-{calls}", f"host-{calls}")

        with patch("axm_p2p.layer.join_host", side_effect=controlled_join):
            worker = threading.Thread(
                target=lambda: first_result.append(layer.join("invite-a", timeout=1.0))
            )
            worker.start()
            self.assertTrue(first_started.wait(timeout=1.0))
            try:
                held = layer.join("invite-b", timeout=1.0)
                self.assertFalse(held.connected)
                self.assertEqual(held.code, "LAYER_OPERATION_IN_PROGRESS")
                self.assertEqual(layer.state, LayerState.JOINING)
                self.assertEqual(calls, 1, "held join must not reach the transport adapter")
            finally:
                release_first.set()
                worker.join(timeout=2.0)

        self.assertFalse(worker.is_alive())
        self.assertEqual(len(first_result), 1)
        self.assertTrue(first_result[0].connected)
        self.assertEqual(layer.state, LayerState.CONNECTED)

    def test_host_is_held_while_join_is_in_flight(self):
        layer = AXMP2PLayer(game_id="axm.shooter", build="build-a")
        first_started = threading.Event()
        release_first = threading.Event()
        first_result = []

        def controlled_join(*args, **kwargs):
            first_started.set()
            self.assertTrue(release_first.wait(timeout=2.0))
            return Peer(("127.0.0.1", 28741), "guest", "host")

        unexpected_host = None
        with patch("axm_p2p.layer.join_host", side_effect=controlled_join):
            worker = threading.Thread(
                target=lambda: first_result.append(layer.join("invite-a", timeout=1.0))
            )
            worker.start()
            self.assertTrue(first_started.wait(timeout=1.0))
            try:
                try:
                    unexpected_host = layer.host(
                        public_host="127.0.0.1",
                        bind_host="127.0.0.1",
                        port=free_udp_port(),
                    )
                except HandshakeError as exc:
                    self.assertEqual(str(exc), "LAYER_OPERATION_IN_PROGRESS")
                else:
                    self.fail("host start crossed an in-flight join")
                self.assertEqual(layer.state, LayerState.JOINING)
            finally:
                if unexpected_host is not None:
                    unexpected_host.close()
                release_first.set()
                worker.join(timeout=2.0)

        self.assertFalse(worker.is_alive())
        self.assertEqual(len(first_result), 1)
        self.assertTrue(first_result[0].connected)

    def test_second_host_is_held_while_first_host_is_starting(self):
        layer = AXMP2PLayer(game_id="axm.shooter", build="build-a")
        first_started = threading.Event()
        release_first = threading.Event()
        first_session = []
        first_error = []

        def controlled_start(_transport):
            first_started.set()
            self.assertTrue(release_first.wait(timeout=2.0))

        def start_first_host():
            try:
                first_session.append(
                    layer.host(
                        public_host="127.0.0.1",
                        bind_host="127.0.0.1",
                        port=free_udp_port(),
                    )
                )
            except BaseException as exc:  # preserved for assertion in the test thread
                first_error.append(exc)

        with patch("axm_p2p.layer.P2PHost.start", autospec=True, side_effect=controlled_start):
            worker = threading.Thread(target=start_first_host)
            worker.start()
            self.assertTrue(first_started.wait(timeout=1.0))
            try:
                with self.assertRaisesRegex(HandshakeError, "^LAYER_OPERATION_IN_PROGRESS$"):
                    layer.host(
                        public_host="127.0.0.1",
                        bind_host="127.0.0.1",
                        port=free_udp_port(),
                    )
            finally:
                release_first.set()
                worker.join(timeout=2.0)

        self.assertFalse(worker.is_alive())
        self.assertEqual(first_error, [])
        self.assertEqual(len(first_session), 1)
        self.assertEqual(layer.state, LayerState.HOSTING)
        first_session[0].close()
        self.assertEqual(layer.state, LayerState.CLOSED)

    def test_unexpected_join_failure_releases_operation_claim(self):
        layer = AXMP2PLayer(game_id="axm.shooter", build="build-a")
        with patch("axm_p2p.layer.join_host", side_effect=RuntimeError("adapter failed")):
            with self.assertRaisesRegex(RuntimeError, "^adapter failed$"):
                layer.join("invite-a", timeout=1.0)
        self.assertEqual(layer.state, LayerState.FAILED)

        peer = Peer(("127.0.0.1", 28741), "guest", "host")
        with patch("axm_p2p.layer.join_host", return_value=peer):
            retry = layer.join("invite-a", timeout=1.0)
        self.assertTrue(retry.connected)
        self.assertEqual(layer.state, LayerState.CONNECTED)

    def test_host_start_failure_releases_operation_claim(self):
        layer = AXMP2PLayer(game_id="axm.shooter", build="build-a")
        with patch(
            "axm_p2p.layer.P2PHost.start",
            autospec=True,
            side_effect=HandshakeError("cannot bind"),
        ):
            with self.assertRaisesRegex(HandshakeError, "^cannot bind$"):
                layer.host(
                    public_host="127.0.0.1",
                    bind_host="127.0.0.1",
                    port=free_udp_port(),
                )
        self.assertEqual(layer.state, LayerState.IDLE)

        with patch("axm_p2p.layer.P2PHost.start", autospec=True):
            retry = layer.host(
                public_host="127.0.0.1",
                bind_host="127.0.0.1",
                port=free_udp_port(),
            )
        self.assertEqual(layer.state, LayerState.HOSTING)
        retry.close()
        self.assertEqual(layer.state, LayerState.CLOSED)
