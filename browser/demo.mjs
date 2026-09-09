import { BrowserDirectError, ManualBrowserPeer } from "./manual_webrtc.mjs";

const byId = (id) => document.getElementById(id);
let host;
let guest;

function show(target, value) {
  target.value = value instanceof BrowserDirectError ? `${value.code}: ${value.message}` : String(value);
}

byId("make-offer").addEventListener("click", async () => {
  try {
    host?.close();
    host = new ManualBrowserPeer({ gameId: byId("host-game").value, build: byId("host-build").value });
    byId("offer-out").value = await host.createOffer();
    show(byId("host-status"), "OFFER_READY — share it; this is not a connection claim");
  } catch (error) { show(byId("host-status"), error); }
});

byId("make-answer").addEventListener("click", async () => {
  try {
    guest?.close();
    guest = new ManualBrowserPeer({ gameId: byId("guest-game").value, build: byId("guest-build").value });
    byId("answer-out").value = await guest.acceptOffer(byId("offer-in").value.trim());
    show(byId("guest-status"), "ANSWER_READY — return it to the host; waiting for direct route");
    await guest.waitForOpen();
    show(byId("guest-status"), "DIRECT_CONNECTED");
    guest.receive(3600000).then((message) => show(byId("message-status"), `Guest received: ${JSON.stringify(message)}`)).catch(() => {});
  } catch (error) { show(byId("guest-status"), error); }
});

byId("accept-answer").addEventListener("click", async () => {
  try {
    if (!host) throw new BrowserDirectError("INVALID_STATE", "create a host offer first");
    await host.acceptAnswer(byId("answer-in").value.trim());
    await host.waitForOpen();
    show(byId("host-status"), "DIRECT_CONNECTED");
    host.receive(3600000).then((message) => show(byId("message-status"), `Host received: ${JSON.stringify(message)}`)).catch(() => {});
  } catch (error) { show(byId("host-status"), error); }
});

byId("send").addEventListener("click", () => {
  try {
    const peer = host?._channel?.readyState === "open" ? host : guest;
    if (!peer) throw new BrowserDirectError("DIRECT_CONNECTION_UNAVAILABLE", "neither side is connected");
    peer.send({ type: "DEMO_MESSAGE", text: byId("message").value });
    show(byId("message-status"), "MESSAGE_SENT_DIRECTLY");
  } catch (error) { show(byId("message-status"), error); }
});
