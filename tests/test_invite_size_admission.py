import unittest
from unittest.mock import patch

from axm_p2p.invite import InviteError, PREFIX, create_invite, decode_invite


MAX_REFERENCE_INVITE_CHARS = 4096


class InviteSizeAdmissionTests(unittest.TestCase):
    def test_decoder_rejects_oversized_token_before_base64_decode(self):
        oversized = PREFIX + ("A" * (MAX_REFERENCE_INVITE_CHARS - len(PREFIX) + 1))

        with patch(
            "axm_p2p.invite.base64.b64decode",
            side_effect=AssertionError("oversized invite reached base64 decoding"),
        ) as decoder:
            with self.assertRaisesRegex(InviteError, "invite exceeds maximum size"):
                decode_invite(oversized, now=100)

        decoder.assert_not_called()

    def test_creator_refuses_to_emit_invite_above_reference_limit(self):
        with self.assertRaisesRegex(InviteError, "invite exceeds maximum size"):
            create_invite(
                game_id="g" * 4000,
                build="build-001",
                host="127.0.0.1",
                port=28741,
                now=100,
            )

    def test_large_but_bounded_invite_still_round_trips(self):
        game_id = "g" * 256
        build = "b" * 256
        host = "h" * 253

        token = create_invite(
            game_id=game_id,
            build=build,
            host=host,
            port=28741,
            now=100,
        )

        self.assertLessEqual(len(token), MAX_REFERENCE_INVITE_CHARS)
        decoded = decode_invite(token, now=100)
        self.assertEqual(decoded.game_id, game_id)
        self.assertEqual(decoded.build, build)
        self.assertEqual(decoded.host, host)


if __name__ == "__main__":
    unittest.main()
