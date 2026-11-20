# Batch 1 / art: no mirrored logo on the loading screen; version footer
import sys
P = sys.argv[1]
h = open(P, encoding='utf-8').read()
def rep(old, new, count=1):
    global h
    n = h.count(old); assert n == count, f'expected {count} got {n}: {old[:90]!r}'
    h = h.replace(old, new)

rep("display: ox + L.w * s < W - 1 ? 'block' : 'none' }); } }",
    "display: ox + L.w * s < W - 1 && !document.getElementById('title').classList.contains('loading') ? 'block' : 'none' }); } }")
rep('<div class="ver">Rules v2.0 · GDD v2.0</div>', '<div class="ver">Rules v2.1 · GDD v2.0</div>')
open(P, 'w', encoding='utf-8').write(h); print('ok')
