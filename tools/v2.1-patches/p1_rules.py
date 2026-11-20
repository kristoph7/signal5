# Batch 1 / rules: halftime switch, 20% collapse knockout, Typhoon deck fix, rules v2.1.0
import sys
P = sys.argv[1]
h = open(P, encoding='utf-8').read()

def rep(old, new, count=1):
    global h
    n = h.count(old)
    assert n == count, f'expected {count} got {n}: {old[:80]!r}'
    h = h.replace(old, new)

# --- data: version + constants + helper
rep("const RULES_VERSION = '2.0.0';",
    "const RULES_VERSION = '2.1.0';\n"
    "// v2.1: halftime switch (Player B moves first from Round 6) and Collapse knockout (<20% Integrity).\n"
    "const HALFTIME_ROUND = 6;\n"
    "const KO_FLOOR = 20;\n"
    "const firstOf = (S) => (S.round >= HALFTIME_ROUND ? 1 - S.playerA : S.playerA);")

# --- Typhoon deck: one Gentle Wind -> Magnitude 3 (sim: 44.6% -> ~48%)
rep("cards: { wind1:2, wind2:2, wind3:1, rain1:2, rain2:2, rain3:1, fire1:2, signal:1, tree:2, relief:2, vaccine:2, drill:1 } },",
    "cards: { wind1:1, wind2:2, wind3:1, rain1:2, rain2:2, rain3:1, fire1:2, quake1:1, signal:1, tree:2, relief:2, vaccine:2, drill:1 } },")

# --- engine: collapse knockout
rep("""  function checkKO(S, vi, ctx) {
    const v = S.p[vi];
    const bl = v.tiles.filter(b => b && !isGrove(b));
    if (bl.length && bl.every(b => b.dead) && !S.over) {
      S.p[1 - vi].medals.gold = true; S.knockout = 1 - vi;
      ctx.ev.push({ t: 'medal', vi: 1 - vi, medal: 'gold' }); ctx.ev.push({ t: 'knockout', winner: 1 - vi });
    }
  }""",
"""  function checkKO(S, vi, ctx) {
    const v = S.p[vi];
    if (S.over || S.knockout != null) return;
    const bl = v.tiles.filter(b => b && !isGrove(b));
    const wiped = bl.length && bl.every(b => b.dead);
    // v2.1 Collapse: during the 10 rounds (not the final Tsunami), a village below KO_FLOOR Integrity is knocked out
    const collapsed = !wiped && S.phase === 'play' && bl.length && integrity(v) < KO_FLOOR;
    if (wiped || collapsed) {
      S.p[1 - vi].medals.gold = true; S.knockout = 1 - vi; S.koWhy = wiped ? 'wipe' : 'collapse';
      ctx.ev.push({ t: 'medal', vi: 1 - vi, medal: 'gold' }); ctx.ev.push({ t: 'knockout', winner: 1 - vi, collapse: !wiped });
    }
  }""")
rep("if (S.knockout != null) { winner = S.knockout; why = 'Knockout — Gold medal'; }",
    "if (S.knockout != null) { winner = S.knockout; why = S.koWhy === 'collapse' ? 'Collapse — Integrity fell below ' + KO_FLOOR + '% (Gold medal)' : 'Knockout — Gold medal'; }")

# --- match loop + turn-order display
rep("const first = S.playerA; // v2.0 strict alternation: A first, B last, every round",
    "const first = firstOf(S); // v2.1: A first in Rounds 1–5, B first from the halftime switch (Round 6)")
rep("""  const first = S.playerA;
  const ord = [first, 1 - first];""",
    """  const first = firstOf(S);
  const ord = [first, 1 - first];""")
rep("r === 4 ? 'Hall Stage 2 unlocked' : r === 7",
    "r === 4 ? 'Hall Stage 2 unlocked' : r === 6 ? 'Halftime switch — the turn order flips' : r === 7")

# --- double-turn messaging (now happens once, at halftime)
rep("const sub = again ? (mine ? 'Initiative swap: you go first this round, so you act twice in a row' : 'Initiative swap: ' + OPP() + ' goes first this round, so they act twice in a row')",
    "const sub = again ? (mine ? 'Halftime switch: you move first from Round 6, so you act twice in a row' : 'Halftime switch: ' + OPP() + ' moves first from Round 6, so they act twice in a row')")
rep("toast('🔁 The first player swaps every round (initiative rule), so the same side sometimes plays two turns in a row. Watch the turn order under the tabs.', 'gold tip');",
    "toast('🔁 Halftime switch: Player B moves first in Rounds 6–10, so they act twice in a row once. Watch the turn order under the tabs.', 'gold tip');")

# --- player-facing text
rep("`Player A takes the first turn<br>in every round.`",
    "`Player A moves first in Rounds 1–5.<br>Player B moves first in Rounds 6–10.`")
rep("`Player A takes the first turn<br>in every round. Turns: 75 s + a 60 s bank.`",
    "`Player A moves first in Rounds 1–5, Player B in 6–10.<br>Turns: 75 s + a 60 s bank.`")
rep("(heads ? 'You act first every round; the CPU acts last (including Round 10).' : 'The CPU acts first every round; you act last (including Round 10).')",
    "(heads ? 'You act first in Rounds 1–5; the CPU acts first in Rounds 6–10.' : 'The CPU acts first in Rounds 1–5; you act first in Rounds 6–10.')")
rep("<p>Player A always moves first and Player B always moves last, every round.</p>",
    "<p>Player A moves first in Rounds 1–5. At the <b>halftime switch</b> (Round 6) the order flips and Player B moves first until the end.</p>")
rep("text: 'This shows who plays this round. Player A always goes first and Player B always goes last, so turns strictly alternate.'",
    "text: 'This shows who plays this round. Player A goes first in Rounds 1–5; from Round 6 (halftime) Player B goes first.'")
rep("Highest wins; destroying everything is a Knockout.",
    "Highest wins. Drop your rival below " + "20% Integrity during the 10 rounds and they <b>Collapse</b> — an instant Knockout.")
rep("(or destroy everything for a Knockout)",
    "(or drop your rival below 20% Integrity during the rounds for a Knockout)")
rep("<td>🥇 Gold</td><td>Every opponent building destroyed at once — Knockout</td>",
    "<td>🥇 Gold</td><td>Opponent Collapses (below 20% Integrity during Rounds 1–10) or loses every building — Knockout</td>", count=2)

open(P, 'w', encoding='utf-8').write(h)
print('ok')
