# Google OAuth Setup Guide for VisoSound

## Issues Fixed
1. ✅ Configured environment variable loading with python-dotenv
2. ✅ Updated settings.py to load credentials from .env
3. ✅ Created .env.example template

## Step 1: Get Google OAuth Credentials

### 1.1 Go to Google Cloud Console
- Visit: https://console.cloud.google.com/
- Sign in with your Google account

### 1.2 Create a New Project
- Click the project dropdown at the top
- Click "NEW PROJECT"
- Enter project name: `VisoSound` (or any name)
- Click "CREATE"

### 1.3 Enable Google+ API
- In the left sidebar, go to "APIs & Services" → "Library"
- Search for "Google+ API"
- Click on it and press "ENABLE"

### 1.4 Create OAuth Credentials
- Go to "APIs & Services" → "Credentials"
- Click "Create Credentials" → "OAuth 2.0 Client ID"
- Choose "Web application"
- Click "Create OAuth consent screen"

#### OAuth Consent Screen Setup:
- **User Type**: Select "External" (for development)
- **App name**: VisoSound
- **User support email**: Your Gmail address
- **Developer contact**: Your Gmail address
- Click "SAVE AND CONTINUE" through all sections
- Add the following scopes:
  - email
  - profile
  - openid

#### Back to Credentials:
- **Name**: VisoSound OAuth
- **Authorized JavaScript origins**: 
  ```
  http://localhost:8000
  http://127.0.0.1:8000
  ```
- **Authorized redirect URIs**:
  ```
  http://localhost:8000/accounts/google/login/callback/
  http://127.0.0.1:8000/accounts/google/login/callback/
  ```
- Click "CREATE"

### 1.5 Copy Your Credentials
- You'll see a dialog with "Client ID" and "Client Secret"
- Copy both values (you'll need them in the next step)

## Step 2: Set Up Environment Variables

### 2.1 Create .env file
In the project root (`/home/rguktrkvalley/Documents/viso_sound/`), create a `.env` file with:

```
GOOGLE_CLIENT_ID=your-client-id-from-google-console
GOOGLE_CLIENT_SECRET=your-client-secret-from-google-console
DEBUG=True
SECRET_KEY=django-insecure-visosound-change-in-production-xyz123
EMAIL_HOST_USER=sathishkumarreddymeegada@gmail.com
EMAIL_HOST_PASSWORD=vije ioqk mbtt zvrf
```

**⚠️ Important**:
- Keep `.env` private (add to `.gitignore`)
- Never commit `.env` to version control
- Use `.env.example` to show what variables are needed

## Step 3: Install Dependencies

```bash
cd /home/rguktrkvalley/Documents/viso_sound
pip install -r requirements.txt
```

This installs `python-dotenv` which loads your .env file.

## Step 4: Run Database Migrations

```bash
python manage.py migrate
```

## Step 5: Register Google OAuth in Database

```bash
python manage.py setup_social_app
```

This command will:
- Create a Site record
- Create a SocialApp record for Google OAuth
- Link them together

Expected output:
```
Site already exists: VisoSound
Successfully created Google social app
```

## Step 6: Test the Setup

1. **Start the development server**:
   ```bash
   python manage.py runserver
   ```

2. **Open your browser**:
   - Go to: http://localhost:8000/login/

3. **Click "Continue with Google"** button

4. **You should be redirected to Google login** (instead of getting 401 error)

## Troubleshooting

### Still getting "Error 401: invalid_client"?
- ✅ Verify `.env` file exists in project root
- ✅ Check GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET are correct (copy-paste again)
- ✅ Restart Django server: `python manage.py runserver`

### "The OAuth client was not found"?
- Run migrations: `python manage.py migrate`
- Run setup command: `python manage.py setup_social_app`
- Check Site ID in Django admin:
  ```
  python manage.py shell
  >>> from django.contrib.sites.models import Site
  >>> Site.objects.all()
  <QuerySet [<Site: VisoSound>]>
  ```

### Connection refused when accessing login?
- Make sure Django server is running: `python manage.py runserver`
- Try: http://127.0.0.1:8000/login/ instead of localhost

### "Invalid redirect URI" error from Google?
- Re-check the Authorized redirect URIs in Google Console
- Must be exactly: `http://localhost:8000/accounts/google/login/callback/`
- Restart Django server after any changes

## Production Deployment

For production (e.g., online domain like `example.com`):

1. **Update .env**:
   ```
   GOOGLE_CLIENT_ID=your-production-client-id
   GOOGLE_CLIENT_SECRET=your-production-client-secret
   ```

2. **Update Google Console**:
   - Add authorized origins: `https://example.com`
   - Add redirect URI: `https://example.com/accounts/google/login/callback/`

3. **Update ALLOWED_HOSTS in settings.py**:
   ```python
   ALLOWED_HOSTS = ['example.com', 'www.example.com']
   ```

4. **Update Site domain in Django admin**:
   - Go to: http://admin/django_admin_site/sites/1/change/
   - Update domain to: `example.com`

## Quick Reference

| Issue | Fix |
|-------|-----|
| "invalid_client" | Check GOOGLE_CLIENT_ID/SECRET in .env |
| "OAuth client not found" | Run `python manage.py setup_social_app` |
| "Invalid redirect URI" | Update Google Console URIs exactly |
| Login not working | Restart server: `python manage.py runserver` |

## Files Modified
- ✅ `requirements.txt` - Added python-dotenv
- ✅ `viso_sound/settings.py` - Added .env loading
- ✅ `.env.example` - Template for environment variables
- ⏳ `.env` - Create this with your credentials (NOT committed to git)
