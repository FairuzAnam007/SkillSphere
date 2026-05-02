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
    RecruiterShortlist,
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "role",
        "is_locked",
        "failed_login_attempts",
    )

    list_filter = (
        "role",
        "is_locked",
    )

    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__email",
    )


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "department",
        "semester",
        "session",
        "cgpa",
    )

    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "department",
        "university",
    )

    list_filter = (
        "department",
        "semester",
        "session",
    )


@admin.register(CertificateProject)
class CertificateProjectAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "student_profile",
        "created_at",
    )

    search_fields = (
        "title",
        "student_profile__user__username",
        "student_profile__user__first_name",
        "student_profile__user__last_name",
    )

    list_filter = (
        "created_at",
    )


@admin.register(SkillCategory)
class SkillCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "description",
    )

    search_fields = (
        "name",
        "description",
    )


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "student_profile",
        "category",
        "verification_status",
        "proficiency_level",
        "verified_by",
        "created_at",
    )

    search_fields = (
        "name",
        "description",
        "student_profile__user__username",
        "student_profile__user__first_name",
        "student_profile__user__last_name",
    )

    list_filter = (
        "category",
        "verification_status",
        "proficiency_level",
        "created_at",
    )


@admin.register(MentorshipRequest)
class MentorshipRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "student",
        "teacher",
        "status",
        "created_at",
        "responded_at",
    )

    search_fields = (
        "student__username",
        "student__first_name",
        "student__last_name",
        "teacher__username",
        "teacher__first_name",
        "teacher__last_name",
    )

    list_filter = (
        "status",
        "created_at",
        "responded_at",
    )


@admin.register(SkillVerificationRequest)
class SkillVerificationRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "student",
        "teacher",
        "skill",
        "status",
        "requested_at",
        "responded_at",
    )

    search_fields = (
        "student__username",
        "student__first_name",
        "student__last_name",
        "teacher__username",
        "teacher__first_name",
        "teacher__last_name",
        "skill__name",
    )

    list_filter = (
        "status",
        "requested_at",
        "responded_at",
    )


@admin.register(VerificationLog)
class VerificationLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "action",
        "actor",
        "student",
        "teacher",
        "skill",
        "created_at",
    )

    search_fields = (
        "actor__username",
        "student__username",
        "teacher__username",
        "skill__name",
        "note",
    )

    list_filter = (
        "action",
        "created_at",
    )


@admin.register(RecruiterShortlist)
class RecruiterShortlistAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "recruiter_name",
        "candidate_name",
        "created_at_safe",
    )

    search_fields = (
        "recruiter__username",
        "recruiter__first_name",
        "recruiter__last_name",
        "student_profile__user__username",
        "student_profile__user__first_name",
        "student_profile__user__last_name",
    )

    def recruiter_name(self, obj):
        return obj.recruiter.username if obj.recruiter else "N/A"

    recruiter_name.short_description = "Recruiter"

    def candidate_name(self, obj):
        if obj.student_profile and obj.student_profile.user:
            user = obj.student_profile.user
            full_name = f"{user.first_name} {user.last_name}".strip()
            return full_name or user.username
        return "N/A"

    candidate_name.short_description = "Candidate"

    def created_at_safe(self, obj):
        return getattr(obj, "created_at", "N/A")

    created_at_safe.short_description = "Created At"