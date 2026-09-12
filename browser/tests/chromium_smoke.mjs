import assert from "node:assert/strict";
import { chromium } from "playwright";

const origin = process.env.AXM_BROWSER_ORIGIN || "http://127.0.0.1:8765/browser/test_harness.html";
const browser = await chromium.launch({ headless: true });
try {
  const host = await browser.newPage();
  const guest = await browser.newPage();
  await Promise.all([host.goto(origin), guest.goto(origin)]);
  await Promise.all([host.waitForFunction(() => window.ready), guest.waitForFunction(() => window.ready)]);
  const offer = await host.evaluate(async () => {
    window.peer = new window.AXM.ManualBrowserPeer({ gameId: "axm.browser-smoke", build: "v1" });
    return window.peer.createOffer({ expiresInSeconds: 60 });
  });
  const answer = await guest.evaluate(async (token) => {
    window.peer = new window.AXM.ManualBrowserPeer({ gameId: "axm.browser-smoke", build: "v1" });
    return window.peer.acceptOffer(token);
  }, offer);
  await host.evaluate((token) => window.peer.acceptAnswer(token), answer);
  await Promise.all([
    host.evaluate(() => window.peer.waitForOpen()),
    guest.evaluate(() => window.peer.waitForOpen()),
  ]);
  await host.evaluate(() => window.peer.send({ type: "PING", tick: 11 }));
  assert.deepEqual(await guest.evaluate(() => window.peer.receive()), { tick: 11, type: "PING" });
  await guest.evaluate(() => window.peer.send({ type: "PONG", tick: 11 }));
  assert.deepEqual(await host.evaluate(() => window.peer.receive()), { tick: 11, type: "PONG" });
  console.log("CHROMIUM_DIRECT_DATACHANNEL_PASS");
} finally {
  await browser.close();
}
