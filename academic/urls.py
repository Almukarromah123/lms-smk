from django.urls import path
from . import views

app_name = 'academic'

urlpatterns = [
    # Bulk enrollment hub
    path('bulk-enrollment/', views.BulkEnrollmentHubView.as_view(), name='bulk_enrollment'),

    # Student bulk enrollment
    path('bulk-enrollment/siswa/', views.BulkStudentEnrollmentView.as_view(), name='student_enrollment'),
    path('bulk-enrollment/siswa/success/', views.StudentEnrollmentSuccessView.as_view(), name='student_enrollment_success'),

    # Teacher bulk enrollment
    path('bulk-enrollment/guru/', views.BulkTeacherEnrollmentView.as_view(), name='teacher_enrollment'),
    path('bulk-enrollment/guru/success/', views.TeacherEnrollmentSuccessView.as_view(), name='teacher_enrollment_success'),

    # Legacy paths for backward compatibility
    path('enrollment-success/', views.BulkEnrollmentSuccessView.as_view(), name='enrollment_success'),
    path('export-credentials/', views.ExportStudentCredentialsView.as_view(), name='export_credentials'),
]
