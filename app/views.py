import json
import base64
import numpy as np
import requests
import cv2
from io import BytesIO
from PIL import Image

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings



import json
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings
from django.urls import reverse

from .models import UserProfile


# ── AUTH (Combined Login/Register) ───────────────────────────────────────────
def auth_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    next_url = request.GET.get('next')
    if next_url:
        return redirect(f"{reverse('login')}?next={next_url}")
    return redirect('login')


# ── REGISTER ──────────────────────────────────────────────────────────────────
def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username  = request.POST.get('username', '').strip()
        email     = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        language  = request.POST.get('language', 'English')

        # ── Validation ──────────────────────────────────────────────────────
        if not username or not email or not password1:
            messages.error(request, 'All fields are required.')
        elif password1 != password2:
            messages.error(request, 'Passwords do not match.')
        elif len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'An account with this email already exists.')
        else:
            # ── Create User + Profile ────────────────────────────────────────
            user = User.objects.create_user(username=username, email=email, password=password1)
            UserProfile.objects.create(user=user, preferred_language=language)
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f'Welcome to VisoSound, {username}!')
            return redirect('home')

    return render(request, 'app/register.html', {
        'languages': SUPPORTED_LANGUAGES,
    })


# ── LOGIN ─────────────────────────────────────────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'app/login.html')


# ── LOGOUT ────────────────────────────────────────────────────────────────────
@login_required
def logout_view(request):
    logout(request)
    return redirect('auth')


# ── FORGOT PASSWORD ───────────────────────────────────────────────────────────
def forgot_password_view(request):
    """Step 1: User enters their registered email."""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Show same success message to prevent email enumeration attacks
            messages.success(request, 'If that email exists, a reset link has been sent.')
            return redirect('forgot_password')

        # Generate token + uid
        uid   = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_link = request.build_absolute_uri(
            reverse('reset_password', kwargs={'uidb64': uid, 'token': token})
        )

        # Send the email
        send_mail(
            subject='VisoSound – Password Reset Request',
            message=(
                f'Hi {user.username},\n\n'
                f'You requested a password reset for your VisoSound account.\n\n'
                f'Click the link below to set a new password (valid for 24 hours):\n'
                f'{reset_link}\n\n'
                f'If you did not request this, you can safely ignore this email.\n\n'
                f'– The VisoSound Team'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        messages.success(request, 'A password reset link has been sent to your email.')
        return redirect('forgot_password')

    return render(request, 'app/forgot_password.html')


# ── RESET PASSWORD ────────────────────────────────────────────────────────────
def reset_password_view(request, uidb64, token):
    """Step 2: User clicks link in email, enters new password."""
    try:
        uid  = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is None or not default_token_generator.check_token(user, token):
        messages.error(request, 'This password reset link is invalid or has expired.')
        return redirect('forgot_password')

    if request.method == 'POST':
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        if not password1:
            messages.error(request, 'Password cannot be empty.')
        elif password1 != password2:
            messages.error(request, 'Passwords do not match.')
        elif len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
        else:
            user.set_password(password1)
            user.save()
            messages.success(request, 'Password updated! You can now log in.')
            return redirect('auth')

    return render(request, 'app/reset_password.html', {'uidb64': uidb64, 'token': token})



# ── EMOTION → EMOJI MAP ────────────────────────────────────────────────────────
EMOTION_EMOJI = {
    'happy':    {'emoji': '😄', 'label': 'Happy',     'color': '#00d25a'},
    'sad':      {'emoji': '😢', 'label': 'Sad',       'color': '#ff5040'},
    'angry':    {'emoji': '😠', 'label': 'Angry',     'color': '#ff2244'},
    'fear':     {'emoji': '😨', 'label': 'Fearful',   'color': '#ffc800'},
    'surprise': {'emoji': '😲', 'label': 'Surprised', 'color': '#00c8ff'},
    'disgust':  {'emoji': '🤢', 'label': 'Disgusted', 'color': '#c800c8'},
    'neutral':  {'emoji': '😐', 'label': 'Neutral',   'color': '#b4b4b4'},
}

# ── LANGUAGE → EMOTION SEARCH QUERIES ─────────────────────────────────────────
EMOTION_SEARCH = {
    'English': {
        'happy':    'upbeat happy pop feel good',
        'sad':      'sad emotional ballad heartbreak',
        'angry':    'rock rage intense energy',
        'fear':     'calm peaceful ambient',
        'surprise': 'exciting energetic pop dance',
        'disgust':  'dark alternative indie',
        'neutral':  'lofi chill study beats',
    },
    'Tamil': {
        'happy':    'tamil kuthu happy dance',
        'sad':      'tamil sad melody love',
        'angry':    'tamil mass bgm action',
        'fear':     'tamil devotional calm',
        'surprise': 'tamil party dance number',
        'disgust':  'tamil independent music',
        'neutral':  'tamil soft melody evening',
    },
    'Hindi': {
        'happy':    'bollywood happy dance party',
        'sad':      'hindi sad romantic melody',
        'angry':    'hindi intense bgm',
        'fear':     'hindi devotional spiritual',
        'surprise': 'bollywood party 2024',
        'disgust':  'hindi indie alternative',
        'neutral':  'hindi soft ghazal',
    },
    'Telugu': {
        'happy':    'telugu happy dance songs',
        'sad':      'telugu sad melody love',
        'angry':    'telugu mass bgm action',
        'fear':     'telugu devotional calm',
        'surprise': 'telugu energetic dance',
        'disgust':  'telugu indie folk',
        'neutral':  'telugu soft melody',
    },
    'Korean': {
        'happy':    'kpop upbeat happy dance',
        'sad':      'kpop ballad sad emotional',
        'angry':    'k-rock intense energy',
        'fear':     'korean healing soft',
        'surprise': 'kpop exciting new',
        'disgust':  'korean indie alternative',
        'neutral':  'korean lofi chill',
    },
    'Spanish': {
        'happy':    'reggaeton feliz fiesta',
        'sad':      'balada romantica triste',
        'angry':    'rock español intenso',
        'fear':     'musica relajante calma',
        'surprise': 'salsa bachata energetic',
        'disgust':  'indie alternativo oscuro',
        'neutral':  'bossa nova suave',
    },
}

SUPPORTED_LANGUAGES = list(EMOTION_SEARCH.keys())

# ── Language-Only Search (ignores emotion) ────────────────────────────────────
LANGUAGE_SEARCH = {
    'English': 'popular english songs 2024 hits',
    'Tamil':   'popular tamil songs hits',
    'Hindi':   'popular hindi songs bollywood hits',
    'Telugu':  'popular telugu songs hits',
    'Korean':  'popular kpop songs hits',
    'Spanish': 'popular spanish songs hits reggaeton',
}

# ── Popular Song Names by Language ────────────────────────────────────────────
POPULAR_SONGS = {
    'English': [
        'Blinding Lights The Weeknd',
        'Watermelon Sugar Harry Styles',
        'Levitating Dua Lipa',
        'Good 4 U Olivia Rodrigo',
        'Stay The Kid Laroi Justin Bieber',
        'Peaches Justin Bieber',
        'Drivers License Olivia Rodrigo',
        'Montero Lil Nas X',
        'Permission to Dance BTS',
        'Butter BTS',
    ],
    'Tamil': [
        'Naachiyaar Tamil song',
        'Rowdy Baby Dhanush',
        'Oh Oh Oh Tamil song',
        'Taanakkaran Tamil song',
        'Master the blame',
        'Vaathi Coming Dhanush',
        'Putham Pudhu Kaalai',
        'Coffee with Kadhal',
        'Oh My Dog Tamil song',
        'Adiye Tamil song',
    ],
    'Hindi': [
        'Kesariya Brahmāstra',
        'Raatan Lambiyan',
        'Ghungroo War',
        'Tum Hi Ho Aashiqui 2',
        'Kabira Yeh Jawaani Hai Deewani',
        'Bheegi Hawa Saathiya',
        'Tera Hone Laga Hoon Ajab Prem Ki Ghazab Kahani',
        'Pehla Nasha Jo Subahon Mein',
        'Tujhe Dekha Toh Yeh Jana Sanam',
        'Kaho Na Kaho Kuch Bhi Na',
    ],
    'Telugu': [
        'Samajavaragamana Telugu song',
        'Butta Bomma Armaan Malik',
        'Naaku Mukka Telugu song',
        'Idi Sangathi Telugu song',
        'Manasu Mangalyam Telugu song',
        'Srimanthudu Telugu song',
        'Pelli Kanuka Telugu song',
        'Dhee Telugu song',
        'Oh My Dog Telugu song',
        'Sasirekha Parinayam Telugu song',
    ],
    'Korean': [
        'Dynamite BTS',
        'Butter BTS',
        'Permission to Dance BTS',
        'Boy With Luv BTS',
        'DNA BTS',
        'Fake Love BTS',
        'Spring Day BTS',
        'Blood Sweat & Tears BTS',
        'Fire BTS',
        'Save Me BTS',
    ],
    'Spanish': [
        'Despacito Luis Fonsi Daddy Yankee',
        'Bailando Enrique Iglesias',
        'La Macarena Los Del Rio',
        'Hips Dont Lie Shakira',
        'Gasolina Daddy Yankee',
        'La Bamba Ritchie Valens',
        'Conga Gloria Estefan',
        'Rhythm Is Gonna Get You Gloria Estefan',
        'Livin La Vida Loca Ricky Martin',
        'Maria Maria Santana',
    ],
}


# ── Custom Emotion Predictor ──────────────────────────────────────────────────
from predict_emotion import detect_emotion_from_image_custom


def detect_emotion_from_image(image_data_b64: str):
    """
    Takes a base64 JPEG/PNG string (from <canvas>),
    returns (emotion, confidence, scores_dict).
    Uses custom trained model, falls back to mock if unavailable.
    """
    # Try custom model first
    result = detect_emotion_from_image_custom(image_data_b64)
    if result is not None:
        emotion, confidence, scores = result
    else:
        # Fallback to mock if custom model fails
        emotions = list(EMOTION_EMOJI.keys())
        weights = [0.35, 0.20, 0.10, 0.20, 0.08, 0.04, 0.03]
        emotion = np.random.choice(emotions, p=weights)
        confidence = float(np.random.uniform(0.60, 0.95))
        scores = {e: round(float(np.random.uniform(0, 0.05)), 3) for e in emotions}
        scores[emotion] = confidence

    return emotion, confidence, scores


def search_spotify_tracks(query: str):
    """Call Spotify23 RapidAPI and return list of track dicts."""
    key = getattr(settings, 'RAPIDAPI_KEY', '')
    if not key or key == 'YOUR_RAPIDAPI_KEY_HERE':
        # Return mock data if no API key
        return get_mock_tracks(query)

    try:
        resp = requests.get(
            'https://spotify23.p.rapidapi.com/search/',
            headers={
                'X-RapidAPI-Key': key,
                'X-RapidAPI-Host': 'spotify23.p.rapidapi.com',
            },
            params={'q': query, 'type': 'tracks', 'offset': '0', 'limit': '5'},
            timeout=8,
        )
        resp.raise_for_status()
        data = resp.json()
        tracks = []
        for item in data.get('tracks', {}).get('items', []):
            d = item.get('data', {})
            if not d:
                continue

            spotify_id = d.get('id') or ''
            if not spotify_id:
                uri = d.get('uri', '')
                if uri.startswith('spotify:track:'):
                    spotify_id = uri.split(':')[-1]

            if not spotify_id:
                continue

            cover_sources = d.get('albumOfTrack', {}).get('coverArt', {}).get('sources', [])
            cover = cover_sources[0].get('url', '') if cover_sources else ''
            url = d.get('external_urls', {}).get('spotify') or f'https://open.spotify.com/track/{spotify_id}'

            tracks.append({
                'title':  d.get('name', 'Unknown'),
                'artist': d.get('artists', {}).get('items', [{}])[0].get('profile', {}).get('name', 'Unknown'),
                'url':    url,
                'cover':  cover,
            })
        return tracks[:5] if tracks else get_mock_tracks(query)
    except Exception as e:
        print(f'[VisoSound] Spotify API error: {e}')
        return get_mock_tracks(query)


def get_mock_tracks(query: str):
    """Return mock track data for testing."""
    lower = query.lower()
    if 'happy' in lower or 'upbeat' in lower or 'feel good' in lower:
        return [
            {'title': 'Happy', 'artist': 'Pharrell Williams', 'url': 'https://open.spotify.com/track/60nZcImufyMA1MKQY3dcCH', 'cover': ''},
            {'title': 'Good As Hell', 'artist': 'Lizzo', 'url': 'https://open.spotify.com/track/2G7e0sNFx7GvGgkJRGsK58', 'cover': ''},
        ]
    if 'sad' in lower or 'emotional' in lower or 'ballad' in lower:
        return [
            {'title': 'Someone Like You', 'artist': 'Adele', 'url': 'https://open.spotify.com/track/4kflIGfjdZJW4ot2ioixTB', 'cover': ''},
            {'title': 'Fix You', 'artist': 'Coldplay', 'url': 'https://open.spotify.com/track/3e9HZxeyfWwjeyPAMmWSSQ', 'cover': ''},
        ]
    if 'angry' in lower or 'rage' in lower or 'intense' in lower:
        return [
            {'title': 'Break Stuff', 'artist': 'Limp Bizkit', 'url': 'https://open.spotify.com/track/2b4bY6qdK7B8woxT0GQ8RS', 'cover': ''},
            {'title': 'Killing In The Name', 'artist': 'Rage Against The Machine', 'url': 'https://open.spotify.com/track/6i3mBybzJCwQ9JE5B2A6xG', 'cover': ''},
        ]
    if 'surprise' in lower or 'exciting' in lower or 'energetic' in lower:
        return [
            {'title': 'Uptown Funk', 'artist': 'Mark Ronson', 'url': 'https://open.spotify.com/track/32OlwWuMpZ6b0aN2RZOeMS', 'cover': ''},
            {'title': 'Can’t Stop', 'artist': 'Red Hot Chili Peppers', 'url': 'https://open.spotify.com/track/2s5WOiUKYl7pOge0GlkZdT', 'cover': ''},
        ]
    return [
        {'title': 'Dreams', 'artist': 'Fleetwood Mac', 'url': 'https://open.spotify.com/track/2dLLR6qlu5UJ5gk0dKz0h3', 'cover': ''},
        {'title': 'Weightless', 'artist': 'Marconi Union', 'url': 'https://open.spotify.com/track/6VVwmbK3Z4wG1YH25K4vib', 'cover': ''},
    ]


# ── Django Views ───────────────────────────────────────────────────────────────

@login_required
def home(request):
    context = {
        'languages': SUPPORTED_LANGUAGES,
        'emotions': EMOTION_EMOJI,
    }
    return render(request, 'app/home.html', context)

@login_required
def index(request):
    context = {
        'languages': SUPPORTED_LANGUAGES,
        'emotions': EMOTION_EMOJI,
    }
    return render(request, 'app/index.html', context)


@csrf_exempt
def detect_emotion(request):
    """POST: {image: base64string} → {emotion, confidence, scores, emoji, label, color}"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        body = json.loads(request.body)
        image_b64 = body.get('image', '')
        if not image_b64:
            return JsonResponse({'error': 'No image data'}, status=400)

        emotion, confidence, scores = detect_emotion_from_image(image_b64)
        info = EMOTION_EMOJI.get(emotion, EMOTION_EMOJI['neutral'])

        return JsonResponse({
            'emotion':    emotion,
            'confidence': round(confidence * 100, 1),
            'scores':     {k: round(v * 100, 1) for k, v in scores.items()},
            'emoji':      info['emoji'],
            'label':      info['label'],
            'color':      info['color'],
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def search_songs(request):
    """POST: {emotion, language, mode?} → {tracks: [...]}"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        body = json.loads(request.body)
        emotion  = body.get('emotion', 'happy')
        language = body.get('language', 'English')
        mode     = body.get('mode', 'emotion')  # 'emotion', 'language_only', 'popular'

        if language not in EMOTION_SEARCH:
            language = 'English'

        if mode == 'emotion':
            # Emotion + language search is more specific and keeps the emoji mood relevant
            if emotion not in EMOTION_SEARCH[language]:
                emotion = 'neutral'
            query = f"{language} {emotion} songs {EMOTION_SEARCH[language][emotion]}"
            tracks = search_spotify_tracks(query)

        elif mode == 'language_only':
            # Language-only search (ignores emotion)
            query = LANGUAGE_SEARCH.get(language, 'popular songs')
            tracks = search_spotify_tracks(query)

        elif mode == 'popular':
            # Search for specific popular song names
            song_names = POPULAR_SONGS.get(language, POPULAR_SONGS['English'])
            tracks = []
            for song in song_names[:5]:  # Limit to 5 songs
                song_tracks = search_spotify_tracks(song)
                if song_tracks:
                    tracks.extend(song_tracks[:1])  # Take first result for each song
            tracks = tracks[:5]  # Ensure max 5 tracks
            query = f"Popular {language} songs"

        else:
            return JsonResponse({'error': 'Invalid mode'}, status=400)

        return JsonResponse({'tracks': tracks, 'query': query, 'mode': mode})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def search_songs_by_name(request):
    """POST: {query: string} → {tracks: [...]}"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        body = json.loads(request.body)
        query = body.get('query', '').strip()

        if not query:
            return JsonResponse({'error': 'Query is required'}, status=400)

        tracks = search_spotify_tracks(query)
        return JsonResponse({'tracks': tracks, 'query': query})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
