
'use strict';
/* ================= SIGNAL 5 — SYNTH AUDIO v2.1 (no files) =================
   Same API as v2.0 (play, setSfx, setMusic, unlock, S) plus:
   scene('title'|'game'|'over'), intensity(0..2), danger(bool), storm(0..1), duck(sec), voice(text)
   • Storm bed: looping rain + gusting wind, level follows the match (ambience follows the SFX toggle)
   • Adaptive music: chiptune loop + drums (mid-game) + faster/snare finale + siren pad while a Signal is pending
   • Kulintang-style bell ensemble (melody + agung gong + dabakan drum) on the title and in the win flourish
   • Ducking: music dips under sirens, big crashes and the Tsunami                                        */
const SFX = (() => {
  let ac = null, master, sfxBus, musBus, ambBus, noiseBuf; const S = { sfx: true, music: true, started: false };
  const MUS_VOL = 0.22; let duckUntil = 0;
  const st = { scene: 'title', intensity: 0, danger: false, storm: 0.2 };
  let rainG, windG, windF;
  function ensure() {
    if (ac) { if (ac.state === 'suspended') ac.resume(); return true; }
    try { ac = new (window.AudioContext || window.webkitAudioContext)(); } catch (e) { return false; }
    master = ac.createGain(); master.gain.value = 0.8; master.connect(ac.destination);
    sfxBus = ac.createGain(); sfxBus.gain.value = S.sfx ? 0.9 : 0; sfxBus.connect(master);
    musBus = ac.createGain(); musBus.gain.value = S.music ? MUS_VOL : 0; musBus.connect(master);
    ambBus = ac.createGain(); ambBus.gain.value = 1; ambBus.connect(sfxBus);
    noiseBuf = ac.createBuffer(1, ac.sampleRate * 2, ac.sampleRate); const d = noiseBuf.getChannelData(0); for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;
    buildStorm();
    return true;
  }
  function env(g, t, a, peak, dec, sus = 0.0001) { g.gain.cancelScheduledValues(t); g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(peak, t + a); g.gain.exponentialRampToValueAtTime(Math.max(sus, 0.0001), t + a + dec); }
  function noise(t, dur, type, f0, f1, peak = 0.5, q = 1, bus) {
    const s = ac.createBufferSource(); s.buffer = noiseBuf; s.loop = true;
    const f = ac.createBiquadFilter(); f.type = type; f.Q.value = q; f.frequency.setValueAtTime(f0, t); f.frequency.exponentialRampToValueAtTime(Math.max(20, f1), t + dur);
    const g = ac.createGain(); env(g, t, 0.01, peak, dur);
    s.connect(f); f.connect(g); g.connect(bus || sfxBus); s.start(t); s.stop(t + dur + 0.05);
  }
  function tone(t, freq, dur, type = 'square', peak = 0.2, slide = 0, bus) {
    const o = ac.createOscillator(); o.type = type; o.frequency.setValueAtTime(freq, t); if (slide) o.frequency.exponentialRampToValueAtTime(Math.max(20, freq * slide), t + dur);
    const g = ac.createGain(); env(g, t, 0.005, peak, dur); o.connect(g); g.connect(bus || sfxBus); o.start(t); o.stop(t + dur + 0.05);
  }
  // kulintang-like bronze gong: FM bell with an inharmonic partial and a fast-decaying strike
  function bell(t, f, dur = 0.9, peak = 0.16, bus) {
    const c = ac.createOscillator(), m = ac.createOscillator(), mg = ac.createGain(), g = ac.createGain();
    c.type = 'sine'; m.type = 'sine'; c.frequency.value = f; m.frequency.value = f * 2.76;
    mg.gain.setValueAtTime(f * 2.2, t); mg.gain.exponentialRampToValueAtTime(f * 0.05, t + dur * 0.6);
    m.connect(mg); mg.connect(c.frequency); c.connect(g); g.connect(bus || musBus);
    env(g, t, 0.003, peak, dur); c.start(t); m.start(t); c.stop(t + dur + 0.1); m.stop(t + dur + 0.1);
  }
  function gong(t, f = 98, peak = 0.35, bus) { // agung: low hanging gong with a little pitch bend
    const o = ac.createOscillator(), g = ac.createGain(); o.type = 'sine'; o.frequency.setValueAtTime(f * 1.04, t); o.frequency.exponentialRampToValueAtTime(f, t + 0.25);
    const o2 = ac.createOscillator(); o2.type = 'sine'; o2.frequency.value = f * 2.01; const g2 = ac.createGain(); env(g2, t, 0.005, peak * 0.25, 1.2);
    env(g, t, 0.01, peak, 2.4); o.connect(g); o2.connect(g2); g.connect(bus || musBus); g2.connect(bus || musBus); o.start(t); o2.start(t); o.stop(t + 2.6); o2.stop(t + 1.4);
  }
  const P = {
    click: (t) => tone(t, 880, 0.06, 'square', 0.08, 1.4),
    tap: (t) => tone(t, 520, 0.05, 'triangle', 0.12, 1.2),
    card: (t) => { noise(t, 0.18, 'bandpass', 1200, 4000, 0.25, 2); },
    whoosh: (t) => noise(t, 0.45, 'bandpass', 400, 2400, 0.3, 1.5),
    build: (t) => { tone(t, 160, 0.12, 'square', 0.25, 0.6); noise(t, 0.12, 'lowpass', 900, 200, 0.4); tone(t + 0.1, 660, 0.1, 'square', 0.1); tone(t + 0.18, 990, 0.14, 'square', 0.1); },
    coin: (t) => { tone(t, 988, 0.07, 'square', 0.1); tone(t + 0.07, 1318, 0.18, 'square', 0.1); },
    error: (t) => { tone(t, 180, 0.12, 'sawtooth', 0.14); tone(t + 0.12, 140, 0.16, 'sawtooth', 0.14); },
    fire: (t) => { noise(t, 0.9, 'lowpass', 3000, 300, 0.6); tone(t, 90, 0.5, 'sawtooth', 0.2, 0.5); for (let i = 0; i < 8; i++) noise(t + Math.random() * 0.8, 0.03, 'highpass', 3000, 3000, 0.25); },
    crackle: (t) => { for (let i = 0; i < 4; i++) noise(t + Math.random() * 0.4, 0.025, 'highpass', 2500, 2500, 0.18); },
    wind: (t) => noise(t, 1.4, 'bandpass', 300, 1400, 0.45, 3),
    rain: (t) => noise(t, 1.6, 'highpass', 4000, 2500, 0.22),
    splash: (t) => { noise(t, 0.35, 'lowpass', 2500, 300, 0.45); tone(t, 300, 0.2, 'sine', 0.15, 0.4); },
    quake: (t) => { noise(t, 1.4, 'lowpass', 180, 50, 0.9); tone(t, 45, 1.2, 'sawtooth', 0.35, 0.7); },
    crash: (t) => { noise(t, 0.7, 'lowpass', 1600, 120, 0.7); tone(t, 70, 0.5, 'square', 0.25, 0.5); duck(0.6); },
    thunder: (t) => { noise(t, 0.08, 'highpass', 2000, 2000, 0.6); noise(t + 0.05, 1.8, 'lowpass', 600, 60, 0.8); },
    block: (t) => { tone(t, 1200, 0.08, 'square', 0.14); tone(t + 0.06, 1600, 0.12, 'triangle', 0.12); },
    steam: (t) => noise(t, 0.6, 'highpass', 5000, 1500, 0.25),
    siren: (t) => { duck(2.2); for (let i = 0; i < 3; i++) { tone(t + i * 0.6, 600, 0.3, 'sawtooth', 0.12, 1.5); tone(t + i * 0.6 + 0.3, 900, 0.3, 'sawtooth', 0.12, 0.66); } },
    tsunami: (t) => { duck(4.5); noise(t, 3.2, 'lowpass', 300, 1500, 0.8); noise(t + 1, 2.2, 'bandpass', 800, 200, 0.5); tone(t, 38, 3.4, 'sine', 0.4, 0.8); },
    heal: (t) => { [523, 659, 784, 1046].forEach((f, i) => tone(t + i * 0.07, f, 0.18, 'triangle', 0.12)); },
    turn: (t) => { [392, 523, 659].forEach((f, i) => tone(t + i * 0.09, f, 0.16, 'square', 0.09)); },
    win: (t) => { duck(3); [523, 659, 784, 1046, 784, 1046, 1318].forEach((f, i) => tone(t + i * 0.12, f, 0.22, 'square', 0.12)); gong(t, 98, 0.4, sfxBus); [0, 2, 4, 7, 9, 12].forEach((n, i) => bell(t + 0.9 + i * 0.11, 523 * Math.pow(2, n / 12), 1.1, 0.14, sfxBus)); },
    lose: (t) => { duck(3); [392, 349, 311, 262].forEach((f, i) => tone(t + i * 0.22, f, 0.32, 'triangle', 0.15)); gong(t + 0.9, 73, 0.35, sfxBus); },
    medal: (t) => { [784, 988, 1318].forEach((f, i) => tone(t + i * 0.1, f, 0.3, 'square', 0.1)); bell(t + 0.32, 1568, 0.9, 0.1, sfxBus); },
    short: (t) => { for (let i = 0; i < 6; i++) tone(t + i * 0.05, 1800 + Math.random() * 1500, 0.03, 'square', 0.1); },
    // v2.1: heavy layer for Level 3 hazards and landfall
    boom: (t) => { duck(1.2); tone(t, 55, 1.4, 'sine', 0.55, 0.45); noise(t, 1.6, 'lowpass', 900, 40, 0.8); noise(t + 0.02, 0.12, 'highpass', 2500, 1200, 0.4); },
  };
  let lastPlay = {};
  function play(name, delay = 0) {
    if (!S.sfx || !ensure()) return;
    const now = performance.now(); if (lastPlay[name] && now - lastPlay[name] < 40) return; lastPlay[name] = now;
    try { P[name] && P[name](ac.currentTime + delay); } catch (e) {}
  }

  /* ---------- storm bed ---------- */
  function buildStorm() {
    const rs = ac.createBufferSource(); rs.buffer = noiseBuf; rs.loop = true;
    const rf = ac.createBiquadFilter(); rf.type = 'highpass'; rf.frequency.value = 2500; const rl = ac.createBiquadFilter(); rl.type = 'lowpass'; rl.frequency.value = 7500; rainG = ac.createGain(); rainG.gain.value = 0;
    rs.connect(rf); rf.connect(rl); rl.connect(rainG); rainG.connect(ambBus); rs.start();
    const ws = ac.createBufferSource(); ws.buffer = noiseBuf; ws.loop = true; ws.playbackRate.value = 0.7;
    windF = ac.createBiquadFilter(); windF.type = 'bandpass'; windF.Q.value = 1.4; windF.frequency.value = 520; windG = ac.createGain(); windG.gain.value = 0;
    const lfo = ac.createOscillator(); lfo.frequency.value = 0.11; const lg = ac.createGain(); lg.gain.value = 260; lfo.connect(lg); lg.connect(windF.frequency); lfo.start();
    const gust = ac.createOscillator(); gust.frequency.value = 0.067; const gg = ac.createGain(); gg.gain.value = 0; gust.connect(gg); gg.connect(windG.gain); gust.start(); windG._gust = gg;
    ws.connect(windF); windF.connect(windG); windG.connect(ambBus); ws.start();
    applyStorm(0.01);
  }
  function applyStorm(ramp = 1.5) {
    if (!ac || !rainG) return; const t = ac.currentTime, L = Math.max(0, Math.min(1, st.storm)) * (st.danger ? 1.25 : 1);
    rainG.gain.setTargetAtTime(0.05 * L, t, ramp); windG.gain.setTargetAtTime(0.09 * L, t, ramp); windG._gust.gain.setTargetAtTime(0.06 * L, t, ramp);
  }
  function storm(level) { st.storm = level; applyStorm(); }
  function duck(sec) { if (!ac || !musBus || !S.music) return; const t = ac.currentTime; duckUntil = Math.max(duckUntil, t + sec);
    musBus.gain.cancelScheduledValues(t); musBus.gain.setTargetAtTime(MUS_VOL * 0.22, t, 0.05); musBus.gain.setTargetAtTime(MUS_VOL, duckUntil, 0.6); }

  /* ---------- adaptive music ---------- */
  let musTimer = null, step = 0, next = 0;
  const scale = [0, 2, 4, 7, 9, 12, 14, 16];
  const prog = [[0, 'C'], [5, 'F'], [7, 'G'], [9, 'Am']];
  const KUL = [0, 2, 4, 7, 9, 12, 14]; // kulintang-like pentatonic row (low to high)
  const KPAT = [0, 2, 3, 2, 4, 3, 2, 1, 0, 2, 3, 5, 4, 3, 1, 2]; // binalig-style ostinato (indices into KUL)
  function mtone(t, f, d, type, g) { const o = ac.createOscillator(); o.type = type; o.frequency.value = f; const gg = ac.createGain(); env(gg, t, 0.01, g, d); o.connect(gg); gg.connect(musBus); o.start(t); o.stop(t + d + 0.05); }
  function kick(t, g = 0.5) { const o = ac.createOscillator(); o.type = 'sine'; o.frequency.setValueAtTime(140, t); o.frequency.exponentialRampToValueAtTime(42, t + 0.14); const gg = ac.createGain(); env(gg, t, 0.003, g, 0.2); o.connect(gg); gg.connect(musBus); o.start(t); o.stop(t + 0.3); }
  function hat(t, g = 0.06) { noise(t, 0.04, 'highpass', 7000, 7000, g, 1, musBus); }
  function snare(t, g = 0.18) { noise(t, 0.16, 'bandpass', 1800, 900, g, 0.8, musBus); tone(t, 190, 0.08, 'triangle', g * 0.6, 0.7, musBus); }
  function dabakan(t, g = 0.16) { noise(t, 0.09, 'lowpass', 900, 300, g, 1.2, musBus); }
  function bpm() { return st.scene === 'title' ? 96 : st.danger ? 122 : st.intensity >= 2 ? 114 : 104; }
  function tick() {
    while (next < ac.currentTime + 0.3) {
      const spb = 60 / bpm() / 2, t = next;
      if (st.scene === 'title') {
        const k = step % 16, bar = Math.floor(step / 16) % 4;
        if (k === 0) gong(t, bar % 2 ? 87 : 98, 0.32);
        if (k % 2 === 0 || Math.random() < 0.35) bell(t, 262 * Math.pow(2, KUL[(KPAT[k] + (bar === 3 ? 1 : 0)) % KUL.length] / 12), 0.7, k % 4 === 0 ? 0.21 : 0.14);
        if (k % 4 === 2 || k % 8 === 7) dabakan(t, k % 4 === 2 ? 0.16 : 0.09);
      } else if (st.scene === 'game') {
        const bar = Math.floor(step / 8) % 4, beat = step % 8; const root = 196 * Math.pow(2, prog[bar][0] / 12);
        const tense = st.intensity >= 2 || st.danger;
        if (beat % 4 === 0) mtone(t, root / 2, spb * 3, 'triangle', 0.5);
        if (beat % 2 === 1) mtone(t, root, spb * 0.6, 'square', 0.07);
        if ((step * 7 + bar) % 3 !== 0) { const n = scale[(step * 5 + bar * 3) % scale.length]; mtone(t, root * 2 * Math.pow(2, (n - (tense ? 1 : 0)) / 12), spb * 0.9, 'square', 0.05); }
        if (st.intensity >= 1) { if (beat === 0 || beat === 4 || (st.intensity >= 2 && beat === 6)) kick(t, 0.42); if (beat % 2 === 1) hat(t); }
        if (st.intensity >= 2 && (beat === 2 || beat === 6)) snare(t);
        if (st.danger && beat === 0) { // siren pad: two-note rising wail, one per bar
          const o = ac.createOscillator(), f = ac.createBiquadFilter(), g = ac.createGain(); o.type = 'sawtooth'; f.type = 'lowpass'; f.frequency.value = 1100;
          o.frequency.setValueAtTime(330, t); o.frequency.linearRampToValueAtTime(495, t + spb * 4); o.frequency.linearRampToValueAtTime(330, t + spb * 8);
          env(g, t, spb * 2, 0.07, spb * 6); o.connect(f); f.connect(g); g.connect(musBus); o.start(t); o.stop(t + spb * 8 + 0.1);
        }
        if (step % 32 === 0 && st.intensity >= 1) bell(t, 523 * (st.danger ? 0.94 : 1), 1.0, 0.07); // a kulintang accent each phrase
      }
      next += spb; step++;
    }
  }
  function startMusic() { if (musTimer || !ensure()) return; next = ac.currentTime + 0.1; musTimer = setInterval(tick, 100); }
  function stopMusic() { clearInterval(musTimer); musTimer = null; }
  function scene(name) { if (st.scene === name) return; st.scene = name; step = 0; if (name === 'over') { stopMusic(); } else if (S.music && S.started) startMusic(); if (name === 'title') storm(0.22); }
  function intensity(n) { st.intensity = n; }
  function danger(on) { on = !!on; if (st.danger === on) return; st.danger = on; applyStorm(0.8); }
  function setSfx(on) { S.sfx = on; if (sfxBus) sfxBus.gain.value = on ? 0.9 : 0; }
  function setMusic(on) { S.music = on; if (on) { ensure(); musBus.gain.value = MUS_VOL; if (st.scene !== 'over') startMusic(); } else { if (musBus) musBus.gain.value = 0; stopMusic(); } }
  function unlock() { if (S.started) return; S.started = true; ensure(); applyStorm(2); if (S.music && st.scene !== 'over') startMusic(); }
  // Browser text-to-speech stand-in for a recorded voice line (replace with a recorded clip when available)
  function voice(text, lang = 'fil-PH') {
    try {
      if (!S.sfx || !window.speechSynthesis) return; const u = new SpeechSynthesisUtterance(text);
      const vs = speechSynthesis.getVoices(); const v = vs.find(x => /^fil|^tl/i.test(x.lang)) || vs.find(x => /en-PH/i.test(x.lang)) || vs.find(x => /^en/i.test(x.lang));
      if (v) { u.voice = v; u.lang = v.lang; } else u.lang = lang; u.rate = 0.95; u.pitch = 0.9; u.volume = 0.9; speechSynthesis.cancel(); speechSynthesis.speak(u);
    } catch (e) {}
  }
  return { play, setSfx, setMusic, unlock, S, scene, intensity, danger, storm, duck, voice, _st: st };
})();
window.SFX = SFX;

