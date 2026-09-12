# AXM City Multiplayer — Foundation

Status: **FOUNDATION / HYPOTHESIS**  
Lane: `axm/chat-city-mesh-foundation-2026-09-02`

This document captures the founding architecture so later research can challenge, refine or measure it without silently replacing the original direction.

## 1. Problem statement

Modern multiplayer often centralizes more compute, state and delivery than is strictly necessary. AXM City Multiplayer explores the opposite direction:

> Let participant hardware compute the experience locally, and make shared infrastructure carry only the smallest verified information required for participants to agree on the same match.

The long-term target is a free-to-use city multiplayer fabric that can be built from modest dedicated hardware rather than requiring a datacenter-scale service.

That target is **not yet proven**.

## 2. Physical network root

The city fabric uses dedicated fixed nodes.

Participant phones, laptops, consoles and PCs are endpoints. They are not expected to provide opportunistic routing for the city backbone.

Why:

- mobile devices leave the area,
- batteries and background limits make them poor infrastructure,
- operating-system behavior is not a stable routing contract,
- user consent is clearer when infrastructure is a deliberate physical node,
- fixed nodes can use better placement, antennas, power and thermal design.

### Opt-in signal spots

Coverage grows because people or places voluntarily host serious fixed nodes:

```text
home / roof      AXM node ●────● AXM node      shop
                               |
community site   AXM node ●────● AXM node      apartment
                               |
                          player clients
```

The volunteer is agreeing to host infrastructure. Installing an AXM game does not silently make a personal device a relay.

## 3. Node classes

Do not assume every node needs the same hardware.

### Access / Street Node

Purpose:

- connect nearby player devices,
- route city traffic,
- maintain local node health,
- potentially perform light integrity or admission checks.

Optimization target: low cost, stable 24/7 operation, good usable coverage and enough concurrency for its local cell.

### Relay / Bridge Node

Purpose:

- connect cells across longer or strategically important paths,
- sit at strong physical locations such as roofs or elevated sites,
- prioritize radio/routing quality over game compute.

### Match / Truth Node

Purpose:

- order authoritative events,
- validate legal state transitions,
- retain bounded replay/checkpoint evidence,
- perform state-hash comparison and repair,
- coordinate match admission based on real load.

It does not need to render the game.

### Core Node

Optional stronger node for:

- many simultaneous match coordinators,
- city-wide indexes or discovery metadata,
- leaderboard aggregation,
- replicated checkpoints,
- other services proven to benefit from concentration.

The architecture must not assume a core node is required for every local match.

## 4. Radio/network candidates

No radio is CANON yet.

### Bluetooth LE / Bluetooth Mesh

Potential role:

- tiny discovery/control messages,
- provisioning/supporting traffic,
- low-rate presence or health signaling.

Not currently assumed to be the primary realtime gameplay backbone.

### Wi-Fi Aware

Potential role:

- direct nearby client connectivity without requiring internet or a traditional access point,
- secure local peer/service discovery where platform support permits it.

Android and modern Apple platforms expose Wi-Fi Aware APIs, making this worth future client-side testing.

### Wi-Fi Direct / infrastructure Wi-Fi

Potential role:

- compatibility paths for direct/local connectivity,
- ordinary household LAN play,
- access-node client attachment where that is simpler than newer peer technologies.

### 802.11s-style fixed mesh + routing

Potential role:

- dedicated node-to-node multi-hop city transport,
- cells connected through multiple fixed routes rather than one giant city transmitter.

Routing candidates must be measured under real topology changes, interference and congestion. A protocol name is not proof of usable city multiplayer.

### Wi-Fi HaLow / 802.11ah

Potential future role:

- longer fixed hops or lower-frequency urban links if legal European spectrum rules, available hardware and measured throughput/latency justify it.

Do not copy US range claims into a Netherlands design without local regulatory and field validation.

## 5. QR / bootstrap model

The network does not have to advertise itself as a conventional public Wi-Fi network.

A QR or equivalent out-of-band bootstrap can provide the information needed to join or discover the correct service/network.

Possible contents:

```text
network / fabric ID
root public key
protocol version
rendezvous information
join credential or scoped token
```

The QR is an invitation/bootstrap mechanism, not the security boundary.

Important distinction:

> Not publicly listed is not the same as physically undetectable.

Radio traffic can still be observed by capable equipment. Authentication, encryption and cryptographic identity provide security. A hidden SSID or quiet advertisement does not.

## 6. Local compute inversion

The player's device should do the expensive experiential work whenever deterministic agreement permits it:

- rendering,
- animation,
- audio,
- UI,
- world generation,
- deterministic physics,
- deterministic NPC/game logic,
- local asset use.

Shared infrastructure should carry the causes and verified state that participants must agree on.

Conceptual event:

```text
match_id
tick
player_id
input/event
sequence
signature
```

Conceptual verification:

```text
STATE_HASH tick=N hash=...
```

If participants agree, do not transmit a representation of the whole world merely because it is visually complex.

### Target equation

```text
shared rules
+ shared seed
+ ordered input/events
+ authoritative state changes
+ periodic hashes
+ bounded checkpoints / repair
= same resulting match state
```

The amount of network traffic this can actually save is a **measurement question**.

## 7. Match admission by truth gate

Do not hardcode marketing claims such as “one node supports 500 matches.”

A node should admit work only while measured conditions remain inside tested bounds.

Conceptual gate:

```text
MATCH_ALLOWED =
    CPU_p95            < cpu_budget
AND memory_residency   < memory_budget
AND radio_airtime      < airtime_budget
AND packet_loss        < loss_limit
AND jitter             < jitter_limit
AND latency            < latency_limit
AND state_integrity    == valid
```

Real thresholds must come from experiments.

## 8. Cell-based city architecture

A city should not be treated as one giant broadcast domain.

Prefer local cells and explicit bridges:

```text
[West cell] ----\
                 +---- district/city routing
[Centre cell] ---+
                 |
[North cell] ----/
```

A match between nearby players should remain local when possible. City-wide metadata can be tiny while game traffic follows only the paths that need it.

The geographic size of the city is therefore only one scaling variable. Others include:

- node density,
- hop quality,
- interference,
- traffic per match,
- match locality,
- routing overhead,
- deterministic compression/reconstruction,
- compute required for truth gates.

## 9. Accounts and data

“No mandatory cloud account” does not mean “accounts are forbidden.”

Accounts can add:

- username and avatar,
- achievements,
- stats,
- friends,
- teams/clans,
- rankings,
- match history,
- persistent shared-world identity.

Default direction:

- keep primary player data on the user's own device,
- use portable/cryptographic identity where practical,
- synchronize only what a shared feature genuinely requires,
- avoid making an account a paywall or artificial access gate.

A future identity could prove continuity through a public/private key pair without requiring AXM to collect a real name, phone number or home address.

## 10. Household LAN independence

AXM games should preserve conventional local networking.

A household can run:

- local cooperative games,
- local versus,
- local servers,
- private mods/rules,
- direct device-to-device or router LAN sessions.

City-network integrity state does not disable this.

Root boundary:

> Your hardware, your private LAN, your rules. Shared AXM human matchmaking, shared integrity rules.

## 11. Integrity and cheating

AXM does not assume cheating or hacking can be perfectly prevented.

Instead, design for:

1. authoritative evidence capture,
2. deterministic or otherwise reproducible replay,
3. objective rule/state checks,
4. optional AI-assisted investigation,
5. explicit routing consequences when the violation is verified.

### AI is not the conviction boundary

AI can:

- inspect replay,
- detect suspicious patterns,
- summarize evidence,
- compare behavior against known legal state space,
- help humans or deterministic checks find the relevant window.

AI alone does not establish cheating.

### No ownership-style ban requirement

The intended response is state/routing based:

```text
NORMAL HUMAN MATCH ROUTING
        |
        | verified integrity violation
        v
ANOMALY / AI MATCH ROUTING
```

A player/network boundary can still:

- join the AXM fabric where technically allowed,
- access games/resources that are not human competitive matchmaking,
- play private LAN games,
- play AI/anomaly matches.

It loses human-match trust at the city-network boundary selected by the integrity policy.

### Access-point / signal containment

If a verified cheated match originates through a particular city-network signal/access boundary, that boundary may lose human matchmaking trust.

AXM does not need to determine whether the person was:

- the node owner,
- a child,
- another household member,
- a friend visiting,
- some other authorized user of that local connection.

The truthful claim is only that a verified integrity violation was carried through that boundary.

This policy is intentionally strict because the city multiplayer service is a free shared commons, not a purchased entitlement or manual support contract.

Do not silently expand that statement into an accusation against every person at the physical location.

### Cheater / anomaly matches as content

A quarantined identity/access route can be matched against AI opponents or explicit anomaly modes instead of human players.

Those modes may deliberately turn cheating behavior into playful game mechanics, ridiculous cosmetics or adversarial AI responses, provided the system:

- does not pretend the AI is a human player,
- does not expose real-world identity,
- does not encourage harassment or doxing,
- keeps the consequence inside the game/network context.

## 12. First-entry notice

Players should see the integrity rule before their first city human match.

The notice should be short and understandable. It should explain that AXM is not promising perfect cheat prevention and that verified manipulation changes human matchmaking eligibility/routing.

The acknowledgement can be retained as a small versioned receipt so the rule is not retroactively rewritten.

See `FIRST_JOIN_INTEGRITY_NOTICE.md`.

## 13. Cost philosophy

The project is specifically interested in whether city multiplayer can be built at ordinary-person/hobbyist infrastructure cost.

Do not assume cheapness. Measure it.

Useful future score:

```text
NODE_VALUE =
usable_coverage
* real_throughput
* reliability
* concurrent_capacity
---------------------------------
hardware_cost + measured_power_cost
```

Other penalties must include interference, hop latency, packet loss, maintenance and placement constraints.

Four cheap well-placed nodes may outperform one expensive long-range node. That is a field question, not an axiom.

## 14. What is explicitly unproven

As of this foundation:

- no chosen city-node hardware,
- no proven Tilburg coverage map,
- no measured match traffic budget,
- no proven concurrent match count,
- no validated cross-platform deterministic engine,
- no implemented city mesh,
- no validated QR bootstrap protocol,
- no production identity protocol,
- no implemented replay conviction gate,
- no validated AI cheater opponent,
- no established regulatory configuration for long-range radios.

These are the work, not missing footnotes.

## 15. External starting references

Official/primary starting points to verify during implementation:

- Android Wi-Fi Aware: https://developer.android.com/reference/android/net/wifi/aware/package-summary
- Android Wi-Fi Direct: https://developer.android.com/develop/connectivity/wifi/wifip2p
- Apple Wi-Fi Aware: https://developer.apple.com/documentation/WiFiAware
- Bluetooth Mesh primer: https://www.bluetooth.com/bluetooth-mesh-networking-primer/
- Linux wireless 802.11s: https://wireless.docs.kernel.org/en/latest/en/developers/documentation/ieee80211/802.11s.html

Keep future citations close to the claims they support, especially for radio range, legal power limits and device compatibility.