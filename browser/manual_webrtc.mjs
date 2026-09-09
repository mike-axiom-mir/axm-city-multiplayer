const PREFIX = "AXMWEBRTC1.";
const PROTOCOL = "axm.browser-direct/v1";
const CHANNEL_LABEL = "axm-direct-v1";
const MAX_TOKEN_BYTES = 64 * 1024;
const MAX_MESSAGE_BYTES = 64 * 1024;
const TOKEN_KEYS = ["body", "sha256"];
const BODY_KEYS = ["build", "expiresAt", "gameId", "kind", "protocol", "sdp", "sessionId"];

export class BrowserDirectError extends Error {
  constructor(code, message) {
    super(message);
    this.name = "BrowserDirectError";
    this.code = code;
  }
}

function fail(code, message) {
  throw new BrowserDirectError(code, message);
}

function exactKeys(value, keys, label) {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    fail("INVALID_TOKEN", `${label} must be an object`);
  }
  const actual = Object.keys(value).sort();
  const expected = [...keys].sort();
  if (actual.length !== expected.length || actual.some((key, index) => key !== expected[index])) {
    fail("INVALID_TOKEN", `${label} fields do not match the v1 contract`);
  }
}

function stableJson(value) {
  if (value === null || typeof value !== "object") return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(stableJson).join(",")}]`;
  return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${stableJson(value[key])}`).join(",")}}`;
}

function bytesToBase64Url(bytes) {
  let binary = "";
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary).replaceAll("+", "-").replaceAll("/", "_").replace(/=+$/u, "");
}

function base64UrlToBytes(value) {
  if (!/^[A-Za-z0-9_-]+$/u.test(value)) fail("INVALID_TOKEN", "token is not canonical base64url");
  const padded = value.replaceAll("-", "+").replaceAll("_", "/") + "===".slice((value.length + 3) % 4);
  let binary;
  try {
    binary = atob(padded);
  } catch {
    fail("INVALID_TOKEN", "token base64url is malformed");
  }
  return Uint8Array.from(binary, (char) => char.charCodeAt(0));
}

async function sha256Hex(text) {
  const cryptoApi = globalThis.crypto;
  if (!cryptoApi?.subtle) fail("CRYPTO_UNAVAILABLE", "Web Crypto SHA-256 is unavailable");
  const digest = await cryptoApi.subtle.digest("SHA-256", new TextEncoder().encode(text));
  return [...new Uint8Array(digest)].map((byte) => byte.toString(16).padStart(2, "0")).join("");
}

function validateBody(body, expectedKind, expected = {}) {
  exactKeys(body, BODY_KEYS, "token body");
  if (body.protocol !== PROTOCOL || body.kind !== expectedKind) {
    fail("INCOMPATIBLE_TOKEN", `expected ${expectedKind} ${PROTOCOL} token`);
  }
  for (const field of ["gameId", "build", "sessionId", "sdp"]) {
    if (typeof body[field] !== "string" || !body[field]) fail("INVALID_TOKEN", `${field} must be a non-empty string`);
  }
  if (!Number.isSafeInteger(body.expiresAt)) fail("INVALID_TOKEN", "expiresAt must be an integer");
  if (body.expiresAt <= Math.floor(Date.now() / 1000)) fail("INVITE_EXPIRED", "browser direct token has expired");
  if (expected.gameId !== undefined && body.gameId !== expected.gameId) fail("WRONG_GAME", "game identifier does not match");
  if (expected.build !== undefined && body.build !== expected.build) fail("WRONG_BUILD", "build identifier does not match");
  if (expected.sessionId !== undefined && body.sessionId !== expected.sessionId) fail("WRONG_SESSION", "session identifier does not match");
  return body;
}

export async function encodeBrowserDirectToken(body) {
  if (!body || !["offer", "answer"].includes(body.kind)) fail("INVALID_TOKEN", "token kind must be offer or answer");
  validateBody(body, body.kind);
  const bodyJson = stableJson(body);
  const envelope = { body, sha256: await sha256Hex(bodyJson) };
  const bytes = new TextEncoder().encode(stableJson(envelope));
  if (bytes.byteLength > MAX_TOKEN_BYTES) fail("TOKEN_TOO_LARGE", "browser direct token exceeds 64 KiB");
  return PREFIX + bytesToBase64Url(bytes);
}

export async function decodeBrowserDirectToken(token, expectedKind, expected = {}) {
  if (typeof token !== "string" || !token.startsWith(PREFIX)) fail("INVALID_TOKEN", `token must start with ${PREFIX}`);
  const encoded = token.slice(PREFIX.length);
  if (!encoded || encoded.length > Math.ceil(MAX_TOKEN_BYTES * 4 / 3)) fail("INVALID_TOKEN", "token length is invalid");
  const bytes = base64UrlToBytes(encoded);
  if (bytes.byteLength > MAX_TOKEN_BYTES) fail("TOKEN_TOO_LARGE", "browser direct token exceeds 64 KiB");
  let envelope;
  try {
    envelope = JSON.parse(new TextDecoder("utf-8", { fatal: true }).decode(bytes));
  } catch {
    fail("INVALID_TOKEN", "token JSON is malformed");
  }
  exactKeys(envelope, TOKEN_KEYS, "token envelope");
  if (typeof envelope.sha256 !== "string" || !/^[0-9a-f]{64}$/u.test(envelope.sha256)) fail("INVALID_TOKEN", "token SHA-256 is malformed");
  const canonical = stableJson(envelope.body);
  if (envelope.sha256 !== await sha256Hex(canonical)) fail("TOKEN_CORRUPT", "token SHA-256 does not match its body");
  if (stableJson(envelope) !== new TextDecoder().decode(bytes)) fail("INVALID_TOKEN", "token JSON is not canonical");
  return validateBody(envelope.body, expectedKind, expected);
}

function requiredText(value, name) {
  if (typeof value !== "string" || !value.trim() || value.length > 128) fail("INVALID_CONFIGURATION", `${name} must be 1-128 characters`);
  return value;
}

function randomSessionId() {
  const cryptoApi = globalThis.crypto;
  if (!cryptoApi?.getRandomValues) fail("CRYPTO_UNAVAILABLE", "Web Crypto randomness is unavailable");
  return bytesToBase64Url(cryptoApi.getRandomValues(new Uint8Array(18)));
}

function rtcFactoryOrFail(factory) {
  const selected = factory || globalThis.RTCPeerConnection;
  if (typeof selected !== "function") fail("WEBRTC_UNAVAILABLE", "this browser does not provide RTCPeerConnection");
  return selected;
}

function waitForIce(pc, timeoutMs) {
  if (pc.iceGatheringState === "complete") return Promise.resolve();
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      pc.removeEventListener("icegatheringstatechange", changed);
      reject(new BrowserDirectError("DIRECT_CONNECTION_UNAVAILABLE", "local ICE gathering timed out"));
    }, timeoutMs);
    function changed() {
      if (pc.iceGatheringState === "complete") {
        clearTimeout(timer);
        pc.removeEventListener("icegatheringstatechange", changed);
        resolve();
      }
    }
    pc.addEventListener("icegatheringstatechange", changed);
  });
}

export class ManualBrowserPeer {
  constructor({ gameId, build, rtcFactory, iceTimeoutMs = 5000 } = {}) {
    this.gameId = requiredText(gameId, "gameId");
    this.build = requiredText(build, "build");
    this._rtcFactory = rtcFactoryOrFail(rtcFactory);
    this._iceTimeoutMs = iceTimeoutMs;
    this._pc = null;
    this._channel = null;
    this._channelReady = new Promise((resolve) => { this._resolveChannel = resolve; });
    this._sessionId = null;
    this._expiresAt = null;
    this._role = null;
    this._messages = [];
    this._receivers = [];
  }

  _newConnection() {
    // Empty ICE server list is deliberate: never contact STUN/TURN infrastructure.
    const pc = new this._rtcFactory({ iceServers: [] });
    pc.addEventListener("connectionstatechange", () => {
      if (["failed", "disconnected"].includes(pc.connectionState)) this._rejectReceivers("DIRECT_CONNECTION_UNAVAILABLE", `WebRTC became ${pc.connectionState}`);
    });
    this._pc = pc;
    return pc;
  }

  _attachChannel(channel) {
    if (channel.label !== CHANNEL_LABEL) fail("INCOMPATIBLE_CHANNEL", "unexpected DataChannel label");
    channel.binaryType = "arraybuffer";
    channel.addEventListener("message", (event) => {
      if (typeof event.data !== "string" || new TextEncoder().encode(event.data).byteLength > MAX_MESSAGE_BYTES) return;
      let parsed;
      try { parsed = JSON.parse(event.data); } catch { return; }
      const receiver = this._receivers.shift();
      if (receiver) receiver.resolve(parsed); else this._messages.push(parsed);
    });
    this._channel = channel;
    this._resolveChannel(channel);
  }

  _rejectReceivers(code, message) {
    for (const receiver of this._receivers.splice(0)) receiver.reject(new BrowserDirectError(code, message));
  }

  async createOffer({ expiresInSeconds = 600 } = {}) {
    if (this._role) fail("INVALID_STATE", "peer already has a signaling role");
    if (!Number.isSafeInteger(expiresInSeconds) || expiresInSeconds < 30 || expiresInSeconds > 3600) fail("INVALID_CONFIGURATION", "expiresInSeconds must be an integer from 30 to 3600");
    this._role = "host";
    this._sessionId = randomSessionId();
    this._expiresAt = Math.floor(Date.now() / 1000) + expiresInSeconds;
    const pc = this._newConnection();
    this._attachChannel(pc.createDataChannel(CHANNEL_LABEL, { ordered: true }));
    await pc.setLocalDescription(await pc.createOffer());
    await waitForIce(pc, this._iceTimeoutMs);
    return encodeBrowserDirectToken({ protocol: PROTOCOL, kind: "offer", gameId: this.gameId, build: this.build, sessionId: this._sessionId, expiresAt: this._expiresAt, sdp: pc.localDescription.sdp });
  }

  async acceptOffer(token) {
    if (this._role) fail("INVALID_STATE", "peer already has a signaling role");
    const offer = await decodeBrowserDirectToken(token, "offer", { gameId: this.gameId, build: this.build });
    this._role = "guest";
    this._sessionId = offer.sessionId;
    this._expiresAt = offer.expiresAt;
    const pc = this._newConnection();
    pc.addEventListener("datachannel", (event) => this._attachChannel(event.channel), { once: true });
    await pc.setRemoteDescription({ type: "offer", sdp: offer.sdp });
    await pc.setLocalDescription(await pc.createAnswer());
    await waitForIce(pc, this._iceTimeoutMs);
    return encodeBrowserDirectToken({ protocol: PROTOCOL, kind: "answer", gameId: this.gameId, build: this.build, sessionId: this._sessionId, expiresAt: this._expiresAt, sdp: pc.localDescription.sdp });
  }

  async acceptAnswer(token) {
    if (this._role !== "host" || !this._pc) fail("INVALID_STATE", "createOffer must run before acceptAnswer");
    const answer = await decodeBrowserDirectToken(token, "answer", { gameId: this.gameId, build: this.build, sessionId: this._sessionId });
    await this._pc.setRemoteDescription({ type: "answer", sdp: answer.sdp });
  }

  async waitForOpen(timeoutMs = 10000) {
    if (!this._pc) fail("INVALID_STATE", "signaling has not started");
    const deadline = Date.now() + timeoutMs;
    const channel = this._channel || await new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(new BrowserDirectError("DIRECT_CONNECTION_UNAVAILABLE", "remote DataChannel did not arrive")), timeoutMs);
      this._channelReady.then((value) => { clearTimeout(timer); resolve(value); });
    });
    if (channel.readyState === "open") return;
    const remaining = Math.max(0, deadline - Date.now());
    await new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(new BrowserDirectError("DIRECT_CONNECTION_UNAVAILABLE", "direct DataChannel did not open")), remaining);
      channel.addEventListener("open", () => { clearTimeout(timer); resolve(); }, { once: true });
    });
  }

  send(value) {
    if (this._channel?.readyState !== "open") fail("DIRECT_CONNECTION_UNAVAILABLE", "direct DataChannel is not open");
    const encoded = stableJson(value);
    if (encoded === undefined) fail("INVALID_MESSAGE", "message must be JSON-serializable");
    if (new TextEncoder().encode(encoded).byteLength > MAX_MESSAGE_BYTES) fail("MESSAGE_TOO_LARGE", "message exceeds 64 KiB");
    this._channel.send(encoded);
  }

  receive(timeoutMs = 10000) {
    if (this._messages.length) return Promise.resolve(this._messages.shift());
    if (!this._channel) return Promise.reject(new BrowserDirectError("INVALID_STATE", "signaling has not produced a DataChannel"));
    return new Promise((resolve, reject) => {
      const entry = {
        resolve: (value) => { clearTimeout(entry.timer); resolve(value); },
        reject: (error) => { clearTimeout(entry.timer); reject(error); },
        timer: null,
      };
      this._receivers.push(entry);
      entry.timer = setTimeout(() => {
        const index = this._receivers.indexOf(entry);
        if (index >= 0) this._receivers.splice(index, 1);
        reject(new BrowserDirectError("DIRECT_CONNECTION_UNAVAILABLE", "no direct message arrived before timeout"));
      }, timeoutMs);
    });
  }

  close() {
    this._channel?.close();
    this._pc?.close();
    this._rejectReceivers("CLOSED", "peer closed");
  }
}

export function describeBrowserDirectCapability() {
  return {
    id: PROTOCOL,
    signaling: "manual-copy-paste",
    transport: "WebRTC-DataChannel",
    iceServers: [],
    relayFallback: false,
    accountRequired: false,
    failureCode: "DIRECT_CONNECTION_UNAVAILABLE",
    limits: { tokenBytes: MAX_TOKEN_BYTES, messageBytes: MAX_MESSAGE_BYTES },
  };
}
