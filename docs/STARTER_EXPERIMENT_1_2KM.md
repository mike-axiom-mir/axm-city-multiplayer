# AXM City Multiplayer — Cheapest Credible 1–2 km Starter Experiment

**Research date:** 2026-09-02  
**Lane:** `axm/chat-city-mesh-foundation-2026-09-02`  
**Truth state:** `RESEARCHED_NOT_FIELD_MEASURED`  
**CANON state:** `NOT_CANON`  

## Decision

The cheapest credible first experiment is **not** a city-wide access point, a server farm, a phone relay mesh, or a full 802.11s deployment.

It is one fixed **5 GHz directional point-to-point link** joining two small local LAN islands across approximately 1–2 km:

```text
existing laptop / local AP
          |
       Ethernet
          |
 directional radio A
          ))) 1–2 km (((
 directional radio B
          |
       Ethernet
          |
existing laptop / local AP
```

Each end uses a dedicated outdoor radio. Phones and computers connect only at short local range or by Ethernet. They do not carry the city backbone.

This single segment is enough to test the central AXM hypothesis:

> Can two independently running game clients remain in exact verified agreement across a cheap, local-only metropolitan radio link while exchanging only ordered state-changing information, hashes, and bounded repair data?

## Purchase recommendation

**Recommended first pair:** two MikroTik `SXTsq 5 ax` units.

Why this pair currently wins the starter decision:

- approximately €55–€65 per unit in current European/Dutch listings;
- current Wi-Fi 6 hardware rather than an old stock experiment;
- 16 dBi directional antenna;
- Gigabit Ethernet;
- AP mode and station/CPE use;
- RouterOS level 4;
- weatherproof enclosure;
- power adapter, Gigabit passive-PoE injector, and hose clamp included;
- maximum stated power draw of 6 W each;
- manufacturer reports field testing to 3 km in high-interference urban conditions, while explicitly not defining that as a guaranteed throughput result.

**Expected radio-pair cost:** approximately **€110–€137** before shipping.

**Expected practical experiment total, reusing existing computers and suitable mounting points:** approximately **€145–€205**.

The total includes the radio pair, two outdoor Ethernet runs, and optionally grounded surge protection. It excludes paid rooftop labour, a new mast, landlord permission costs, and any new client computers because none are required for the first proof.

## The absolute price floor

Two MikroTik `SXTsq Lite5` units can reduce the radio-pair price to roughly **€84–€95** from current Dutch listings, and some cross-border listings advertise lower pre-shipping prices.

They are enough for the experiment because AXM state traffic should be tiny relative to even a 100 Mbps Ethernet port. However, they are Wi-Fi 4 devices with 10/100 Ethernet, 64 MB RAM, and RouterOS level 3.

The saving versus the `SXTsq 5 ax` pair is normally only about €25–€45. That is too small to justify buying the older floor model unless:

1. the budget is absolutely fixed;
2. a used or borrowed matched pair is available very cheaply; or
3. this is knowingly treated as disposable proof hardware.

## The cheapest path of all

Before buying, try to borrow or buy a matched used pair of known outdoor CPE radios with both PoE injectors and power supplies.

A current Marktplaats search showed a used Ubiquiti NanoBeam 5AC Gen2 listing around €45 per unit. Listings are volatile and are not a dependable budget baseline.

A used pair is only a bargain if all of the following are true:

- both units are the same compatible generation;
- both boot and reset normally;
- the correct PoE injectors and power supplies are included;
- Ethernet ports negotiate correctly;
- regulatory country settings remain available;
- DFS is functional;
- enclosures and cable glands are undamaged;
- the seller has not locked management credentials;
- there is no corrosion or water ingress.

Set a hard rule: if a questionable used pair approaches the price of two new `SXTsq 5 ax` units, buy the new pair.

## Costed configurations

Prices are observed market ranges on 2026-09-02, not promises. Shipping and VAT presentation differ by seller.

| Configuration | Radios | Approx. pair price | Practical first total | Main trade-off |
|---|---|---:|---:|---|
| Borrowed matched pair | known 5 GHz outdoor CPE | €0–€70 | €30–€130 | cheapest, condition unknown |
| Absolute new floor | 2 × SXTsq Lite5 | €84–€95 | €115–€170 | old Wi-Fi 4, 100 Mbps Ethernet |
| **Recommended** | **2 × SXTsq 5 ax** | **€110–€137** | **€145–€205** | best current value |
| More urban link margin | 2 × LiteBeam 5AC | €118–€156 | €175–€230 | 23 dBi, larger, proprietary airMAX |
| Strong Wi-Fi 6 margin | 2 × LHG 5 ax | €174–€182 | €230–€260 | 24.5 dBi, larger dishes |
| 60 GHz comparison | Wireless Wire Cube Pro pair | about €250+ | €290+ | fast, weather-sensitive, unnecessary for first proof |

## Minimum bill of materials

### Reused at zero new cost

- two existing laptops, PCs, mini-PCs, or other Ethernet-capable hosts;
- one existing router or access point at either end only if local wireless clients are desired;
- mains power at both fixed locations;
- ordinary short indoor Ethernet patch leads where already available.

The first proof can connect one computer directly to each PoE injector. A Raspberry Pi, dedicated server, cloud instance, and managed switch are not required.

### New material for the recommended build

| Item | Quantity | Observed/estimated cost | Notes |
|---|---:|---:|---|
| MikroTik SXTsq 5 ax | 2 | €110–€137 total | power supply, Gigabit PoE injector, clamp included |
| UV-resistant outdoor Cat6, 15–20 m | 2 | €25–€45 total | choose 100% copper for a permanent run |
| Additional pole/window brackets | 0–2 | €0–€40 | zero when an appropriate railing/pole exists |
| Gigabit Ethernet surge protector | 0–2 temporary; 2 permanent | €0–€32 total | protection requires a proper earth connection |
| Drip-loop/weatherproof cable details | as needed | €0–€15 | do not leave water a path indoors |

### Realistic totals

```text
bare but credible supervised proof:
€110–€137 radios
+ €25–€45 cable
= €135–€182 before shipping

better protected fixed install:
€135–€182
+ roughly €30 surge protection
+ mounting details where needed
= approximately €165–€225
```

The headline planning range remains **€145–€205** where shipping, cable length, and already-owned materials balance out. A difficult rooftop can cost more than the radios. Site access is the actual budget dragon.

## What “1–2 km reach” means

The first proof should mean:

> A reliable fixed link between two dedicated nodes located 1–2 km apart.

It should **not** mean:

> One giant transmitter directly serving ordinary phones throughout a 1–2 km radius.

A high-mounted radio may be able to reach a phone, while the phone lacks the antenna gain and transmit power to return a reliable signal through buildings. That produces deceptive one-way range.

The first usable city primitive is therefore:

```text
LAN island A <---- fixed directional backhaul ----> LAN island B
```

Once that works, each island can serve local devices over a normal short-range AP. Later islands can be joined by additional fixed links.

## Why 5 GHz wins the first experiment

### 5 GHz directional CPE

Best starter balance of:

- low hardware price;
- legal licence-exempt operation when correctly configured;
- enough bandwidth by a huge margin for state-only multiplayer;
- mature outdoor equipment;
- compact antennas;
- detailed radio telemetry;
- straightforward point-to-point deployment.

### 2.4 GHz

Rejected as the first backbone because:

- it is generally more crowded;
- the legal power boundary is less helpful for this use;
- its Fresnel zone is larger;
- it spends scarce shared spectrum on a job cheap 5 GHz CPEs already perform better.

It can remain useful for short-range client access at each island.

### 60 GHz

Technically attractive but not the cheapest proof. MikroTik's Wireless Wire Cube Pro is a preconfigured 60 GHz pair with automatic 5 GHz backup. The manufacturer positions it for approximately 1 km and reports a 2.4 km test, but the suggested pair price is $298 and 60 GHz is more weather-sensitive.

This may become an excellent clean high-capacity backbone later. It is unnecessary for proving tiny state traffic now.

### LoRa / LoRaWAN

Rejected for interactive game traffic. It is designed as low-power wide-area IoT connectivity for small battery-operated devices. It may later carry tiny emergency health beacons or node-status breadcrumbs, not the multiplayer event stream.

### Wi-Fi HaLow

Interesting later because of sub-GHz propagation and IP support, but current hardware availability and price do not beat ordinary 5 GHz directional CPE for this first fixed link.

### Bluetooth

Potentially useful for nearby discovery or bootstrap. Not the backbone.

### Omnidirectional “city antenna”

Rejected for the first test. It creates weak return-link assumptions, more interference intake, less antenna gain, and a muddy benchmark. Directional point-to-point gives the cleanest truth.

## Legal radio boundary in the Netherlands

This is an engineering summary, not a substitute for checking the current Dutch regulation and the exact Declaration of Conformity for the chosen hardware.

The Dutch Rijksinspectie Digitale Infrastructuur states that Wi-Fi can be used on licence-exempt frequencies without a registration duty, including private, business, and commercial use. It also warns that users must accept shared use and have no guarantee of interference-free operation. Professional use should therefore include a risk analysis.

For the European 5 GHz WAS/RLAN conditions:

- `5150–5250 MHz`: limited outdoor use; equipment used outdoors may not be attached to fixed outdoor infrastructure or a fixed outdoor antenna;
- `5250–5350 MHz`: outdoor use is not permitted;
- `5470–5725 MHz`: indoor and outdoor use is permitted;
- maximum mean EIRP in `5470–5725 MHz`: `1 W / 30 dBm`;
- transmitter power control and dynamic frequency selection are required;
- settings must not be changed in a way that defeats DFS compliance.

Therefore the first AXM link must:

1. use European/International hardware approved for the Netherlands;
2. set the correct country/regulatory profile to `Netherlands`;
3. retain the real built-in antenna gain;
4. retain DFS and TPC;
5. never use `SuperChannel`, a false country, a false antenna gain, or other power-limit bypass;
6. let the certified device reduce transmitter power so total EIRP stays legal;
7. log DFS channel moves as part of the field evidence.

The experiment is specifically **not** a power-maximization exercise. It is an information-minimization exercise.

## Link math

The following values are ideal calculations, not throughput guarantees.

At approximately 5.5 GHz, free-space path loss is:

```text
1 km: about 107.25 dB
2 km: about 113.27 dB
```

Assuming the legal maximum of 30 dBm EIRP and ignoring connector, obstruction, multipath, interference, polarization, and fade losses:

| Receive antenna | Ideal received level at 1 km | Ideal received level at 2 km |
|---:|---:|---:|
| 16 dBi SXTsq | about -61 dBm | about -67 dBm |
| 23 dBi LiteBeam | about -54 dBm | about -60 dBm |
| 24.5 dBi LHG | about -53 dBm | about -59 dBm |

Interpretation:

- 1 km with a clean path should be comfortable for the 16 dBi pair;
- 2 km is still plausible for the state experiment but has less top-rate margin;
- a 23–24.5 dBi pair buys approximately 7–8.5 dB of receive-side margin and rejects more off-axis interference;
- buildings or trees can erase far more than the price difference between radios can recover.

### Fresnel clearance

Seeing the other antenna is necessary but not always sufficient. Objects entering the first Fresnel zone add path loss.

At 5.5 GHz, the approximate midpoint first-Fresnel radius is:

```text
1 km link: 3.69 m radius
60% clearance target: 2.22 m around the visual line

2 km link: 5.22 m radius
60% clearance target: 3.13 m around the visual line
```

That is why two higher windows, balconies, roofs, or poles matter more than buying a stronger computer.

A tree canopy, roof ridge, billboard, or nearby building sitting just below the visual line can still damage the link.

## Site gate before spending money

Do not buy the radios until there are two candidate fixed sites.

For each site record:

- coordinates;
- straight-line distance;
- estimated antenna height above street/ground;
- ownership or explicit placement permission;
- access to mains power;
- maximum Ethernet cable route;
- clear photograph toward the other site;
- whether an exterior railing/pole is available;
- whether the signal must pass through glass;
- whether the glass has metallic/low-emissivity coating;
- major trees, roofs, or construction cranes in the path;
- whether safe access requires climbing or professional work.

Use a free link planner to check terrain and approximate Fresnel clearance, then verify visually on site. Planning software does not reliably know every tree, roof, sign, or metal-coated window.

**Hard hold:** no purchase when the two sites do not have a credible path.

## Deployment sequence

### Gate 0 — desktop bench

Place both radios in the same room at very low configured power or with sufficient separation.

Prove:

- both reset and update normally;
- both are on the same stable RouterOS release;
- Netherlands regulatory profile is active;
- management IPs are known;
- one radio can act as AP/bridge and one as station/bridge;
- encryption works;
- the link works with no internet cable connected;
- both Ethernet paths reach the two test computers;
- configuration backups and receipts are saved.

### Gate 1 — short outdoor alignment

Use two safe, accessible positions across approximately 100–300 m.

Purpose:

- learn aiming;
- learn the signal metrics;
- discover cable/PoE mistakes;
- verify weatherproof handling;
- run the complete measurement harness cheaply before attempting 1 km.

### Gate 2 — 1 km proof

This is the preferred first city-centre milestone.

Run:

- continuous ping;
- bidirectional TCP throughput;
- bidirectional UDP loss/jitter tests at several loads;
- 4-hour state-sync run;
- 24-hour state-sync run if the 4-hour run is clean;
- deliberate packet loss and reconnect tests;
- one real LAN game or deterministic AXM state-pulse demo.

### Gate 3 — 2 km extension

Use the same radios if the site geometry is clean.

Do not interpret failure as proof that the architecture fails. Separate:

- path obstruction;
- interference;
- alignment;
- legal power boundary;
- cable/PoE issues;
- radio capacity;
- state protocol behaviour.

If the link budget is weak while the path is otherwise valid, compare the same sites using LiteBeam 5AC or LHG 5 ax units before changing the architecture.

### Gate 4 — third fixed node

Only after the first segment has receipts.

A true middle relay normally needs one directional radio per link direction or a deliberately selected sector topology. One radio pointed east cannot magically become an excellent west-facing link at the same time.

Use separate channels/radios where practical so the relay does not receive and retransmit every frame on one shared collision domain.

## Initial configuration direction

This is not a copy-paste RouterOS configuration. Exact commands must match the purchased hardware and current stable software.

Use:

- one AP/bridge radio;
- one station/bridge radio;
- unique strong link credentials;
- management addresses on an isolated private subnet;
- a narrow `20 MHz` channel for the first robustness test;
- the least-congested legal channel found during a site scan;
- Netherlands country profile;
- DFS/TPC enabled and unmodified;
- no WAN/default route on the isolated first proof;
- Ethernet-connected measurement hosts;
- NTP or a controlled local time source for logs, while game truth uses explicit ticks/sequence numbers rather than trusting wall-clock timing.

Start with a transparent bridge because it makes the first proof easy to understand. Move to routed Layer 3 cells before growing a city network so broadcasts do not become city-wide soup.

## Measurement harness

### Radio evidence

Record at fixed intervals:

- model and firmware version;
- frequency and channel width;
- regulatory country;
- reported transmit power and antenna gain;
- RSSI per chain;
- noise floor;
- signal-to-noise ratio;
- negotiated modulation/rate;
- retransmissions/errors;
- Ethernet negotiation rate;
- uptime;
- DFS/radar events and channel changes;
- CPU, memory, and temperature;
- weather and major path changes.

### Network evidence

Measure both directions:

- ping minimum, median, p95, p99, and maximum;
- packet loss;
- jitter;
- TCP throughput;
- UDP loss/jitter at stepped loads;
- latency while the link is deliberately loaded;
- disconnect duration;
- time to reconnect;
- bytes transmitted and received;
- broadcast/multicast volume.

Use normal open tools such as `ping`, `iperf3`, packet capture, and structured JSON/CSV logging on the endpoint computers. The radios do not need to host the game logic.

### AXM state evidence

The first deterministic state pulse should log:

```text
match_id
protocol_version
seed_hash
tick
sender_id
sequence_number
input/event
previous_state_hash
result_state_hash
packet_bytes
acknowledgement
repair_request
checkpoint_bytes
```

Measure:

- useful state bytes per second;
- total wire bytes per second;
- events per player per second;
- state-hash agreement rate;
- unexplained divergence count;
- repair frequency;
- repair bytes;
- time to recover from a dropped packet;
- time to recover from a link interruption;
- maximum simultaneously replayable matches on an ordinary endpoint.

## Provisional first-pass gates

These are engineering targets for the first run, not product claims and not CANON limits.

| Gate | Provisional target |
|---|---|
| Internet independence | match continues with no WAN route and no external DNS |
| Link continuity | no unexplained drop longer than 5 seconds during the 24-hour run |
| Unloaded latency | p95 round trip below 10 ms |
| Controlled-load latency | p99 round trip below 25 ms at the chosen test load |
| Packet loss | below 0.5% during intended state traffic |
| State truth | zero unexplained state divergence |
| Replay | identical final hash from recorded seed + event stream |
| Repair | deliberate packet loss repairs without restarting the match |
| Traffic | initial demo stays below 50 KB/s per match before later tightening |
| Source integrity | hardware, firmware, config, weather, raw logs, and scripts retained |

A 50 KB/s temporary traffic ceiling equals about 0.4 Mbps. Even the old 100 Mbps Lite5 Ethernet boundary is not the first-game bottleneck. The purpose of measurement is to drive this ceiling down while keeping exact replay and repair.

## Power cost

Using manufacturer maximum power figures:

```text
2 × SXTsq 5 ax at 6 W each:
12 W maximum combined
about 105.1 kWh/year if operated continuously at maximum draw

2 × LiteBeam 5AC at 7 W each:
14 W maximum combined
about 122.6 kWh/year

2 × LHG 5 ax at 5 W each:
10 W maximum combined
about 87.6 kWh/year
```

The experiment can initially run only during tests. Electricity cost should use the actual host-site tariff rather than a guessed national number.

## Safety and installation boundary

The low radio price does not make roof work casual.

- Do not work alone on a roof, tower, or unsafe ladder.
- Obtain property-owner permission.
- Use exterior-rated cable and proper strain relief.
- Make a drip loop before cable entry.
- Keep PoE injectors and mains adapters indoors.
- Ground surge protection correctly; an ungrounded protector is decoration.
- Treat lightning/earthing design as professional work where a mast or rooftop run is involved.
- Temporarily accessible balcony/window tests are not permission to improvise a permanent unsafe installation.
- Configure and test both radios on a desk before mounting.

## What not to buy for the first proof

Do **not** buy yet:

- a dedicated game server;
- a Raspberry Pi solely for this link;
- a cloud instance;
- an omnidirectional city antenna;
- a sector base station;
- a managed controller appliance;
- a LoRa gateway;
- Bluetooth repeaters;
- a 60 GHz pair;
- multiple mesh relays;
- new gaming PCs;
- expensive anti-cheat compute.

First prove one cheap, lawful, observable radio segment and one exact state protocol across it.

## Resulting starter architecture

```text
SITE A

existing PC running:
- deterministic game/state client
- test harness
- raw evidence logger

        |
     Ethernet
        |
SXTsq 5 ax A
AP/bridge, legal NL profile

        ))) 1–2 km (((

SXTsq 5 ax B
station/bridge, legal NL profile
        |
     Ethernet
        |

existing PC running:
- deterministic game/state client
- test harness
- raw evidence logger

SITE B
```

Optional existing home routers can create short-range local Wi-Fi at each site. They are outside the long-range backhaul test.

## Recommendation in one line

> **Find two elevated consenting sites with real line of sight, then buy two SXTsq 5 ax units and nothing resembling a server.**

If those sites are 2 km apart with uncertain clearance or heavy interference, move one step up to two LiteBeam 5AC or LHG 5 ax units rather than buying more compute.

## Sources captured on 2026-09-02

### Dutch and EU spectrum rules

- [RDI — Vergunningvrij frequentiegebruik](https://www.rdi.nl/onderwerpen/consumenten/vergunningvrij-frequentiegebruik)
- [EUR-Lex — Commission Implementing Decision (EU) 2022/179, consolidated 2022-11-25](https://eur-lex.europa.eu/eli/dec_impl/2022/179/2022-11-25/eng)

### Hardware primary sources

- [MikroTik SXTsq 5 ax](https://mikrotik.com/product/sxtsq_5ax)
- [MikroTik SXTsq Lite5](https://mikrotik.com/product/RBSXTsq5nD)
- [MikroTik LHG 5 ax](https://mikrotik.com/product/lhg_5_ax)
- [Ubiquiti LiteBeam 5AC EU](https://eu.store.ui.com/eu/en/products/litebeam-5ac)
- [TP-Link CPE710](https://www.tp-link.com/uk/business-networking/pharos-cpe/cpe710/)
- [MikroTik Wireless Wire Cube Pro](https://mikrotik.com/product/wireless_wire_cube_pro)

### Link planning and deployment

- [Cambium LINKPlanner — Fresnel Zone](https://lp.cambiumnetworks.com/doc/fresnel_zone.html)
- [Cambium LINKPlanner](https://www.cambiumnetworks.com/products/software/linkplanner/)
- [Cisco — Site Preparation and Planning](https://www.cisco.com/c/en/us/td/docs/wireless/technology/mesh/8-6/b_mesh_86/Site_Preparation_and_Planning.html)
- [Ubiquiti UISP Design Center](https://ispdesign.ui.com/)

### Example market checks

- [Dutch price listing — SXTsq 5 ax](https://www.proshop.nl/Router/MikroTik-SXTsq-5-ax-wireless-router-Wi-Fi-6-Wireless-router-Wi-Fi-6/3419678)
- [Dutch price listing — SXTsq Lite5](https://tweakers.net/pricewatch/1227457/mikrotik-sxtsq-lite5.html)
- [Dutch LiteBeam pair listing](https://www.wifishop.nl/p/ubiquiti-litebeam-ac-gen2-point-to-point-set-60242)
- [Dutch outdoor Cat6 examples](https://netwerkkabel.eu/en/collections/cat6-outdoor)
- [Dutch Ethernet surge-protector example](https://www.galaxus.nl/en/s4/product/ubiquiti-eth-sp-g2-surge-protect-gen2-surge-protection-8599528)

## Deferred until exact sites exist

The following cannot be truthfully finalized without the two endpoint coordinates and installation heights:

- exact radio model decision;
- exact channel;
- predicted receive level;
- required antenna height;
- Fresnel obstruction profile;
- mounting hardware;
- cable length;
- legal installation detail;
- stable throughput;
- latency;
- match capacity;
- total checkout price.

No city coverage, capacity, latency, or match-count claim is CANON from this desk research alone.
