from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import UserProfile, StudentProfile, CertificateProject


class SprintOneTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            username='student1',
            password='TestPass123!',
            email='student1@example.com'
        )
        UserProfile.objects.update_or_create(
            user=self.student,
            defaults={'role': 'student', 'is_locked': False, 'failed_login_attempts': 0}
        )

    def test_login_page_loads(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_login_success(self):
        response = self.client.post(
            reverse('login'),
            {'username': 'student1', 'password': 'TestPass123!'},
            follow=True
        )
        self.assertRedirects(response, reverse('student_dashboard'))

    def test_invalid_login_shows_error(self):
        response = self.client.post(reverse('login'), {
            'username': 'student1',
            'password': 'WrongPassword',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username or password.")

    def test_failed_attempt_count_increases(self):
        self.client.post(reverse('login'), {
            'username': 'student1',
            'password': 'WrongPassword',
        })
        profile = UserProfile.objects.get(user=self.student)
        self.assertEqual(profile.failed_login_attempts, 1)

    def test_account_locks_after_three_attempts(self):
        for _ in range(3):
            self.client.post(reverse('login'), {
                'username': 'student1',
                'password': 'WrongPassword',
            })
        profile = UserProfile.objects.get(user=self.student)
        self.assertTrue(profile.is_locked)
        self.assertEqual(profile.failed_login_attempts, 3)

    def test_locked_user_cannot_login(self):
        profile = UserProfile.objects.get(user=self.student)
        profile.is_locked = True
        profile.save()

        response = self.client.post(reverse('login'), {
            'username': 'student1',
            'password': 'TestPass123!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This account is locked. Please contact admin.")

    def test_password_reset_page_loads(self):
        response = self.client.get(reverse('password_reset'))
        self.assertEqual(response.status_code, 200)

    def test_password_reset_email_sent(self):
        response = self.client.post(reverse('password_reset'), {
            'email': 'student1@example.com'
        })
        self.assertRedirects(response, reverse('password_reset_done'))
        self.assertEqual(len(mail.outbox), 1)


class SprintTwoTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            username='student1',
            password='TestPass123!',
            email='student1@example.com'
        )
        self.teacher = User.objects.create_user(
            username='teacher1',
            password='TestPass123!',
            email='teacher1@example.com'
        )
        UserProfile.objects.update_or_create(user=self.student, defaults={'role': 'student'})
        UserProfile.objects.update_or_create(user=self.teacher, defaults={'role': 'teacher'})

    def test_create_student_profile(self):
        self.client.login(username='student1', password='TestPass123!')
        response = self.client.post(reverse('create_student_profile'), {
            'phone': '01700000000',
            'address': 'Dhaka',
            'date_of_birth': '2003-01-01',
            'bio': 'CSE student',
            'university': 'UAP',
            'department': 'CSE',
            'semester': '3.2',
            'session': '2023-24',
            'cgpa': '3.75',
            'extracurricular_activities': 'Debate',
            'skills_summary': 'Python, Django',
        })
        self.assertRedirects(response, reverse('student_dashboard'))
        self.assertEqual(StudentProfile.objects.count(), 1)

    def test_update_student_profile(self):
        StudentProfile.objects.create(user=self.student, phone='01700000000', university='UAP')
        self.client.login(username='student1', password='TestPass123!')

        response = self.client.post(reverse('update_student_profile'), {
            'phone': '01811111111',
            'address': 'Dhaka',
            'date_of_birth': '2003-01-01',
            'bio': 'Updated bio',
            'university': 'UAP',
            'department': 'CSE',
            'semester': '3.2',
            'session': '2023-24',
            'cgpa': '3.90',
            'extracurricular_activities': 'Programming contest',
            'skills_summary': 'Python, Django, SQL',
        })
        self.assertRedirects(response, reverse('student_dashboard'))

    def test_teacher_cannot_access_student_profile_pages(self):
        self.client.login(username='teacher1', password='TestPass123!')
        response = self.client.get(reverse('create_student_profile'))
        self.assertEqual(response.status_code, 403)

    def test_upload_certificate_project(self):
        StudentProfile.objects.create(user=self.student)
        self.client.login(username='student1', password='TestPass123!')

        test_file = SimpleUploadedFile(
            "certificate.pdf",
            b"fake pdf content",
            content_type="application/pdf"
        )

        response = self.client.post(
            reverse('upload_certificate_project'),
            {
                'title': 'Python Certificate',
                'certificate_file': test_file,
                'project_link': 'https://example.com/project',
                'description': 'My certificate and project',
            }
        )
        self.assertRedirects(response, reverse('student_dashboard'))
        self.assertEqual(CertificateProject.objects.count(), 1)