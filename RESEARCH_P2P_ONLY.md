# Research: P2P-only multiplayer without AXM-funded infrastructure

## Decision

For free/local AXM games, the default online path is player-hosted direct peer-to-peer.

No AXM-operated relay, gameplay proxy, central matchmaking service, or dedicated-server service is required by the default core.

A peer-provided introduction/signaling message is allowed. That is not the same thing as relaying gameplay. The architectural boundary is that continuing game traffic does not depend on an AXM-operated middlebox and a failed direct route is allowed to fail honestly.

## Important networking truth

Classic UDP/TCP hole punching is often described as peer-to-peer, but the common Internet pattern still needs a way for peers to discover externally mapped endpoints and coordinate simultaneous connection attempts.

Reference: RFC 5128, *State of Peer-to-Peer (P2P) Communication across Network Address Translators (NATs)*.
https://www.rfc-editor.org/rfc/rfc5128

ICE makes this split explicit: peers gather candidate addresses, exchange them over a signaling path, and perform connectivity checks. ICE commonly uses STUN for reflexive addresses and may use TURN as a relay fallback.

Reference: RFC 8445, *Interactive Connectivity Establishment (ICE)*.
https://www.rfc-editor.org/rfc/rfc8445

AXM may reuse the useful **candidate exchange + connectivity check** idea without inheriting a mandatory paid TURN/relay fallback.

## Serverless reachable-host path

The host needs an endpoint the guest can actually reach.

Preferred possibilities:

1. globally reachable IPv6 plus an allowed firewall rule;
2. an explicit router/NAT port mapping;
3. a user-created manual port-forward;
4. an externally observed mapping learned from another reachable peer, followed by direct connectivity checks;
5. otherwise fail as `DIRECT_CONNECTION_UNAVAILABLE`.

PCP is a standards-track protocol designed to let applications create mappings for inbound communication through NAT/firewall devices, including short-lived uses such as games. The resulting external address/port can then be communicated to the remote peer through an AXM invite or peer-signaling record.

Reference: RFC 6887, *Port Control Protocol (PCP)*.
https://www.rfc-editor.org/rfc/rfc6887

UPnP IGD is another widely deployed local-router mechanism. MiniUPnP is one implementation that can query the external address and add/delete port mappings without any AXM cloud service.

Reference implementation:
https://github.com/miniupnp/miniupnp

STUN formalizes the idea that a remote endpoint can tell a client which source address/port it observed.

Reference: RFC 8489, *Session Traversal Utilities for NAT (STUN)*.
https://www.rfc-editor.org/rfc/rfc8489

A future AXM public peer can potentially provide this tiny observation function to another peer. That must be tested. If a third peer is still carrying the gameplay after connection, the test did not prove a direct path.

## Production transport direction

The Python UDP code in this repository is intentionally a reference handshake, not final game netcode.

For native games, a strong candidate adapter is Valve's open-source GameNetworkingSockets. The open-source project can use custom P2P signaling, supports reliable/unreliable UDP messaging, fragmentation/reassembly, encryption, IPv6 and ICE-based NAT traversal. AXM does not need Steam Datagram Relay for a deliberately direct-only path.

References:
https://github.com/ValveSoftware/GameNetworkingSockets
https://github.com/ValveSoftware/GameNetworkingSockets/blob/master/README_P2P.md
https://github.com/ValveSoftware/GameNetworkingSockets/blob/master/include/steam/steamnetworkingcustomsignaling.h

## Decentralized discovery / matchmaking direction

The direct invite solves the known-peer case. A larger public fabric needs a way to find currently available peers without one central AXM database.

Useful precedents:

- BitTorrent BEP 5 uses a Kademlia-style DHT for trackerless peer discovery, making participating nodes collectively provide peer location information.
- libp2p uses peer discovery, signed routing records, DHT/pubsub patterns and peer exchange; its AutoNAT work is also a useful reference for asking other peers whether a node is externally reachable.
- published research has demonstrated structured P2P matchmaking designs without a central matchmaking node.

References:
https://www.bittorrent.org/beps/bep_0005.html
https://github.com/libp2p/specs/blob/master/RFC/0002-signed-envelopes.md
https://github.com/libp2p/specs/blob/master/RFC/0003-routing-records.md
https://docs.libp2p.io/concepts/nat/autonat/
https://link.springer.com/article/10.1007/s12083-019-00725-3

AXM should not treat any one precedent as the answer. The research gates compare simpler and hybrid discovery strategies before selecting one.

## No blockchain requirement

The public fabric does not need permanent global consensus or a ledger of player presence.

Preferred state is signed and short-lived:

```text
peer/group routing record  -> minutes or longer, replaceable
presence ticket            -> seconds, expires automatically
match proposal             -> seconds, selected peers only
match state                -> session scoped
```

Only the participants in a proposed match need to agree on that match. The entire network does not need to vote.

## What v0.1 already proves

- invite generation is local;
- invite transfer can happen through any external messaging channel;
- invite decoding is local;
- game/build compatibility can be checked before joining;
- host/guest authenticate the join using the invite session key;
- actual reference-handshake traffic is direct;
- a failed direct route terminates instead of invoking paid fallback infrastructure.

## What is still research

- remembered cryptographic peer bonds;
- endpoint observation by community peers;
- automatic router mapping and beginner-safe repair guidance;
- public/private/federated groups;
- decentralized presence propagation;
- public P2P matchmaking;
- cold-start ignition peers;
- host-role fairness and rollback;
- coordinator migration;
- Internet-scale discovery and abuse resistance.

See:

- `PEER_FABRIC_ARCHITECTURE.md`
- `PEER_FABRIC_RESEARCH_GATES.md`

## Next adapter gate

The next practical engineering gate remains local endpoint exposure:

```text
HOST presses Host Multiplayer
  -> bind game UDP port
  -> try global IPv6
  -> try PCP / UPnP / NAT-PMP local router mapping
  -> optionally verify an observed external candidate with another peer
  -> if mapping succeeds, put candidate address+port in invite
  -> otherwise offer manual port-forward/direct address entry
  -> externally verify reachability
  -> produce one copyable invite
```

No public AXM service is required for that flow.
