from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager

from .models import (
    UserProfile,
    StudentProfile,
    SkillCategory,
    Skill,
    MentorshipRequest,
    SkillVerificationRequest,
)


class SprintSeleniumTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        chrome_options = Options()
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1400,1000")

        # Uncomment this line if you do not want Chrome window to open.
        # chrome_options.add_argument("--headless=new")

        cls.browser = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options,
        )

        cls.wait = WebDriverWait(cls.browser, 15)

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()

    def setUp(self):
        self.student = User.objects.create_user(
            username="student1",
            password="TestPass123!",
            email="student1@example.com",
            first_name="Student",
            last_name="One",
        )

        self.teacher = User.objects.create_user(
            username="teacher1",
            password="TestPass123!",
            email="teacher1@example.com",
            first_name="Teacher",
            last_name="One",
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

        self.student_profile, created = StudentProfile.objects.get_or_create(
            user=self.student
        )

        self.student_profile.phone_number = "01711111111"
        self.student_profile.address = "Dhaka, Bangladesh"
        self.student_profile.department = "CSE"
        self.student_profile.university = "University Of Asia Pacific"
        self.student_profile.cgpa = "3.81"
        self.student_profile.save()

        self.category, created = SkillCategory.objects.get_or_create(
            name="Programming",
            defaults={
                "description": "Programming skill category",
            },
        )

    def login(self, username, password):
        self.browser.get(f"{self.live_server_url}/login/")

        username_input = self.wait.until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        username_input.clear()
        username_input.send_keys(username)

        password_input = self.browser.find_element(By.NAME, "password")
        password_input.clear()
        password_input.send_keys(password)

        self.browser.find_element(By.XPATH, "//button[@type='submit']").click()

    def login_student(self):
        self.login("student1", "TestPass123!")

        self.wait.until(
            EC.url_contains("/dashboard/student/")
        )

    def login_teacher(self):
        self.login("teacher1", "TestPass123!")

        self.wait.until(
            EC.url_contains("/dashboard/teacher/")
        )

    def test_01_home_page_loads(self):
        self.browser.get(f"{self.live_server_url}/")

        self.assertIn("SkillSphere", self.browser.page_source)

    def test_02_signup_page_loads(self):
        self.browser.get(f"{self.live_server_url}/signup/")

        self.wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        self.assertIn("SkillSphere", self.browser.page_source)
        self.assertTrue(self.browser.find_element(By.NAME, "username"))
        self.assertTrue(self.browser.find_element(By.NAME, "email"))

    def test_03_login_page_loads(self):
        self.browser.get(f"{self.live_server_url}/login/")

        self.wait.until(
            EC.presence_of_element_located((By.NAME, "username"))
        )

        self.assertIn("Login", self.browser.page_source)
        self.assertTrue(self.browser.find_element(By.NAME, "username"))
        self.assertTrue(self.browser.find_element(By.NAME, "password"))

    def test_04_valid_student_login_redirects_to_student_dashboard(self):
        self.login_student()

        self.assertIn("/dashboard/student/", self.browser.current_url)
        self.assertIn("Student Dashboard", self.browser.page_source)

    def test_05_valid_teacher_login_redirects_to_teacher_dashboard(self):
        self.login_teacher()

        self.assertIn("/dashboard/teacher/", self.browser.current_url)
        self.assertIn("Teacher Dashboard", self.browser.page_source)

    def test_06_invalid_login_shows_error(self):
        self.browser.get(f"{self.live_server_url}/login/")

        username_input = self.wait.until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        username_input.clear()
        username_input.send_keys("student1")

        password_input = self.browser.find_element(By.NAME, "password")
        password_input.clear()
        password_input.send_keys("WrongPassword123")

        self.browser.find_element(By.XPATH, "//button[@type='submit']").click()

        self.wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        page = self.browser.page_source.lower()

        self.assertTrue(
            "invalid" in page
            or "please enter a correct" in page
            or "error" in page
            or "errorlist" in page
        )

    def test_07_student_dashboard_shows_profile_data(self):
        self.login_student()

        page = self.browser.page_source

        self.assertIn("Student Dashboard", page)
        self.assertTrue("Student One" in page or "student1" in page)
        self.assertIn("01711111111", page)
        self.assertIn("Dhaka", page)
        self.assertIn("CSE", page)

    def test_08_update_profile_page_loads(self):
        self.login_student()

        self.browser.get(f"{self.live_server_url}/profile/update/")

        self.wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "form"))
        )

        self.assertTrue(
            "Update" in self.browser.page_source
            or "Profile" in self.browser.page_source
        )

    def test_09_upload_certificate_page_loads(self):
        self.login_student()

        self.browser.get(f"{self.live_server_url}/profile/upload/")

        self.wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "form"))
        )

        self.assertTrue(
            "Upload" in self.browser.page_source
            or "Certificate" in self.browser.page_source
            or "Project" in self.browser.page_source
        )

    def test_10_add_skill_page_loads(self):
        self.login_student()

        self.browser.get(f"{self.live_server_url}/skills/add/")

        self.wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "form"))
        )

        self.assertTrue(
            "Skill" in self.browser.page_source
            or "Add" in self.browser.page_source
        )

    def test_11_request_teacher_connection_page_loads(self):
        self.login_student()

        self.browser.get(f"{self.live_server_url}/mentorship/request/")

        self.wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "form"))
        )

        self.assertTrue(
            "Teacher" in self.browser.page_source
            or "Mentorship" in self.browser.page_source
            or "Request" in self.browser.page_source
        )

    def test_12_teacher_dashboard_loads(self):
        self.login_teacher()

        self.assertIn("/dashboard/teacher/", self.browser.current_url)
        self.assertIn("Teacher Dashboard", self.browser.page_source)

    def test_13_teacher_can_view_pending_connection_request(self):
        MentorshipRequest.objects.create(
            student=self.student,
            teacher=self.teacher,
            message="Please guide me for Django.",
            status="pending",
        )

        self.login_teacher()

        page = self.browser.page_source

        self.assertIn("Teacher Dashboard", page)
        self.assertTrue(
            "Please guide me for Django" in page
            or "student1" in page
            or "Student One" in page
        )

    def test_14_student_can_view_skill_on_dashboard(self):
        Skill.objects.create(
            student_profile=self.student_profile,
            category=self.category,
            name="Django",
            description="Django web development",
            verification_status="not_requested",
        )

        self.login_student()

        page = self.browser.page_source

        self.assertIn("Django", page)
        self.assertTrue(
            "not requested" in page.lower()
            or "Not Requested" in page
            or "verification" in page.lower()
        )

    def test_15_request_skill_verification_page_loads(self):
        MentorshipRequest.objects.create(
            student=self.student,
            teacher=self.teacher,
            message="Please mentor me.",
            status="accepted",
        )

        skill = Skill.objects.create(
            student_profile=self.student_profile,
            category=self.category,
            name="Python",
            description="Python programming",
            proof_link="https://github.com/example/python",
            verification_status="not_requested",
        )

        self.login_student()

        self.browser.get(
            f"{self.live_server_url}/verification/request/{skill.pk}/"
        )

        self.wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "form"))
        )

        self.assertTrue(
            "Verification" in self.browser.page_source
            or "Request" in self.browser.page_source
            or "Skill" in self.browser.page_source
        )

    def test_16_teacher_can_view_pending_skill_verification(self):
        MentorshipRequest.objects.create(
            student=self.student,
            teacher=self.teacher,
            message="Please mentor me.",
            status="accepted",
        )

        skill = Skill.objects.create(
            student_profile=self.student_profile,
            category=self.category,
            name="Python",
            description="Python programming",
            proof_link="https://github.com/example/python",
            verification_status="pending",
        )

        SkillVerificationRequest.objects.create(
            student=self.student,
            teacher=self.teacher,
            skill=skill,
            message="Please verify my Python skill.",
            status="pending",
        )

        self.login_teacher()

        page = self.browser.page_source

        self.assertIn("Python", page)
        self.assertTrue(
            "Please verify my Python skill" in page
            or "Pending Skill Verification" in page
            or "Verify" in page
            or "Verification" in page
        )

    def test_17_approve_skill_page_loads(self):
        skill = Skill.objects.create(
            student_profile=self.student_profile,
            category=self.category,
            name="Python",
            description="Python programming",
            proof_link="https://github.com/example/python",
            verification_status="pending",
        )

        verification_request = SkillVerificationRequest.objects.create(
            student=self.student,
            teacher=self.teacher,
            skill=skill,
            message="Please verify.",
            status="pending",
        )

        self.login_teacher()

        self.browser.get(
            f"{self.live_server_url}/verification/approve/{verification_request.pk}/"
        )

        self.wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "form"))
        )

        self.assertTrue(
            "Approve" in self.browser.page_source
            or "Skill" in self.browser.page_source
        )

    def test_18_reject_skill_page_loads(self):
        skill = Skill.objects.create(
            student_profile=self.student_profile,
            category=self.category,
            name="Machine Learning",
            description="ML basics",
            proof_link="https://github.com/example/ml",
            verification_status="pending",
        )

        verification_request = SkillVerificationRequest.objects.create(
            student=self.student,
            teacher=self.teacher,
            skill=skill,
            message="Please verify.",
            status="pending",
        )

        self.login_teacher()

        self.browser.get(
            f"{self.live_server_url}/verification/reject/{verification_request.pk}/"
        )

        self.wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "form"))
        )

        self.assertTrue(
            "Reject" in self.browser.page_source
            or "Skill" in self.browser.page_source
        )