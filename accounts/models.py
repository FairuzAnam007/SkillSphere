from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ("student", "Student"),
        ("teacher", "Teacher"),
        ("recruiter", "Recruiter"),
        ("admin", "Admin"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="userprofile"
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="student"
    )
    is_locked = models.BooleanField(default=False)
    failed_login_attempts = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    profile_picture = models.ImageField(
        upload_to="profile_pictures/",
        blank=True,
        null=True
    )
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    university = models.CharField(max_length=150, blank=True)
    department = models.CharField(max_length=100, blank=True)
    semester = models.CharField(max_length=50, blank=True)
    session = models.CharField(max_length=50, blank=True)
    cgpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        blank=True,
        null=True
    )
    bio = models.TextField(blank=True)
    extracurricular_activities = models.TextField(blank=True)
    skills_summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.user.username


class CertificateProject(models.Model):
    student_profile = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="certificates"
    )
    title = models.CharField(max_length=150)
    certificate_file = models.FileField(
        upload_to="certificates/",
        blank=True,
        null=True
    )
    project_link = models.URLField(blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.title


class SkillCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Skill Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Skill(models.Model):
    VERIFICATION_STATUS_CHOICES = [
        ("not_requested", "Not Requested"),
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    PROFICIENCY_LEVEL_CHOICES = [
        ("", "Not Assigned"),
        ("Beginner", "Beginner"),
        ("Intermediate", "Intermediate"),
        ("Advanced", "Advanced"),
        ("Expert", "Expert"),
    ]

    student_profile = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="skills"
    )
    category = models.ForeignKey(
        SkillCategory,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="skills"
    )
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    proof_file = models.FileField(
        upload_to="skill_proofs/",
        blank=True,
        null=True
    )
    proof_link = models.URLField(blank=True)
    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS_CHOICES,
        default="not_requested"
    )
    proficiency_level = models.CharField(
        max_length=20,
        choices=PROFICIENCY_LEVEL_CHOICES,
        blank=True
    )
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="verified_skills"
    )
    verified_at = models.DateTimeField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.student_profile.user.username}"


class MentorshipRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    ]

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_mentorship_requests"
    )
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_mentorship_requests"
    )
    message = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    responded_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ("student", "teacher")
        ordering = ["-created_at"]

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
        related_name="verification_requests"
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_skill_verification_requests"
    )
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_skill_verification_requests"
    )
    message = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )
    feedback = models.TextField(blank=True)
    requested_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    responded_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ("skill", "student", "teacher")
        ordering = ["-requested_at"]

    def __str__(self):
        return f"{self.skill.name} - {self.student.username} - {self.status}"


class VerificationLog(models.Model):
    ACTION_CHOICES = [
        ("mentorship_requested", "Mentorship Requested"),
        ("mentorship_accepted", "Mentorship Accepted"),
        ("mentorship_rejected", "Mentorship Rejected"),
        ("verification_requested", "Verification Requested"),
        ("skill_approved", "Skill Approved"),
        ("skill_rejected", "Skill Rejected"),
    ]

    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    actor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="verification_actions"
    )
    student = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="student_verification_logs"
    )
    teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="teacher_verification_logs"
    )
    skill = models.ForeignKey(
        Skill,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="verification_logs"
    )
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_action_display()} - {self.created_at}"


class RecruiterShortlist(models.Model):
    recruiter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shortlisted_candidates"
    )
    student_profile = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="shortlisted_by_recruiters"
    )
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        unique_together = ("recruiter", "student_profile")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.recruiter.username} shortlisted {self.student_profile.user.username}"


class JobPost(models.Model):
    JOB_TYPE_CHOICES = [
        ("internship", "Internship"),
        ("part_time", "Part Time"),
        ("full_time", "Full Time"),
        ("remote", "Remote"),
    ]

    recruiter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="job_posts"
    )
    title = models.CharField(max_length=200)
    company_name = models.CharField(max_length=150)
    job_type = models.CharField(
        max_length=30,
        choices=JOB_TYPE_CHOICES,
        default="internship"
    )
    location = models.CharField(max_length=150, blank=True)
    description = models.TextField()
    required_skills = models.CharField(
        max_length=255,
        help_text="Example: Python, Django, SQL"
    )
    deadline = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.company_name}"


class JobApplication(models.Model):
    STATUS_CHOICES = [
        ("applied", "Applied"),
        ("reviewing", "Reviewing"),
        ("shortlisted", "Shortlisted"),
        ("rejected", "Rejected"),
        ("accepted", "Accepted"),
    ]

    job = models.ForeignKey(
        JobPost,
        on_delete=models.CASCADE,
        related_name="applications"
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="job_applications"
    )
    cover_letter = models.TextField(blank=True)
    cv_file = models.FileField(
        upload_to="job_applications/cv/",
        blank=True,
        null=True
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="applied"
    )
    recruiter_note = models.TextField(blank=True)
    applied_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("job", "student")
        ordering = ["-applied_at"]

    def __str__(self):
        return f"{self.student.username} applied for {self.job.title}"