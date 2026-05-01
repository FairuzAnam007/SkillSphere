from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

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


class SprintUnitTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            username="student1",
            password="TestPass123!",
            email="student1@example.com",
            first_name="Fairuz",
            last_name="Anam",
        )

        UserProfile.objects.update_or_create(
            user=self.student,
            defaults={
                "role": "student",
                "is_locked": False,
                "failed_login_attempts": 0,
            },
        )

        self.student_profile, created = StudentProfile.objects.get_or_create(
            user=self.student
        )

        self.teacher = User.objects.create_user(
            username="teacher1",
            password="TestPass123!",
            email="teacher1@example.com",
            first_name="Teacher",
            last_name="One",
        )

        UserProfile.objects.update_or_create(
            user=self.teacher,
            defaults={
                "role": "teacher",
                "is_locked": False,
                "failed_login_attempts": 0,
            },
        )

        self.category, created = SkillCategory.objects.get_or_create(
            name="Programming",
            defaults={"description": "Coding and software development"},
        )

    def login_student(self):
        return self.client.login(username="student1", password="TestPass123!")

    def login_teacher(self):
        return self.client.login(username="teacher1", password="TestPass123!")

    def test_user_profile_created_by_signal(self):
        user = User.objects.create_user(
            username="newuser",
            password="TestPass123!",
        )

        self.assertTrue(UserProfile.objects.filter(user=user).exists())

    def test_student_profile_creation(self):
        profile = StudentProfile.objects.get(user=self.student)

        self.assertEqual(profile.user.username, "student1")
        self.assertEqual(profile.full_name(), "Fairuz Anam")

    def test_student_dashboard_requires_login(self):
        response = self.client.get(reverse("student_dashboard"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_student_dashboard_loads_for_student(self):
        self.login_student()

        response = self.client.get(reverse("student_dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/student_dashboard.html")

    def test_teacher_dashboard_loads_for_teacher(self):
        self.login_teacher()

        response = self.client.get(reverse("teacher_dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/teacher_dashboard.html")

    def test_student_cannot_access_teacher_dashboard(self):
        self.login_student()

        response = self.client.get(reverse("teacher_dashboard"))

        self.assertEqual(response.status_code, 403)

    def test_teacher_cannot_access_student_dashboard(self):
        self.login_teacher()

        response = self.client.get(reverse("student_dashboard"))

        self.assertEqual(response.status_code, 403)

    def test_update_student_profile(self):
        self.login_student()

        response = self.client.post(
            reverse("update_student_profile"),
            {
                "phone_number": "01952595185",
                "address": "Pathapath",
                "date_of_birth": "2002-01-01",
                "university": "University Of Asia Pacific",
                "department": "CSE",
                "semester": "3rd",
                "session": "2nd",
                "cgpa": "3.81",
                "bio": "Student bio",
                "extracurricular_activities": "Leadership",
                "skills_summary": "Coding",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.student_profile.refresh_from_db()
        self.assertEqual(self.student_profile.phone_number, "01952595185")
        self.assertEqual(self.student_profile.department, "CSE")

    def test_upload_certificate_project(self):
        self.login_student()

        certificate = SimpleUploadedFile(
            "certificate.pdf",
            b"dummy certificate content",
            content_type="application/pdf",
        )

        response = self.client.post(
            reverse("upload_certificate_project"),
            {
                "title": "Django Certificate",
                "certificate_file": certificate,
                "project_link": "https://example.com/project",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            CertificateProject.objects.filter(
                student_profile=self.student_profile,
                title="Django Certificate",
            ).exists()
        )

    def test_delete_certificate_project(self):
        self.login_student()

        certificate = CertificateProject.objects.create(
            student_profile=self.student_profile,
            title="Test Certificate",
            project_link="https://example.com",
        )

        response = self.client.post(
            reverse("delete_certificate_project", args=[certificate.pk])
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(CertificateProject.objects.filter(pk=certificate.pk).exists())

    def test_add_skill(self):
        self.login_student()

        response = self.client.post(
            reverse("add_skill"),
            {
                "name": "Python",
                "category": self.category.pk,
                "description": "Python programming skill",
                "proof_link": "https://example.com/python-proof",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Skill.objects.filter(
                student_profile=self.student_profile,
                name="Python",
            ).exists()
        )

    def test_edit_skill(self):
        self.login_student()

        skill = Skill.objects.create(
            student_profile=self.student_profile,
            category=self.category,
            name="Python",
            description="Old description",
            proof_link="https://example.com/old",
        )

        response = self.client.post(
            reverse("edit_skill", args=[skill.pk]),
            {
                "name": "Python Advanced",
                "category": self.category.pk,
                "description": "Updated description",
                "proof_link": "https://example.com/new",
            },
        )

        self.assertEqual(response.status_code, 302)
        skill.refresh_from_db()
        self.assertEqual(skill.name, "Python Advanced")
        self.assertEqual(skill.verification_status, "not_requested")

    def test_delete_skill(self):
        self.login_student()

        skill = Skill.objects.create(
            student_profile=self.student_profile,
            category=self.category,
            name="Python",
        )

        response = self.client.post(reverse("delete_skill", args=[skill.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Skill.objects.filter(pk=skill.pk).exists())

    def test_student_can_send_mentorship_request(self):
        self.login_student()

        response = self.client.post(
            reverse("request_teacher_connection"),
            {
                "teacher": self.teacher.pk,
                "message": "I want mentoring for my skills.",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            MentorshipRequest.objects.filter(
                student=self.student,
                teacher=self.teacher,
                status="pending",
            ).exists()
        )

    def test_teacher_can_accept_mentorship_request(self):
        request_obj = MentorshipRequest.objects.create(
            student=self.student,
            teacher=self.teacher,
            message="Please mentor me.",
            status="pending",
        )

        self.login_teacher()

        response = self.client.post(
            reverse("respond_mentorship_request", args=[request_obj.pk, "accept"])
        )

        self.assertEqual(response.status_code, 302)
        request_obj.refresh_from_db()
        self.assertEqual(request_obj.status, "accepted")

    def test_student_can_request_skill_verification_after_connection(self):
        MentorshipRequest.objects.create(
            student=self.student,
            teacher=self.teacher,
            status="accepted",
        )

        skill = Skill.objects.create(
            student_profile=self.student_profile,
            category=self.category,
            name="Python",
            description="Python programming",
            proof_link="https://example.com/proof",
        )

        self.login_student()

        response = self.client.post(
            reverse("request_skill_verification", args=[skill.pk]),
            {
                "teacher": self.teacher.pk,
                "message": "Please verify my Python skill.",
            },
        )

        self.assertEqual(response.status_code, 302)

        skill.refresh_from_db()
        self.assertEqual(skill.verification_status, "pending")

        self.assertTrue(
            SkillVerificationRequest.objects.filter(
                skill=skill,
                student=self.student,
                teacher=self.teacher,
                status="pending",
            ).exists()
        )

    def test_teacher_can_approve_skill_verification(self):
        MentorshipRequest.objects.create(
            student=self.student,
            teacher=self.teacher,
            status="accepted",
        )

        skill = Skill.objects.create(
            student_profile=self.student_profile,
            category=self.category,
            name="Python",
            verification_status="pending",
        )

        verification_request = SkillVerificationRequest.objects.create(
            skill=skill,
            student=self.student,
            teacher=self.teacher,
            status="pending",
            message="Please approve.",
        )

        self.login_teacher()

        response = self.client.post(
            reverse("approve_skill_verification", args=[verification_request.pk]),
            {
                "proficiency_level": "advanced",
                "feedback": "Good work.",
            },
        )

        self.assertEqual(response.status_code, 302)

        skill.refresh_from_db()
        verification_request.refresh_from_db()

        self.assertEqual(skill.verification_status, "approved")
        self.assertEqual(skill.proficiency_level, "advanced")
        self.assertEqual(skill.verified_by, self.teacher)
        self.assertEqual(verification_request.status, "approved")

    def test_teacher_can_reject_skill_verification(self):
        skill = Skill.objects.create(
            student_profile=self.student_profile,
            category=self.category,
            name="Networking",
            verification_status="pending",
        )

        verification_request = SkillVerificationRequest.objects.create(
            skill=skill,
            student=self.student,
            teacher=self.teacher,
            status="pending",
        )

        self.login_teacher()

        response = self.client.post(
            reverse("reject_skill_verification", args=[verification_request.pk]),
            {
                "rejection_reason": "Proof is not clear.",
            },
        )

        self.assertEqual(response.status_code, 302)

        skill.refresh_from_db()
        verification_request.refresh_from_db()

        self.assertEqual(skill.verification_status, "rejected")
        self.assertEqual(skill.rejection_reason, "Proof is not clear.")
        self.assertEqual(verification_request.status, "rejected")

    def test_verification_log_created_for_mentorship_request(self):
        self.login_student()

        self.client.post(
            reverse("request_teacher_connection"),
            {
                "teacher": self.teacher.pk,
                "message": "Need mentoring.",
            },
        )

        self.assertTrue(
            VerificationLog.objects.filter(
                action="mentorship_requested",
                student=self.student,
                teacher=self.teacher,
            ).exists()
        )