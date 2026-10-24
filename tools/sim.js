#!/usr/bin/env node
/* SIGNAL 5 balance simulator (GDD v2.0 §16.4)
   Runs the game's own rules engine + Kapitan CPU headless, CPU vs CPU, every pairing
   of the preset decks, and prints the health metrics the GDD targets.
   Usage:  node tools/sim.js [games=1600]                                          */
'use strict';
const fs = require('fs'), path = require('path'), vm = require('vm');
const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
const ctx = { console, structuredClone, Math, JSON, Object, Array, Set, Map, Image: function () {}, document: { createElement: () => ({ getContext: () => null }) } };
vm.createContext(ctx);
vm.runInContext(scripts.slice(0, 3).join('\n;\n') + '\n;this.__S5 = { Eng, AI, CARDS, DECKS, deckList, CP_SCHED, RULES_VERSION };', ctx);
const { Eng, AI, CARDS, DECKS, deckList, RULES_VERSION } = ctx.__S5;

// minimal copy of the UI's eco dispatcher
function eco(S, v, a) { const f = { build: () => Eng.build(S, v, a.type, a.i), upgrade: () => Eng.upgrade(S, v, a.i), stageUp: () => Eng.stageUp(S, v), repairPondo: () => Eng.repairPondo(S, v, a.i, a.n), repairWorker: () => Eng.repairWorker(S, v, a.i), rebuild: () => Eng.rebuild(S, v, a.i), addSeg: () => Eng.addSeg(S, v, a.key, a.t), repairSeg: () => Eng.repairSeg(S, v, a.key), hire: () => Eng.hire(S, v, a.i), train: () => Eng.train(S, v, a.i), evacuate: () => Eng.evacuate(S, v, a.i), retrofit: () => Eng.retrofit(S, v, a.i) }[a.fn]; return f ? f() : { ok: false }; }

function play(seed, d0, d1) {
  const S = Eng.newGame(seed, deckList(DECKS[d0]), deckList(DECKS[d1]), ['A', 'B']);
  AI.blindBuild(S, 0); AI.blindBuild(S, 1); AI.preparedPlan(S, 0); AI.preparedPlan(S, 1);
  S.playerA = Eng.rand(S) < 0.5 ? 0 : 1; S.phase = 'play'; S.p.forEach(v => Eng.recomputePower(v));
  const sig = [0, 0];
  outer: for (let r = 1; r <= 10; r++) {
    S.round = r; const first = S.playerA; // strict alternation (v2.0)
    for (const pi of [first, 1 - first]) {
      const v = S.p[pi]; S.cur = pi;
      if (v.signalPending) { sig[pi] = 1; Eng.landfall(S, pi, AI.bestEye(S, pi)); if (S.knockout != null) break outer; }
      Eng.startTurn(S, pi); if (S.knockout != null) break outer;
      const memo = {}; let fails = 0;
      while (true) {
        const a = AI.next(S, pi, 1, memo); if (a.kind === 'end') break; let res;
        if (a.kind === 'play') { const id = v.hand[a.h]; const tg = Object.assign({}, a.tg); if (tg.vi == null && CARDS[id].need.length && CARDS[id].kind === 'disaster') tg.vi = 1 - pi; if (CARDS[id].kind === 'buff' && tg.vi == null) tg.vi = pi; res = Eng.playCard(S, pi, a.h, tg); }
        else res = eco(S, v, a);
        if (!res || !res.ok) { if (++fails > 4) break; continue; } if (S.knockout != null) break outer;
      }
      Eng.endTurn(S, pi); if (S.knockout != null) break outer;
      if (v.hand.length) { let d = AI.chooseDiscard(S, pi); if (v.hand[d] === 'signal') d = v.hand.findIndex(x => x !== 'signal'); if (d >= 0) v.discard.push(v.hand.splice(d, 1)[0]); }
      Eng.refill(S, v);
    }
  }
  const pre = S.p.map(Eng.integrity);
  if (S.knockout == null) { Eng.tsunami(S, 0); Eng.tsunami(S, 1); if (Eng.finalResult(S).winner === -1) { S.suddenDeath = true; Eng.tsunami(S, 0, [4, 3, 2, 1]); Eng.tsunami(S, 1, [4, 3, 2, 1]); } }
  const f = Eng.finalResult(S);
  return { w: f.winner, first: S.playerA, sc: f.sc, pre, d0, d1, ko: S.knockout != null, sd: !!S.suddenDeath };
}

const N = +process.argv[2] || 1600; const decks = Object.keys(DECKS); const R = [];
for (let i = 0; i < N; i++) R.push(play(5000 + i * 7919, decks[i % decks.length], decks[Math.floor(i / decks.length) % decks.length]));
const pct = (x) => (100 * x).toFixed(1) + '%'; const mean = (a) => a.reduce((s, x) => s + x, 0) / a.length;
const w = {}, g = {}; R.forEach(x => { if (x.d0 === x.d1) return; [[0, x.d0], [1, x.d1]].forEach(([s, d]) => { g[d] = (g[d] || 0) + 1; w[d] = (w[d] || 0) + (x.w === s); }); });
const flips = R.filter(x => !x.ko && x.w !== -1 && (x.pre[0] - x.pre[1]) * (x.sc[0] - x.sc[1]) < 0).length;
console.log(`SIGNAL 5 rules v${RULES_VERSION} — ${N} CPU-vs-CPU games`);
console.log(`Player A win rate        ${pct(R.filter(x => x.w === x.first).length / N)}   (target 48–52%)`);
for (const d of decks) console.log(`  ${DECKS[d].name.padEnd(22)} ${pct(w[d] / g[d])}   (target 45–55%)`);
console.log(`Avg winner Integrity     ${mean(R.map(x => Math.max(...x.sc))).toFixed(1)}%  (target 45–70%)`);
console.log(`Knockouts                ${R.filter(x => x.ko).length}      (target <5%)`);
console.log(`Sudden-Death games       ${R.filter(x => x.sd).length}   unresolved draws ${R.filter(x => x.w === -1).length}`);
console.log(`Tsunami changed winner   ${pct(flips / N)}   (target 5–15%)`);
