import json
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, TemplateView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseForbidden, JsonResponse
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta, date
from calendar import Calendar, monthrange

from accounts.models import User
from academic.models import Class, StudentEnrollment, ClassSubjectTeacher
from assignments.models import Assignment
from exams.models import Exam
from .models import AttendanceSession, AttendanceRecord
from .forms import AttendanceSessionForm, BulkAttendanceMarkForm, StudentAttendanceSubmitForm
from .utils import get_qr_code_base64


class EventCalendarView(LoginRequiredMixin, TemplateView):
    """Main calendar view showing all events (attendance, assignments, exams)"""
    template_name = 'academic/calendar.html'
    login_url = 'accounts:login'

    def get_user_classes(self):
        """Get classes for current user based on role"""
        if self.request.user.role == 'TEACHER':
            return Class.objects.filter(
                subject_teachers__teacher=self.request.user
            ).distinct()
        elif self.request.user.role == 'STUDENT':
            return Class.objects.filter(
                enrollments__student=self.request.user,
                enrollments__status='ACTIVE'
            ).distinct()
        return Class.objects.none()

    def get_events_for_date(self, date_obj):
        """Get all events for a specific date"""
        user_classes = self.get_user_classes()
        events = []

        # Attendance sessions (per-subject)
        sessions = AttendanceSession.objects.filter(
            session_date=date_obj,
            class_subject_teacher__class_obj__in=user_classes
        )
        for session in sessions:
            # Determine URL based on session type and user role
            if self.request.user.role == 'TEACHER':
                url = reverse('attendance:mark_attendance', kwargs={'session_id': session.id})
            elif self.request.user.role == 'STUDENT':
                # For LURING sessions, student shows QR code; for DARING, they submit attendance
                if session.session_type == 'LURING':
                    url = reverse('attendance:qr_code_display', kwargs={'session_id': session.id})
                else:
                    url = reverse('attendance:student_submit', kwargs={'session_id': session.id})
            else:
                url = '#'

            events.append({
                'type': 'attendance',
                'title': f"📋 {session.class_subject_teacher.subject.name} - Attendance",
                'description': f"{session.class_subject_teacher.class_obj.name} - {session.description}",
                'id': str(session.id),
                'url': url,
                'color': 'blue'
            })

        # Assignment deadlines
        assignments = Assignment.objects.filter(
            due_date__date=date_obj,
            class_obj__in=user_classes
        )
        for assignment in assignments:
            events.append({
                'type': 'assignment',
                'title': f"📝 {assignment.title}",
                'description': assignment.class_obj.name,
                'id': str(assignment.id),
                'url': reverse('assignments:detail', kwargs={'assignment_id': assignment.id}),
                'color': 'green'
            })

        # Exams
        exams = Exam.objects.filter(
            exam_date__date=date_obj,
            class_obj__in=user_classes
        )
        
        # For students, exclude exams they already completed
        if self.request.user.role == 'STUDENT':
            from exams.models import ExamSession
            from django.db.models import Exists, OuterRef
            
            completed_exams = ExamSession.objects.filter(
                student=self.request.user,
                exam=OuterRef('id'),
                status__in=['SUBMITTED', 'GRADED']
            )
            exams = exams.exclude(Exists(completed_exams))
        
        for exam in exams:
            events.append({
                'type': 'exam',
                'title': f"✏️ {exam.title}",
                'description': exam.class_obj.name,
                'id': str(exam.id),
                'url': reverse('exams:detail', kwargs={'exam_id': exam.id}),
                'color': 'purple'
            })

        return events

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get month and year from query string
        today = date.today()
        year = int(self.request.GET.get('year', today.year))
        month = int(self.request.GET.get('month', today.month))

        # Validate month/year
        if month < 1:
            month = 12
            year -= 1
        elif month > 12:
            month = 1
            year += 1

        # Create calendar
        cal = Calendar()
        month_calendar = cal.monthdayscalendar(year, month)

        # Enrich calendar with events
        enriched_calendar = []
        for week in month_calendar:
            enriched_week = []
            for day in week:
                if day == 0:
                    enriched_week.append(None)
                else:
                    date_obj = date(year, month, day)
                    events = self.get_events_for_date(date_obj)
                    enriched_week.append({
                        'day': day,
                        'date': date_obj,
                        'events': events,
                        'is_today': date_obj == today,
                        'event_count': len(events)
                    })
            enriched_calendar.append(enriched_week)

        # Navigation
        prev_month = month - 1 if month > 1 else 12
        prev_year = year if month > 1 else year - 1
        next_month = month + 1 if month < 12 else 1
        next_year = year if month < 12 else year + 1

        context.update({
            'calendar': enriched_calendar,
            'current_year': year,
            'current_month': month,
            'month_name': ['January', 'February', 'March', 'April', 'May', 'June',
                          'July', 'August', 'September', 'October', 'November', 'December'][month - 1],
            'weekdays': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            'prev_month': prev_month,
            'prev_year': prev_year,
            'next_month': next_month,
            'next_year': next_year,
            'user_role': self.request.user.role,
        })

        return context


class EventDetailView(LoginRequiredMixin, TemplateView):
    """Show detailed view of events on a specific date"""
    template_name = 'academic/event_detail.html'
    login_url = 'accounts:login'

    def get_user_classes(self):
        """Get classes for current user based on role"""
        if self.request.user.role == 'TEACHER':
            return Class.objects.filter(
                subject_teachers__teacher=self.request.user
            ).distinct()
        elif self.request.user.role == 'STUDENT':
            return Class.objects.filter(
                enrollments__student=self.request.user,
                enrollments__status='ACTIVE'
            ).distinct()
        return Class.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event_date_str = self.kwargs.get('event_date')

        try:
            event_date = datetime.strptime(event_date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            messages.error(self.request, 'Invalid date format')
            return context

        user_classes = self.get_user_classes()

        # Get events for this date
        attendance_sessions = AttendanceSession.objects.filter(
            session_date=event_date,
            class_subject_teacher__class_obj__in=user_classes
        )

        assignments = Assignment.objects.filter(
            due_date__date=event_date,
            class_obj__in=user_classes
        )

        exams = Exam.objects.filter(
            exam_date__date=event_date,
            class_obj__in=user_classes
        )

        context.update({
            'event_date': event_date,
            'attendance_sessions': attendance_sessions,
            'assignments': assignments,
            'exams': exams,
            'user_role': self.request.user.role,
        })

        return context


class CreateAttendanceSessionView(LoginRequiredMixin, CreateView):
    """Teacher creates attendance session for a specific subject"""
    model = AttendanceSession
    form_class = AttendanceSessionForm
    template_name = 'attendance/create_session.html'
    success_url = reverse_lazy('attendance:events_calendar')
    login_url = 'accounts:login'

    @method_decorator(login_required(login_url='accounts:login'))
    def dispatch(self, *args, **kwargs):
        # Only teachers can create sessions
        if self.request.user.role != 'TEACHER':
            messages.error(self.request, 'Only teachers can create attendance sessions.')
            return redirect('dashboard')
        return super().dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['teacher'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Only show classes teacher teaches
        context['teacher_classes'] = Class.objects.filter(
            subject_teachers__teacher=self.request.user
        ).distinct()
        return context

    def form_valid(self, form):
        # Get form data
        class_obj = form.cleaned_data['class_obj']
        subject = form.cleaned_data['subject']
        session_type = form.cleaned_data.get('session_type', 'LURING')

        # Verify teacher teaches this class-subject combination
        try:
            class_subject_teacher = ClassSubjectTeacher.objects.get(
                class_obj=class_obj,
                subject=subject,
                teacher=self.request.user
            )
        except ClassSubjectTeacher.DoesNotExist:
            messages.error(self.request, 'You do not teach this subject in this class.')
            return self.form_invalid(form)

        # Create session with class_subject_teacher
        form.instance.class_subject_teacher = class_subject_teacher
        form.instance.session_type = session_type

        # Save the form (this creates the session)
        response = super().form_valid(form)

        # For LURING sessions, generate initial QR token
        if session_type == 'LURING':
            form.instance.generate_new_qr_token()

        messages.success(self.request, f'Attendance session created successfully! (Type: {form.instance.get_session_type_display()})')
        return response


class MarkAttendanceView(LoginRequiredMixin, TemplateView):
    """Teacher bulk mark attendance for a session (per subject)"""
    template_name = 'attendance/mark_attendance.html'
    login_url = 'accounts:login'

    @method_decorator(login_required(login_url='accounts:login'))
    def dispatch(self, *args, **kwargs):
        if self.request.user.role != 'TEACHER':
            messages.error(self.request, 'Only teachers can mark attendance.')
            return redirect('dashboard')
        return super().dispatch(*args, **kwargs)

    def get_session(self):
        """Get attendance session and verify authorization"""
        session_id = self.kwargs.get('session_id')
        try:
            session = AttendanceSession.objects.get(id=session_id)
            # Verify teacher owns this session
            if session.class_subject_teacher.teacher != self.request.user:
                return None
            return session
        except AttendanceSession.DoesNotExist:
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = self.get_session()

        if not session:
            context['error'] = 'Attendance session not found or access denied.'
            return context

        # Get enrolled students for this class
        enrollments = StudentEnrollment.objects.filter(
            class_obj=session.class_subject_teacher.class_obj,
            status='ACTIVE'
        ).select_related('student')

        # Get existing attendance records
        existing_records = AttendanceRecord.objects.filter(
            attendance_session=session,
            attendance_date=session.session_date
        ).values_list('student_id', 'status', 'arrival_time')
        record_dict = {str(student_id): (status, arrival_time) for student_id, status, arrival_time in existing_records}

        # Create form
        form = BulkAttendanceMarkForm(enrollments, data=self.request.POST or None)

        context.update({
            'session': session,
            'form': form,
            'enrollments': enrollments,
            'record_dict': record_dict,
        })

        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(*args, **kwargs)
        session = self.get_session()

        if not session:
            messages.error(request, 'Attendance session not found or access denied.')
            return redirect('attendance:events_calendar')

        form = context['form']

        if form.is_valid():
            enrollments = StudentEnrollment.objects.filter(
                class_obj=session.class_subject_teacher.class_obj,
                status='ACTIVE'
            )

            for enrollment in enrollments:
                field_name = f'student_{enrollment.id}'
                arrival_field_name = f'arrival_{enrollment.id}'

                if field_name in form.cleaned_data:
                    status = form.cleaned_data[field_name]
                    arrival_time = form.cleaned_data.get(arrival_field_name)

                    # Create or update attendance record
                    record, created = AttendanceRecord.objects.update_or_create(
                        student=enrollment.student,
                        attendance_session=session,
                        attendance_date=session.session_date,
                        defaults={
                            'status': status,
                            'arrival_time': arrival_time,
                            'recorded_by': request.user,
                        }
                    )

            messages.success(request, f'Attendance marked for {enrollments.count()} students.')
            return redirect('attendance:events_calendar')
        else:
            return render(request, self.template_name, context)


class StudentAttendanceSubmitView(LoginRequiredMixin, CreateView):
    """Student submit/confirm attendance for a subject"""
    model = AttendanceRecord
    form_class = StudentAttendanceSubmitForm
    template_name = 'attendance/student_submit.html'
    login_url = 'accounts:login'

    @method_decorator(login_required(login_url='accounts:login'))
    def dispatch(self, *args, **kwargs):
        if self.request.user.role != 'STUDENT':
            messages.error(self.request, 'Only students can submit attendance.')
            return redirect('dashboard')
        return super().dispatch(*args, **kwargs)

    def get_session(self):
        """Get attendance session and verify authorization"""
        session_id = self.kwargs.get('session_id')
        try:
            session = AttendanceSession.objects.get(id=session_id)
            # Verify student is enrolled in this class
            if not StudentEnrollment.objects.filter(
                student=self.request.user,
                class_obj=session.class_subject_teacher.class_obj,
                status='ACTIVE'
            ).exists():
                return None
            return session
        except AttendanceSession.DoesNotExist:
            return None

    def get(self, request, *args, **kwargs):
        """For LURING sessions, redirect directly to QR code display"""
        session = self.get_session()
        
        if not session:
            messages.error(request, 'Attendance session not found or access denied.')
            return redirect('attendance:events_calendar')
        
        # For LURING sessions, go directly to QR code display
        if session.session_type == 'LURING':
            return redirect('attendance:qr_code_display', session_id=session.id)
        
        # For DARING sessions, show the form
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = self.get_session()

        if not session:
            context['error'] = 'Attendance session not found or access denied.'
            return context

        # Check if already submitted
        existing = AttendanceRecord.objects.filter(
            student=self.request.user,
            attendance_session=session,
            attendance_date=session.session_date
        ).first()

        context.update({
            'session': session,
            'existing_record': existing,
        })

        return context

    def form_valid(self, form):
        session = self.get_session()

        if not session:
            messages.error(self.request, 'Attendance session not found or access denied.')
            return redirect('attendance:events_calendar')

        # Create or update attendance record
        form.instance.student = self.request.user
        form.instance.attendance_session = session
        form.instance.attendance_date = session.session_date
        form.instance.recorded_by = None  # Student recorded themselves

        # If arrival_time not provided, use current time
        if not form.instance.arrival_time:
            form.instance.arrival_time = datetime.now().time()

        messages.success(self.request, 'Attendance submitted successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        session_id = self.kwargs.get('session_id')
        try:
            session = AttendanceSession.objects.get(id=session_id)
            # Redirect to QR display only for LURING sessions
            if session.session_type == 'LURING':
                return reverse_lazy('attendance:qr_code_display', kwargs={'session_id': session_id})
        except AttendanceSession.DoesNotExist:
            pass
        # For DARING and other types, go back to calendar
        return reverse_lazy('attendance:events_calendar')


class StudentAttendanceHistoryView(LoginRequiredMixin, ListView):
    """Student view their attendance history"""
    model = AttendanceRecord
    template_name = 'attendance/student_history.html'
    context_object_name = 'records'
    paginate_by = 25
    login_url = 'accounts:login'

    @method_decorator(login_required(login_url='accounts:login'))
    def dispatch(self, *args, **kwargs):
        if self.request.user.role != 'STUDENT':
            messages.error(self.request, 'Only students can view their attendance history.')
            return redirect('dashboard')
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        return AttendanceRecord.objects.filter(
            student=self.request.user
        ).select_related('attendance_session', 'recorded_by').order_by('-attendance_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Calculate stats
        all_records = AttendanceRecord.objects.filter(student=self.request.user)
        total = all_records.count()

        if total > 0:
            present = all_records.filter(status='PRESENT').count()
            absent = all_records.filter(status='ABSENT').count()
            permission = all_records.filter(status='PERMISSION').count()
            sick = all_records.filter(status='SICK').count()

            context.update({
                'stats': {
                    'total': total,
                    'present': present,
                    'absent': absent,
                    'permission': permission,
                    'sick': sick,
                    'percentage': round((present / total * 100), 2) if total > 0 else 0,
                }
            })

        return context

# ============ TEACHER VIEWS FOR STATISTICS & REPORTS ============

from functools import wraps
from accounts.views import role_required
from attendance.utils import (
    export_attendance_to_pdf_daily,
    export_attendance_to_xlsx_daily,
    export_attendance_to_pdf_semester,
    export_attendance_to_xlsx_semester,
)


class TeacherAttendanceStatsView(LoginRequiredMixin, TemplateView):
    """Teacher view attendance statistics for a specific day"""
    template_name = 'attendance/teacher_stats_daily.html'
    login_url = 'accounts:login'

    @method_decorator(login_required(login_url='accounts:login'))
    def dispatch(self, *args, **kwargs):
        if self.request.user.role != 'TEACHER':
            messages.error(self.request, 'Only teachers can view attendance statistics.')
            return redirect('accounts:dashboard')
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        filter_type = self.request.GET.get('filter_type', 'date')
        context['filter_type'] = filter_type

        # Get teacher's classes and subjects
        teacher_class_subjects = ClassSubjectTeacher.objects.filter(
            teacher=self.request.user
        ).select_related('class_obj', 'subject')

        context['class_subjects'] = teacher_class_subjects

        if filter_type == 'session':
            # Filter by attendance session
            session_id = self.request.GET.get('session_id')
            if session_id:
                try:
                    session = AttendanceSession.objects.get(id=session_id, class_subject_teacher__teacher=self.request.user)
                    records = AttendanceRecord.objects.filter(
                        attendance_session=session
                    ).select_related('student', 'recorded_by').order_by('student__first_name', 'student__last_name')

                    context.update({
                        'records': records,
                        'class_obj': session.class_subject_teacher.class_obj,
                        'subject': session.class_subject_teacher.subject,
                        'date': session.session_date,
                        'session': session,
                    })
                except AttendanceSession.DoesNotExist:
                    messages.error(self.request, 'Attendance session not found.')
        else:
            # Filter by date and class-subject
            class_subject_id = self.request.GET.get('class_subject_id')
            date_str = self.request.GET.get('date', str(date.today()))

            if class_subject_id:
                try:
                    attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    class_subject = ClassSubjectTeacher.objects.get(
                        id=class_subject_id,
                        teacher=self.request.user
                    )

                    # Get all sessions for this class-subject on that date
                    sessions = AttendanceSession.objects.filter(
                        class_subject_teacher=class_subject,
                        session_date=attendance_date
                    )

                    records = AttendanceRecord.objects.filter(
                        attendance_session__in=sessions
                    ).select_related('student', 'recorded_by').order_by('student__first_name', 'student__last_name')

                    context.update({
                        'records': records,
                        'class_obj': class_subject.class_obj,
                        'subject': class_subject.subject,
                        'date': attendance_date,
                    })
                except (ClassSubjectTeacher.DoesNotExist, ValueError):
                    pass

        # Calculate statistics
        records = context.get('records', AttendanceRecord.objects.none())
        total = records.count()
        present_count = records.filter(status='PRESENT').count()
        absent_count = records.filter(status='ABSENT').count()
        permission_count = records.filter(status='PERMISSION').count()
        sick_count = records.filter(status='SICK').count()

        context.update({
            'total': total,
            'present_count': present_count,
            'absent_count': absent_count,
            'permission_count': permission_count,
            'sick_count': sick_count,
            'attendance_percentage': (present_count / total * 100) if total > 0 else 0,
        })

        return context


class ExportDailyStatsView(LoginRequiredMixin, TemplateView):
    """Export daily attendance statistics to PDF or XLSX (per-subject)"""
    login_url = 'accounts:login'

    @method_decorator(login_required(login_url='accounts:login'))
    def dispatch(self, *args, **kwargs):
        if self.request.user.role != 'TEACHER':
            messages.error(self.request, 'Only teachers can export attendance statistics.')
            return redirect('accounts:dashboard')
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        export_format = request.GET.get('format', 'pdf')
        class_subject_id = request.GET.get('class_subject_id')
        date_str = request.GET.get('date', str(date.today()))

        try:
            attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            class_subject = ClassSubjectTeacher.objects.get(
                id=class_subject_id,
                teacher=request.user
            )

            sessions = AttendanceSession.objects.filter(
                class_subject_teacher=class_subject,
                session_date=attendance_date
            )

            records = AttendanceRecord.objects.filter(
                attendance_session__in=sessions
            ).select_related('student', 'recorded_by')

            if export_format == 'xlsx':
                return export_attendance_to_xlsx_daily(
                    class_subject.class_obj,
                    attendance_date,
                    records,
                    subject=class_subject.subject
                )
            else:
                return export_attendance_to_pdf_daily(
                    class_subject.class_obj,
                    attendance_date,
                    records,
                    subject=class_subject.subject
                )

        except (ClassSubjectTeacher.DoesNotExist, ValueError) as e:
            messages.error(request, 'Invalid class-subject or date provided.')
            return redirect('attendance:teacher_stats_daily')


class TeacherSemesterReportView(LoginRequiredMixin, TemplateView):
    """Teacher view semester attendance report"""
    template_name = 'attendance/teacher_semester_report.html'
    login_url = 'accounts:login'

    @method_decorator(login_required(login_url='accounts:login'))
    def dispatch(self, *args, **kwargs):
        if self.request.user.role != 'TEACHER':
            messages.error(self.request, 'Only teachers can view semester reports.')
            return redirect('accounts:dashboard')
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get teacher's class-subject combinations
        teacher_class_subjects = ClassSubjectTeacher.objects.filter(
            teacher=self.request.user
        ).select_related('class_obj', 'subject')

        context['class_subjects'] = teacher_class_subjects

        class_subject_id = self.request.GET.get('class_subject_id')
        semester = int(self.request.GET.get('semester', 1))
        context['semester'] = semester

        if class_subject_id:
            try:
                class_subject = ClassSubjectTeacher.objects.get(
                    id=class_subject_id,
                    teacher=self.request.user
                )
                context['class_subject'] = class_subject
                context['class_obj'] = class_subject.class_obj
                context['subject'] = class_subject.subject

                current_year = date.today().year
                if semester == 1:
                    start_date = date(current_year, 7, 1)
                    end_date = date(current_year, 12, 31)
                    semester_label = "Semester 1 (July - December)"
                else:
                    start_date = date(current_year - 1, 1, 1) if date.today().month < 7 else date(current_year, 1, 1)
                    end_date = date(current_year, 6, 30)
                    semester_label = "Semester 2 (January - June)"

                context['semester_label'] = semester_label
                context['start_date'] = start_date
                context['end_date'] = end_date

                enrollments = StudentEnrollment.objects.filter(
                    class_obj=class_subject.class_obj,
                    status='ACTIVE'
                ).select_related('student').order_by('student__first_name', 'student__last_name')

                summaries = []
                for enrollment in enrollments:
                    # Get attendance for this student-subject combination
                    sessions = AttendanceSession.objects.filter(
                        class_subject_teacher=class_subject,
                        session_date__range=[start_date, end_date]
                    )

                    total_records = AttendanceRecord.objects.filter(
                        student=enrollment.student,
                        attendance_session__in=sessions
                    )

                    total_days = total_records.count()
                    present_count = total_records.filter(status='PRESENT').count()
                    absent_count = total_records.filter(status='ABSENT').count()
                    permission_count = total_records.filter(status='PERMISSION').count()
                    sick_count = total_records.filter(status='SICK').count()

                    percentage = (present_count / total_days * 100) if total_days > 0 else 0

                    summaries.append({
                        'student': enrollment.student,
                        'total_days': total_days,
                        'present': present_count,
                        'absent': absent_count,
                        'permission': permission_count,
                        'sick': sick_count,
                        'percentage': percentage,
                    })

                sort_by = self.request.GET.get('sort', 'name')
                if sort_by == 'percentage_asc':
                    summaries.sort(key=lambda x: x['percentage'])
                elif sort_by == 'percentage_desc':
                    summaries.sort(key=lambda x: x['percentage'], reverse=True)
                else:
                    summaries.sort(key=lambda x: x['student'].get_full_name())

                context['summaries'] = summaries
                context['total_students'] = len(summaries)
                context['sort'] = sort_by

            except ClassSubjectTeacher.DoesNotExist:
                messages.error(self.request, 'Class-Subject not found.')

        return context


class ExportSemesterReportView(LoginRequiredMixin, TemplateView):
    """Export semester attendance report to PDF or XLSX (per-subject)"""
    login_url = 'accounts:login'

    @method_decorator(login_required(login_url='accounts:login'))
    def dispatch(self, *args, **kwargs):
        if self.request.user.role != 'TEACHER':
            messages.error(self.request, 'Only teachers can export semester reports.')
            return redirect('accounts:dashboard')
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        export_format = request.GET.get('format', 'pdf')
        class_subject_id = request.GET.get('class_subject_id')
        semester = int(request.GET.get('semester', 1))

        try:
            class_subject = ClassSubjectTeacher.objects.get(
                id=class_subject_id,
                teacher=request.user
            )

            current_year = date.today().year
            if semester == 1:
                start_date = date(current_year, 7, 1)
                end_date = date(current_year, 12, 31)
            else:
                start_date = date(current_year - 1, 1, 1) if date.today().month < 7 else date(current_year, 1, 1)
                end_date = date(current_year, 6, 30)

            enrollments = StudentEnrollment.objects.filter(
                class_obj=class_subject.class_obj,
                status='ACTIVE'
            ).select_related('student').order_by('student__first_name', 'student__last_name')

            sessions = AttendanceSession.objects.filter(
                class_subject_teacher=class_subject,
                session_date__range=[start_date, end_date]
            )

            summaries = []
            for enrollment in enrollments:
                total_records = AttendanceRecord.objects.filter(
                    student=enrollment.student,
                    attendance_session__in=sessions
                )

                total_days = total_records.count()
                present_count = total_records.filter(status='PRESENT').count()
                absent_count = total_records.filter(status='ABSENT').count()
                sick_count = total_records.filter(status='SICK').count()

                percentage = (present_count / total_days * 100) if total_days > 0 else 0

                summaries.append({
                    'student': enrollment.student,
                    'total_days': total_days,
                    'present': present_count,
                    'absent': absent_count,
                    'sick': sick_count,
                    'percentage': percentage,
                })

            if export_format == 'xlsx':
                return export_attendance_to_xlsx_semester(
                    class_subject.class_obj,
                    semester,
                    summaries,
                    start_date,
                    end_date,
                    subject=class_subject.subject
                )
            else:
                return export_attendance_to_pdf_semester(
                    class_subject.class_obj,
                    semester,
                    summaries,
                    start_date,
                    end_date,
                    subject=class_subject.subject
                )

        except ClassSubjectTeacher.DoesNotExist:
            messages.error(request, 'Class-Subject not found.')
            return redirect('attendance:teacher_semester_report')


# ============ QR CODE ATTENDANCE FEATURES ============


class StudentQRCodeDisplayView(LoginRequiredMixin, TemplateView):
    """Student displays QR code for teacher to scan (LURING sessions only)"""
    template_name = 'attendance/student_qr_display.html'
    login_url = 'accounts:login'

    @method_decorator(login_required(login_url='accounts:login'))
    def dispatch(self, *args, **kwargs):
        if self.request.user.role != 'STUDENT':
            messages.error(self.request, 'Only students can view QR code.')
            return redirect('dashboard')
        return super().dispatch(*args, **kwargs)

    def get_session(self):
        """Get attendance session and verify authorization"""
        session_id = self.kwargs.get('session_id')
        try:
            session = AttendanceSession.objects.get(id=session_id)

            # Verify student is enrolled in this class
            if not StudentEnrollment.objects.filter(
                student=self.request.user,
                class_obj=session.class_subject_teacher.class_obj,
                status='ACTIVE'
            ).exists():
                return None

            # Verify it's a LURING session
            if session.session_type != 'LURING':
                return None

            return session
        except AttendanceSession.DoesNotExist:
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = self.get_session()

        if not session:
            context['error'] = 'Attendance session not found or not available.'
            return context

        # Get student enrollment
        try:
            enrollment = StudentEnrollment.objects.get(
                student=self.request.user,
                class_obj=session.class_subject_teacher.class_obj,
                status='ACTIVE'
            )
        except StudentEnrollment.DoesNotExist:
            context['error'] = 'You are not enrolled in this class.'
            return context

        # Generate unique QR data for this student: enrollment_id:session_id:timestamp
        from django.utils import timezone
        timestamp = timezone.now().isoformat()
        qr_data = f"{enrollment.id}:{session.id}:{timestamp}"
        
        # Get QR code as base64 data URI
        qr_code = get_qr_code_base64(qr_data, size=250)

        context.update({
            'session': session,
            'enrollment': enrollment,
            'qr_code': qr_code,
            'qr_data': qr_data,
            'session_info': {
                'class_name': session.class_subject_teacher.class_obj.name,
                'subject_name': session.class_subject_teacher.subject.name,
                'teacher_name': session.class_subject_teacher.teacher.get_full_name(),
                'session_date': session.session_date,
                'session_time': session.created_at.strftime('%H:%M'),
            },
            'expires_in_seconds': 60,
        })

        return context


class TeacherScanQRCodeView(LoginRequiredMixin, TemplateView):
    """Teacher scans QR codes from students to mark attendance"""
    template_name = 'attendance/teacher_qr_scan.html'
    login_url = 'accounts:login'

    @method_decorator(login_required(login_url='accounts:login'))
    def dispatch(self, *args, **kwargs):
        if self.request.user.role != 'TEACHER':
            messages.error(self.request, 'Only teachers can scan QR codes.')
            return redirect('dashboard')
        return super().dispatch(*args, **kwargs)

    def get_session(self):
        """Get attendance session and verify authorization"""
        session_id = self.kwargs.get('session_id')
        try:
            session = AttendanceSession.objects.get(id=session_id)

            # Verify teacher owns this session
            if session.class_subject_teacher.teacher != self.request.user:
                return None

            # Verify it's a LURING session
            if session.session_type != 'LURING':
                return None

            return session
        except AttendanceSession.DoesNotExist:
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = self.get_session()

        if not session:
            context['error'] = 'Attendance session not found or access denied.'
            return context

        # Get enrolled students
        enrollments = StudentEnrollment.objects.filter(
            class_obj=session.class_subject_teacher.class_obj,
            status='ACTIVE'
        ).select_related('student').order_by('student__first_name', 'student__last_name')

        # Get students already marked via QR today
        marked_records = AttendanceRecord.objects.filter(
            attendance_session=session,
            attendance_date=session.session_date
        ).select_related('student').order_by('-recorded_at')

        context.update({
            'session': session,
            'enrollments': enrollments,
            'marked_records': marked_records,
            'total_students': enrollments.count(),
            'marked_count': marked_records.count(),
        })

        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(*args, **kwargs)
        session = self.get_session()

        if not session:
            messages.error(request, 'Attendance session not found or access denied.')
            return redirect('attendance:events_calendar')

        qr_token = request.POST.get('qr_token', '').strip()

        if not qr_token:
            context['error'] = 'Please scan a QR code.'
            return render(request, self.template_name, context)

        # Check if QR token is valid
        if not session.is_qr_token_valid(qr_token):
            if not session.is_qr_token_expired():
                messages.error(request, 'Invalid QR code token.')
            else:
                messages.error(request, 'QR code has expired. Please ask for a fresh one.')
            return render(request, self.template_name, context)

        # Find which student this token belongs to
        # (In a real app, you might have a mapping table, but for now
        # we just search for the most recent generated record)
        # Actually, we'll use a simpler approach: ask for student ID with QR

        context['success'] = 'QR code scanned successfully! Now select a student to mark.'
        return render(request, self.template_name, context)


class MarkAttendanceFromQRAPIView(LoginRequiredMixin, View):
    """API endpoint to mark attendance from QR code scan"""
    login_url = 'accounts:login'

    def post(self, request):
        """Mark a student as present using QR data (enrollment_id:session_id:timestamp)"""
        import sys

        # Debug: Check if request.body is accessible
        try:
            body_unicode = request.body.decode('utf-8')
            if not body_unicode:
                print("ERROR: Request body is empty!", file=sys.stderr)
                return JsonResponse({'error': 'Request body is empty'}, status=400)
        except UnicodeDecodeError as e:
            print(f"ERROR: Unicode decode error - {str(e)}", file=sys.stderr)
            return JsonResponse({'error': f'Invalid encoding: {str(e)}'}, status=400)
        except Exception as e:
            print(f"ERROR: Failed to read request body - {str(e)}", file=sys.stderr)
            return JsonResponse({'error': f'Cannot read request body: {str(e)}'}, status=400)

        try:
            # Parse JSON request body
            try:
                data = json.loads(body_unicode)
            except json.JSONDecodeError as e:
                print(f"ERROR: JSON decode error - {str(e)}", file=sys.stderr)
                return JsonResponse({'error': f'Invalid JSON format: {str(e)}'}, status=400)

            qr_data = data.get('qr_data', '').strip()
            session_id = data.get('session_id')

            print(f"DEBUG: qr_data={qr_data}, session_id={session_id}", file=sys.stderr)

            # Verify teacher authorization
            if request.user.role != 'TEACHER':
                return JsonResponse({'error': 'Only teachers can mark attendance.'}, status=403)

            if not qr_data:
                return JsonResponse({'error': 'QR data is required.'}, status=400)

            if not session_id:
                return JsonResponse({'error': 'Session ID is required.'}, status=400)

            # Parse QR data: enrollment_id:session_id:timestamp
            parts = qr_data.split(':')
            if len(parts) < 2:
                return JsonResponse({'error': 'Invalid QR code format. Expected enrollment_id:session_id:timestamp'}, status=400)

            enrollment_id = parts[0]
            qr_session_id = parts[1]
            # Timestamp might have colons (ISO format), we only need the first two parts

            # Get session
            try:
                session = AttendanceSession.objects.get(id=session_id)
            except AttendanceSession.DoesNotExist:
                return JsonResponse({'error': 'Attendance session not found.'}, status=404)

            # Verify teacher owns this session
            if session.class_subject_teacher.teacher != request.user:
                return JsonResponse({'error': 'Access denied. You do not own this session.'}, status=403)

            # Verify it's LURING session
            if session.session_type != 'LURING':
                return JsonResponse({'error': 'This is not a LURING (in-person) session.'}, status=400)

            # Verify QR session matches current session
            if str(qr_session_id) != str(session_id):
                return JsonResponse({'error': 'QR code is from a different session.'}, status=400)

            # Get student enrollment by ID
            try:
                enrollment = StudentEnrollment.objects.select_related('student').get(
                    id=enrollment_id,
                    status='ACTIVE'
                )
            except StudentEnrollment.DoesNotExist:
                return JsonResponse({'error': f'Student enrollment not found (ID: {enrollment_id}).'}, status=404)

            # Verify student is in this class
            if enrollment.class_obj != session.class_subject_teacher.class_obj:
                return JsonResponse({'error': 'Student is not enrolled in this class.'}, status=400)

            # Create or update attendance record
            record, created = AttendanceRecord.objects.update_or_create(
                student=enrollment.student,
                attendance_session=session,
                attendance_date=session.session_date,
                defaults={
                    'status': 'PRESENT',
                    'arrival_time': datetime.now().time(),
                    'recorded_by': request.user,
                }
            )

            print(f"SUCCESS: {enrollment.student.get_full_name()} marked as present", file=sys.stderr)

            return JsonResponse({
                'success': True,
                'message': f'{enrollment.student.get_full_name()} marked as present.',
                'student_name': enrollment.student.get_full_name(),
                'student_id_in_class': enrollment.student_id_in_class or 'N/A',
                'created': created,
            }, status=200)

        except Exception as e:
            import traceback
            error_msg = f"Exception in MarkAttendanceFromQRAPIView: {str(e)}"
            print(f"ERROR: {error_msg}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return JsonResponse({'error': error_msg}, status=500)


class QRTokenRefreshAPIView(LoginRequiredMixin, View):
    """API endpoint to refresh QR token and return new token with base64 image"""
    login_url = 'accounts:login'

    def get(self, request, session_id):
        try:
            session = AttendanceSession.objects.get(id=session_id)

            # Verify it's a LURING session
            if session.session_type != 'LURING':
                return JsonResponse(
                    {'error': 'Not a LURING session'},
                    status=400
                )

            # Check if user is student in this class or teacher of this session
            is_student = StudentEnrollment.objects.filter(
                student=request.user,
                class_obj=session.class_subject_teacher.class_obj,
                status='ACTIVE'
            ).exists()

            is_teacher = session.class_subject_teacher.teacher == request.user

            if not (is_student or is_teacher):
                return JsonResponse(
                    {'error': 'Access denied'},
                    status=403
                )

            # Check if token has expired, regenerate if needed
            if session.is_qr_token_expired():
                session.generate_new_qr_token()

            # Get QR code as base64
            qr_data = get_qr_code_base64(session.qr_token, size=250)

            return JsonResponse({
                'success': True,
                'token': session.qr_token,
                'qr_image': qr_data,
                'expires_at': session.qr_token_expires_at.isoformat(),
                'generated_at': session.qr_token_generated_at.isoformat(),
            })

        except AttendanceSession.DoesNotExist:
            return JsonResponse(
                {'error': 'Session not found'},
                status=404
            )
        except Exception as e:
            return JsonResponse(
                {'error': f'Error refreshing QR code: {str(e)}'},
                status=500
            )
