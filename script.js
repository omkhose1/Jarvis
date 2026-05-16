/**
 * script.js — Jarvis AI Assistant Frontend Logic
 *
 * Features:
 *  - Send messages to Django /api/chat/
 *  - Display AI responses with TTS (text-to-speech)
 *  - Voice input via SpeechRecognition API
 *  - Load chat history from /api/history/
 *  - Execute actions (open URLs) returned by backend
 */

// ─────────────────────────────────────────────
// CONFIG
// ─────────────────────────────────────────────

const API_BASE   = 'http://127.0.0.1:8000/api';  // Django backend URL
const SESSION_ID = 'jarvis-session-' + (localStorage.getItem('jarvis_sid') || (() => {
  const id = Date.now().toString(36);
  localStorage.setItem('jarvis_sid', id);
  return id;
})());

// ─────────────────────────────────────────────
// DOM ELEMENTS
// ─────────────────────────────────────────────

const messagesEl    = document.getElementById('messages');
const inputEl       = document.getElementById('user-input');
const sendBtn       = document.getElementById('send-btn');
const micBtn        = document.getElementById('mic-btn');
const typingEl      = document.getElementById('typing');
const historyList   = document.getElementById('history-list');
const refreshBtn    = document.getElementById('refresh-history');
const clockEl       = document.getElementById('live-clock');
const voiceStatus   = document.getElementById('voice-status');

// ─────────────────────────────────────────────
// LIVE CLOCK
// ─────────────────────────────────────────────

function updateClock() {
  const now = new Date();
  const h   = String(now.getHours()).padStart(2, '0');
  const m   = String(now.getMinutes()).padStart(2, '0');
  const s   = String(now.getSeconds()).padStart(2, '0');
  if (clockEl) clockEl.textContent = `${h}:${m}:${s}`;
}
setInterval(updateClock, 1000);
updateClock();

// ─────────────────────────────────────────────
// SEND MESSAGE
// ─────────────────────────────────────────────

async function sendMessage(text) {
  text = text.trim();
  if (!text) return;

  // Add user bubble
  appendMessage(text, 'user');
  inputEl.value = '';

  // Show typing animation
  typingEl.style.display = 'flex';
  scrollBottom();

  try {
    const res = await fetch(`${API_BASE}/chat/`, {
      method : 'POST',
      headers: { 'Content-Type': 'application/json' },
      body   : JSON.stringify({ message: text, session_id: SESSION_ID }),
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    const data = await res.json();
    typingEl.style.display = 'none';

    // Show AI response
    appendMessage(data.response, 'ai', data.timestamp, data.action);

    // Speak the response
    speak(data.response);

    // Execute action (e.g. open URL)
    if (data.action) handleAction(data.action);

  } catch (err) {
    typingEl.style.display = 'none';
    appendMessage(
      `⚠️ Connection error: ${err.message}. Make sure Django server is running on port 8000.`,
      'ai'
    );
    console.error('Chat error:', err);
  }
}

// ─────────────────────────────────────────────
// APPEND MESSAGE BUBBLE
// ─────────────────────────────────────────────

function appendMessage(text, role, timestamp, action) {
  const isAI = role === 'ai';

  const row    = document.createElement('div');
  row.className = `msg ${isAI ? 'ai-msg' : 'user-msg'}`;

  const avatar = document.createElement('div');
  avatar.className = `msg-avatar ${isAI ? 'ai-avatar' : 'user-avatar'}`;
  avatar.textContent = isAI ? 'AI' : 'YOU';

  const bubble = document.createElement('div');
  bubble.className = 'msg-bubble';
  bubble.innerHTML = `<p>${escapeHtml(text)}</p>`;

  // If action is open URL, add a clickable link
  if (action && action.type === 'open_url') {
    const link = document.createElement('a');
    link.href      = action.url;
    link.target    = '_blank';
    link.className = 'url-notice';
    link.textContent = `🔗 Click to open → ${action.url}`;
    bubble.appendChild(link);
  }

  // Timestamp
  if (timestamp) {
    const t = document.createElement('div');
    t.className   = 'msg-time';
    t.textContent = timestamp;
    bubble.appendChild(t);
  }

  row.appendChild(avatar);
  row.appendChild(bubble);
  messagesEl.appendChild(row);
  scrollBottom();
}

function scrollBottom() {
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/\n/g, '<br>');
}

// ─────────────────────────────────────────────
// TEXT-TO-SPEECH
// ─────────────────────────────────────────────

function speak(text) {
  if (!window.speechSynthesis) return;

  // Cancel any ongoing speech
  window.speechSynthesis.cancel();

  const utterance       = new SpeechSynthesisUtterance(text);
  utterance.rate        = 1.0;
  utterance.pitch       = 0.9;
  utterance.volume      = 1.0;

  // Try to pick a nice voice
  const voices = window.speechSynthesis.getVoices();
  const preferred = voices.find(v =>
    v.name.includes('Google') || v.name.includes('Microsoft') || v.lang === 'en-US'
  );
  if (preferred) utterance.voice = preferred;

  window.speechSynthesis.speak(utterance);
}

// Voices load async in some browsers
window.speechSynthesis?.addEventListener('voiceschanged', () => {});

// ─────────────────────────────────────────────
// HANDLE BACKEND ACTIONS
// ─────────────────────────────────────────────

function handleAction(action) {
  if (action.type === 'open_url') {
    // Small delay so user sees the message first
    setTimeout(() => window.open(action.url, '_blank'), 800);
  }
}

// ─────────────────────────────────────────────
// VOICE INPUT (SpeechRecognition)
// ─────────────────────────────────────────────

let recognition     = null;
let isListening     = false;

// Check browser support
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

if (SpeechRecognition) {
  recognition              = new SpeechRecognition();
  recognition.lang         = 'en-US';
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  recognition.onstart = () => {
    isListening = true;
    micBtn.classList.add('listening');
    if (voiceStatus) { voiceStatus.textContent = 'LISTENING'; voiceStatus.className = 'green'; }
    inputEl.placeholder = '🎤 Listening...';
  };

  recognition.onend = () => {
    isListening = false;
    micBtn.classList.remove('listening');
    if (voiceStatus) { voiceStatus.textContent = 'READY'; voiceStatus.className = 'yellow'; }
    inputEl.placeholder = 'Speak your command, sir...';
  };

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    inputEl.value    = transcript;
    sendMessage(transcript);
  };

  recognition.onerror = (event) => {
    console.error('SpeechRecognition error:', event.error);
    if (voiceStatus) { voiceStatus.textContent = 'ERROR'; voiceStatus.className = 'red'; }
    setTimeout(() => {
      if (voiceStatus) { voiceStatus.textContent = 'READY'; voiceStatus.className = 'yellow'; }
    }, 2000);
  };

} else {
  // Browser doesn't support voice input
  micBtn.title   = 'Voice input not supported in this browser';
  micBtn.style.opacity = '0.4';
  micBtn.style.cursor  = 'not-allowed';
  if (voiceStatus) { voiceStatus.textContent = 'N/A'; voiceStatus.className = 'red'; }
}

micBtn.addEventListener('click', () => {
  if (!recognition) return;
  if (isListening) {
    recognition.stop();
  } else {
    recognition.start();
  }
});

// ─────────────────────────────────────────────
// EVENT LISTENERS
// ─────────────────────────────────────────────

// Send on button click
sendBtn.addEventListener('click', () => sendMessage(inputEl.value));

// Send on Enter key
inputEl.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage(inputEl.value);
  }
});

// ─────────────────────────────────────────────
// LOAD CHAT HISTORY
// ─────────────────────────────────────────────

async function loadHistory() {
  try {
    const res  = await fetch(`${API_BASE}/history/?session_id=${SESSION_ID}&limit=15`);
    const data = await res.json();

    historyList.innerHTML = '';

    if (!data.history || data.history.length === 0) {
      historyList.innerHTML = '<p class="empty-note">No conversation history yet.</p>';
      return;
    }

    // Show most recent first in side panel
    [...data.history].reverse().forEach(item => {
      const el = document.createElement('div');
      el.className = 'history-item';
      el.innerHTML = `
        <div class="h-user">▶ ${escapeHtml(item.user_message.slice(0, 60))}${item.user_message.length > 60 ? '…' : ''}</div>
        <div class="h-ai">${escapeHtml(item.ai_response.slice(0, 80))}${item.ai_response.length > 80 ? '…' : ''}</div>
        <div class="h-time">${item.timestamp}</div>
      `;
      // Click to re-ask
      el.addEventListener('click', () => {
        inputEl.value = item.user_message;
        inputEl.focus();
      });
      historyList.appendChild(el);
    });

  } catch (err) {
    historyList.innerHTML = '<p class="empty-note">Could not load history.</p>';
  }
}

// Load history on page load & when refresh button clicked
document.addEventListener('DOMContentLoaded', () => {
  loadHistory();
});
refreshBtn.addEventListener('click', loadHistory);
