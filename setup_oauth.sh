#!/bin/bash
# Automation script to set up Google OAuth for VisoSound

set -e  # Exit on error

echo "🔐 VisoSound Google OAuth Setup"
echo "=============================="
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo ""
    echo "Please create a .env file in the project root with your Google OAuth credentials:"
    echo ""
    echo "Create .env with:"
    echo "  GOOGLE_CLIENT_ID=your-client-id"
    echo "  GOOGLE_CLIENT_SECRET=your-client-secret"
    echo ""
    echo "See SETUP_OAUTH.md for detailed instructions."
    exit 1
fi

# Read credentials from .env
source .env

# Verify credentials
if [ -z "$GOOGLE_CLIENT_ID" ] || [ -z "$GOOGLE_CLIENT_SECRET" ]; then
    echo "❌ Error: GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET not set in .env"
    exit 1
fi

echo "✅ Found .env credentials"
echo ""

# Install requirements
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Run migrations
echo "🗄️  Running database migrations..."
python manage.py migrate --noinput
echo "✅ Migrations completed"
echo ""

# Set up Google OAuth
echo "🔐 Setting up Google OAuth..."
python manage.py setup_social_app
echo "✅ Google OAuth configured"
echo ""

echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Start server: python manage.py runserver"
echo "  2. Visit: http://localhost:8000/login/"
echo "  3. Click 'Continue with Google'"
echo ""
