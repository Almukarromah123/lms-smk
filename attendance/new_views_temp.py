
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
    login_url = 'login'

    @method_decorator(login_required(login_url='login'))
    def dispatch(self, *args, **kwargs):
        if self.request.user.role != 'TEACHER':
            messages.error(self.request, 'Only teachers can view attendance statistics.')
            return redirect('accounts:dashboard')
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        filter_type = self.request.GET.get('filter_type', 'date')
        context['filter_type'] = filter_type

        # Get teacher's classes
        teacher_classes = Class.objects.filter(
            subject_teachers__teacher=self.request.user
        ).distinct()
        context['classes'] = teacher_classes

        if filter_type == 'session':
            # Filter by attendance session
            session_id = self.request.GET.get('session_id')
            if session_id:
                try:
                    session = AttendanceSession.objects.get(id=session_id, teacher=self.request.user)
                    records = AttendanceRecord.objects.filter(
                        class_obj=session.class_obj,
                        attendance_date=session.session_date
                    ).select_related('student', 'recorded_by').order_by('student__first_name', 'student__last_name')

                    context.update({
                        'records': records,
                        'class_obj': session.class_obj,
                        'date': session.session_date,
                        'session': session,
                    })
                except AttendanceSession.DoesNotExist:
                    messages.error(self.request, 'Attendance session not found.')
        else:
            # Filter by date
            class_id = self.request.GET.get('class_id')
            date_str = self.request.GET.get('date', str(date.today()))

            if class_id:
                try:
                    attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    class_obj = Class.objects.get(id=class_id, subject_teachers__teacher=self.request.user)
                    records = AttendanceRecord.objects.filter(
                        class_obj=class_obj,
                        attendance_date=attendance_date
                    ).select_related('student', 'recorded_by').order_by('student__first_name', 'student__last_name')

                    context.update({
                        'records': records,
                        'class_obj': class_obj,
                        'date': attendance_date,
                    })
                except (Class.DoesNotExist, ValueError):
                    pass

        # Calculate statistics
        records = context.get('records', AttendanceRecord.objects.none())
        total = records.count()
        present_count = records.filter(status='PRESENT').count()
        absent_count = records.filter(status='ABSENT').count()
        sick_count = records.filter(status='SICK').count()

        context.update({
            'total': total,
            'present_count': present_count,
            'absent_count': absent_count,
            'sick_count': sick_count,
            'attendance_percentage': (present_count / total * 100) if total > 0 else 0,
        })

        return context


class ExportDailyStatsView(LoginRequiredMixin, TemplateView):
    """Export daily attendance statistics to PDF or XLSX"""
    login_url = 'login'

    @method_decorator(login_required(login_url='login'))
    def dispatch(self, *args, **kwargs):
        if self.request.user.role != 'TEACHER':
            messages.error(self.request, 'Only teachers can export attendance statistics.')
            return redirect('accounts:dashboard')
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        export_format = request.GET.get('format', 'pdf')
        class_id = request.GET.get('class_id')
        date_str = request.GET.get('date', str(date.today()))

        try:
            attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            class_obj = Class.objects.get(id=class_id, subject_teachers__teacher=request.user)
            records = AttendanceRecord.objects.filter(
                class_obj=class_obj,
                attendance_date=attendance_date
            ).select_related('student', 'recorded_by')

            if export_format == 'xlsx':
                return export_attendance_to_xlsx_daily(class_obj, attendance_date, records)
            else:
                return export_attendance_to_pdf_daily(class_obj, attendance_date, records)

        except (Class.DoesNotExist, ValueError) as e:
            messages.error(request, 'Invalid class or date provided.')
            return redirect('attendance:teacher_stats_daily')


class TeacherSemesterReportView(LoginRequiredMixin, TemplateView):
    """Teacher view semester attendance report"""
    template_name = 'attendance/teacher_semester_report.html'
    login_url = 'login'

    @method_decorator(login_required(login_url='login'))
    def dispatch(self, *args, **kwargs):
        if self.request.user.role != 'TEACHER':
            messages.error(self.request, 'Only teachers can view semester reports.')
            return redirect('accounts:dashboard')
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        teacher_classes = Class.objects.filter(
            subject_teachers__teacher=self.request.user
        ).distinct()
        context['classes'] = teacher_classes

        class_id = self.request.GET.get('class_id')
        semester = int(self.request.GET.get('semester', 1))
        context['semester'] = semester

        if class_id:
            try:
                class_obj = Class.objects.get(id=class_id, subject_teachers__teacher=self.request.user)
                context['class_obj'] = class_obj

                current_year = date.today().year
                if semester == 1:
                    start_date = date(current_year, 1, 1)
                    end_date = date(current_year, 6, 30)
                    semester_label = "Semester 1 (January - June)"
                else:
                    start_date = date(current_year, 7, 1)
                    end_date = date(current_year, 12, 31)
                    semester_label = "Semester 2 (July - December)"

                context['semester_label'] = semester_label
                context['start_date'] = start_date
                context['end_date'] = end_date

                enrollments = StudentEnrollment.objects.filter(
                    class_obj=class_obj,
                    status='ACTIVE'
                ).select_related('student').order_by('student__first_name', 'student__last_name')

                summaries = []
                for enrollment in enrollments:
                    total_records = AttendanceRecord.objects.filter(
                        student=enrollment.student,
                        class_obj=class_obj,
                        attendance_date__range=[start_date, end_date]
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

            except Class.DoesNotExist:
                messages.error(self.request, 'Class not found.')

        return context


class ExportSemesterReportView(LoginRequiredMixin, TemplateView):
    """Export semester attendance report to PDF or XLSX"""
    login_url = 'login'

    @method_decorator(login_required(login_url='login'))
    def dispatch(self, *args, **kwargs):
        if self.request.user.role != 'TEACHER':
            messages.error(self.request, 'Only teachers can export semester reports.')
            return redirect('accounts:dashboard')
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        export_format = request.GET.get('format', 'pdf')
        class_id = request.GET.get('class_id')
        semester = int(request.GET.get('semester', 1))

        try:
            class_obj = Class.objects.get(id=class_id, subject_teachers__teacher=request.user)

            current_year = date.today().year
            if semester == 1:
                start_date = date(current_year, 1, 1)
                end_date = date(current_year, 6, 30)
            else:
                start_date = date(current_year, 7, 1)
                end_date = date(current_year, 12, 31)

            enrollments = StudentEnrollment.objects.filter(
                class_obj=class_obj,
                status='ACTIVE'
            ).select_related('student').order_by('student__first_name', 'student__last_name')

            summaries = []
            for enrollment in enrollments:
                total_records = AttendanceRecord.objects.filter(
                    student=enrollment.student,
                    class_obj=class_obj,
                    attendance_date__range=[start_date, end_date]
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
                return export_attendance_to_xlsx_semester(class_obj, semester, summaries, start_date, end_date)
            else:
                return export_attendance_to_pdf_semester(class_obj, semester, summaries, start_date, end_date)

        except Class.DoesNotExist:
            messages.error(request, 'Class not found.')
            return redirect('attendance:teacher_semester_report')
