from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry" / "capabilities.jsonl"
MARKER = ROOT / ".axm" / "discovery-public.json"
GENERATOR = ROOT / "tools" / "generate_public_capabilities.py"
EXPECTED_IDS = {
    "axm-p2p-direct-invite-v1",
    "axm-p2p-direct-join-v1",
    "axm-p2p-game-layer-v1",
}


class PublicCapabilityRegistryTests(unittest.TestCase):
    def test_generator_matches_committed_registry(self):
        result = subprocess.run(
            [sys.executable, str(GENERATOR), "--check"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_registry_is_bounded_source_backed_discovery(self):
        rows = [
            json.loads(line)
            for line in REGISTRY.read_text("utf-8").splitlines()
            if line.strip()
        ]
        self.assertEqual({row["id"] for row in rows}, EXPECTED_IDS)
        self.assertEqual([row["id"] for row in rows], sorted(EXPECTED_IDS))
        for row in rows:
            self.assertEqual(row["schema"], "axm.public-capability/v1")
            self.assertEqual(row["providers"], ["axm-city-multiplayer"])
            self.assertEqual(row["consumers"], [])
            self.assertEqual(row["status"], "IMPLEMENTED_REFERENCE")
            self.assertFalse(row["truth"]["declaration_is_runtime_proof"])
            self.assertFalse(row["truth"]["grants_authority"])
            self.assertTrue(row["truth"]["generated_from_repo_state"])
            self.assertTrue(row["source_evidence"])

    def test_public_discovery_requires_explicit_repository_identity(self):
        marker = json.loads(MARKER.read_text("utf-8"))
        self.assertEqual(marker["schema"], "axm.discovery-public/v1")
        self.assertEqual(marker["repo"], "mike-axiom-mir/axm-city-multiplayer")
        self.assertIs(marker["public"], True)


if __name__ == "__main__":
    unittest.main()
