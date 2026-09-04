# AXM Multiplayer Master Index

Status: **navigation / coverage index — not CANON and not a merge action**

Date: 2026-09-05

Purpose: one front door for the multiplayer work that has been spread across several chats and PR lanes. This file does not collapse distinct experiments into one implementation. It tells a future AXM instance where each decision lives, what is measured, and what remains research.

## Root multiplayer direction

For free/local AXM games, multiplayer should remain player-owned by default.

```text
LAN substrate
    |
    v
Friend P2P
    |
    v
Private Social Group P2P
    |
    v
Public Per-Game P2P
    |
    v
Global AXM P2P Fabric
```

A wider layer expands **discovery**, not automatic trust. Actual game traffic remains direct P2P when a direct path exists. A failed direct path may fail honestly instead of silently consuming AXM-paid relay/server capacity.

## Current repository lanes

### PR #2 — City Mesh foundation

Scope: fixed opt-in city networking infrastructure and deterministic multiplayer truth/integrity research.

Preserves:

- dedicated fixed city nodes; phones/participant devices are clients, not mesh relays;
- city-cell / multi-hop research;
- local simulation/rendering wherever deterministic agreement permits;
- minimal event/state/hash/checkpoint synchronization;
- local-first account direction with guest/basic-play independence;
- household LAN play independent of city human matchmaking;
- deterministic record/replay anti-cheat evidence;
- AI-assisted review, never AI as sole proof boundary;
- bounded integrity routing / quarantine direction rather than ownership-style exclusion;
- legal/RF/cost/capacity truth gates before city-scale claims.

Do not silently merge this lane into Peer Fabric. It is a separate physical-network experiment that may later interoperate.

### PR #3 — Direct P2P core + Peer Fabric research

Measured base:

- `AXMP2P1` copy/paste invite;
- game/build compatibility;
- expiry/corruption handling;
- authenticated reference UDP admission handshake;
- stable game-facing `AXMP2PLayer` seam;
- previously reported local reference suite: **8/8 passing**.

Research extension:

- remembered cryptographic peer bonds;
- Router Helper;
- peer-assisted endpoint observation;
- four online discovery scopes;
- private/federated/public groups;
- decentralized public discovery;
- signed expiring presence tickets;
- decentralized matchmaking proposals;
- ignition peers / optional AI gamer wrapper;
- measured host/coordinator selection;
- host-role fairness / rollback;
- checkpointed coordinator migration;
- old-game resurrection;
- eventual reusable SDK direction.

## Four player-chosen online discovery scopes

LAN is the substrate and is not counted as an Internet/social discovery layer.

1. **Friend P2P** — explicit invite or remembered consent-based peer.
2. **Private Social Group P2P** — bounded club/clan/family/game-night discovery; optional explicit federation.
3. **Public Per-Game P2P** — strangers may discover compatible players inside one game namespace and form decentralized matches.
4. **Global AXM P2P Fabric** — participating games share bootstrap/discovery infrastructure while matchmaking remains separated by game/protocol/ruleset.

The implementation MUST NOT silently widen the selected scope.

## Coverage map

| Decision / subsystem | Primary source |
| --- | --- |
| no paid AXM gameplay relay by default | `AXM_P2P_CONTRACT.md` |
| direct copy/paste invite | `README.md`, `AXM_P2P_CONTRACT.md` |
| direct-connect protocol research | `RESEARCH_P2P_ONLY.md` |
| remembered peer consent/bonds | `PEER_FABRIC_ARCHITECTURE.md`, `PEER_FABRIC_RESEARCH_GATES.md` |
| beginner-safe Router Helper | `PEER_FABRIC_ARCHITECTURE.md`, `PEER_FABRIC_RESEARCH_GATES.md` |
| peer endpoint observer / STUN-like helper | `RESEARCH_P2P_ONLY.md`, `PEER_FABRIC_RESEARCH_GATES.md` |
| private/federated/public groups | `PEER_FABRIC_ARCHITECTURE.md` |
| four discovery scopes + Global AXM | `PEER_FABRIC_DISCOVERY_SCOPES.md` |
| public distributed discovery | `PEER_FABRIC_ARCHITECTURE.md` |
| no blockchain/global-ledger requirement | `RESEARCH_P2P_ONLY.md`, `PEER_FABRIC_ARCHITECTURE.md` |
| decentralized Quick Match proposals | `PEER_FABRIC_ARCHITECTURE.md`, `PEER_FABRIC_RESEARCH_GATES.md` |
| ignition peer / AI gamer bootstrap | `PEER_FABRIC_ARCHITECTURE.md` |
| bounded discovery graph, not all-to-all | `PEER_FABRIC_ARCHITECTURE.md`, `PEER_FABRIC_DISCOVERY_SCOPES.md` |
| host selection by measured network quality | `PEER_FABRIC_RESEARCH_GATES.md` |
| host role must not own privileged game time | `PEER_FABRIC_ARCHITECTURE.md`, `PEER_FABRIC_RESEARCH_GATES.md` |
| deterministic checkpoint host migration | `PEER_FABRIC_ARCHITECTURE.md`, `PEER_FABRIC_RESEARCH_GATES.md` |
| low-bandwidth / adversity / reconnect discipline | `PEER_FABRIC_OPERATING_PRINCIPLES.md`, `PEER_FABRIC_RESILIENCE_GATES.md` |
| serverless default / server-capable exception boundary | `PEER_FABRIC_OPERATING_PRINCIPLES.md` |
| old multiplayer resurrection without AXM services | `PEER_FABRIC_RESEARCH_GATES.md` |
| third-party SDK only after measurement | `PEER_FABRIC_ARCHITECTURE.md`, `PEER_FABRIC_RESEARCH_GATES.md` |
| visual architecture log | `visuals/PEER_FABRIC_VISUAL_LOG.svg` |
| city physical mesh/integrity lane | PR #2 `docs/*` |

## Social-platform boundary

Discord, forums, messaging apps, websites, QR codes or other social systems may distribute an invite or group entrance.

They do **not** own the AXM group, do not need to carry the match, and should not become required infrastructure after peers have joined the fabric.

A community should be able to move from one social platform to another while keeping its underlying game-group identity/permissions.

## State-first boundary

Peer Fabric is not intended to send an entire rendered world when peers can reconstruct it locally.

Preferred network payloads are bounded game facts such as:

```text
input / event
state delta
simulation tick
hash
checkpoint acknowledgement
repair/correction
```

Rendering, animation, most simulation and other reconstructible work stay local according to the game adapter.

## Server boundary

Default direction:

```text
SERVERLESS BY DEFAULT
SERVER-CAPABLE BY EXCEPTION
```

Peer Fabric is the default for ordinary session-based multiplayer when measurements support it. Dedicated/server infrastructure remains a separate title-specific tool for cases such as huge persistent worlds, continuous asynchronous state, neutral official competitive authority, or other workloads that genuinely require persistent central computation.

Self-hosted/community dedicated servers may coexist without becoming an AXM-funded default dependency.

## Truth status

### Measured

Only the existing v0.1 local direct-invite/admission reference results are currently measured in PR #3.

### Research, not yet proven

- Internet-wide NAT traversal rate;
- Router Helper device coverage;
- reconnect/path migration success;
- public discovery at scale;
- public matchmaking quality;
- global cross-game discovery value;
- Sybil/eclipse resilience;
- production rollback/fairness;
- production host/coordinator migration;
- SDK readiness.

Do not promote any of these to completed/CANON without receipts from the corresponding gates.

## Immediate next engineering sequence

```text
1. local endpoint exposure + Router Helper
2. external reachability verification
3. community peer endpoint observation
4. deterministic resilience/adversity harness
5. group/discovery simulations
6. decentralized matchmaking simulator
7. fairness + migration harnesses
8. bounded shooter integration
```

The large vision stays preserved, but implementation should advance one measured gate at a time.
