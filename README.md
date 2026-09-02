# AXM City Multiplayer

AXM City Multiplayer is a research project for **free, local-first multiplayer across a city-scale dedicated mesh** without making a cloud datacenter responsible for rendering or simulating every player's game.

The central research question is:

> How little shared infrastructure is actually required when participant hardware computes its own experience and the network synchronizes only the truth that must be shared?

## Current status

**FOUNDATION / HYPOTHESIS STAGE**

No city-scale performance, coverage, capacity, cost, anti-cheat accuracy, or hardware claim is considered proven yet. This repository exists to turn those ideas into measurable gates rather than stories.

## Root architecture

```text
PLAYER PC / PHONE / CONSOLE
        |
        | client connection
        v
DEDICATED AXM ACCESS / STREET NODE
        |
        | fixed multi-hop city fabric
        v
DEDICATED AXM RELAY / BRIDGE NODES
        |
        +---- MATCH / TRUTH NODES
        |
        +---- optional CITY CORE services
```

- Phones and player devices are **clients only**, never required mesh relays.
- Fixed nodes provide the serious networking backbone.
- People can voluntarily extend coverage by hosting a dedicated node at a suitable location.
- Player hardware renders and computes as much of the game as possible.
- Shared nodes synchronize inputs/events, authoritative state changes, ordering, hashes, checkpoints, repair and integrity evidence.
- Private household LAN play remains independent from city-network matchmaking.

## Deterministic multiplayer direction

The target is not to stream the experience. The target is to synchronize the smallest verified information that causes every participant to derive the same experience locally.

```text
shared rules + shared seed + ordered player events
+ authoritative deltas + state hashes + rare repair
= synchronized world
```

This is a research direction, not yet a capacity claim.

## Network direction

Candidate technologies currently worth measuring include:

- Bluetooth LE / Bluetooth Mesh for small discovery, control or supporting messages rather than the primary gameplay backbone.
- Wi-Fi Aware for infrastructure-free nearby peer connectivity where device support permits it.
- Wi-Fi Direct / ordinary Wi-Fi paths as client or compatibility options.
- 802.11s-style fixed Wi-Fi mesh plus suitable routing for dedicated node-to-node city transport.
- Wi-Fi HaLow / 802.11ah as a future long-range candidate where legal spectrum rules, hardware availability and measured urban performance make sense.
- Other low-rate/ranging radios only where they solve a specific supporting problem.

Nothing is selected as CANON hardware or radio yet.

## Identity and accounts

Accounts are allowed and useful. Profiles, stats, achievements, rankings, friends and persistent identity are fun.

The intended default is **local-first identity and data ownership**:

- user state primarily lives on the user's device,
- cryptographic identity can prove continuity without requiring a central company to own the person,
- guest/basic access should remain possible where practical,
- an account enhances participation rather than becoming a toll booth.

## Integrity model

AXM does not assume cheating can be made impossible.

The intended direction is:

```text
record authoritative match evidence
        -> deterministic replay
        -> objective rule / state checks
        -> optional AI-assisted analysis
        -> verified integrity result
```

AI may investigate. AI alone is not proof.

A verified city-network cheating event can change routing state instead of creating a conventional ownership-style ban:

```text
HUMAN MATCH TRUST
      -> verified integrity violation
      -> ANOMALY / AI MATCH ROUTING
```

Private LAN play still works. The network need not investigate which household member, visitor or device owner caused the event beyond what the evidence actually proves.

See `docs/FIRST_JOIN_INTEGRITY_NOTICE.md` for the proposed up-front player notice.

## Repository working rule

**One working chat = one PR lane.**

See [`AGENTS.md`](AGENTS.md). Do not let one conversation fan out across multiple branches and half-finished PRs.

## Foundation documents

- [`docs/CITY_MESH_FOUNDATION.md`](docs/CITY_MESH_FOUNDATION.md) — architecture and decisions captured from the founding discussion.
- [`docs/RESEARCH_GATES.md`](docs/RESEARCH_GATES.md) — measurements required before large claims are allowed.
- [`docs/FIRST_JOIN_INTEGRITY_NOTICE.md`](docs/FIRST_JOIN_INTEGRITY_NOTICE.md) — draft first-entry integrity notice.

## External technical starting points

These are research references, not endorsements or proof of the final architecture:

- Android Wi-Fi Aware: https://developer.android.com/reference/android/net/wifi/aware/package-summary
- Android Wi-Fi Direct: https://developer.android.com/develop/connectivity/wifi/wifip2p
- Apple Wi-Fi Aware: https://developer.apple.com/documentation/WiFiAware
- Bluetooth Mesh primer: https://www.bluetooth.com/bluetooth-mesh-networking-primer/
- Linux wireless 802.11s documentation: https://wireless.docs.kernel.org/en/latest/en/developers/documentation/ieee80211/802.11s.html

## License

License choice should be made explicitly and consistently with the wider AXM repository policy. Do not silently invent or change licensing in a research PR.