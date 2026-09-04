# AXM City Multiplayer

## AXM P2P Direct Invite v0.1

The default multiplayer contract for free/local AXM games is intentionally simple:

> **Host → Copy Invite → Send Anywhere → Guest Pastes → Direct Connect**

AXM does **not** pay to relay, proxy, or host gameplay traffic for free local games.

### Core rules

- Player-hosted peer-to-peer is the default.
- No AXM relay fallback.
- No required AXM account.
- No required AXM lobby server.
- LAN/direct-IP use remains possible even if AXM services do not exist.
- A copied invite carries only what a guest needs to attempt the direct session.
- If the route is not reachable, return `DIRECT_CONNECTION_UNAVAILABLE`.
- Do not silently fall back to paid AXM infrastructure.
- A future title may add its own dedicated-server mode, but that is outside this default core.

### Why this repository starts small

This is a reusable reference contract, not a full game netcode engine. Different games have different needs for replication, rollback, lockstep, snapshots, voice, anti-cheat, tick rates, and transport security.

v0.1 therefore provides:

1. a portable invite format;
2. expiry and corruption detection;
3. game/build compatibility fields;
4. a session secret shared only through the invite;
5. an authenticated UDP join handshake;
6. deterministic failure when direct connectivity is unavailable.

The UDP code is a **reference handshake**. Production games should plug their engine/network transport behind the same invite contract and provide appropriate encryption, replay protection, packet ordering, congestion control, and game-state validation.

## Invite contract

Invite prefix:

```text
AXMP2P1.
```

Payload fields:

```text
v protocol version
g game identifier
b build/ruleset fingerprint
h directly reachable host or DNS name
p UDP port
s random session id
k random session key
e expiry timestamp
```

The token is base64url-encoded canonical JSON plus a checksum. The checksum detects copy/paste corruption. It is not intended to prove authorship: anyone holding the invite is intentionally allowed to join.

## Reference CLI

Run from the repo root:

```bash
python -m axm_p2p.cli host \
  --game axm.example \
  --build build-001 \
  --public-host 203.0.113.50 \
  --port 28741
```

The host receives one copyable token.

Guest:

```bash
python -m axm_p2p.cli join "AXMP2P1...." \
  --game axm.example \
  --build build-001
```

### Internet use

The host address/port must actually be reachable by the guest. On many home routers this means a port mapping or port-forwarding rule. A future adapter may automate router mapping locally, but **no third-party relay is part of the default design**.

If the ISP/router topology prevents direct reachability, the free P2P mode is allowed to fail. Users or communities may host their own additional infrastructure outside this core if they want different trade-offs.

## Game integration boundary

A game should expose only two ordinary UI actions:

```text
HOST MULTIPLAYER
→ create local session
→ expose/copy invite

JOIN MULTIPLAYER
→ paste invite
→ validate game + build
→ attempt direct connection
→ CONNECTED or DIRECT_CONNECTION_UNAVAILABLE
```

The game owns the actual gameplay protocol after connection.

## Test

```bash
python -m unittest discover -s tests -v
```

The reference suite checks invite round-trip, expiry, corruption, build mismatch, and a real localhost UDP host/guest handshake.
