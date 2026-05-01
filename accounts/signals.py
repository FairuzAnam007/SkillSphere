from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db import OperationalError, ProgrammingError, IntegrityError

from .models import UserProfile, SkillCategory


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Automatically creates a UserProfile for every new User.

    This prevents login/dashboard errors where a user exists
    but has no role profile.
    """
    try:
        if created:
            UserProfile.objects.get_or_create(
                user=instance,
                defaults={
                    "role": "student",
                    "is_locked": False,
                    "failed_login_attempts": 0,
                },
            )
        else:
            UserProfile.objects.get_or_create(
                user=instance,
                defaults={
                    "role": "student",
                    "is_locked": False,
                    "failed_login_attempts": 0,
                },
            )

    except (OperationalError, ProgrammingError, IntegrityError):
        # Avoid crashing during migrations or test database setup.
        return


@receiver(post_migrate)
def create_default_skill_categories(sender, **kwargs):
    """
    Creates default skill categories after migration.

    get_or_create is used so duplicate categories are not created
    when migrations/tests run multiple times.
    """
    if sender.name != "accounts":
        return

    try:
        default_categories = [
            ("Programming", "Coding, software development, and programming skills"),
            ("Web Development", "Frontend, backend, and full-stack development"),
            ("Database", "SQL, database design, and data management"),
            ("Networking", "Networking, routing, switching, and security"),
            ("Design", "UI, UX, graphics, and visual design"),
            ("Communication", "Presentation, writing, and teamwork"),
            ("Research", "Academic research and documentation"),
            ("Leadership", "Leadership, teamwork, and organizational skills"),
            ("Creative", "Creative, content, and visual presentation skills"),
        ]


        for name, description in default_categories:
            SkillCategory.objects.get_or_create(
                name=name,
                defaults={
                    "description": description,
                },
            )

    except (OperationalError, ProgrammingError, IntegrityError):
        # Avoid crashing during migrations or tests.
        return