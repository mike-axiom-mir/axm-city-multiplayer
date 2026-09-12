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

The reference guest accepts handshake replies only from the host address and port carried by that invite. The shared session key authenticates an invite holder; it must not let a different endpoint race the invited host and become the returned peer.

## Invite resource admission

The reference copied-invite token is bounded to **4096 characters**.

- A guest MUST reject a longer token before Base64 decoding or JSON parsing.
- The reference producer MUST refuse to emit a token above the same ceiling.
- A token inside the ceiling still has to pass canonical Base64URL, checksum, canonical JSON, exact-shape, type, version, and expiry checks.

This is a local parser-resource boundary, not an authentication claim, packet-size guarantee, or proof about the channel used to carry the invite. The caller necessarily already possesses the pasted string before `decode_invite()` can apply this limit.

## Failure is an allowed state

`DIRECT_CONNECTION_UNAVAILABLE` is a legitimate terminal result for the default free P2P path.

The software should explain likely causes such as firewall, router/NAT, ISP CGNAT, expired invite, wrong build, or closed host, but it must not silently purchase or consume AXM relay capacity.

## Admission proof and pre-admission resource boundary

A valid `HELLO` is not an admitted peer. The reference handshake is versioned and requires:

```text
HELLO -> authenticated WELCOME -> authenticated ACK -> admitted peer
```

While the host waits for the authenticated ACK, it keeps only bounded temporary handshake evidence.

The reference host therefore:

- limits the number of simultaneous incomplete authenticated handshakes;
- expires each incomplete handshake after a bounded lifetime;
- does not refresh that lifetime merely because the same `HELLO` is repeated;
- reuses the same pending host nonce for a legitimate retry while that pending handshake remains live;
- refuses a late `ACK` after its pending handshake has expired;
- creates authoritative peer state only after the authenticated ACK gate succeeds.

The default bound is a local resource-safety policy, not a gameplay-capacity claim. An explicit caller may choose a different positive bound and lifetime for a particular game/runtime.

This boundary does not make the bearer invite secret private after it has been shared, authenticate a human identity, provide per-IP fairness, prevent packet floods before the Python process, or replace operating-system/firewall/network rate controls. It specifically prevents an invite holder from growing the reference host's in-memory pre-admission handshake table without limit by withholding ACKs.

## Game-facing layer operation ownership

One `AXMP2PLayer` instance admits at most one transient `host()` or `join()` operation at a time. The claim is established before invite or transport work begins and released on success or failure. A concurrent call fails closed with `LAYER_OPERATION_IN_PROGRESS` and does not overwrite the owning operation's `JOINING` state or enter a transport adapter.

An active host session remains a longer-lived, separate ownership state and is reported as `HOST_SESSION_ALREADY_ACTIVE`. This is an in-process integration invariant, not a cross-process lock or a gameplay-connection lifecycle.

## Portability

The invite and join-state contract should remain transport-neutral enough to support:

- native UDP game transports;
- engine networking layers;
- encrypted reliable-UDP libraries;
- WebRTC/DataChannel adapters where appropriate;
- LAN-only builds.

Transport choice may change. The economic boundary does not.
