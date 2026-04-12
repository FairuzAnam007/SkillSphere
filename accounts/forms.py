from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import StudentProfile, CertificateProject


class CustomUserSignupForm(UserCreationForm):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('recruiter', 'Recruiter'),
    ]

    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=False)
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'role', 'password1', 'password2']


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Enter your username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'})
    )

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if not username:
            raise forms.ValidationError("Username is required.")

        if not password:
            raise forms.ValidationError("Password is required.")

        user_obj = User.objects.filter(username=username).first()

        if user_obj and hasattr(user_obj, 'profile') and user_obj.profile.is_locked:
            raise forms.ValidationError("This account is locked. Please contact admin.")

        self.user_cache = authenticate(
            self.request,
            username=username,
            password=password
        )

        if self.user_cache is None:
            if user_obj and hasattr(user_obj, 'profile'):
                user_obj.profile.failed_login_attempts += 1
                if user_obj.profile.failed_login_attempts >= 3:
                    user_obj.profile.is_locked = True
                user_obj.profile.save()

            raise forms.ValidationError("Invalid username or password.")

        if not self.user_cache.is_active:
            raise forms.ValidationError("This account is inactive.")

        if hasattr(self.user_cache, 'profile'):
            self.user_cache.profile.failed_login_attempts = 0
            self.user_cache.profile.save()

        return self.cleaned_data


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = [
            'profile_picture',
            'phone',
            'address',
            'date_of_birth',
            'bio',
            'university',
            'department',
            'semester',
            'session',
            'cgpa',
            'extracurricular_activities',
            'skills_summary',
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 3}),
            'extracurricular_activities': forms.Textarea(attrs={'rows': 3}),
            'skills_summary': forms.Textarea(attrs={'rows': 3}),
        }


class CertificateProjectForm(forms.ModelForm):
    class Meta:
        model = CertificateProject
        fields = ['title', 'certificate_file', 'project_link', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        certificate_file = cleaned_data.get('certificate_file')
        project_link = cleaned_data.get('project_link')

        if not certificate_file and not project_link:
            raise forms.ValidationError("Upload a certificate file or provide a project link.")

        return cleaned_data

    def clean_certificate_file(self):
        file = self.cleaned_data.get('certificate_file')
        if file:
            allowed_extensions = ['pdf', 'jpg', 'jpeg', 'png']
            file_extension = file.name.split('.')[-1].lower()

            if file_extension not in allowed_extensions:
                raise forms.ValidationError("Only PDF, JPG, JPEG, and PNG files are allowed.")

            if file.size > 5 * 1024 * 1024:
                raise forms.ValidationError("File size must be under 5 MB.")
        return file