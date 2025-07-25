# accounts/signals.py
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserProfile

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    - When a new User is created, make a UserProfile.
    - On subsequent saves (e.g. updating last_login), do nothing.
    """
    if created:
        UserProfile.objects.create(user=instance)
    # else: don’t call instance.profile.save() here,
    # you don’t need to update the UserProfile on every User.save.
