#!/usr/bin/env python3
"""Generate the public AXM capability registry from the shipped P2P surface."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "registry" / "capabilities.jsonl"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SCHEMA = "axm.public-capability/v1"
PROVIDER = "axm-city-multiplayer"
STATUS = "IMPLEMENTED_REFERENCE"
EXPECTED_PREFIX = "AXMP2P1."


def _require_callable(module, name: str):
    value = getattr(module, name, None)
    if not callable(value):
        raise RuntimeError(f"public capability source is missing callable {name!r}")
    return value


def _truth() -> dict[str, object]:
    return {
        "contract_probe": "python -m unittest discover -s tests -v",
        "declaration_is_runtime_proof": False,
        "generated_from_repo_state": True,
        "generator_probe": "python tools/generate_public_capabilities.py --check",
        "grants_authority": False,
    }


def _row(
    capability_id: str,
    *,
    symbols: list[str],
    source_evidence: list[str],
    interface_kind: str,
    extra_interface: dict[str, object] | None = None,
) -> dict[str, object]:
    interface: dict[str, object] = {
        "kind": interface_kind,
        "module": "axm_p2p",
        "symbols": symbols,
    }
    if extra_interface:
        interface.update(extra_interface)
    return {
        "consumers": [],
        "id": capability_id,
        "interface": interface,
        "provider_statuses": [{"id": PROVIDER, "status": STATUS}],
        "providers": [PROVIDER],
        "schema": SCHEMA,
        "source_evidence": source_evidence,
        "status": STATUS,
        "truth": _truth(),
    }


def build_registry() -> list[dict[str, object]]:
    import axm_p2p
    from axm_p2p import invite

    exported = set(getattr(axm_p2p, "__all__", ()))
    for name in ("AXMP2PLayer", "create_invite", "decode_invite", "join_host"):
        if name not in exported:
            raise RuntimeError(f"public axm_p2p.__all__ no longer exports {name!r}")
        _require_callable(axm_p2p, name)

    if invite.PREFIX != EXPECTED_PREFIX:
        raise RuntimeError(
            f"invite prefix changed from {EXPECTED_PREFIX!r} to {invite.PREFIX!r}; "
            "version the discovery capability instead of silently rewriting it"
        )

    layer = axm_p2p.AXMP2PLayer
    for method in ("host", "join"):
        _require_callable(layer, method)

    rows = [
        _row(
            "axm-p2p-direct-invite-v1",
            symbols=["create_invite", "decode_invite"],
            source_evidence=[
                "AXM_P2P_CONTRACT.md",
                "axm_p2p/__init__.py",
                "axm_p2p/invite.py",
                "tests/test_p2p.py",
            ],
            interface_kind="python+token",
            extra_interface={"token_prefix": EXPECTED_PREFIX},
        ),
        _row(
            "axm-p2p-direct-join-v1",
            symbols=["join_host", "P2PHost"],
            source_evidence=[
                "AXM_P2P_CONTRACT.md",
                "axm_p2p/__init__.py",
                "axm_p2p/udp.py",
                "tests/test_p2p.py",
            ],
            interface_kind="python",
        ),
        _row(
            "axm-p2p-game-layer-v1",
            symbols=["AXMP2PLayer", "HostSession", "JoinResult", "LayerState"],
            source_evidence=[
                "AXM_P2P_CONTRACT.md",
                "axm_p2p/__init__.py",
                "axm_p2p/layer.py",
                "tests/test_layer.py",
            ],
            interface_kind="python",
        ),
    ]
    rows.sort(key=lambda item: str(item["id"]))
    return rows


def render(rows: list[dict[str, object]]) -> str:
    return "".join(
        json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        for row in rows
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if the committed registry differs from the current public P2P surface",
    )
    args = parser.parse_args(argv)

    text = render(build_registry())
    if args.check:
        actual = OUTPUT.read_text("utf-8") if OUTPUT.is_file() else None
        if actual != text:
            print(
                "public capability registry is stale; run "
                "`python tools/generate_public_capabilities.py`",
                file=sys.stderr,
            )
            return 1
        print("public capability registry: PASS (3 records)")
        return 0

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {OUTPUT.relative_to(ROOT)} (3 records)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
