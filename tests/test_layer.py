import socket
import unittest

from axm_p2p import AXMP2PLayer, LayerState


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

        self.assertEqual(host.state, LayerState.CLOSED)

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
