# SIGNAL 5 — Web Prototype

A mobile-first browser prototype of **SIGNAL 5**, a 1 vs 1 disaster-preparedness card strategy game by **Team Pura**.

- Defend your barangay on a 4×4 isometric island, build walls and drainage on tile edges, and send hazards (fire, wind, rain, earthquake, Signal No. 5) at your rival.
- Play **vs CPU** or **online vs a friend** (room code / share link; direct WebRTC with a public relay fallback).
- Single self-contained `index.html` — no build step. Deployed on Vercel as a static site.

Rules follow the **SIGNAL 5 Game Design Document v2.0** (`docs/SIGNAL_5_GDD_v2.0.docx`), rules version `2.0.0`.

## What changed in rules v2.0 (esports-ready edition)

| Area | v2.0 |
|---|---|
| Turn order | Strict alternation: Player A first, Player B last, every round (no double turns) |
| Signal No. 5 | Waits in a **Command slot** (never shuffled), joins your hand in Round 8, expires after Round 9. Landfall: 1 Wind + 1 Flood, +1 Wind in the Eye |
| Buildings | Standard 7 HP, Concrete 10 HP (Barangay Hall unchanged) |
| Card costs | Candlelight 4, Wildfire 7, Strong Gale 2, Hurricane 4, Rainfall 2, Torrential Downpour 4, Magnitude 8 9 |
| Decks | 7–10 Preparedness cards, exactly 1 Signal No. 5; Balanced Kapitan and Fault Line presets adjusted |
| Opening hand | Cards still locked in Round 2 are skipped in the opening deal |
| Ties | Sudden-Death Tsunami (4/3/2/1), then draw (groups) / replay with seats swapped (playoffs) |
| Online fair play | Each player shuffles with a **private seed**; the opponent's browser never holds your hand or deck order. SHA-256 commitments are exchanged before the match and revealed after it; the result screen shows whether the opponent's plays matched their committed deck |
| Timers (online) | 75 s per turn + 60 s time bank per game, +20 s when answering a declared Signal No. 5; 15 s discard |
| Results | Result screen shows Match ID and rules version; **⬇ Result** downloads a JSON result record for tournament reporting |

## Balance simulator

```
node tools/sim.js 1600
```

Runs the game's own rules engine and Kapitan CPU headless (CPU vs CPU, every preset-deck pairing) and prints the GDD §16.4 health metrics. Run it before every balance patch.

## Testing online play locally

Open `index.html?net=bc` in two tabs of the same browser (served over http) to play online through a BroadcastChannel instead of WebRTC.
