from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from .models import (
    UserProfile,
    StudentProfile,
    CertificateProject,
    SkillCategory,
    Skill,
    MentorshipRequest,
    SkillVerificationRequest,
)


class SignupForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=False)
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES, required=True)

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

        for field_name, field in self.fields.items():
            if field_name == "role":
                field.widget.attrs.update({"class": "form-control form-select"})
            else:
                field.widget.attrs.update({"class": "form-control"})

    def save(self, commit=True):
        user = super().save(commit=False)

        user.first_name = self.cleaned_data.get("first_name")
        user.last_name = self.cleaned_data.get("last_name")
        user.email = self.cleaned_data.get("email")

        if commit:
            user.save()

            UserProfile.objects.update_or_create(
                user=user,
                defaults={
                    "role": self.cleaned_data.get("role", "student"),
                    "is_locked": False,
                    "failed_login_attempts": 0,
                },
            )

        return user


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter username",
            }
        )
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter password",
            }
        )
    )


class StudentProfileForm(forms.ModelForm):
    class Meta:
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
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "address": forms.Textarea(attrs={"rows": 3}),
            "bio": forms.Textarea(attrs={"rows": 4}),
            "extracurricular_activities": forms.Textarea(attrs={"rows": 3}),
            "skills_summary": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})


class CertificateProjectForm(forms.ModelForm):
    class Meta:
        model = CertificateProject
        fields = ["title", "certificate_file", "project_link"]

        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Example: Django Certificate"}),
            "project_link": forms.URLInput(attrs={"placeholder": "https://example.com/project"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})


class SkillCategoryForm(forms.ModelForm):
    class Meta:
        model = SkillCategory
        fields = ["name", "description"]

        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})


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
            "description": forms.Textarea(attrs={"rows": 4}),
            "proof_link": forms.URLInput(attrs={"placeholder": "https://example.com/proof"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})


class MentorshipRequestForm(forms.ModelForm):
    teacher = forms.ModelChoiceField(
        queryset=User.objects.none(),
        empty_label="Select Teacher",
        required=True,
    )

    class Meta:
        model = MentorshipRequest
        fields = ["teacher", "message"]

        widgets = {
            "message": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Write why you want mentoring from this teacher",
                }
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["teacher"].queryset = User.objects.filter(
            userprofile__role="teacher",
            is_active=True,
        ).order_by("first_name", "username")

        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})


class SkillVerificationRequestForm(forms.ModelForm):
    teacher = forms.ModelChoiceField(
        queryset=User.objects.none(),
        empty_label="Select connected teacher",
        required=True,
    )

    class Meta:
        model = SkillVerificationRequest
        fields = ["teacher", "message"]

        widgets = {
            "message": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Write a short note about this skill proof",
                }
            )
        }

    def __init__(self, *args, **kwargs):
        student = kwargs.pop("student", None)
        super().__init__(*args, **kwargs)

        if student:
            connected_teacher_ids = MentorshipRequest.objects.filter(
                student=student,
                status="accepted",
            ).values_list("teacher_id", flat=True)

            self.fields["teacher"].queryset = User.objects.filter(
                id__in=connected_teacher_ids,
                is_active=True,
            )

        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})


class ApproveSkillVerificationForm(forms.ModelForm):
    proficiency_level = forms.ChoiceField(
        choices=Skill.PROFICIENCY_CHOICES,
        required=True,
    )

    feedback = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "placeholder": "Optional feedback for student",
            }
        ),
    )

    class Meta:
        model = Skill
        fields = ["proficiency_level"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})


class RejectSkillVerificationForm(forms.Form):
    rejection_reason = forms.CharField(
        required=True,
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "class": "form-control",
                "placeholder": "Write reason for rejection",
            }
        ),
    )