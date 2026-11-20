# SIGNAL 5 — v2.1 (batch 1: every P0 item)

**Base:** `v2-esports` @ `892fcf7`. All 10 script blocks are byte-identical to the live signal5-ph.vercel.app build.
**Install:** replace `index.html`. It's still one self-contained file (14.6 MB, +20 KB), with no new assets or dependencies.
This replaces the earlier part-1 file; everything from part 1 is included here.

---

## 1. Rule changes (Rules v2.0.0 → v2.1.0)

All balance numbers come from headless CPU-vs-CPU matches using the game's own engine and AI.

| Change | Before | After |
|---|---|---|
| **Halftime switch:** Player A moves first in Rounds 1–5, Player B in Rounds 6–10 | Player B won 59.3% (1,000 mirror matches) | **48.7%** (2,500 matches, all 4 decks) |
| **Collapse knockout:** a village below **20% Integrity** during Rounds 1–10 is knocked out (opponent gets Gold). It doesn't apply during the final Tsunami. | 0 knockouts in about 490 matches | Knockout in about 14% of matches, nearly all at Signal No. 5 landfall |
| **Typhoon Season:** one Gentle Wind → one Magnitude 3 | 44.6% | about 48% (every deck now 45.6–53.8%) |

Rejected options, with their results, are in the earlier part-1 changelog. All rule text (coin toss, How to Play, Rulebook, tutorial, Round 6 banner and the result reason) has been updated to match.

⚠️ **Online:** both players must run v2.1. The turn order changed, so a v2.0 phone against a v2.1 phone will desync.

## 2. New: ⚡ Quick Match (deck screen)

- **6 rounds** (Rounds 1, 3, 5, 8, 9, 10). Every unlock still fires: Level 2 and Level 3 hazards, the Hall stages, Signal No. 5, the halftime switch and the Tsunami. The round counter reads "ROUND 1/6", and lock messages use the same numbers.
- No setup: both sides use the sample layout and your opening hand is picked for you. **About 10–13 seconds from the deck screen to your first turn** (the full flow takes several minutes).
- It's **Balanced vs Balanced** with the Rookie CPU. In 6 rounds the deck matchups swing hard (Typhoon 70%, Fire 39%), so the mirror match keeps the demo fair. Seat balance is 47.4% (800 matches).
- Why 6 rounds and not 5: every 5-round format gave the last player in the final round 81–88% (I tested all 32 turn orders). Keeping Rounds 8–9–10 together fixes it.

## 3. New: 👥 Pass & Play (deck screen)

- Two players on **one device, no internet**. This is your stage backup if the venue network fails.
- Quick (6 rounds) or Full (10 rounds). Balanced mirror on both sides, sample layouts, automatic opening hands.
- An opaque "Pass the device to Player 2" screen covers the hand between turns. The UI always shows the acting player as "you", and the result screen names the winner ("P2 WINS!").

## 4. Gameplay

- **Hover preview** (mouse): see the damage before you tap, including the **Integrity change** (`📉 100→87%`) and a `☠ KNOCKOUT!` warning. The original preview-after-tap already existed and is unchanged on phones.
- **Undo** (↶ UNDO button, or Ctrl+Z) for build, upgrade, repair, hire, train, evacuate, retrofit and wall/drain actions. It clears when you play a card or end your turn. It works **online** too: the rival's game mirrors the undo.
- **Keyboard:** `1`–`6` pick a card, `Enter` play, `Esc` cancel, `Space` end turn, `Ctrl+Z` undo.
- **Collapse line:** a red marker at 20% on both Integrity bars. The bar pulses within 10 points of it, with a one-time warning for each side.

## 5. Audio (rewritten module, same interface; still no audio files)

Listen: `signal5-v21-audio-preview.mp3`, about 36 s, recorded from the game's own audio output. It plays, in order: title theme → early game → mid game → Signal pending (with voice line) → Level 3 impact → Tsunami → win.

- **Storm bed:** looping rain plus gusting wind that grows each round and peaks at the Tsunami. It follows the **SFX** toggle.
- **Music that changes with the match:** drums from Round 5, a faster tempo and snare from Round 8, and a rising **siren pad while a Signal No. 5 is pending**.
- **Ducking:** the music dips under sirens, big crashes and the Tsunami, so the action sounds come through.
- **Kulintang-style title theme:** FM bell tones on a pentatonic ostinato, a low agung-style gong and a dabakan-style hand drum. The same bells finish the win jingle, and a gong ends the loss.
- **Level 3 hazards** (Wildfire, Hurricane, Torrential Downpour, Magnitude 8) and landfall add a heavy sub-bass impact.
- **Voice call** when Signal No. 5 is raised: "Signal Number 5! Lumikas na!" This uses the browser's text-to-speech and is **a stand-in**; replace it with a recorded voice line if you can. The voice depends on the device, and some phones have no Filipino voice.
- Mixing: peak −3.5 dB with no clipping. The rain layer was tuned down after a spectrum check showed it masking the music.

## 6. Opening scene + art

- **~4.5 s opening scene** on the title island: lightning, the "PAGASA WARNING · LANDFALL IMMINENT / SIGNAL NO. 5" overlay with the siren, then the menu. It plays **once per visit**; any tap or key skips it, and it's off when reduced motion is set (in Settings or by the device). Add `?nocold` to the URL to turn it off for a session. Sound only plays if the browser allows it before the first tap (most don't), so the first showing is usually silent.
- No mirrored, backwards logo on the loading screen on wide or tablet screens. Footer now reads "Rules v2.1".

---

## Verified (headless Chrome, served locally)

| Check | Result |
|---|---|
| All scripts parse, page loads | ✅ zero console errors at 1280×800 and 762×834 |
| Full 10-round CPU match through the real UI (×3) | ✅ completed with zero errors; turn log shows the halftime order |
| Quick Match end to end | ✅ 6 rounds, Tsunami, result screen, zero errors |
| Pass & Play end to end (Quick) | ✅ seats swap behind the pass screen, winner named, zero errors |
| **Online (two-tab lockstep, `?net=bc`)** | ✅ build → undo → turn change: both games identical, 0 desyncs, the rival sees "undid an action" |
| Undo / hover preview / keyboard | ✅ Pondo 12→10→12, actions 2→1→2, walls 3→2; preview "💥 2 dmg · 📉 100→97%" |
| Tutorial | ✅ runs, no errors |
| Patch scripts | ✅ applying them to the original reproduces this file byte-for-byte |

## Please test yourselves before finals

1. **Online between two real phones** over mobile data and over venue Wi-Fi. I could only test the two-tab mode, not real WebRTC or the public relay.
2. **Real phones** (low-end Android plus iPhone): Pass & Play, the button layout on the deck screen, and audio once you tap.
3. **Listen** to the soundtrack on real speakers. I tuned it from measurements and a spectrum, not by ear.

## Re-applying to newer code

`patches/` holds one script per change. Run them in order (p1 → p8) with `python3 pN_name.py index.html`; `p7_audio.py` needs `sfx_v21.js` next to it. Each script stops with a clear error if the code it expects has changed. `balance_sim.js` is the Node simulator used for every balance number in this file.
