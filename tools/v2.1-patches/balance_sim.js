if (process.env.TRACE) global.TRACE = {};
// Headless SIGNAL 5 simulator. Usage: node sim.js '<json opts>'
// opts: { order: 'base'|'snake', hallKO: bool, aCP: {round: bonus}, cards: {id: {cp:n}}, deckA, deckB, n, seed0, lvl, mode }
const opts = JSON.parse(process.argv[2] || '{}');
const M = require('./engine.js');
const { Eng, AI, DECKS, deckList, ecoApply, CARDS } = M;
if (opts.cards) for (const id in opts.cards) Object.assign(CARDS[id], opts.cards[id]);
if (opts.decks) for (const k in opts.decks) DECKS[k] = opts.decks[k];

function hallCheck(S) {
  if (S.knockout != null) return;
  if (opts.koBelow && S.round >= (opts.koFrom || 1)) for (const vi of [0, 1]) { if (Eng.integrity(S.p[vi]) < opts.koBelow) { S.knockout = 1 - vi; return; } }
  if (!opts.hallKO) return;
  for (const vi of [0, 1]) { const h = Eng.hall(S.p[vi]); if (h && h.dead) { S.knockout = 1 - vi; return; } }
}

function sim(seed, d0, d1, first, lvl) {
  const S = Eng.newGame(seed, deckList(DECKS[d0]), deckList(DECKS[d1]), ['P0', 'P1']);
  S.playerA = first;
  AI.blindBuild(S, 0); AI.blindBuild(S, 1); AI.preparedPlan(S, 0); AI.preparedPlan(S, 1);
  S.phase = 'play'; S.p.forEach(v => Eng.recomputePower(v));
  const turn = (pi) => {
    const v = S.p[pi];
    if (v.signalPending) { Eng.landfall(S, pi, AI.bestEye(S, pi)); hallCheck(S); if (S.knockout != null) return; }
    Eng.startTurn(S, pi); hallCheck(S); if (S.knockout != null) return;
    if (opts.aCP && pi === S.playerA && opts.aCP[S.round]) v.cp += opts.aCP[S.round];
    if (opts.bCP && pi !== S.playerA && opts.bCP[S.round]) v.cp += opts.bCP[S.round];
    const memo = {}; let fails = 0;
    while (true) {
      const act = AI.next(S, pi, lvl, memo); if (act.kind === 'end') break;
      let r;
      if (act.kind === 'play') {
        const id = v.hand[act.h];
        if (!id) r = { ok: false };
        else {
          const tg = Object.assign({}, act.tg);
          if (tg.vi == null && CARDS[id].need.length && CARDS[id].kind === 'disaster') tg.vi = 1 - pi;
          if (CARDS[id].kind === 'buff' && tg.vi == null) tg.vi = pi;
          r = Eng.playCard(S, pi, act.h, tg);
        }
      } else r = ecoApply(S, v, act);
      if (!r || !r.ok) { if (++fails > 4) break; continue; }
      hallCheck(S); if (S.knockout != null) return;
    }
    Eng.endTurn(S, pi); hallCheck(S); if (S.knockout != null) return;
    if (v.hand.length) {
      let d = AI.chooseDiscard(S, pi);
      if (v.hand[d] === 'signal') d = v.hand.findIndex(x => x !== 'signal');
      if (d != null && d >= 0) v.discard.push(v.hand.splice(d, 1)[0]);
    }
    Eng.refill(S, v);
  };
  const A = S.playerA, B = 1 - A;
  for (const r of (opts.rounds || [1,2,3,4,5,6,7,8,9,10])) {
    S.round = r;
    const swapR = opts.swapRounds || [6,7,8,9,10]; const order = (opts.order === 'snake' && r % 2 === 0) || swapR.includes(r) ? [B, A] : [A, B];
    for (const pi of order) { turn(pi); if (S.knockout != null) return { winner: S.knockout, ko: true, round: r }; }
    if (global.TRACE) { const I = S.p.map(Eng.integrity); TRACE[r] = (TRACE[r]||0) + (I[B]-I[A]); }
  }
  const ecoOnly = (pi) => { const v = S.p[pi];
    if (opts.finalPrep === 'full') Eng.startTurn(S, pi); else { v.actions = (()=>{ const c = v.tiles.find(b => b && b.type === 'cons'); return c && Eng.functional(c) ? Eng.healthyStaff(c) : 0; })(); v.engActions = Math.min(v.actions, Eng.engineers(v)); v.cp = 0; }
    hallCheck(S); if (S.knockout != null) return;
    const memo = {}; let fails = 0;
    while (true) { const act = AI.next(S, pi, lvl, memo); if (act.kind === 'end') break;
      if (act.kind === 'play') { if (++fails > 4) break; continue; }
      const r = ecoApply(S, v, act); if (!r || !r.ok) { if (++fails > 4) break; continue; } }
    v.actions = 0; };
  if (opts.finalPrep === 'A' || opts.finalPrep === 'full') { ecoOnly(A); if (S.knockout != null) return { winner: S.knockout, ko: true, round: 'P' }; }
  if (opts.finalPrep === 'both') { ecoOnly(B); ecoOnly(A); }
  const pre = S.p.map(Eng.integrity);
  if (global.TRACE) { TRACE.pre = (TRACE.pre||0) + (pre[B]-pre[A]); }
  S.phase = 'tsunami';
  for (const vi of [0, 1]) Eng.tsunami(S, vi);
  hallCheck(S);
  if (S.knockout == null && Eng.finalResult(S).winner === -1) { S.suddenDeath = true; for (const vi of [0, 1]) Eng.tsunami(S, vi, [4, 3, 2, 1]); }
  const res = Eng.finalResult(S);
  if (global.TRACE) { TRACE.fin = (TRACE.fin||0) + (res.sc[B]-res.sc[A]); TRACE.dmgA=(TRACE.dmgA||0)+S.p[A].stats.dmgDealt; TRACE.dmgB=(TRACE.dmgB||0)+S.p[B].stats.dmgDealt; TRACE.cardsA=(TRACE.cardsA||0)+S.p[A].stats.cardsPlayed; TRACE.cardsB=(TRACE.cardsB||0)+S.p[B].stats.cardsPlayed; }
  return { winner: res.winner, ko: S.knockout != null, sc: res.sc, pre };
}

const n = opts.n || 400, lvl = opts.lvl ?? 1, seed0 = opts.seed0 || 1;
if (opts.mode === 'matrix') {
  const decks = opts.list || ['balanced', 'fire', 'typhoon', 'quake'];
  const wins = Object.fromEntries(decks.map(d => [d, [0, 0]])); const pairs = {};
  for (let i = 0; i < decks.length; i++) for (let j = i + 1; j < decks.length; j++) {
    let x = 0, y = 0;
    for (let s = 0; s < n; s++) for (const first of [0, 1]) {
      const r = sim((seed0 + s) * 31337 + first, decks[i], decks[j], first, lvl);
      if (r.winner === 0) x++; else if (r.winner === 1) y++;
    }
    pairs[decks[i] + ' v ' + decks[j]] = x + '-' + y;
    wins[decks[i]][0] += x; wins[decks[i]][1] += 2 * n; wins[decks[j]][0] += y; wins[decks[j]][1] += 2 * n;
  }
  const rate = Object.fromEntries(Object.entries(wins).map(([k, [w, t]]) => [k, (100 * w / t).toFixed(1) + '%']));
  console.log(JSON.stringify({ opts, pairs, rate }));
} else {
  let a = 0, b = 0, d = 0, ko = 0, koRounds = {}, flips = 0;
  const deck = opts.deck || 'balanced';
  for (let s = 0; s < n; s++) {
    const first = s % 2; const r = sim((seed0 + s) * 7919 + 13, deck, deck, first, lvl);
    if (r.winner === -1) d++; else if (r.winner === first) a++; else b++;
    if (r.ko) { ko++; koRounds[r.round || 'T'] = (koRounds[r.round || 'T'] || 0) + 1; }
    if (r.pre && r.winner !== -1 && r.winner !== (r.pre[0] > r.pre[1] ? 0 : 1)) flips++;
  }
  if (global.TRACE) for (const k in TRACE) TRACE[k] = +(TRACE[k]/n).toFixed(2);
  console.log(JSON.stringify({ trace: global.TRACE, opts, A: a, B: b, draws: d, B_rate: (100 * b / (a + b)).toFixed(1), ko, koRounds, flips }));
}
