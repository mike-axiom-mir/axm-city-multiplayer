# AXM Peer Fabric Resilience Gates

Status: **TEST PLAN — no gate below is claimed passed**

Date: 2026-09-05

These gates preserve the connection-smoothness and low-bandwidth principles from the multiplayer design discussion. They complement `PEER_FABRIC_RESEARCH_GATES.md` rather than replacing it.

## R1 — Low-bandwidth budget harness

Create a game-neutral transport harness that can impose explicit upload/download ceilings.

Start with example profiles such as:

- 1 Mbps upload;
- 2 Mbps upload;
- 5 Mbps upload;
- unrestricted local baseline.

Record separately:

- gameplay payload bytes;
- protocol/header/encryption overhead;
- discovery/signaling bytes;
- repair/retransmit bytes;
- checkpoint bytes.

**Pass condition:** the harness produces deterministic traffic receipts and shows exactly which subsystem consumes the budget. No per-game bandwidth claim is made from the harness alone.

## R2 — Bad-network adversity matrix

Inject controlled network faults:

- 100 ms base latency;
- variable jitter;
- 1%, 3% and 5% packet loss;
- duplicate packets;
- out-of-order packets;
- burst loss;
- short stalls;
- asymmetric latency where supported.

Measure:

- state divergence;
- correction rate;
- rollback depth;
- disconnect rate;
- useful payload vs repair overhead;
- perceived/local response timing in the synthetic fairness client.

**Pass condition:** every failure mode is explicit and reproducible; no silent state rewrite is used to make the test look smooth.

## R3 — Temporary disconnect / reconnect

With a valid remembered peer bond and an active match, interrupt the data path for bounded periods such as 1, 3 and 5 seconds.

Test:

```text
connected
 -> path disappears
 -> liveness detects failure
 -> direct candidates retried
 -> peer identity re-authenticated
 -> agreed checkpoint/input boundary restored
 -> resume OR explicit terminal failure
```

The reconnect must not create a new permanent trust relationship or widen discovery scope.

**Pass condition:** both peers either resume on identical canonical state or fail explicitly.

## R4 — Address and port change

Change the public endpoint while preserving the same peer identity.

Cases:

- NAT mapping changes port;
- public IPv4 changes;
- IPv6 prefix/address changes where testable;
- stale candidate remains in local cache.

**Pass condition:** identity survives address change, stale candidates expire, and the software never treats the new address itself as proof of peer identity.

## R5 — Interface/path migration

Where the platform/transport permits, test a live peer changing network interface or preferred route.

Example:

```text
Wi-Fi path active
 -> Ethernet becomes available
 -> candidate measured
 -> path migrates or reconnects
```

Also test the inverse and abrupt loss of the preferred interface.

**Pass condition:** migration is authenticated and scope-preserving, or fails explicitly without corrupting match state.

## R6 — Multiple-candidate resilience

Give peers multiple candidate paths and deliberately break the currently selected one.

Measure:

- time to detect loss;
- time to usable alternate path;
- duplicate/late packet handling;
- whether canonical state remains identical;
- whether a Router Helper action is requested only when genuinely needed.

**Pass condition:** the system does not unnecessarily restart the whole social/matchmaking flow when another already-authorized direct path remains viable.

## R7 — Bandwidth-pressure topology selection

Compare gameplay topology under the same synthetic game traffic:

- full mesh;
- single coordinator/star;
- bounded tree/hybrid candidate.

Run at increasing player counts and varying host upload caps.

Measure per-peer and worst-peer bandwidth, latency path length, coordinator load and failure impact.

**Pass condition:** topology choice is backed by measured receipts rather than a universal assumption that mesh or host-star is always best.

## R8 — Historical validation / bounded rewind

For a game-neutral hit/action model, retain a bounded recent state history and compare:

1. judge only at packet-arrival state;
2. judge against the validated historical tick at which the action occurred;
3. bounded rollback/replay variant.

Test both coordinator and remote players under different RTTs.

**Pass condition:** the coordinator does not receive a unique validation shortcut, rewind is capped/versioned, and the harness reports the trade-off between fairness and accepting stale actions.

## R9 — Do not equalize to the worst connection blindly

Compare:

- artificial delay applied to all peers to match the worst RTT;
- local prediction + shared canonical acceptance rules;
- bounded fairness window with rejection beyond the window.

**Pass condition:** retain only a design whose measured fairness improves without unnecessarily forcing every low-latency peer to feel like the worst connection.

## R10 — Coordinator loss under adversity

Combine coordinator migration with:

- packet loss;
- high jitter;
- temporary partition;
- stale checkpoint acknowledgement;
- candidate replacement failure.

**Pass condition:** surviving peers resume only from an agreed state boundary or terminate explicitly. No coordinator is allowed to invent a new canonical state because migration became inconvenient.

## R11 — AI ignition peer independence

Use an AI-gamer-wrapped ignition peer to bootstrap a fresh client, then remove it completely.

Verify:

- discovery continues through ordinary peers;
- matchmaking remains possible;
- gameplay does not route through the AI ignition peer;
- a second compatible community peer can replace the AI bootstrap role;
- optional AI-opponent gameplay is a separate game feature from the bootstrap protocol.

**Pass condition:** removing the AI does not collapse an already bootstrapped public fabric.

## R12 — Long-idle wake / old-game path

Simulate the public fabric being absent for a long interval, then restart with only a small set of old clients and one valid social/group/ignition entry route.

Verify:

- stale discovery records are rejected;
- peers can rebuild a fresh overlay;
- no AXM service is required to restore public discovery;
- direct matches can form if current network topology permits.

This complements the old-game resurrection gate by specifically testing stale network state and re-ignition.

## Stop conditions

Repair before expanding when any of these occur:

- reconnect authenticates an address instead of peer identity;
- path migration widens consent/discovery scope;
- low-bandwidth tests are passed only by dropping canonical events without explicit policy;
- fairness depends on a hidden coordinator shortcut;
- rollback/rewind is unbounded;
- a temporary network fault silently rewrites divergent state;
- ignition AI remains necessary after peers are independently connected.
