from django.urls import path
from . import views

app_name = 'grades'

urlpatterns = [
    # Student views
    path('my-grades/', views.StudentGradesView.as_view(), name='my_grades'),
    path('report-card/', views.ReportCardView.as_view(), name='report_card'),

    # Teacher views
    path('teacher/gradebook/', views.TeacherGradebookView.as_view(), name='gradebook'),
    path('teacher/gradebook/<uuid:class_id>/', views.ClassGradebookView.as_view(), name='class_gradebook'),
]
