import assert from "node:assert/strict";
import fs from "node:fs/promises";
import { chromium } from "playwright";

const origin = process.env.AXM_BROWSER_DESK_ORIGIN || "http://127.0.0.1:8765/browser/";
const artifactDir = process.env.AXM_BROWSER_ARTIFACT_DIR || "browser-artifacts";
await fs.mkdir(artifactDir, { recursive: true });

const browser = await chromium.launch({ headless: true });
try {
  const host = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  const guest = await browser.newPage({ viewport: { width: 390, height: 844 } });
  const errors = [];
  for (const [name, page] of [["host", host], ["guest", guest]]) {
    page.on("pageerror", (error) => errors.push(`${name}:page:${error.message}`));
    page.on("console", (message) => { if (message.type() === "error") errors.push(`${name}:console:${message.text()}`); });
  }

  await Promise.all([host.goto(origin), guest.goto(origin)]);
  await host.click("#role-host");
  await guest.click("#role-guest");
  assert.equal(await host.locator("#host-card").isVisible(), true);
  assert.equal(await host.locator("#guest-card").isVisible(), false);
  assert.equal(await guest.locator("#guest-card").isVisible(), true);
  assert.equal(await guest.locator("#host-card").isVisible(), false);

  await host.click("#make-offer");
  await host.waitForFunction(() => document.querySelector("#host-status")?.dataset.code === "OFFER_READY");
  const offer = await host.inputValue("#offer-out");
  assert.match(offer, /^AXMWEBRTC1\./u);

  await guest.fill("#offer-in", offer);
  await guest.click("#make-answer");
  await guest.waitForFunction(() => document.querySelector("#guest-status")?.dataset.code === "ANSWER_READY");
  const answer = await guest.inputValue("#answer-out");
  assert.match(answer, /^AXMWEBRTC1\./u);

  await host.fill("#answer-in", answer);
  await host.click("#accept-answer");
  await Promise.all([
    host.waitForFunction(() => document.body.dataset.directState === "connected"),
    guest.waitForFunction(() => document.body.dataset.directState === "connected"),
  ]);
  assert.match(await host.locator("#host-status").innerText(), /DIRECT_CONNECTED/u);
  assert.match(await guest.locator("#guest-status").innerText(), /DIRECT_CONNECTED/u);

  await host.fill("#message", "experience ping");
  await host.click("#send");
  await guest.waitForFunction(() => document.querySelector("#message-status")?.dataset.code === "DIRECT_MESSAGE_RECEIVED");
  assert.match(await guest.locator("#message-status").innerText(), /experience ping/u);

  await guest.fill("#message", "experience pong");
  await guest.click("#send");
  await host.waitForFunction(() => document.querySelector("#message-status")?.dataset.code === "DIRECT_MESSAGE_RECEIVED");
  assert.match(await host.locator("#message-status").innerText(), /experience pong/u);

  await host.screenshot({ path: `${artifactDir}/browser-direct-host-desktop.png`, fullPage: true });
  await guest.screenshot({ path: `${artifactDir}/browser-direct-guest-mobile.png`, fullPage: true });

  const guestOverflow = await guest.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  const hostOverflow = await host.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  assert.ok(guestOverflow <= 0, `mobile horizontal overflow: ${guestOverflow}px`);
  assert.ok(hostOverflow <= 0, `desktop horizontal overflow: ${hostOverflow}px`);
  assert.match(await guest.locator(".truth").innerText(), /NO STUN, TURN, RELAY/iu);
  assert.equal(errors.length, 0, errors.join("\n"));
  console.log("CHROMIUM_BROWSER_DIRECT_EXPERIENCE_PASS");
} finally {
  await browser.close();
}
