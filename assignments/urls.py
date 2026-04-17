from django.urls import path
from . import views

app_name = 'assignments'

urlpatterns = [
    # Student views
    path('list/', views.StudentAssignmentListView.as_view(), name='student_list'),
    path('<uuid:assignment_id>/', views.AssignmentDetailView.as_view(), name='detail'),
    path('<uuid:assignment_id>/submit/', views.SubmitAssignmentView.as_view(), name='submit'),

    # Teacher views
    path('teacher/list/', views.TeacherAssignmentListView.as_view(), name='teacher_list'),
    path('teacher/create/', views.CreateAssignmentView.as_view(), name='create'),
    path('teacher/<uuid:assignment_id>/edit/', views.EditAssignmentView.as_view(), name='edit'),
    path('teacher/<uuid:assignment_id>/delete/', views.DeleteAssignmentView.as_view(), name='delete'),
    path('teacher/<uuid:assignment_id>/submissions/', views.ViewSubmissionsView.as_view(), name='submissions'),
    path('teacher/<uuid:assignment_id>/grade/<uuid:submission_id>/', views.GradeSubmissionView.as_view(), name='grade'),
]
