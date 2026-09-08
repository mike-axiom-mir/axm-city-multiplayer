# AXM Peer Fabric Operating Principles

Status: **preserved design principles — research until measured**

Date: 2026-09-05

This file captures design decisions from the P2P multiplayer discussion that were previously only implicit across architecture/test files.

## 1. Serverless by default, server-capable by exception

For ordinary session-based AXM multiplayer, the default should be direct player-owned networking when measurements show it is suitable.

```text
SERVERLESS BY DEFAULT
SERVER-CAPABLE BY EXCEPTION
```

A dedicated/server path remains legitimate when the workload genuinely benefits from persistent central computation, for example:

- huge persistent worlds that continue changing while individual players are offline;
- large asynchronous/shared economies;
- official competitive modes that deliberately choose a neutral central authority;
- workloads with hidden information that should not be present on participating client machines;
- title-specific scale/topology that direct peers cannot reasonably sustain.

That server mode is separate from the free/local default. Community/self-hosted dedicated servers may also exist without creating an AXM operating obligation.

## 2. Modern bandwidth is margin, not permission to become wasteful

Historic P2P games often operated under tiny upstream budgets. Modern fixed connections commonly provide far more upload capacity, but Peer Fabric should treat that improvement as safety margin rather than an excuse to transmit unnecessary state.

Design preference:

```text
simulate/reconstruct locally
        +
transmit only what peers need to agree
```

Candidate network payloads include:

- player inputs;
- authoritative/accepted events;
- compact state deltas;
- simulation ticks/time markers;
- state hashes;
- bounded checkpoints;
- corrections/repair receipts.

Do not transmit rendering, animation, or reconstructible world detail merely because bandwidth is available.

No fixed bandwidth claim becomes CANON until measured per game/topology.

## 3. Test against bad networks, not only today's good connection

The target should be a multiplayer layer that behaves gracefully under conditions much worse than a developer's normal home connection.

Example **test profiles, not production promises**:

```text
upload cap:        1 Mbps
latency:           100 ms
packet loss:       5%
jitter:            variable spikes
packet order:      occasional reordering
brief disconnect:  1-5 seconds
endpoint change:   yes
interface change:  Wi-Fi <-> Ethernet where testable
host/coordinator:  disappears mid-match
```

If a game remains usable under a deliberately hostile profile, modern broadband becomes headroom rather than a requirement.

## 4. Connection success is not the end of connectivity work

After two peers connect, Peer Fabric should continue to protect the path.

Research direction:

- keep bounded heartbeat/liveness state;
- maintain more than one viable connection candidate when practical;
- detect temporary path failure;
- re-authenticate using peer identity rather than trusting a changed address;
- retry direct candidates after public IP/port changes;
- support path/interface migration where the transport permits it;
- expire stale candidates;
- never silently widen discovery/permission during reconnection;
- terminate explicitly when no permitted direct route remains.

A remembered peer bond is an identity/consent relationship. It is not a permanent IP-address pin.

## 5. Equalize game authority, not every player's physical latency

Host/coordinator privilege should be designed out where practical.

The coordinator may organize traffic but should not receive a special game-time lane.

Candidate fairness mechanisms:

- shared simulation/tick acceptance rules;
- immediate local prediction;
- bounded rollback/replay;
- bounded input acceptance windows;
- recent state history for game-specific lag compensation/rewind;
- deterministic validation of historical hit/action state where the game requires it.

Do **not** blindly add enough artificial delay to every low-latency player to match the worst connection. The objective is to remove host-role privilege, not to pretend geography and physical latency do not exist.

Any fairness/rewind window must be bounded, versioned, measured and game-specific.

## 6. Discovery topology and gameplay topology are separate choices

Public discovery should be bounded-degree, not all-to-all.

Gameplay topology may differ by match size:

- very small sessions may use a full peer mesh;
- larger sessions may choose a measured coordinator/star/tree/hybrid topology;
- host/coordinator selection should use measured path quality, not social status.

The same player-owned economic boundary applies to every topology.

## 7. Ignition AI is a wrapper, not a dependency

An AI gamer may act as an ignition peer because it is often online and can provide a friendly first contact.

Optional user experience:

```text
no human peers found
    -> AI gamer can provide introductions
    -> optionally play as an opponent while humans are unavailable
```

The bootstrap protocol underneath must remain tiny, deterministic and replaceable by any compatible community peer. The AI must not become central matchmaking authority or required gameplay relay.

## 8. Social platforms are entrances, not owners

Discord, forums, messaging apps, websites, QR codes and other communities can distribute friend/group/public invitations.

After entry, the group identity and multiplayer fabric should be independent of that platform.

If a community moves from one social platform to another, its AXM group should not need to die with the old platform.

## 9. Wider discovery never implies wider trust

The player controls the maximum discovery scope:

```text
Friends
Private groups
Public players in this game
Global AXM fabric
```

Global participation means the machine may help/consume the shared discovery substrate according to its settings. It does not mean every AXM peer becomes permanently trusted or receives unrestricted inbound access.

Direct endpoint details remain gated until the selected connection/match handshake.

## 10. Multiplayer longevity is a first-class acceptance goal

A successful free multiplayer game should not become permanently dependent on the developer paying a central matchmaking bill.

Long-term target:

```text
developer/company service disappears
        -> players still possess game + Peer Fabric
        -> one friend/group/ignition route exists
        -> peer network wakes
        -> players form direct matches
```

This is not considered proven until the old-game resurrection gate passes with AXM-operated services unavailable.

## 11. Economic success must not become infrastructure punishment

The architectural target is that increasing player count does not automatically multiply AXM gameplay-hosting cost.

This does not mean the system has zero costs or zero operational concerns. It means the default match should consume the participating players' own compute/network resources rather than requiring AXM to relay every packet.

Any future paid/official infrastructure must be explicit and title-specific, never a hidden fallback from the free direct path.
