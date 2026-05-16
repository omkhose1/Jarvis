"""
views.py - API endpoints for Jarvis AI Assistant

Endpoints:
  POST /api/chat/     → Send message, get AI response
  GET  /api/history/  → Retrieve stored chat history
"""
import json
import datetime
import urllib.request
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings

from .models import ChatLog


# ─────────────────────────────────────────────
# 1. COMMAND PROCESSOR
#    Handles special commands without using AI
# ─────────────────────────────────────────────

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

def process_command(message: str):
    """
    Check if message matches a built-in command.
    Returns a dict with response + optional URL to open, or None if no match.
    """
    msg = message.lower().strip()

    # ── Time / Date commands ──────────────────
    if any(w in msg for w in ['what time', 'current time', 'tell me the time']):
        now = datetime.datetime.now()
        return {
            'response': f"The current time is {now.strftime('%I:%M %p')}.",
            'action': None
        }

    if any(w in msg for w in ['what date', 'today\'s date', "what's the date", 'current date']):
        today = datetime.date.today()
        return {
            'response': f"Today is {today.strftime('%A, %B %d, %Y')}.",
            'action': None
        }

    if 'day is it' in msg or 'what day' in msg:
        day = datetime.date.today().strftime('%A')
        return {
            'response': f"Today is {day}.",
            'action': None
        }

    # ── Website open commands ─────────────────
    for command, url in SITE_COMMANDS.items():
        if command in msg:
            site_name = command.replace('open ', '').capitalize()
            return {
                'response': f"Opening {site_name} for you!",
                'action': {'type': 'open_url', 'url': url}
            }

    # ── Search commands ───────────────────────
    if msg.startswith('search ') or msg.startswith('google '):
        query = msg.replace('search ', '').replace('google ', '').strip()
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        return {
            'response': f"Searching Google for: {query}",
            'action': {'type': 'open_url', 'url': url}
        }

    if msg.startswith('youtube ') or 'search youtube for' in msg:
        query = msg.replace('youtube ', '').replace('search youtube for', '').strip()
        url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        return {
            'response': f"Searching YouTube for: {query}",
            'action': {'type': 'open_url', 'url': url}
        }

    # ── Greeting shortcuts ────────────────────
    if msg in ['hi', 'hello', 'hey', 'hey jarvis', 'hello jarvis']:
        return {
            'response': "Hello! I'm Jarvis, your AI assistant. How can I help you today?",
            'action': None
        }

    return None   # No command matched — pass to AI


# ─────────────────────────────────────────────
# 2. AI RESPONSE via OpenAI
# ─────────────────────────────────────────────

def get_ai_response(message: str) -> str:
    """
    Send message to OpenAI ChatGPT and return the response text.
    Uses urllib (no extra dependencies) to call the API.
    """
    api_key = settings.OPENAI_API_KEY

    # If no real key, return a friendly fallback
    if not api_key or api_key == 'your-openai-api-key-here':
        return (
            "I'm Jarvis, your AI assistant! It looks like the OpenAI API key "
            "isn't configured yet. Please add your OPENAI_API_KEY to the settings. "
            "In the meantime, I can still handle commands like 'open YouTube', "
            "'what time is it', or 'search Google for [topic]'."
        )

    payload = json.dumps({
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are Jarvis, an advanced AI assistant. "
                    "Be helpful, concise, and slightly witty. "
                    "Keep responses under 150 words unless a longer answer is truly needed."
                )
            },
            {"role": "user", "content": message}
        ],
        "max_tokens": 300,
        "temperature": 0.7,
    }).encode('utf-8')

    req = urllib.request.Request(
        'https://api.openai.com/v1/chat/completions',
        data=payload,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}',
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return data['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"I encountered an issue connecting to my AI core: {str(e)}"


# ─────────────────────────────────────────────
# 3. API VIEWS
# ─────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def chat(request):
    """
    POST /api/chat/
    Body: { "message": "your text here", "session_id": "optional" }
    Returns: { "response": "...", "action": {...} or null, "timestamp": "..." }
    """
    # Handle CORS preflight
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

        # 1. Try built-in commands first (fast, no API call needed)
        command_result = process_command(message)

        if command_result:
            ai_response = command_result['response']
            action      = command_result.get('action')
        else:
            # 2. Fall back to OpenAI
            ai_response = get_ai_response(message)
            action      = None

        # 3. Save to database
        log = ChatLog.objects.create(
            user_message=message,
            ai_response=ai_response,
            session_id=session_id,
        )

        return JsonResponse({
            'response' : ai_response,
            'action'   : action,
            'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)


@require_http_methods(["GET"])
def history(request):
    """
    GET /api/history/?limit=20&session_id=default
    Returns last N chat messages from the database.
    """
    limit      = int(request.GET.get('limit', 20))
    session_id = request.GET.get('session_id', 'default')

    logs = ChatLog.objects.filter(session_id=session_id)[:limit]

    data = [
        {
            'user_message': log.user_message,
            'ai_response' : log.ai_response,
            'timestamp'   : log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        }
        for log in logs
    ]

    # Reverse so oldest message appears first in the chat
    return JsonResponse({'history': list(reversed(data))})
