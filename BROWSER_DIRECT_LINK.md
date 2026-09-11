# Browser Direct Link v1

Status: bounded experimental transport adapter; not CANON

`browser/manual_webrtc.mjs` closes one specific gap in the native reference: normal browser pages cannot open its UDP socket. The adapter carries JSON messages over an ordered WebRTC DataChannel and uses manual copy/paste offer/answer tokens for signaling.

It deliberately configures `iceServers: []`. It does not contact STUN or TURN, discover strangers, create a lobby, require an account, or relay traffic. Host and guest must exchange both tokens through a channel they choose.

## Run the local desk

From the repository root:

```bash
python -m http.server 8765
```

Open `http://127.0.0.1:8765/browser/` in two browser profiles or on two devices that can reach the local server. The host sends the offer to the guest; the guest returns the answer; both sides report `DIRECT_CONNECTED` only after the DataChannel opens.

The browser adapter uses its own `AXMWEBRTC1.` token. It does not accept or reinterpret native `AXMP2P1.` UDP invites. Both contracts bind game, build, session, expiry, and transport-specific connection material, but they are not wire-compatible.

## Library seam

```js
import { ManualBrowserPeer } from "./browser/manual_webrtc.mjs";

const host = new ManualBrowserPeer({ gameId: "axm.example", build: "build-001" });
const offerToken = await host.createOffer();
// send offerToken to the guest; receive answerToken back
await host.acceptAnswer(answerToken);
await host.waitForOpen();
host.send({ type: "READY", tick: 0 });
```

The guest constructs the same class, calls `acceptOffer(offerToken)`, returns the resulting answer token, waits for open, and uses `send()` / `receive()`.

## Truth and security boundary

- A token SHA-256 detects accidental or unsophisticated modification; it is not a signature or proof of authorship.
- WebRTC supplies encrypted DTLS transport after direct negotiation. This adapter does not authenticate a human identity or prove that game messages are honest.
- Manual tokens contain SDP network candidates and must be shared only with the intended peer.
- Empty ICE servers make this implementation local/offline and prevent it from configuring hidden STUN/TURN infrastructure. In addition, `AXMWEBRTC1` admission rejects any SDP ICE candidate whose declared candidate type is `relay` with `RELAY_CANDIDATE_FORBIDDEN`, before an incoming token reaches `setRemoteDescription()` and before a locally supplied SDP can be emitted as a direct token. This makes the no-TURN-relay traffic boundary executable even when the other endpoint or an injected `RTCPeerConnection` implementation is not the same trusted adapter.
- The candidate check is a bounded SDP admission rule, not candidate authentication. It does not prove how a non-relay address was learned, establish Internet/NAT reachability, or prevent a malicious browser/network stack from behaving outside the declared SDP contract.
- LAN/same-machine paths remain the primary supported experiment. NAT/CGNAT/firewall failure is an honest `DIRECT_CONNECTION_UNAVAILABLE` outcome.
- There is no gameplay replication, rollback, voice, matchmaking, reconnect, hostile-process sandbox, or automatic fallback here.

## Verification

Dependency-free contract and simulated transport tests:

```bash
node --test browser/tests/manual_webrtc.test.mjs
```

The CI workflow additionally starts the exact static files and runs `browser/tests/chromium_smoke.mjs` in real headless Chromium. It negotiates two independent browser peers, copies the offer and answer between them, opens a direct DataChannel, and exchanges verified PING/PONG JSON in both directions.
