# Replay evidence bridge v0.1

Status: **EXPERIMENTAL / evidence intake only / no sanction or CANON authority**

AXM City Multiplayer already preserves deterministic record/replay evidence as the preferred anti-cheat proof direction, with AI allowed only as an assisting reviewer rather than the proof boundary. TruthGrid now has a concrete portable replay-capsule verifier. This bridge consumes that provider through an explicit local CLI instead of copying its replay engine into this repository.

```text
TruthGrid match ledger
  -> axm.truthgrid-replay-capsule/v0.01
  -> explicit local truthgrid-replay verifier
  -> axm.city-multiplayer.replay-evidence/v0.1
  -> later human / policy review gate
```

## Use

The provider is optional and is never auto-discovered or installed:

```bash
python -m axm_p2p.replay_evidence \
  --provider-cli /reviewed/local/path/to/truthgrid-replay \
  --capsule /local/path/to/replay-capsule.json
```

A successful observation returns `VERIFIED_RUNTIME_EVIDENCE` with `EVIDENCE_ONLY` authority. Missing providers, provider rejection, schema drift, or a verification result that does not bind back to the exact capsule return a deterministic `HOLD` receipt and exit code `2`.

The receipt independently binds:

- exact replay-capsule file bytes by SHA-256;
- the selected provider executable bytes by SHA-256;
- TruthGrid replay-capsule and verification schema identities;
- engine and ruleset identities;
- provider-observed capsule SHA-256;
- action/tick counts, genesis hash, final hash, and optimized/reference equality;
- an outer deterministic AXM City Multiplayer receipt SHA-256.

The adapter invokes exactly the executable supplied by the caller, without a shell. It does not search `$PATH` for a provider, download one, install one, or fall back to a cloud service.

## Cross-repository evidence pin

The first reviewed compatibility target is TruthGrid PR #6 exact head:

`38dd064297870a9e9f092e14c80c3f4b401998e0`

That provider head has its own native replay-capsule CI and clean offline package-consumer evidence. The City Multiplayer workflow deliberately does **not** request a broader credential in order to clone the sibling private repository: a normal repository-scoped `GITHUB_TOKEN` cannot read another private repo. Provider-to-consumer execution therefore remains an explicit local/review integration gate using the reviewed provider path, rather than silently widening CI credentials.

The compatibility pin is evidence lineage, not a runtime dependency or promotion decision. If the provider contract or reviewed head changes, the bridge version/pin must be re-evaluated rather than silently accepting drift.

## Authority boundary

A verified replay receipt does **not** mean a player cheated or did not cheat. It does not prove who authored the capsule, that submitted inputs were honest, that the remote match used the declared engine, or that a participant identity is trustworthy.

The v0.1 receipt therefore hard-codes all of these authorities to `false`:

- automatic judgement;
- sanction;
- matchmaking routing/quarantine;
- merge;
- CANON.

Any later integrity-routing or anti-cheat system must combine game-specific evidence with an explicit review/policy gate. AI may help inspect evidence but is not allowed to turn this receipt into a verdict by itself.

## Security / local boundary

The external provider process is **not sandboxed** by this adapter. Running it is an explicit local execution decision. The reviewed pin identifies one compatibility target; other provider binaries require their own provenance/review.

No relay, account, cloud, paid service, AI service, or always-on AXM infrastructure is added by this bridge.
