from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from .models import (
    StudentProfile,
    CertificateProject,
    Skill,
    MentorshipRequest,
    SkillVerificationRequest,
    JobPost,
    JobApplication,
)


class SignupForm(UserCreationForm):
    ROLE_CHOICES = [
        ("student", "Student"),
        ("teacher", "Teacher"),
        ("recruiter", "Recruiter"),
    ]

    
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "role",
            "password1",
            "password2",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        placeholders = {
            "first_name": "Enter first name",
            "last_name": "Enter last name",
            "username": "Choose username",
            "email": "Enter email",
            "password1": "Enter password",
            "password2": "Confirm password",
        }

        for name, field in self.fields.items():
            field.widget.attrs.update({"class": "form-control"})
            if name in placeholders:
                field.widget.attrs.update({"placeholder": placeholders[name]})


class  CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter username",
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Enter password",
        })
    )


class StudentProfileForm(forms.ModelForm):
    class  Meta:
        model = StudentProfile
        fields = [
            "profile_picture",
            "phone_number",
            "address",
            "date_of_birth",
            "university",
            "department",
            "semester",
            "session",
            "cgpa",
            "bio",
            "extracurricular_activities",
            "skills_summary",
        ]
        widgets = {
            "profile_picture": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "date_of_birth": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "university": forms.TextInput(attrs={"class": "form-control"}),
            "department": forms.TextInput(attrs={"class": "form-control"}),
            "semester": forms.TextInput(attrs={"class": "form-control"}),
            "session": forms.TextInput(attrs={"class": "form-control"}),
            "cgpa": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "bio": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "extracurricular_activities": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "skills_summary": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class CertificateProjectForm(forms.ModelForm):
    class Meta:
        model = CertificateProject
        fields = [
            "title",
            "certificate_file",
            "project_link",
            "description",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "certificate_file": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "project_link": forms.URLInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = [
            "name",
            "category",
            "description",
            "proof_file",
            "proof_link",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "proof_file": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "proof_link": forms.URLInput(attrs={"class": "form-control"}),
        }


class MentorshipRequestForm(forms.ModelForm):
    teacher = forms.ModelChoiceField(
        queryset=User.objects.none(),
        label="Teacher",
        empty_label="Select Teacher",
        widget=forms.Select(attrs={"class": "form-control"})
    )

    class Meta:
        model = MentorshipRequest
        fields = ["teacher", "message"]
        widgets = {
            "message": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Write why you want mentoring from this teacher",
                "rows": 4,
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["teacher"].queryset = User.objects.filter(
            userprofile__role="teacher"
        ).order_by("first_name", "last_name", "username")


class SkillVerificationRequestForm(forms.ModelForm):
    teacher = forms.ModelChoiceField(
        queryset=User.objects.none(),
        label="Teacher",
        empty_label="Select Connected Teacher",
        widget=forms.Select(attrs={"class": "form-control"})
    )

    class Meta:
        model = SkillVerificationRequest
        fields = ["teacher", "message"]
        widgets = {
            "message": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Write a message for skill verification",
                "rows": 4,
            })
        }

    def __init__(self, *args, **kwargs):
        student = kwargs.pop("student", None)
        super().__init__(*args, **kwargs)

        if student:
            self.fields["teacher"].queryset = User.objects.filter(
                received_mentorship_requests__student=student,
                received_mentorship_requests__status="accepted",
            ).distinct()
        else:
            self.fields["teacher"].queryset = User.objects.none()


class ApproveSkillVerificationForm(forms.ModelForm):
    feedback = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "placeholder": "Write feedback for the student",
            "rows": 4,
        })
    )

    class Meta:
        model = Skill
        fields = ["proficiency_level"]
        widgets = {
            "proficiency_level": forms.Select(attrs={"class": "form-control"})
        }


class RejectSkillVerificationForm(forms.Form):
    rejection_reason = forms.CharField(
        label="Rejection Reason",
        required=True,
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "placeholder": "Write the reason for rejecting this skill",
            "rows": 4,
        })
    )


class RecruiterSearchForm(forms.Form):
    keyword = forms.CharField(required=False)
    verified_only = forms.BooleanField(required=False)
    department = forms.CharField(required=False)
    min_cgpa = forms.DecimalField(required=False, max_digits=4, decimal_places=2)
    proficiency_level = forms.ChoiceField(
        required=False,
        choices=[("", "Any Level")] + list(Skill.PROFICIENCY_LEVEL_CHOICES)
    )


class JobPostForm(forms.ModelForm):
    class Meta:
        model = JobPost
        fields = [
            "title",
            "company_name",
            "job_type",
            "location",
            "description",
            "required_skills",
            "deadline",
            "is_active",
        ]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Software Engineer Intern",
            }),
            "company_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Company name",
            }),
            "job_type": forms.Select(attrs={"class": "form-control"}),
            "location": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Dhaka / Remote",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Write job description, requirements, responsibilities",
            }),
            "required_skills": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Python, Django, SQL",
            }),
            "deadline": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = [
            "cover_letter",
            "cv_file",
        ]
        widgets = {
            "cover_letter": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Write a short cover letter",
            }),
            "cv_file": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }


class ApplicationStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = [
            "status",
            "recruiter_note",
        ]
        widgets = {
            "status": forms.Select(attrs={"class": "form-control"}),
            "recruiter_note": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Write recruiter note for the student",
            }),
        }
