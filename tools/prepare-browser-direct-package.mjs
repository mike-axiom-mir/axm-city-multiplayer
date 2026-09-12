import { createHash } from "node:crypto";
import { lstat, readFile, unlink, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const packageDir = path.join(repoRoot, "packages", "browser-direct");
const generatedNames = ["manual_webrtc.mjs", "LICENSE", "THIRD_PARTY.json", "capability.json", "PROVENANCE.json"];
const sourceCommit = "16e17183ac20392e00f565492b5ccf067188f9fa";
const packagingCommit = "256f670d832633159a3d91b9e4f522a438e966b4";
const expected = {
  source: {
    path: "browser/manual_webrtc.mjs",
    gitBlob: "56e418fca2f22fd6b3a836e332d0f055994046b4",
  },
  license: {
    path: "LICENSE",
    gitBlob: "261eeb9e9f8b2b4b0d119366dda99c6fd7d35c64",
  },
  thirdParty: {
    path: "THIRD_PARTY.json",
    gitBlob: "58eef537cf04fb4f0cb3d66128f61a081d2d84c1",
  },
};

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

async function readBoundSource(entry) {
  const fullPath = path.join(repoRoot, entry.path);
  const stat = await lstat(fullPath);
  if (!stat.isFile() || stat.isSymbolicLink()) {
    throw new Error(`${entry.path} must be a regular non-symlink file`);
  }
  const bytes = await readFile(fullPath);
  const actualBlob = gitBlobSha1(bytes);
  if (actualBlob !== entry.gitBlob) {
    throw new Error(`${entry.path} Git blob drift: expected ${entry.gitBlob}, got ${actualBlob}`);
  }
  return { bytes, sha256: sha256(bytes), gitBlob: actualBlob };
}

async function cleanup() {
  for (const name of generatedNames) {
    try {
      await unlink(path.join(packageDir, name));
    } catch (error) {
      if (error?.code !== "ENOENT") throw error;
    }
  }
}

if (process.argv.includes("--cleanup")) {
  await cleanup();
  process.exit(0);
}

await cleanup();
const source = await readBoundSource(expected.source);
const license = await readBoundSource(expected.license);
const thirdParty = await readBoundSource(expected.thirdParty);

const provider = await import(`${pathToFileURL(path.join(repoRoot, expected.source.path)).href}?package-prepack=${source.sha256}`);
const descriptor = provider.describeBrowserDirectCapability?.();
const expectedDescriptor = {
  id: "axm.browser-direct/v1",
  signaling: "manual-copy-paste",
  transport: "WebRTC-DataChannel",
  iceServers: [],
  relayFallback: false,
  accountRequired: false,
  failureCode: "DIRECT_CONNECTION_UNAVAILABLE",
  limits: { tokenBytes: 65536, messageBytes: 65536 },
};
if (stableJson(descriptor) !== stableJson(expectedDescriptor)) {
  throw new Error("browser direct executable descriptor drifted from the package contract");
}

const capability = {
  schema: "axm.city-multiplayer.browser-direct-package-capability/v1",
  id: "axm.browser-direct/v1",
  status: "EXPERIMENTAL",
  runtime: {
    kind: "browser-esm",
    requirements: ["Web Crypto", "RTCPeerConnection", "WebRTC DataChannel"],
    networkServiceRequired: false,
  },
  provider: descriptor,
  operations: [
    "createOffer",
    "acceptOffer",
    "acceptAnswer",
    "waitForOpen",
    "send",
    "receive",
    "close",
    "encodeBrowserDirectToken",
    "decodeBrowserDirectToken",
  ],
  authority: {
    automaticInstall: false,
    automaticExecution: false,
    relayFallback: false,
    matchmaking: false,
    merge: false,
    canon: false,
  },
};

const provenance = {
  schema: "axm.city-multiplayer.browser-direct-package-provenance/v1",
  repository: "mike-axiom-mir/axm-city-multiplayer",
  prerequisite: {
    pullRequest: 23,
    commit: sourceCommit,
  },
  packagingLineage: {
    pullRequest: 18,
    commit: packagingCommit,
  },
  providerSource: {
    path: expected.source.path,
    gitBlob: source.gitBlob,
    sha256: source.sha256,
    bytes: source.bytes.length,
  },
  license: {
    id: "Apache-2.0",
    path: expected.license.path,
    gitBlob: license.gitBlob,
    sha256: license.sha256,
    bytes: license.bytes.length,
  },
  thirdParty: {
    path: expected.thirdParty.path,
    gitBlob: thirdParty.gitBlob,
    sha256: thirdParty.sha256,
    bytes: thirdParty.bytes.length,
  },
  capabilitySha256: sha256(Buffer.from(stableJson(capability), "utf8")),
  authority: {
    integrityOnly: true,
    authorshipAuthenticated: false,
    automaticInstall: false,
    automaticExecution: false,
    release: false,
    merge: false,
    canon: false,
  },
};

await writeFile(path.join(packageDir, "manual_webrtc.mjs"), source.bytes);
await writeFile(path.join(packageDir, "LICENSE"), license.bytes);
await writeFile(path.join(packageDir, "THIRD_PARTY.json"), thirdParty.bytes);
await writeFile(path.join(packageDir, "capability.json"), `${JSON.stringify(capability, null, 2)}\n`, "utf8");
await writeFile(path.join(packageDir, "PROVENANCE.json"), `${JSON.stringify(provenance, null, 2)}\n`, "utf8");
