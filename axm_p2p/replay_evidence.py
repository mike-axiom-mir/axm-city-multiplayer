"""Bounded external replay-evidence intake for AXM City Multiplayer.

This module does not implement or copy a game replay engine. It invokes an explicitly
selected local TruthGrid verifier and turns its PASS result into a deterministic,
non-authoritative evidence receipt.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Sequence

RECEIPT_SCHEMA = "axm.city-multiplayer.replay-evidence/v0.1"
TRUTHGRID_CAPSULE_SCHEMA = "axm.truthgrid-replay-capsule/v0.01"
TRUTHGRID_VERIFICATION_SCHEMA = "axm.truthgrid-replay-verification/v0.01"
TRUTHGRID_ENGINE_VERSION = "truthgrid-engine/v0.01"
TRUTHGRID_RULESET_VERSION = "truthgrid-rules/v0.01"

_CAPSULE_KEYS = {
    "actions",
    "capsuleSha256",
    "engineVersion",
    "finalHash",
    "genesisHash",
    "receiptsSha256",
    "rulesetVersion",
    "schema",
    "seed",
    "stateHashes",
}
_VERIFICATION_KEYS = {
    "actions",
    "capsuleSha256",
    "engineVersion",
    "finalHash",
    "genesisHash",
    "optimizedEqualsReference",
    "rulesetVersion",
    "schema",
    "status",
    "ticks",
}
_AUTHORITY = {
    "automaticJudgement": False,
    "canon": False,
    "matchmakingRouting": False,
    "merge": False,
    "sanction": False,
}
_LIMITS = [
    "provider execution is explicit and local; this adapter does not discover or install it",
    "verification is specific to the declared TruthGrid engine and ruleset",
    "replay determinism does not prove player-input honesty, authorship, identity, or a cheat-free match",
    "the external provider process is not sandboxed by this adapter",
]


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _seal(receipt: dict[str, Any]) -> dict[str, Any]:
    sealed = dict(receipt)
    sealed["receiptSha256"] = _sha256_bytes(_canonical_bytes(receipt))
    return sealed


def _hold(code: str, *, capsule_file_sha256: str | None = None) -> dict[str, Any]:
    receipt: dict[str, Any] = {
        "schema": RECEIPT_SCHEMA,
        "status": "HOLD",
        "code": code,
        "evidenceAuthority": "NONE",
        "authority": dict(_AUTHORITY),
        "limits": list(_LIMITS),
    }
    if capsule_file_sha256 is not None:
        receipt["capsuleFileSha256"] = capsule_file_sha256
    return _seal(receipt)


def _read_capsule(path: Path) -> tuple[dict[str, Any] | None, str | None, str | None]:
    try:
        raw = path.read_bytes()
    except OSError:
        return None, None, "CAPSULE_UNAVAILABLE"
    file_sha = _sha256_bytes(raw)
    try:
        capsule = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None, file_sha, "CAPSULE_INVALID_JSON"
    if not isinstance(capsule, dict):
        return None, file_sha, "CAPSULE_NOT_OBJECT"
    if set(capsule) != _CAPSULE_KEYS:
        return None, file_sha, "CAPSULE_CONTRACT_DRIFT"
    if capsule.get("schema") != TRUTHGRID_CAPSULE_SCHEMA:
        return None, file_sha, "CAPSULE_SCHEMA_MISMATCH"
    if capsule.get("engineVersion") != TRUTHGRID_ENGINE_VERSION:
        return None, file_sha, "ENGINE_VERSION_MISMATCH"
    if capsule.get("rulesetVersion") != TRUTHGRID_RULESET_VERSION:
        return None, file_sha, "RULESET_VERSION_MISMATCH"
    if not isinstance(capsule.get("actions"), list):
        return None, file_sha, "CAPSULE_ACTIONS_INVALID"
    hashes = capsule.get("stateHashes")
    if not isinstance(hashes, list) or not hashes:
        return None, file_sha, "CAPSULE_STATE_HASHES_INVALID"
    return capsule, file_sha, None


def _provider_executable_sha256(command: Sequence[str]) -> str | None:
    if not command:
        return None
    executable = Path(command[0])
    if not executable.exists() or not executable.is_file():
        return None
    try:
        return _sha256_bytes(executable.resolve().read_bytes())
    except OSError:
        return None


def verify_truthgrid_replay(
    capsule_path: str | os.PathLike[str],
    provider_command: Sequence[str],
    *,
    timeout_seconds: float = 15.0,
) -> dict[str, Any]:
    """Verify one capsule through an explicit local TruthGrid provider.

    The returned receipt never grants sanction, matchmaking, merge, or CANON authority.
    A rejected/missing/drifted provider produces a deterministic HOLD receipt.
    """

    capsule_file = Path(capsule_path)
    capsule, file_sha, capsule_error = _read_capsule(capsule_file)
    if capsule_error is not None:
        return _hold(capsule_error, capsule_file_sha256=file_sha)

    if len(provider_command) != 1 or not isinstance(provider_command[0], str):
        return _hold("PROVIDER_COMMAND_INVALID", capsule_file_sha256=file_sha)

    executable_sha = _provider_executable_sha256(provider_command)
    if executable_sha is None:
        return _hold("PROVIDER_UNAVAILABLE", capsule_file_sha256=file_sha)

    command = [*provider_command, "verify", "--capsule", str(capsule_file.resolve())]
    try:
        completed = subprocess.run(
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="strict",
            timeout=timeout_seconds,
            check=False,
            shell=False,
        )
    except (OSError, subprocess.SubprocessError, UnicodeError):
        return _hold("PROVIDER_EXECUTION_FAILED", capsule_file_sha256=file_sha)

    if completed.returncode != 0:
        return _hold("PROVIDER_REJECTED_CAPSULE", capsule_file_sha256=file_sha)

    try:
        verification = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return _hold("PROVIDER_OUTPUT_INVALID_JSON", capsule_file_sha256=file_sha)

    if not isinstance(verification, dict) or set(verification) != _VERIFICATION_KEYS:
        return _hold("PROVIDER_VERIFICATION_CONTRACT_DRIFT", capsule_file_sha256=file_sha)
    if verification.get("schema") != TRUTHGRID_VERIFICATION_SCHEMA:
        return _hold("PROVIDER_VERIFICATION_SCHEMA_MISMATCH", capsule_file_sha256=file_sha)
    if verification.get("status") != "PASS" or verification.get("optimizedEqualsReference") is not True:
        return _hold("PROVIDER_DID_NOT_PROVE_REPLAY", capsule_file_sha256=file_sha)

    expected_pairs = {
        "engineVersion": capsule["engineVersion"],
        "rulesetVersion": capsule["rulesetVersion"],
        "capsuleSha256": capsule["capsuleSha256"],
        "genesisHash": capsule["genesisHash"],
        "finalHash": capsule["finalHash"],
        "actions": len(capsule["actions"]),
        "ticks": len(capsule["stateHashes"]) - 1,
    }
    for field, expected in expected_pairs.items():
        if verification.get(field) != expected:
            return _hold("PROVIDER_CAPSULE_BINDING_MISMATCH", capsule_file_sha256=file_sha)

    receipt = {
        "schema": RECEIPT_SCHEMA,
        "status": "VERIFIED_RUNTIME_EVIDENCE",
        "code": "TRUTHGRID_REPLAY_VERIFIED",
        "evidenceAuthority": "EVIDENCE_ONLY",
        "provider": {
            "capability": TRUTHGRID_CAPSULE_SCHEMA,
            "verificationSchema": TRUTHGRID_VERIFICATION_SCHEMA,
            "engineVersion": verification["engineVersion"],
            "rulesetVersion": verification["rulesetVersion"],
            "executableSha256": executable_sha,
        },
        "capsule": {
            "fileSha256": file_sha,
            "capsuleSha256": verification["capsuleSha256"],
            "actions": verification["actions"],
            "ticks": verification["ticks"],
            "genesisHash": verification["genesisHash"],
            "finalHash": verification["finalHash"],
            "optimizedEqualsReference": True,
        },
        "authority": dict(_AUTHORITY),
        "limits": list(_LIMITS),
    }
    return _seal(receipt)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m axm_p2p.replay_evidence",
        description="Convert an explicit local TruthGrid replay verification into bounded multiplayer evidence.",
    )
    parser.add_argument("--capsule", required=True, help="Path to a TruthGrid replay capsule JSON file")
    parser.add_argument(
        "--provider-cli",
        required=True,
        help="Exact local truthgrid-replay executable to invoke; no provider is auto-discovered",
    )
    parser.add_argument("--timeout", type=float, default=15.0, help="Provider timeout in seconds")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    receipt = verify_truthgrid_replay(
        args.capsule,
        [args.provider_cli],
        timeout_seconds=args.timeout,
    )
    sys.stdout.write(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return 0 if receipt["status"] == "VERIFIED_RUNTIME_EVIDENCE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
