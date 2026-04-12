from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.urls import reverse

from .forms import (
    CustomUserSignupForm,
    CustomLoginForm,
    StudentProfileForm,
    CertificateProjectForm,
)
from .models import UserProfile, StudentProfile, CertificateProject
from .decorator import role_required


def home(request):
    return render(request, 'accounts/home.html')


@transaction.atomic
def signup_view(request):
    if request.method == 'POST':
        form = CustomUserSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = form.cleaned_data['role']

            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.role = role
            profile.save()

            login(request, user)
            return redirect('role_redirect')
    else:
        form = CustomUserSignupForm()

    return render(request, 'accounts/signup.html', {'form': form})


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = CustomLoginForm

    def get_success_url(self):
        return reverse('role_redirect')


@login_required
def role_redirect_view(request):
    if request.user.is_superuser:
        return redirect('admin_dashboard')

    if hasattr(request.user, 'profile'):
        role = request.user.profile.role

        if role == 'student':
            return redirect('student_dashboard')
        elif role == 'teacher':
            return redirect('teacher_dashboard')
        elif role == 'recruiter':
            return redirect('recruiter_dashboard')
        elif role == 'admin':
            return redirect('admin_dashboard')

    return redirect('home')


@role_required(['student'])
def student_dashboard(request):
    profile = StudentProfile.objects.filter(user=request.user).first()
    uploads = []
    if profile:
        uploads = profile.certificates_projects.all().order_by('-uploaded_at')

    return render(request, 'accounts/dashboard.html', {
        'role_title': 'Student Dashboard',
        'student_profile': profile,
        'uploads': uploads,
    })


@role_required(['teacher'])
def teacher_dashboard(request):
    return render(request, 'accounts/dashboard.html', {'role_title': 'Teacher Dashboard'})


@role_required(['recruiter'])
def recruiter_dashboard(request):
    return render(request, 'accounts/dashboard.html', {'role_title': 'Recruiter Dashboard'})


@role_required(['admin'])
def admin_dashboard(request):
    return render(request, 'accounts/dashboard.html', {'role_title': 'Admin Dashboard'})


@role_required(['student'])
def create_student_profile(request):
    if hasattr(request.user, 'student_profile'):
        return redirect('update_student_profile')

    if request.method == 'POST':
        form = StudentProfileForm(request.POST, request.FILES)
        if form.is_valid():
            student_profile = form.save(commit=False)
            student_profile.user = request.user
            student_profile.save()
            messages.success(request, "Student profile created successfully.")
            return redirect('student_dashboard')
    else:
        form = StudentProfileForm()

    return render(request, 'accounts/create_student_profile.html', {'form': form})


@role_required(['student'])
def update_student_profile(request):
    student_profile, _ = StudentProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = StudentProfileForm(request.POST, request.FILES, instance=student_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Student profile updated successfully.")
            return redirect('student_dashboard')
    else:
        form = StudentProfileForm(instance=student_profile)

    return render(request, 'accounts/update_student_profile.html', {'form': form})


@role_required(['student'])
def upload_certificate_project(request):
    student_profile, _ = StudentProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = CertificateProjectForm(request.POST, request.FILES)
        if form.is_valid():
            upload_item = form.save(commit=False)
            upload_item.student_profile = student_profile
            upload_item.save()
            messages.success(request, "Certificate or project link uploaded successfully.")
            return redirect('student_dashboard')
    else:
        form = CertificateProjectForm()

    return render(request, 'accounts/upload_certificate_project.html', {'form': form})


@role_required(['student'])
def delete_certificate_project(request, pk):
    student_profile = get_object_or_404(StudentProfile, user=request.user)
    item = get_object_or_404(CertificateProject, pk=pk, student_profile=student_profile)

    if request.method == 'POST':
        item.delete()
        messages.success(request, "Item deleted successfully.")
        return redirect('student_dashboard')

    return render(request, 'accounts/delete_certificate_project.html', {'item': item})


@role_required(['student'])
def student_only_page(request):
    return render(request, 'accounts/protected_page.html', {'page_title': 'Student Only Page'})


@role_required(['teacher'])
def teacher_only_page(request):
    return render(request, 'accounts/protected_page.html', {'page_title': 'Teacher Only Page'})


@role_required(['recruiter'])
def recruiter_only_page(request):
    return render(request, 'accounts/protected_page.html', {'page_title': 'Recruiter Only Page'})


def custom_permission_denied_view(request, exception=None):
    return render(request, 'accounts/403.html', status=403)