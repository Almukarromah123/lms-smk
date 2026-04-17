from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import TemplateView, FormView, UpdateView
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.http import HttpResponseForbidden
from functools import wraps
from .models import User, UserProfile
from academic.models import StudentEnrollment, ClassSubjectTeacher
from assignments.models import Assignment, AssignmentSubmission
from exams.models import ExamSession
from grades.models import GradeBook
from payments.models import StudentBill
from django.db.models import Q


def role_required(*roles):
    """Decorator to check user role"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            if request.user.role not in roles:
                messages.error(request, "You don't have permission to access this page.")
                return redirect('accounts:dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


class CustomLoginView(LoginView):
    """Custom login view"""
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    next_page = 'accounts:dashboard'

    def get_success_url(self):
        return reverse_lazy('accounts:dashboard')


class CustomLogoutView(LogoutView):
    """Custom logout view"""
    next_page = 'accounts:login'


@login_required(login_url='accounts:login')
def dashboard(request):
    """Route to appropriate dashboard based on user role"""
    if request.user.role == 'ADMIN':
        return redirect('accounts:admin_dashboard')
    elif request.user.role == 'TEACHER':
        return redirect('accounts:teacher_dashboard')
    elif request.user.role == 'STUDENT':
        return redirect('accounts:student_dashboard')
    return redirect('accounts:login')


class AdminDashboardView(TemplateView):
    """Admin dashboard"""
    template_name = 'dashboard/admin_dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        # Check login first
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        # Check admin role
        if request.user.role != 'ADMIN':
            messages.error(request, "You don't have permission to access this page.")
            return redirect('accounts:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.db.models import Count

        context['total_users'] = User.objects.count()
        context['total_students'] = User.objects.filter(role='STUDENT').count()
        context['total_teachers'] = User.objects.filter(role='TEACHER').count()
        context['total_classes'] = __import__('academic.models', fromlist=['Class']).Class.objects.count()
        context['total_subjects'] = __import__('academic.models', fromlist=['Subject']).Subject.objects.count()

        # Recent activities
        from academic.models import StudentEnrollment
        context['recent_enrollments'] = StudentEnrollment.objects.select_related('student', 'class_obj').order_by('-created_at')[:5]

        return context


class TeacherDashboardView(TemplateView):
    """Teacher dashboard"""
    template_name = 'dashboard/teacher_dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        # Check login first
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        # Check teacher role
        if request.user.role != 'TEACHER':
            messages.error(request, "You don't have permission to access this page.")
            return redirect('accounts:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        teacher = self.request.user

        # Get classes taught by this teacher
        class_ids = ClassSubjectTeacher.objects.filter(
            teacher=teacher
        ).values_list('class_obj_id', flat=True).distinct()
        context['teaching_assignments'] = ClassSubjectTeacher.objects.filter(
            teacher=teacher,
            class_obj_id__in=class_ids
        ).select_related('class_obj', 'subject')

        # Get recent assignments
        context['recent_assignments'] = Assignment.objects.filter(
            teacher=teacher
        ).order_by('-due_date')[:5]

        # Get pending submissions to grade
        from django.db.models import Count, Q
        pending_submissions = AssignmentSubmission.objects.filter(
            assignment__teacher=teacher,
            is_graded=False,
            submitted_at__isnull=False
        ).values('assignment').annotate(count=Count('id'))
        context['pending_grading_count'] = sum(item['count'] for item in pending_submissions)

        # Get exams created
        context['recent_exams'] = __import__('exams.models', fromlist=['Exam']).Exam.objects.filter(
            created_by=teacher
        ).order_by('-exam_date')[:5]

        return context


class StudentDashboardView(TemplateView):
    """Student dashboard"""
    template_name = 'dashboard/student_dashboard.html'

    @method_decorator(login_required(login_url='accounts:login'))
    @method_decorator(role_required('STUDENT'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        student = self.request.user

        # Get enrolled classes
        enrollments = StudentEnrollment.objects.filter(
            student=student,
            status='ACTIVE'
        ).select_related('class_obj')
        context['enrolled_classes'] = enrollments

        # Get current assignments
        classes = enrollments.values_list('class_obj', flat=True)
        context['pending_assignments'] = Assignment.objects.filter(
            class_obj__in=classes,
            is_active=True
        ).order_by('due_date')[:5]

        # Get submissions to submit
        context['my_assignments'] = AssignmentSubmission.objects.filter(
            student=student
        ).select_related('assignment').order_by('-assignment__due_date')[:5]

        # Get exam sessions
        context['upcoming_exams'] = ExamSession.objects.filter(
            student=student,
            status__in=['NOT_STARTED', 'IN_PROGRESS']
        ).select_related('exam').order_by('exam__exam_date')[:5]

        # Get grades
        context['recent_grades'] = GradeBook.objects.filter(
            student=student
        ).select_related('subject').order_by('-last_updated')[:5]

        # Get pending bills
        context['pending_bills'] = StudentBill.objects.filter(
            student=student,
            status__in=['PENDING', 'PARTIAL', 'OVERDUE']
        ).select_related('bill_type').order_by('due_date')[:5]

        return context


class UserProfileView(TemplateView):
    """User profile view"""
    template_name = 'accounts/profile.html'

    @method_decorator(login_required(login_url='accounts:login'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user'] = user
        if hasattr(user, 'profile'):
            context['profile'] = user.profile
        return context


class EditProfileView(UpdateView):
    """Edit user profile"""
    model = User
    template_name = 'accounts/edit_profile.html'
    form_class = None  # Will be dynamically set
    success_url = reverse_lazy('accounts:profile')

    @method_decorator(login_required(login_url='accounts:login'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_object(self):
        return self.request.user

    def get_form_class(self):
        from .forms import UserProfileForm
        return UserProfileForm

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Profile updated successfully!')
        return response


class CustomPasswordChangeView(PasswordChangeView):
    """Change password view"""
    template_name = 'accounts/change_password.html'
    success_url = reverse_lazy('accounts:profile')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Password changed successfully!')
        return response
