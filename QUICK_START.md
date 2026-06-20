# ⚡ Quick Start: Fix Google OAuth in 5 Minutes

## Problem
```
Authorization Error
The OAuth client was not found.
Error 401: invalid_client
```

## Root Cause
- Missing Google OAuth credentials
- SocialApp not registered in database
- Environment variables not configured

## Solution

### Step 1: Get Credentials (3 minutes)
1. Go to: https://console.cloud.google.com/
2. Create new project → "VisoSound"
3. Enable "Google+ API"
4. Create "OAuth 2.0 Client ID" (Web application)
5. Add authorized redirect:
   ```
   http://127.0.0.1:8000/accounts/google/login/callback/
   ```
6. Copy Client ID and Client Secret

### Step 2: Create .env File (1 minute)
Create `.env` in project root with:
```
GOOGLE_CLIENT_ID=your-client-id-here
GOOGLE_CLIENT_SECRET=your-client-secret-here
```

### Step 3: Run Setup (1 minute)
```bash
cd /home/rguktrkvalley/Documents/viso_sound

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Register OAuth app
python manage.py setup_social_app
```

### Step 4: Test
```bash
python manage.py runserver
# Visit: http://localhost:8000/login/
# Click "Continue with Google" → Should work! ✅
```

## Files Changed
- ✅ `requirements.txt` - Added python-dotenv
- ✅ `viso_sound/settings.py` - Load from .env
- ✅ `setup_oauth.sh` - Automation script
- ✅ `.gitignore` - Protect secrets

## Troubleshooting

| Error | Fix |
|-------|-----|
| `invalid_client` | Check .env credentials match Google Console |
| `OAuth client not found` | Run `python manage.py setup_social_app` |
| `Invalid redirect URI` | Update Google Console URI exactly |

## ✅ What Works Now
- ✅ Google OAuth button configured in login.html
- ✅ Django Allauth integrated
- ✅ Database migrations ready
- ✅ Environment variables loading properly

See `SETUP_OAUTH.md` for detailed guide with screenshots.
