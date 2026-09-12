# AXM Direct Invite Desk

The Direct Invite Desk is a local-only browser realization of the existing `AXMP2P1` invite contract.

Run:

```bash
python -m axm_p2p.invite_desk
```

Then open `http://127.0.0.1:8765/`.

The desk can create a share token and validate a pasted token before a native game or CLI attempts connection. It deliberately does **not** open UDP from the browser, start a gameplay host, provide rendezvous, relay traffic, require an account, or claim that a valid token means the route is reachable. The token itself contains the session secret required by the existing direct-invite contract; anyone holding the token can attempt to join until expiry, so the UI treats it as share-by-choice bearer material.

The server binds only to loopback, loads no external resources, returns `Cache-Control: no-store`, and does not expose the session key as separate browser metadata. `DISPLAY ≠ CONNECTED` is the visible truth boundary.
