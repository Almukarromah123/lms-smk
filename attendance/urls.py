from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    # Calendar & Events
    path('events/', views.EventCalendarView.as_view(), name='events_calendar'),
    path('events/<str:event_date>/', views.EventDetailView.as_view(), name='event_detail'),

    # Attendance Sessions (Teacher)
    path('session/create/', views.CreateAttendanceSessionView.as_view(), name='create_session'),
    path('session/<uuid:session_id>/mark/', views.MarkAttendanceView.as_view(), name='mark_attendance'),
    path('session/<uuid:session_id>/history/', views.StudentAttendanceHistoryView.as_view(), name='session_history'),

    # Student Attendance
    path('submit/<uuid:session_id>/', views.StudentAttendanceSubmitView.as_view(), name='student_submit'),
    path('history/', views.StudentAttendanceHistoryView.as_view(), name='student_history'),

    # QR Code - Student Display & Teacher Scan
    path('session/<uuid:session_id>/qr-code/', views.StudentQRCodeDisplayView.as_view(), name='qr_code_display'),
    path('session/<uuid:session_id>/qr-scan/', views.TeacherScanQRCodeView.as_view(), name='qr_scan'),

    # Teacher Statistics & Reports
    path('stats/daily/', views.TeacherAttendanceStatsView.as_view(), name='teacher_stats_daily'),
    path('stats/daily/export/', views.ExportDailyStatsView.as_view(), name='export_daily'),
    path('recap/semester/', views.TeacherSemesterReportView.as_view(), name='teacher_semester_report'),
    path('recap/semester/export/', views.ExportSemesterReportView.as_view(), name='export_semester'),

    # API - QR Token Refresh (JSON)
    path('api/session/<uuid:session_id>/qr-refresh/', views.QRTokenRefreshAPIView.as_view(), name='qr_refresh_api'),
    path('api/mark-attendance-qr/', views.MarkAttendanceFromQRAPIView.as_view(), name='mark_attendance_qr_api'),
]
