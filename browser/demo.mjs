import { BrowserDirectError, ManualBrowserPeer } from "./manual_webrtc.mjs";

const byId = (id) => document.getElementById(id);
let host;
let guest;
let currentRole = null;

const phases = ["phase-role", "phase-token", "phase-route", "phase-message"];
const failureHelp = {
  DIRECT_CONNECTION_UNAVAILABLE: "No relay fallback is hidden behind this failure. Keep both tabs open, confirm the devices have a route WebRTC can use, then start a fresh attempt.",
  INVALID_TOKEN: "The pasted token is not a valid AXMWEBRTC1 handoff. Copy the complete token again, then start a fresh attempt.",
  TOKEN_CORRUPT: "The token changed during copy/paste. Ask the peer to copy it again, then start a fresh attempt.",
  TOKEN_TOO_LARGE: "The handoff exceeds the bounded 64 KiB token limit. Start a fresh attempt only after the oversized input is removed.",
  INVITE_EXPIRED: "This handoff expired. Start a fresh attempt instead of extending stale connection state.",
  WRONG_GAME: "The two browsers are set to different game IDs. Match the game ID, then start a fresh attempt.",
  WRONG_BUILD: "The two browsers are set to different builds/rulesets. Match the build, then start a fresh attempt.",
  WRONG_SESSION: "This answer belongs to a different host session. Start a fresh attempt and use only the answer created from its new offer.",
  INCOMPATIBLE_TOKEN: "This is the wrong handoff type or protocol. Browser Direct uses AXMWEBRTC1 offer/answer tokens only. Start a fresh attempt with the correct handoff type.",
  WEBRTC_UNAVAILABLE: "This browser does not expose the required WebRTC peer connection capability. A fresh attempt cannot add a missing browser capability.",
  CRYPTO_UNAVAILABLE: "This browser does not expose the Web Crypto capability required to verify handoff integrity. A fresh attempt cannot add a missing browser capability.",
  INVALID_CONFIGURATION: "Game/build settings are incomplete or outside the bounded contract. Correct them, then start a fresh attempt.",
  INVALID_STATE: "The signaling steps are out of order. Start a fresh attempt rather than continuing stale signaling state.",
};

function setPhase(index, state) {
  const item = byId(phases[index]);
  if (state) item.dataset.state = state;
  else delete item.dataset.state;
}

function setProgress(completedThrough, activeIndex) {
  phases.forEach((_, index) => setPhase(index, index <= completedThrough ? "done" : index === activeIndex ? "active" : ""));
}

function setNext(message, tone = "neutral") {
  const target = byId("next-action");
  target.textContent = message;
  target.dataset.tone = tone;
}

function setRetryAvailable(visible) {
  byId("retry-panel").hidden = !visible;
}

function setOutput(target, code, detail = "", tone = "neutral") {
  target.dataset.code = code;
  target.dataset.tone = tone;
  target.replaceChildren();
  const label = document.createElement("span");
  label.className = "state-label";
  label.textContent = target.id === "host-status" ? "HOST STATE" : target.id === "guest-status" ? "GUEST STATE" : "MESSAGE STATE";
  target.append(label, document.createTextNode(detail ? `${code} — ${detail}` : code));
}

function showFailure(target, error) {
  const code = error instanceof BrowserDirectError ? error.code : "UNEXPECTED_ERROR";
  const message = error instanceof Error ? error.message : String(error);
  setOutput(target, code, message, "held");
  setNext(failureHelp[code] || "The direct attempt was held. Preserve the machine code shown here and start a fresh attempt only after checking the stated condition.", "held");
  setRetryAvailable(true);
}

function resetPeers() {
  host?.close();
  guest?.close();
  host = undefined;
  guest = undefined;
  byId("offer-out").value = "";
  byId("offer-in").value = "";
  byId("answer-out").value = "";
  byId("answer-in").value = "";
  byId("copy-offer").disabled = true;
  byId("copy-answer").disabled = true;
  byId("send").disabled = true;
  setOutput(byId("host-status"), "NOT_STARTED");
  setOutput(byId("guest-status"), "NOT_STARTED");
  setOutput(byId("message-status"), "NO_MESSAGE_SENT");
  setRetryAvailable(false);
  document.body.dataset.directState = "idle";
}

function chooseRole(role) {
  if (currentRole !== role) resetPeers();
  currentRole = role;
  byId("role-host").setAttribute("aria-pressed", String(role === "host"));
  byId("role-guest").setAttribute("aria-pressed", String(role === "guest"));
  byId("host-card").hidden = role !== "host";
  byId("guest-card").hidden = role !== "guest";
  byId("verify-card").hidden = false;
  setProgress(0, 1);
  setNext(role === "host"
    ? "Create an offer, send that token to the intended guest, and keep this tab open."
    : "Paste the host’s offer here. This browser will validate it before creating an answer.");
  document.body.dataset.role = role;
}

function startFreshAttempt() {
  resetPeers();
  if (!currentRole) {
    setProgress(-1, 0);
    setNext("Choose whether this browser is hosting or joining. Each device uses only its own side.");
    byId("role-host").focus();
    return;
  }
  setProgress(0, 1);
  if (currentRole === "host") {
    setNext("Fresh local attempt ready. Create a new offer; any token already shared is not remotely revoked and still expires on its own.", "ready");
    byId("make-offer").focus();
  } else {
    setNext("Fresh local attempt ready. Ask the host for a new offer, then paste that new token here.", "ready");
    byId("offer-in").focus();
  }
}

async function copyToken(sourceId, button, label) {
  const source = byId(sourceId);
  if (!source.value) return;
  try {
    await navigator.clipboard.writeText(source.value);
    button.textContent = `${label} copied`;
  } catch {
    source.focus();
    source.select();
    const copied = typeof document.execCommand === "function" && document.execCommand("copy");
    button.textContent = copied ? `${label} copied` : `Select ${label.toLowerCase()}`;
  }
  setTimeout(() => { button.textContent = `Copy ${label.toLowerCase()}`; }, 1600);
}

function markConnected(target, peer, side) {
  setRetryAvailable(false);
  setOutput(target, "DIRECT_CONNECTED", "direct DataChannel is open; no relay was used", "ready");
  setProgress(2, 3);
  setNext("Direct channel open. Send a test message; this proves transport only, not gameplay authority.", "ready");
  byId("send").disabled = false;
  document.body.dataset.directState = "connected";
  peer.receive(3600000).then((message) => {
    setOutput(byId("message-status"), "DIRECT_MESSAGE_RECEIVED", `${side} received ${JSON.stringify(message)}`, "ready");
    setProgress(3, -1);
    setNext("Peer message received. The direct transport path is live; the game still owns replication, rules, and input authority.", "ready");
  }).catch(() => {});
}

byId("role-host").addEventListener("click", () => chooseRole("host"));
byId("role-guest").addEventListener("click", () => chooseRole("guest"));
byId("fresh-attempt").addEventListener("click", startFreshAttempt);
byId("copy-offer").addEventListener("click", () => copyToken("offer-out", byId("copy-offer"), "Offer"));
byId("copy-answer").addEventListener("click", () => copyToken("answer-out", byId("copy-answer"), "Answer"));

byId("make-offer").addEventListener("click", async () => {
  try {
    setRetryAvailable(false);
    host?.close();
    host = new ManualBrowserPeer({ gameId: byId("host-game").value, build: byId("host-build").value });
    setOutput(byId("host-status"), "GATHERING_DIRECT_CANDIDATES", "creating a local offer; this is not a connection claim");
    setNext("Wait while this browser gathers its local direct candidates. No external signaling service is contacted.");
    byId("offer-out").value = await host.createOffer();
    byId("copy-offer").disabled = false;
    setOutput(byId("host-status"), "OFFER_READY", "send it to the intended guest; keep this tab open", "ready");
    setProgress(0, 1);
    setNext("Copy the offer to the guest. Then paste only the answer created from this offer back into this host tab.");
  } catch (error) { showFailure(byId("host-status"), error); }
});

byId("make-answer").addEventListener("click", async () => {
  try {
    setRetryAvailable(false);
    guest?.close();
    guest = new ManualBrowserPeer({ gameId: byId("guest-game").value, build: byId("guest-build").value });
    setOutput(byId("guest-status"), "VALIDATING_OFFER", "checking protocol, game, build, expiry, and token integrity");
    setNext("Validating the host offer before this browser creates any answer.");
    byId("answer-out").value = await guest.acceptOffer(byId("offer-in").value.trim());
    byId("copy-answer").disabled = false;
    setOutput(byId("guest-status"), "ANSWER_READY", "return it to the host; keep this tab open while the direct route negotiates", "ready");
    setProgress(1, 2);
    setNext("Copy this answer back to the host. Keep both tabs open; a direct route may still fail because there is no relay fallback.");
    await guest.waitForOpen();
    markConnected(byId("guest-status"), guest, "Guest");
  } catch (error) { showFailure(byId("guest-status"), error); }
});

byId("accept-answer").addEventListener("click", async () => {
  try {
    setRetryAvailable(false);
    if (!host) throw new BrowserDirectError("INVALID_STATE", "create a host offer first");
    setOutput(byId("host-status"), "VALIDATING_ANSWER", "checking this answer belongs to the current host session");
    await host.acceptAnswer(byId("answer-in").value.trim());
    setOutput(byId("host-status"), "TRYING_DIRECT_ROUTE", "answer accepted; waiting for the DataChannel to open");
    setProgress(1, 2);
    setNext("Keep both tabs open while WebRTC tries the direct route. If it cannot open, the result stays failed rather than silently relaying traffic.");
    await host.waitForOpen();
    markConnected(byId("host-status"), host, "Host");
  } catch (error) { showFailure(byId("host-status"), error); }
});

byId("send").addEventListener("click", () => {
  try {
    setRetryAvailable(false);
    const peer = currentRole === "host" ? host : currentRole === "guest" ? guest : null;
    if (!peer) throw new BrowserDirectError("INVALID_STATE", "choose a role and complete signaling first");
    peer.send({ type: "DEMO_MESSAGE", text: byId("message").value });
    setOutput(byId("message-status"), "MESSAGE_SENT_DIRECTLY", "sent on this open DataChannel; peer receipt is separate", "ready");
  } catch (error) { showFailure(byId("message-status"), error); }
});
