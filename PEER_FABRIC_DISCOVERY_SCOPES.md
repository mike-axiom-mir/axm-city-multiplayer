# AXM Peer Fabric Discovery Scopes

Status: **RESEARCH ARCHITECTURE — not yet implemented, benchmarked, merged, or CANON**

Date: 2026-09-05

This document refines AXM Peer Fabric into one local substrate plus **four player-chosen online discovery scopes**.

The scopes are not four different networking stacks. They are progressively wider consent/discovery boundaries on top of the same direct P2P fabric.

## LAN is the substrate, not one of the four online layers

Local-network play is the floor:

```text
LAN / same local network
        |
        +-- direct local discovery / direct local session
        +-- no Internet discovery required
        +-- remains usable independently of wider Peer Fabric participation
```

LAN should remain available even when every online discovery scope is disabled.

It is intentionally not counted as one of the four Internet/social discovery layers because it does not require the wider-distance discovery fabric.

## The four online discovery scopes

```text
LAN substrate
     |
     v
[1] FRIEND P2P
     |
     v
[2] PRIVATE SOCIAL GROUP P2P
     |
     v
[3] PUBLIC PER-GAME P2P
     |
     v
[4] GLOBAL AXM P2P FABRIC
```

The player chooses how far outward discovery may travel.

A broader scope expands who may be **discovered as a compatible candidate**. It does not automatically grant strangers persistent trust, group membership, or unrestricted network access.

---

## Scope 1 — Friend P2P

Purpose: connect directly to known people.

Entry methods may include:

- copy/paste invite;
- QR invite;
- remembered consent-based peer bond;
- direct LAN peer promoted to an Internet-capable remembered peer;
- an externally delivered invite through Discord, Signal, WhatsApp, email, forum, or any other social channel.

Conceptual flow:

```text
PLAYER A
   |
   | explicit invite / remembered peer bond
   v
PLAYER B
   |
   v
direct P2P game
```

Properties:

- explicit person-to-person consent;
- no public presence advertisement required;
- no group membership required;
- no central AXM lobby required;
- easiest online scope to reason about and test.

This is the closest evolution of classic direct-connect multiplayer, with the expert networking burden moved into Peer Fabric and Router Helper.

---

## Scope 2 — Private Social Group P2P

Purpose: let a bounded club, clan, family, friend circle, or game-night community discover each other without making themselves public.

```text
PRIVATE GROUP
  |-- Peer A
  |-- Peer B
  |-- Peer C
  `-- Peer D
```

A member may advertise temporary presence such as:

```text
online
playing axm.shooter
looking for co-op
party has 2/4 players
```

but that presence remains inside the private group or explicitly approved federation.

Properties:

- membership is a consent boundary;
- group discovery does not imply permanent peer bonds between every member;
- group members do not need to know one another personally;
- direct endpoint details remain gated until peers actually form/accept a connection;
- the group can be distributed through an invite on an existing social platform without that platform owning the group;
- leaving/revocation removes future group-scoped discovery authorization according to group policy.

### Optional federation

Private groups may later choose explicit group-to-group federation:

```text
GROUP A <-> GROUP B <-> GROUP C
```

Federation widens discovery only to approved groups. Membership databases do not merge automatically.

---

## Scope 3 — Public per-game P2P

Purpose: let strangers find compatible players for **one specific game** without a central AXM matchmaking server.

Example namespace:

```text
axm.shooter public fabric

Group A ---- Group B
   |            |
Peer 1        Peer 8
   |            |
Group C ---- Group D
```

Public groups and individual public participants contribute bounded peer links to that game's discovery overlay.

The important scaling rule is:

> Public P2P is **not** every player connected to every other player.

Each participant keeps a bounded number of discovery neighbors. Signed, expiring presence/matchmaking records propagate through the overlay. Actual gameplay connections are created only for the selected match participants.

Example public ticket:

```text
scope = GAME_PUBLIC
game_id = axm.shooter
ruleset = ...
mode = team_deathmatch
party_size = 1
status = looking
expires_at = ...
session_peer_id = ...
signature = ...
```

Example match path:

```text
publish short-lived LOOKING ticket
            |
            v
discover compatible game-scoped tickets
            |
            v
local candidate scoring
            |
            v
signed bounded match proposal
            |
            v
selected players accept
            |
            v
direct P2P match
```

No global queue ordering or blockchain-style consensus is required. Only the selected participants need to agree on the match proposal.

Properties:

- unknown players can match without first becoming friends;
- public presence is temporary and game-scoped;
- game version/ruleset compatibility is checked before match formation;
- direct network details are not automatically broadcast to the whole public fabric;
- the network may grow organically one public group/peer at a time;
- community ignition peers may help a new player find the first live peers.

---

## Scope 4 — Global AXM P2P Fabric

Purpose: let participating games share one larger decentralized **discovery substrate** while preserving game-specific matchmaking.

This is the widest player-selectable scope.

```text
                 AXM GLOBAL PEER FABRIC

        Peer routing / bootstrap / health / discovery
              /             |              \
             /              |               \
            v               v                v
      AXM Shooter        AXM RTS         AXM Co-op
      namespace          namespace       namespace
          |                  |               |
      shooter match       RTS match        co-op match
```

### Critical separation

Global AXM does **not** mean combining all games into one matchmaking pool.

The fabric can share:

- peer discovery neighbors;
- ignition/bootstrap routes;
- cryptographic transport identity primitives;
- NAT/path observations where safe and relevant;
- protocol capability advertisements;
- network-health measurements;
- bounded abuse-defense knowledge that is valid across the fabric.

But match tickets remain namespaced by at least:

```text
game_id
protocol_version
ruleset/build compatibility
mode / queue intent
```

A peer currently participating in an RTS can help keep the wider AXM discovery fabric connected without being presented as an eligible Shooter opponent.

### Why this layer matters

At sufficient adoption, every compatible multiplayer game can strengthen the common discovery network instead of each title rebuilding an isolated matchmaking island.

That creates a potentially self-reinforcing ecosystem:

```text
more games
   -> more participating peers
   -> more bootstrap/discovery paths
   -> stronger shared fabric
   -> easier cold start for future games
```

This remains a hypothesis until measured under churn, hostile peers, network partitions, version skew, and Internet-scale simulation.

---

## Player choice is the governing rule

The desired user-facing decision is simple:

```text
ONLINE DISCOVERY

( ) Friends only
( ) My private groups
( ) Public players in this game
( ) Global AXM fabric
```

The exact UI is not CANON, but the permission principle is:

> **The player chooses the widest discovery boundary for the session/game.**

The implementation MUST NOT silently widen a user's discovery scope.

Games may remember a player's explicit preference locally, but a broader remembered choice should remain visible and reversible.

### Broader scope does not mean broader trust

If a player selects Global AXM, the permission is conceptually:

```text
"My machine may participate in the wider discovery fabric and advertise
short-lived compatible-game availability according to my settings."
```

It does **not** mean:

```text
"Every AXM user is permanently trusted by my machine."
```

Actual direct-connect authorization remains a bounded handshake for the selected connection or match.

---

## Search can expand outward without changing the permission model

A game may optionally search from nearest/narrowest to widest permitted scope:

```text
LAN
 -> friends
 -> private groups
 -> game public
 -> global AXM fabric
```

Example:

```text
Player selected GLOBAL AXM
        |
        +-- compatible LAN peer? use it
        +-- compatible friend? use it
        +-- compatible group peer? use it
        +-- compatible game-public peer? use it
        `-- otherwise continue through global discovery substrate
```

This is a candidate matching policy, not a requirement. A player may prefer a strict scope such as "private group only" even when wider scopes are configured elsewhere.

---

## Ignition peer relationship to the scopes

A fresh installation can know zero live peers. Any online scope therefore needs at least one initial route.

The first route may come from:

```text
friend invite
private-group invite
public game invite
community ignition peer
AI gamer acting as ignition peer
remembered prior peer
```

An ignition peer only needs to provide enough information to reach additional compatible peers.

```text
NEW PEER
   |
   v
IGNITION PEER
   |
   | introductions / endpoint observation
   v
LIVE PEERS
   |
   v
chosen discovery scope
```

It must not become mandatory gameplay relay or central match authority.

---

## Failure and fallback semantics

A wider discovery scope cannot override physical network truth.

Discovery success:

```text
compatible peer found
```

does not guarantee:

```text
direct network path exists
```

Peer Fabric still performs direct-path testing and may invoke the consent-based Router Helper where appropriate.

If no direct route can be established and the title has no separately selected infrastructure mode, the honest terminal state remains:

```text
DIRECT_CONNECTION_UNAVAILABLE
```

No discovery scope may silently convert that into AXM-funded relay traffic.

---

## Research gates introduced by the four-scope model

### Gate DS-1 — Scope isolation

Prove that presence published to `FRIENDS` cannot be discovered through private/public/global queries without explicit widening.

### Gate DS-2 — Private-group isolation

Create multiple private groups with overlapping members and verify that membership/presence does not leak across group boundaries.

### Gate DS-3 — Per-game namespace isolation

Run at least two simulated games on the same public discovery overlay. Verify that Shooter matchmaking never returns RTS-only tickets and vice versa.

### Gate DS-4 — Global shared-substrate value

Compare cold-start and peer-discovery success for:

1. isolated per-game discovery networks;
2. a shared global AXM discovery substrate with game-scoped matchmaking tickets.

Measure whether the shared fabric actually improves route/bootstrap resilience rather than merely adding overhead.

### Gate DS-5 — Bounded degree at scale

Simulate increasing peer counts while keeping each peer's discovery-neighbor budget bounded. Verify that connection count grows approximately with `N * k`, not `N^2`.

### Gate DS-6 — Player choice / no silent widening

For every transition between scopes, prove that widening requires an explicit local state change and that narrowing immediately prevents new advertisements outside the selected boundary.

### Gate DS-7 — Cross-game churn

Continuously add/remove entire game populations from the global fabric. Verify that one game's disappearance does not collapse discovery for unrelated games.

### Gate DS-8 — Global does not equal global trust

Verify that receiving/discovering a public/global presence ticket is insufficient to create a remembered peer bond or unrestricted inbound access.

---

## Current truth status

**Measured already in this PR lane:** the v0.1 local direct-invite/admission reference core and its previously reported 8/8 reference suite.

**Not yet measured:** these four discovery scopes, global shared fabric, cross-game isolation, scope-transition semantics, large-scale overlay behavior, or the new gates above.

The four-scope model is therefore a preserved architecture direction, not a claim of completed multiplayer infrastructure.
