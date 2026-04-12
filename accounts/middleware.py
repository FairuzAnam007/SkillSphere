from django.core.exceptions import PermissionDenied


class RolePermissionMiddleware:
    ROLE_PROTECTED_URLS = {
        'student_dashboard': ['student'],
        'teacher_dashboard': ['teacher'],
        'recruiter_dashboard': ['recruiter'],
        'admin_dashboard': ['admin'],
        'student_only_page': ['student'],
        'teacher_only_page': ['teacher'],
        'recruiter_only_page': ['recruiter'],
        'create_student_profile': ['student'],
        'update_student_profile': ['student'],
        'upload_certificate_project': ['student'],
        'delete_certificate_project': ['student'],
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not request.user.is_authenticated:
            return None

        resolver_match = getattr(request, 'resolver_match', None)
        url_name = resolver_match.url_name if resolver_match else None

        if not url_name or url_name not in self.ROLE_PROTECTED_URLS:
            return None

        allowed_roles = self.ROLE_PROTECTED_URLS[url_name]

        if request.user.is_superuser:
            return None

        if not hasattr(request.user, 'profile'):
            raise PermissionDenied("No profile assigned.")

        if request.user.profile.role not in allowed_roles:
            raise PermissionDenied("You are not authorized to access this page.")

        return None