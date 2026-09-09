# Install and consume the AXM P2P capability

The `axm_p2p` reference layer is installable from a verified repository checkout. It has no runtime dependency outside the Python standard library and does not add a relay, account, cloud, or AXM service requirement.

## Install from a local checkout

```bash
python -m pip install --no-deps --no-build-isolation ./axm-city-multiplayer
```

For a reproducible integration, pin the checkout to a reviewed commit before installing it. The package version describes the public Python/CLI contract; a GitHub release is not implied until one actually exists.

## Use as a Python library

```python
from axm_p2p import AXMP2PLayer

network = AXMP2PLayer(game_id="my.game", build="ruleset-1")
host = network.host(public_host="203.0.113.50", port=28741)
print(host.invite_token)
```

Games should use `AXMP2PLayer` rather than importing the invite, HMAC, or UDP internals directly. The layer remains the replaceable transport boundary.

## Use as a command

Installing the project provides both equivalent entry points:

```bash
axm-p2p --help
python -m axm_p2p --help
```

Other local tools can inspect non-secret invite metadata without parsing Python object output:

```bash
axm-p2p show "AXMP2P1...." --json
```

The JSON view intentionally omits `session_key`. Consumers should preserve and pass the original invite token to the join operation instead of logging or reconstructing credential material.

## Offline boundary

Building and installing with `--no-build-isolation` uses the environment's existing packaging tools and does not resolve runtime dependencies. Direct play still requires a reachable peer endpoint; installation does not introduce an AXM relay fallback.

