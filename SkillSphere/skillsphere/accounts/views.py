from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.urls import reverse
from django.utils import timezone

from .forms import (
    CustomUserSignupForm,
    CustomLoginForm,
    StudentProfileForm,
    CertificateProjectForm,
    SkillVerificationRequestForm,
    ApproveSkillForm,
    RejectSkillForm,
)
from .models import (
    UserProfile,
    StudentProfile,
    CertificateProject,
    Skill,
    SkillVerificationRequest,
    VerificationLog,
)
from .decorator import role_required


# ==================== HOME / AUTH ====================

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


# ==================== ROLE DASHBOARDS ====================

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


# ==================== STUDENT PROFILE ====================

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


# ==================== ROLE-PROTECTED PAGES ====================

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


# ==================== STORY 4: SKILL VERIFICATION ====================

# ----- SCRUM-40: Request Skill Verification (Student) -----
@role_required(['student'])
def request_skill_verification(request):
    student_profile, _ = StudentProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = SkillVerificationRequestForm(request.POST, student=student_profile)
        if form.is_valid():
            skill = form.cleaned_data['skill']

            # Prevent duplicate pending/approved request for same skill
            already = SkillVerificationRequest.objects.filter(
                student=student_profile, skill=skill,
                status__in=['pending', 'approved']
            ).exists()
            if already:
                messages.error(request, f"You already have an active request for {skill.name}.")
                return redirect('my_verifications')

            req = form.save(commit=False)
            req.student = student_profile
            req.save()

            # SCRUM-45: log the action
            VerificationLog.objects.create(
                request=req, action='requested', performed_by=request.user
            )
            messages.success(request, "Verification request submitted.")
            return redirect('my_verifications')
    else:
        form = SkillVerificationRequestForm(student=student_profile)

    return render(request, 'accounts/request_skill_verification.html', {'form': form})


@role_required(['student'])
def my_verifications(request):
    """Student sees all their verification requests with status."""
    student_profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    requests_list = SkillVerificationRequest.objects.filter(
        student=student_profile
    ).order_by('-requested_at')
    return render(request, 'accounts/my_verifications.html', {
        'requests_list': requests_list
    })


# ----- SCRUM-41 + 42 + 43: Approve / Reject (Teacher) -----
@role_required(['teacher'])
def pending_verifications(request):
    """Teacher's queue of pending requests."""
    pending = SkillVerificationRequest.objects.filter(
        status='pending'
    ).select_related('student__user', 'skill').order_by('requested_at')
    return render(request, 'accounts/pending_verifications.html', {
        'pending': pending
    })


@role_required(['teacher'])
def verification_detail(request, pk):
    """Teacher views a request and approves OR rejects."""
    req = get_object_or_404(SkillVerificationRequest, pk=pk)

    approve_form = ApproveSkillForm(instance=req)
    reject_form = RejectSkillForm(instance=req)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'approve':
            approve_form = ApproveSkillForm(request.POST, instance=req)
            if approve_form.is_valid():
                req = approve_form.save(commit=False)
                req.status = 'approved'
                req.verifier = request.user
                req.reviewed_at = timezone.now()
                req.save()
                VerificationLog.objects.create(
                    request=req, action='approved', performed_by=request.user,
                    note=f"Proficiency: {req.proficiency_level}"
                )
                messages.success(request, f"{req.skill.name} approved.")
                return redirect('pending_verifications')

        elif action == 'reject':
            reject_form = RejectSkillForm(request.POST, instance=req)
            if reject_form.is_valid():
                req = reject_form.save(commit=False)
                req.status = 'rejected'
                req.verifier = request.user
                req.reviewed_at = timezone.now()
                req.save()
                VerificationLog.objects.create(
                    request=req, action='rejected', performed_by=request.user,
                    note=req.rejection_reason
                )
                messages.success(request, f"{req.skill.name} rejected.")
                return redirect('pending_verifications')

    return render(request, 'accounts/verification_detail.html', {
        'req': req,
        'approve_form': approve_form,
        'reject_form': reject_form,
    })


# ----- SCRUM-45: Admin Verification Logs -----
@role_required(['admin'])
def verification_logs(request):
    logs = VerificationLog.objects.select_related(
        'request__student__user', 'request__skill', 'performed_by'
    ).all()

    action_filter = request.GET.get('action')
    if action_filter:
        logs = logs.filter(action=action_filter)

    return render(request, 'accounts/verification_logs.html', {
        'logs': logs,
        'action_filter': action_filter,
    })