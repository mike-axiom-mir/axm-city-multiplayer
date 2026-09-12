# AXM City Multiplayer — Cheapest 1–2 km Starter Research

Status: **CANDIDATE / NOT CANON / NOT PURCHASED / NOT FIELD-VERIFIED**

Research date: 2026-09-03

This file belongs to the founding chat's single PR lane. It does not select production hardware or claim city coverage.

## Research question

What is the cheapest serious fixed-node experiment that can test the AXM City Multiplayer physical-network hypothesis over roughly 1–2 km, while keeping participant phones/PCs as clients only and keeping the design legal and measurable in the Netherlands?

## Result

The cheapest useful first proof is **not** a 1–2 km direct phone-to-access-point link.

Use two fixed, directional outdoor radios as a point-to-point backbone. Plug an existing computer into each end by Ethernet for the first test. Add ordinary local Wi-Fi access points later only where client devices need to join.

Initial topology:

```text
PC A
  |
Ethernet
  |
SXTsq 5 ax  ))))))  1–2 km directional 5 GHz  ((((((  SXTsq 5 ax
                                                          |
                                                       Ethernet
                                                          |
                                                         PC B
```

Later client topology:

```text
phones / PCs
     |
local Wi-Fi AP
     |
Ethernet
     |
directional backhaul ===== directional backhaul
                                      |
                                  local Wi-Fi AP
                                      |
                                  phones / PCs
```

## Leading candidate: MikroTik SXTsq 5 ax

Model: `SXTsq-5axD`

Why it currently wins the price/performance comparison:

- 5 GHz Wi-Fi 6 / 802.11ax
- integrated 16 dBi directional antenna
- Gigabit Ethernet
- RouterOS v7, license level 4, including AP capability
- IP55 outdoor enclosure
- maximum power consumption 6 W
- 24 V adapter, Gigabit PoE injector and mounting clamp included
- manufacturer says it has been field-tested to 3 km in high-interference urban scenarios and uses a design capable of 10+ km line-of-sight links
- current EU street prices found during this run are approximately €56–65 per unit, excluding/depending on shipping

This makes the **radio-only two-endpoint experiment roughly €110–130 before any cable/mounting costs**, assuming existing PCs are used at both ends.

Sources checked:

- MikroTik specification sheet: https://cdn.mikrotik.com/web-assets/product_files/SXTsq5ax_250409.pdf
- MikroTik product brief: https://cdn.mikrotik.com/web-assets/product_files/SXTsq5ax_250427.pdf
- MikroTik EU safety/regulatory guide: https://cdn.mikrotik.com/web-assets/product_files/QG_SXTsq-5axD_250447.pdf
- Current EU example price, €55.76: https://www.omg.de/mikrotik/wireless-systeme/mikrotik-sxtsq-5-ax-sxtsq-5axd/a-30754
- Current EU example price, €57.08: https://www.dateks.lv/en/cenas/wireless/1220237-mikrotik-sxtsq-5-ax

Manufacturer distance statements are **candidate evidence, not an AXM field result**. Tilburg performance must be measured.

## Absolute-price-floor candidate: MikroTik SXTsq Lite5

Current prices found are roughly €41–52 per unit. It also has a 16 dBi directional antenna, but it is an older Wi-Fi 4 design and its Ethernet interface is limited to 100 Mbit/s.

Two units can reduce the radio purchase to roughly the €85–105 range, but saving around a few tens of euros for the pair also gives up Wi-Fi 6, Gigabit Ethernet, the much newer CPU/platform and extra future headroom.

**Research verdict:** useful as a deliberately minimum-cost control, but the SXTsq 5 ax is the stronger starting buy unless the budget is extremely tight.

## Ubiquiti alternative

The Ubiquiti NanoStation 5AC Loco is currently around €53.90 in the Netherlands and has Gigabit Ethernet. It is a valid low-cost point-to-point candidate.

However, current listings/reviews note that the Loco does not include its PoE injector, which reduces or removes its apparent price advantage once a complete two-node setup is priced.

Current NL price source: https://tweakers.net/pricewatch/1167409/ubiquiti-nanostation-ac-loco-single-pack.html

A LiteBeam 5AC Gen2 pair provides 23 dBi antennas and stronger link margin, but current Dutch pricing is materially higher. That hardware is more interesting if the first SXTsq test reveals a link-budget problem rather than as the cheapest starting point.

## Netherlands radio boundary

License-free Wi-Fi use is permitted in the Netherlands when the designated frequencies and conditions are respected. RDI also makes clear that license-free use does not guarantee interference-free operation.

For outdoor 5 GHz RLAN operation, the current Dutch regulation lists 5470–5725 MHz at up to 1 W average e.i.r.p. with the required mitigation/TPC conditions; without TPC, the permitted average e.i.r.p. and density are reduced by 3 dB. The equipment must comply with the applicable DFS/radar-protection requirements.

Sources:

- RDI license-free use: https://www.rdi.nl/onderwerpen/consumenten/vergunningvrij-frequentiegebruik
- Current regulation: https://wetten.overheid.nl/jci1.3:c:BWBR0036378&g=2025-07-01&z=2026-01-29

MikroTik's own EU guide says the device must run RouterOS v7.15 or later/stable for local-regulation compliance and that the user is responsible for legal channel, output power and DFS settings.

**AXM test rule:** set the regulatory country to Netherlands, keep current stable firmware, keep DFS/TPC/regulatory controls enabled, and do not use Superchannel or manual power hacks.

## What 1–2 km means

This experiment proves a **1–2 km backbone span**, not a 1–2 km omnidirectional phone-coverage radius.

The fixed radios have directional gain at both ends. Ordinary phones do not. Client devices therefore connect locally to the nearest fixed site and the fixed sites carry traffic across the long hop.

Buildings and vegetation attenuate radio signals. In a dense city centre, placement and line-of-sight are more important than simply increasing transmitter power.

If a building blocks the path, the preferred AXM response is:

```text
add a legal relay point
```

not:

```text
increase power until physics apologises
```

## Minimal purchase for Proof 0

Assuming two existing PCs/laptops and accessible high mounting points:

1. 2 × MikroTik SXTsq 5 ax
2. outdoor-rated Ethernet cable as needed for each site
3. safe mounting hardware if the included clamp cannot attach to the available structure

The radios already include their power adapters and Gigabit PoE injectors.

No dedicated game server is required for Proof 0. No local outdoor AP is required either. Connect each test computer directly to its site's radio.

## Proof sequence

Do not begin at 2 km and then guess why a failure happened.

### Gate A — table/room

- update firmware
- set Netherlands regulatory domain
- configure the pair as a legal point-to-point bridge/routed link
- confirm Ethernet transport

### Gate B — short outdoor

- 50–100 m clear path
- record RSSI/SNR, modulation/rate, ping, jitter, packet loss, TCP/UDP throughput and radio CPU

### Gate C — intermediate

- approximately 300–500 m
- repeat the same receipt

### Gate D — 1 km

- repeat measurements under actual urban RF conditions

### Gate E — 2 km

- only after earlier gates pass
- repeat measurements and compare degradation rather than merely recording PASS/FAIL

### Gate F — AXM state traffic

Once the radio link is boring and stable, run a small deterministic multiplayer/state-sync harness over it and measure:

- authoritative bytes per player per second
- packet rate
- jitter sensitivity
- recovery traffic after deliberate loss
- replay/checkpoint repair traffic
- number of simultaneous synthetic matches before a defined truth/latency gate fails

This is the measurement that connects the radio experiment to the larger AXM hypothesis.

## First real relay after the two-node proof

For A → B → C, do not make one radio at B repeatedly receive and retransmit the same channel if the goal is a serious backbone.

A robust candidate relay is:

```text
A radio
   )))))
       B radio #1 -- Ethernet/router -- B radio #2
                                      )))))
                                          C radio
```

That means a serious transit site can eventually have **two directional backhaul radios**, one toward each neighbour, while local users get a separate access AP only if that site is also a player access point.

This separates:

- backbone capacity
- local client capacity
- compute/match-host capacity

and lets each one scale independently.

## HaLow decision

Wi-Fi HaLow remains a valuable future research lane because sub-GHz propagation could help with longer or obstructed links and AXM ultimately hopes to transmit very sparse state.

It is **not the cheapest first proof today**. Current evaluation hardware costs substantially more than the 5 GHz CPE candidates, native client support remains limited, and EU sub-GHz rules impose constraints that need a separate legal/airtime study before treating HaLow as a general game backbone.

The correct order is:

```text
measure real AXM state traffic first
        ↓
then ask whether HaLow can legally carry that traffic
```

not the reverse.

## Current recommendation

**Buy nothing until two plausible line-of-sight sites are identified.**

If two sites exist, the current preferred first hardware is:

```text
2 × MikroTik SXTsq 5 ax
```

This is the smallest serious experiment found in this research run that preserves the AXM architecture: fixed infrastructure, client devices only at the edge, legal local radio, inexpensive operation, and enough bandwidth/compute headroom that the first experiment tests the architecture rather than an obsolete 100-Mbit bottleneck.

## Truth boundary

Not proven yet:

- reliable 1 km or 2 km operation at any specific Tilburg placement
- usable throughput under the exact local interference profile
- number of AXM matches per link
- number of relays that can be chained before latency becomes unacceptable
- city-scale economics
- final radio technology

The first purchase is a **measurement instrument for the hypothesis**, not a declaration that the city network already works.
