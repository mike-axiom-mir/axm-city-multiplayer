# AGENTS.md

## Purpose

This repository researches and builds AXM City Multiplayer: a local-first multiplayer fabric using dedicated fixed networking nodes, deterministic client-side simulation, minimal authoritative state exchange, and explicit truth gates.

These instructions apply to every human or AI contributor working in this repository.

## Mandatory lane discipline

### One chat = one PR lane

1. Every working chat/session claims exactly **one** branch and **one** pull-request lane before making substantive changes.
2. If the current chat already owns an open PR lane, continue in that lane. Do not create a second branch or PR for the same chat.
3. Do not spread one chat's work across sibling PRs, experimental branches, or opportunistic side branches.
4. If new ideas exceed the active lane's scope, record them in a backlog or decision log and leave implementation for a future chat/PR lane.
5. Do not make substantive commits directly to `main`. The only allowed exception is unavoidable repository bootstrap when an empty repository has no branch from which a PR lane can be created.
6. Do not merge, close, rebase away, or declare CANON unless Mike explicitly requests that action or the active task explicitly grants it.
7. Before editing overlapping work, inspect the current branch/main state and preserve both valid directions. Never silently drop work to make a diff easier.

Recommended branch form:

```text
axm/chat-<bounded-topic>-YYYY-MM-DD
```

The PR description should state the lane boundary and list deferred work rather than expanding scope.

## Truth discipline

Use these status words deliberately:

- **HYPOTHESIS**: plausible idea; not yet measured.
- **RESEARCHED**: supported by external documentation or prior art, but not demonstrated by AXM.
- **MEASURED**: observed in an AXM experiment with retained evidence.
- **IMPLEMENTED**: code or hardware path exists, but may not yet satisfy its acceptance gate.
- **VERIFIED**: the defined gate passed with retained evidence.

Never upgrade one status into another because the result feels likely.

For performance, capacity, range, latency, cost, anti-cheat accuracy, or city-scale claims, preserve the measurement conditions and evidence. Prefer admission gates driven by live metrics over hardcoded promises.

## Core architecture roots

Preserve these unless a PR explicitly exists to challenge one of them:

- The city backbone uses **dedicated, fixed, serious nodes**. Participant phones are clients, not opportunistic mesh relays.
- Coverage grows through opt-in placement of fixed nodes at suitable homes, shops, roofs, community locations, or other sites.
- Optimize node hardware for legal usable range, throughput, latency, concurrency, stability, power, and cost per useful coverage area.
- Player hardware should perform as much rendering, simulation, audio, UI, and deterministic game work as safely possible.
- Shared infrastructure should coordinate only what must be shared: ordering, authenticated events, authoritative state changes, hashes, checkpoints, repair, routing, and integrity evidence.
- Do not require cloud execution when local execution is sufficient.
- Accounts may add profiles, stats, identity, achievements, continuity, friends, rankings, and related features. Basic play should not become a toll booth merely because accounts exist.
- User data is local-first. Prefer user-owned cryptographic identity and portable local state over central ownership of identity.
- Private household/local LAN multiplayer remains independent of city matchmaking. City integrity state must not disable a user's own LAN play.
- Cheating is not treated as perfectly preventable. Preserve deterministic record/replay evidence and bounded integrity routing.
- AI may assist cheat review, anomaly classification, or replay inspection, but AI alone is not proof. Objective/replayable evidence is the truth boundary.
- A verified integrity violation can remove **human-match trust** from the relevant city-network identity/access boundary and route future city matches to AI/anomaly matchmaking instead. This is routing/containment, not a claim of ownership over the player.
- Do not claim that every person in a household or location cheated. Only claim what the evidence establishes about the network event or access boundary.
- The system does not owe manual investigation into who inside a household caused a verified violation. If appeals or automated re-verification exist, they are an optional system feature, not an invented promise.

## Safety, consent, and privacy

- Becoming a signal/node location is opt-in.
- Installing a game must never silently turn a user's phone or computer into city infrastructure.
- Collect the least identity information needed for the feature.
- Do not dox, expose private identity, or encourage real-world harassment of cheaters.
- In-game anomaly/cheater consequences may be playful, but keep them inside the game/network context.
- Unlisted or non-advertised radio presence is not security. Authentication and cryptographic trust are the security boundary.

## Change discipline

Before claiming completion, report:

1. what changed,
2. what was tested or measured,
3. what remains hypothesis,
4. what was intentionally deferred,
5. whether merge/CANON was performed.

No fake done. No silent rewrite. No scope laundering.