from django.urls import path
from . import views

app_name = 'exams'

urlpatterns = [
    # Student views
    path('list/', views.StudentExamListView.as_view(), name='student_list'),
    path('<uuid:exam_id>/', views.ExamDetailView.as_view(), name='detail'),
    path('<uuid:exam_id>/start/', views.StartExamView.as_view(), name='start'),
    path('session/<uuid:session_id>/session/', views.ExamSessionView.as_view(), name='session'),

    # Teacher views
    path('teacher/list/', views.TeacherExamListView.as_view(), name='teacher_list'),
    path('teacher/create/', views.CreateExamView.as_view(), name='create'),
    path('teacher/<uuid:exam_id>/edit/', views.EditExamView.as_view(), name='edit'),
    path('teacher/<uuid:exam_id>/delete/', views.DeleteExamView.as_view(), name='delete'),
    path('teacher/<uuid:exam_id>/questions/', views.ManageQuestionsView.as_view(), name='questions'),
    path('teacher/<uuid:exam_id>/questions/add/', views.AddQuestionView.as_view(), name='question_add'),
    path('teacher/<uuid:exam_id>/questions/import/', views.ImportQuestionsView.as_view(), name='question_import'),
    path('teacher/<uuid:exam_id>/questions/<uuid:question_id>/edit/', views.EditQuestionView.as_view(), name='question_edit'),
    path('teacher/<uuid:exam_id>/questions/<uuid:question_id>/delete/', views.DeleteQuestionView.as_view(), name='question_delete'),
    path('teacher/<uuid:exam_id>/results/', views.ExamResultsView.as_view(), name='results'),

    # API endpoints
    path('api/log-violation/', views.log_violation_api, name='log_violation'),
]
