from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Q, Count, Prefetch
from datetime import datetime
from functools import wraps

from .models import Course, Module, Lesson, LessonAccess, CourseAttachment
from academic.models import StudentEnrollment, ClassSubjectTeacher
from accounts.models import User


def role_required(*roles):
    """Decorator to check user role"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.role not in roles:
                messages.error(request, "Anda tidak memiliki akses ke halaman ini.")
                return redirect('accounts:dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# ==================== STUDENT VIEWS ====================

class StudentCourseListView(ListView):
    """List courses for enrolled student"""
    model = Course
    template_name = 'courses/student_course_list.html'
    context_object_name = 'courses'
    paginate_by = 6

    @method_decorator(login_required(login_url='login'))
    def dispatch(self, *args, **kwargs):
        if self.request.user.role != 'STUDENT':
            messages.error(self.request, "Akses ditolak.")
            return redirect('accounts:dashboard')
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        """Get courses for enrolled classes"""
        student = self.request.user
        enrollments = StudentEnrollment.objects.filter(
            student=student,
            status='ACTIVE'
        ).values_list('class_obj_id', flat=True)

        return Course.objects.filter(
            class_obj_id__in=enrollments,
            is_active=True
        ).select_related('subject', 'teacher', 'class_obj').annotate(
            module_count=Count('modules')
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user

        # Get lesson completion stats for each course
        for course in context['courses']:
            total_lessons = Lesson.objects.filter(
                module__course=course
            ).count()

            completed_lessons = LessonAccess.objects.filter(
                student=student,
                lesson__module__course=course,
                is_completed=True
            ).count()

            course.total_lessons = total_lessons
            course.completed_lessons = completed_lessons
            course.progress_percent = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0

        return context


class CourseDetailView(DetailView):
    """Display course details with modules"""
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'
    pk_url_kwarg = 'course_id'

    @method_decorator(login_required(login_url='login'))
    def dispatch(self, *args, **kwargs):
        if self.request.user.role not in ['STUDENT', 'TEACHER']:
            messages.error(self.request, "Akses ditolak.")
            return redirect('accounts:dashboard')
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        if user.role == 'STUDENT':
            # Students can only view their enrolled courses
            enrollments = StudentEnrollment.objects.filter(
                student=user,
                status='ACTIVE'
            ).values_list('class_obj_id', flat=True)
            return Course.objects.filter(
                class_obj_id__in=enrollments,
                is_active=True
            ).select_related('subject', 'teacher', 'class_obj')
        else:  # TEACHER
            # Teachers can only view their own courses
            return Course.objects.filter(
                teacher=user
            ).select_related('subject', 'teacher', 'class_obj')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user
        course = self.get_object()

        # Get modules with lessons
        modules = course.modules.prefetch_related('lessons').order_by('order')
        context['modules'] = modules

        # Get attachments
        context['attachments'] = course.attachments.all()

        # Get student's lesson access records
        lesson_accesses = LessonAccess.objects.filter(
            student=student,
            lesson__module__course=course
        ).values_list('lesson_id', flat=True)
        context['completed_lesson_ids'] = list(lesson_accesses)

        # Calculate progress
        total_lessons = Lesson.objects.filter(
            module__course=course
        ).count()
        completed = LessonAccess.objects.filter(
            student=student,
            lesson__module__course=course,
            is_completed=True
        ).count()
        context['progress_percent'] = (completed / total_lessons * 100) if total_lessons > 0 else 0

        return context


class ModuleDetailView(DetailView):
    """Display module with lessons"""
    model = Module
    template_name = 'courses/module_detail.html'
    context_object_name = 'module'
    pk_url_kwarg = 'module_id'

    @method_decorator(login_required(login_url='login'))
    def dispatch(self, *args, **kwargs):
        if self.request.user.role != 'STUDENT':
            messages.error(self.request, "Akses ditolak.")
            return redirect('accounts:dashboard')
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        student = self.request.user
        enrollments = StudentEnrollment.objects.filter(
            student=student,
            status='ACTIVE'
        ).values_list('class_obj_id', flat=True)

        return Module.objects.filter(
            course__class_obj_id__in=enrollments,
            course__is_active=True
        ).select_related('course')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        module = self.get_object()
        student = self.request.user

        # Get lessons in order
        lessons = module.lessons.order_by('order')
        context['lessons'] = lessons

        # Track which lessons are completed
        completed_ids = LessonAccess.objects.filter(
            student=student,
            lesson__module=module,
            is_completed=True
        ).values_list('lesson_id', flat=True)
        context['completed_lesson_ids'] = list(completed_ids)

        # Get course for breadcrumb
        context['course'] = module.course

        return context


class LessonDetailView(DetailView):
    """Display lesson content"""
    model = Lesson
    template_name = 'courses/lesson_detail.html'
    context_object_name = 'lesson'
    pk_url_kwarg = 'lesson_id'

    @method_decorator(login_required(login_url='login'))
    def dispatch(self, *args, **kwargs):
        if self.request.user.role != 'STUDENT':
            messages.error(self.request, "Akses ditolak.")
            return redirect('accounts:dashboard')
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        student = self.request.user
        enrollments = StudentEnrollment.objects.filter(
            student=student,
            status='ACTIVE'
        ).values_list('class_obj_id', flat=True)

        return Lesson.objects.filter(
            module__course__class_obj_id__in=enrollments,
            module__course__is_active=True
        ).select_related('module__course')

    def get(self, request, *args, **kwargs):
        """Record lesson access"""
        lesson = self.get_object()
        student = request.user

        # Track access
        access, created = LessonAccess.objects.get_or_create(
            lesson=lesson,
            student=student
        )
        if not created:
            access.last_accessed = datetime.now()
            access.save()

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lesson = self.get_object()
        student = self.request.user

        # Get or create access record
        access = LessonAccess.objects.get(lesson=lesson, student=student)
        context['lesson_access'] = access

        # Get module and course
        context['module'] = lesson.module
        context['course'] = lesson.module.course

        # Get all lessons in module for navigation
        context['module_lessons'] = lesson.module.lessons.order_by('order')

        # Find previous and next lessons
        lessons_in_module = list(lesson.module.lessons.order_by('order'))
        current_index = lessons_in_module.index(lesson)

        context['previous_lesson'] = lessons_in_module[current_index - 1] if current_index > 0 else None
        context['next_lesson'] = lessons_in_module[current_index + 1] if current_index < len(lessons_in_module) - 1 else None

        return context


@login_required(login_url='login')
@role_required('STUDENT')
def mark_lesson_complete(request, lesson_id):
    """Mark lesson as completed"""
    student = request.user
    lesson = get_object_or_404(Lesson, id=lesson_id)

    # Verify student has access
    enrollments = StudentEnrollment.objects.filter(
        student=student,
        status='ACTIVE'
    ).values_list('class_obj_id', flat=True)

    if not lesson.module.course.class_obj_id in enrollments:
        messages.error(request, "Akses ditolak.")
        return redirect('courses:student_courses')

    # Update access record
    access, created = LessonAccess.objects.get_or_create(
        lesson=lesson,
        student=student
    )
    access.is_completed = True
    access.completion_date = datetime.now()
    access.save()

    messages.success(request, f"'{lesson.title}' ditandai sebagai selesai!")
    return redirect('lesson_detail', lesson_id=lesson_id)


# ==================== TEACHER VIEWS ====================

class TeacherCourseListView(ListView):
    """List courses taught by teacher"""
    model = Course
    template_name = 'courses/teacher_course_list.html'
    context_object_name = 'courses'
    paginate_by = 6

    @method_decorator(login_required(login_url='login'))
    def dispatch(self, *args, **kwargs):
        if self.request.user.role != 'TEACHER':
            messages.error(self.request, "Akses ditolak.")
            return redirect('accounts:dashboard')
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        teacher = self.request.user
        return Course.objects.filter(
            teacher=teacher
        ).select_related('subject', 'class_obj', 'academic_year').annotate(
            module_count=Count('modules'),
            student_count=Count('class_obj__enrollments', distinct=True)
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_courses'] = self.get_queryset().count()
        return context


class CourseCreateView(CreateView):
    """Create new course"""
    model = Course
    template_name = 'courses/course_form.html'
    fields = ['subject', 'class_obj', 'academic_year', 'description', 'syllabus']
    success_url = reverse_lazy('courses:teacher_courses')

    @method_decorator(login_required(login_url='login'))
    def dispatch(self, *args, **kwargs):
        if self.request.user.role != 'TEACHER':
            messages.error(self.request, "Akses ditolak.")
            return redirect('accounts:dashboard')
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.instance.teacher = self.request.user
        messages.success(self.request, "Course berhasil dibuat!")
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Filter to only classes and subjects taught by this teacher
        teacher = self.request.user
        kwargs['initial'] = {}
        return kwargs


class CourseUpdateView(UpdateView):
    """Update course details"""
    model = Course
    template_name = 'courses/course_form.html'
    fields = ['description', 'syllabus', 'is_active']
    pk_url_kwarg = 'course_id'
    success_url = reverse_lazy('courses:teacher_courses')

    @method_decorator(login_required(login_url='login'))
    def dispatch(self, *args, **kwargs):
        if self.request.user.role != 'TEACHER':
            messages.error(self.request, "Akses ditolak.")
            return redirect('accounts:dashboard')
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        return Course.objects.filter(teacher=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Course berhasil diperbarui!")
        return super().form_valid(form)


# ==================== MODULE VIEWS ====================

class ModuleCreateView(CreateView):
    """Create module in course"""
    model = Module
    template_name = 'courses/module_form.html'
    fields = ['title', 'description', 'order']
    success_url = reverse_lazy('courses:teacher_courses')

    @method_decorator(login_required(login_url='login'))
    def dispatch(self, *args, **kwargs):
        if self.request.user.role != 'TEACHER':
            messages.error(self.request, "Akses ditolak.")
            return redirect('accounts:dashboard')
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_id = self.kwargs.get('course_id')
        context['course'] = get_object_or_404(Course, id=course_id, teacher=self.request.user)
        return context

    def form_valid(self, form):
        course_id = self.kwargs.get('course_id')
        course = get_object_or_404(Course, id=course_id, teacher=self.request.user)
        form.instance.course = course
        messages.success(self.request, "Module berhasil dibuat!")
        return super().form_valid(form)

    def get_success_url(self):
        course_id = self.kwargs.get('course_id')
        return reverse_lazy('course_detail', kwargs={'course_id': course_id})


# ==================== LESSON VIEWS ====================

class LessonCreateView(CreateView):
    """Create lesson in module"""
    model = Lesson
    template_name = 'courses/lesson_form.html'
    fields = ['title', 'description', 'content_type', 'text_content', 'video_file', 'video_url', 'pdf_file', 'duration_minutes', 'order', 'is_mandatory']
    success_url = reverse_lazy('courses:teacher_courses')

    @method_decorator(login_required(login_url='login'))
    def dispatch(self, *args, **kwargs):
        if self.request.user.role != 'TEACHER':
            messages.error(self.request, "Akses ditolak.")
            return redirect('accounts:dashboard')
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        module_id = self.kwargs.get('module_id')
        module = get_object_or_404(Module, id=module_id)

        # Verify teacher has access
        if module.course.teacher != self.request.user:
            messages.error(self.request, "Akses ditolak.")
            raise PermissionError("Access denied")

        context['module'] = module
        context['course'] = module.course
        return context

    def form_valid(self, form):
        module_id = self.kwargs.get('module_id')
        module = get_object_or_404(Module, id=module_id, course__teacher=self.request.user)
        form.instance.module = module
        messages.success(self.request, "Lesson berhasil dibuat!")
        return super().form_valid(form)

    def get_success_url(self):
        course_id = self.kwargs.get('course_id')
        return reverse_lazy('course_detail', kwargs={'course_id': course_id})


# ==================== COURSE STATS ====================

class CourseAnalyticsView(DetailView):
    """View course analytics (teacher only)"""
    model = Course
    template_name = 'courses/course_analytics.html'
    context_object_name = 'course'
    pk_url_kwarg = 'course_id'

    @method_decorator(login_required(login_url='login'))
    def dispatch(self, *args, **kwargs):
        if self.request.user.role != 'TEACHER':
            messages.error(self.request, "Akses ditolak.")
            return redirect('accounts:dashboard')
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        return Course.objects.filter(teacher=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()

        # Get enrolled students
        students = User.objects.filter(
            role='STUDENT',
            enrollments__class_obj=course.class_obj,
            enrollments__status='ACTIVE'
        ).distinct()
        context['total_students'] = students.count()

        # Get lesson completion stats
        modules = course.modules.prefetch_related('lessons').all()
        total_lessons = sum(m.lessons.count() for m in modules)
        context['total_modules'] = modules.count()
        context['total_lessons'] = total_lessons

        # Student progress
        student_progress = []
        for student in students:
            completed = LessonAccess.objects.filter(
                student=student,
                lesson__module__course=course,
                is_completed=True
            ).count()
            progress_pct = (completed / total_lessons * 100) if total_lessons > 0 else 0
            student_progress.append({
                'student': student,
                'completed': completed,
                'total': total_lessons,
                'progress': progress_pct
            })

        context['student_progress'] = sorted(student_progress, key=lambda x: x['progress'], reverse=True)

        # Calculate average progress for display
        if student_progress:
            avg_progress = sum(p['progress'] for p in student_progress) / len(student_progress)
            context['average_progress'] = round(avg_progress, 0)
        else:
            context['average_progress'] = 0

        return context
