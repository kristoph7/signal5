# Batch 1 / UI: 20% Collapse line on the Integrity bars + danger state + one-time warning toast
import sys
P = sys.argv[1]
h = open(P, encoding='utf-8').read()
def rep(old, new, count=1):
    global h
    n = h.count(old); assert n == count, f'expected {count} got {n}: {old[:90]!r}'
    h = h.replace(old, new)

rep(".ibar .tube::after{content:'';position:absolute;top:0;bottom:0;left:50%;border-left:2px dashed #ffd23a66}",
    ".ibar .tube::after{content:'';position:absolute;top:0;bottom:0;left:50%;border-left:2px dashed #ffd23a66}"
    " .ibar .tube::before{content:'';position:absolute;top:-1px;bottom:-1px;left:20%;border-left:3px solid #ff3b3bdd;z-index:2;box-shadow:0 0 6px #ff3b3b}"
    " .ibar.danger .tube{animation:ibDanger .9s ease-in-out infinite}"
    " .ibar.danger .pc{color:#ff6b5a}"
    " @keyframes ibDanger{0%,100%{box-shadow:0 0 0 #ff3b3b00}50%{box-shadow:0 0 12px #ff3b3bcc}}")
rep("el.querySelector('.pc').textContent = pc.toFixed(0) + '%'; el.querySelector('.fill').style.width = pc + '%';",
    "el.querySelector('.pc').textContent = pc.toFixed(0) + '%'; el.querySelector('.fill').style.width = pc + '%';\n"
    "    const danger = S.phase === 'play' && pc < KO_FLOOR + 10; el.classList.toggle('danger', danger);\n"
    "    if (danger && !(GAME.koWarned || (GAME.koWarned = {}))[i]) { GAME.koWarned[i] = 1; toast(i === 0 ? '⚠️ Your Integrity is near ' + KO_FLOOR + '% — below the red line your barangay COLLAPSES (instant loss). Repair and evacuate!' : '☠ ' + esc(OPP()) + ' is near the ' + KO_FLOOR + '% Collapse line — one big hit could knock them out!', i === 0 ? 'bad' : 'gold'); }")
rep("  S.phase = 'play'; GAME.phase = 'wait';\n", "  S.phase = 'play'; GAME.phase = 'wait'; GAME.koWarned = {};\n")
open(P, 'w', encoding='utf-8').write(h); print('ok2')
