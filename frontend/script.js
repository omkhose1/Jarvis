/* J.A.R.V.I.S — script.js
   Features: Chat, Voice, TTS, Sound FX, Dark/Light Mode, History
*/

const API_BASE   = 'http://127.0.0.1:8000/api';
const SESSION_ID = 'jarvis-' + (localStorage.getItem('jarvis_sid') || (() => {
  const id = Date.now().toString(36);
  localStorage.setItem('jarvis_sid', id);
  return id;
})());

const messagesEl  = document.getElementById('messages');
const inputEl     = document.getElementById('user-input');
const sendBtn     = document.getElementById('send-btn');
const micBtn      = document.getElementById('mic-btn');
const typingEl    = document.getElementById('typing');
const historyList = document.getElementById('history-list');
const refreshBtn  = document.getElementById('refresh-history');
const clockEl     = document.getElementById('live-clock');
const voiceStatus = document.getElementById('voice-status');
const themeToggle = document.getElementById('theme-toggle');
const themeIcon   = document.getElementById('theme-icon');

// ── THEME ────────────────────────────────
let isDark = localStorage.getItem('jarvis-theme') !== 'light';

function applyTheme() {
  document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
  themeIcon.textContent = isDark ? '☀️' : '🌙';
  localStorage.setItem('jarvis-theme', isDark ? 'dark' : 'light');
}
applyTheme();

themeToggle.addEventListener('click', () => {
  isDark = !isDark;
  applyTheme();
  playBeep(isDark ? 600 : 800);
});

// ── CLOCK ────────────────────────────────
function updateClock() {
  const now = new Date();
  const h = String(now.getHours()).padStart(2,'0');
  const m = String(now.getMinutes()).padStart(2,'0');
  const s = String(now.getSeconds()).padStart(2,'0');
  if (clockEl) clockEl.textContent = h + ':' + m + ':' + s;
}
setInterval(updateClock, 1000);
updateClock();

// ── AUDIO CONTEXT ────────────────────────
let audioCtx = null;
function getAudioCtx() {
  if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  return audioCtx;
}

function playTone(freq, type, start, duration, gain) {
  const ac = getAudioCtx();
  const o  = ac.createOscillator();
  const g  = ac.createGain();
  o.connect(g); g.connect(ac.destination);
  o.type = type || 'sine';
  o.frequency.value = freq;
  g.gain.setValueAtTime(0, ac.currentTime + start);
  g.gain.linearRampToValueAtTime(gain || 0.2, ac.currentTime + start + 0.02);
  g.gain.linearRampToValueAtTime(0, ac.currentTime + start + duration);
  o.start(ac.currentTime + start);
  o.stop(ac.currentTime + start + duration + 0.05);
}

function playBeep(freq) { playTone(freq || 880, 'sine', 0, 0.1, 0.15); }

// ── SOUND FX ─────────────────────────────
function playSound(type) {
  activateWave();
  animateMouth(2000);

  const setStatus = (t) => { const el = document.querySelector('.sub-tag'); if(el) el.textContent = t; };

  const sounds = {
    boot: () => {
      [200,300,400,600,800,1000].forEach((f,i) => playTone(f,'sine',i*0.12,0.22,0.25));
      playTone(1200,'sine',0.8,0.5,0.18);
      speak('All systems online. Jarvis ready, Sir.');
    },
    hello: () => {
      [440,550,660].forEach((f,i) => playTone(f,'sine',i*0.12,0.15,0.2));
      speak('Good day Sir. I am Jarvis, your personal AI assistant. How may I help you today?');
    },
    alert: () => {
      for(let i=0;i<6;i++) { playTone(880,'square',i*0.15,0.1,0.15); playTone(440,'square',i*0.15+0.1,0.05,0.1); }
      speak('Warning! Anomaly detected. Running diagnostics, Sir.');
    },
    scan: () => {
      for(let i=0;i<20;i++) playTone(200+i*40,'sine',i*0.06,0.08,0.1);
      speak('Scanning environment. All clear, Sir.');
    },
    ready: () => {
      [880,1100,1320].forEach((f,i) => playTone(f,'sine',i*0.07,0.12,0.18));
      speak('All systems ready, Sir. Awaiting your command.');
    },
    beep: () => {
      playTone(1000,'sine',0,0.05,0.25);
      playTone(1000,'sine',0.1,0.05,0.25);
      playTone(1500,'sine',0.2,0.1,0.18);
      speak('Signal received and acknowledged, Sir.');
    },
  };

  if (sounds[type]) sounds[type]();
}

// ── WAVEFORM ─────────────────────────────
function activateWave() {
  document.querySelectorAll('.w-bar').forEach((b,i) => {
    setTimeout(() => b.classList.add('active'), i * 30);
  });
  setTimeout(() => document.querySelectorAll('.w-bar').forEach(b => b.classList.remove('active')), 2500);
}

// ── MOUTH ANIMATION ──────────────────────
function animateMouth(duration) {
  const mouth = document.getElementById('jarvis-mouth');
  if (!mouth) return;
  let t = 0;
  const iv = setInterval(() => {
    const open = Math.sin(t * 7) * 7 + 82;
    mouth.setAttribute('d', `M 30 78 Q 60 ${open} 90 78`);
    t += 0.12;
  }, 60);
  setTimeout(() => {
    clearInterval(iv);
    mouth.setAttribute('d', 'M 30 78 Q 60 82 90 78');
  }, duration);
}

// ── FACE BARS ANIMATION ──────────────────
setInterval(() => {
  const v1 = 55 + Math.floor(Math.random() * 40);
  const v2 = 65 + Math.floor(Math.random() * 30);
  const v3 = 45 + Math.floor(Math.random() * 45);
  const b1 = document.getElementById('fb1'); if(b1) b1.style.width = v1+'%';
  const b2 = document.getElementById('fb2'); if(b2) b2.style.width = v2+'%';
  const b3 = document.getElementById('fb3'); if(b3) b3.style.width = v3+'%';
  const fv1 = document.getElementById('fv1'); if(fv1) fv1.textContent = v1+'%';
  const fv2 = document.getElementById('fv2'); if(fv2) fv2.textContent = v2+'%';
  const fv3 = document.getElementById('fv3'); if(fv3) fv3.textContent = v3+'%';
}, 2500);

// ── TEXT-TO-SPEECH ───────────────────────
function speak(text) {
  if (!window.speechSynthesis) return;
  window.speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text);
  u.rate = 0.95; u.pitch = 0.85; u.volume = 1;
  const voices = window.speechSynthesis.getVoices();
  const v = voices.find(v => v.name.includes('Google') || v.lang === 'en-US');
  if (v) u.voice = v;
  u.onstart = () => {
    activateWave();
    animateMouth(text.length * 60);
    if (voiceStatus) { voiceStatus.textContent = 'SPEAKING'; voiceStatus.className = 'cyan'; }
  };
  u.onend = () => {
    if (voiceStatus) { voiceStatus.textContent = 'READY'; voiceStatus.className = 'yellow'; }
  };
  window.speechSynthesis.speak(u);
}
window.speechSynthesis?.addEventListener('voiceschanged', () => {});

// ── SEND MESSAGE ─────────────────────────
async function sendMessage(text) {
  text = text.trim();
  if (!text) return;
  appendMessage(text, 'user');
  inputEl.value = '';
  typingEl.style.display = 'flex';
  scrollBottom();
  playBeep(440);

  try {
    const res  = await fetch(API_BASE + '/chat/', {
      method : 'POST',
      headers: { 'Content-Type': 'application/json' },
      body   : JSON.stringify({ message: text, session_id: SESSION_ID }),
    });
    const data = await res.json();
    typingEl.style.display = 'none';
    appendMessage(data.response, 'ai', data.timestamp, data.action);
    speak(data.response);
    if (data.action) handleAction(data.action);
    playBeep(660);
  } catch (err) {
    typingEl.style.display = 'none';
    appendMessage('Connection error. Make sure Django is running on port 8000.', 'ai');
    playTone(220, 'sawtooth', 0, 0.3, 0.15);
  }
}

// ── APPEND MESSAGE ───────────────────────
function appendMessage(text, role, timestamp, action) {
  const isAI = role === 'ai';
  const row  = document.createElement('div');
  row.className = 'msg ' + (isAI ? 'ai-msg' : 'user-msg');

  const avatar = document.createElement('div');
  avatar.className = 'msg-avatar ' + (isAI ? 'ai-avatar' : 'user-avatar');
  avatar.textContent = isAI ? 'AI' : 'YOU';

  const bubble = document.createElement('div');
  bubble.className = 'msg-bubble';
  bubble.innerHTML = '<p>' + text.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\n/g,'<br>') + '</p>';

  if (action && action.type === 'open_url') {
    const link = document.createElement('a');
    link.href = action.url; link.target = '_blank';
    link.className = 'url-notice';
    link.textContent = 'Click to open: ' + action.url;
    bubble.appendChild(link);
  }

  if (timestamp) {
    const t = document.createElement('div');
    t.className = 'msg-time'; t.textContent = timestamp;
    bubble.appendChild(t);
  }

  row.appendChild(avatar);
  row.appendChild(bubble);
  messagesEl.appendChild(row);
  scrollBottom();
}

function scrollBottom() { messagesEl.scrollTop = messagesEl.scrollHeight; }

function handleAction(action) {
  if (action.type === 'open_url') setTimeout(() => window.open(action.url, '_blank'), 600);
}

// ── VOICE INPUT ──────────────────────────
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition = null, isListening = false;

if (SpeechRecognition) {
  recognition = new SpeechRecognition();
  recognition.lang = 'en-US';
  recognition.interimResults = false;
  recognition.onstart = () => {
    isListening = true;
    micBtn.classList.add('listening');
    if (voiceStatus) { voiceStatus.textContent = 'LISTENING'; voiceStatus.className = 'green'; }
    inputEl.placeholder = 'Listening...';
    playBeep(550);
  };
  recognition.onend = () => {
    isListening = false;
    micBtn.classList.remove('listening');
    if (voiceStatus) { voiceStatus.textContent = 'READY'; voiceStatus.className = 'yellow'; }
    inputEl.placeholder = 'Speak your command, sir...';
  };
  recognition.onresult = (e) => {
    const t = e.results[0][0].transcript;
    inputEl.value = t;
    sendMessage(t);
  };
  recognition.onerror = () => {
    if (voiceStatus) { voiceStatus.textContent = 'ERROR'; voiceStatus.className = ''; }
    setTimeout(() => { if(voiceStatus) { voiceStatus.textContent='READY'; voiceStatus.className='yellow'; } }, 2000);
  };
} else {
  micBtn.style.opacity = '0.4';
  micBtn.style.cursor  = 'not-allowed';
  if (voiceStatus) voiceStatus.textContent = 'N/A';
}

micBtn.addEventListener('click', () => {
  if (!recognition) return;
  isListening ? recognition.stop() : recognition.start();
});

// ── EVENTS ───────────────────────────────
sendBtn.addEventListener('click', () => sendMessage(inputEl.value));
inputEl.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') { e.preventDefault(); sendMessage(inputEl.value); }
});

// ── HISTORY ──────────────────────────────
async function loadHistory() {
  try {
    const res  = await fetch(API_BASE + '/history/?session_id=' + SESSION_ID + '&limit=15');
    const data = await res.json();
    historyList.innerHTML = '';
    if (!data.history || !data.history.length) {
      historyList.innerHTML = '<p class="empty-note">No history yet.</p>';
      return;
    }
    [...data.history].reverse().forEach(item => {
      const el = document.createElement('div');
      el.className = 'history-item';
      el.innerHTML =
        '<div class="h-user">' + item.user_message.slice(0,55) + (item.user_message.length>55?'…':'') + '</div>' +
        '<div class="h-ai">'  + item.ai_response.slice(0,70)  + (item.ai_response.length>70?'…':'')  + '</div>' +
        '<div class="h-time">' + item.timestamp + '</div>';
      el.addEventListener('click', () => { inputEl.value = item.user_message; inputEl.focus(); });
      historyList.appendChild(el);
    });
  } catch {
    historyList.innerHTML = '<p class="empty-note">Could not load history.</p>';
  }
}

document.addEventListener('DOMContentLoaded', loadHistory);
refreshBtn.addEventListener('click', loadHistory);
