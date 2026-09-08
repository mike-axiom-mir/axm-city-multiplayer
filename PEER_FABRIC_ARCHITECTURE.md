# AXM Peer Fabric Architecture

Status: **RESEARCH ARCHITECTURE — not yet implemented, benchmarked, merged, or CANON**

Date: 2026-09-04

This document captures the multiplayer architecture that grew out of the direct-invite P2P lane. It preserves the current economic boundary while extending the design from two known players toward communities and public matchmaking without requiring an AXM-operated gameplay or matchmaking service.

## Root objective

Make direct multiplayer feel ordinary to a non-networking user while keeping the default free-game path player-owned.

The target user experience is:

```text
friend / group / public quick match
            -> consent
            -> direct path discovery
            -> direct P2P game
```

The default architecture MUST NOT silently turn success into a recurring AXM infrastructure bill.

## Non-negotiable boundary

For the default free/local path:

- no AXM-funded gameplay relay is required;
- no AXM-funded dedicated game server is required;
- no AXM account is required merely to connect;
- no AXM central matchmaking database is required;
- direct failure remains an honest allowed state when no usable path exists;
- community/self-hosted infrastructure may be added by users without becoming an AXM obligation;
- title-specific dedicated servers remain a separate option for games that genuinely need central persistent authority.

This does **not** mean that no third peer may ever carry a tiny introduction or signaling message. A peer-provided introduction is different from relaying the match. The economic and architectural boundary is that the game traffic and continuing match do not depend on an AXM-operated middlebox.

## The fabric in one picture

```text
EXTERNAL SOCIAL SPACE
Discord / forum / message / QR / friend
                |
                | invite or first peer
                v
        +------------------+
        | AXM PEER FABRIC  |
        +------------------+
          | identity + consent
          | peer bonds
          | groups
          | discovery overlay
          | public presence
          | matchmaking proposals
          | path discovery / NAT help
          v
      DIRECT P2P SESSION
          |
          | deterministic game state
          | prediction / rollback
          | receipts / checkpoints
          v
          GAME
```

External social systems may distribute an invite. They do not own the AXM group or carry the match.

## State classes and lifetimes

The design is intentionally state-based rather than ledger-based.

| State | Typical lifetime | Owner / authority | Propagation |
| --- | --- | --- | --- |
| local peer identity | long-lived | local player device | only when needed |
| peer bond | long-lived until revoked | the two consenting peers | private |
| group membership | medium/long-lived | group policy + member | group scoped |
| public discovery record | minutes | signing peer/group | bounded overlay |
| presence ticket | seconds | signing peer | public/federated scope only |
| matchmaking proposal | seconds | candidate participants | selected participants only |
| match state | one session | game protocol | active match peers |
| checkpoint / receipt | bounded by game policy | match participants | match scoped |

There is no requirement for a permanent global chain of presence, queue or match-search history.

## 1. Local identity, consent and peer bonds

A peer should have a local cryptographic keypair. The public key or a derived peer identifier allows another peer to verify that a later signed record came from the same network identity.

The first connection may begin with the existing `AXMP2P1` invite. On explicit acceptance the game may optionally create a remembered **peer bond**:

```text
Peer A identity  <->  consent receipt  <->  Peer B identity
```

A peer bond may remember:

- peer public identity;
- compatible game/protocol ids;
- last successful connection method;
- locally chosen nickname/trust label;
- revocation state.

It SHOULD NOT treat an old IP address as identity. Network addresses change.

Revoking a peer bond removes future automatic trust. It does not rewrite historical local receipts.

### Privacy refinement

The stable network identity does not have to equal a public social/account identity. Public matchmaking can use short-lived session identifiers or unlinkable presentation keys where practical so that publishing `LOOKING_FOR_MATCH` does not automatically publish a permanent social graph.

## 2. Connectivity: find a direct path before declaring failure

Candidate direct paths should be gathered locally and tested in a deterministic preference order.

Candidate sources may include:

1. same-LAN addresses;
2. globally reachable IPv6;
3. explicit local router mapping through PCP;
4. NAT-PMP where available;
5. UPnP IGD where explicitly permitted by the user;
6. manual port forwarding;
7. an externally observed UDP address learned from another reachable peer;
8. simultaneous connectivity checks / hole-punch attempts when both peers have suitable mappings.

The final protocol may borrow ICE-style candidate gathering and connectivity checks while deliberately omitting mandatory TURN relay fallback. RFC 8445 demonstrates the useful split between candidate exchange and actual connectivity checks; AXM does not need to inherit the economic choice of always providing a relay.

A reachable peer can also act as a lightweight endpoint observer: it can tell another peer which source IP/port it observed. That is STUN-like information exchange performed by the community fabric rather than a required AXM STUN service.

### Important truth boundary

This improves reachable cases; it cannot create an inbound route where the ISP/NAT topology provides none. Some CGNAT/symmetric-NAT combinations can still make pure direct connectivity unavailable.

The correct result remains:

`DIRECT_CONNECTION_UNAVAILABLE`

not a hidden paid relay.

## 3. Router Helper: remove the knowledge barrier

The old P2P usability failure was often not lack of connectivity but lack of networking expertise.

A separate local helper should turn:

```text
"forward UDP 28741 on the correct LAN host and firewall"
```

into:

```text
Direct hosting needs one local network change.
[Apply safely] [Show me exactly what to click] [Cancel]
```

The helper should:

- diagnose before changing anything;
- prefer temporary/reversible mappings;
- use PCP / NAT-PMP / UPnP only with explicit consent;
- create only the minimum required local firewall rule;
- verify actual external reachability rather than trusting a router success response;
- provide model-specific manual guidance when safe automation is unavailable;
- explain CGNAT or impossible topology plainly;
- remove its own mappings/rules on request;
- never enable DMZ or broad remote administration as a shortcut;
- never pretend a requested mapping is a verified connection.

The helper exists to remove the expert-knowledge tax, not to become a general router-control application.

## 4. Groups: private, federated and public

A group is a discovery and consent namespace, not necessarily a game server.

### Private

Membership and presence stay inside that group.

```text
PRIVATE A
  A1
  A2
  A3
```

No automatic export into public matchmaking.

### Federated

A group explicitly allows selected other groups to exchange matchmaking presence.

```text
GROUP A <-> GROUP B <-> GROUP C
```

Membership lists do not have to merge.

### Public

A public group opts into the game-wide public discovery fabric.

```text
PUBLIC A ---- PUBLIC B
    |             |
 PUBLIC C ---- PUBLIC D
```

**Public does not mean every member opens a socket to every other member.** That would scale badly. Public groups participate in a bounded overlay where each peer/group keeps only a limited set of discovery neighbors.

Public also does not mean publishing every member's network endpoint. The group may export only signed short-lived matchmaking/presence records. Direct connection information is exchanged after a match or connection handshake is accepted.

## 5. Public discovery overlay

Two proven decentralized mechanisms are useful references:

- Kademlia-style DHTs for locating peers/resources without one tracker;
- gossip/pubsub overlays for rapidly changing temporary state.

BitTorrent BEP 5 is a practical precedent: a DHT stores peer contact information so each participating node contributes to trackerless discovery.

A promising AXM split is therefore:

### Slower-changing discovery state

Use a DHT-like structure for:

- game/public-group rendezvous records;
- reachable discovery peers;
- bootstrap peer exchange;
- protocol/version namespaces.

### Fast-changing ephemeral state

Use bounded gossip/pubsub or direct neighbor exchange for:

- online presence;
- `LOOKING_FOR_MATCH` tickets;
- party availability;
- short-lived network quality hints;
- match proposal routing.

This is a **candidate architecture**, not a selected implementation. It must be tested against a simpler pure-DHT design and against a simpler bounded-gossip design.

### Signed, expiring records

Public records should be domain-separated and signed by their issuer. A useful conceptual precedent is libp2p's signed-envelope model, which was designed so data stored in an untrusted public location can still be authenticated.

Example presence ticket:

```text
record_type = axm.presence.v1
game_id = axm.shooter
protocol = 1
ruleset_hash = ...
session_peer_id = ...
mode = team_deathmatch
party_size = 1
status = looking
issued_at = ...
expires_at = ...
nonce = ...
signature = ...
```

The ticket must expire automatically. No explicit global delete is required for ordinary presence disappearance.

## 6. Decentralized public matchmaking

The public network only needs to answer:

> Which currently advertising peers are compatible enough to attempt a match?

It does **not** need global consensus about the whole queue.

A local matcher may score candidates using:

- game/protocol/ruleset compatibility;
- requested mode;
- party size;
- measured latency;
- jitter;
- packet loss;
- reachable path quality;
- optional broad skill bucket;
- optional region/language/community preferences.

The scoring formula must be versioned and deterministic for the same observed inputs.

### Match proposal handshake

A candidate match can be formed without a central authority:

```text
search tickets
    -> choose candidate set
    -> create signed proposal
    -> each candidate accepts exactly one active proposal
    -> required accepts collected
    -> match commit
    -> establish direct game links
```

Example proposal fields:

```text
proposal_id
proposer_session_id
participant_session_ids
mode
ruleset_hash
network_protocol
created_at
expires_at
candidate_score_receipt
```

Each participant signs an acceptance or rejection.

A short arbitration rule is needed for races where one player appears in multiple proposals. One research candidate is: within a bounded arbitration window, a peer selects the highest local score and uses the proposal id as a deterministic tie-breaker, then issues one short-lived `MATCH_LEASE`. Other proposals receive `BUSY`.

Only the selected participants need agreement. There is no reason to ask the entire public network to vote.

### Matchmaking truth boundary

Decentralized matchmaking can remove the central matchmaker, but it cannot guarantee globally perfect queue fairness or a single universal ordering of all players without introducing heavier consensus. AXM should optimize for useful, fast, locally verifiable matching rather than pretend to have a globally ordered queue.

## 7. Ignition peer: solve cold start without becoming the network

A fresh installation knows nobody. Information cannot be discovered from zero known endpoints.

AXM therefore permits an **ignition peer**:

```text
new player
    -> one known reachable ignition peer
    -> receive several live peer introductions
    -> connect directly to those peers
    -> continue through public fabric
```

The ignition peer:

- may be a friend's machine;
- may be a peer learned from a group invite;
- may be a community volunteer node;
- may be an AI gamer that happens to be online often;
- must not be required to relay gameplay;
- must not become central match authority;
- should disappear from the path after peer introductions;
- must be replaceable by any compatible peer.

The AI persona is optional. The bootstrap function itself should remain tiny and deterministic.

A healthy client should remember multiple previously successful public peers so the ignition peer becomes a fallback rather than a permanent dependency.

## 8. Host is a network role, not privileged time

Traditional listen-server games can give the host an advantage because host input reaches local authority immediately.

AXM should separate:

- **network coordinator**: helps carry/organize packets;
- **canonical game timing**: applies the same ordering/fairness rules to every player.

A candidate design for deterministic games is:

```text
local input
    -> immediate local prediction
    -> tagged with simulation tick
    -> shared bounded input window
    -> canonical tick resolution
    -> rollback/replay if prediction differed
```

The coordinator's own input must travel through the same logical acceptance rule as remote input even if it does not physically traverse the Internet.

This can greatly reduce **host-specific** advantage. It cannot remove the physical advantage of genuinely lower latency or make geographically distant players identical.

## 9. Host/coordinator migration

A coordinator disappearing should not necessarily kill a deterministic match.

Research direction:

1. periodically produce a bounded checkpoint;
2. hash it;
3. retain the ordered input/event log since that checkpoint;
4. peers acknowledge the checkpoint/hash according to the game's trust model;
5. pre-rank replacement coordinators from measured connection quality;
6. on coordinator loss, elect the next reachable candidate;
7. restore checkpoint + replay accepted events;
8. continue if state hashes agree.

This is substantially easier for games that already have deterministic, checkpointable state than for opaque server-authoritative worlds.

## 10. Mesh shape: discovery and gameplay are different

Do not confuse a public discovery mesh with a full gameplay mesh.

### Discovery overlay

Should have bounded degree.

If each peer holds roughly `k` discovery neighbors, connection count grows approximately with `N * k`, not `N^2`.

### Gameplay

For very small matches a full peer mesh may be reasonable because it removes a single transport center.

For larger matches a star/tree/coordinator shape may be more bandwidth-efficient. The game transport choice can differ from the discovery overlay while preserving the same player-owned economic boundary.

Therefore AXM Peer Fabric should expose **topology adapters**, not hard-code "everyone always connects to everyone".

## 11. Security and abuse boundaries

Decentralization removes a central bill; it does not remove attackers.

The research layer must explicitly test:

### Sybil / fake-peer flooding

A public key proves continuity of a key, not that it represents one human. Defenses should begin with local rate limits, bounded ticket publication, proof-of-work only if later measurements justify it, and local behavioral scoring rather than a global identity registry.

### DHT poisoning / eclipse attempts

Mitigations to test:

- signed records;
- query multiple independent peers;
- keep diverse neighbors;
- random exploration in addition to best-known peers;
- reject stale sequence/expiry records;
- local peer scoring;
- never trust one ignition peer as the sole view of the network.

libp2p GossipSub v1.1 is a useful reference because it uses local peer scoring, gossip diversification and bounded spam responses instead of one global reputation authority.

### Amplification / unsolicited traffic

Connection handshakes must be non-amplifying or tightly bounded. Public advertisements should not authorize arbitrary large responses. Use short-lived cookies/nonces, rate limits and stateless rejection where practical.

### IP privacy truth

Direct P2P ultimately reveals a network endpoint to the peers you directly connect with. Public group membership should not reveal it to everyone, but AXM cannot promise IP anonymity in a direct-only architecture. Strong endpoint hiding requires a relay/VPN-style intermediary and is outside the default free direct path.

### Cheating

Peer Fabric discovery is not the anti-cheat authority. The existing AXM direction remains deterministic record/replay evidence, bounded sanctions/routing, AI-assisted review rather than AI as sole judge, and no claim that cheating can be perfectly prevented.

## 12. Third-party / SDK direction

If the research succeeds, the reusable value is not one game implementation but a layered SDK.

Candidate modules:

```text
axm-peer-identity
axm-peer-invite
axm-peer-connectivity
axm-peer-router-helper
axm-peer-discovery
axm-peer-groups
axm-peer-matchmaking
axm-peer-transport
axm-peer-checkpoint
```

A game should ideally ask for intent, not networking trivia:

```text
create_private_group(...)
join_group(invite)
find_public_match(game, mode, party_size)
host_direct(...)
join_direct(...)
```

The game then supplies its own replication/rollback/state adapter.

## 13. What this architecture does not claim yet

Not yet measured or proven:

- public discovery convergence at Internet scale;
- resistance to sustained Sybil/eclipse attacks;
- reliable NAT traversal rate across consumer ISPs;
- router-helper device coverage;
- acceptable bandwidth/CPU cost for large public fabrics;
- fair matchmaking quality at high churn;
- production-grade host migration;
- production shooter rollback/fairness;
- browser-only direct transport without external relay dependency;
- third-party SDK readiness.

These remain research gates.

## Reference precedents

These are references, not dependencies or proof that AXM's full design is solved:

- RFC 5128 — P2P communication across NATs: https://www.rfc-editor.org/rfc/rfc5128
- RFC 6887 — Port Control Protocol (PCP): https://www.rfc-editor.org/rfc/rfc6887
- RFC 8445 — ICE candidate gathering/connectivity checks: https://www.rfc-editor.org/rfc/rfc8445
- RFC 8489 — STUN / mapped transport address: https://www.rfc-editor.org/rfc/rfc8489
- BitTorrent BEP 5 — trackerless DHT peer discovery: https://www.bittorrent.org/beps/bep_0005.html
- libp2p signed envelopes: https://github.com/libp2p/specs/blob/master/RFC/0002-signed-envelopes.md
- libp2p routing records: https://github.com/libp2p/specs/blob/master/RFC/0003-routing-records.md
- libp2p AutoNAT / hole punching concepts: https://docs.libp2p.io/concepts/nat/autonat/ and https://docs.libp2p.io/concepts/hole-punching/
- libp2p GossipSub v1.1: https://github.com/libp2p/specs/blob/master/pubsub/gossipsub/gossipsub-v1.1.md
- Valve GameNetworkingSockets P2P/custom signaling: https://github.com/ValveSoftware/GameNetworkingSockets/blob/master/README_P2P.md
- "P2P matchmaking solution for online games" (SelfAid, 2020): https://link.springer.com/article/10.1007/s12083-019-00725-3
