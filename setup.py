"""
JARVIS AI Assistant - Auto Setup Script
Run this once to create the entire project structure!
Usage: python setup.py
"""
import os

BASE = os.path.dirname(os.path.abspath(__file__))

def write(path, content):
    full = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  ✅ Created: {path}")

print("\n🤖 Building JARVIS project...\n")

# ── requirements.txt ─────────────────────────
write("backend/requirements.txt", """Django>=4.2,<5.0
django-cors-headers>=4.0
""")

# ── manage.py ────────────────────────────────
write("backend/manage.py", """#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Couldn't import Django.") from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
""")

# ── backend/__init__.py ───────────────────────
write("backend/backend/__init__.py", "# backend package\n")

# ── backend/wsgi.py ───────────────────────────
write("backend/backend/wsgi.py", """import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
application = get_wsgi_application()
""")

# ── backend/urls.py ───────────────────────────
write("backend/backend/urls.py", """from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('assistant.urls')),
]
""")

# ── backend/settings.py ───────────────────────
write("backend/backend/settings.py", """import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-change-this-in-production'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'assistant',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ]},
}]

WSGI_APPLICATION = 'backend.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOW_ALL_ORIGINS = True

# Add your OpenAI API key here or set as environment variable
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', 'your-openai-api-key-here')
""")

# ── assistant/__init__.py ─────────────────────
write("backend/assistant/__init__.py", "# assistant package\n")

# ── assistant/models.py ───────────────────────
write("backend/assistant/models.py", """from django.db import models

class ChatLog(models.Model):
    user_message = models.TextField()
    ai_response  = models.TextField()
    timestamp    = models.DateTimeField(auto_now_add=True)
    session_id   = models.CharField(max_length=100, blank=True, default='default')

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.timestamp:%Y-%m-%d %H:%M}] {self.user_message[:50]}"
""")

# ── assistant/admin.py ────────────────────────
write("backend/assistant/admin.py", """from django.contrib import admin
from .models import ChatLog

@admin.register(ChatLog)
class ChatLogAdmin(admin.ModelAdmin):
    list_display   = ('timestamp', 'session_id', 'user_message', 'ai_response')
    list_filter    = ('session_id',)
    search_fields  = ('user_message', 'ai_response')
    readonly_fields = ('timestamp',)
""")

# ── assistant/urls.py ─────────────────────────
write("backend/assistant/urls.py", """from django.urls import path
from . import views

urlpatterns = [
    path('chat/',    views.chat,    name='chat'),
    path('history/', views.history, name='history'),
]
""")

# ── assistant/views.py ────────────────────────
write("backend/assistant/views.py", """import json
import datetime
import urllib.request
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from .models import ChatLog

SITE_COMMANDS = {
    'open youtube'  : 'https://youtube.com',
    'open google'   : 'https://google.com',
    'open github'   : 'https://github.com',
    'open gmail'    : 'https://mail.google.com',
    'open facebook' : 'https://facebook.com',
    'open twitter'  : 'https://twitter.com',
    'open instagram': 'https://instagram.com',
    'open reddit'   : 'https://reddit.com',
    'open netflix'  : 'https://netflix.com',
    'open spotify'  : 'https://spotify.com',
}

def process_command(message):
    msg = message.lower().strip()

    if any(w in msg for w in ['what time', 'current time', 'tell me the time']):
        now = datetime.datetime.now()
        return {'response': f"The current time is {now.strftime('%I:%M %p')}.", 'action': None}

    if any(w in msg for w in ['what date', "today's date", "what's the date", 'current date']):
        today = datetime.date.today()
        return {'response': f"Today is {today.strftime('%A, %B %d, %Y')}.", 'action': None}

    if 'day is it' in msg or 'what day' in msg:
        return {'response': f"Today is {datetime.date.today().strftime('%A')}.", 'action': None}

    for command, url in SITE_COMMANDS.items():
        if command in msg:
            site_name = command.replace('open ', '').capitalize()
            return {'response': f"Opening {site_name} for you!", 'action': {'type': 'open_url', 'url': url}}

    if msg.startswith('search ') or msg.startswith('google '):
        query = msg.replace('search ', '').replace('google ', '').strip()
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        return {'response': f"Searching Google for: {query}", 'action': {'type': 'open_url', 'url': url}}

    if msg.startswith('youtube ') or 'search youtube for' in msg:
        query = msg.replace('youtube ', '').replace('search youtube for', '').strip()
        url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        return {'response': f"Searching YouTube for: {query}", 'action': {'type': 'open_url', 'url': url}}

    if msg in ['hi', 'hello', 'hey', 'hey jarvis', 'hello jarvis']:
        return {'response': "Hello! I am Jarvis, your AI assistant. How can I help you today?", 'action': None}

    return None

def get_ai_response(message):
    api_key = settings.OPENAI_API_KEY
    if not api_key or api_key == 'your-openai-api-key-here':
        return (
            "I am Jarvis! The OpenAI API key is not configured yet. "
            "I can still handle commands like 'open YouTube', 'what time is it', "
            "or 'search Google for Python tutorials'."
        )
    payload = json.dumps({
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are Jarvis, an advanced AI assistant. Be helpful and concise."},
            {"role": "user", "content": message}
        ],
        "max_tokens": 300,
    }).encode('utf-8')

    req = urllib.request.Request(
        'https://api.openai.com/v1/chat/completions',
        data=payload,
        headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {api_key}'}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return data['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"I encountered an issue: {str(e)}"

@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def chat(request):
    if request.method == "OPTIONS":
        response = JsonResponse({})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"
        return response
    try:
        body       = json.loads(request.body)
        message    = body.get('message', '').strip()
        session_id = body.get('session_id', 'default')
        if not message:
            return JsonResponse({'error': 'Message cannot be empty.'}, status=400)

        result = process_command(message)
        if result:
            ai_response = result['response']
            action      = result.get('action')
        else:
            ai_response = get_ai_response(message)
            action      = None

        log = ChatLog.objects.create(user_message=message, ai_response=ai_response, session_id=session_id)
        return JsonResponse({'response': ai_response, 'action': action, 'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S')})
    except Exception as e:
        return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)

@require_http_methods(["GET"])
def history(request):
    limit      = int(request.GET.get('limit', 20))
    session_id = request.GET.get('session_id', 'default')
    logs = ChatLog.objects.filter(session_id=session_id)[:limit]
    data = [{'user_message': l.user_message, 'ai_response': l.ai_response, 'timestamp': l.timestamp.strftime('%Y-%m-%d %H:%M:%S')} for l in logs]
    return JsonResponse({'history': list(reversed(data))})
""")

# ── frontend/index.html ───────────────────────
write("frontend/index.html", """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>J.A.R.V.I.S - AI Assistant</title>
  <link rel="stylesheet" href="style.css" />
  <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;800&family=Rajdhani:wght@300;400;500&display=swap" rel="stylesheet">
</head>
<body>
  <div class="bg-grid"></div>
  <div class="jarvis-shell">
    <header class="hud-header">
      <div class="logo-block">
        <div class="arc-reactor">
          <div class="arc-ring r1"></div>
          <div class="arc-ring r2"></div>
          <div class="arc-core"></div>
        </div>
        <div class="logo-text">
          <span class="logo-main">J.A.R.V.I.S</span>
          <span class="logo-sub">Just A Rather Very Intelligent System</span>
        </div>
      </div>
      <div class="hud-stats">
        <div class="stat"><span class="stat-label">STATUS</span><span class="stat-value online">ONLINE</span></div>
        <div class="stat"><span class="stat-label">TIME</span><span class="stat-value" id="live-clock">--:--</span></div>
      </div>
    </header>
    <main class="main-layout">
      <section class="chat-panel">
        <div class="panel-title"><span class="dot"></span> COMMUNICATION FEED</div>
        <div class="messages" id="messages">
          <div class="msg ai-msg">
            <div class="msg-avatar ai-avatar">AI</div>
            <div class="msg-bubble">
              <p>Good day. I am <strong>Jarvis</strong>. How can I assist you?</p>
              <ul class="hint-list">
                <li>🕐 "What time is it?"</li>
                <li>🌐 "Open YouTube"</li>
                <li>🔍 "Search Google for Python"</li>
              </ul>
            </div>
          </div>
        </div>
        <div class="typing-indicator" id="typing" style="display:none;">
          <span></span><span></span><span></span>
          <em>Jarvis is processing...</em>
        </div>
        <div class="input-row">
          <button class="mic-btn" id="mic-btn" title="Voice Input">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
              <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
              <line x1="12" y1="19" x2="12" y2="23"/>
              <line x1="8" y1="23" x2="16" y2="23"/>
            </svg>
          </button>
          <input type="text" id="user-input" class="chat-input" placeholder="Speak your command, sir..." autocomplete="off"/>
          <button class="send-btn" id="send-btn">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <line x1="22" y1="2" x2="11" y2="13"/>
              <polygon points="22 2 15 22 11 13 2 9 22 2"/>
            </svg>
          </button>
        </div>
      </section>
      <aside class="side-panel">
        <div class="info-card">
          <div class="panel-title"><span class="dot"></span> SYSTEM STATUS</div>
          <div class="diag-grid">
            <div class="diag-item"><span>API</span><span class="green">ACTIVE</span></div>
            <div class="diag-item"><span>VOICE</span><span id="voice-status" class="yellow">READY</span></div>
            <div class="diag-item"><span>DB</span><span class="green">SQLITE</span></div>
            <div class="diag-item"><span>MODE</span><span class="cyan">JARVIS</span></div>
          </div>
        </div>
        <div class="info-card history-card">
          <div class="panel-title">
            <span class="dot"></span> MEMORY LOG
            <button class="refresh-btn" id="refresh-history">↻</button>
          </div>
          <div class="history-list" id="history-list">
            <p class="empty-note">No history yet.</p>
          </div>
        </div>
      </aside>
    </main>
  </div>
  <script src="script.js"></script>
</body>
</html>
""")

# ── frontend/style.css ────────────────────────
write("frontend/style.css", """:root {
  --bg: #020b14; --panel: #061a2e; --border: rgba(0,180,255,0.18);
  --accent: #00b4ff; --accent2: #0ff; --accent3: #00ffd5;
  --text: #c8e8ff; --text-dim: #4a7a99;
  --glow: 0 0 12px rgba(0,180,255,0.5);
  --green: #00ff99; --yellow: #ffd700; --cyan: #00ffd5; --red: #ff4060;
  --font-hud: 'Orbitron', sans-serif; --font-body: 'Rajdhani', sans-serif;
}
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body { height: 100%; background: var(--bg); color: var(--text); font-family: var(--font-body); font-size: 15px; }
.bg-grid { position: fixed; inset: 0; z-index: 0; background-image: linear-gradient(rgba(0,180,255,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(0,180,255,0.04) 1px, transparent 1px); background-size: 50px 50px; animation: grid-move 20s linear infinite; }
@keyframes grid-move { 0%{background-position:0 0} 100%{background-position:50px 50px} }
.jarvis-shell { position: relative; z-index: 1; display: flex; flex-direction: column; min-height: 100vh; max-width: 1400px; margin: 0 auto; padding: 16px; gap: 16px; }
.hud-header { display: flex; align-items: center; justify-content: space-between; padding: 14px 24px; background: linear-gradient(135deg, rgba(6,26,46,0.95), rgba(2,11,20,0.9)); border: 1px solid var(--border); border-radius: 8px; box-shadow: var(--glow); }
.logo-block { display: flex; align-items: center; gap: 16px; }
.arc-reactor { position: relative; width: 48px; height: 48px; display: flex; align-items: center; justify-content: center; }
.arc-ring { position: absolute; border-radius: 50%; border: 2px solid var(--accent); }
.r1 { width: 48px; height: 48px; opacity: 0.3; animation: spin 6s linear infinite; }
.r2 { width: 34px; height: 34px; opacity: 0.6; animation: spin 3s linear infinite reverse; border-color: var(--accent3); }
.arc-core { width: 16px; height: 16px; border-radius: 50%; background: radial-gradient(circle, #fff 0%, var(--accent) 50%, var(--accent2) 100%); box-shadow: 0 0 12px var(--accent), 0 0 30px var(--accent); animation: pulse-core 2s ease-in-out infinite; }
@keyframes spin { to{transform:rotate(360deg)} }
@keyframes pulse-core { 0%,100%{transform:scale(1)} 50%{transform:scale(1.15)} }
.logo-text { display: flex; flex-direction: column; }
.logo-main { font-family: var(--font-hud); font-size: 1.4rem; font-weight: 800; letter-spacing: 0.25em; color: var(--accent2); text-shadow: var(--glow); }
.logo-sub { font-size: 0.65rem; letter-spacing: 0.12em; color: var(--text-dim); text-transform: uppercase; }
.hud-stats { display: flex; gap: 24px; }
.stat { display: flex; flex-direction: column; align-items: center; gap: 2px; }
.stat-label { font-family: var(--font-hud); font-size: 0.5rem; letter-spacing: 0.15em; color: var(--text-dim); }
.stat-value { font-family: var(--font-hud); font-size: 0.75rem; color: var(--accent); }
.stat-value.online { color: var(--green); text-shadow: 0 0 8px var(--green); }
.main-layout { display: grid; grid-template-columns: 1fr 300px; gap: 16px; flex: 1; }
.chat-panel, .info-card { background: linear-gradient(160deg, rgba(6,26,46,0.9), rgba(2,11,20,0.95)); border: 1px solid var(--border); border-radius: 8px; }
.chat-panel { display: flex; flex-direction: column; }
.panel-title { display: flex; align-items: center; gap: 8px; font-family: var(--font-hud); font-size: 0.6rem; letter-spacing: 0.2em; color: var(--accent); padding: 10px 16px; border-bottom: 1px solid var(--border); text-transform: uppercase; }
.dot { width: 6px; height: 6px; border-radius: 50%; background: var(--accent); box-shadow: 0 0 8px var(--accent); animation: blink 2s ease-in-out infinite; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }
.messages { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 14px; max-height: calc(100vh - 260px); }
.messages::-webkit-scrollbar { width: 4px; }
.messages::-webkit-scrollbar-thumb { background: var(--accent); border-radius: 2px; }
.msg { display: flex; gap: 10px; align-items: flex-start; animation: msg-in 0.3s ease; }
@keyframes msg-in { from{opacity:0;transform:translateY(10px)} to{opacity:1;transform:translateY(0)} }
.user-msg { flex-direction: row-reverse; }
.msg-avatar { width: 34px; height: 34px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-family: var(--font-hud); font-size: 0.55rem; font-weight: 700; flex-shrink: 0; }
.ai-avatar { background: linear-gradient(135deg,#001a33,#003366); border: 1px solid var(--accent); color: var(--accent); }
.user-avatar { background: linear-gradient(135deg,#001a1a,#003322); border: 1px solid var(--accent3); color: var(--accent3); }
.msg-bubble { max-width: 78%; padding: 12px 16px; border-radius: 12px; font-size: 0.92rem; line-height: 1.55; }
.ai-msg .msg-bubble { background: rgba(0,40,80,0.6); border: 1px solid rgba(0,180,255,0.2); border-top-left-radius: 3px; }
.user-msg .msg-bubble { background: rgba(0,60,50,0.5); border: 1px solid rgba(0,255,213,0.2); border-top-right-radius: 3px; color: #b0ffe8; }
.hint-list { margin: 8px 0 0 16px; opacity: 0.75; font-size: 0.85rem; }
.url-notice { display: inline-block; margin-top: 8px; padding: 4px 10px; background: rgba(0,180,255,0.1); border: 1px solid rgba(0,180,255,0.3); border-radius: 4px; font-size: 0.75rem; color: var(--accent); cursor: pointer; text-decoration: none; }
.typing-indicator { display: flex; align-items: center; gap: 6px; padding: 8px 20px; font-size: 0.75rem; color: var(--text-dim); }
.typing-indicator span { width: 6px; height: 6px; border-radius: 50%; background: var(--accent); display: inline-block; animation: bounce 1.2s ease-in-out infinite; }
.typing-indicator span:nth-child(2){animation-delay:0.2s} .typing-indicator span:nth-child(3){animation-delay:0.4s}
@keyframes bounce { 0%,80%,100%{transform:translateY(0)} 40%{transform:translateY(-6px)} }
.input-row { display: flex; gap: 10px; align-items: center; padding: 12px 16px; border-top: 1px solid var(--border); }
.chat-input { flex: 1; background: rgba(0,20,40,0.7); border: 1px solid var(--border); border-radius: 6px; color: var(--text); font-family: var(--font-body); font-size: 0.95rem; padding: 10px 16px; outline: none; transition: border-color 0.2s, box-shadow 0.2s; }
.chat-input::placeholder { color: var(--text-dim); }
.chat-input:focus { border-color: var(--accent); box-shadow: 0 0 10px rgba(0,180,255,0.25); }
.send-btn, .mic-btn { width: 42px; height: 42px; border-radius: 8px; border: 1px solid var(--border); background: rgba(0,20,40,0.7); color: var(--accent); cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s; }
.send-btn:hover, .mic-btn:hover { background: rgba(0,180,255,0.15); box-shadow: var(--glow); border-color: var(--accent); }
.send-btn svg, .mic-btn svg { width: 18px; height: 18px; }
.mic-btn.listening { background: rgba(255,64,96,0.2); border-color: var(--red); color: var(--red); animation: mic-pulse 1s ease-in-out infinite; }
@keyframes mic-pulse { 0%,100%{transform:scale(1)} 50%{transform:scale(1.08)} }
.side-panel { display: flex; flex-direction: column; gap: 14px; }
.info-card { padding-bottom: 14px; }
.diag-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; padding: 12px 16px; }
.diag-item { display: flex; justify-content: space-between; align-items: center; font-size: 0.72rem; padding: 6px 10px; background: rgba(0,20,40,0.5); border: 1px solid var(--border); border-radius: 4px; font-family: var(--font-hud); }
.diag-item span:first-child { color: var(--text-dim); }
.green{color:var(--green);text-shadow:0 0 6px var(--green)} .yellow{color:var(--yellow)} .cyan{color:var(--cyan)}
.history-card { flex: 1; display: flex; flex-direction: column; }
.refresh-btn { margin-left: auto; background: none; border: none; color: var(--accent); cursor: pointer; font-size: 1rem; transition: transform 0.3s; }
.refresh-btn:hover { transform: rotate(180deg); }
.history-list { flex: 1; overflow-y: auto; padding: 10px 12px; display: flex; flex-direction: column; gap: 8px; max-height: 320px; }
.history-item { padding: 8px 10px; background: rgba(0,20,40,0.5); border: 1px solid var(--border); border-radius: 5px; font-size: 0.75rem; cursor: pointer; transition: border-color 0.2s; }
.history-item:hover { border-color: var(--accent); }
.history-item .h-user { color: var(--accent3); margin-bottom: 3px; }
.history-item .h-ai { color: var(--text-dim); font-size: 0.68rem; }
.history-item .h-time { color: var(--text-dim); font-size: 0.6rem; margin-top: 4px; }
.empty-note { color: var(--text-dim); font-size: 0.78rem; padding: 8px; text-align: center; }
@media (max-width: 900px) { .main-layout{grid-template-columns:1fr} .side-panel{display:none} .hud-stats{display:none} }
""")

# ── frontend/script.js ────────────────────────
write("frontend/script.js", """const API_BASE   = 'http://127.0.0.1:8000/api';
const SESSION_ID = 'jarvis-' + (localStorage.getItem('jarvis_sid') || (() => { const id = Date.now().toString(36); localStorage.setItem('jarvis_sid', id); return id; })());

const messagesEl  = document.getElementById('messages');
const inputEl     = document.getElementById('user-input');
const sendBtn     = document.getElementById('send-btn');
const micBtn      = document.getElementById('mic-btn');
const typingEl    = document.getElementById('typing');
const historyList = document.getElementById('history-list');
const refreshBtn  = document.getElementById('refresh-history');
const clockEl     = document.getElementById('live-clock');
const voiceStatus = document.getElementById('voice-status');

function updateClock() {
  const now = new Date();
  if (clockEl) clockEl.textContent = [now.getHours(), now.getMinutes(), now.getSeconds()].map(n => String(n).padStart(2,'0')).join(':');
}
setInterval(updateClock, 1000); updateClock();

async function sendMessage(text) {
  text = text.trim(); if (!text) return;
  appendMessage(text, 'user'); inputEl.value = '';
  typingEl.style.display = 'flex'; scrollBottom();
  try {
    const res  = await fetch(`${API_BASE}/chat/`, { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({message: text, session_id: SESSION_ID}) });
    const data = await res.json();
    typingEl.style.display = 'none';
    appendMessage(data.response, 'ai', data.timestamp, data.action);
    speak(data.response);
    if (data.action) handleAction(data.action);
  } catch (err) {
    typingEl.style.display = 'none';
    appendMessage('Connection error. Make sure Django is running on port 8000.', 'ai');
  }
}

function appendMessage(text, role, timestamp, action) {
  const isAI = role === 'ai';
  const row = document.createElement('div'); row.className = `msg ${isAI ? 'ai-msg' : 'user-msg'}`;
  const avatar = document.createElement('div'); avatar.className = `msg-avatar ${isAI ? 'ai-avatar' : 'user-avatar'}`; avatar.textContent = isAI ? 'AI' : 'YOU';
  const bubble = document.createElement('div'); bubble.className = 'msg-bubble';
  bubble.innerHTML = `<p>${text.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\\n/g,'<br>')}</p>`;
  if (action && action.type === 'open_url') {
    const link = document.createElement('a'); link.href = action.url; link.target = '_blank'; link.className = 'url-notice'; link.textContent = `Click to open: ${action.url}`; bubble.appendChild(link);
  }
  if (timestamp) { const t = document.createElement('div'); t.className = 'msg-time'; t.textContent = timestamp; bubble.appendChild(t); }
  row.appendChild(avatar); row.appendChild(bubble); messagesEl.appendChild(row); scrollBottom();
}

function scrollBottom() { messagesEl.scrollTop = messagesEl.scrollHeight; }
function speak(text) {
  if (!window.speechSynthesis) return;
  window.speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text); u.rate = 1.0; u.pitch = 0.9;
  const voices = window.speechSynthesis.getVoices();
  const v = voices.find(v => v.name.includes('Google') || v.lang === 'en-US');
  if (v) u.voice = v;
  window.speechSynthesis.speak(u);
}
function handleAction(action) { if (action.type === 'open_url') setTimeout(() => window.open(action.url, '_blank'), 800); }

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition = null, isListening = false;
if (SpeechRecognition) {
  recognition = new SpeechRecognition(); recognition.lang = 'en-US'; recognition.interimResults = false;
  recognition.onstart = () => { isListening = true; micBtn.classList.add('listening'); if(voiceStatus){voiceStatus.textContent='LISTENING';voiceStatus.className='green';} inputEl.placeholder='Listening...'; };
  recognition.onend   = () => { isListening = false; micBtn.classList.remove('listening'); if(voiceStatus){voiceStatus.textContent='READY';voiceStatus.className='yellow';} inputEl.placeholder='Speak your command, sir...'; };
  recognition.onresult = (e) => { const t = e.results[0][0].transcript; inputEl.value = t; sendMessage(t); };
  recognition.onerror  = () => { if(voiceStatus){voiceStatus.textContent='ERROR';voiceStatus.className='';} };
} else { micBtn.style.opacity='0.4'; micBtn.style.cursor='not-allowed'; if(voiceStatus){voiceStatus.textContent='N/A';} }

micBtn.addEventListener('click', () => { if (!recognition) return; isListening ? recognition.stop() : recognition.start(); });
sendBtn.addEventListener('click', () => sendMessage(inputEl.value));
inputEl.addEventListener('keydown', (e) => { if (e.key === 'Enter') { e.preventDefault(); sendMessage(inputEl.value); } });

async function loadHistory() {
  try {
    const res = await fetch(`${API_BASE}/history/?session_id=${SESSION_ID}&limit=15`);
    const data = await res.json();
    historyList.innerHTML = '';
    if (!data.history || !data.history.length) { historyList.innerHTML = '<p class="empty-note">No history yet.</p>'; return; }
    [...data.history].reverse().forEach(item => {
      const el = document.createElement('div'); el.className = 'history-item';
      el.innerHTML = `<div class="h-user">${item.user_message.slice(0,60)}</div><div class="h-ai">${item.ai_response.slice(0,80)}</div><div class="h-time">${item.timestamp}</div>`;
      el.addEventListener('click', () => { inputEl.value = item.user_message; inputEl.focus(); });
      historyList.appendChild(el);
    });
  } catch { historyList.innerHTML = '<p class="empty-note">Could not load history.</p>'; }
}

document.addEventListener('DOMContentLoaded', loadHistory);
refreshBtn.addEventListener('click', loadHistory);
""")

print("\n✅ JARVIS project created successfully!\n")
print("📋 Next steps:")
print("  1. cd backend")
print("  2. pip install -r requirements.txt")
print("  3. python manage.py migrate")
print("  4. python manage.py runserver")
print("  5. Open frontend/index.html in Chrome")
print("\n🚀 Jarvis is ready!\n")
