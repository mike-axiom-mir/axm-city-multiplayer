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

## Invite resource admission

The reference copied-invite token is bounded to **4096 characters**.

- A guest MUST reject a longer token before Base64 decoding or JSON parsing.
- The reference producer MUST refuse to emit a token above the same ceiling.
- A token inside the ceiling still has to pass the existing canonical Base64URL, checksum, canonical JSON, exact-shape, type, version, and expiry checks.

This is a local parser-resource boundary, not an authentication claim, packet-size guarantee, or proof about the channel used to carry the invite. The caller necessarily already possesses the pasted string before `decode_invite()` can apply this limit.

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
