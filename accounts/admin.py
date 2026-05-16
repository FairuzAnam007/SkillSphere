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
    JobPost,
    JobApplication,
    SkillEnrollment,
    ConversationMessage,
    Notification,
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
        "created_at",
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


@admin.register(JobPost)
class JobPostAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "company_name",
        "job_type",
        "recruiter",
        "is_active",
        "deadline",
        "created_at",
    )

    search_fields = (
        "title",
        "company_name",
        "required_skills",
        "recruiter__username",
    )

    list_filter = (
        "job_type",
        "is_active",
        "deadline",
        "created_at",
    )


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "job",
        "student",
        "status",
        "applied_at",
        "updated_at",
    )

    search_fields = (
        "job__title",
        "job__company_name",
        "student__username",
        "student__first_name",
        "student__last_name",
    )

    list_filter = (
        "status",
        "applied_at",
        "updated_at",
    )


@admin.register(SkillEnrollment)
class SkillEnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "skill_title",
        "student_name",
        "mentor",
        "status",
        "progress",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "skill_title",
        "description",
        "student_profile__user__username",
        "student_profile__user__first_name",
        "student_profile__user__last_name",
        "mentor__username",
        "mentor__first_name",
        "mentor__last_name",
    )

    list_filter = (
        "status",
        "progress",
        "created_at",
        "updated_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "verified_at",
    )

    def student_name(self, obj):
        user = obj.student_profile.user

        full_name = f"{user.first_name} {user.last_name}".strip()

        return full_name or user.username

    student_name.short_description = "Student"

    @admin.register(ConversationMessage)
    class ConversationMessageAdmin(admin.ModelAdmin):
        list_display = (
            "id",
            "sender",
            "receiver",
            "subject",
            "is_read",
            "created_at",
        )

        search_fields = (
            "sender__username",
            "receiver__username",
            "subject",
            "message",
        )

        list_filter = (
            "is_read",
            "created_at",
        )

    @admin.register(Notification)
    class NotificationAdmin(admin.ModelAdmin):
        list_display = (
            "id",
            "user",
            "title",
            "notification_type",
            "is_read",
            "created_at",
        )

        search_fields = (
            "user__username",
            "title",
            "message",
        )

        list_filter = (
            "notification_type",
            "is_read",
            "created_at",
        )
