# AXM P2P Default Contract

Status: v0.1 reference contract

## Economic boundary

AXM free/local games do not require AXM-funded gameplay infrastructure.

The default implementation MUST NOT:

- proxy gameplay through AXM;
- require an AXM-hosted relay;
- require an AXM-hosted dedicated server;
- hide bandwidth cost behind a fallback path;
- make online continuation depend on AXM staying online.

## User promise

If one player can expose a reachable endpoint, that player can host.

They copy one invite and send it through any external channel they choose: message app, email, QR encoder, forum, or clipboard transfer.

The guest pastes the invite into the game and attempts a direct connection.

## Failure is an allowed state

`DIRECT_CONNECTION_UNAVAILABLE` is a legitimate terminal result for the default free P2P path.

The software should explain likely causes such as firewall, router/NAT, ISP CGNAT, expired invite, wrong build, or closed host, but it must not silently purchase or consume AXM relay capacity.

## Pre-admission resource boundary

A valid `HELLO` is not an admitted peer. While the reference round-trip handshake waits for its authenticated `ACK`, the host keeps only bounded temporary handshake evidence.

The reference host therefore:

- limits the number of simultaneous incomplete authenticated handshakes;
- expires each incomplete handshake after a bounded lifetime;
- does not refresh that lifetime merely because the same `HELLO` is repeated;
- reuses the same pending host nonce for a legitimate retry while that pending handshake remains live;
- refuses a late `ACK` after its pending handshake has expired;
- creates authoritative peer state only after the existing authenticated ACK gate succeeds.

The default bound is a local resource-safety policy, not a gameplay-capacity claim. An explicit caller may choose a different positive bound and lifetime for a particular game/runtime.

This boundary does not make the bearer invite secret private after it has been shared, authenticate a human identity, provide per-IP fairness, prevent packet floods before the Python process, or replace operating-system/firewall/network rate controls. It specifically prevents an invite holder from growing the reference host's in-memory pre-admission handshake table without limit by withholding ACKs.

## Portability

The invite and join-state contract should remain transport-neutral enough to support:

- native UDP game transports;
- engine networking layers;
- encrypted reliable-UDP libraries;
- WebRTC/DataChannel adapters where appropriate;
- LAN-only builds.

Transport choice may change. The economic boundary does not.
