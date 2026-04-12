from django.contrib import admin
from .models import UserProfile, StudentProfile, CertificateProject


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'is_locked', 'failed_login_attempts')


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'university', 'department', 'semester', 'cgpa')
    search_fields = ('user__username', 'university', 'department')


@admin.register(CertificateProject)
class CertificateProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'student_profile', 'project_link', 'uploaded_at')
    search_fields = ('title',)