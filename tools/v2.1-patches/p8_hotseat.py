# Batch 1 / esports backup: PASS & PLAY — two players on one device, no internet needed.
# Both sides use Balanced + the sample layout; Prepared Plans are auto-picked. Choose 6 (Quick) or 10 (Full) rounds.
# The UI always shows the acting player as "you" (seat 0): between turns the villages swap seats behind an opaque pass screen.
import sys
P = sys.argv[1]
h = open(P, encoding='utf-8').read()
def rep(old, new, count=1):
    global h
    n = h.count(old); assert n == count, f'expected {count} got {n}: {old[:90]!r}'
    h = h.replace(old, new)

# ---- deck screen: split the slot into QUICK MATCH (vs CPU) and PASS & PLAY
rep("""    ${online() ? '' : `<button class="qm-btn" id="scQuick" style="${scR(690, 834, 962, 914)}"><span>⚡ QUICK MATCH</span><small>6 rounds · no setup</small></button>`}""",
    """    ${online() ? '' : `<button class="qm-btn" id="scQuick" style="${scR(690, 830, 962, 878)}"><span>⚡ QUICK MATCH</span></button><button class="qm-btn hs" id="scHot" style="${scR(690, 884, 962, 922)}"><span>👥 PASS &amp; PLAY</span></button>`}""")
rep(".qm-btn small{font:900 16px Nunito,sans-serif;color:#5a3000;letter-spacing:0}",
    ".qm-btn small{font:900 16px Nunito,sans-serif;color:#5a3000;letter-spacing:0}"
    "\n#scQuick{font-size:27px;border-width:3px} .qm-btn.hs{font-size:21px;border-width:3px;background:linear-gradient(#bde9ff,#4fb4ff 55%,#1f7ee0);color:#06264a;box-shadow:0 4px 0 #0b3f7a;animation:none}"
    "\n#passfx{position:fixed;inset:0;z-index:300;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:18px;background:radial-gradient(circle at 50% 40%,#173a7a,#050d24 70%);color:#fff;text-align:center;font-family:'Lilita One',sans-serif}"
    "\n#passfx.hidden{display:none} #passfx small{font:800 18px Nunito,sans-serif;color:#9fc4ff;letter-spacing:1px} #passfx b{font-size:clamp(34px,7vw,64px);color:#ffd23a;text-shadow:0 4px 0 #000} #passfx p{font:700 17px Nunito,sans-serif;color:#cfe0ff;max-width:520px;margin:0 16px}"
    "\n#passfx button{font:400 26px 'Lilita One',sans-serif;padding:14px 34px;border-radius:16px;border:4px solid #fff1b8;background:linear-gradient(#ffe68a,#ffb21f 55%,#f08a00);color:#2b1500;cursor:pointer;box-shadow:0 6px 0 #8a4f00}")
rep("  if ($('scQuick')) $('scQuick').onclick = () => { SFX.play('click'); GAME.quick = true; GAME.aiLevel = 0; scClose(); coinToss(); };",
    "  if ($('scQuick')) $('scQuick').onclick = () => { SFX.play('click'); GAME.mode = 'cpu'; GAME.oppName = 'CPU'; GAME.quick = true; GAME.aiLevel = 0; scClose(); coinToss(); };\n"
    "  if ($('scHot')) $('scHot').onclick = () => { SFX.play('click'); scClose(); hotseatMenu(); };")
# a normal NEXT always means vs CPU (or online)
rep("  $('scNext').onclick = () => { SFX.play('click'); GAME.quick = false;",
    "  $('scNext').onclick = () => { SFX.play('click'); GAME.quick = false; if (GAME.mode === 'hotseat') { GAME.mode = 'cpu'; GAME.oppName = 'CPU'; }")

# ---- hotseat flow
rep("// Quick Match: skip Blind Build, layout reveal and Prepared Plan — straight into Round 1",
"""/* ---------- PASS & PLAY (v2.1) ---------- */
function hotseatMenu() {
  modal('👥 Pass & Play', `<p>Two players share this device — no internet needed. Both barangays use the <b>Balanced</b> deck and the sample layout, and opening hands are dealt automatically.</p><p>Between turns, a cover screen hides your hand while you pass the device.</p>`,
    [{ label: '⚡ QUICK · 6 rounds', cls: 'gold', fn: () => { closeModal(); hotseatToss(true); } }, { label: '🏆 FULL · 10 rounds', fn: () => { closeModal(); hotseatToss(false); } }, { label: 'Back', fn: () => { closeModal(); deckSelect(); } }]);
}
function hotseatToss(quick) {
  GAME.mode = 'hotseat'; GAME.quick = quick; GAME.oppName = 'Player 2';
  const seed = (Math.random() * 2 ** 31) | 0;
  const S = GAME.S = Eng.newGame(seed, deckList(DECKS.balanced), deckList(DECKS.balanced), ['Player 1', 'Player 2']);
  S.seedLog = seed; GAME.log = []; if (quick) { S.rounds = QUICK_ROUNDS.slice(); S.quick = true; }
  const heads = Eng.rand(S) < 0.5; S.playerA = heads ? 0 : 1;
  scToss(heads, 'Player 2', quick ? `Pass & Play · 6 rounds<br>Player A moves first in Rounds 1–3, Player B in 4–6.` : `Pass & Play · 10 rounds<br>Player A moves first in Rounds 1–5, Player B in 6–10.`, () => hotseatSetup());
}
async function hotseatSetup() {
  const S = GAME.S;
  enterBuild();
  Eng.applyLayout(S, S.p[0], LAYOUTS[0]); Eng.applyLayout(S, S.p[1], LAYOUTS[0]);
  R.sync(0, S); R.sync(1, S); closeSheet();
  $('sub').classList.remove('hidden'); restoreActionButtons(); $('btnEnd').classList.add('hidden'); layoutInsets();
  GAME.busy = true; R.showLabels = false; $('tLabels').classList.remove('on');
  AI.preparedPlan(S, 0); AI.preparedPlan(S, 1);
  await banner('👥 PASS & PLAY', 'Same deck, same layout — the better Kapitan wins', '', 1700);
  GAME.busy = false; refreshHUD();
  startMatch();
}
function swapSeats(S) {
  S.p.reverse(); S.playerA = 1 - S.playerA; if (S.knockout != null) S.knockout = 1 - S.knockout;
  R.vs.reverse(); if (R.walkers) R.walkers.reverse(); if (GAME.koWarned) GAME.koWarned = { 0: GAME.koWarned[1], 1: GAME.koWarned[0] };
  GAME.oppName = S.p[1].name; GAME.undo = []; GAME.lastPi = -1;
  R.sync(0, S); R.sync(1, S); R.view = 0; updateTabs(); renderHand(true); refreshHUD();
}
function passScreen(name, whileCovered) {
  let el = $('passfx'); if (!el) { el = document.createElement('div'); el.id = 'passfx'; el.className = 'hidden'; document.body.appendChild(el); }
  el.innerHTML = `<small>PASS &amp; PLAY</small><b>${esc(name)}</b><p>Hand the device to <b style="font-size:inherit;color:#fff;text-shadow:none">${esc(name)}</b>. Everyone else, look away from the hand.</p><button id="passGo">I'M ${esc(name.toUpperCase())} — START ➜</button>`;
  el.classList.remove('hidden'); try { whileCovered && whileCovered(); } catch (e) { console.error(e); }
  return new Promise(res => { $('passGo').onclick = () => { SFX.play('click'); el.classList.add('hidden'); res(); }; });
}
async function hotseatFinish() {
  const S = GAME.S; const r = Eng.finalResult(S); if (r.winner === 1) swapSeats(S); finish();
}
// Quick Match: skip Blind Build, layout reveal and Prepared Plan — straight into Round 1""")

# ---- match loop: in Pass & Play every turn is played as seat 0
rep("  const S = GAME.S; GAME.matchStart = GAME.matchStart || Date.now(); if (!online()) AI.preparedPlan(S, 1);",
    "  const S = GAME.S; GAME.matchStart = GAME.matchStart || Date.now(); if (!online() && GAME.mode !== 'hotseat') AI.preparedPlan(S, 1);")
rep("      for (const [k, pi] of [first, 1 - first].entries()) { GAME.turnIdx = k; await takeTurn(pi); if (S.knockout != null) return finish(); }\n    }\n    await tsunamiPhase();\n    finish();",
    "      if (GAME.mode === 'hotseat') {\n"
    "        const seats = [S.p[first], S.p[1 - first]];\n"
    "        for (const [k, vobj] of seats.entries()) { GAME.turnIdx = k; await passScreen(vobj.name, () => { if (S.p[0] !== vobj) swapSeats(S); }); GAME.lastPi = -1; await takeTurn(0); if (S.knockout != null) return hotseatFinish(); }\n"
    "        continue;\n      }\n"
    "      for (const [k, pi] of [first, 1 - first].entries()) { GAME.turnIdx = k; await takeTurn(pi); if (S.knockout != null) return finish(); }\n    }\n    await tsunamiPhase();\n    GAME.mode === 'hotseat' ? hotseatFinish() : finish();")

# ---- labels: names instead of YOU / CPU
rep("$('ib1').querySelector('.nm').textContent = OPP().slice(0, 8).toUpperCase();",
    "$('ib1').querySelector('.nm').textContent = GAME.mode === 'hotseat' ? S.p[1].name.replace('Player ', 'P') : OPP().slice(0, 8).toUpperCase(); $('ib0').querySelector('.nm').textContent = GAME.mode === 'hotseat' ? S.p[0].name.replace('Player ', 'P') : 'YOU';")
rep("<b>${i === 0 ? 'YOU' : esc(online() ? OPP().toUpperCase() : 'CPU')}</b>",
    "<b>${GAME.mode === 'hotseat' ? esc(S.p[i].name.toUpperCase()) : i === 0 ? 'YOU' : esc(online() ? OPP().toUpperCase() : 'CPU')}</b>")
rep("    const head = { win: 'VICTORY!', lose: 'DEFEAT', draw: 'DRAW' }[kind];\n    const sub = win ? 'Your barangay was better prepared.'",
    "    const head = GAME.mode === 'hotseat' && res.winner >= 0 ? esc(S.p[res.winner].name.replace('Player ', 'P')) + ' WINS!' : { win: 'VICTORY!', lose: 'DEFEAT', draw: 'DRAW' }[kind];\n"
    "    const sub = GAME.mode === 'hotseat' && res.winner >= 0 ? esc(S.p[res.winner].name) + '’s barangay was better prepared.' : win ? 'Your barangay was better prepared.'")
rep("const sub = again ? (mine ?", "const sub = GAME.mode === 'hotseat' ? esc(S.p[0].name) + ', the barangay awaits your orders' : again ? (mine ?")
rep("await banner(mine ? (again ? 'YOUR TURN AGAIN' : 'YOUR TURN')",
    "await banner(GAME.mode === 'hotseat' ? esc(S.p[0].name.toUpperCase()) + '’S TURN' : mine ? (again ? 'YOUR TURN AGAIN' : 'YOUR TURN')")

rep("A(i === 0 ? 'r_house' : 'r_robot')", "A(i === 0 || GAME.mode === 'hotseat' ? 'r_house' : 'r_robot')")
open(P, 'w', encoding='utf-8').write(h); print('ok')
