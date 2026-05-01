from django.shortcuts import redirect
from django.urls import reverse
from django.core.exceptions import PermissionDenied

from .models import UserProfile


class RolePermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not request.user.is_authenticated:
            return None

        if request.user.is_superuser:
            return None

        path = request.path

        ignored_paths = [
            reverse("home"),
            reverse("logout"),
            reverse("role_redirect"),
        ]

        if path in ignored_paths:
            return None

        profile, created = UserProfile.objects.get_or_create(
            user=request.user,
            defaults={"role": "student"},
        )

        if path.startswith("/dashboard/student/") and profile.role != "student":
            raise PermissionDenied("Only students can access student dashboard.")

        if path.startswith("/dashboard/teacher/") and profile.role != "teacher":
            raise PermissionDenied("Only teachers can access teacher dashboard.")

        if path.startswith("/skills/") and profile.role != "student":
            raise PermissionDenied("Only students can manage skills.")

        if path.startswith("/profile/") and profile.role != "student":
            raise PermissionDenied("Only students can manage profile.")

        if path.startswith("/mentorship/request/") and profile.role != "student":
            raise PermissionDenied("Only students can request mentoring.")

        if path.startswith("/mentorship/respond/") and profile.role != "teacher":
            raise PermissionDenied("Only teachers can respond to mentoring requests.")

        if path.startswith("/verification/") and profile.role not in ["student", "teacher"]:
            raise PermissionDenied("Only students and teachers can access verification.")

        return None