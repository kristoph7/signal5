# Batch 1 / audience: ~4 s cold open on the title island (lightning + SIGNAL NO. 5 alert + siren), once per visit, skippable
import sys
P = sys.argv[1]
h = open(P, encoding='utf-8').read()
def rep(old, new, count=1):
    global h
    n = h.count(old); assert n == count, f'expected {count} got {n}: {old[:90]!r}'
    h = h.replace(old, new)

# Menu island: expose a lightning strike
rep("  M._dbg = () => ({ view, ppl, boats });",
    "  M._dbg = () => ({ view, ppl, boats });\n"
    "  M.strike = (y) => { flash = 1; boltY = y || rnd(220, 520); shake = Math.max(shake, 0.55); sfx('thunder'); };")

# boot: run the cold open before the menu buttons fade in
rep("  $('loadbar').classList.add('hidden'); $('tBtns').classList.remove('hidden'); $('tBtns').classList.add('fadein');",
    "  $('loadbar').classList.add('hidden'); await coldOpen(); $('tBtns').classList.remove('hidden'); $('tBtns').classList.add('fadein');")

rep("(async function boot() {",
"""/* ---------- COLD OPEN (v2.1): a Signal No. 5 strike on the title island, once per visit; tap or any key skips ---------- */
async function coldOpen() {
  let seen = false; try { seen = sessionStorage.getItem('signal5.cold') === '1'; sessionStorage.setItem('signal5.cold', '1'); } catch (e) {}
  let reduced = false; try { reduced = !!(JSON.parse(localStorage.getItem('signal5.settings') || '{}').reduced) || matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) {}
  if (seen || reduced || /[?&]nocold\\b/.test(location.search)) return;
  let skip = false; const sk = () => { skip = true; try { SFX.unlock(); } catch (e) {} };
  window.addEventListener('pointerdown', sk); window.addEventListener('keydown', sk);
  const w = (ms) => new Promise(r => { const t0 = performance.now(); const tick = () => (skip || performance.now() - t0 >= ms) ? r() : setTimeout(tick, 50); tick(); });
  const strike = (y) => { try { Menu.strike && Menu.strike(y); } catch (e) {} };
  try {
    await w(250); strike(300); await w(550); if (!skip) strike(460); await w(500);
    const el = $('s5fx');
    if (!skip && el) {
      $('s5sub').textContent = 'PAGASA WARNING · LANDFALL IMMINENT'; $('s5msg').textContent = 'BUILD. PREPARE. SURVIVE.';
      el.classList.remove('hidden', 'go'); void el.offsetWidth; el.classList.add('go'); try { SFX.play('siren'); } catch (e) {}
      await w(2400); el.classList.add('hidden');
    }
    if (!skip) { strike(380); await w(350); }
  } finally { window.removeEventListener('pointerdown', sk); window.removeEventListener('keydown', sk); const el = $('s5fx'); if (el) el.classList.add('hidden'); }
}
(async function boot() {""")
open(P, 'w', encoding='utf-8').write(h); print('ok')
