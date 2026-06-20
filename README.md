# 🎵 VisoSound — Face Expression → Music Generator

A Django web app that:
1. Opens your webcam live in the browser
2. Detects your face expression using **DeepFace**
3. Maps expression → emoji (happy 😄, sad 😢, angry 😠, etc.)
4. Searches **Spotify** via RapidAPI based on emotion + language
5. Shows clickable song cards with cover art

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
cd viso_sound
pip install -r requirements.txt
```

### 2. Set your RapidAPI key
Open `viso_sound/settings.py` and set:
```python
RAPIDAPI_KEY = 'your_rapidapi_key_here'
```
Get a free key at https://rapidapi.com → subscribe to **Spotify23** API.

### 3. Run migrations & start server
```bash
python manage.py migrate
python manage.py runserver
```

### 4. Open browser
Go to **http://127.0.0.1:8000**

---

## 📂 Project Structure
```
viso_sound/
├── manage.py
├── requirements.txt
├── viso_sound/           ← Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── app/                  ← Main app
    ├── views.py          ← Emotion detection + Spotify API logic
    ├── urls.py
    └── templates/
        └── app/
            └── index.html  ← Full UI (camera + songs)
```

---

## 🌐 Supported Languages
- English, Tamil, Hindi, Telugu, Korean, Spanish

## 😄 Supported Emotions
- happy, sad, angry, fear, surprise, disgust, neutral

---

## 🔑 API Info
- **Face Detection**: DeepFace (local, no API key needed)
- **Music Search**: RapidAPI Spotify23 (free tier available)
  - Falls back to mock results if no key is set

---

## 🛠 Tech Stack
- **Backend**: Django 4.x, Python 3.10+
- **Face AI**: DeepFace + OpenCV
- **Music API**: RapidAPI (Spotify23)
- **Frontend**: Vanilla JS + HTML/CSS (no framework)
