import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    c = s.count(a); assert c == n, (a[:70], c); s = s.replace(a, b)
rep("const firstOf = (S) => (S.round >= HALFTIME_ROUND ? 1 - S.playerA : S.playerA);",
    "// v2.2: Quick Match has no halftime switch — 1,000 simulated games: A 48.1% with no switch vs 56.9% with it.\nconst firstOf = (S) => (S.round >= HALFTIME_ROUND && !S.quick ? 1 - S.playerA : S.playerA);")
rep("so every unlock (L2/L3 hazards, Hall stages, Signal No. 5, halftime) still fires.", "so every unlock (L2/L3 hazards, Hall stages, Signal No. 5) still fires.")
rep("Player A moves first in Rounds 1–3, Player B in 4–6.", "Player A moves first every round (no halftime switch).", 2)
rep("8: 'Signal No. 5 · Hall Stage 3 · the turn order flips'", "8: 'Signal No. 5 · Hall Stage 3 unlocked'")
rep("<b>halftime switch</b> (Round 6)", "<b>halftime switch</b> (Round 6; not used in the 6-round Quick Match)", 3)
open(p, 'w', encoding='utf-8').write(s); print('ok')
