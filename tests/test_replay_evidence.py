import copy
import json
from pathlib import Path
import stat
import tempfile
import textwrap
import unittest

from axm_p2p.replay_evidence import RECEIPT_SCHEMA, verify_truthgrid_replay


BASE_CAPSULE = {
    "schema": "axm.truthgrid-replay-capsule/v0.01",
    "engineVersion": "truthgrid-engine/v0.01",
    "rulesetVersion": "truthgrid-rules/v0.01",
    "seed": 7,
    "genesisHash": "1111111111111111",
    "actions": [],
    "stateHashes": ["1111111111111111"],
    "finalHash": "1111111111111111",
    "receiptsSha256": "2" * 64,
    "capsuleSha256": "3" * 64,
}


class ReplayEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.capsule = self.root / "capsule.json"
        self.capsule.write_text(json.dumps(BASE_CAPSULE), encoding="utf-8")

    def tearDown(self):
        self.tempdir.cleanup()

    def _provider(self, body: str) -> list[str]:
        path = self.root / "provider.py"
        source = textwrap.dedent(body).lstrip()
        if not source.startswith("#!"):
            source = "#!/usr/bin/env python3\n" + source
        path.write_text(source, encoding="utf-8")
        path.chmod(path.stat().st_mode | stat.S_IXUSR)
        return [str(path)]

    def _pass_provider(self) -> list[str]:
        return self._provider(
            """
            #!/usr/bin/env python3
            import json, sys
            capsule = json.load(open(sys.argv[-1], encoding='utf-8'))
            print(json.dumps({
                'schema': 'axm.truthgrid-replay-verification/v0.01',
                'status': 'PASS',
                'engineVersion': capsule['engineVersion'],
                'rulesetVersion': capsule['rulesetVersion'],
                'capsuleSha256': capsule['capsuleSha256'],
                'actions': len(capsule['actions']),
                'ticks': len(capsule['stateHashes']) - 1,
                'genesisHash': capsule['genesisHash'],
                'finalHash': capsule['finalHash'],
                'optimizedEqualsReference': True,
            }))
            """
        )

    def test_verified_provider_becomes_evidence_only_receipt(self):
        receipt = verify_truthgrid_replay(self.capsule, self._pass_provider())
        self.assertEqual(receipt["schema"], RECEIPT_SCHEMA)
        self.assertEqual(receipt["status"], "VERIFIED_RUNTIME_EVIDENCE")
        self.assertEqual(receipt["evidenceAuthority"], "EVIDENCE_ONLY")
        self.assertTrue(receipt["capsule"]["optimizedEqualsReference"])
        self.assertFalse(any(receipt["authority"].values()))
        self.assertEqual(len(receipt["receiptSha256"]), 64)

    def test_same_evidence_produces_same_receipt(self):
        provider = self._pass_provider()
        first = verify_truthgrid_replay(self.capsule, provider)
        second = verify_truthgrid_replay(self.capsule, provider)
        self.assertEqual(first, second)

    def test_missing_provider_fails_cleanly(self):
        receipt = verify_truthgrid_replay(self.capsule, [str(self.root / "missing")])
        self.assertEqual(receipt["status"], "HOLD")
        self.assertEqual(receipt["code"], "PROVIDER_UNAVAILABLE")
        self.assertFalse(any(receipt["authority"].values()))

    def test_provider_rejection_remains_hold(self):
        provider = self._provider("""
            import sys
            print('{"schema":"axm.truthgrid-replay-error/v0.01","status":"HOLD"}', file=sys.stderr)
            raise SystemExit(1)
        """)
        receipt = verify_truthgrid_replay(self.capsule, provider)
        self.assertEqual(receipt["status"], "HOLD")
        self.assertEqual(receipt["code"], "PROVIDER_REJECTED_CAPSULE")

    def test_mismatched_pass_cannot_bind_to_another_capsule(self):
        provider = self._provider("""
            import json
            print(json.dumps({
                'schema': 'axm.truthgrid-replay-verification/v0.01',
                'status': 'PASS',
                'engineVersion': 'truthgrid-engine/v0.01',
                'rulesetVersion': 'truthgrid-rules/v0.01',
                'capsuleSha256': '0' * 64,
                'actions': 0,
                'ticks': 0,
                'genesisHash': '1111111111111111',
                'finalHash': '1111111111111111',
                'optimizedEqualsReference': True,
            }))
        """)
        receipt = verify_truthgrid_replay(self.capsule, provider)
        self.assertEqual(receipt["status"], "HOLD")
        self.assertEqual(receipt["code"], "PROVIDER_CAPSULE_BINDING_MISMATCH")

    def test_capsule_contract_drift_is_rejected_before_execution(self):
        drifted = copy.deepcopy(BASE_CAPSULE)
        drifted["claimedCheatFree"] = True
        self.capsule.write_text(json.dumps(drifted), encoding="utf-8")
        receipt = verify_truthgrid_replay(self.capsule, self._pass_provider())
        self.assertEqual(receipt["status"], "HOLD")
        self.assertEqual(receipt["code"], "CAPSULE_CONTRACT_DRIFT")


if __name__ == "__main__":
    unittest.main()
