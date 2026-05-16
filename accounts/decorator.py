from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import UserProfile

def role_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            profile, created = UserProfile.objects.get_or_create
            (
                user=request.user,
                defaults={"role": "student"},
            )

            if profile.role not in allowed_roles:
                raise PermissionDenied("You are not allowed to access this page.")

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator
