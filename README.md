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
6. deterministic failure when direct connectivity is unavailable;
7. a stable game-facing `AXMP2PLayer` integration seam;
8. thread-safe guest-admission events for host games.

The UDP code is a **reference handshake**. Production games should plug their engine/network transport behind the same invite contract and provide appropriate encryption, replay protection, packet ordering, congestion control, and game-state validation.

## Peer Fabric research extension

The same PR lane now also preserves the larger serverless-multiplayer research direction discovered after the v0.1 direct invite worked:

```text
friend / social invite / ignition peer
            ↓
cryptographic peer identity + consent
            ↓
private / federated / public groups
            ↓
bounded decentralized discovery overlay
            ↓
signed expiring presence tickets
            ↓
local peer-to-peer matchmaking proposals
            ↓
direct P2P game
```

The important distinction is:

- **measured base:** direct invite/admission reference core;
- **research:** remembered peer bonds, router helper, community endpoint observation, public groups, decentralized discovery/matchmaking, host fairness, rollback and coordinator migration.

Public discovery does **not** mean every player connects to every other player. A scalable public fabric should use a bounded overlay for discovery and create actual game connections only for selected matches.

The research direction also does not require blockchain-style permanent global consensus. Presence and match-search state should be signed, scoped and short-lived.

See:

- `PEER_FABRIC_ARCHITECTURE.md` — complete architecture and truth boundaries;
- `PEER_FABRIC_RESEARCH_GATES.md` — bounded experiments from router/NAT repair through public matchmaking and old-game resurrection;
- `RESEARCH_P2P_ONLY.md` — protocol precedents and direct-only networking boundary;
- `SHOOTER_LAYER_TEST.md` — existing bounded shooter admission gate.

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

The host address/port must actually be reachable by the guest. On many home routers this means a port mapping or port-forwarding rule. A future adapter may automate router mapping locally, but **no third-party gameplay relay is part of the default design**.

If the ISP/router topology prevents direct reachability, the free P2P mode is allowed to fail. Users or communities may host their own additional infrastructure outside this core if they want different trade-offs.

## Game integration boundary

Games should integrate through `AXMP2PLayer` instead of importing invite/HMAC/UDP internals directly.

```python
from axm_p2p import AXMP2PLayer

net = AXMP2PLayer(game_id="axm.shooter", build="build-001")

# Host
host = net.host(public_host="203.0.113.50", port=28741)
print(host.invite_token)
peer = host.wait_for_guest(timeout=30)

# Guest
result = net.join(pasted_invite, timeout=3)
if result.connected:
    print("DIRECT_CONNECTED")
else:
    print(result.code)
```

The game-facing flow remains deliberately small:

```text
HOST MULTIPLAYER
→ create local session
→ expose/copy invite
→ receive guest-admitted event

JOIN MULTIPLAYER
→ paste invite
→ validate game + build
→ attempt direct connection
→ DIRECT_CONNECTED or stable failure code
```

The game owns the actual gameplay protocol after connection.

## Browser boundary

The native reference adapter uses direct UDP sockets. Normal browser pages cannot open arbitrary UDP sockets, so a browser-only game must use a different transport adapter behind the same layer contract or a native local wrapper. Do not introduce an AXM-funded relay/rendezvous service merely to hide that platform limitation.

See `SHOOTER_LAYER_TEST.md` for the bounded future shooter integration gate and `examples/shooter_layer_smoke.py` for the host/join shape.

## Test

```bash
python -m unittest discover -s tests -v
```

The current reference suite checks invite round-trip, expiry, corruption, build mismatch, direct localhost handshake, stable layer result codes, and the game-facing host/join admission flow.
