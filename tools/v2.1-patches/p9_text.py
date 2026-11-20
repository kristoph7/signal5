# v2.1.1 — UI text cleanup for the national finals (text + small CSS only; no rule or balance changes)
# Terms: "Hazard" cards / "Preparedness" cards · "barangay" (score keeps its name "Village Integrity")
#        "walls and drains" (no "segments") · no dev jargon ("GDD") · sentence-case card text
import sys, re
P = sys.argv[1]
h = open(P, encoding='utf-8').read()
def rep(old, new, count=1):
    global h
    n = h.count(old); assert n == count, f'expected {count} got {n}: {old[:90]!r}'
    h = h.replace(old, new)

# ---------------------------------------------------------------- card text (checked against the rules engine)
CARD_TEXT = {
  'fire1':  'Deal 1 Fire damage and Burn 1. The fire also spreads 1 damage to one adjacent tile you choose.',
  'fire2':  'Deal 2 Fire damage and Burn 2. The fire spreads 1 damage to every adjacent tile.',
  'fire3':  'Deal 3 Fire damage and Burn 3. Every adjacent tile takes 2 Fire damage and Burn 1.',
  'wind1':  'No damage. Puts out level-1 fires (Cigar) on the target and adjacent tiles. Draw 1 card.',
  'wind2':  'Deal 1 Wind damage to a whole row or column. Puts out level-1 and level-2 fires on that line.',
  'wind3':  'Deal 2 Wind damage to the target and every adjacent tile. The target also takes 1 Flood damage and is Flooded. Puts out all fires.',
  'rain1':  'Deal 1 Flood damage. Puts out level-1 and level-2 fires.',
  'rain2':  'Deal 2 Flood damage, plus 1 Flood damage to every adjacent tile. Puts out all fires.',
  'rain3':  'Deal 2 Flood damage to the target and every adjacent tile, and Flood them all. Puts out all fires.',
  'quake1': 'Deal 1 Raw damage. Break 1 wall or drain on the target’s edges (your choice).',
  'quake2': 'Deal 2 Raw damage, plus 1 to every adjacent tile. Break every wall and drain on the target’s edges.',
  'quake3': 'Deal 3 Raw damage to the target, 2 to adjacent tiles and 1 to every other tile. Breaks nearby walls and drains. Aftershock: 1 more Raw damage to the target at the start of your next turn.',
  'signal': 'Command card: it joins your hand when Signal No. 5 unlocks. Declare it that round or the next. Landfall at the start of your next turn: 1 Wind + 1 Flood to every tile, +1 Wind in the 2×2 Eye you choose, and every wall and drain is damaged.',
  'vaccine':'Heal up to 3 injured residents now. Your Health Center heals 1 extra at your next upkeep.',
  'feeding':'Costs 2 CP + 2 Food. Prevents the next 3 injuries until your next turn, and your barangay cannot go hungry.',
  'relief': 'Restore 3 HP to your most damaged buildings. Rebuild 1 destroyed building for 0 Pondo this turn.',
  'drill':  'Until the end of your opponent’s next turn: earthquakes deal 1 less damage per tile and injure no one, and their earthquake cards cost 1 more CP.',
  'tree':   'Plant a mangrove grove on an empty tile. Adjacent tiles take 1 less Wind and Flood damage. Max 2 groves.',
  'ayuda':  'Gain 4 Food. If your Food now covers your population, gain 1 resident.',
  'tesda':  'Gain 3 KP, or train 1 worker for free (Engineers need the DPWH Office).',
}
for cid, txt in CARD_TEXT.items():
    pat = re.compile(r"(\n  " + cid + r": \{ name: '[^']*'[^\n]*\n\s*text: ')([^']*)(')")
    m = pat.search(h); assert m, cid
    h = h[:m.start(2)] + txt.replace("'", "\\'") + h[m.end(2):]

# ---------------------------------------------------------------- building + deck descriptions
rep("desc: 'Pondo income, houses DRRM Officers, evacuation shelter. Required.',",
    "desc: 'Your town center. Earns Pondo every upkeep, houses your DRRM Officers and shelters evacuees. Every barangay needs one.',")
rep("desc: 'Houses residents. Residents earn +1 Pondo per 2 healthy.',",
    "desc: 'Home for your residents. Every 2 healthy residents earn 1 Pondo per upkeep.',")
rep("desc: 'Produces Food. +1 Food if any edge has Drainage (irrigated).',",
    "desc: 'Grows Food every upkeep. Gives 1 extra Food when a drain touches it (irrigation).',")
rep("desc: 'Supplies Power. Shorts when Flooded unless it has a Drainage edge.',",
    "desc: 'Powers your buildings. Shorts out when flooded unless a drain touches it.',")
rep("desc: 'Produces Knowledge Points. Evacuation shelter.',",
    "desc: 'Earns Knowledge Points (KP) every upkeep and shelters evacuees.',")
rep("desc: 'BHW slots. Barangay Health Workers heal Injured residents.',",
    "desc: 'Barangay Health Workers heal injured residents every upkeep. A trained Nurse heals 2 and keeps the injured from leaving.',")
rep("desc: 'Firefighters extinguish Burning tokens. Covered tiles take −1 Fire.',",
    "desc: 'Firefighters put out fires every upkeep. Tiles it covers take 1 less Fire damage.',")
rep("desc: 'Construction Workers: 1 worker action each (build, upgrade, repair, segments).',",
    "desc: 'Each Construction Worker gives 1 worker action per turn: build, upgrade, repair, or add walls and drains.',")
rep("desc: 'Adjacent tiles take −1 Wind and −1 Flood (incl. Tsunami). Can Burn.',",
    "desc: 'Mangroves shield their neighbors: adjacent tiles take 1 less Wind and Flood damage, even from the Tsunami. Groves can burn.',")
rep("{ name: 'GDD Sample', tiles:", "{ name: 'Starter', tiles:")

# ---------------------------------------------------------------- jargon: walls & drains, GDD
rep("why: 'Segment cap ' + segCap(v) + ' (Hall stage)' };", "why: 'Wall & drain limit reached (' + segCap(v) + ') — upgrade your Hall for more' };")
rep("['Segment cap', d.cap]", "['Wall & drain limit', d.cap]")
rep("<p class=\"desc\">Edge segments sit on the grid lines. Cap: <b>", "<p class=\"desc\">Walls and drains sit on the lines between tiles. Built: <b>")
rep("<b>breaks</b> wall/drain segments.", "<b>breaks</b> walls and drains.")
rep("<b>breaks segments</b>", "<b>breaks walls and drains</b>")
rep("Drainage −1/segment max −2", "Drainage −1 per drain, max −2", count=2)
rep("Drainage −1/segment, adjacent Grove", "Drainage −1 per drain, adjacent Grove", count=2)
rep("hire, segments, evacuate, stage up", "hire, add walls and drains, evacuate, upgrade the Hall", count=2)
rep("repairSeg: '🔧 Segment repaired'", "repairSeg: '🔧 Wall/drain repaired'")
rep("toast('Loaded the GDD sample layout (40 Pondo)', 'gold');", "toast('📋 Starter layout placed. Leftover Pondo carries into Round 1.', 'gold');")
rep("$('btnCancel').textContent = '📋 SAMPLE';", "$('btnCancel').textContent = '📋 STARTER';")
rep("Tap <b>📋 SAMPLE</b> for a ready-made layout", "Tap <b>📋 STARTER</b> for a ready-made layout")
rep("Tap <b>📋 SAMPLE</b> for a ready layout.", "Tap <b>📋 STARTER</b> for a ready-made layout.")
rep('<div class="ver">Rules v2.1 · GDD v2.0</div>', '<div class="ver">Rules v2.1</div>')
rep("and the sample layout, and opening hands are dealt automatically.", "and the Starter layout, and opening hands are dealt automatically.")
rep("'Sample layouts are built · your opening hand is ready'", "'Starter layouts are built · your opening hand is ready'")
rep("'⚡ Quick Match: your barangay uses the sample layout and the CPU built “' + esc(lay) + '”. Tap OPPONENT to scout it.'",
    "'⚡ Quick Match: both barangays use a ready-made layout. Tap OPPONENT to scout the CPU’s.'")

# ---------------------------------------------------------------- Hazard / Preparedness naming
rep("${c.kind === 'buff' ? '🛡 BUFF' : '⚠ HAZARD'}", "${c.kind === 'buff' ? '🛡 PREPARE' : '⚠ HAZARD'}")
rep("['dis', 'Disasters', 332, 578, 'rb_dis']", "['dis', 'Hazards', 332, 578, 'rb_dis']")
rep("dis: '🔥 Disasters',", "dis: '🔥 Hazards',")
rep("<p>No buff increases attack. Buffs target your own village.</p>", "<p>Preparedness cards never deal damage. They only affect your own barangay.</p>", count=2)
rep("['🔥 Spread & counters', `<p>Disasters spread to adjacent tiles exactly as the card says.</p>",
    "['🔥 Spread & counters', `<p>Hazards spread to adjacent tiles exactly as the card says.</p>")
rep("<li>Disasters hit the opponent. Wind & Rain may target your own village to put out fires.</li>",
    "<li>Hazards hit your opponent. Wind and Rain cards may also target your own barangay to put out fires.</li>")
rep("<li>Disasters spread to adjacent tiles exactly as the card says.", "<li>Hazards spread to adjacent tiles exactly as the card says.")

# ---------------------------------------------------------------- village -> barangay (score name "Village Integrity" kept)
rep("{ title: 'Fill your village',", "{ title: 'Fill your barangay',")
rep("After Round 10 a Tsunami hits both villages, and the highest <b>Village Integrity</b> wins.", "After Round 10 a Tsunami hits both barangays, and the highest <b>Village Integrity</b> wins.")
rep("You defend your village and act as the hazard controller for your opponent's. After Round 10 a Tsunami hits both villages",
    "You defend your barangay and send hazards at your opponent's. After Round 10 a Tsunami hits both barangays")
rep("<p>After Round 10 a <b>Tsunami</b> hits both villages by row:", "<p>After Round 10 a <b>Tsunami</b> hits both barangays by row:")
rep("'The league’s final evaluation — it hits both villages'", "'The league’s final test — it hits both barangays'")
rep("'Dead even — a second, stronger Tsunami hits both villages'", "'Dead even — a second, stronger Tsunami hits both barangays'")
rep("toast(e.pi === 0 ? '🍚 Your village is HUNGRY — workers skip actions' : '🍚 ' + OPP() + '’s village is hungry'",
    "toast(e.pi === 0 ? '🍚 Your barangay is hungry — workers and health staff skip their jobs this upkeep' : '🍚 ' + OPP() + '’s barangay is hungry'")
rep("If you run short the village is Hungry and workers skip their jobs.", "If you run short, your barangay goes hungry and workers skip their jobs.")
rep("'<p>✔ May target your own village to put out fires (its damage still applies).</p>'", "'<p>✔ Can target your own barangay to put out fires (its damage still applies).</p>'")
rep("'on' : ''}\">🏡 My village</button>", "'on' : ''}\">🏡 My barangay</button>")

# ---------------------------------------------------------------- turn hints, status lines, banners, toasts
rep("'⚠ YOUR TURN', 'Tap a card to attack or prepare — or tap your tiles to build.'", "'▶ YOUR TURN', 'Play a card, or tap your own tiles to build.'", count=3)
rep("setPhase('🗑 REFRESH', 'Discard exactly 1 card, then draw back to 5.')", "setPhase('🗑 DISCARD', 'Pick 1 card to discard. You draw back to 5.')")
rep("setPhase('🗑 REFRESH', OPP() + ' is discarding…')", "setPhase('🗑 DISCARD', OPP() + ' is discarding…')")
rep("setPhase('🔥 BURN STEP', 'Burning tiles take 1 Fire damage, then cool by one level')", "setPhase('🔥 BURN STEP', 'Each burning building takes 1 Fire damage, then its fire weakens by 1.')")
rep("'The opposing Kapitan is acting as hazard controller for your barangay.'", "'The CPU is sending hazards at your barangay. Watch how each one resolves.'")
rep("OPP() + ' is acting as hazard controller for your barangay. You can look around while you wait.'", "OPP() + ' is sending hazards at your barangay. You can look around while you wait.'")
rep("setPhase('🌀 LANDFALL', 'Tap the opponent’s map to place the 2×2 EYE (+1 Wind).')", "setPhase('🌀 LANDFALL', 'Tap your opponent’s island to place the 2×2 Eye (+1 Wind inside it).')")
rep("await banner('LANDFALL!', 'Signal No. 5 — God help us.', 'purple', 1700);", "await banner('LANDFALL!', 'Signal No. 5 makes landfall — brace for impact!', 'purple', 1700);")
rep("toast('👶 +1 resident (Food ≥ 4)', 'good');", "toast('👶 New resident! (4+ Food left over)', 'good');")
rep("e.n + ' injured resident(s) relocated'", "e.n + (e.n === 1 ? ' injured resident went untreated and left the barangay' : ' injured residents went untreated and left the barangay')")
rep("toast('Minimum 8 buildings (you have ' + Eng.buildingCount(v) + ')', 'bad');", "toast('Build at least 8 buildings first (you have ' + Eng.buildingCount(v) + ')', 'bad');")
rep("toast('Choose an OPEN tile', 'bad');", "toast('Pick an empty tile', 'bad');")
rep("toast('Hire workers during your turn (2 Pondo each)', 'gold');", "toast('You can hire workers during your turn (2 Pondo each)', 'gold');")
rep("toast('🌀 Your unused Signal No. 5 expired after Round 9', '');", "toast('🌀 Your Signal No. 5 expired unused', '');")
rep("'🌀 Signal No. 5 has moved from your Command slot into your hand — declare it in Round 8 or 9'",
    "'🌀 Signal No. 5 is now in your hand — declare it this round or next'")
rep("'🌀 ' + OPP() + ' now holds Signal No. 5 (Command slot)'", "'🌀 ' + OPP() + ' now holds Signal No. 5'")
rep("toast('⏱ Time up — discarded the right-most card', 'bad');", "toast('⏱ Time’s up — your right-most card was discarded', 'bad');")
rep("toast('⏱ Time up — turn ended automatically', 'bad');", "toast('⏱ Time’s up — your turn ended automatically', 'bad');")
rep("'⏱ Turn time used — now spending your ' + GAME.bank + ' s time bank'", "'⏱ Turn timer ran out — using your ' + GAME.bank + 's time bank'")
rep("'Turn timer running out — End Turn soon! (bank: ' + (GAME.bank || 0) + ' s)'", "'Turn timer running out — end your turn soon (bank: ' + (GAME.bank || 0) + 's)'")
rep("'Time bank running — End Turn soon!'", "'Time bank running — end your turn soon!'")
rep('<span class="pt" id="phT">⚠ HAZARD PHASE</span><span class="sep"></span><span class="pd" id="phD">Select a card to prepare your move.</span>',
    '<span class="pt" id="phT">▶ YOUR TURN</span><span class="sep"></span><span class="pd" id="phD">Play a card, or tap your own tiles to build.</span>')
rep("text: 'Press <b>END TURN</b> when you’re done. Burning tiles take damage, then you discard 1 card and draw back to 5.'",
    "text: 'Press <b>END TURN</b> when you’re done. Burning buildings take damage, then you discard 1 card and draw back to 5.'")

# ---------------------------------------------------------------- resource bar: consistent labels, shown on laptops
rep("['power', 'ui_energy', 'ENERGY',", "['power', 'ui_energy', 'POWER',")
rep("['drrm', 'ui_shield', 'DRRM',", "['drrm', 'ui_shield', 'OFFICERS',")
rep("[data-layout=\"wide\"] .chip .lb{display:none}",
    "[data-layout=\"wide\"] .chip .lb{display:block;font-size:9px;letter-spacing:.4px;opacity:.85;margin-bottom:1px}")

# ---------------------------------------------------------------- event log: one icon per line, "Setup" heading
rep("for (const l of rows) { if (l.r !== lastR) { html += `<div class=\"lg-r\">Round ${l.r || 'Setup'}</div>`; lastR = l.r; } html += `<div class=\"lg-e ${mine(l.text) ? 'me' : 'op'}\"><i>${icon(l.text)}</i><span>${esc(l.text)}</span></div>`; }",
    "for (const l of rows) { if (l.r !== lastR) { html += `<div class=\"lg-r\">${l.r ? (GAME.S && GAME.S.rounds ? 'Round ' + ((GAME.S.rounds.indexOf(l.r) + 1) || l.r) : 'Round ' + l.r) : 'Setup'}</div>`; lastR = l.r; }\n"
    "    const em = l.text.match(/^(\\p{Extended_Pictographic}[\\uFE0F\\u200D\\p{Extended_Pictographic}]*)\\s*/u); const ic = em ? em[1] : icon(l.text), tx = em ? l.text.slice(em[0].length) : l.text;\n"
    "    html += `<div class=\"lg-e ${mine(l.text) ? 'me' : 'op'}\"><i>${ic}</i><span>${esc(tx)}</span></div>`; }")

# ---------------------------------------------------------------- portrait phones: full-screen menus are landscape
rep("\n#passfx{", "\n@media (orientation:portrait) and (max-width:700px){#scene:not(.hidden)::before{content:'↻  Turn your phone sideways for a bigger view';position:fixed;top:max(14px,env(safe-area-inset-top));left:50%;transform:translateX(-50%);z-index:5;padding:8px 14px;border-radius:999px;background:#071a3dee;border:2px solid #ffd23a;color:#ffe9a0;font:800 13px Nunito,sans-serif;white-space:nowrap;pointer-events:none}}\n#passfx{")

# ---------------------------------------------------------------- card panel keeps proper casing; short summaries for Next Draw
rep("<p>${esc(c.text.charAt(0) + c.text.slice(1).toLowerCase())}</p>", "<p>${esc(c.text)}</p>")
rep("function cardBlurb(id) { const c = CARDS[id]; const t = c.text.replace(/\\s+/g, ' ').trim(); const first = t.split('. ')[0]; return (c.kind === 'disaster' && c.fam !== 'signal' ? 'LV ' + c.lvl + ' · ' : '') + first.replace(/\\.$/, '') + '.'; }",
    "const CARD_SHORT = { fire1: '1 Fire dmg + spread', fire2: '2 Fire dmg + spread', fire3: '3 Fire dmg + spread', wind1: 'Puts out small fires', wind2: '1 Wind dmg to a line', wind3: '2 Wind dmg + area', rain1: '1 Flood dmg', rain2: '2 Flood dmg + spread', rain3: '2 Flood dmg + area', quake1: '1 Raw dmg + break a wall', quake2: '2 Raw dmg + area', quake3: 'Raw dmg to the whole island', signal: 'Landfall on every tile', vaccine: 'Heal 3 injured', feeding: 'Prevent 3 injuries', relief: 'Repair 3 HP + free rebuild', drill: 'Weaken earthquakes', tree: 'Plant a mangrove grove', ayuda: '+4 Food', tesda: '+3 KP or train a worker' };\n"
    "function cardBlurb(id) { const c = CARDS[id]; const t = CARD_SHORT[id] || c.text.split('. ')[0]; return (c.kind === 'disaster' && c.fam !== 'signal' ? 'LV ' + c.lvl + ' · ' : '') + t; }")
# ---------------------------------------------------------------- Rulebook: Turn tab (stale turn-order rule) + Damage tab wording + unlock column
rep("<li><b>Upkeep</b>: (a) Firefighters extinguish (b) worker actions (c) BHWs heal (d) production (e) food & growth (f) injured count down (g) floods drain.</li>",
    "<li><b>Upkeep</b> (automatic): firefighters put out fires → workers get their actions → health workers heal → buildings produce Pondo, Food and KP → residents eat and may grow → untreated injuries count down → floods drain away.</li>", count=2)
rep("<li><b>Command</b>: gain CP (3,4,5,6,7,8,9,10,10,10) + max 1 carry-over.</li>",
    "<li><b>Command</b>: gain Command Points — 3 in Round 1, rising by 1 each round to 10. Up to 1 unspent CP carries over.</li>", count=2)
rep("<li><b>Landfall</b>: your pending Signal No. 5 / Aftershock resolves on the opponent.</li>",
    "<li><b>Landfall</b>: if you declared Signal No. 5 or set up an Aftershock, it hits your opponent now.</li>", count=2)
rep("<li><b>Burn</b>: your burning tiles take 1 Fire.</li><li><b>Refresh</b>: discard 1, draw to 5.</li></ol><p>Player A goes first and Player B goes last in <b>every</b> round, so nobody ever takes two turns in a row.</p>",
    "<li><b>Burn</b>: each of your burning buildings takes 1 Fire damage.</li><li><b>Discard</b>: discard 1 card, then draw back to 5.</li></ol><p><b>Turn order:</b> Player A moves first in Rounds 1–5. At the <b>halftime switch</b> (Round 6) the order flips and Player B moves first until the end, so Player B plays two turns in a row once.</p>", count=2)
rep("<li>Affected tiles; remove damage crossing a Firewall (Fire) or Drainage (Flood). Raw ignores edges.</li><li>Base damage → material modifiers → mitigation (Fire Response −1, Drainage −1 per drain, max −2, Grove −1 Wind/Flood, Drill & Retrofit −1 Raw).</li><li>Floor at 0, reduce HP, injure occupants (minus Rescue), place statuses, extinguish, update states.</li>",
    "<li>Find the tiles hit. Fire that would cross a Firewall, or Flood that would cross a drain, is blocked. Raw damage ignores walls and drains.</li><li>Start from the card’s damage, apply the building’s material (table above), then reductions: Fire Station cover −1 Fire, each drain −1 Flood (max −2), adjacent Grove −1 Wind/Flood, Earthquake Drill or Retrofit −1 Raw.</li><li>Damage never goes below 0. The building loses that much HP, people inside are injured (DRRM Rescue can prevent some), then Burning or Flooded is applied and fires may be put out.</li>", count=2)
rep("<p><b>Burning Ln</b>: at the owner's Burn step deals 1 Fire, then drops a level. <b>Flooded</b>: no production at next upkeep; a Flooded Substation shorts (1 Raw to neighbours) unless it has a drain.</p>",
    "<p><b>Burning (level 1–3)</b>: at its owner’s Burn step the building takes 1 Fire damage, then the fire drops one level. <b>Flooded</b>: produces nothing at the next upkeep. A flooded Substation shorts out (1 Raw damage to its neighbors) unless a drain touches it.</p>", count=2)
rep("<tr><th>Tag</th><th>Fire</th><th>Wind</th><th>Flood</th><th>Raw</th></tr>", "<tr><th>Material</th><th>Fire</th><th>Wind</th><th>Flood</th><th>Raw</th></tr>", count=2)
rep("<td>Round ${CARDS[i].unlock}</td>", "<td style=\"white-space:nowrap\">Round ${RL(CARDS[i].unlock)}</td>", count=2)

open(P, 'w', encoding='utf-8').write(h); print('ok')
