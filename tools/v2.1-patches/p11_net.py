# v2.2 — online play: Supabase Realtime cloud path + direct P2P + relay backup, weak-signal handling, visible status
import sys, os
P = sys.argv[1]
h = open(P, encoding='utf-8').read()
def rep(old, new, count=1):
    global h
    n = h.count(old); assert n == count, f'expected {count} got {n}: {old[:90]!r}'
    h = h.replace(old, new)

# 1) swap the network module (same API: host, join, send, expect, pending, close, active, shareLink, onStatus, onMessage)
a = h.index("\n'use strict';\n/* ================= SIGNAL 5 — ONLINE (lockstep) =================")
b = h.index("  return N;\n})();", a) + len("  return N;\n})();")
h = h[:a] + open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'net_v22.js'), encoding='utf-8').read().rstrip('\n') + h[b:]

# 2) status light + lobby line + weak-opponent notices
rep("  NET.onStatus = (s) => { const el = $('netDot'); if (!el) return; el.className = 'netdot ' + s; el.title = s === 'p2p' ? 'Direct connection' : s === 'relay' ? 'Relay connection' : 'Connecting…'; };",
    "  NET.onStatus = (s, info = {}) => {\n"
    "    const label = info.silent ? 'Opponent’s connection is weak — waiting…' : s === 'p2p' ? 'Direct connection' : s === 'cloud' ? 'Cloud connection' : s === 'relay' ? 'Backup relay connection' : 'Connecting…';\n"
    "    const ms = info.rtt && !info.silent && s !== 'connecting' ? ' · ' + info.rtt + ' ms' : '';\n"
    "    const el = $('netDot'); if (el) { el.className = 'netdot ' + (info.silent ? 'weak' : s); el.title = label + ms; el.setAttribute('aria-label', label); }\n"
    "    const ln = $('netLine'); if (ln) ln.textContent = (s === 'connecting' ? '⏳ Connecting to the game server…' : '🟢 ' + label + ms);\n"
    "    if (GAME.S && GAME.phase !== 'title' && !(GAME.S && GAME.S.over)) {\n"
    "      if (info.silent && !GAME.netWeak) { GAME.netWeak = true; toast('📶 ' + esc(OPP()) + '’s connection is weak — waiting for them to catch up…', 'bad'); }\n"
    "      else if (!info.silent && GAME.netWeak) { GAME.netWeak = false; toast('📶 ' + esc(OPP()) + ' is back online', 'good'); }\n"
    "    }\n"
    "  };")
rep("<p id=\"lobbyState\" style=\"margin-top:14px;color:#8fa9d8\">⏳ Waiting for a friend to join…</p></div>`",
    "<p id=\"lobbyState\" style=\"margin-top:14px;color:#8fa9d8\">⏳ Waiting for a friend to join…</p><p id=\"netLine\" style=\"margin:6px 0 0;font-size:13px;color:#9fd8c8\">⏳ Connecting to the game server…</p></div>`")
rep("<p style=\"text-align:center;font-size:12px;color:#8fa9d8\">If this takes long, check the code with your friend and make sure their room screen is still open.</p>`",
    "<p id=\"netLine\" style=\"text-align:center;font-size:13px;color:#9fd8c8;margin:0 0 6px\">⏳ Connecting to the game server…</p><p style=\"text-align:center;font-size:12px;color:#8fa9d8\">If this takes long, check the code with your friend and make sure their room screen is still open.</p>`")
# styles for the light (it had none, so it was invisible)
rep("\n#passfx{",
    "\n.netdot{display:inline-block;width:11px;height:11px;margin:0 6px;border-radius:50%;vertical-align:middle;background:#5b6b8c;box-shadow:0 0 0 2px #0b1a3e}"
    "\n.netdot.off{display:none} .netdot.p2p{background:#3ddc84} .netdot.cloud{background:#3fd1c4} .netdot.relay{background:#ffb21f}"
    "\n.netdot.connecting{background:#8fa9d8;animation:ndPulse 1s ease-in-out infinite} .netdot.weak{background:#ff4b4b;animation:ndPulse .7s ease-in-out infinite}"
    "\n@keyframes ndPulse{0%,100%{opacity:1}50%{opacity:.3}}"
    "\n#passfx{")
rep("const RULES_VERSION = '2.1.0';", "const RULES_VERSION = '2.1.0';\nconst NET_VERSION = '2.2';")

open(P, 'w', encoding='utf-8').write(h); print('ok')
