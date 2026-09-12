import base64
import hashlib
import json
import unittest

from axm_p2p.invite import PREFIX, InviteError, create_invite, decode_invite


def _payload(**overrides):
    payload = {
        "v": 1,
        "g": "axm.game",
        "b": "build-1",
        "h": "127.0.0.1",
        "p": 29991,
        "s": "session-id",
        "k": "session-key",
        "e": 130,
    }
    payload.update(overrides)
    return payload


def _token_from_body(body: bytes) -> str:
    checksum = hashlib.sha256(body).digest()[:10]
    encoded = base64.urlsafe_b64encode(body + checksum).decode("ascii").rstrip("=")
    return PREFIX + encoded


def _token(payload: dict) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return _token_from_body(body)


class InviteContractTests(unittest.TestCase):
    def test_generated_invite_remains_canonical_and_decodable(self):
        token = create_invite(
            game_id="axm.game",
            build="build-1",
            host="127.0.0.1",
            port=29991,
            lifetime_seconds=30,
            now=100,
        )
        invite = decode_invite(token, now=101)
        self.assertEqual(invite.game_id, "axm.game")
        self.assertEqual(invite.build, "build-1")
        self.assertEqual(invite.port, 29991)
        self.assertEqual(invite.expires_at, 130)

    def test_decoder_rejects_fields_that_would_require_type_coercion(self):
        invalid = (
            {"g": 7},
            {"b": False},
            {"h": ["127.0.0.1"]},
            {"p": True},
            {"s": 22},
            {"k": ""},
            {"e": "130"},
            {"v": True},
        )
        for overrides in invalid:
            with self.subTest(overrides=overrides):
                with self.assertRaises(InviteError):
                    decode_invite(_token(_payload(**overrides)), now=101)

    def test_decoder_rejects_valid_checksum_over_noncanonical_json(self):
        body = json.dumps(_payload(), sort_keys=False, indent=2).encode("utf-8")
        token = _token_from_body(body)
        with self.assertRaisesRegex(InviteError, "canonical JSON"):
            decode_invite(token, now=101)

    def test_decoder_rejects_noncanonical_base64url_spelling(self):
        token = _token(_payload())
        with self.assertRaisesRegex(InviteError, "canonical base64url"):
            decode_invite(token + "=", now=101)

    def test_create_rejects_boolean_integer_fields(self):
        with self.assertRaises(InviteError):
            create_invite(game_id="g", build="b", host="127.0.0.1", port=True)
        with self.assertRaises(InviteError):
            create_invite(game_id="g", build="b", host="127.0.0.1", port=29991, lifetime_seconds=True)

    def test_create_rejects_non_string_identity_fields(self):
        with self.assertRaises(InviteError):
            create_invite(game_id=7, build="b", host="127.0.0.1", port=29991)
        with self.assertRaises(InviteError):
            create_invite(game_id="g", build="", host="127.0.0.1", port=29991)


if __name__ == "__main__":
    unittest.main()
