# v2.1.1 — phone (portrait) layout fixes found in the UI audit
import sys
P = sys.argv[1]
h = open(P, encoding='utf-8').read()
def rep(old, new, count=1):
    global h
    n = h.count(old); assert n == count, f'expected {count} got {n}: {old[:90]!r}'
    h = h.replace(old, new)

# 1) card panel was 44vw wide (~170 px on a phone): text overlapped the TAP A TARGET button
rep('[data-layout="port"] #inspect{bottom:auto;top:calc(var(--subB) + 8px)}',
    '[data-layout="port"] #inspect{bottom:auto;top:calc(var(--subB) + 8px)}'
    '\n[data-layout="port"] #inspect.panel{width:calc(100vw - 74px);max-width:440px;grid-template-columns:34% 1fr}'
    '\n[data-layout="port"] #inspect.aim .ip-col>p{display:block;font-size:13px;line-height:1.3}')
# 2) opening a building panel closes any leftover card panel (it could stay pinned on touch screens)
rep("function openTile(i) {\n  const S = GAME.S;",
    "function openTile(i) {\n  if (!GAME.sel) { GAME.inspectHover = false; try { closeInspect(); } catch (e) {} }\n  const S = GAME.S;")
open(P, 'w', encoding='utf-8').write(h); print('ok')
