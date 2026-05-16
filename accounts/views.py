from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone

from .decorator import role_required
from .forms import (
    SignupForm,
    CustomAuthenticationForm,
    StudentProfileForm,
    CertificateProjectForm,
    SkillForm,
    MentorshipRequestForm,
    SkillVerificationRequestForm,
    ApproveSkillVerificationForm,
    RejectSkillVerificationForm,
    JobPostForm,
    JobApplicationForm,
    ApplicationStatusUpdateForm,
)

from .models import (
    UserProfile,
    StudentProfile,
    CertificateProject,
    Skill,
    MentorshipRequest,
    SkillVerificationRequest,
    VerificationLog,
    RecruiterShortlist,
    JobPost,
    JobApplication,
)


# =========================
# Basic Pages
# =========================

def home(request):
    return render(request, "accounts/home.html")


def permission_denied_view(request, exception=None):
    return render(request, "403.html", status=403)


# =========================
# Authentication
# =========================

def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)

        if form.is_valid():
            user = form.save()
            selected_role = form.cleaned_data.get("role", "student")

            UserProfile.objects.update_or_create(
                user=user,
                defaults={
                    "role": selected_role,
                    "is_locked": False,
                    "failed_login_attempts": 0,
             
                },
            )

            if selected_role == "student":
                StudentProfile.objects.get_or_create(user=user)

            messages.success(request, "Account created successfully. Please login.")
            return redirect("login")
    else:
        form = SignupForm()

    return render(request, "accounts/signup.html", {"form": form})


class CustomLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = CustomAuthenticationForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("role_redirect")


@login_required
def role_redirect(request):
    if request.user.is_superuser:
        return redirect("admin:index")

    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            "role": "student",
            "is_locked": False,
            "failed_login_attempts": 0,
        },
    )

    if profile.role == "student":
        StudentProfile.objects.get_or_create(user=request.user)
        return redirect("student_dashboard")

    if profile.role == "teacher":
        return redirect("teacher_dashboard")

    if profile.role == "recruiter":
        return redirect("recruiter_dashboard")

    if profile.role == "admin":
        return redirect("admin:index")

    return redirect("home")


# =========================
# Helper
# =========================

def get_student_profile(user):
    student_profile, created = StudentProfile.objects.get_or_create(user=user)
    return student_profile


# =========================
# Student Dashboard
# =========================
 
 
@login_required
@role_required("student")
def student_dashboard(request):
    student_profile = get_student_profile(request.user)

    certificates = CertificateProject.objects.filter(
        student_profile=student_profile
    ).order_by("-created_at")

    skills = Skill.objects.filter(
        student_profile=student_profile
    ).select_related("category", "verified_by").order_by("-created_at")

    mentorship_requests = MentorshipRequest.objects.filter(
        student=request.user
    ).select_related("teacher").order_by("-created_at")

    connected_teachers = User.objects.filter(
        received_mentorship_requests__student=request.user,
        received_mentorship_requests__status="accepted",
    ).distinct()

    verification_requests = SkillVerificationRequest.objects.filter(
        student=request.user
    ).select_related("skill", "teacher").order_by("-requested_at")

    available_jobs = JobPost.objects.filter(
        is_active=True
    ).select_related("recruiter").order_by("-created_at")

    applied_job_ids = JobApplication.objects.filter(
        student=request.user
    ).values_list("job_id", flat=True)

    my_applications_list = JobApplication.objects.filter(
        student=request.user
    ).select_related("job").order_by("-applied_at")

    context = {
        "student_profile": student_profile,
        "certificates": certificates,
        "skills": skills,
        "mentorship_requests": mentorship_requests,
        "connected_teachers": connected_teachers,
        "verification_requests": verification_requests,
        "available_jobs": available_jobs,
        "applied_job_ids": applied_job_ids,
        "my_applications_list": my_applications_list,
    }

    return render(request, "accounts/student_dashboard.html", context)


# ========================
# Teacher Dashboard
# =========================


@login_required
@role_required("teacher")
def teacher_dashboard(request):
    pending_mentorship_requests = MentorshipRequest.objects.filter(
        teacher=request.user,
        status="pending",
    ).select_related("student").order_by("-created_at")

    accepted_mentorship_requests = MentorshipRequest.objects.filter(
        teacher=request.user,
        status="accepted",
    ).select_related("student").order_by("-responded_at")

    pending_verification_requests = SkillVerificationRequest.objects.filter(
        teacher=request.user,
        status="pending",
    ).select_related("skill", "student").order_by("-requested_at")

    completed_verification_requests = SkillVerificationRequest.objects.filter(
        teacher=request.user
    ).exclude(status="pending").select_related(
        "skill", "student"
    ).order_by("-responded_at")

    logs = VerificationLog.objects.filter(
        teacher=request.user
    ).select_related(
        "actor", "student", "teacher", "skill"
    ).order_by("-created_at")[:20]

    context = {
        "pending_mentorship_requests": pending_mentorship_requests,
        "accepted_mentorship_requests": accepted_mentorship_requests,
        "pending_verification_requests": pending_verification_requests,
        "completed_verification_requests": completed_verification_requests,

        # These aliases are added so older teacher_dashboard.html also works
        "pending_connections": pending_mentorship_requests,
        "accepted_connections": accepted_mentorship_requests,
        "pending_skill_requests": pending_verification_requests,
        "completed_skill_requests": completed_verification_requests,

     
         "logs": logs,
        
    }

    return render(request, "accounts/teacher_dashboard.html", context)


# =========================
# Recruiter Dashboard
# =========================

@login_required
@role_required("recruiter")
def recruiter_dashboard(request):
    query = request.GET.get("q", "").strip()
    verified_only = request.GET.get("verified_only", "")
    department = request.GET.get("department", "").strip()
    min_cgpa = request.GET.get("min_cgpa", "").strip()
    proficiency = request.GET.get("proficiency", "").strip()

    students = StudentProfile.objects.select_related("user").prefetch_related(
        "skills",
        "skills__category",
    ).all()

    if query:
        students = students.filter(
            Q(user__username__icontains=query)
            | Q(user__first_name__icontains=query)
            | Q(user__last_name__icontains=query)
            | Q(skills__name__icontains=query)
            | Q(skills__category__name__icontains=query)
        ).distinct()

    if verified_only == "on":
        students = students.filter(
            skills__verification_status="approved"
        ).distinct()

    if department:
        students = students.filter(
            department__icontains=department
        )

    if min_cgpa:
        try:
            students = students.filter(cgpa__gte=float(min_cgpa))
        except ValueError:
            messages.error(request, "CGPA filter must be a valid number.")

    if proficiency:
        students = students.filter(
            skills__proficiency_level__icontains=proficiency,
            skills__verification_status="approved",
        ).distinct()

    job_posts = JobPost.objects.filter(
        recruiter=request.user
    ).order_by("-created_at")

    applications = JobApplication.objects.filter(
        job__recruiter=request.user
    ).select_related("job", "student").order_by("-applied_at")

    shortlists = RecruiterShortlist.objects.filter(
        recruiter=request.user
    ).select_related("student_profile", "student_profile__user")

    shortlisted_ids = shortlists.values_list("student_profile_id", flat=True)

    context = {
        "students": students,
        "query": query,
        "verified_only": verified_only,
        "department": department,
        "min_cgpa": min_cgpa,
        "proficiency": proficiency,
        "job_posts": job_posts,
        "applications": applications,
        "shortlists": shortlists,
        "shortlisted_ids": shortlisted_ids,
    }

    return render(request, "accounts/recruiter_dashboard.html", context)


# =========================
# Student Profile
# =========================

@login_required
@role_required("student")
def create_student_profile(request):
    student_profile = get_student_profile(request.user)

    if request.method == "POST":
        form = StudentProfileForm(
            request.POST,
            request.FILES,
            instance=student_profile,
        )

        if form.is_valid():
            form.save()
            messages.success(request, "Student profile created successfully.")
            return redirect("student_dashboard")
    else:
        form = StudentProfileForm(instance=student_profile)

    return render(
        request,
        "accounts/create_student_profile.html",
        {
            "form": form,
            "title": "Create Student Profile",
            "button_text": "Save Profile",
        },
    )


@login_required
@role_required("student")
def update_student_profile(request):
    student_profile = get_student_profile(request.user)

    if request.method == "POST":
        form = StudentProfileForm(
            request.POST,
            request.FILES,
            instance=student_profile,
        )

        if form.is_valid():
            form.save()
            messages.success(request, "Student profile updated successfully.")
            return redirect("student_dashboard")
    else:
        form = StudentProfileForm(instance=student_profile)

    return render(
        request,
        "accounts/update_student_profile.html",
        {
            "form": form,
            "title": "Update Student Profile",
            "button_text": "Update Profile",
        },
        
    )


# =========================
# Certificate / Project
# =========================

@login_required
@role_required("student")
def upload_certificate_project(request):
    student_profile = get_student_profile(request.user)

    if request.method == "POST":
        form = CertificateProjectForm(request.POST, request.FILES)

        if form.is_valid():
            certificate = form.save(commit=False)
            certificate.student_profile = student_profile
            certificate.save()

            messages.success(
                request,
                "Certificate or project link uploaded successfully.",
            )
            return redirect("student_dashboard")
    else:
        form = CertificateProjectForm()

    return render(
        request,
        "accounts/upload_certificate_project.html",
        {
            "form": form,
            "title": "Upload Certificate or Project",
            "button_text": "Upload",
        },
    )


@login_required
@role_required("student")
def delete_certificate_project(request, pk):
    student_profile = get_student_profile(request.user)

    certificate = get_object_or_404(
        CertificateProject,
        pk=pk,
        student_profile=student_profile,
    )

    if request.method == "POST":
        certificate.delete()
        messages.success(
            request,
            "Certificate or project deleted successfully.",
        )

    return redirect("student_dashboard")


# =========================
# Skills
# =========================

@login_required
@role_required("student")
def add_skill(request):
    student_profile = get_student_profile(request.user)

    if request.method == "POST":
        form = SkillForm(request.POST, request.FILES)

        if form.is_valid():
            skill = form.save(commit=False)
            skill.student_profile = student_profile
            skill.verification_status = "not_requested"
            skill.save()

            messages.success(request, "Skill added successfully.")
            return redirect("student_dashboard")
    else:
        form = SkillForm()

    return render(
        request,
        "accounts/skill_form.html",
        {
            "form": form,
            "title": "Add Skill",
            "button_text": "Save Skill",
        },
    )


@login_required
@role_required("student")
def edit_skill(request, pk):
    student_profile = get_student_profile(request.user)

    skill = get_object_or_404(
        Skill,
        pk=pk,
        student_profile=student_profile,
    )

    if skill.verification_status == "approved":
        messages.error(request, "Approved skill cannot be edited.")
        return redirect("student_dashboard")

    if request.method == "POST":
        form = SkillForm(request.POST, request.FILES, instance=skill)

        if form.is_valid():
            updated_skill = form.save(commit=False)
            updated_skill.verification_status = "not_requested"
            updated_skill.proficiency_level = ""
            updated_skill.verified_by = None
            updated_skill.verified_at = None
            updated_skill.rejection_reason = ""
            updated_skill.save()

            messages.success(request, "Skill updated successfully.")
            return redirect("student_dashboard")
    else:
        form = SkillForm(instance=skill)

    return render(
        request,
        "accounts/skill_form.html",
        {
            "form": form,
            "title": "Edit Skill",
            "button_text": "Update Skill",
        },
    )


@login_required
@role_required("student")
def delete_skill(request, pk):
    student_profile = get_student_profile(request.user)

    skill = get_object_or_404(
        Skill,
        pk=pk,
        student_profile=student_profile,
    )

    if request.method == "POST":
        skill.delete()
        messages.success(request, "Skill deleted successfully.")

    return redirect("student_dashboard")


# =========================
# Mentorship Connection
# =========================

@login_required
@role_required("student")
def request_teacher_connection(request):
    if request.method == "POST":
        form = MentorshipRequestForm(request.POST)

        if form.is_valid():
            teacher = form.cleaned_data["teacher"]
            message = form.cleaned_data["message"]

            if teacher == request.user:
                messages.error(request, "You cannot send request to yourself.")
                return redirect("student_dashboard")

            mentorship_request, created = MentorshipRequest.objects.get_or_create(
                student=request.user,
                teacher=teacher,
                defaults={
                    "message": message,
                    "status": "pending",
                },
            )

            if not created:
                mentorship_request.message = message
                mentorship_request.status = "pending"
                mentorship_request.responded_at = None
                mentorship_request.save()

            VerificationLog.objects.create(
                action="mentorship_requested",
                actor=request.user,
                student=request.user,
                teacher=teacher,
                note="Student requested teacher mentorship.",
            )

            messages.success(request, "Mentorship request sent successfully.")
            return redirect("student_dashboard")
    else:
        form = MentorshipRequestForm()

    return render(
        request,
        "accounts/request_teacher_connection.html",
        {
            "form": form,
            "title": "Request Teacher Mentorship",
            "button_text": "Send Request",
        },
    )


@login_required
@role_required("teacher")
def respond_mentorship_request(request, pk, action):
    mentorship_request = get_object_or_404(
        MentorshipRequest,
        pk=pk,
        teacher=request.user,
    )

    if request.method == "POST":
        if action == "accept":
            mentorship_request.status = "accepted"
            log_action = "mentorship_accepted"
            message_text = "Mentorship request accepted."

        elif action == "reject":
            mentorship_request.status = "rejected"
            log_action = "mentorship_rejected"
            message_text = "Mentorship request rejected."

        else:
            messages.error(request, "Invalid action.")
            return redirect("teacher_dashboard")

        mentorship_request.responded_at = timezone.now()
        mentorship_request.save()

        VerificationLog.objects.create(
            action=log_action,
            actor=request.user,
            student=mentorship_request.student,
            teacher=request.user,
            note=message_text,
        )

        messages.success(request, message_text)

    return redirect("teacher_dashboard")


# =========================
# Skill Verification
# =========================

@login_required
@role_required("student")
def request_skill_verification(request, skill_id):
    student_profile = get_student_profile(request.user)

    skill = get_object_or_404(
        Skill,
        pk=skill_id,
        student_profile=student_profile,
    )

    connected_teachers = User.objects.filter(
        received_mentorship_requests__student=request.user,
        received_mentorship_requests__status="accepted",
    ).distinct()

    if not connected_teachers.exists():
        messages.error(
            request,
            "You must connect with a teacher before requesting skill verification.",
        )
        return redirect("student_dashboard")

    if request.method == "POST":
        form = SkillVerificationRequestForm(
            request.POST,
            student=request.user,
        )

        if form.is_valid():
            teacher = form.cleaned_data["teacher"]
            message = form.cleaned_data["message"]

            verification_request, created = SkillVerificationRequest.objects.get_or_create(
                skill=skill,
                student=request.user,
                teacher=teacher,
                defaults={
                    "message": message,
                    "status": "pending",
                },
            )

            if not created:
                verification_request.message = message
                verification_request.status = "pending"
                verification_request.feedback = ""
                verification_request.responded_at = None
                verification_request.save()

            skill.verification_status = "pending"
            skill.verified_by = None
            skill.verified_at = None
            skill.rejection_reason = ""
            skill.save()

            VerificationLog.objects.create(
                action="verification_requested",
                actor=request.user,
                student=request.user,
                teacher=teacher,
                skill=skill,
                note="Student requested skill verification.",
            )

            messages.success(request, "Skill verification request sent.")
            return redirect("student_dashboard")
    else:
        form = SkillVerificationRequestForm(student=request.user)

    return render(
        request,
        "accounts/request_skill_verification.html",
        {
            "form": form,
            "skill": skill,
            "title": "Request Skill Verification",
            "button_text": "Send Verification Request",
        },
    )


@login_required
@role_required("teacher")
def approve_skill_verification(request, request_id):
    verification_request = get_object_or_404(
        SkillVerificationRequest,
        pk=request_id,
        teacher=request.user,
        status="pending",
    )

    skill = verification_request.skill

    if request.method == "POST":
        form = ApproveSkillVerificationForm(request.POST, instance=skill)

        if form.is_valid():
            approved_skill = form.save(commit=False)
            approved_skill.verification_status = "approved"
            approved_skill.verified_by = request.user
            approved_skill.verified_at = timezone.now()
            approved_skill.rejection_reason = ""
            approved_skill.save()

            verification_request.status = "approved"
            verification_request.feedback = form.cleaned_data.get("feedback", "")
            verification_request.responded_at = timezone.now()
            verification_request.save()

            VerificationLog.objects.create(
                action="skill_approved",
                actor=request.user,
                student=verification_request.student,
                teacher=request.user,
                skill=skill,
                note=f"Skill approved as {approved_skill.proficiency_level}.",
            )

            messages.success(request, "Skill approved successfully.")
            return redirect("teacher_dashboard")
    else:
        form = ApproveSkillVerificationForm(instance=skill)

    return render(
        request,
        "accounts/approve_skill_verification.html",
        {
            "form": form,
            "verification_request": verification_request,
            "skill": skill,
            "title": "Approve Skill Verification",
            "button_text": "Approve Skill",
        },
    )


@login_required
@role_required("teacher")
def reject_skill_verification(request, request_id):
    verification_request = get_object_or_404(
        SkillVerificationRequest,
        pk=request_id,
        teacher=request.user,
        status="pending",
    )

    skill = verification_request.skill

    if request.method == "POST":
        form = RejectSkillVerificationForm(request.POST)

        if form.is_valid():
            reason = form.cleaned_data["rejection_reason"]

            skill.verification_status = "rejected"
            skill.verified_by = request.user
            skill.verified_at = timezone.now()
            skill.proficiency_level = ""
            skill.rejection_reason = reason
            skill.save()

            verification_request.status = "rejected"
            verification_request.feedback = reason
            verification_request.responded_at = timezone.now()
            verification_request.save()

            VerificationLog.objects.create(
                action="skill_rejected",
                actor=request.user,
                student=verification_request.student,
                teacher=request.user,
                skill=skill,
                note=reason,
            )

            messages.success(request, "Skill rejected successfully.")
            return redirect("teacher_dashboard")
    else:
        form = RejectSkillVerificationForm()

    return render(
        request,
        "accounts/reject_skill_verification.html",
        {
            "form": form,
            "verification_request": verification_request,
            "skill": skill,
            "title": "Reject Skill Verification",
            "button_text": "Reject Skill",
        },
    )


# =========================
# Recruiter Shortlist
# =========================

@login_required
@role_required("recruiter")
def save_shortlisted_candidate(request, student_profile_id):
    student_profile = get_object_or_404(
        StudentProfile,
        pk=student_profile_id,
    )

    RecruiterShortlist.objects.get_or_create(
        recruiter=request.user,
        student_profile=student_profile,
    )

    messages.success(request, "Candidate saved to shortlist.")
    return redirect("recruiter_dashboard")


@login_required
@role_required("recruiter")
def remove_shortlisted_candidate(request, shortlist_id):
    shortlist = get_object_or_404(
        RecruiterShortlist,
        pk=shortlist_id,
        recruiter=request.user,
    )

    shortlist.delete()
    messages.success(request, "Candidate removed from shortlist.")
    return redirect("recruiter_dashboard")


# =========================
# Job Post, Apply, Track Status
# =========================

@login_required
@role_required("recruiter")
def create_job_post(request):
    if request.method == "POST":
        form = JobPostForm(request.POST)

        if form.is_valid():
            job = form.save(commit=False)
            job.recruiter = request.user
            job.save()

            messages.success(request, "Job or internship posted successfully.")
            return redirect("recruiter_dashboard")
    else:
        form = JobPostForm()

    return render(
        request,
        "accounts/job_post_form.html",
        {
            "form": form,
            "title": "Post Job or Internship",
            "button_text": "Publish Post",
        },
    )


@login_required
@role_required("student")
def job_list(request):
    jobs = JobPost.objects.filter(
        is_active=True
    ).select_related("recruiter").order_by("-created_at")

    applied_job_ids = JobApplication.objects.filter(
        student=request.user
    ).values_list("job_id", flat=True)

    context = {
        "jobs": jobs,
        "applied_job_ids": applied_job_ids,
    }

    return render(request, "accounts/job_list.html", context)


@login_required
@role_required("student")
def apply_job(request, job_id):
    job = get_object_or_404(
        JobPost,
        pk=job_id,
        is_active=True,
    )

    already_applied = JobApplication.objects.filter(
        job=job,
        student=request.user,
    ).exists()

    if already_applied:
        messages.error(request, "You have already applied for this position.")
        return redirect("job_list")

    if request.method == "POST":
        form = JobApplicationForm(request.POST, request.FILES)

        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.student = request.user
            application.status = "applied"
            application.save()

            messages.success(request, "Application submitted successfully.")
            return redirect("my_applications")
    else:
        form = JobApplicationForm()

    return render(
        request,
        "accounts/apply_job.html",
        {
            "form": form,
            "job": job,
        },
    )


@login_required
@role_required("student")
def my_applications(request):
    applications = JobApplication.objects.filter(
        student=request.user
    ).select_related("job").order_by("-applied_at")

    return render(
        request,
        "accounts/my_applications.html",
        {
            "applications": applications,
        },
    )


@login_required
@role_required("recruiter")
def update_application_status(request, pk):
    application = get_object_or_404(
        JobApplication,
        pk=pk,
        job__recruiter=request.user,
    )

    if request.method == "POST":
        form = ApplicationStatusUpdateForm(
            request.POST,
            instance=application,
        )

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Application status updated successfully.",
            )
            return redirect("recruiter_dashboard")
    else:
        form = ApplicationStatusUpdateForm(instance=application)

    return render(
        request,
        "accounts/update_application_status.html",
        {
            "form": form,
            "application": application,
        },
    )
