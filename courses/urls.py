from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    # Student views
    path('my-courses/', views.StudentCourseListView.as_view(), name='student_courses'),
    path('course/<uuid:course_id>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('module/<uuid:module_id>/', views.ModuleDetailView.as_view(), name='module_detail'),
    path('lesson/<uuid:lesson_id>/', views.LessonDetailView.as_view(), name='lesson_detail'),
    path('lesson/<uuid:lesson_id>/complete/', views.mark_lesson_complete, name='mark_complete'),

    # Teacher views
    path('teacher/courses/', views.TeacherCourseListView.as_view(), name='teacher_courses'),
    path('teacher/course/create/', views.CourseCreateView.as_view(), name='course_create'),
    path('teacher/course/<uuid:course_id>/edit/', views.CourseUpdateView.as_view(), name='course_edit'),
    path('teacher/course/<uuid:course_id>/analytics/', views.CourseAnalyticsView.as_view(), name='course_analytics'),

    # Module views
    path('teacher/course/<uuid:course_id>/module/create/', views.ModuleCreateView.as_view(), name='module_create'),

    # Lesson views
    path('teacher/course/<uuid:course_id>/module/<uuid:module_id>/lesson/create/', views.LessonCreateView.as_view(), name='lesson_create'),
]
