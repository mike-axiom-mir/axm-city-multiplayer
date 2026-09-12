# AXM City Multiplayer — Research Gates

Status: **FOUNDATION / NOT YET MEASURED**

This file converts the city-multiplayer idea into gates. A later chat may claim progress only when it can attach retained evidence to the relevant gate.

## Gate 0 — Lane integrity

Before technical work:

- current chat owns exactly one PR lane,
- scope is written in the PR,
- no sibling implementation branch is created for the same chat,
- deferred ideas are logged rather than silently implemented elsewhere.

Pass condition: repo history clearly shows one bounded lane for the working chat.

## Gate 1 — Candidate node inventory

Goal: find the cheapest serious fixed hardware worth field testing.

For every candidate retain:

- exact model/revision,
- radio chipset(s),
- supported bands/standards,
- antenna configuration and legal configuration options,
- Ethernet capability,
- CPU/RAM/storage,
- idle and loaded power draw,
- purchase price including required adapters/antennas,
- operating-system/driver support,
- availability in the Netherlands/EU,
- expected maintenance/replacement difficulty.

Do not rank by advertised range alone.

## Gate 2 — Netherlands radio legality

Goal: make every field test legal for the actual band/configuration being used.

For each radio mode establish:

- allowed frequency range,
- permitted effective radiated power,
- channel-width constraints,
- DFS/listen-before-talk/duty-cycle requirements where applicable,
- indoor/outdoor restrictions,
- antenna/gain implications,
- whether the exact test needs a licence or may operate licence-free.

Pass condition: retained primary-source regulatory references map to the exact hardware configuration used in field testing.

## Gate 3 — Single-hop urban RF truth

Measure each candidate in real city conditions, not only open-field line-of-sight.

Test classes:

- same room/building,
- through one exterior wall,
- street-level line of sight,
- street-level obstructed,
- elevated/roof-to-roof where permission exists,
- rain/wet conditions if materially relevant,
- daytime/evening interference periods.

Retain:

- distance,
- approximate environment/topology,
- RSSI/SNR where available,
- negotiated PHY rate,
- real application throughput,
- latency p50/p95/p99,
- jitter,
- packet loss,
- reconnect/recovery behavior,
- power draw during test.

Pass condition: node range is described as a measured envelope, not a marketing number.

## Gate 4 — Multi-hop mesh truth

Goal: establish whether fixed nodes can relay city traffic without latency or loss exploding.

Test at minimum:

- 1 hop,
- 2 hops,
- 3 hops,
- 5 hops,
- alternate-path failover,
- one node disappearing mid-session,
- congested intermediate node,
- mixed-quality links.

Retain per-hop and end-to-end:

- latency,
- jitter,
- loss,
- throughput,
- convergence/failover time,
- CPU/RAM load,
- routing overhead,
- airtime/channel utilization.

Pass condition: a defined topology stays within the multiplayer traffic budget from Gate 7.

## Gate 5 — Cell architecture

Goal: avoid one giant city broadcast domain.

Prototype at least two local cells connected by a bridge.

Verify:

- local-local match traffic stays local when possible,
- only required cross-cell state crosses the bridge,
- city discovery metadata remains bounded,
- failure of one cell does not unnecessarily collapse another,
- routing tables/state remain manageable as node count grows.

## Gate 6 — Deterministic game kernel

Goal: prove two heterogeneous participant machines can derive the same match state from the same starting state and ordered events.

Test:

- identical hardware first,
- different CPU families,
- different operating systems where supported,
- different frame rates,
- network jitter and delayed event delivery,
- pause/reconnect/replay,
- long-duration drift.

Retain:

- shared seed/rules version,
- event stream,
- per-tick or periodic hashes,
- first divergence tick if any,
- exact repair path.

Pass condition: the selected kernel reproduces exact agreed state under the declared platform set or explicitly bounds nondeterministic components outside the authoritative state.

## Gate 7 — Minimum match traffic

Goal: answer the key question: **how little shared information is actually required?**

Instrument real prototype matches.

Measure separately:

- player input/event bytes,
- protocol framing,
- signatures/authentication,
- authoritative deltas,
- hash traffic,
- checkpoint traffic,
- repair traffic,
- discovery/control traffic,
- retransmission/error overhead.

Retain:

- bytes/sec p50/p95/p99 per player,
- bytes/sec per match,
- packets/sec,
- burst size,
- behavior during intense game moments,
- behavior during repair.

Do not use toy arithmetic as a capacity claim after this gate exists.

## Gate 8 — Match/truth node compute cost

Goal: determine how many matches a modest machine can coordinate when it does not render them.

Measure:

- CPU p50/p95/p99,
- peak and resident RAM,
- storage/checkpoint writes,
- network I/O,
- cryptographic verification cost,
- replay/integrity cost,
- thermal/power behavior.

Scale concurrent matches until a defined admission threshold is reached.

Pass condition: publish the measured capacity **with the exact game workload, hardware and thresholds**, never as a universal match count.

## Gate 9 — Live admission gate

Implement a node admission decision based on measured limits rather than a fixed marketing number.

Candidate inputs:

```text
CPU_p95
memory residency
radio airtime
packet loss
jitter
latency
queue depth
state-integrity health
checkpoint/repair pressure
```

Verify that a node rejects or redirects new work before existing matches exceed accepted quality limits.

## Gate 10 — QR/bootstrap and trust

Goal: make first entry simple without pretending obscurity is security.

Prototype a QR/out-of-band bootstrap carrying only the data required to find and authenticate the intended fabric/service.

Verify:

- no secret is exposed unnecessarily,
- credentials can be scoped/versioned/revoked where required,
- a scanner without authorization cannot impersonate a trusted node,
- network identity can be verified cryptographically,
- joining does not silently authorize the user's device as infrastructure.

## Gate 11 — Local-first player identity

Goal: support fun accounts without central ownership becoming mandatory.

Prototype:

- local profile,
- stats/achievements,
- cryptographic identity,
- portable/exportable state,
- device migration,
- optional shared leaderboard proof.

Measure how little central/city state is actually required.

Pass condition: losing a central service does not erase the user's local identity/profile data.

## Gate 12 — Private LAN independence

A city-network failure or quarantine must not break ordinary private LAN play.

Test:

- city nodes offline,
- no internet,
- no account service,
- city human-match trust removed,
- household router only,
- direct local connection where supported.

Pass condition: local cooperative/versus sessions still function according to the game's declared LAN requirements.

## Gate 13 — Record/replay integrity evidence

Goal: capture enough authoritative evidence to reproduce a suspected manipulation without recording unnecessary personal data.

Verify:

- event ordering is retained,
- relevant state transitions are reconstructible,
- evidence is signed/hashed as needed,
- exact rules/version are identifiable,
- replay can reproduce the disputed interval,
- evidence retention is bounded,
- clean matches do not accumulate infinite logs.

## Gate 14 — Objective cheat proof

Start with cheats that violate mathematically defined state/rule limits.

Examples suitable for an early deterministic gate:

- impossible movement transition,
- illegal fire rate,
- impossible inventory/ammunition transition,
- invalid cooldown,
- unauthorized state mutation,
- fabricated sequence/event signature.

Pass condition: the same retained evidence reproduces the violation and a clean legal trace does not trigger the same rule.

Statistical/behavioral detections such as aim assistance require separate confidence research and must not be silently treated as mathematical certainty.

## Gate 15 — AI-assisted replay review

AI is a reviewer/helper, not the truth source.

Test whether an isolated AI review session can:

- locate suspicious intervals,
- explain objective violations,
- correlate multiple evidence streams,
- distinguish confirmed facts from suspicion,
- produce a concise machine-readable finding.

Compare AI findings against deterministic ground truth where available.

Retain false-positive and false-negative measurements.

## Gate 16 — Integrity routing / anomaly matchmaking

Implement the intended containment policy:

```text
trusted city human-match route
        -> verified integrity violation
        -> human-match trust removed at selected boundary
        -> AI/anomaly matchmaking route
```

Verify:

- the route change is deterministic and auditable,
- human players are not silently mixed into anomaly matches,
- the player can still access allowed non-human network functions,
- private LAN play remains unaffected,
- the system does not claim more about household/person identity than evidence supports.

## Gate 17 — Evasion pressure

Test cheap evasion attempts only after Gate 16 works.

Examples:

- new local player profile,
- reconnect/session rotation,
- repeated cheating from the same city access boundary,
- device changes,
- protocol replay/spoof attempts.

The goal is not perfect attribution of a human being. The goal is to protect human matchmaking with the minimum reliable trust boundary.

Do not collect invasive personal identity merely to make evasion harder.

## Gate 18 — AI/anomaly opponent

Prototype an explicitly non-human opponent/mode for quarantined routing.

Requirements:

- clearly identified as AI/anomaly play,
- capable of providing a playable match,
- may use deliberately exaggerated mechanics as game content,
- does not masquerade as a human opponent,
- does not expose or shame real-world personal identity.

Measure whether this mode can absorb quarantined traffic without harming normal match capacity.

## Gate 19 — Cost model

For each deployment prototype retain:

### Capital

- node hardware,
- antennas,
- mounts/enclosures,
- cabling/power supplies,
- optional batteries/UPS,
- installation materials.

### Running

- measured watts/node,
- local electricity assumption,
- replacement/maintenance assumptions,
- any connectivity/service costs actually required.

Calculate at minimum:

```text
EUR per useful covered area
EUR per concurrent accepted match
EUR per active player under test workload
watts per accepted match
```

Do not hide donated hardware or volunteer hosting from the model. Record them as such.

## Gate 20 — Small real-world pilot

Only after the earlier gates establish a viable path.

Suggested progression:

1. room/building,
2. two nearby fixed sites,
3. small street cluster,
4. several-cell neighborhood pilot,
5. larger district,
6. city-scale experiment only if measurements justify it.

At each level define a rollback condition before deployment.

## Gate 21 — Public claim gate

Before README/marketing language may say a capability is real, require retained evidence for the exact claim.

Examples:

- “works without internet” requires an offline run,
- “supports N matches” requires measured N under a named workload,
- “covers X distance” requires measured legal configuration and environment,
- “detects cheat Y” requires replayable evidence and false-positive testing,
- “city-scale” requires a real city-scale or defensibly representative deployment, not extrapolation alone.

## Deferred research questions

These are intentionally recorded rather than spread into new PR lanes:

- exact dedicated-node hardware shortlist,
- EU Wi-Fi HaLow availability and regulatory fit,
- best fixed-mesh routing protocol for the chosen radios,
- cross-platform deterministic simulation strategy,
- cryptographic portable identity format,
- account/stat replication model,
- exact replay retention budget,
- anomaly/AI opponent design,
- leaderboard trust and anti-forgery,
- neighborhood/city discovery protocol,
- node-placement optimization,
- redundancy when a volunteer signal spot disappears,
- software update distribution without turning the city fabric into a cloud dependency.

A future chat should claim one of these as a bounded PR lane rather than trying to solve all of them at once.