from django.urls import path
from django.contrib.auth.views import (
    LogoutView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)

from . import views


urlpatterns = [
    path("", views.home, name="home"),

    path("signup/", views.signup_view, name="signup"),
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page="home"), name="logout"),

    path("dashboard/", views.role_redirect, name="role_redirect"),

    # Backup old URL, so /redirect-dashboard/ will not show 404
    path("redirect-dashboard/", views.role_redirect, name="redirect_dashboard"),

    path("dashboard/student/", views.student_dashboard, name="student_dashboard"),
    path("dashboard/teacher/", views.teacher_dashboard, name="teacher_dashboard"),
    path("dashboard/recruiter/", views.recruiter_dashboard, name="recruiter_dashboard"),

    path("profile/create/", views.create_student_profile, name="create_student_profile"),
    path("profile/update/", views.update_student_profile, name="update_student_profile"),
    path("profile/upload/", views.upload_certificate_project, name="upload_certificate_project"),
    path(
        "profile/certificate/<int:pk>/delete/",
        views.delete_certificate_project,
        name="delete_certificate_project",
    ),

    path("skills/add/", views.add_skill, name="add_skill"),
    path("skills/<int:pk>/edit/", views.edit_skill, name="edit_skill"),
    path("skills/<int:pk>/delete/", views.delete_skill, name="delete_skill"),

    path("mentorship/request/", views.request_teacher_connection, name="request_teacher_connection"),
    path(
        "mentorship/respond/<int:pk>/<str:action>/",
        views.respond_mentorship_request,
        name="respond_mentorship_request",
    ),

    path(
        "verification/request/<int:skill_id>/",
        views.request_skill_verification,
        name="request_skill_verification",
    ),
    path(
        "verification/approve/<int:request_id>/",
        views.approve_skill_verification,
        name="approve_skill_verification",
    ),
    path(
        "verification/reject/<int:request_id>/",
        views.reject_skill_verification,
        name="reject_skill_verification",
    ),

    path(
        "password-reset/",
        PasswordResetView.as_view(
            template_name="accounts/password_reset.html",
            email_template_name="accounts/password_reset_email.html",
            subject_template_name="accounts/password_reset_subject.txt",
            success_url="/password-reset/done/",
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        PasswordResetDoneView.as_view(template_name="accounts/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.html",
            success_url="/password-reset-complete/",
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset-complete/",
        PasswordResetCompleteView.as_view(template_name="accounts/password_reset_complete.html"),
        name="password_reset_complete",
    ),
]
