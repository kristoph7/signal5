
'use strict';
/* ================= SIGNAL 5 — ONLINE v2.2 (lockstep, multi-path) =================
   Every game message has a sequence number; the receiver de-duplicates, re-orders and
   acknowledges, and anything unacknowledged is re-sent. The SAME message goes out on
   every path that is up, so whichever arrives first wins:
   • CLOUD  — Supabase Realtime broadcast over a secure WebSocket (wss, port 443).
              Primary path: works on school/venue Wi-Fi, mobile data, CGNAT, any browser.
   • DIRECT — WebRTC data channel via PeerJS (when the network allows it; lowest latency).
   • RELAY  — ntfy.sh HTTPS/SSE, only used while the cloud socket is down.
   Weak-signal handling: heartbeats, dead-socket detection, instant reconnect on
   'online' / tab-visible, fast re-sends, and an opponent-silence indicator.
   ?net=bc uses a BroadcastChannel (two tabs, same browser) for offline testing.          */
const NET = (() => {
  const N = { role: null, code: null, status: 'off', p2p: false, relay: false, cloud: false, mode: 'off', handlers: {}, queue: [], waiters: [],
    seq: 0, sent: {}, acked: 0, recv: 0, buf: {}, lastHeard: 0, rtt: 0, onStatus: null, onMessage: null, closed: false };
  // Supabase project "signal5-realtime" (Singapore). The anon key is a public client key: the
  // project has no tables, so it only allows joining Realtime broadcast rooms.
  const SB_URL = 'wss://adjvpffeayevqqzsnglt.supabase.co/realtime/v1/websocket';
  const SB_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFkanZwZmZlYXlldnFxenNuZ2x0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTU1MjU1NDksImV4cCI6MjExMTEwMTU0OX0.k8qVqbIdQpPpHrAkzD-4miUKkLvQtFzzkMFkhHiEV6E';
  const RELAY = 'https://ntfy.sh/';
  const PEER_CDN = 'https://cdn.jsdelivr.net/npm/peerjs@1.5.4/dist/peerjs.min.js';
  const ALPH = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  const topic = () => 'signal5-room-' + N.code.toLowerCase() + '-v22';
  const peerId = (r) => 'signal5-' + N.code.toLowerCase() + '-v22-' + r;
  const testMode = /[?&]net=bc/.test(location.search);
  let bc = null, es = null, peer = null, conn = null, postChain = Promise.resolve(), resendTimer = null, pingTimer = null;

  function setStatus() {
    const silent = N.lastHeard && Date.now() - N.lastHeard > 10000;
    const s = N.p2p ? 'p2p' : N.cloud ? 'cloud' : (N.relay || bc) ? 'relay' : 'connecting';
    N.status = s; N.onStatus && N.onStatus(s, { silent, rtt: N.rtt });
  }
  function newCode() { let c = ''; for (let i = 0; i < 6; i++) c += ALPH[Math.floor(Math.random() * ALPH.length)]; return c; }

  /* ---- inbound ---- */
  function onRaw(text) {
    let m; try { m = typeof text === 'string' ? JSON.parse(text) : text; } catch (e) { return; }
    if (!m || m.f === N.role || m.room !== N.code) return;
    const wasSilent = N.lastHeard && Date.now() - N.lastHeard > 10000;
    N.lastHeard = Date.now(); if (wasSilent) setStatus();
    if (m.a > N.acked) { for (let s = N.acked + 1; s <= m.a; s++) delete N.sent[s]; N.acked = m.a; }
    if (m.t === 'ack') return;
    if (m.t === 'ping') { raw({ f: N.role, room: N.code, t: 'pong', at: m.at, a: N.recv }, true); return; }
    if (m.t === 'pong') { if (m.at) N.rtt = Date.now() - m.at; return; }
    if (m.s <= N.recv || N.buf[m.s]) { sendAck(); return; }
    N.buf[m.s] = m;
    while (N.buf[N.recv + 1]) { const x = N.buf[N.recv + 1]; delete N.buf[N.recv + 1]; N.recv++; deliver(x); }
    sendAck();
  }
  let ackTimer = null;
  const fast = () => N.p2p || N.cloud || bc;
  function sendAck() { clearTimeout(ackTimer); ackTimer = setTimeout(() => raw({ f: N.role, room: N.code, t: 'ack', a: N.recv }, true), fast() ? 80 : 1500); }
  function deliver(m) {
    if (N.onMessage && N.onMessage(m)) return; // control messages handled by app
    const w = N.waiters.findIndex(w => w.types.includes(m.t));
    if (w >= 0 && N.queue.length === 0) { const W = N.waiters.splice(w, 1)[0]; W.res(m); return; }
    N.queue.push(m); flushWaiters();
  }
  function flushWaiters() {
    while (N.queue.length && N.waiters.length) {
      const m = N.queue[0]; const wi = N.waiters.findIndex(w => w.types.includes(m.t));
      if (wi < 0) return; N.queue.shift(); N.waiters.splice(wi, 1)[0].res(m);
    }
  }
  N.expect = (types) => new Promise(res => { types = [].concat(types); N.waiters.push({ types, res }); flushWaiters(); });
  N.pending = (type) => N.queue.some(m => m.t === type);

  /* ---- outbound: every path that is up ---- */
  function raw(obj, light) {
    const txt = JSON.stringify(obj);
    if (bc) { bc.postMessage(txt); return; }
    let sent = false;
    if (conn && conn.open) { try { conn.send(txt); sent = true; } catch (e) {} }
    if (sbSend(txt)) sent = true;
    if (!sent) { if (light) { if (es) relayPost(txt); } else if (Date.now() - N.t0 > 6000) relayPost(txt); } // the cloud usually joins in <1 s; resend-on-join covers that window
  }
  function relayPost(txt) {
    if (!es) startRelay(); // lazily open the backup relay only when it is needed
    postChain = postChain.then(async () => {
      for (let k = 0; k < 3; k++) {
        try { const r = await fetch(RELAY + topic(), { method: 'POST', body: txt }); if (r.ok) return; } catch (e) {}
        await new Promise(r => setTimeout(r, 500 * (k + 1)));
      }
    });
  }
  N.send = (t, d = {}) => {
    const m = { f: N.role, room: N.code, s: ++N.seq, t, d, a: N.recv, at: Date.now() };
    N.sent[m.s] = m; raw(m); return m.s;
  };
  function resendAll() { for (const s in N.sent) { const m = N.sent[s]; m.at = Date.now(); m.a = N.recv; raw(m); } }
  function resendLoop() {
    resendTimer = setInterval(() => {
      const now = Date.now(), wait = fast() ? 1800 : 5000;
      for (const s in N.sent) { const m = N.sent[s]; if (now - m.at > wait) { m.at = now; m.a = N.recv; raw(m); } }
      setStatus();
    }, 700);
    pingTimer = setInterval(() => { if (!N.closed) raw({ f: N.role, room: N.code, t: 'ping', at: Date.now(), a: N.recv }, true); }, 4000);
  }

  /* ---- CLOUD: Supabase Realtime broadcast (raw Phoenix protocol v1, no library) ---- */
  let ws = null, sbRef = 0, joinRef = null, hbTimer = null, hbPending = null, sbRetry = 0, sbReconnect = null, sbLastIn = 0;
  const chan = () => 'realtime:signal5-' + N.code.toLowerCase();
  function sbSend(txt) {
    if (!ws || ws.readyState !== 1 || !N.cloud) return false;
    try { ws.send(JSON.stringify({ topic: chan(), event: 'broadcast', payload: { type: 'broadcast', event: 'm', payload: { x: txt } }, ref: String(++sbRef), join_ref: joinRef })); return true; } catch (e) { return false; }
  }
  function sbConnect() {
    if (testMode || N.closed) return;
    clearTimeout(sbReconnect); sbReconnect = null;
    try { if (ws) { ws.onclose = null; ws.close(); } } catch (e) {}
    N.cloud = false; setStatus();
    let sock;
    try { sock = new WebSocket(SB_URL + '?apikey=' + encodeURIComponent(SB_KEY) + '&vsn=1.0.0'); } catch (e) { sbSchedule(); return; }
    ws = sock;
    const openTimer = setTimeout(() => { if (ws === sock && sock.readyState !== 1) { try { sock.close(); } catch (e) {} } }, 8000);
    sock.onopen = () => {
      clearTimeout(openTimer); sbLastIn = Date.now();
      joinRef = String(++sbRef);
      sock.send(JSON.stringify({ topic: chan(), event: 'phx_join', payload: { config: { broadcast: { ack: false, self: false }, presence: { enabled: false }, private: false }, access_token: SB_KEY }, ref: joinRef, join_ref: joinRef }));
      clearInterval(hbTimer);
      hbTimer = setInterval(() => {
        if (ws !== sock || sock.readyState !== 1) return;
        if (hbPending && Date.now() - hbPending > 8000) { try { sock.close(); } catch (e) {} return; } // dead socket: reconnect
        if (Date.now() - sbLastIn > 30000) { try { sock.close(); } catch (e) {} return; }
        hbPending = Date.now(); try { sock.send(JSON.stringify({ topic: 'phoenix', event: 'heartbeat', payload: {}, ref: String(++sbRef) })); } catch (e) {}
      }, 15000);
    };
    sock.onmessage = (e) => {
      sbLastIn = Date.now(); let m; try { m = JSON.parse(e.data); } catch (er) { return; }
      if (m.topic === 'phoenix' && m.event === 'phx_reply') { hbPending = null; return; }
      if (m.event === 'phx_reply' && m.ref === joinRef) {
        if (m.payload && m.payload.status === 'ok') { N.cloud = true; sbRetry = 0; setStatus(); resendAll(); }
        else { try { sock.close(); } catch (er) {} }
        return;
      }
      if (m.event === 'broadcast' && m.payload && m.payload.payload && typeof m.payload.payload.x === 'string') { onRaw(m.payload.payload.x); return; }
      if (m.event === 'phx_error' || m.event === 'phx_close') { try { sock.close(); } catch (er) {} }
    };
    sock.onerror = () => {};
    sock.onclose = () => { clearTimeout(openTimer); if (ws !== sock) return; N.cloud = false; clearInterval(hbTimer); hbPending = null; setStatus(); sbSchedule(); };
  }
  function sbSchedule() {
    if (N.closed || sbReconnect) return;
    const d = Math.min(5000, 400 * Math.pow(2, sbRetry++)) + Math.random() * 300;
    sbReconnect = setTimeout(() => { sbReconnect = null; sbConnect(); }, d);
  }
  function wake() { // network came back, or the tab became visible again: reconnect now
    if (!N.role || N.closed || testMode) return;
    if (!ws || ws.readyState > 1 || !N.cloud) { sbRetry = 0; sbConnect(); }
    if (peer && peer.disconnected) { try { peer.reconnect(); } catch (e) {} }
    resendAll();
  }
  window.addEventListener('online', wake);
  document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'visible') wake(); });

  /* ---- RELAY: ntfy.sh (backup only) ---- */
  function startRelay() {
    if (testMode) { if (!bc) { bc = new BroadcastChannel('signal5-' + N.code); bc.onmessage = (e) => onRaw(e.data); N.relay = true; setStatus(); } return; }
    if (es) return;
    try {
      es = new EventSource(RELAY + topic() + '/sse?since=10m');
      es.onopen = () => { N.relay = true; setStatus(); };
      es.onmessage = (e) => { try { const d = JSON.parse(e.data); if (d.event === 'message' && d.message) onRaw(d.message); } catch (er) {} };
      es.onerror = () => { N.relay = false; setStatus(); };
    } catch (e) {}
  }

  /* ---- DIRECT: WebRTC via PeerJS (bonus fast path) ---- */
  function loadPeer() {
    if (window.Peer) return Promise.resolve(true);
    return new Promise(res => { const s = document.createElement('script'); s.src = PEER_CDN; s.onload = () => res(!!window.Peer); s.onerror = () => res(false); document.head.appendChild(s); setTimeout(() => res(!!window.Peer), 8000); });
  }
  const ICE = { iceServers: [{ urls: ['stun:stun.l.google.com:19302', 'stun:stun1.l.google.com:19302'] }, { urls: 'stun:stun.cloudflare.com:3478' }, { urls: 'stun:global.stun.twilio.com:3478' }] };
  function wireConn(c) {
    conn = c;
    c.on('open', () => { N.p2p = true; setStatus(); resendAll(); });
    c.on('data', (d) => onRaw(d));
    c.on('close', () => { if (conn === c) { N.p2p = false; setStatus(); } });
    c.on('error', () => { if (conn === c) { N.p2p = false; setStatus(); } });
  }
  async function startP2P() {
    if (testMode) return;
    if (!(await loadPeer())) return;
    try {
      if (N.role === 'h') {
        peer = new Peer(peerId('h'), { config: ICE, debug: 0 });
        peer.on('connection', (c) => wireConn(c));
      } else {
        peer = new Peer(undefined, { config: ICE, debug: 0 });
        const tryConnect = () => { if (N.p2p || N.closed) return; const c = peer.connect(peerId('h'), { reliable: true, serialization: 'raw' }); wireConn(c); };
        peer.on('open', () => { tryConnect(); setTimeout(tryConnect, 5000); setTimeout(tryConnect, 15000); });
      }
      peer.on('error', () => {});
      peer.on('disconnected', () => { try { peer.reconnect(); } catch (e) {} });
    } catch (e) {}
  }

  function start() {
    N.closed = false; N.t0 = Date.now();
    if (testMode) startRelay(); else { sbConnect(); setTimeout(() => { if (!N.cloud && !N.closed) startRelay(); }, 6000); startP2P(); }
    resendLoop(); setStatus();
  }
  N.host = () => { N.role = 'h'; N.code = newCode(); start(); return N.code; };
  N.join = (code) => { N.role = 'g'; N.code = code.toUpperCase().replace(/[^A-Z0-9]/g, ''); start(); return N.code; };
  N.close = () => {
    try { N.send('bye'); } catch (e) {}
    setTimeout(() => { N.closed = true; try { es && es.close(); } catch (e) {} try { conn && conn.close(); } catch (e) {} try { peer && peer.destroy(); } catch (e) {} try { bc && bc.close(); } catch (e) {}
      try { if (ws) { ws.onclose = null; ws.close(); } } catch (e) {} clearInterval(resendTimer); clearInterval(pingTimer); clearInterval(hbTimer); clearTimeout(sbReconnect); }, 500);
  };
  N.active = () => !!N.role && !N.closed;
  N.shareLink = () => location.origin + location.pathname + '?room=' + N.code + (testMode ? '&net=bc' : '');
  return N;
})();
