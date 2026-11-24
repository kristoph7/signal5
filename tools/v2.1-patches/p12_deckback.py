import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    c = s.count(a); assert c == n, (a[:60], c); s = s.replace(a, b)
rep("${scIB('b_view', [980, 836, 1286, 912], 'scView')}${scIB('b_next', [1306, 828, 1606, 912], 'scNext')}`, { esc: () => scClose() });",
    "${scIB('b_view', [980, 836, 1286, 912], 'scView')}${scIB('b_next', [1306, 828, 1606, 912], 'scNext')}${scIB('b_back', [28, 24, 248, 90], 'scDeckBack')}`, { esc: () => deckBack() });")
rep("  $('scView').onclick = () => { SFX.play('click'); viewDeck(); };\n",
    "  $('scView').onclick = () => { SFX.play('click'); viewDeck(); };\n  $('scDeckBack').onclick = () => { SFX.play('click'); deckBack(); };\n")
rep("/* ---------- DECK LIST ---------- */",
    "function deckBack() { GAME.mode = 'cpu'; GAME.oppName = 'CPU'; GAME.quick = false; scClose(); }\n\n/* ---------- DECK LIST ---------- */")
open(p, 'w', encoding='utf-8').write(s); print('ok')
