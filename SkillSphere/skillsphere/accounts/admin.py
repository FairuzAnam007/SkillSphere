from django.contrib import admin

from .models import (
    UserProfile,
    StudentProfile,
    CertificateProject,
    Skill,
    SkillVerificationRequest,
    VerificationLog,
)


# ==================== USER & PROFILE ====================

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'is_locked', 'failed_login_attempts')
    list_filter = ('role', 'is_locked')
    search_fields = ('user__username',)


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'university', 'department', 'semester', 'cgpa')
    search_fields = ('user__username', 'university', 'department')


@admin.register(CertificateProject)
class CertificateProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'student_profile', 'project_link', 'uploaded_at')
    search_fields = ('title',)


# ==================== STORY 4: SKILL VERIFICATION ====================

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'created_at')
    search_fields = ('name', 'category')


@admin.register(SkillVerificationRequest)
class SkillVerificationRequestAdmin(admin.ModelAdmin):
    list_display = ('student', 'skill', 'status', 'proficiency_level', 'verifier', 'requested_at')
    list_filter = ('status', 'proficiency_level')
    search_fields = ('student__user__username', 'skill__name')


@admin.register(VerificationLog)
class VerificationLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'request', 'performed_by', 'timestamp')
    list_filter = ('action',)
    readonly_fields = ('request', 'action', 'performed_by', 'note', 'timestamp')