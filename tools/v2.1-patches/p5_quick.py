# Batch 1 / audience: QUICK MATCH — 6 rounds (1,3,5,8,9,10), Balanced mirror, sample layouts, auto Prepared Plan
# Sim: seat balance Player B 47.4% (800 matches); knockouts ~5%. Deck choice is locked to Balanced because
# short games amplify deck matchups (Typhoon 70% / Fire 39% in 6 rounds).
import sys
P = sys.argv[1]
h = open(P, encoding='utf-8').read()
def rep(old, new, count=1):
    global h
    n = h.count(old); assert n == count, f'expected {count} got {n}: {old[:90]!r}'
    h = h.replace(old, new)

# ---- data helpers
rep("const firstOf = (S) => (S.round >= HALFTIME_ROUND ? 1 - S.playerA : S.playerA);",
"""const firstOf = (S) => (S.round >= HALFTIME_ROUND ? 1 - S.playerA : S.playerA);
// Quick Match plays 6 of the 10 rounds, so every unlock (L2/L3 hazards, Hall stages, Signal No. 5, halftime) still fires.
const QUICK_ROUNDS = [1, 3, 5, 8, 9, 10];
const roundLabel = (S) => (S && S.rounds ? (S.rounds.indexOf(S.round) + 1) + '/' + S.rounds.length : String(S ? S.round : ''));
// real round -> the round number the player sees (Quick Match counts 1–6)
const RL = (n) => { const S = typeof window !== 'undefined' && window.GAME && GAME.S; if (!S || !S.rounds) return n; const k = S.rounds.findIndex(r => r >= n); return k < 0 ? S.rounds.length : k + 1; };""")

# ---- engine lock messages use the displayed round number
rep("'Unlocks at Round ' + c.unlock", "'Unlocks at Round ' + RL(c.unlock)")
rep("'Unlocks at Round ' + n.round", "'Unlocks at Round ' + RL(n.round)")
rep("'Too late (last call was Round 9)'", "'Too late (last call was Round ' + RL(9) + ')'")

# ---- match loop over the round list
rep("""    for (let r = 1; r <= 10; r++) {
      S.round = r; GAME.tension = r >= 8 ? 0.7 : 0;
      refreshHUD();
      await banner('ROUND ' + r, r === 1""",
"""    const QSUB = { 1: 'Quick Match — 6 rounds · Balanced vs Balanced', 3: 'Level 2 hazards unlocked', 5: 'Level 3 hazards + Hall Stage 2 unlocked', 8: 'Signal No. 5 · Hall Stage 3 · the turn order flips', 9: 'Last call for Signal No. 5', 10: 'Final round — the Tsunami comes next' };
    for (const r of (S.rounds || [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])) {
      S.round = r; GAME.tension = r >= 8 ? 0.7 : 0;
      refreshHUD();
      if (S.rounds) { await banner('ROUND ' + roundLabel(S), QSUB[r] || ''); } else
      await banner('ROUND ' + r, r === 1""")
rep("el.innerHTML = `<span class=\"rn\">ROUND ${S.round}</span>",
    "el.innerHTML = `<span class=\"rn\">ROUND ${roundLabel(S)}</span>")

# ---- coin toss: Quick Match uses Balanced for both sides and the short round list
rep("""  const cpuKeys = Object.keys(DECKS); const cpuDeck = DECKS[cpuKeys[Math.floor(Math.random() * cpuKeys.length)]];
  GAME.cpuDeckName = cpuDeck.name;
  const S = GAME.S = Eng.newGame(seed, deckList({ cards: myDeckCards() }), deckList(cpuDeck), ['You', 'CPU']);
  S.seedLog = seed; GAME.log = [];
  const heads = Eng.rand(S) < 0.5; S.playerA = heads ? 0 : 1;
  scToss(heads, 'CPU', `Player A moves first in Rounds 1–5.<br>Player B moves first in Rounds 6–10.`, () => { enterBuild(); toast('🤖 The CPU is playing the ' + esc(cpuDeck.name) + ' deck', 'gold'); });""",
"""  const cpuKeys = Object.keys(DECKS); const cpuDeck = GAME.quick ? DECKS.balanced : DECKS[cpuKeys[Math.floor(Math.random() * cpuKeys.length)]];
  GAME.cpuDeckName = cpuDeck.name;
  const S = GAME.S = Eng.newGame(seed, deckList({ cards: GAME.quick ? DECKS.balanced.cards : myDeckCards() }), deckList(cpuDeck), ['You', 'CPU']);
  S.seedLog = seed; GAME.log = [];
  if (GAME.quick) { S.rounds = QUICK_ROUNDS.slice(); S.quick = true; }
  const heads = Eng.rand(S) < 0.5; S.playerA = heads ? 0 : 1;
  if (GAME.quick) scToss(heads, 'CPU', `⚡ Quick Match · 6 rounds · Balanced vs Balanced<br>Player A moves first in Rounds 1–3, Player B in 4–6.`, () => quickSetup());
  else scToss(heads, 'CPU', `Player A moves first in Rounds 1–5.<br>Player B moves first in Rounds 6–10.`, () => { enterBuild(); toast('🤖 The CPU is playing the ' + esc(cpuDeck.name) + ' deck', 'gold'); });
}
// Quick Match: skip Blind Build, layout reveal and Prepared Plan — straight into Round 1
async function quickSetup() {
  const S = GAME.S;
  enterBuild();
  Eng.applyLayout(S, S.p[0], LAYOUTS[0]); const lay = AI.blindBuild(S, 1);
  R.sync(0, S); R.sync(1, S); closeSheet();
  $('sub').classList.remove('hidden'); restoreActionButtons(); $('btnEnd').classList.add('hidden'); layoutInsets();
  GAME.busy = true; R.showLabels = false; $('tLabels').classList.remove('on');
  AI.preparedPlan(S, 0);
  await banner('⚡ QUICK MATCH', 'Sample layouts are built · your opening hand is ready', '', 1700);
  toast('⚡ Quick Match: your barangay uses the sample layout and the CPU built “' + esc(lay) + '”. Tap OPPONENT to scout it.', 'gold');
  GAME.busy = false; refreshHUD();
  startMatch();""")

# ---- deck screen: QUICK MATCH button (offline only); normal NEXT clears quick mode
rep("""    ${scIB('b_view', [980, 836, 1286, 912], 'scView')}${scIB('b_next', [1306, 828, 1606, 912], 'scNext')}`, { esc: () => scClose() });""",
"""    ${online() ? '' : `<button class="qm-btn" id="scQuick" style="${scR(690, 834, 962, 914)}"><span>⚡ QUICK MATCH</span><small>6 rounds · no setup</small></button>`}
    ${scIB('b_view', [980, 836, 1286, 912], 'scView')}${scIB('b_next', [1306, 828, 1606, 912], 'scNext')}`, { esc: () => scClose() });""")
rep("""  $('scNext').onclick = () => { SFX.play('click'); if (GAME.deckKey === 'custom' && !GAME.custom) { scClose(); return deckBuilder(); } scClose(); online() ? onlineLobby() : coinToss(); };""",
"""  $('scNext').onclick = () => { SFX.play('click'); GAME.quick = false; if (GAME.deckKey === 'custom' && !GAME.custom) { scClose(); return deckBuilder(); } scClose(); online() ? onlineLobby() : coinToss(); };
  if ($('scQuick')) $('scQuick').onclick = () => { SFX.play('click'); GAME.quick = true; GAME.aiLevel = 0; scClose(); coinToss(); };""")
rep(".sc-seg{position:absolute;display:flex;border-radius:14px;background:#06204a;border:3px solid #1d4a90;overflow:hidden}",
    ".sc-seg{position:absolute;display:flex;border-radius:14px;background:#06204a;border:3px solid #1d4a90;overflow:hidden}"
    "\n.qm-btn{position:absolute;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;border:4px solid #fff1b8;border-radius:16px;"
    "background:linear-gradient(#ffe68a,#ffb21f 55%,#f08a00);color:#2b1500;font:400 31px 'Lilita One',sans-serif;letter-spacing:.5px;line-height:1;cursor:pointer;"
    "box-shadow:0 6px 0 #8a4f00,0 0 22px #ffcf4a99;animation:qmPulse 1.6s ease-in-out infinite}"
    "\n.qm-btn small{font:900 16px Nunito,sans-serif;color:#5a3000;letter-spacing:0}"
    "\n.qm-btn:hover{filter:brightness(1.08)} .qm-btn:active{transform:translateY(3px);box-shadow:0 3px 0 #8a4f00}"
    "\n@keyframes qmPulse{0%,100%{box-shadow:0 6px 0 #8a4f00,0 0 10px #ffcf4a55}50%{box-shadow:0 6px 0 #8a4f00,0 0 28px #ffcf4acc}}")

open(P, 'w', encoding='utf-8').write(h); print('ok')
