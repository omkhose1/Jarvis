# 🤖 J.A.R.V.I.S — AI Assistant Setup Guide

## 📁 Project Structure

```
jarvis/
├── backend/                  ← Django project
│   ├── manage.py
│   ├── requirements.txt
│   ├── backend/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── assistant/            ← Django app
│       ├── models.py         ← ChatLog database model
│       ├── views.py          ← /api/chat/ and /api/history/
│       ├── urls.py           ← URL routing
│       └── admin.py          ← Admin panel setup
└── frontend/
    ├── index.html            ← Jarvis UI
    ├── style.css             ← Futuristic HUD styles
    └── script.js             ← Chat + voice + history logic
```

---

## ⚙️ Step 1 — Install Python & Django

Make sure Python 3.9+ is installed, then:

```bash
# Go into the backend folder
cd jarvis/backend

# (Optional but recommended) Create a virtual environment
python -m venv venv

# Activate it:
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 🔑 Step 2 — Add Your OpenAI API Key

Open `backend/settings.py` and find this line:

```python
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', 'your-openai-api-key-here')
```

**Option A** — Set as environment variable (recommended):
```bash
# Mac/Linux
export OPENAI_API_KEY="sk-your-key-here"

# Windows CMD
set OPENAI_API_KEY=sk-your-key-here
```

**Option B** — Replace directly in settings.py (not for production):
```python
OPENAI_API_KEY = 'sk-your-key-here'
```

> 💡 **No OpenAI key?** Jarvis still works! Built-in commands (time, date, open YouTube, search Google, etc.) work without any API key.

---

## 🗄️ Step 3 — Create the Database

```bash
# Still inside jarvis/backend/
python manage.py makemigrations
python manage.py migrate
```

This creates `db.sqlite3` — all chat history is stored here automatically.

---

## 👤 Step 4 — Create Admin User (Optional)

```bash
python manage.py createsuperuser
```

Visit `http://127.0.0.1:8000/admin/` to view all chat logs.

---

## 🚀 Step 5 — Run the Django Server

```bash
python manage.py runserver
```

You should see:
```
Starting development server at http://127.0.0.1:8000/
```

Test the API:
```bash
curl -X POST http://127.0.0.1:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "what time is it"}'
```

---

## 🌐 Step 6 — Open the Frontend

Open `jarvis/frontend/index.html` directly in your browser.

> ⚠️ If you see CORS errors, make sure Django is running first, then refresh the page.

---

## 🎤 Voice Input Notes

- **Chrome** works best for voice recognition
- Click the microphone button and speak
- Your browser may ask for microphone permission — click Allow
- Text-to-speech (Jarvis speaks back) is built-in via browser Web Speech API

---

## 🌍 Built-in Commands (No API Key Needed)

| Command | What it does |
|---------|-------------|
| "What time is it?" | Shows current time |
| "What's today's date?" | Shows today's date |
| "Open YouTube" | Opens youtube.com |
| "Open Google" | Opens google.com |
| "Open GitHub" | Opens github.com |
| "Search Python tutorials" | Google search |
| "YouTube machine learning" | YouTube search |
| "Hi" / "Hello" | Greeting response |

---

## 🚢 Deployment Options

### Render (Free tier)
1. Push code to GitHub
2. Go to render.com → New Web Service
3. Connect repo, set build command: `pip install -r requirements.txt`
4. Set start command: `python manage.py migrate && gunicorn backend.wsgi`
5. Add environment variable: `OPENAI_API_KEY`

### Railway
1. Push to GitHub
2. railway.app → New Project → Deploy from GitHub
3. Add `OPENAI_API_KEY` in Variables tab

### Before deploying:
- Set `DEBUG = False` in settings.py
- Set `ALLOWED_HOSTS = ['your-domain.com']`
- Use a real `SECRET_KEY` from environment variable
- Run `python manage.py collectstatic`

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Connection refused" on frontend | Start Django: `python manage.py runserver` |
| CORS errors | Check `django-cors-headers` is installed and in INSTALLED_APPS |
| Voice not working | Use Chrome; allow microphone permission |
| No AI response | Add OpenAI API key; built-in commands work without it |
| Database errors | Run `python manage.py migrate` |
