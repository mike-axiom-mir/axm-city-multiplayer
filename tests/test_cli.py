import contextlib
import io
import json
import unittest
from unittest import mock

from axm_p2p.cli import main
from axm_p2p.invite import create_invite


class CliTests(unittest.TestCase):
    def test_show_json_is_stable_and_does_not_emit_session_secret(self):
        with mock.patch("axm_p2p.invite.time.time", return_value=100):
            token = create_invite(
                game_id="axm.consumer",
                build="build-7",
                host="127.0.0.1",
                port=28741,
                lifetime_seconds=30,
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                result = main(["show", token, "--json"])

        payload = json.loads(stdout.getvalue())
        self.assertEqual(result, 0)
        self.assertEqual(payload["protocol"], 1)
        self.assertEqual(payload["game_id"], "axm.consumer")
        self.assertEqual(payload["build"], "build-7")
        self.assertEqual(payload["host"], "127.0.0.1")
        self.assertEqual(payload["port"], 28741)
        self.assertEqual(payload["expires_at"], 130)
        self.assertNotIn("session_key", payload)
        self.assertNotIn("k", payload)


if __name__ == "__main__":
    unittest.main()
