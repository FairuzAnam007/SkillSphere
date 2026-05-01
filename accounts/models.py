from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.utils import timezone


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ("student", "Student"),
        ("teacher", "Teacher"),
        ("recruiter", "Recruiter"),
        ("admin", "Admin"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="userprofile")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="student")
    is_locked = models.BooleanField(default=False)
    failed_login_attempts = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="studentprofile")

    profile_picture = models.ImageField(
        upload_to="profile_pictures/",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp"])],
    )

    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(blank=True, null=True)

    university = models.CharField(max_length=150, blank=True)
    department = models.CharField(max_length=100, blank=True)
    semester = models.CharField(max_length=50, blank=True)
    session = models.CharField(max_length=50, blank=True)
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)

    bio = models.TextField(blank=True)
    extracurricular_activities = models.TextField(blank=True)
    skills_summary = models.TextField(blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def full_name(self):
        name = f"{self.user.first_name} {self.user.last_name}".strip()
        return name if name else self.user.username

    def __str__(self):
        return self.full_name()


class CertificateProject(models.Model):
    student_profile = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="certificates",
    )

    title = models.CharField(max_length=150)

    certificate_file = models.FileField(
        upload_to="certificates/",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(["pdf", "jpg", "jpeg", "png"])],
    )

    project_link = models.URLField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.title} - {self.student_profile.full_name()}"


class SkillCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name_plural = "Skill Categories"

    def __str__(self):
        return self.name


class Skill(models.Model):
    PROFICIENCY_CHOICES = [
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
        ("expert", "Expert"),
    ]

    VERIFICATION_STATUS_CHOICES = [
        ("not_requested", "Not Requested"),
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    student_profile = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="skills",
    )

    category = models.ForeignKey(
        SkillCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="skills",
    )

    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)

    proof_file = models.FileField(
        upload_to="skill_proofs/",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(["pdf", "jpg", "jpeg", "png"])],
    )

    proof_link = models.URLField(blank=True)

    proficiency_level = models.CharField(
        max_length=20,
        choices=PROFICIENCY_CHOICES,
        blank=True,
    )

    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS_CHOICES,
        default="not_requested",
    )

    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_skills",
    )

    verified_at = models.DateTimeField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_verified(self):
        return self.verification_status == "approved"

    def __str__(self):
        return f"{self.name} - {self.student_profile.full_name()}"


class MentorshipRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    ]

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_mentorship_requests",
    )

    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_mentorship_requests",
    )

    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    created_at = models.DateTimeField(default=timezone.now)
    responded_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ("student", "teacher")

    def __str__(self):
        return f"{self.student.username} to {self.teacher.username} - {self.status}"


class SkillVerificationRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name="verification_requests",
    )

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_skill_verification_requests",
    )

    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_skill_verification_requests",
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    message = models.TextField(blank=True)
    feedback = models.TextField(blank=True)

    requested_at = models.DateTimeField(default=timezone.now)
    responded_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.skill.name} - {self.student.username} - {self.teacher.username}"


class VerificationLog(models.Model):
    ACTION_CHOICES = [
        ("mentorship_requested", "Mentorship Requested"),
        ("mentorship_accepted", "Mentorship Accepted"),
        ("mentorship_rejected", "Mentorship Rejected"),
        ("verification_requested", "Verification Requested"),
        ("skill_approved", "Skill Approved"),
        ("skill_rejected", "Skill Rejected"),
    ]

    action = models.CharField(max_length=40, choices=ACTION_CHOICES)

    actor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="verification_actions",
    )

    student = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="student_verification_logs",
    )

    teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="teacher_verification_logs",
    )

    skill = models.ForeignKey(
        Skill,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="logs",
    )

    note = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.action} - {self.created_at}"