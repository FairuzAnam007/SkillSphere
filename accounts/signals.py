from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db import OperationalError, ProgrammingError

from .models import UserProfile, SkillCategory


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(
            user=instance,
            defaults={
                "role": "student",
                "is_locked": False,
                "failed_login_attempts": 0,
            }
        )


@receiver(post_migrate)
def create_default_skill_categories(sender, **kwargs):
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
            ("Leadership", "Leadership, teamwork, and management skills"),
            ("Creative", "Creative, content, and media-related skills"),
            ("Soft Skill", "Communication, teamwork, problem-solving, and adaptability"),
        ]

        for name, description in default_categories:
            SkillCategory.objects.get_or_create(
                name=name,
                defaults={"description": description},
            )

    except (OperationalError, ProgrammingError):
        return