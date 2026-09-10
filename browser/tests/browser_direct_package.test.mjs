import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import { mkdtemp, mkdir, readFile, rm, writeFile, access } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
const packageDir = path.join(repoRoot, "packages", "browser-direct");
const npm = process.platform === "win32" ? "npm.cmd" : "npm";
const generatedNames = ["manual_webrtc.mjs", "LICENSE", "THIRD_PARTY.json", "capability.json", "PROVENANCE.json"];

function sha256(bytes) {
  return createHash("sha256").update(bytes).digest("hex");
}

function gitBlobSha1(bytes) {
  return createHash("sha1")
    .update(Buffer.from(`blob ${bytes.length}\0`, "utf8"))
    .update(bytes)
    .digest("hex");
}

function stableJson(value) {
  if (value === null || typeof value !== "object") return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(stableJson).join(",")}]`;
  return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${stableJson(value[key])}`).join(",")}}`;
}

function run(command, args, options = {}) {
  return execFileSync(command, args, {
    cwd: repoRoot,
    encoding: "utf8",
    stdio: ["ignore", "pipe", "pipe"],
    env: {
      ...process.env,
      npm_config_audit: "false",
      npm_config_fund: "false",
      npm_config_update_notifier: "false",
    },
    ...options,
  });
}

async function assertGeneratedCleaned() {
  for (const name of generatedNames) {
    await assert.rejects(access(path.join(packageDir, name)), (error) => error?.code === "ENOENT");
  }
}

function packTo(directory) {
  const text = run(npm, ["pack", packageDir, "--pack-destination", directory, "--json"]);
  const result = JSON.parse(text);
  assert.equal(result.length, 1);
  return result[0];
}

test("browser direct adapter packs deterministically and works from a clean offline consumer", async (t) => {
  const tempRoot = await mkdtemp(path.join(os.tmpdir(), "axm-browser-direct-package-"));
  t.after(async () => {
    run(process.execPath, ["tools/prepare-browser-direct-package.mjs", "--cleanup"]);
    await rm(tempRoot, { recursive: true, force: true });
  });

  run(process.execPath, ["tools/prepare-browser-direct-package.mjs", "--cleanup"]);
  await assertGeneratedCleaned();

  const firstDir = path.join(tempRoot, "pack-a");
  const secondDir = path.join(tempRoot, "pack-b");
  await mkdir(firstDir);
  await mkdir(secondDir);
  const first = packTo(firstDir);
  await assertGeneratedCleaned();
  const second = packTo(secondDir);
  await assertGeneratedCleaned();

  assert.equal(first.filename, second.filename);
  const firstTarball = await readFile(path.join(firstDir, first.filename));
  const secondTarball = await readFile(path.join(secondDir, second.filename));
  assert.equal(sha256(firstTarball), sha256(secondTarball), "two packs must be byte-identical in one toolchain");

  const expectedFiles = [
    "LICENSE",
    "PROVENANCE.json",
    "README.md",
    "THIRD_PARTY.json",
    "capability.json",
    "manual_webrtc.mjs",
    "package.json",
  ];
  assert.deepEqual(first.files.map((entry) => entry.path).sort(), expectedFiles);

  const consumerDir = path.join(tempRoot, "consumer");
  await mkdir(consumerDir);
  await writeFile(path.join(consumerDir, "package.json"), '{"name":"axm-browser-direct-consumer-fixture","private":true,"type":"module"}\n');
  run(npm, [
    "install",
    "--offline",
    "--ignore-scripts",
    "--no-audit",
    "--no-fund",
    path.join(firstDir, first.filename),
  ], { cwd: consumerDir });

  const installedDir = path.join(consumerDir, "node_modules", "axm-city-browser-direct");
  const providerBytes = await readFile(path.join(repoRoot, "browser", "manual_webrtc.mjs"));
  const installedBytes = await readFile(path.join(installedDir, "manual_webrtc.mjs"));
  assert.deepEqual(installedBytes, providerBytes, "package must carry exact provider bytes");

  const provenance = JSON.parse(await readFile(path.join(installedDir, "PROVENANCE.json"), "utf8"));
  assert.equal(provenance.schema, "axm.city-multiplayer.browser-direct-package-provenance/v1");
  assert.equal(provenance.prerequisite.pullRequest, 14);
  assert.equal(provenance.prerequisite.commit, "4f317c7c3e1b163a48dcbff3ea612bc04846cb1a");
  assert.equal(provenance.providerSource.path, "browser/manual_webrtc.mjs");
  assert.equal(provenance.providerSource.gitBlob, gitBlobSha1(installedBytes));
  assert.equal(provenance.providerSource.sha256, sha256(installedBytes));
  assert.equal(provenance.authority.authorshipAuthenticated, false);
  assert.equal(provenance.authority.automaticInstall, false);
  assert.equal(provenance.authority.automaticExecution, false);
  assert.equal(provenance.authority.merge, false);
  assert.equal(provenance.authority.canon, false);

  const capability = JSON.parse(await readFile(path.join(installedDir, "capability.json"), "utf8"));
  assert.equal(capability.id, "axm.browser-direct/v1");
  assert.equal(capability.status, "EXPERIMENTAL");
  assert.equal(capability.provider.transport, "WebRTC-DataChannel");
  assert.deepEqual(capability.provider.iceServers, []);
  assert.equal(capability.provider.relayFallback, false);
  assert.equal(capability.authority.automaticExecution, false);
  assert.equal(provenance.capabilitySha256, sha256(Buffer.from(stableJson(capability), "utf8")));

  const consumerScript = path.join(consumerDir, "consume.mjs");
  await writeFile(consumerScript, `
import {
  BrowserDirectError,
  ManualBrowserPeer,
  decodeBrowserDirectToken,
  describeBrowserDirectCapability,
  encodeBrowserDirectToken,
} from "axm-city-browser-direct";
const descriptor = describeBrowserDirectCapability();
const expiresAt = Math.floor(Date.now() / 1000) + 120;
const body = {
  protocol: "axm.browser-direct/v1",
  kind: "offer",
  gameId: "axm.package-consumer",
  build: "build-1",
  sessionId: "session-1",
  expiresAt,
  sdp: "v=0\\r\\n",
};
const token = await encodeBrowserDirectToken(body);
const decoded = await decodeBrowserDirectToken(token, "offer", { gameId: body.gameId, build: body.build });
let absenceCode = null;
try {
  new ManualBrowserPeer({ gameId: body.gameId, build: body.build });
} catch (error) {
  if (!(error instanceof BrowserDirectError)) throw error;
  absenceCode = error.code;
}
console.log(JSON.stringify({ descriptor, decoded, absenceCode }));
`);
  const consumed = JSON.parse(run(process.execPath, [consumerScript], { cwd: consumerDir }));
  assert.equal(consumed.descriptor.id, "axm.browser-direct/v1");
  assert.equal(consumed.descriptor.relayFallback, false);
  assert.deepEqual(consumed.decoded, {
    build: "build-1",
    expiresAt: consumed.decoded.expiresAt,
    gameId: "axm.package-consumer",
    kind: "offer",
    protocol: "axm.browser-direct/v1",
    sdp: "v=0\r\n",
    sessionId: "session-1",
  });
  assert.equal(consumed.absenceCode, "WEBRTC_UNAVAILABLE", "non-browser consumers must fail cleanly without RTCPeerConnection");
});
