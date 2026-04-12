from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def role_required(allowed_roles=None):
    if allowed_roles is None:
        allowed_roles = []

    def decorator(view_func):
        @login_required
        def wrapper(request, *args, **kwargs):
            user = request.user

            if user.is_superuser:
                return view_func(request, *args, **kwargs)

            if not hasattr(user, 'profile'):
                raise PermissionDenied("You do not have a profile assigned.")

            if user.profile.role not in allowed_roles:
                raise PermissionDenied("You are not authorized to access this page.")

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator