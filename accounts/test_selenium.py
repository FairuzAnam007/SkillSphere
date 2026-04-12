from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from .models import UserProfile
import time


class SprintSeleniumTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        chrome_options = Options()
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1400,1000")

        cls.browser = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        cls.wait = WebDriverWait(cls.browser, 10)

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()

    def setUp(self):
        self.student = User.objects.create_user(
            username="student1",
            password="TestPass123!",
            email="student1@example.com"
        )
        UserProfile.objects.update_or_create(
            user=self.student,
            defaults={
                "role": "student",
                "is_locked": False,
                "failed_login_attempts": 0
            }
        )

    def login_student(self):
        self.browser.get(f"{self.live_server_url}/login/")
        time.sleep(2)

        username_input = self.wait.until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        username_input.clear()
        username_input.send_keys("student1")
        time.sleep(1)

        password_input = self.browser.find_element(By.NAME, "password")
        password_input.clear()
        password_input.send_keys("TestPass123!")
        time.sleep(1)

        self.browser.find_element(By.XPATH, "//button[@type='submit']").click()
        self.wait.until(EC.url_contains("/dashboard/student/"))
        time.sleep(2)

    def test_login_page_ui_loads(self):
        self.browser.get(f"{self.live_server_url}/login/")
        time.sleep(2)

        self.assertIn("Login to SkillSphere", self.browser.page_source)
        self.assertTrue(self.browser.find_element(By.NAME, "username"))
        self.assertTrue(self.browser.find_element(By.NAME, "password"))

    def test_valid_login_redirects_to_student_dashboard(self):
        self.login_student()

        self.assertIn("/dashboard/student/", self.browser.current_url)
        self.assertIn("Student Dashboard", self.browser.page_source)

    def test_invalid_login_shows_error_message(self):
        self.browser.get(f"{self.live_server_url}/login/")
        time.sleep(2)

        username_input = self.wait.until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        username_input.clear()
        username_input.send_keys("student1")
        time.sleep(1)

        password_input = self.browser.find_element(By.NAME, "password")
        password_input.clear()
        password_input.send_keys("WrongPassword")
        time.sleep(1)

        self.browser.find_element(By.XPATH, "//button[@type='submit']").click()

        self.wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "errorlist"))
        )
        time.sleep(2)

        self.assertIn("Invalid username or password.", self.browser.page_source)

    def test_password_reset_page_loads(self):
        self.browser.get(f"{self.live_server_url}/password-reset/")
        time.sleep(2)

        self.assertIn("Reset your password", self.browser.page_source)

    def test_create_student_profile_page_loads(self):
        self.login_student()

        self.browser.get(f"{self.live_server_url}/profile/create/")
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "form")))
        time.sleep(2)

        self.assertIn("Create Your Profile", self.browser.page_source)