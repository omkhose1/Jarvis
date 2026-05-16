"""
Run this script to update views.py automatically!
Usage: python update_views.py
"""
import os

views_content = r'''import json
import datetime
import random
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import ChatLog

SITE_COMMANDS = {
    "open youtube": "https://youtube.com",
    "open google": "https://google.com",
    "open github": "https://github.com",
    "open gmail": "https://mail.google.com",
    "open facebook": "https://facebook.com",
    "open twitter": "https://twitter.com",
    "open instagram": "https://instagram.com",
    "open whatsapp": "https://web.whatsapp.com",
    "open netflix": "https://netflix.com",
    "open spotify": "https://spotify.com",
    "open amazon": "https://amazon.in",
    "open flipkart": "https://flipkart.com",
    "open maps": "https://maps.google.com",
    "open linkedin": "https://linkedin.com",
    "open telegram": "https://web.telegram.org",
    "open swiggy": "https://swiggy.com",
    "open zomato": "https://zomato.com",
    "open irctc": "https://irctc.co.in",
    "open chatgpt": "https://chat.openai.com",
    "open wikipedia": "https://wikipedia.org",
    "open reddit": "https://reddit.com",
    "open pinterest": "https://pinterest.com",
    "open zoom": "https://zoom.us",
}

JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs!",
    "Why did the computer go to the doctor? It had a virus!",
    "What do you call a computer that sings? A Dell!",
    "Why was the math book sad? It had too many problems!",
    "I told my computer I needed a break. Now it won't stop sending me Kit-Kat ads!",
]

FACTS = [
    "The first computer bug was an actual moth found in Harvard Mark II in 1947!",
    "Google processes over 8.5 billion searches per day!",
    "India has the second largest number of internet users in the world!",
    "The first website ever created is still online at info.cern.ch!",
    "WhatsApp has over 2 billion users worldwide!",
]

MOTIVATIONS = [
    "Believe you can and you are halfway there!",
    "Every expert was once a beginner. Keep going!",
    "Dream big, work hard, stay focused!",
    "You are capable of amazing things!",
    "Your only limit is your mind!",
]

def process_command(message):
    msg = message.lower().strip()

    # Greetings
    if any(w in msg for w in ["hi", "hello", "hey"]) and len(msg) < 20:
        return {"response": "Hello Sir! I am Jarvis. How may I help you today?", "action": None}
    if "how are you" in msg:
        return {"response": "Running at optimal efficiency Sir! All systems online.", "action": None}
    if "your name" in msg or "who are you" in msg:
        return {"response": "I am Jarvis, Just A Rather Very Intelligent System!", "action": None}
    if "thank" in msg:
        return {"response": "You are welcome Sir! Always at your service.", "action": None}
    if "bye" in msg or "goodbye" in msg:
        return {"response": "Goodbye Sir! Jarvis signing off!", "action": None}
    if "good morning" in msg:
        return {"response": "Good Morning Sir! Have a fantastic day!", "action": None}
    if "good night" in msg:
        return {"response": "Good Night Sir! Sweet dreams!", "action": None}
    if "good afternoon" in msg:
        return {"response": "Good Afternoon Sir! Hope your day is going well!", "action": None}

    # Time and Date
    if any(w in msg for w in ["what time", "time now", "time is it"]):
        now = datetime.datetime.now()
        return {"response": "The current time is " + now.strftime("%I:%M %p") + ", Sir.", "action": None}
    if any(w in msg for w in ["what date", "todays date", "date today", "date is it"]):
        today = datetime.date.today()
        return {"response": "Today is " + today.strftime("%A, %B %d, %Y") + ", Sir.", "action": None}
    if "what day" in msg or "day is it" in msg:
        return {"response": "Today is " + datetime.date.today().strftime("%A") + ", Sir.", "action": None}
    if "what year" in msg:
        return {"response": "The current year is " + str(datetime.date.today().year) + ", Sir.", "action": None}
    if "what month" in msg:
        return {"response": "The current month is " + datetime.date.today().strftime("%B") + ", Sir.", "action": None}

    # Open websites
    for command, url in SITE_COMMANDS.items():
        if command in msg:
            site_name = command.replace("open ", "").capitalize()
            return {"response": "Opening " + site_name + " for you Sir!", "action": {"type": "open_url", "url": url}}

    # Search
    if msg.startswith("search ") or msg.startswith("google "):
        query = msg.replace("search ", "").replace("google ", "").strip()
        url = "https://www.google.com/search?q=" + query.replace(" ", "+")
        return {"response": "Searching Google for: " + query, "action": {"type": "open_url", "url": url}}

    if msg.startswith("youtube ") or "search youtube" in msg:
        query = msg.replace("youtube ", "").replace("search youtube for", "").replace("search youtube", "").strip()
        url = "https://www.youtube.com/results?search_query=" + query.replace(" ", "+")
        return {"response": "Searching YouTube for: " + query + " Sir!", "action": {"type": "open_url", "url": url}}

    # Weather
    if "weather" in msg:
        city = msg.replace("weather in", "").replace("weather of", "").replace("weather for", "").replace("weather", "").strip()
        if not city:
            city = "my location"
        url = "https://www.google.com/search?q=weather+in+" + city.replace(" ", "+")
        return {"response": "Checking weather for " + city.title() + "!", "action": {"type": "open_url", "url": url}}

    # Cricket and IPL
    if "cricket" in msg or "ipl" in msg or "ipl score" in msg:
        return {"response": "Opening live cricket scores Sir! Go India!", "action": {"type": "open_url", "url": "https://www.google.com/search?q=live+cricket+score+today"}}

    if "cricket schedule" in msg or "cricket match" in msg:
        return {"response": "Opening cricket schedule Sir!", "action": {"type": "open_url", "url": "https://www.google.com/search?q=cricket+match+schedule+today"}}

    # News
    if "news" in msg:
        if "cricket" in msg or "sports" in msg:
            return {"response": "Opening sports news Sir!", "action": {"type": "open_url", "url": "https://www.google.com/search?q=cricket+news+today"}}
        if "india" in msg:
            return {"response": "Opening India news Sir!", "action": {"type": "open_url", "url": "https://news.google.com/topstories?hl=en-IN"}}
        return {"response": "Opening Google News Sir!", "action": {"type": "open_url", "url": "https://news.google.com"}}

    # Calculator
    if "calculator" in msg or "calculate" in msg:
        return {"response": "Opening calculator Sir!", "action": {"type": "open_url", "url": "https://www.google.com/search?q=calculator"}}

    # Movies
    if "movie" in msg or "bollywood" in msg or "film" in msg:
        if "hindi" in msg or "bollywood" in msg:
            return {"response": "Opening Bollywood movies!", "action": {"type": "open_url", "url": "https://www.google.com/search?q=latest+bollywood+movies+2026"}}
        return {"response": "Opening latest movies!", "action": {"type": "open_url", "url": "https://www.google.com/search?q=latest+movies+2026"}}

    # Music
    if "song" in msg or "music" in msg or "play" in msg:
        query = msg.replace("play", "").replace("song", "").replace("music", "").strip()
        if not query:
            query = "top hindi songs 2026"
        url = "https://www.youtube.com/results?search_query=" + query.replace(" ", "+")
        return {"response": "Playing music for you Sir!", "action": {"type": "open_url", "url": url}}

    # Food
    if "food" in msg or "hungry" in msg or "eat" in msg or "order food" in msg:
        return {"response": "Opening Swiggy to order food Sir!", "action": {"type": "open_url", "url": "https://swiggy.com"}}

    if "pizza" in msg:
        return {"response": "Searching for pizza near you!", "action": {"type": "open_url", "url": "https://www.google.com/search?q=pizza+near+me"}}

    # Travel
    if "train" in msg or "railway" in msg:
        return {"response": "Opening IRCTC for train booking Sir!", "action": {"type": "open_url", "url": "https://irctc.co.in"}}

    if "flight" in msg or "airline" in msg:
        return {"response": "Searching flights for you Sir!", "action": {"type": "open_url", "url": "https://www.google.com/travel/flights"}}

    if "hotel" in msg:
        return {"response": "Searching hotels for you Sir!", "action": {"type": "open_url", "url": "https://www.google.com/travel/hotels"}}

    # Health
    if "hospital" in msg or "doctor" in msg:
        return {"response": "Searching hospitals near you!", "action": {"type": "open_url", "url": "https://www.google.com/search?q=hospital+near+me"}}

    if "pharmacy" in msg or "medicine" in msg:
        return {"response": "Searching pharmacy near you!", "action": {"type": "open_url", "url": "https://www.google.com/search?q=pharmacy+near+me"}}

    # Fun
    if "joke" in msg or "make me laugh" in msg:
        return {"response": random.choice(JOKES), "action": None}

    if "fact" in msg or "did you know" in msg:
        return {"response": "Interesting fact: " + random.choice(FACTS), "action": None}

    if "motivat" in msg or "inspire" in msg or "encourage" in msg:
        return {"response": random.choice(MOTIVATIONS), "action": None}

    if "flip" in msg or "coin" in msg or "heads or tails" in msg:
        result = random.choice(["Heads", "Tails"])
        return {"response": "I flipped a coin... It is " + result + "!", "action": None}

    if "dice" in msg or "roll" in msg:
        result = random.randint(1, 6)
        return {"response": "You got " + str(result) + "!", "action": None}

    if "random number" in msg:
        result = random.randint(1, 100)
        return {"response": "Your random number is: " + str(result) + "!", "action": None}

    if "rock paper scissors" in msg:
        result = random.choice(["Rock", "Paper", "Scissors"])
        return {"response": "I choose: " + result + "! What did you pick?", "action": None}

    # Knowledge
    if "capital of india" in msg:
        return {"response": "The capital of India is New Delhi Sir.", "action": None}

    if "capital of" in msg:
        country = msg.replace("capital of", "").replace("what is the", "").strip().rstrip("?")
        url = "https://www.google.com/search?q=capital+of+" + country.replace(" ", "+")
        return {"response": "Searching that for you!", "action": {"type": "open_url", "url": url}}

    # Utility
    if "translate" in msg:
        return {"response": "Opening Google Translate!", "action": {"type": "open_url", "url": "https://translate.google.com"}}

    if "speed test" in msg or "internet speed" in msg:
        return {"response": "Opening speed test!", "action": {"type": "open_url", "url": "https://www.speedtest.net"}}

    if "currency" in msg or "exchange rate" in msg:
        return {"response": "Opening currency converter!", "action": {"type": "open_url", "url": "https://www.google.com/search?q=currency+converter"}}

    if "timer" in msg or "alarm" in msg:
        return {"response": "Opening timer for you Sir!", "action": {"type": "open_url", "url": "https://www.google.com/search?q=set+timer"}}

    if "screenshot" in msg:
        return {"response": "Press Win + Shift + S to take a screenshot Sir!", "action": None}

    if "ip address" in msg:
        return {"response": "Checking your IP address!", "action": {"type": "open_url", "url": "https://www.google.com/search?q=what+is+my+ip+address"}}

    # Shopping
    if "buy" in msg or "shop" in msg or "price of" in msg:
        query = msg.replace("buy", "").replace("shop for", "").replace("price of", "").strip()
        url = "https://www.amazon.in/s?k=" + query.replace(" ", "+")
        return {"response": "Searching Amazon for: " + query + "!", "action": {"type": "open_url", "url": url}}

    # Default - search Google
    url = "https://www.google.com/search?q=" + message.replace(" ", "+")
    return {"response": "Let me search that for you Sir!", "action": {"type": "open_url", "url": url}}


@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def chat(request):
    if request.method == "OPTIONS":
        r = JsonResponse({})
        r["Access-Control-Allow-Origin"] = "*"
        r["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        r["Access-Control-Allow-Headers"] = "Content-Type"
        return r
    try:
        body = json.loads(request.body)
        message = body.get("message", "").strip()
        session_id = body.get("session_id", "default")
        if not message:
            return JsonResponse({"error": "Empty message"}, status=400)
        result = process_command(message)
        log = ChatLog.objects.create(user_message=message, ai_response=result["response"], session_id=session_id)
        return JsonResponse({"response": result["response"], "action": result.get("action"), "timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M:%S")})
    except Exception as e:
        return JsonResponse({"error": "Server error: " + str(e)}, status=500)


@require_http_methods(["GET"])
def history(request):
    limit = int(request.GET.get("limit", 20))
    session_id = request.GET.get("session_id", "default")
    logs = ChatLog.objects.filter(session_id=session_id)[:limit]
    data = [{"user_message": l.user_message, "ai_response": l.ai_response, "timestamp": l.timestamp.strftime("%Y-%m-%d %H:%M:%S")} for l in logs]
    return JsonResponse({"history": list(reversed(data))})
'''

# Write to views.py
path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend", "assistant", "views.py")
with open(path, "w", encoding="utf-8") as f:
    f.write(views_content)

print("✅ views.py updated successfully!")
print("Now run: python manage.py runserver")
