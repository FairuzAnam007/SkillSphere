from django.contrib import admin

from .models import (
    UserProfile,
    StudentProfile,
    CertificateProject,
    SkillCategory,
    Skill,
    MentorshipRequest,
    SkillVerificationRequest,
    VerificationLog,
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "is_locked", "failed_login_attempts", "updated_at")
    list_filter = ("role", "is_locked")
    search_fields = ("user__username", "user__first_name", "user__last_name", "user__email")


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "department", "semester", "session", "cgpa")
    search_fields = ("user__username", "department", "university")


@admin.register(CertificateProject)
class CertificateProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "student_profile", "created_at")
    search_fields = ("title", "student_profile__user__username")


@admin.register(SkillCategory)
class SkillCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "student_profile",
        "category",
        "proficiency_level",
        "verification_status",
        "verified_by",
    )
    list_filter = ("category", "proficiency_level", "verification_status")
    search_fields = ("name", "student_profile__user__username")


@admin.register(MentorshipRequest)
class MentorshipRequestAdmin(admin.ModelAdmin):
    list_display = ("student", "teacher", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("student__username", "teacher__username")


@admin.register(SkillVerificationRequest)
class SkillVerificationRequestAdmin(admin.ModelAdmin):
    list_display = ("skill", "student", "teacher", "status", "requested_at", "responded_at")
    list_filter = ("status",)
    search_fields = ("skill__name", "student__username", "teacher__username")


@admin.register(VerificationLog)
class VerificationLogAdmin(admin.ModelAdmin):
    list_display = ("action", "actor", "student", "teacher", "skill", "created_at")
    list_filter = ("action",)
    search_fields = (
        "actor__username",
        "student__username",
        "teacher__username",
        "skill__name",
    )