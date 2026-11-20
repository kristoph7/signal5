# Batch 1 / gameplay: hover damage preview + Integrity delta, undo for economy actions (offline + online)
import sys
P = sys.argv[1]
h = open(P, encoding='utf-8').read()

def rep(old, new, count=1):
    global h
    n = h.count(old)
    assert n == count, f'expected {count} got {n}: {old[:90]!r}'
    h = h.replace(old, new)

# ---------- preview: accept a target override, add Integrity delta + knockout warning
rep("""function computePreview() {
  const S = GAME.S, sel = GAME.sel; const C = clone(S);
  const r = Eng.playCard(C, 0, sel.h, Object.assign({}, sel.tg));
  if (!r.ok) return;""",
"""function computePreview(tgo) {
  const S = GAME.S, sel = GAME.sel; const C = clone(S); const tgt = Object.assign({}, tgo || sel.tg);
  const r = Eng.playCard(C, 0, sel.h, tgt);
  if (!r.ok) return;""")
rep("""  const bits = [`💥 ${P.total} dmg`]; if (P.destroyed) bits.push(`💀 ${P.destroyed}`);""",
"""  const bits = [`💥 ${P.total} dmg`];
  if (tgt.vi != null) { const ib = Eng.integrity(S.p[tgt.vi]), ia = Eng.integrity(C.p[tgt.vi]); if (ib !== ia) bits.push(`📉 ${ib}→${ia}%`); }
  if (C.knockout === 0 && S.knockout == null) bits.unshift('☠ KNOCKOUT!');
  if (P.destroyed) bits.push(`💀 ${P.destroyed}`);""")

# hover preview (mouse): show the result for the tile under the cursor before tapping
rep("function showCardInfo(id, can, readonly) {",
"""function hoverPreview(i) {
  const sel = GAME.sel;
  if (!sel || sel.step !== 'tile' || GAME.phase !== 'action' || GAME.busy) { GAME.hovPrev = undefined; return; }
  if (i === GAME.hovPrev) return; GAME.hovPrev = i;
  const c = CARDS[sel.id];
  if (i < 0 || R.view !== sel.tg.vi || !(sel.valid || []).includes(i) || c.need.includes('open')) { R.preview = null; $('phD').textContent = sel.hint || ''; return; }
  const tg = Object.assign({}, sel.tg, { idx: i }); if (c.need.includes('line') && !tg.line) tg.line = 'row';
  computePreview(tg);
}
function showCardInfo(id, can, readonly) {""")
rep("if (e.pointerType === 'mouse' && !ptrs.size) { const i = R.pickTile(e.clientX, e.clientY); R.hoverIdx = i; cv.style.cursor = i >= 0 ? 'pointer' : 'grab'; }",
    "if (e.pointerType === 'mouse' && !ptrs.size) { const i = R.pickTile(e.clientX, e.clientY); R.hoverIdx = i; cv.style.cursor = i >= 0 ? 'pointer' : 'grab'; try { window.hoverPreview && hoverPreview(i); } catch (er) {} }")
rep("cv.addEventListener('pointerleave', () => { R.hoverIdx = -1; });",
    "cv.addEventListener('pointerleave', () => { R.hoverIdx = -1; try { window.hoverPreview && hoverPreview(-1); } catch (er) {} });")

# ---------- undo
rep("""function localEco(act) {
  const S = GAME.S; const res = ecoApply(S, S.p[0], act);
  if (res && res.ok && online() && S.phase !== 'build') NET.send('act', Object.assign({ kind: 'eco' }, act));
  return res;
}""",
"""function localEco(act) {
  const S = GAME.S; const snap = S.phase !== 'build' ? clone(S.p[0]) : null;
  const res = ecoApply(S, S.p[0], act);
  if (res && res.ok && snap) { GAME.undo.push(snap); if (GAME.undo.length > 30) GAME.undo.shift(); setTimeout(updateUndoBtn, 0); }
  if (res && res.ok && online() && S.phase !== 'build') NET.send('act', Object.assign({ kind: 'eco' }, act));
  return res;
}
/* ---------- UNDO (v2.1): economy actions can be taken back until you play a card or end the turn ---------- */
function restoreVillage(v, snap) { for (const k of Object.keys(v)) if (!(k in snap)) delete v[k]; Object.assign(v, clone(snap)); Eng.recomputePower(v); }
function undoReset() { GAME.undo = []; updateUndoBtn(); }
function updateUndoBtn() { const b = $('btnUndo'); if (!b) return; b.classList.toggle('hidden', !(GAME.phase === 'action' && !GAME.busy && !GAME.sel && GAME.undo.length)); }
function onUndoBtn() {
  if (GAME.phase !== 'action' || GAME.busy || GAME.sel || !GAME.undo.length) return;
  restoreVillage(GAME.S.p[0], GAME.undo.pop()); if (online()) NET.send('undo');
  SFX.play('click'); closeSheet(); syncAll(); toast('↶ Undone', 'good'); updateUndoBtn();
}""")
rep("settings: { sfx: true, music: true, speed: 1, hp: false, reduced: false, vibrate: true }, log: [], discardSel: -1, eyeSel: -1,",
    "settings: { sfx: true, music: true, speed: 1, hp: false, reduced: false, vibrate: true }, log: [], discardSel: -1, eyeSel: -1, undo: [], rUndo: [],")
rep("""      <button class="btn blue hidden" id="btnCancel">↺ CANCEL</button>""",
    """      <button class="btn blue hidden" id="btnUndo" title="Undo last build/repair (Ctrl+Z)">↶ UNDO</button>
      <button class="btn blue hidden" id="btnCancel">↺ CANCEL</button>""")
rep("$('btnCancel').onclick = () => { SFX.play('click'); cancelSel(); };\n  $('btnPlay').onclick = () => onPlayBtn();",
    "$('btnCancel').onclick = () => { SFX.play('click'); cancelSel(); };\n  $('btnUndo').onclick = () => onUndoBtn();\n  $('btnPlay').onclick = () => onPlayBtn();")
# reset at turn start, on card play, on end; refresh visibility when selection changes
rep("""function humanTurn() {
  GAME.phase = 'action'; GAME.busy = false; const S = GAME.S, v = S.p[0];""",
"""function humanTurn() {
  GAME.phase = 'action'; GAME.busy = false; const S = GAME.S, v = S.p[0]; GAME.undo = []; setTimeout(updateUndoBtn, 0);""")
rep("""  const S = GAME.S, sel = GAME.sel; if (!sel || GAME.busy) return;
  GAME.busy = true; const c = CARDS[sel.id];""",
"""  const S = GAME.S, sel = GAME.sel; if (!sel || GAME.busy) return;
  GAME.busy = true; const c = CARDS[sel.id]; undoReset();""")
rep("const go = () => { closeModal(); cancelSel(); stopTurnTimer();",
    "const go = () => { closeModal(); cancelSel(); undoReset(); stopTurnTimer();")
rep("""  if (GAME.phase === 'action') { setPhase('⚠ YOUR TURN', 'Tap a card to attack or prepare — or tap your tiles to build.'); if (!silent) $('btnEnd').classList.remove('hidden'); }
  updateHandState();""",
"""  if (GAME.phase === 'action') { setPhase('⚠ YOUR TURN', 'Tap a card to attack or prepare — or tap your tiles to build.'); if (!silent) $('btnEnd').classList.remove('hidden'); }
  updateHandState(); updateUndoBtn();""")
rep("""  updateHandState(); updateTargeting(); openInspect(id, { play: true });""",
    """  updateHandState(); updateTargeting(); updateUndoBtn(); openInspect(id, { play: true });""")

# online: mirror the opponent's undo
rep("""  while (true) {
    setPhase('🌐 ' + OPP().toUpperCase(), OPP() + ' is planning their move…');
    GAME.phase = 'remote'; GAME.busy = false;
    const m = await NET.expect(['act', 'end']);
    GAME.busy = true; closeSheet();
    if (m.t === 'end') break;
    const act = clone(m.d);""",
"""  GAME.rUndo = [];
  while (true) {
    setPhase('🌐 ' + OPP().toUpperCase(), OPP() + ' is planning their move…');
    GAME.phase = 'remote'; GAME.busy = false;
    const m = await NET.expect(['act', 'end', 'undo']);
    GAME.busy = true; closeSheet();
    if (m.t === 'end') break;
    if (m.t === 'undo') { const sn = GAME.rUndo.pop(); if (sn) { restoreVillage(S.p[pi], sn); syncAll(); toast('↶ ' + esc(OPP()) + ' undid an action', ''); } continue; }
    const act = clone(m.d);
    if (act.kind === 'play') GAME.rUndo = []; else GAME.rUndo.push(clone(S.p[pi]));""")

# keyboard shortcuts for desktop judges (P1, tiny): Ctrl+Z undo, Space end turn, 1-5 pick card, Enter play
rep("window.addEventListener('keydown', e => { if (e.key === 'Escape' && GAME.scEsc",
    """window.addEventListener('keydown', e => {
    if (!GAME.S || /INPUT|TEXTAREA/.test((e.target && e.target.tagName) || '') || !$('modal').classList.contains('hidden')) return;
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'z') { e.preventDefault(); onUndoBtn(); return; }
    if (GAME.phase !== 'action' || GAME.busy) return;
    if (e.key === 'Escape' && GAME.sel) { cancelSel(); return; }
    if (e.key === 'Enter' && GAME.sel && GAME.sel.ready) { e.preventDefault(); onPlayBtn(); return; }
    if (e.key === ' ' && !GAME.sel) { e.preventDefault(); onEndBtn(); return; }
    if (/^[1-6]$/.test(e.key)) { const k = +e.key - 1; if (GAME.S.p[0].hand[k]) onCardTap(k); }
  });
  window.addEventListener('keydown', e => { if (e.key === 'Escape' && GAME.scEsc""")

open(P, 'w', encoding='utf-8').write(h)
print('ok')
