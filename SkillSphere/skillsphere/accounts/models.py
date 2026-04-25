from django.db import models
from django.contrib.auth.models import User


# ==================== USER & PROFILE ====================

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('recruiter', 'Recruiter'),
        ('admin', 'Admin'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    is_locked = models.BooleanField(default=False)
    failed_login_attempts = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')

    profile_picture = models.ImageField(upload_to='student_pictures/', blank=True, null=True)

    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    bio = models.TextField(blank=True)

    university = models.CharField(max_length=150, blank=True)
    department = models.CharField(max_length=150, blank=True)
    semester = models.CharField(max_length=50, blank=True)
    session = models.CharField(max_length=50, blank=True)
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)

    extracurricular_activities = models.TextField(blank=True)
    skills_summary = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} Student Profile"


class CertificateProject(models.Model):
    student_profile = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='certificates_projects'
    )
    title = models.CharField(max_length=200)
    certificate_file = models.FileField(upload_to='certificates/', blank=True, null=True)
    project_link = models.URLField(blank=True)
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# ==================== STORY 4: SKILL VERIFICATION ====================

class Skill(models.Model):
    """Master list of skills (e.g., Python, Django, React)."""
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50, blank=True)  # e.g., Programming, Design
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class SkillVerificationRequest(models.Model):
    """SCRUM-40, 41, 42, 43 — student requests, teacher approves/rejects."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    PROFICIENCY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]

    student = models.ForeignKey(
        StudentProfile, on_delete=models.CASCADE,
        related_name='verification_requests'
    )
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)

    # Proof (one of these must be present — validated in form)
    certificate = models.ForeignKey(
        CertificateProject, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    proof_description = models.TextField(blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    proficiency_level = models.CharField(
        max_length=20, choices=PROFICIENCY_CHOICES, blank=True
    )  # SCRUM-43 — set when approved
    rejection_reason = models.TextField(blank=True)  # SCRUM-42 — set when rejected

    verifier = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='verified_skills'
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        # SCRUM-40: prevent duplicate active requests for the same skill
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'skill'],
                condition=models.Q(status__in=['pending', 'approved']),
                name='unique_active_skill_request'
            )
        ]

    def __str__(self):
        return f"{self.student.user.username} - {self.skill.name} ({self.status})"


class VerificationLog(models.Model):
    """SCRUM-45 — audit trail for every verification action."""

    ACTION_CHOICES = [
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    request = models.ForeignKey(
        SkillVerificationRequest, on_delete=models.CASCADE,
        related_name='logs'
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    note = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.action} - {self.request.skill.name} @ {self.timestamp}"