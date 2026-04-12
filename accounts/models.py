from django.db import models
from django.contrib.auth.models import User


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