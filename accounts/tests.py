from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

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


class SkillSphereSprintUnitTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            username="student1",
            password="TestPass123!",
            email="student1@example.com",
            first_name="Fairuz",
            last_name="Anam",
        )

        self.teacher = User.objects.create_user(
            username="teacher1",
            password="TestPass123!",
            email="teacher1@example.com",
            first_name="Teacher",
            last_name="One",
        )

        self.recruiter = User.objects.create_user(
            username="recruiter1",
            password="TestPass123!",
            email="recruiter1@example.com",
        )

        UserProfile.objects.update_or_create(
            user=self.student,
            defaults={
                "role": "student",
                "is_locked": False,
                "failed_login_attempts": 0,
            },
        )

        UserProfile.objects.update_or_create(
            user=self.teacher,
            defaults={
                "role": "teacher",
                "is_locked": False,
                "failed_login_attempts": 0,
            },
        )

        UserProfile.objects.update_or_create(
            user=self.recruiter,
            defaults={
                "role": "recruiter",
                "is_locked": False,
                "failed_login_attempts": 0,
            },
        )

        self.student_profile, created = StudentProfile.objects.get_or_create(
            user=self.student
        )

        self.category, created = SkillCategory.objects.get_or_create(
            name="Programming",
            defaults={
                "description": "Coding, software development, and programming skills"
            },
        )

    # =========================
    # Sprint 1: Authentication
    # =========================

    def test_signup_page_loads(self):
        response = self.client.get(reverse("signup"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Join SkillSphere")

    def test_login_page_loads(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Login to SkillSphere")

    def test_valid_login_redirects_to_role_redirect(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "student1",
                "password": "TestPass123!",
            },
        )
        self.assertEqual(response.status_code, 302)

    def test_invalid_login_shows_error(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "student1",
                "password": "WrongPassword",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username or password.")

    def test_role_redirect_for_student(self):
        self.client.login(username="student1", password="TestPass123!")
        response = self.client.get(reverse("role_redirect"))
        self.assertRedirects(response, reverse("student_dashboard"))

    def test_role_redirect_for_teacher(self):
        self.client.login(username="teacher1", password="TestPass123!")
        response = self.client.get(reverse("role_redirect"))
        self.assertRedirects(response, reverse("teacher_dashboard"))

    def test_student_cannot_access_teacher_dashboard(self):
        self.client.login(username="student1", password="TestPass123!")
        response = self.client.get(reverse("teacher_dashboard"))
        self.assertIn(response.status_code, [302, 403])

    def test_teacher_cannot_access_student_dashboard(self):
        self.client.login(username="teacher1", password="TestPass123!")
        response = self.client.get(reverse("student_dashboard"))
        self.assertIn(response.status_code, [302, 403])

    def test_password_reset_page_loads(self):
        response = self.client.get(reverse("password_reset"))
        self.assertEqual(response.status_code, 200)

    # ===============================
    # Sprint 2: Student Profile System
    # ===============================

    def test_student_dashboard_loads(self):
        self.client.login(username="student1", password="TestPass123!")
        response = self.client.get(reverse("student_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Student Dashboard")

    def test_create_student_profile_page_loads(self):
        self.client.login(username="student1", password="TestPass123!")
        response = self.client.get(reverse("create_student_profile"))
        self.assertEqual(response.status_code, 200)

    def test_update_student_profile_page_loads(self):
        self.client.login(username="student1", password="TestPass123!")
        response = self.client.get(reverse("update_student_profile"))
        self.assertEqual(response.status_code, 200)

    def test_update_student_profile_data(self):
        self.client.login(username="student1", password="TestPass123!")

        response = self.client.post(
            reverse("update_student_profile"),
            {
                "phone_number": "01952595185",
                "address": "Pathapath",
                "dob": "2002-01-01",
                "university": "University Of Asia Pacific",
                "department": "CSE",
                "semester": "3rd",
                "session": "2nd",
                "cgpa": "3.81",
                "bio": "I am a CSE student.",
                "extracurricular_activities": "Leadership",
                "skills_summary": "Coding",
            },
        )

        self.assertEqual(response.status_code, 302)

        self.student_profile.refresh_from_db()
        self.assertEqual(self.student_profile.phone_number, "01952595185")
        self.assertEqual(self.student_profile.address, "Pathapath")
        self.assertEqual(self.student_profile.university, "University Of Asia Pacific")
        self.assertEqual(self.student_profile.department, "CSE")
        self.assertEqual(str(self.student_profile.cgpa), "3.81")

    def test_upload_certificate_page_loads(self):
        self.client.login(username="student1", password="TestPass123!")
        response = self.client.get(reverse("upload_certificate_project"))
        self.assertEqual(response.status_code, 200)

    def test_upload_certificate_project(self):
        self.client.login(username="student1", password="TestPass123!")

        test_file = SimpleUploadedFile(
            "certificate.pdf",
            b"dummy certificate content",
            content_type="application/pdf",
        )

        response = self.client.post(
            reverse("upload_certificate_project"),
            {
                "title": "Python Certificate",
                "description": "Completed Python basics.",
                "certificate_file": test_file,
                "project_link": "https://github.com/example/project",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            CertificateProject.objects.filter(
                student_profile=self.student_profile,
                title="Python Certificate",
            ).exists()
        )

    def test_delete_certificate_project(self):
        self.client.login(username="student1", password="TestPass123!")

        certificate = CertificateProject.objects.create(
            student_profile=self.student_profile,
            title="Delete Test Certificate",
            description="Testing delete feature.",
            project_link="https://github.com/example/delete-test",
        )

        response = self.client.post(
            reverse("delete_certificate_project", args=[certificate.pk])
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            CertificateProject.objects.filter(pk=certificate.pk).exists()
        )

    # =========================
    # Sprint 3: Skill Management
    # =========================

    def test_skill_category_created(self):
        self.assertEqual(self.category.name, "Programming")

    def test_add_skill_page_loads(self):
        self.client.login(username="student1", password="TestPass123!")
        response = self.client.get(reverse("add_skill"))
        self.assertEqual(response.status_code, 200)

    def test_add_skill(self):
        self.client.login(username="student1", password="TestPass123!")

        response = self.client.post(
            reverse("add_skill"),
            {
                "name": "Python",
                "category": self.category.pk,
                "description": "Python programming skill.",
                "proof_link": "https://github.com/example/python",
            },
        )

        self.assertEqual(response.status_code, 302)

        skill = Skill.objects.get(name="Python")
        self.assertEqual(skill.student_profile, self.student_profile)
        self.assertEqual(skill.category, self.category)
        self.assertEqual(skill.verification_status, "not_requested")

    def test_edit_skill(self):
        self.client.login(username="student1", password="TestPass123!")

        skill = Skill.objects.create(
            student_profile=self.student_profile,
            name="Python",
            category=self.category,
            description="Old description",
            proof_link="https://github.com/example/old",
            verification_status="not_requested",
        )

        response = self.client.post(
            reverse("edit_skill", args=[skill.pk]),
            {
                "name": "Advanced Python",
                "category": self.category.pk,
                "description": "Updated description",
                "proof_link": "https://github.com/example/new",
            },
        )

        self.assertEqual(response.status_code, 302)

        skill.refresh_from_db()
        self.assertEqual(skill.name, "Advanced Python")
        self.assertEqual(skill.description, "Updated description")

    def test_delete_skill(self):
        self.client.login(username="student1", password="TestPass123!")

        skill = Skill.objects.create(
            student_profile=self.student_profile,
            name="Delete Skill",
            category=self.category,
            description="Skill for delete test",
            verification_status="not_requested",
        )

        response = self.client.post(reverse("delete_skill", args=[skill.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Skill.objects.filter(pk=skill.pk).exists())

    def test_approved_skill_cannot_be_edited(self):
        self.client.login(username="student1", password="TestPass123!")

        skill = Skill.objects.create(
            student_profile=self.student_profile,
            name="Verified Python",
            category=self.category,
            description="Approved skill",
            verification_status="approved",
            proficiency_level="Advanced",
            verified_by=self.teacher,
            verified_at=timezone.now(),
        )

        response = self.client.post(
            reverse("edit_skill", args=[skill.pk]),
            {
                "name": "Changed Name",
                "category": self.category.pk,
                "description": "Changed description",
            },
        )

        self.assertEqual(response.status_code, 302)

        skill.refresh_from_db()
        self.assertEqual(skill.name, "Verified Python")

    # =================================
    # Sprint 4: Skill Verification Flow
    # =================================

    def test_request_teacher_connection_page_loads(self):
        self.client.login(username="student1", password="TestPass123!")
        response = self.client.get(reverse("request_teacher_connection"))
        self.assertEqual(response.status_code, 200)

    def test_student_can_request_teacher_connection(self):
        self.client.login(username="student1", password="TestPass123!")

        response = self.client.post(
            reverse("request_teacher_connection"),
            {
                "teacher": self.teacher.pk,
                "message": "Please mentor me.",
            },
        )

        self.assertEqual(response.status_code, 302)

        request_exists = MentorshipRequest.objects.filter(
            student=self.student,
            teacher=self.teacher,
            status="pending",
        ).exists()

        self.assertTrue(request_exists)

    def test_teacher_dashboard_loads(self):
        self.client.login(username="teacher1", password="TestPass123!")
        response = self.client.get(reverse("teacher_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Teacher Dashboard")

    def test_teacher_can_accept_mentorship_request(self):
        mentorship_request = MentorshipRequest.objects.create(
            student=self.student,
            teacher=self.teacher,
            message="Please mentor me.",
            status="pending",
        )

        self.client.login(username="teacher1", password="TestPass123!")

        response = self.client.post(
            reverse(
                "respond_mentorship_request",
                args=[mentorship_request.pk, "accept"],
            )
        )

        self.assertEqual(response.status_code, 302)

        mentorship_request.refresh_from_db()
        self.assertEqual(mentorship_request.status, "accepted")
        self.assertIsNotNone(mentorship_request.responded_at)

    def test_teacher_can_reject_mentorship_request(self):
        mentorship_request = MentorshipRequest.objects.create(
            student=self.student,
            teacher=self.teacher,
            message="Please mentor me.",
            status="pending",
        )

        self.client.login(username="teacher1", password="TestPass123!")

        response = self.client.post(
            reverse(
                "respond_mentorship_request",
                args=[mentorship_request.pk, "reject"],
            )
        )

        self.assertEqual(response.status_code, 302)

        mentorship_request.refresh_from_db()
        self.assertEqual(mentorship_request.status, "rejected")

    def test_student_cannot_request_skill_verification_without_teacher_connection(self):
        self.client.login(username="student1", password="TestPass123!")

        skill = Skill.objects.create(
            student_profile=self.student_profile,
            name="Python",
            category=self.category,
            description="Python programming",
            verification_status="not_requested",
        )

        response = self.client.get(
            reverse("request_skill_verification", args=[skill.pk])
        )

        self.assertEqual(response.status_code, 302)

    def test_student_can_request_skill_verification_after_teacher_connection(self):
        MentorshipRequest.objects.create(
            student=self.student,
            teacher=self.teacher,
            message="Please mentor me.",
            status="accepted",
            responded_at=timezone.now(),
        )

        skill = Skill.objects.create(
            student_profile=self.student_profile,
            name="Python",
            category=self.category,
            description="Python programming",
            proof_link="https://github.com/example/python",
            verification_status="not_requested",
        )

        self.client.login(username="student1", password="TestPass123!")

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
            responded_at=timezone.now(),
        )

        skill = Skill.objects.create(
            student_profile=self.student_profile,
            name="Python",
            category=self.category,
            description="Python programming",
            verification_status="pending",
        )

        verification_request = SkillVerificationRequest.objects.create(
            skill=skill,
            student=self.student,
            teacher=self.teacher,
            message="Please verify.",
            status="pending",
        )

        self.client.login(username="teacher1", password="TestPass123!")

        response = self.client.post(
            reverse("approve_skill_verification", args=[verification_request.pk]),
            {
                "proficiency_level": "Advanced",
                "feedback": "Good work.",
            },
        )

        self.assertEqual(response.status_code, 302)

        skill.refresh_from_db()
        verification_request.refresh_from_db()

        self.assertEqual(skill.verification_status, "approved")
        self.assertEqual(skill.proficiency_level, "Advanced")
        self.assertEqual(skill.verified_by, self.teacher)
        self.assertIsNotNone(skill.verified_at)

        self.assertEqual(verification_request.status, "approved")

    def test_teacher_can_reject_skill_verification(self):
        MentorshipRequest.objects.create(
            student=self.student,
            teacher=self.teacher,
            status="accepted",
            responded_at=timezone.now(),
        )

        skill = Skill.objects.create(
            student_profile=self.student_profile,
            name="Python",
            category=self.category,
            description="Python programming",
            verification_status="pending",
        )

        verification_request = SkillVerificationRequest.objects.create(
            skill=skill,
            student=self.student,
            teacher=self.teacher,
            message="Please verify.",
            status="pending",
        )

        self.client.login(username="teacher1", password="TestPass123!")

        response = self.client.post(
            reverse("reject_skill_verification", args=[verification_request.pk]),
            {
                "rejection_reason": "Need stronger proof.",
            },
        )

        self.assertEqual(response.status_code, 302)

        skill.refresh_from_db()
        verification_request.refresh_from_db()

        self.assertEqual(skill.verification_status, "rejected")
        self.assertEqual(skill.rejection_reason, "Need stronger proof.")
        self.assertEqual(verification_request.status, "rejected")
        self.assertEqual(verification_request.feedback, "Need stronger proof.")

    def test_verification_log_created_for_mentorship_request(self):
        self.client.login(username="student1", password="TestPass123!")

        self.client.post(
            reverse("request_teacher_connection"),
            {
                "teacher": self.teacher.pk,
                "message": "Please mentor me.",
            },
        )

        self.assertTrue(
            VerificationLog.objects.filter(
                action="mentorship_requested",
                student=self.student,
                teacher=self.teacher,
            ).exists()
        )

    def test_verified_badge_data_for_approved_skill(self):
        skill = Skill.objects.create(
            student_profile=self.student_profile,
            name="Python",
            category=self.category,
            description="Python programming",
            verification_status="approved",
            proficiency_level="Advanced",
            verified_by=self.teacher,
            verified_at=timezone.now(),
        )

        self.assertEqual(skill.verification_status, "approved")
        self.assertEqual(skill.proficiency_level, "Advanced")
        self.assertEqual(skill.verified_by.username, "teacher1")