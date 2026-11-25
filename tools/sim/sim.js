// SIGNAL 5 headless match simulator — runs the real game engine + CPU (Kapitan level) for both seats.
// usage: node sim.js '{"n":500,"halftime":6,"ko":20,"rounds":[1..10],"d0":"balanced","d1":"balanced","seed0":1}'
const fs = require('fs'), path = require('path'), vm = require('vm');
const opts = Object.assign({ n: 500, halftime: 6, ko: 20, rounds: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], d0: 'balanced', d1: 'balanced', seed0: 1, lvl: 1, layout: 'random' }, JSON.parse(process.argv[2] || '{}'));
let src = fs.readFileSync(path.join(__dirname, 'engine_src.js'), 'utf8');
src = src.replace('const HALFTIME_ROUND = 6;', `const HALFTIME_ROUND = ${opts.halftime};`).replace('const KO_FLOOR = 20;', `const KO_FLOOR = ${opts.ko};`);
const mod = { exports: {} };
vm.runInNewContext(src, { module: mod, console, Math, JSON, Object, Array });
const { Eng, AI, DECKS, deckList, ecoApply, CARDS, firstOf, LAYOUTS } = mod.exports;

function takeTurn(S, pi) {
  const v = S.p[pi]; S.cur = pi;
  if (v.signalPending) { Eng.landfall(S, pi, AI.bestEye(S, pi)); if (S.knockout != null) return; }
  Eng.startTurn(S, pi); if (S.knockout != null) return;
  const memo = {}; let fails = 0;
  for (let guard = 0; guard < 200; guard++) {
    const act = AI.next(S, pi, opts.lvl, memo);
    if (act.kind === 'end') break;
    let r;
    if (act.kind === 'play') {
      const id = v.hand[act.h]; if (!id) r = { ok: false };
      else {
        const tg = Object.assign({}, act.tg);
        if (tg.vi == null && CARDS[id].need.length && CARDS[id].kind === 'disaster') tg.vi = 1 - pi;
        if (CARDS[id].kind === 'buff' && tg.vi == null) tg.vi = pi;
        r = Eng.playCard(S, pi, act.h, tg); if (r.ok) { S.stats.cards[pi]++; if (id === 'signal') S.stats.signal[pi]++; }
      }
    } else r = ecoApply(S, v, act);
    if (!r || !r.ok) { if (++fails > 4) break; continue; }
    if (S.knockout != null) return;
  }
  Eng.endTurn(S, pi); if (S.knockout != null) return;
  if (v.hand.length) {
    let d = AI.chooseDiscard(S, pi);
    if (v.hand[d] === 'signal') d = v.hand.findIndex(x => x !== 'signal');
    if (d >= 0) v.discard.push(v.hand.splice(d, 1)[0]);
  }
  Eng.refill(S, v);
}

function playGame(seed) {
  const S = Eng.newGame(seed, deckList(DECKS[opts.d0]), deckList(DECKS[opts.d1]), ['P0', 'P1']);
  S.stats = { cards: [0, 0], signal: [0, 0] };
  S.playerA = Eng.rand(S) < 0.5 ? 0 : 1;
  if (opts.layout === 'starter') { Eng.applyLayout(S, S.p[0], LAYOUTS[0]); Eng.applyLayout(S, S.p[1], LAYOUTS[0]); }
  else { AI.blindBuild(S, 0); AI.blindBuild(S, 1); }
  AI.preparedPlan(S, 0); AI.preparedPlan(S, 1);
  S.phase = 'play'; S.p.forEach(v => Eng.recomputePower(v));
  if (opts.rounds.length < 10) { S.rounds = opts.rounds.slice(); S.quick = true; }
  let koRound = null;
  outer: for (const r of opts.rounds) {
    S.round = r; const first = firstOf(S);
    for (const pi of [first, 1 - first]) { takeTurn(S, pi); if (S.knockout != null) { koRound = r; break outer; } }
  }
  let sudden = false;
  if (S.knockout == null) {
    S.phase = 'tsunami';
    for (const vi of [0, 1]) Eng.tsunami(S, vi);
    if (S.knockout == null && Eng.finalResult(S).winner === -1) { S.suddenDeath = sudden = true; for (const vi of [0, 1]) Eng.tsunami(S, vi, [4, 3, 2, 1]); }
  }
  const res = Eng.finalResult(S);
  return { seed, playerA: S.playerA, winner: res.winner, why: res.why, sc: res.sc, koRound, koWhy: S.koWhy || null, sudden, cards: S.stats.cards, signal: S.stats.signal };
}

const out = []; const t0 = Date.now();
for (let k = 0; k < opts.n; k++) out.push(playGame(opts.seed0 + k));
const A = out.filter(g => g.winner === g.playerA).length, draws = out.filter(g => g.winner === -1).length, B = opts.n - A - draws;
const ko = out.filter(g => g.koRound != null);
const margins = out.filter(g => g.winner >= 0).map(g => Math.abs(g.sc[0] - g.sc[1])).sort((a, b) => a - b);
const d0w = out.filter(g => g.winner === 0).length, d1w = out.filter(g => g.winner === 1).length;
const summary = {
  opts, games: opts.n, secs: (Date.now() - t0) / 1000,
  playerA_wins: A, playerB_wins: B, draws, playerA_rate: +(100 * A / opts.n).toFixed(1), playerB_rate: +(100 * B / opts.n).toFixed(1),
  seat0_deck_wins: d0w, seat1_deck_wins: d1w,
  knockouts: ko.length, ko_rate: +(100 * ko.length / opts.n).toFixed(1), collapse_kos: ko.filter(g => g.koWhy === 'collapse').length,
  sudden_death: out.filter(g => g.sudden).length,
  median_margin: margins.length ? margins[Math.floor(margins.length / 2)] : null,
  close_games_under5: out.filter(g => g.winner >= 0 && Math.abs(g.sc[0] - g.sc[1]) < 5).length,
  avg_cards_per_player: +(out.reduce((s, g) => s + g.cards[0] + g.cards[1], 0) / (2 * opts.n)).toFixed(1),
  signal_declared_games: out.filter(g => g.signal[0] + g.signal[1] > 0).length,
  avg_integrity: +(out.reduce((s, g) => s + g.sc[0] + g.sc[1], 0) / (2 * opts.n)).toFixed(1),
};
console.log(JSON.stringify(summary));
if (opts.out) fs.writeFileSync(opts.out, JSON.stringify(out));
