# Batch 1 / audio: replace the synth module (same API + storm bed, adaptive layers, ducking, kulintang theme) and wire it in
import sys, os
P = sys.argv[1]
h = open(P, encoding='utf-8').read()
def rep(old, new, count=1):
    global h
    n = h.count(old); assert n == count, f'expected {count} got {n}: {old[:90]!r}'
    h = h.replace(old, new)

# 1) swap the module
a = h.index("\n'use strict';\n/* ================= SIGNAL 5 — SYNTH AUDIO (no files) ================= */")
b = h.index("window.SFX = SFX;\n", a) + len("window.SFX = SFX;\n")
new_mod = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sfx_v21.js'), encoding='utf-8').read()
h = h[:a] + new_mod + h[b:]

# 2) per-round intensity + storm level
rep("      S.round = r; GAME.tension = r >= 8 ? 0.7 : 0;\n",
    "      S.round = r; GAME.tension = r >= 8 ? 0.7 : 0;\n"
    "      try { SFX.scene('game'); SFX.intensity(r >= 8 ? 2 : r >= 5 ? 1 : 0); SFX.storm(Math.min(1, 0.18 + r * 0.075)); } catch (e) {}\n")
# 3) danger layer while any Signal No. 5 is pending
rep("function refreshHUD() {\n  const S = GAME.S; if (!S) return;",
    "function refreshHUD() {\n  const S = GAME.S; if (!S) return;\n  try { SFX.danger(S.phase === 'play' && S.p.some(v => v.signalPending)); } catch (e) {}")
# 4) Tsunami
rep("  await tsunamiWave();\n", "  try { SFX.danger(false); SFX.storm(1); } catch (e) {}\n  await tsunamiWave();\n")
# 5) result
rep("const win = res.winner === 0; SFX.play(win ? 'win' : 'lose');",
    "const win = res.winner === 0; try { SFX.scene('over'); SFX.danger(false); SFX.storm(0.12); } catch (e) {} SFX.play(win ? 'win' : 'lose');", count=2)
# 6) build phase switches from the title theme to the game loop
rep("function enterBuild() {\n  const S = GAME.S; S.phase = 'build';",
    "function enterBuild() {\n  try { SFX.scene('game'); SFX.intensity(0); SFX.storm(0.15); } catch (e) {}\n  const S = GAME.S; S.phase = 'build';")
# 7) heavier Level 3 impacts
rep("if (c.fam === 'fire') {\n      SFX.play('whoosh');", "if (c.fam === 'fire') {\n      SFX.play('whoosh'); if (c.lvl === 3) SFX.play('boom', 0.5);")
rep("R.tornados.push(tw); SFX.play('wind'); if (c.lvl === 3) {", "R.tornados.push(tw); SFX.play('wind'); if (c.lvl === 3) { SFX.play('boom', 0.4);")
rep("SFX.play('rain'); if (c.lvl >= 2) {", "SFX.play('rain'); if (c.lvl === 3) SFX.play('boom', 0.6); if (c.lvl >= 2) {")
rep("} else if (c.fam === 'quake') {\n      SFX.play('quake');", "} else if (c.fam === 'quake') {\n      SFX.play('quake'); if (c.lvl === 3) SFX.play('boom');")
rep("SFX.play('siren'); SFX.play('wind'); SFX.play('rain');", "SFX.play('siren'); SFX.play('wind'); SFX.play('rain'); SFX.play('boom', 0.3);")
# 8) voice call when Signal No. 5 is raised (browser TTS stand-in)
rep("case 'signalDeclared': R.danger = 0.8; SFX.play('siren');",
    "case 'signalDeclared': R.danger = 0.8; SFX.play('siren'); SFX.voice('Signal Number 5! Lumikas na!');")

open(P, 'w', encoding='utf-8').write(h); print('ok')
