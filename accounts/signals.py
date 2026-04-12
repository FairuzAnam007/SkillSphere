from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.utils import OperationalError, ProgrammingError
from .models import UserProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        try:
            UserProfile.objects.get_or_create(user=instance)
        except (OperationalError, ProgrammingError):
            pass


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        if hasattr(instance, 'profile'):
            instance.profile.save()
    except (OperationalError, ProgrammingError):
        pass