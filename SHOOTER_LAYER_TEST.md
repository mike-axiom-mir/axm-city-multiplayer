# Shooter Layer Test Gate

Status: prepared, not yet integrated into the shooter.

## Goal

Prove that a game can treat AXM P2P as a reusable multiplayer admission layer instead of embedding invite parsing, authentication, or direct-connect rules into game code.

The first shooter test is intentionally small:

```text
HOST MULTIPLAYER
  -> AXMP2PLayer.host(...)
  -> show/copy invite

JOIN MULTIPLAYER
  -> paste invite
  -> AXMP2PLayer.join(...)
  -> DIRECT_CONNECTED or stable failure code

HOST
  -> wait_for_guest()
  -> emit PLAYER_JOINED into shooter state
```

Do not add weapon replication, prediction, rollback, anti-cheat, voice, matchmaking, relay, or dedicated-server behavior to this first gate.

## Stable game-facing result codes

- `DIRECT_CONNECTED`
- `DIRECT_CONNECTION_UNAVAILABLE`
- `INVALID_INVITE`
- `WRONG_GAME`
- `INCOMPATIBLE_BUILD`
- `INVALID_HOST_RESPONSE`
- `UNEXPECTED_HOST_RESPONSE`
- `HOST_AUTHENTICATION_FAILED`

A game may translate these codes into friendly UI text, but should preserve the raw code in diagnostics/receipts.

## Browser truth boundary

The reference adapter uses direct UDP sockets. A normal browser page cannot open arbitrary UDP sockets.

If the shooter remains browser-only, do not fake this adapter into JavaScript. Use one of these later adapter choices while keeping the same game-facing layer contract:

1. package the shooter with a native local networking wrapper/launcher;
2. add a browser-compatible peer transport behind the layer;
3. keep browser mode local/single-player until a direct browser adapter is deliberately built.

No AXM-funded relay, rendezvous, or dedicated server should be introduced merely to make the browser build easier.

## First integration acceptance test

Pass only when all are true:

1. shooter host can press one Host action;
2. shooter exposes one copyable invite;
3. a compatible guest can paste it;
4. both sides report the same admitted session;
5. shooter host receives one `PLAYER_JOINED` event;
6. incompatible build is rejected before gameplay starts;
7. unreachable direct connection ends as `DIRECT_CONNECTION_UNAVAILABLE`;
8. closing the host tears down the local P2P host cleanly;
9. no AXM network service is contacted by the default path.

After this gate passes, gameplay transport/state replication becomes a separate shooter lane.
