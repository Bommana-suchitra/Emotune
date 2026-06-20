from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Set up Google OAuth social application'

    def handle(self, *args, **options):
        # Determine site domain based on environment
        site_domain = os.getenv('SITE_DOMAIN', '127.0.0.1:8000')
        site_name = os.getenv('SITE_NAME', 'VisoSound')
        
        # Create or update site
        site, created = Site.objects.get_or_create(
            id=settings.SITE_ID,
            defaults={'domain': site_domain, 'name': site_name}
        )
        
        # Update domain if it was using default and should be changed
        if not created and site.domain in ['example.com', 'example.org']:
            site.domain = site_domain
            site.name = site_name
            site.save()
            self.stdout.write(f'✅ Updated site domain to: {site.domain}')
        elif created:
            self.stdout.write(f'✅ Created site: {site.domain}')
        else:
            self.stdout.write(f'ℹ️  Site already exists: {site.domain}')

        # Create Google social app
        google_client_id = getattr(settings, 'GOOGLE_CLIENT_ID', '')
        google_client_secret = getattr(settings, 'GOOGLE_CLIENT_SECRET', '')

        def is_placeholder(value: str) -> bool:
            if not value:
                return True
            normalized = value.strip().lower()
            return (
                normalized.startswith('your-')
                or 'your-google-client-id' in normalized
                or 'your-google-client-secret' in normalized
                or 'your-client-id' in normalized
                or 'your-client-secret' in normalized
                or 'replace-me' in normalized
            )

        if is_placeholder(google_client_id) or is_placeholder(google_client_secret):
            self.stdout.write(
                self.style.WARNING(
                    '⚠️  Invalid or placeholder Google OAuth credentials detected.\n'
                    '   - Open .env in the project root\n'
                    '   - Replace GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET with valid values\n'
                    '   - Make sure the client is a Web application with redirect URI:\n'
                    '     http://127.0.0.1:8000/accounts/google/login/callback/\n'
                    '   - Then run: python manage.py setup_social_app\n'
                    '   See SETUP_OAUTH.md for detailed instructions.'
                )
            )
            return

        social_app, created = SocialApp.objects.get_or_create(
            provider='google',
            defaults={
                'name': 'Google',
                'client_id': google_client_id,
                'secret': google_client_secret,
            }
        )

        if created:
            social_app.sites.add(site)
            social_app.save()
            self.stdout.write(
                self.style.SUCCESS(f'✅ Successfully created Google social app')
            )
        else:
            # Update if credentials changed
            if social_app.client_id != google_client_id or social_app.secret != google_client_secret:
                social_app.client_id = google_client_id
                social_app.secret = google_client_secret
                social_app.save()
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Updated Google social app credentials')
                )
            else:
                self.stdout.write(f'ℹ️  Google social app already exists and is up to date')

        # Ensure site is associated
        if not social_app.sites.filter(id=site.id).exists():
            social_app.sites.add(site)
            self.stdout.write(f'✅ Associated Google app with site: {site}')