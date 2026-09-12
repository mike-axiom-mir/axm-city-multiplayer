import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { test } from "node:test";
import { BrowserDirectError, ManualBrowserPeer, decodeBrowserDirectToken, describeBrowserDirectCapability, encodeBrowserDirectToken } from "../manual_webrtc.mjs";

class FakeChannel extends EventTarget {
  constructor(label) { super(); this.label = label; this.readyState = "connecting"; this.peer = null; }
  open() { this.readyState = "open"; this.dispatchEvent(new Event("open")); }
  send(data) { queueMicrotask(() => this.peer.dispatchEvent(new MessageEvent("message", { data }))); }
  close() { this.readyState = "closed"; }
}

const registry = new Map();
let nextId = 1;
class FakeRTC extends EventTarget {
  constructor(config) {
    super();
    assert.deepEqual(config, { iceServers: [] });
    this.id = String(nextId++);
    this.iceGatheringState = "complete";
    this.connectionState = "new";
    this.localDescription = null;
    this.hostChannel = null;
    registry.set(this.id, this);
  }
  createDataChannel(label) { this.hostChannel = new FakeChannel(label); return this.hostChannel; }
  async createOffer() { return { type: "offer", sdp: `offer:${this.id}` }; }
  async createAnswer() { return { type: "answer", sdp: `answer:${this.remoteId}:${this.id}` }; }
  async setLocalDescription(value) { this.localDescription = value; }
  async setRemoteDescription(value) {
    if (value.type === "offer") {
      this.remoteId = value.sdp.split(":")[1];
      const host = registry.get(this.remoteId);
      this.guestChannel = new FakeChannel(host.hostChannel.label);
      host.hostChannel.peer = this.guestChannel;
      this.guestChannel.peer = host.hostChannel;
      queueMicrotask(() => this.dispatchEvent(Object.assign(new Event("datachannel"), { channel: this.guestChannel })));
    } else {
      const [, hostId, guestId] = value.sdp.split(":");
      assert.equal(hostId, this.id);
      const guest = registry.get(guestId);
      this.connectionState = guest.connectionState = "connected";
      this.hostChannel.open();
      guest.guestChannel.open();
    }
  }
  close() { this.connectionState = "closed"; }
}

function stableJson(value) {
  if (value === null || typeof value !== "object") return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(stableJson).join(",")}]`;
  return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${stableJson(value[key])}`).join(",")}}`;
}

function uncheckedToken(body) {
  const bodyJson = stableJson(body);
  const envelope = {
    body,
    sha256: createHash("sha256").update(bodyJson, "utf8").digest("hex"),
  };
  return `AXMWEBRTC1.${Buffer.from(stableJson(envelope), "utf8").toString("base64url")}`;
}

function relaySdp() {
  return [
    "v=0",
    "o=- 1 2 IN IP4 127.0.0.1",
    "s=-",
    "t=0 0",
    "a=candidate:relay 1 UDP 1677729535 192.0.2.50 50000 typ relay raddr 0.0.0.0 rport 0",
  ].join("\r\n");
}

test("manual tokens establish a direct channel with no ICE servers", async () => {
  const host = new ManualBrowserPeer({ gameId: "axm.test", build: "b1", rtcFactory: FakeRTC });
  const guest = new ManualBrowserPeer({ gameId: "axm.test", build: "b1", rtcFactory: FakeRTC });
  const offer = await host.createOffer({ expiresInSeconds: 60 });
  const answer = await guest.acceptOffer(offer);
  await host.acceptAnswer(answer);
  await Promise.all([host.waitForOpen(), guest.waitForOpen()]);
  host.send({ type: "PING", tick: 7 });
  assert.deepEqual(await guest.receive(), { tick: 7, type: "PING" });
  guest.send({ type: "PONG", tick: 7 });
  assert.deepEqual(await host.receive(), { tick: 7, type: "PONG" });
});

test("wrong build fails before creating a peer connection", async () => {
  const host = new ManualBrowserPeer({ gameId: "axm.test", build: "b1", rtcFactory: FakeRTC });
  const offer = await host.createOffer({ expiresInSeconds: 60 });
  const guest = new ManualBrowserPeer({ gameId: "axm.test", build: "b2", rtcFactory: FakeRTC });
  await assert.rejects(() => guest.acceptOffer(offer), (error) => error instanceof BrowserDirectError && error.code === "WRONG_BUILD");
  assert.equal(guest._pc, null);
});

test("tampered, swapped, and non-canonical tokens fail closed", async () => {
  const host = new ManualBrowserPeer({ gameId: "axm.test", build: "b1", rtcFactory: FakeRTC });
  const offer = await host.createOffer({ expiresInSeconds: 60 });
  const body = offer.slice("AXMWEBRTC1.".length);
  const tampered = `AXMWEBRTC1.${body.slice(0, -1)}${body.at(-1) === "A" ? "B" : "A"}`;
  await assert.rejects(() => decodeBrowserDirectToken(tampered, "offer"));
  await assert.rejects(() => decodeBrowserDirectToken(offer, "answer"), (error) => error.code === "INCOMPATIBLE_TOKEN");
  await assert.rejects(() => decodeBrowserDirectToken(`${offer}=`, "offer"), (error) => error.code === "INVALID_TOKEN");
});

test("self-consistent remote relay candidates are refused before WebRTC admission", async () => {
  const token = uncheckedToken({
    protocol: "axm.browser-direct/v1",
    kind: "offer",
    gameId: "axm.test",
    build: "b1",
    sessionId: "relay-attempt",
    expiresAt: Math.floor(Date.now() / 1000) + 60,
    sdp: relaySdp(),
  });
  const guest = new ManualBrowserPeer({ gameId: "axm.test", build: "b1", rtcFactory: FakeRTC });
  await assert.rejects(
    () => guest.acceptOffer(token),
    (error) => error instanceof BrowserDirectError && error.code === "RELAY_CANDIDATE_FORBIDDEN",
  );
  assert.equal(guest._pc, null);
});

test("locally generated relay candidates cannot be encoded as direct tokens", async () => {
  await assert.rejects(
    () => encodeBrowserDirectToken({
      protocol: "axm.browser-direct/v1",
      kind: "offer",
      gameId: "axm.test",
      build: "b1",
      sessionId: "relay-attempt",
      expiresAt: Math.floor(Date.now() / 1000) + 60,
      sdp: relaySdp(),
    }),
    (error) => error instanceof BrowserDirectError && error.code === "RELAY_CANDIDATE_FORBIDDEN",
  );
});

test("missing browser capability is explicit", () => {
  assert.throws(() => new ManualBrowserPeer({ gameId: "axm.test", build: "b1", rtcFactory: null }), (error) => error.code === "WEBRTC_UNAVAILABLE");
});

test("capability declaration preserves the economic boundary", () => {
  assert.deepEqual(describeBrowserDirectCapability(), {
    id: "axm.browser-direct/v1",
    signaling: "manual-copy-paste",
    transport: "WebRTC-DataChannel",
    iceServers: [],
    relayFallback: false,
    accountRequired: false,
    failureCode: "DIRECT_CONNECTION_UNAVAILABLE",
    limits: { tokenBytes: 65536, messageBytes: 65536 },
  });
});
