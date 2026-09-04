# AXM Peer Fabric Research Gates

Status: **TEST PLAN — no gate below is claimed passed unless explicitly marked**

Date: 2026-09-04

This file turns the Peer Fabric idea into bounded experiments. It deliberately separates architectural possibility from measured implementation truth.

## Existing measured base

PR #3 currently has a local reference suite for the `AXMP2P1` direct-invite/admission layer. The existing lane reports 8/8 tests passing for invite handling, stable failure codes, localhost UDP host/guest handshake and the shooter-shaped game-facing admission seam.

That does **not** prove Internet NAT traversal, public discovery, matchmaking, fairness, host migration or production game transport.

## Gate 0 — freeze protocol invariants

Before adding distributed discovery code, write machine-readable schemas for:

- peer identity record;
- peer-bond consent receipt;
- group identity/policy;
- group membership capability;
- public presence ticket;
- discovery peer record;
- matchmaking proposal;
- match acceptance / lease;
- connectivity candidate;
- checkpoint acknowledgement.

Invariant tests:

1. signatures are domain-separated by record type;
2. canonical serialization produces identical bytes for identical state;
3. expired records are always rejected;
4. a record signed for one game/protocol cannot be replayed into another namespace;
5. network address is never treated as peer identity;
6. public presence contains no private-group roster by accident;
7. malformed/oversized records fail before expensive processing.

**Pass condition:** deterministic schema vectors and rejection vectors exist.

## Gate 1 — remembered peer bond

Extend direct invite with an optional explicit `Remember this peer` consent action.

Test:

```text
first invite
  -> peer identities verified
  -> both choose remember
  -> bond stored locally
  -> network address changes
  -> later reconnection authenticates identity, not old IP
```

Also test one-sided and two-sided revocation.

**Pass condition:** later authentication survives address change and revocation prevents automatic rebonding.

## Gate 2 — endpoint exposure + Router Helper

Build the local connectivity diagnoser separately from game logic.

Probe in order:

1. LAN;
2. global IPv6;
3. PCP;
4. NAT-PMP;
5. UPnP IGD if user permits;
6. manual-forward guidance.

Required receipts:

- method attempted;
- local port;
- external candidate if learned;
- router response;
- external verification result;
- rollback action/result.

Do not store router admin credentials.

Adversarial tests:

- router says mapping succeeded but external dial fails;
- device LAN IP changes;
- mapping expires;
- firewall still blocks;
- CGNAT;
- user cancels midway;
- rollback after successful map.

**Pass condition:** helper never reports `DIRECT_READY` solely from a local router success response; external reachability must be independently verified.

## Gate 3 — community peer as endpoint observer

Research a tiny peer-to-peer STUN-like function.

A reachable peer receives a bounded probe and returns the source transport address it observed.

Test with three nodes:

```text
A behind NAT
B behind NAT
C reachable observer
```

A and B each learn an observed candidate through C, exchange candidates through the existing signaling path and attempt simultaneous direct checks.

Critical boundary:

- C may exchange tiny signaling/observation messages;
- C must not carry gameplay bytes after direct connection succeeds;
- no success claim if A/B still require C for data.

**Pass condition:** at least one real cross-network topology demonstrates direct A<->B traffic after C is removed from the data path. Record failures as failures.

## Gate 4 — group permission model in simulation

Implement group semantics before Internet-scale transport.

Modes:

- `PRIVATE`
- `FEDERATED(allowlist)`
- `PUBLIC`

Property tests:

- private tickets never propagate outside group;
- federated tickets only cross approved group edges;
- public tickets may enter game-wide discovery;
- membership lists do not merge merely because discovery is federated;
- leaving/revocation prevents fresh tickets;
- old tickets expire naturally;
- public discovery does not expose a direct endpoint before connection consent.

**Pass condition:** exhaustive small-graph tests find zero scope leaks.

## Gate 5 — ignition peer / cold start

Start a fresh peer with exactly one known reachable ignition peer.

```text
new -> ignition -> peer set -> public overlay
```

Then kill the ignition peer.

Measure:

- introductions received;
- successful independent neighbor connections;
- bytes exchanged with ignition;
- whether public discovery continues after ignition disappears.

Repeat with multiple ignition sources and stale ignition addresses.

**Pass condition:** after bootstrap, the new peer can continue discovery without the ignition peer and no gameplay path depends on it.

## Gate 6 — public discovery overlay simulation

Do not begin with a million real sockets. Build a deterministic event simulator first.

Run at increasing sizes, for example:

- 100 peers;
- 1,000 peers;
- 10,000 peers;
- larger only when previous scales remain measurable.

Inject:

- joins;
- leaves;
- network partitions;
- reconnects;
- expired records;
- stale peer addresses;
- mixed public/private/federated groups.

Compare candidate strategies:

A. structured DHT only;
B. bounded gossip only;
C. DHT for slower peer/group location + gossip for short-lived presence.

Measure:

- discovery convergence time;
- lookup messages per peer;
- steady-state bytes per peer;
- stale-ticket rate;
- duplicate-record rate;
- memory per peer;
- recovery after churn/partition;
- graph degree distribution.

No strategy becomes CANON merely because it is conceptually elegant.

**Pass condition:** select only after measured trade-offs are recorded.

## Gate 7 — signed presence under abuse

Challenge the public overlay with hostile inputs:

- invalid signatures;
- replayed tickets;
- expired tickets;
- oversized tickets;
- one identity flooding tickets;
- many fresh Sybil identities;
- bogus peer-exchange records;
- eclipse attempts where one peer supplies only attacker-controlled neighbors.

Candidate defenses to measure:

- domain-separated signatures;
- strict TTL;
- per-peer publication budgets;
- local connection/message rate limits;
- peer-source diversity;
- random exploration;
- multiple-source lookup;
- local behavioral score with decay;
- bounded response sizes.

Do not invent proof-of-work/economic identity until measurements show it is needed.

**Pass condition:** attacks are measured with and without defenses, and no defense is described as solving Sybil identity globally unless it actually does.

## Gate 8 — decentralized matchmaking simulator

Build matchmaking on top of tickets without a central queue.

Scenario:

1. peers publish compatible/incompatible tickets;
2. local matchers discover candidates;
3. multiple peers may propose overlapping matches;
4. each participant may lease itself to at most one proposal;
5. successful proposal collects all required signed accepts;
6. failed/expired proposals disappear.

Test:

- simultaneous proposals;
- one peer vanishes during proposal;
- ruleset/version mismatch;
- high latency candidate rejected in favor of lower latency;
- party-size constraints;
- stale presence;
- duplicate proposal delivery;
- partitioned groups reconnecting.

Measure:

- time-to-match;
- proposal count per successful match;
- collision/busy rate;
- false match rate;
- abandoned lease rate;
- bytes per match formed.

**Pass condition:** no match starts without the required signed participant agreement, and the same deterministic event trace produces the same decision trace.

## Gate 9 — network-quality scoring

Measure candidate paths directly instead of trusting self-reported ping.

Inputs may include:

- RTT;
- jitter;
- packet loss;
- path reachability;
- recent stability;
- upload capacity only where relevant to the selected gameplay topology.

The selected host/coordinator should be a measured role, not a social privilege.

Test deliberately bad candidates and changing network conditions.

**Pass condition:** selection receipt explains why a coordinator/path won, using measured values.

## Gate 10 — host-advantage fairness harness

Create a deterministic game-neutral tick simulator before shooter integration.

Example synthetic peers:

```text
P1 coordinator: 0 ms local / 20 ms network to others
P2: 25 ms
P3: 45 ms
P4: 70 ms + jitter
```

Compare:

A. naive listen-server immediate-host authority;
B. shared tick acceptance window;
C. prediction + bounded rollback;
D. alternative topology if useful.

Measure:

- action acceptance timing by player;
- correction count;
- rollback depth;
- perceived/local response delay;
- late-input rejection;
- disagreement rate.

The target is to remove **host-role privilege**, not claim that physical latency differences disappear.

**Pass condition:** coordinator inputs follow the same canonical acceptance rule as remote inputs, and measurements show the remaining advantage is attributable to actual path latency rather than a special host code path.

## Gate 11 — coordinator migration

Build a tiny deterministic match state with checkpoints and an input log.

Failure injection:

- coordinator process stops cleanly;
- coordinator disappears without notice;
- coordinator network partition;
- replacement candidate also fails;
- peers disagree on last checkpoint hash.

Required behavior:

- elect replacement from a pre-measured candidate order;
- resume only from an agreed checkpoint/input boundary;
- never silently choose one divergent state as truth;
- if agreement cannot be restored, terminate with an explicit divergence result.

**Pass condition:** surviving peers either resume with identical hashes or fail explicitly; no hidden state rewrite.

## Gate 12 — real-network matrix

After simulation, test real consumer network combinations.

At minimum gather examples across:

- same LAN;
- separate home IPv4 NATs;
- IPv6-capable homes;
- mixed IPv4/IPv6;
- mobile hotspot;
- CGNAT;
- restrictive firewall;
- manual port forward;
- PCP/NAT-PMP/UPnP routers where available.

Record exact topology characteristics where safely observable.

**Pass condition:** publish the success/failure matrix. Do not turn the tested sample into a universal percentage claim.

## Gate 13 — shooter integration

Only after the lower network/fairness gates exist should the new shooter consume the expanded layer.

First shooter slice:

```text
Host / Join Friend
Public Group
Quick Match
Connection diagnosis
Direct session
```

Keep gameplay scope bounded to one small mode/map until transport, rollback and migration measurements are trustworthy.

**Pass condition:** measured game session under artificial packet loss/latency plus at least one real remote direct match. No relay traffic in the default path.

## Gate 14 — old-game resurrection test

Test the lifetime claim directly.

Take a build with all AXM-operated services absent.

Players receive only:

- the game;
- the Peer Fabric code;
- one social/group invite or community ignition peer.

Then prove whether they can form a public group, discover peers and play.

**Pass condition:** multiplayer still functions without contacting an AXM-owned domain/service.

## Gate 15 — third-party integration experiment

Only after the fabric is stable enough internally, integrate it into a tiny unrelated sample game.

Measure:

- code the game must write;
- platform-specific dependencies;
- required networking knowledge;
- failure diagnostics;
- time spent outside the game-state adapter.

This gate decides whether an SDK claim is deserved.

## Stop conditions / repair triggers

Pause expansion when any of these occur:

- public/private scope leak;
- unsigned state accepted as authenticated;
- gameplay silently relayed;
- ignition peer becomes mandatory after bootstrap;
- stale/expired presence creates matches;
- a coordinator can bypass fairness rules;
- host migration rewrites divergent state silently;
- benchmark result is being presented beyond the tested topology/scale.

Repair the failed gate before adding more layers.
