from django.urls import path, reverse_lazy
from django.contrib.auth.views import (
    LogoutView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from .views import (
    # Auth & home
    home,
    signup_view,
    CustomLoginView,
    role_redirect_view,

    # Dashboards
    student_dashboard,
    teacher_dashboard,
    recruiter_dashboard,
    admin_dashboard,

    # Student profile
    create_student_profile,
    update_student_profile,
    upload_certificate_project,
    delete_certificate_project,

    # Role-protected pages
    student_only_page,
    teacher_only_page,
    recruiter_only_page,

    # Story 4 — Skill Verification
    request_skill_verification,
    my_verifications,
    pending_verifications,
    verification_detail,
    verification_logs,
)


urlpatterns = [
    # ===== Home & Auth =====
    path('', home, name='home'),
    path('signup/', signup_view, name='signup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # ===== Role redirect =====
    path('redirect-dashboard/', role_redirect_view, name='role_redirect'),

    # ===== Dashboards =====
    path('dashboard/student/', student_dashboard, name='student_dashboard'),
    path('dashboard/teacher/', teacher_dashboard, name='teacher_dashboard'),
    path('dashboard/recruiter/', recruiter_dashboard, name='recruiter_dashboard'),
    path('dashboard/admin/', admin_dashboard, name='admin_dashboard'),

    # ===== Student Profile =====
    path('profile/create/', create_student_profile, name='create_student_profile'),
    path('profile/update/', update_student_profile, name='update_student_profile'),
    path('profile/upload/', upload_certificate_project, name='upload_certificate_project'),
    path('profile/upload/delete/<int:pk>/', delete_certificate_project, name='delete_certificate_project'),

    # ===== Role-protected pages =====
    path('student-page/', student_only_page, name='student_only_page'),
    path('teacher-page/', teacher_only_page, name='teacher_only_page'),
    path('recruiter-page/', recruiter_only_page, name='recruiter_only_page'),

    # ===== Story 4 — Skill Verification =====
    path('verification/request/', request_skill_verification, name='request_skill_verification'),
    path('verification/my/', my_verifications, name='my_verifications'),
    path('verification/pending/', pending_verifications, name='pending_verifications'),
    path('verification/<int:pk>/', verification_detail, name='verification_detail'),
    path('admin-logs/verification/', verification_logs, name='verification_logs'),

    # ===== Password Reset =====
    path(
        'password-reset/',
        PasswordResetView.as_view(
            template_name='accounts/password_reset.html',
            email_template_name='accounts/password_reset_email.html',
            subject_template_name='accounts/password_reset_subject.txt',
            success_url=reverse_lazy('password_reset_done'),
        ),
        name='password_reset'
    ),
    path(
        'password-reset/done/',
        PasswordResetDoneView.as_view(
            template_name='accounts/password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        PasswordResetConfirmView.as_view(
            template_name='accounts/password_reset_confirm.html',
            success_url=reverse_lazy('password_reset_complete')
        ),
        name='password_reset_confirm'
    ),
    path(
        'reset/done/',
        PasswordResetCompleteView.as_view(
            template_name='accounts/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
]