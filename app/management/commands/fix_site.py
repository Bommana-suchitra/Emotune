from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
import os

class Command(BaseCommand):
    help = 'Fix the Site domain if it was incorrectly set to example.com'

    def handle(self, *args, **options):
        try:
            site = Site.objects.get(id=1)
            
            old_domain = site.domain
            site_domain = os.getenv('SITE_DOMAIN', '127.0.0.1:8000')
            site_name = os.getenv('SITE_NAME', 'VisoSound')
            
            if site.domain in ['example.com', 'example.org']:
                site.domain = site_domain
                site.name = site_name
                site.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Updated site domain from "{old_domain}" to "{site.domain}"'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'ℹ️  Site domain is already correct: {site.domain}')
                )
        except Site.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('❌ Site with ID=1 not found. Run migrations first.')
            )
