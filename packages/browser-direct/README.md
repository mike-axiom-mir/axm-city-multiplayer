# AXM City Browser Direct

Status: **EXPERIMENTAL** · local package · no relay fallback · not CANON

This package is a portable consumption seam for the browser-native direct transport implemented by `browser/manual_webrtc.mjs` in AXM City Multiplayer.

It does not maintain a second WebRTC implementation. `npm pack` verifies the exact reviewed provider blob, copies those bytes into the tarball, and emits source/provenance metadata beside them.

## Build a local tarball

From the repository root on the exact reviewed source line:

```bash
npm pack ./packages/browser-direct --pack-destination ./dist
```

The package stays `private: true`; this is a deliberate local/offline distribution path, not a registry release.

## Install into a browser project

```bash
npm install --offline --ignore-scripts ./axm-city-browser-direct-0.1.0.tgz
```

Then import the bounded adapter:

```js
import {
  ManualBrowserPeer,
  BrowserDirectError,
  encodeBrowserDirectToken,
  decodeBrowserDirectToken,
  describeBrowserDirectCapability,
} from "axm-city-browser-direct";
```

The host/guest flow remains the provider contract:

```text
host createOffer -> copy offer -> guest acceptOffer -> copy answer
-> host acceptAnswer -> both waitForOpen -> direct DataChannel messages
```

## Package evidence

The tarball contains:

- the exact verified `manual_webrtc.mjs` provider bytes;
- `capability.json`, derived from the provider's executable descriptor;
- `PROVENANCE.json`, binding the provider repository, prerequisite commit, source Git blob, SHA-256, and copied license/third-party evidence;
- the repository's Apache-2.0 `LICENSE` and current third-party ledger.

The package test builds twice, requires byte-identical tarballs in the same toolchain, installs from a local tarball with npm offline mode, imports through the package name from outside the repository checkout, exercises token encode/decode, verifies provenance against installed bytes, and requires a clean `WEBRTC_UNAVAILABLE` refusal when the host runtime has no `RTCPeerConnection`.

The hosted browser gate additionally serves the **installed package bytes** to real Chromium and performs the two-peer offer/answer/DataChannel PING/PONG proof.

## Truth and authority boundary

- Packaging does not improve NAT reachability. With `iceServers: []`, same-machine/LAN direct routes remain the primary supported experiment and `DIRECT_CONNECTION_UNAVAILABLE` is an honest outcome.
- SDP tokens expose network candidates and must be shared only with the intended peer.
- WebRTC encrypts the negotiated transport; this package does not authenticate a human, prove honest gameplay messages, provide matchmaking, replication, rollback, reconnect, or anti-cheat.
- SHA-256 and Git blob identity are integrity/lineage evidence, not authorship signatures.
- Importing the package is an explicit consumer decision. Discovery, installation, execution, release, merge, and CANON authority are not granted automatically.
