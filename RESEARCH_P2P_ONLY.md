# Research: P2P-only multiplayer without AXM-funded infrastructure

## Decision

For free/local AXM games, the default online path is player-hosted direct peer-to-peer.

No AXM relay, rendezvous, gameplay proxy, or dedicated-server service is required by the default core.

## Important networking truth

Classic UDP/TCP hole punching is often described as peer-to-peer, but the common Internet pattern still uses a publicly reachable introducer/rendezvous service so peers can discover their externally mapped endpoints and coordinate the simultaneous connection attempt.

Reference: RFC 5128, *State of Peer-to-Peer (P2P) Communication across Network Address Translators (NATs)*.
https://www.rfc-editor.org/rfc/rfc5128

Because this project is intentionally avoiding an AXM-operated service dependency, rendezvous-assisted hole punching is not part of the default v0.1 path.

## Serverless reachable-host path

The host needs an endpoint the guest can actually reach.

Preferred possibilities:

1. globally reachable IPv6 plus an allowed firewall rule;
2. an explicit router/NAT port mapping;
3. a user-created manual port-forward;
4. otherwise fail as `DIRECT_CONNECTION_UNAVAILABLE`.

PCP is a standards-track protocol designed to let applications create mappings for inbound communication through NAT/firewall devices, including short-lived uses such as games. The resulting external address/port can then be communicated to the remote peer through the AXM invite.

Reference: RFC 6887, *Port Control Protocol (PCP)*.
https://www.rfc-editor.org/rfc/rfc6887

UPnP IGD is another widely deployed local-router mechanism. MiniUPnP is one implementation that can query the external address and add/delete port mappings without any AXM cloud service.

Reference implementation:
https://github.com/miniupnp/miniupnp

## Production transport direction

The Python UDP code in this repository is intentionally a reference handshake, not final game netcode.

For native games, a strong candidate adapter is Valve's open-source GameNetworkingSockets. The open-source project can be used without Steam and provides reliable/unreliable UDP messaging, fragmentation/reassembly, encryption, and direct IPv4 examples. AXM does not need Steam Datagram Relay for the direct-IP path.

Reference:
https://github.com/ValveSoftware/GameNetworkingSockets

## What v0.1 proves

- invite generation is local;
- invite transfer can happen through any external messaging channel;
- invite decoding is local;
- game/build compatibility can be checked before joining;
- host/guest authenticate the join using the invite session key;
- actual traffic is direct;
- a failed direct route terminates instead of invoking paid fallback infrastructure.

## Next adapter gate

The next practical engineering gate is local endpoint exposure:

```text
HOST presses Host Multiplayer
  -> bind game UDP port
  -> try global IPv6
  -> try PCP / UPnP / NAT-PMP local router mapping
  -> if mapping succeeds, put external address+port in invite
  -> otherwise offer manual port-forward/direct address entry
  -> produce one copyable invite
```

No public AXM service is required for that flow.
