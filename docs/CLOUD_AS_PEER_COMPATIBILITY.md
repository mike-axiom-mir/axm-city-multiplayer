# AXM Cloud-as-Peer Compatibility Principle

Status: **COMPATIBILITY NOTE / NOT IMPLEMENTED / NOT CANON**

Date: 2026-09-05

This note preserves a simple compatibility insight for future AXM multiplayer work and for third-party developers reading the repository:

> Cloud infrastructure is still a machine on a network. In Peer Fabric terms, it can be treated as a peer with unusually strong uptime, reachability, bandwidth, and persistence rather than as a fundamentally different architecture.

This does **not** mean every cloud system can be converted trivially, and it does not remove title-specific authority requirements. It means existing cloud-hosted multiplayer does not have to be discarded before it can interoperate with a peer-first fabric.

## The abstraction

Candidate peer locations may include:

```text
home PC
console / handheld
community server
city node
VPS
cloud VM
dedicated bare-metal host
AI gamer machine
```

The useful distinction is not primarily *where* the machine runs. The useful distinction is which capabilities and authorities it has.

Example capability description:

```text
peer_id
reachable = true
uptime_class = high
bandwidth_class = high
can_introduce = true
can_observe_endpoint = true
can_coordinate = true
can_store_checkpoint = true
can_host_match = true
```

The exact schema is not selected.

## Existing cloud game migration path

An existing game may begin with:

```text
player A ---+
player B ---+--> cloud game server
player C ---+
```

A gradual Peer Fabric integration could preserve the cloud machine and reinterpret it as a stable peer role:

```text
player A -------- player B
    \                /
     \              /
      CLOUD PEER / COORDINATOR
```

Possible staged path:

1. keep the existing cloud server and game authority model;
2. add AXM-compatible peer/session identity at the networking boundary;
3. expose the cloud host as one reachable peer/capability provider;
4. allow direct player-to-player paths where the title's rules permit them;
5. move discovery or matchmaking into the peer fabric only if and when measured gates justify it;
6. keep cloud persistence, neutral authority, hidden information, world continuity, or other central roles where they remain genuinely useful.

This is a compatibility direction, not a migration promise.

## Peer does not mean equal authority

A peer-first protocol does not require every participant to have identical powers.

A game's rules may assign different roles:

```text
PLAYER_PEER
  may submit player inputs

COORDINATOR_PEER
  may order or bundle accepted events

CHECKPOINT_PEER
  may retain bounded recovery state

IGNITION_PEER
  may introduce live peers

AUTHORITATIVE_CLOUD_PEER
  may own title-specific canonical decisions
```

The architectural goal is to make authority **explicit and role-based**, not to grant special ownership merely because a machine happens to run in a datacenter.

## Why this helps third-party adoption

A developer with an existing cloud game should not have to think:

> "Peer Fabric requires deleting our backend first."

A better question is:

> "Which parts of our backend are already just network participants, which roles genuinely need central persistence/authority, and which paths can become direct or community-owned?"

That lets integration be incremental.

A capable AI inspecting an open-source or available codebase may be able to identify the existing transport boundary, treat the server as a stable peer, and build adapters around it without rewriting unrelated rendering/gameplay systems. Difficulty here becomes partly a measure of how deeply the original game welded networking assumptions into its internal logic.

## Economic boundary remains unchanged

Cloud participation is allowed.

Mandatory AXM-funded cloud participation is not the default.

```text
cloud peer chosen by developer/community
        -> allowed

community pays for its own stable host
        -> allowed

player hosts a VPS as ignition/discovery peer
        -> allowed

AXM silently pays recurring relay/server costs
so every free match can function
        -> outside the default Peer Fabric contract
```

A cloud peer may be excellent because it is stable. Its usefulness does not make it the owner of the network.

## Failure and disappearance

A strong long-term target remains:

```text
one cloud peer disappears
        -> compatible peers seek another permitted route/role holder
        -> fabric continues where its protocol/topology allows
```

For title-specific authoritative persistent worlds this may not always be possible. Such titles should state that dependency honestly rather than pretending to be serverless.

## Relationship to PR #3

PR #3 is the source lane for the direct P2P implementation and Peer Fabric operating principles. This document does not modify or duplicate that implementation.

It records a compatibility insight discovered while PR #2's city-network work was being compared with PR #3:

```text
LOCAL MACHINE
CITY NODE
CLOUD MACHINE
DEDICATED SERVER

all become candidate network peers with explicit roles/capabilities.
```

A future reconciliation/integration lane may decide whether this belongs directly in Peer Fabric's canonical operating principles after measurement and review.

## Current truth status

**RESEARCHED / ARCHITECTURAL:** cloud and dedicated hosts can participate in ordinary network protocols and can therefore be modeled as stable peers where the protocol permits.

**HYPOTHESIS:** treating cloud/server deployments as peer roles will materially reduce migration friction for existing games integrating with AXM-compatible Peer Fabric.

**NOT PROVEN:** one-day conversion of arbitrary cloud games, seamless authority migration, zero-downtime role replacement, or suitability for every server-authoritative title.

No merge or CANON action is performed by this note.
