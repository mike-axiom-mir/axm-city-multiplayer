from __future__ import annotations

import argparse
import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from .invite import Invite, InviteError, create_invite, decode_invite

_MAX_BODY = 16 * 1024


def public_invite_view(invite: Invite, *, now: int | None = None) -> dict[str, Any]:
    """Project an invite into human-visible metadata without exposing session_key."""
    now = int(time.time() if now is None else now)
    return {
        "protocol": invite.protocol,
        "game": invite.game_id,
        "build": invite.build,
        "host": invite.host,
        "port": invite.port,
        "session": invite.session_id,
        "expiresAt": invite.expires_at,
        "secondsRemaining": max(0, invite.expires_at - now),
        "transport": "DIRECT_UDP_REFERENCE",
        "relay": False,
    }


def create_share_packet(payload: dict[str, Any], *, now: int | None = None) -> dict[str, Any]:
    try:
        token = create_invite(
            game_id=payload.get("game"),
            build=payload.get("build"),
            host=payload.get("host"),
            port=payload.get("port"),
            lifetime_seconds=payload.get("lifetimeSeconds", 3600),
            now=now,
        )
        invite = decode_invite(token, now=now)
    except (InviteError, TypeError) as exc:
        return {"status": "HELD", "code": "INVITE_INPUT_INVALID", "detail": str(exc)}
    return {
        "status": "READY_TO_SHARE",
        "token": token,
        "invite": public_invite_view(invite, now=now),
        "warning": "Anyone holding this token can attempt to join while it is valid.",
    }


def inspect_share_packet(payload: dict[str, Any], *, now: int | None = None) -> dict[str, Any]:
    token = payload.get("token")
    try:
        invite = decode_invite(token, now=now)
    except (InviteError, TypeError) as exc:
        return {"status": "HELD", "code": "INVITE_NOT_USABLE", "detail": str(exc)}
    return {
        "status": "VALID",
        "invite": public_invite_view(invite, now=now),
        "nextAction": "Pass the unchanged token to the native AXMP2PLayer/CLI to attempt direct connection.",
        "browserCanConnect": False,
    }


_PAGE = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="dark">
<title>AXM Direct Invite Desk</title>
<style>
:root{font-family:Inter,ui-sans-serif,system-ui,sans-serif;background:#0a0d12;color:#edf3ff;--panel:#121821;--line:#293548;--muted:#91a0b5;--accent:#88c7ff;--ok:#9de6bd;--hold:#ffd494}
*{box-sizing:border-box}body{margin:0;min-height:100vh;background:radial-gradient(circle at 70% -10%,#172639 0,transparent 42%),#0a0d12}
main{width:min(1040px,calc(100% - 28px));margin:auto;padding:34px 0 54px}.eyebrow{letter-spacing:.16em;text-transform:uppercase;color:var(--accent);font-size:.72rem;font-weight:800}
h1{font-size:clamp(2rem,7vw,4.2rem);line-height:.95;margin:.35rem 0 .7rem;max-width:760px}p{color:var(--muted);line-height:1.55}.truth{display:flex;gap:10px;flex-wrap:wrap;margin:18px 0 28px}.pill{border:1px solid var(--line);border-radius:999px;padding:8px 12px;font-size:.76rem;font-weight:800;letter-spacing:.06em}.pill strong{color:var(--ok)}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}.panel{background:linear-gradient(180deg,#141b25,#0f141c);border:1px solid var(--line);border-radius:22px;padding:20px;box-shadow:0 16px 50px #0006}.panel h2{margin:.1rem 0 .25rem;font-size:1.35rem}.hint{font-size:.9rem;margin-top:0}
label{display:block;font-size:.78rem;color:#b8c5d8;font-weight:800;margin:14px 0 7px}input,textarea,button{font:inherit}input,textarea{width:100%;border:1px solid #34445c;background:#090d13;color:#fff;border-radius:12px;padding:12px 13px;outline:none}input:focus,textarea:focus,button:focus-visible{border-color:var(--accent);box-shadow:0 0 0 3px #65b8ff35}textarea{min-height:132px;resize:vertical;font-family:ui-monospace,SFMono-Regular,monospace;font-size:.78rem;line-height:1.45}
.row{display:grid;grid-template-columns:1fr 1fr;gap:10px}.actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:15px}button{border:1px solid #46698c;background:#1a527c;color:#fff;border-radius:12px;padding:11px 14px;font-weight:850;cursor:pointer}button.secondary{background:#141b24;border-color:#34445c;color:#d8e3f1}button:disabled{opacity:.45;cursor:not-allowed}
.result{display:none;margin-top:16px;border-top:1px solid var(--line);padding-top:16px}.result.show{display:block}.status{font-size:.76rem;font-weight:900;letter-spacing:.08em;text-transform:uppercase}.status.ok{color:var(--ok)}.status.hold{color:var(--hold)}
.meta{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;margin:12px 0}.meta div{background:#0b1017;border:1px solid #233044;border-radius:11px;padding:10px}.meta b{display:block;font-size:.68rem;color:#8495ac;text-transform:uppercase;letter-spacing:.08em;margin-bottom:3px}.meta span{overflow-wrap:anywhere;font-size:.9rem}
.token{font-family:ui-monospace,SFMono-Regular,monospace;word-break:break-all;background:#080c11;border:1px dashed #38506d;border-radius:12px;padding:12px;font-size:.72rem;line-height:1.45;color:#d9edff}.warning{font-size:.82rem;color:#ffd9a6}.foot{margin-top:22px;border-left:3px solid #34445c;padding-left:14px;font-size:.84rem}
@media(max-width:760px){main{padding-top:22px}.grid{grid-template-columns:1fr}.panel{padding:16px}.row{grid-template-columns:1fr}.meta{grid-template-columns:1fr 1fr}h1{font-size:2.45rem}}
@media(prefers-reduced-motion:reduce){*{scroll-behavior:auto!important;transition:none!important}}
</style>
</head>
<body><main>
<div class="eyebrow">AXM · local / direct only</div>
<h1>Direct Invite Desk</h1>
<p>Create or inspect the same <strong>AXMP2P1</strong> token used by the native reference core. The desk never relays gameplay and the browser never pretends it can open the UDP connection.</p>
<div class="truth"><span class="pill"><strong>LOCAL</strong> loopback UI</span><span class="pill"><strong>NO</strong> account</span><span class="pill"><strong>NO</strong> relay</span><span class="pill"><strong>DISPLAY ≠ CONNECTED</strong></span></div>
<div class="grid">
<section class="panel" aria-labelledby="host-title"><h2 id="host-title">Host · make invite</h2><p class="hint">Generate a token, copy it, send it through any channel you choose.</p>
<label for="game">Game ID</label><input id="game" value="axm.example" autocomplete="off">
<label for="build">Build / ruleset</label><input id="build" value="build-001" autocomplete="off">
<div class="row"><div><label for="host">Reachable host</label><input id="host" value="203.0.113.50" autocomplete="off"></div><div><label for="port">UDP port</label><input id="port" type="number" min="1" max="65535" value="28741"></div></div>
<label for="life">Invite lifetime</label><select id="life" style="width:100%;padding:12px;border-radius:12px;background:#090d13;color:#fff;border:1px solid #34445c"><option value="900">15 minutes</option><option value="3600" selected>1 hour</option><option value="14400">4 hours</option></select>
<div class="actions"><button id="create">Create share token</button><button id="copy" class="secondary" disabled>Copy token</button></div>
<div id="hostResult" class="result" aria-live="polite"><div id="hostStatus" class="status"></div><div id="hostMeta" class="meta"></div><div id="hostToken" class="token"></div><p id="hostWarning" class="warning"></p></div>
</section>
<section class="panel" aria-labelledby="join-title"><h2 id="join-title">Guest · inspect invite</h2><p class="hint">Validate before handing the unchanged token to a native game or CLI.</p>
<label for="joinToken">Paste invite</label><textarea id="joinToken" spellcheck="false" placeholder="AXMP2P1...."></textarea>
<div class="actions"><button id="inspect">Validate invite</button><button id="copyCmd" class="secondary" disabled>Copy native join command</button></div>
<div id="joinResult" class="result" aria-live="polite"><div id="joinStatus" class="status"></div><div id="joinMeta" class="meta"></div><p id="joinNext" class="warning"></p></div>
<p class="foot">Browser boundary: this page can create and validate tokens only. Direct connection remains the native <code>AXMP2PLayer</code>/UDP adapter. If the route is unreachable, the core is allowed to fail rather than hiding that behind paid infrastructure.</p>
</section></div>
</main>
<script>
const $=id=>document.getElementById(id); let lastToken=''; let lastInvite=null;
function esc(s){return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function meta(target,m){target.innerHTML=['game','build','host','port','session','secondsRemaining'].map(k=>`<div><b>${esc(k==='secondsRemaining'?'expires in':k)}</b><span>${esc(k==='secondsRemaining'?m[k]+'s':m[k])}</span></div>`).join('')}
async function post(path,payload){let r=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});return r.json()}
function status(el,text,ok){el.textContent=text;el.className='status '+(ok?'ok':'hold')}
$('create').onclick=async()=>{const r=await post('/api/create',{game:$('game').value.trim(),build:$('build').value.trim(),host:$('host').value.trim(),port:Number($('port').value),lifetimeSeconds:Number($('life').value)});$('hostResult').classList.add('show');const ok=r.status==='READY_TO_SHARE';status($('hostStatus'),r.status,ok);if(ok){lastToken=r.token;$('hostToken').textContent=r.token;meta($('hostMeta'),r.invite);$('hostWarning').textContent=r.warning;$('copy').disabled=false;$('joinToken').value=r.token}else{$('hostToken').textContent='';$('hostMeta').innerHTML='';$('hostWarning').textContent=r.detail;$('copy').disabled=true}};
$('inspect').onclick=async()=>{const token=$('joinToken').value.trim();const r=await post('/api/inspect',{token});$('joinResult').classList.add('show');const ok=r.status==='VALID';status($('joinStatus'),r.status,ok);if(ok){lastInvite=r.invite;meta($('joinMeta'),r.invite);$('joinNext').textContent='Validated, not connected. '+r.nextAction;$('copyCmd').disabled=false}else{$('joinMeta').innerHTML='';$('joinNext').textContent=r.detail;$('copyCmd').disabled=true}};
function shellQuote(text){return `'${String(text).replace(/'/g, `'"'"'`)}'`}
async function copyText(text,button){try{await navigator.clipboard.writeText(text);const old=button.textContent;button.textContent='Copied';setTimeout(()=>button.textContent=old,900)}catch{button.textContent='Copy unavailable'}}
$('copy').onclick=()=>copyText(lastToken,$('copy'));
$('copyCmd').onclick=()=>{if(!lastInvite)return;copyText(`python -m axm_p2p.cli join ${shellQuote($('joinToken').value.trim())} --game ${shellQuote(lastInvite.game)} --build ${shellQuote(lastInvite.build)}`,$('copyCmd'))};
$('joinToken').addEventListener('keydown',e=>{if((e.ctrlKey||e.metaKey)&&e.key==='Enter')$('inspect').click()});
</script></body></html>'''


class InviteDeskHandler(BaseHTTPRequestHandler):
    server_version = "AXMInviteDesk/0.1"

    def log_message(self, format: str, *args: Any) -> None:
        return

    def _headers(self, status: int, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'")
        self.end_headers()

    def do_GET(self) -> None:
        if self.path != "/":
            self._headers(404, "text/plain; charset=utf-8")
            self.wfile.write(b"not found")
            return
        body = _PAGE.encode("utf-8")
        self._headers(200, "text/html; charset=utf-8")
        self.wfile.write(body)

    def do_POST(self) -> None:
        if self.path not in {"/api/create", "/api/inspect"}:
            self._headers(404, "application/json")
            self.wfile.write(b'{"status":"HELD","code":"NOT_FOUND"}')
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        if length <= 0 or length > _MAX_BODY or self.headers.get("Content-Type", "").split(";", 1)[0].strip() != "application/json":
            self._headers(400, "application/json")
            self.wfile.write(b'{"status":"HELD","code":"REQUEST_INVALID"}')
            return
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            if type(payload) is not dict:
                raise ValueError
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
            self._headers(400, "application/json")
            self.wfile.write(b'{"status":"HELD","code":"REQUEST_INVALID"}')
            return
        result = create_share_packet(payload) if self.path == "/api/create" else inspect_share_packet(payload)
        body = json.dumps(result, separators=(",", ":")).encode("utf-8")
        self._headers(200, "application/json")
        self.wfile.write(body)


def serve(*, port: int = 8765) -> None:
    server = ThreadingHTTPServer(("127.0.0.1", port), InviteDeskHandler)
    print(f"AXM Direct Invite Desk: http://127.0.0.1:{server.server_port}/")
    print("Loopback only. This UI does not relay or connect gameplay traffic.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve the local-only AXM Direct Invite Desk")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    if not (0 <= args.port <= 65535):
        parser.error("--port must be 0..65535")
    serve(port=args.port)


if __name__ == "__main__":
    main()
