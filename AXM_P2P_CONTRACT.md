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

## Portability

The invite and join-state contract should remain transport-neutral enough to support:

- native UDP game transports;
- engine networking layers;
- encrypted reliable-UDP libraries;
- WebRTC/DataChannel adapters where appropriate;
- LAN-only builds.

Transport choice may change. The economic boundary does not.
