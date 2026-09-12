# First-Join Integrity Notice

Status: **DRAFT POLICY TEXT**

This notice is intended to appear before a player's first AXM City human multiplayer match. It is deliberately short. It is not a replacement for technical documentation.

---

## Welcome to AXM City Multiplayer

This network is free to use.

AXM does not promise to make cheating impossible or constantly fight every new cheat. Instead, shared matches keep enough verified state and replay evidence to detect serious manipulation.

**If cheating is verified through this city-network connection, that connection can lose access to human matchmaking.**

You are not banned from AXM. Allowed network functions can still work, and games can still be played through AI/anomaly matchmaking. Your own household/private LAN multiplayer remains independent and still works according to the game itself.

AXM does not need to determine which household member, visitor, device owner or other person caused the violation. The system only records what the verified network/match evidence establishes.

**Human multiplayer is shared. Keep that state clean and enjoy it.**

`[ I UNDERSTAND • JOIN HUMAN MATCHMAKING ]`

---

## Acknowledgement receipt

A minimal local receipt may record the policy version that was shown:

```json
{
  "schema": "axm-city-integrity-ack/v1",
  "policyVersion": "axm-city-integrity/v1",
  "acknowledged": true,
  "acknowledgedAt": "<local timestamp>",
  "networkId": "<fabric identifier>"
}
```

The receipt exists to preserve source integrity: what rule was shown, which version it was, and whether the player acknowledged it.

It is not permission to collect unrelated personal data.

## Implementation notes

- Show this before first **city human matchmaking**, not before private LAN play.
- Do not hide the routing consequence in a long terms-of-service document.
- Do not call the consequence a conventional ban if the implementation is actually a change of matchmaking trust/routing state.
- Do not claim that every person at a physical location cheated.
- If policy wording materially changes, version it. Do not silently rewrite the historical receipt.
- AI/anomaly opponents must be identified as non-human; never secretly substitute an AI while claiming the opponent is human.