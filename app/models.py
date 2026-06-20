from django.db import models
from django.contrib.auth.models import User

LANGUAGE_CHOICES = [
    ('English', 'English'),
    ('Tamil', 'Tamil'),
    ('Hindi', 'Hindi'),
    ('Telugu', 'Telugu'),
    ('Korean', 'Korean'),
    ('Spanish', 'Spanish'),
]

class UserProfile(models.Model):
    """
    Extends Django's built-in User model with VisoSound-specific fields.
    The built-in User already stores:
      - username, email, password (hashed), first_name, last_name,
        is_active, date_joined, last_login
    This model adds app-specific preferences.
    """
    user              = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    preferred_language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, default='English')
    avatar            = models.ImageField(upload_to='avatars/', null=True, blank=True)
    created_at        = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s profile"