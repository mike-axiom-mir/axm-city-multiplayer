import unittest
from axm_p2p.invite import decode_invite
from axm_p2p.invite_desk import create_share_packet, inspect_share_packet, public_invite_view


class InviteDeskTest(unittest.TestCase):
    def test_create_packet_is_shareable_and_hides_session_key_from_metadata(self):
        out = create_share_packet({
            "game": "axm.shooter",
            "build": "test-7",
            "host": "198.51.100.7",
            "port": 28741,
            "lifetimeSeconds": 900,
        }, now=1_000)
        self.assertEqual(out["status"], "READY_TO_SHARE")
        self.assertTrue(out["token"].startswith("AXMP2P1."))
        self.assertNotIn("session_key", out["invite"])
        self.assertNotIn("sessionKey", out["invite"])
        self.assertEqual(out["invite"]["secondsRemaining"], 900)
        decoded = decode_invite(out["token"], now=1_000)
        self.assertEqual(decoded.game_id, "axm.shooter")

    def test_inspection_reports_transport_truth_without_connection_claim(self):
        made = create_share_packet({"game":"g","build":"b","host":"127.0.0.1","port":9999,"lifetimeSeconds":60}, now=2_000)
        out = inspect_share_packet({"token": made["token"]}, now=2_010)
        self.assertEqual(out["status"], "VALID")
        self.assertFalse(out["browserCanConnect"])
        self.assertEqual(out["invite"]["transport"], "DIRECT_UDP_REFERENCE")
        self.assertFalse(out["invite"]["relay"])
        self.assertEqual(out["invite"]["secondsRemaining"], 50)

    def test_invalid_and_expired_invites_hold(self):
        self.assertEqual(inspect_share_packet({"token":"not-an-invite"}, now=1)["status"], "HELD")
        made = create_share_packet({"game":"g","build":"b","host":"127.0.0.1","port":9999,"lifetimeSeconds":1}, now=10)
        held = inspect_share_packet({"token": made["token"]}, now=12)
        self.assertEqual(held["status"], "HELD")
        self.assertIn("expired", held["detail"])

    def test_public_projection_never_leaks_key(self):
        made = create_share_packet({"game":"g","build":"b","host":"127.0.0.1","port":9999,"lifetimeSeconds":60}, now=100)
        invite = decode_invite(made["token"], now=100)
        view = public_invite_view(invite, now=100)
        self.assertNotIn(invite.session_key, repr(view))


if __name__ == "__main__":
    unittest.main()
