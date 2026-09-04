# AXM Multiplayer Transport Convergence Seam

Status: **ARCHITECTURE CONVERGENCE / NOT MERGED / NOT CANON**

Date recognized: 2026-09-05

This document records an unexpected convergence between two independently developed multiplayer lanes in this repository:

- **PR #2 — City Mesh foundation**: fixed opt-in radio/network infrastructure, local-first simulation, minimal shared state, truth/integrity gates.
- **PR #3 — Direct P2P core + Peer Fabric**: measured direct-invite P2P reference core plus decentralized discovery/bootstrap/resilience research.

The two lanes were intentionally kept separate while they were being developed. They now appear to fit as different transport scales beneath the same multiplayer truth/state layer.

Do not copy or replace PR #3's P2P architecture inside PR #2. PR #3 remains the source lane for the P2P implementation and Peer Fabric research.

## The convergence

The game should not need a different simulation/truth model merely because packets travel through a different physical path.

```text
                 AXM MULTIPLAYER TRUTH LAYER

        ordered events / deltas / hashes / receipts
        checkpoints / replay / repair / integrity
                         |
          +--------------+--------------+
          |              |              |
          v              v              v
    HOUSEHOLD LAN    CITY FABRIC     GLOBAL P2P
    device/device    fixed radios     Internet peers
    local network    multi-hop        direct paths
```

These are not three separate multiplayer products. They are candidate **transport domains** for one reusable state/truth protocol.

## Scale 1 — Household / local LAN

Root:

```text
player device <---- local network ----> player device
```

Properties:

- lowest infrastructure dependency;
- private household rules remain private;
- no city-integrity enforcement is required inside a user's own LAN;
- can remain usable even if city human-match trust is unavailable;
- suitable baseline for deterministic protocol testing.

## Scale 2 — City fabric

Root:

```text
player
  |
local access
  |
fixed AXM node
  )))))) fixed radio / routed mesh ((((((
fixed AXM node
  |
local access
  |
player
```

Properties preserved from PR #2:

- participant phones/devices are clients, not opportunistic mesh relays;
- serious fixed nodes form the backbone;
- opt-in placements extend coverage;
- candidate starter test is a lawful point-to-point fixed link before attempting a full city;
- city routing/integrity may use access-boundary trust state;
- exact cost/range/capacity remains measurement-gated.

The city fabric may eventually behave to the game like another reachable packet path. It should not force the game to stream rendered worlds or invent a separate simulation model.

## Scale 3 — Global Peer Fabric

PR #3 is the source of truth for this lane.

Preserved direction:

```text
host -> copy invite -> send anywhere -> guest joins -> direct connection
```

and later:

```text
friend P2P
    -> private social-group P2P
    -> public per-game P2P
    -> global AXM P2P discovery fabric
```

Default economic boundary:

- player-owned direct P2P for ordinary free/local games;
- no AXM-funded continuing gameplay relay by default;
- a tiny endpoint observer / ignition peer may help bootstrap or introduce peers without becoming the gameplay path;
- direct-path failure is allowed to fail honestly;
- dedicated servers remain title-specific exceptions rather than mandatory platform infrastructure.

## Common protocol ambition

The convergence hypothesis is:

> A multiplayer game should express the smallest authoritative facts needed for peers to agree, while the transport layer decides how those facts travel.

Candidate transport-independent game facts:

```text
protocol / game / build identity
session identity
participant identity
simulation tick / sequence
ordered input or event
authoritative state delta
state hash
checkpoint acknowledgement
repair/correction
integrity receipt
```

The exact schema is not CANON yet.

The game adapter may remain responsible for what is reconstructible locally versus what must cross the network.

## Why this matters

Without the convergence:

```text
LAN game code
city game code
global P2P game code
```

risk becoming three implementations.

With a transport seam:

```text
                   GAME ADAPTER
                       |
               AXM TRUTH/STATE PROTOCOL
                       |
                 TRANSPORT SEAM
             /          |          \
           LAN         CITY         P2P
```

A game can potentially keep one deterministic multiplayer core and choose the best available transport domain.

This is the architectural multiplier: improvements to replay, checkpointing, state compression, integrity, migration, prediction, or repair can potentially benefit every transport scale instead of being rebuilt per network type.

## Transport selection must remain explicit

Convergence must not become silent scope widening.

A player should still know whether they are entering:

- private LAN,
- city/local shared matchmaking,
- friend P2P,
- private social-group P2P,
- public per-game P2P,
- global AXM discovery.

Discovery scope, trust scope, integrity policy and privacy consequences differ by domain even if the game-state protocol is shared.

## Integrity boundaries

The evidence machinery can be shared:

```text
ordered/signed facts
      -> retained match record
      -> deterministic replay
      -> objective rule/state verification
      -> optional AI-assisted inspection
```

But enforcement scope remains transport-specific.

Examples:

- private LAN: user-owned environment; AXM city quarantine does not police it;
- city fabric: verified manipulation may change the relevant city access/trust routing state;
- global P2P: use peer/session/identity trust and evidence appropriate to direct Internet peers; do not automatically infer a city access-point consequence.

AI may assist analysis. AI alone is never the truth boundary.

## Identity/account convergence

All three scales can share the same local-first identity direction:

- optional account/profile for stats, achievements, friends and continuity;
- local device remains primary owner of personal game state where practical;
- portable cryptographic identity can support continuity;
- basic access should not become dependent on AXM owning a central identity database merely because profiles are useful.

Transport should not redefine ownership of identity.

## Browser convergence

Browser accessibility can be treated as another endpoint/runtime surface rather than a new multiplayer authority.

Where browser P2P works, PR #3's Peer Fabric research can provide direct Internet paths. Where a browser/device is physically on the city fabric, ordinary IP connectivity through that fabric may carry the same game protocol.

Browser support therefore belongs above the transport seam, not as a reason to centralize the game.

## Failure is allowed to remain honest

The common system must not pretend every transport has equal guarantees.

Examples:

```text
LAN unavailable
-> no LAN session

city path unavailable
-> no city path / try another reachable node if policy permits

P2P NAT traversal fails
-> direct global P2P unavailable unless a separate allowed path exists
```

Do not silently add paid relays, hidden cloud dependencies or user-device mesh relay behavior to make an availability metric look better.

## Research gates created by the convergence

Before claiming one reusable multiplayer substrate, measure at least:

1. **Transport abstraction gate** — same game-state test passes over loopback/LAN, simulated city-link conditions and P2P reference transport without changing game semantics.
2. **Packet-class gate** — classify which facts require reliable ordered delivery, unreliable/latest delivery, acknowledgement, replay retention or checkpoint repair.
3. **Determinism gate** — peers derive equivalent canonical state from the same accepted event sequence.
4. **Transport-switch gate** — determine whether a live session can migrate paths without changing authoritative game history; do not assume this is safe.
5. **Latency/jitter gate** — measure gameplay behavior under each transport class rather than assuming local-radio and Internet paths are equivalent.
6. **Bandwidth gate** — measure authoritative bytes/player/second and repair bursts for real game adapters.
7. **Integrity-scope gate** — verify that LAN, city and global P2P consequences remain correctly bounded to their domains.
8. **Identity portability gate** — same local-first player identity can participate across transports without central ownership becoming mandatory.
9. **Discovery-scope gate** — entering a wider discovery layer never silently widens trust, membership or endpoint exposure.
10. **No-hidden-relay gate** — prove no user device or AXM-funded service becomes continuing gameplay transit unless explicitly selected by that mode.

## Merge discipline

This document is a seam map, not permission to collapse the two active PRs immediately.

Current safe sequence:

```text
PR #2 preserves city physical-network research
PR #3 preserves P2P implementation/research
        |
        v
future integration lane starts from both accepted histories
        |
        v
transport-independent protocol/adaptor test
```

When the lanes are reconciled, preserve both truth histories and resolve the shared README deliberately. Do not choose one README by overwrite.

## Current truth statement

**MEASURED:** PR #3 reports an 8/8 passing local direct-invite/reference P2P suite.

**RESEARCHED:** fixed legal long-range Wi-Fi hardware can form point-to-point packet links suitable for a first city-fabric experiment.

**HYPOTHESIS:** LAN, fixed city radio/network transport and global direct P2P can share one deterministic AXM game-state/truth protocol with transport-specific discovery, trust and integrity policy.

**NOT YET PROVEN:** seamless live transport migration, city field range/capacity, Internet NAT success rate, one protocol's suitability for every game genre, or production-scale cross-transport matchmaking.

No merge or CANON action is performed by this document.
