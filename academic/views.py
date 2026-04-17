from django.shortcuts import render, redirect
from django.views.generic import FormView, ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from .models import StudentEnrollment, Class
from .forms import BulkStudentEnrollmentForm, BulkTeacherEnrollmentForm, StudentCredentialExportForm, generate_student_password
import csv
from datetime import datetime
import io


class BulkEnrollmentHubView(LoginRequiredMixin, TemplateView):
    """Landing page untuk memilih bulk enrollment siswa atau guru"""
    template_name = 'academic/bulk_enrollment_hub.html'
    login_url = 'accounts:login'

    def dispatch(self, *args, **kwargs):
        # Only admin can access
        if self.request.user.role != 'ADMIN':
            messages.error(self.request, 'Hanya admin yang dapat melakukan bulk enrollment.')
            return redirect('accounts:dashboard')
        return super().dispatch(*args, **kwargs)


class BulkStudentEnrollmentView(LoginRequiredMixin, FormView):
    """Bulk enroll students from Excel file"""
    template_name = 'academic/bulk_student_enrollment.html'
    form_class = BulkStudentEnrollmentForm
    success_url = reverse_lazy('academic:student_enrollment_success')

    @method_decorator(login_required(login_url='accounts:login'))
    def dispatch(self, *args, **kwargs):
        # Only admin can bulk enroll
        if self.request.user.role != 'ADMIN':
            messages.error(self.request, 'Hanya admin yang dapat melakukan bulk enrollment.')
            return redirect('accounts:dashboard')
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        """Process the Excel file"""
        result = form.process_excel()

        # Store result in session
        self.request.session['enrollment_result'] = result
        self.request.session['enrollment_timestamp'] = datetime.now().isoformat()

        messages.success(
            self.request,
            f'Berhasil menambahkan {result["success"]} siswa. '
            f'{result["failed"]} baris gagal diproses.'
        )

        return super().form_valid(form)


class BulkTeacherEnrollmentView(LoginRequiredMixin, FormView):
    """Bulk enroll teachers from Excel file"""
    template_name = 'academic/bulk_teacher_enrollment.html'
    form_class = BulkTeacherEnrollmentForm
    success_url = reverse_lazy('academic:teacher_enrollment_success')

    @method_decorator(login_required(login_url='accounts:login'))
    def dispatch(self, *args, **kwargs):
        # Only admin can bulk enroll
        if self.request.user.role != 'ADMIN':
            messages.error(self.request, 'Hanya admin yang dapat melakukan bulk enrollment.')
            return redirect('accounts:dashboard')
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        """Process the Excel file"""
        result = form.process_excel()

        # Store result in session
        self.request.session['enrollment_result'] = result
        self.request.session['enrollment_timestamp'] = datetime.now().isoformat()

        messages.success(
            self.request,
            f'Berhasil menambahkan {result["success"]} guru. '
            f'{result["failed"]} baris gagal diproses.'
        )

        return super().form_valid(form)


class StudentEnrollmentSuccessView(LoginRequiredMixin, ListView):
    """Display student bulk enrollment results"""
    template_name = 'academic/student_enrollment_success.html'
    context_object_name = 'accounts'

    def get_queryset(self):
        # Get result from session
        result = self.request.session.get('enrollment_result', {})
        return result.get('accounts', [])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        result = self.request.session.get('enrollment_result', {})
        context['success_count'] = result.get('success', 0)
        context['failed_count'] = result.get('failed', 0)
        context['errors'] = result.get('errors', [])
        context['enrollment_type'] = 'siswa'
        return context


class TeacherEnrollmentSuccessView(LoginRequiredMixin, ListView):
    """Display teacher bulk enrollment results"""
    template_name = 'academic/teacher_enrollment_success.html'
    context_object_name = 'accounts'

    def get_queryset(self):
        # Get result from session
        result = self.request.session.get('enrollment_result', {})
        return result.get('accounts', [])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        result = self.request.session.get('enrollment_result', {})
        context['success_count'] = result.get('success', 0)
        context['failed_count'] = result.get('failed', 0)
        context['errors'] = result.get('errors', [])
        context['enrollment_type'] = 'guru'
        return context


class BulkEnrollmentSuccessView(LoginRequiredMixin, ListView):
    """Display bulk enrollment results (legacy - redirect to student success)"""
    template_name = 'academic/enrollment_success.html'
    context_object_name = 'accounts'

    def get_queryset(self):
        # Get result from session
        result = self.request.session.get('enrollment_result', {})
        return result.get('accounts', [])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        result = self.request.session.get('enrollment_result', {})
        context['success_count'] = result.get('success', 0)
        context['failed_count'] = result.get('failed', 0)
        context['errors'] = result.get('errors', [])
        return context


class ExportStudentCredentialsView(LoginRequiredMixin, FormView):
    """Export student credentials to PDF or CSV"""
    template_name = 'academic/export_credentials.html'
    form_class = StudentCredentialExportForm
    success_url = reverse_lazy('academic:bulk_enrollment')

    @method_decorator(login_required(login_url='accounts:login'))
    def dispatch(self, *args, **kwargs):
        if self.request.user.role != 'ADMIN':
            messages.error(self.request, 'Hanya admin yang dapat export credentials.')
            return redirect('accounts:dashboard')
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        """Export credentials in requested format"""
        class_obj = form.cleaned_data['class_obj']
        format_choice = form.cleaned_data['format_choice']

        # Get all students in class
        enrollments = StudentEnrollment.objects.filter(
            class_obj=class_obj,
            status='ACTIVE'
        ).select_related('student')

        if format_choice == 'csv':
            return self._export_csv(class_obj, enrollments)
        else:
            return self._export_pdf(class_obj, enrollments)

    def _export_csv(self, class_obj, enrollments):
        """Export as CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="credentials_{class_obj.id}.csv"'

        writer = csv.writer(response, encoding='utf-8')
        writer.writerow(['No.', 'Email', 'Nama Lengkap', 'Username', 'Password', 'NIS', 'Kelas', 'Tanggal'])

        for i, enrollment in enumerate(enrollments, 1):
            student = enrollment.student
            
            # Extract middle name from first_name
            first_name_parts = str(student.first_name).strip().split()
            # Use the second part as middle name (or first part if only one word)
            if len(first_name_parts) > 1:
                middle_name = first_name_parts[1]
            else:
                middle_name = student.first_name
            
            # Generate password using the same logic as bulk enrollment
            password = generate_student_password(middle_name, middle_name, i)
            
            writer.writerow([
                str(i),
                student.email,
                student.get_full_name(),
                student.username,
                password,
                enrollment.student_id_in_class or 'N/A',
                class_obj.name,
                datetime.now().strftime('%d-%m-%Y')
            ])

        return response

    def _export_pdf(self, class_obj, enrollments):
        """Export as PDF"""
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.units import inch
        from io import BytesIO
        from django.core.files.base import ContentFile

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
        styles = getSampleStyleSheet()
        story = []

        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=6,
            alignment=1
        )
        story.append(Paragraph("DAFTAR AKUN SISWA", title_style))
        story.append(Paragraph(f"Kelas: {class_obj.name}", styles['Normal']))
        story.append(Spacer(1, 0.3 * inch))

        # Credentials table with passwords
        data = [['No.', 'Email', 'Nama', 'Username', 'Password', 'NIS']]
        for i, enrollment in enumerate(enrollments, 1):
            student = enrollment.student
            
            # Extract middle name from first_name
            first_name_parts = str(student.first_name).strip().split()
            # Use the second part as middle name (or first part if only one word)
            if len(first_name_parts) > 1:
                middle_name = first_name_parts[1]
            else:
                middle_name = student.first_name
            
            # Generate password using the same logic as bulk enrollment
            password = generate_student_password(middle_name, middle_name, i)
            
            data.append([
                str(i),
                student.email,
                student.get_full_name(),
                student.username,
                password,
                enrollment.student_id_in_class or 'N/A'
            ])

        table = Table(data, colWidths=[0.5*inch, 1.8*inch, 1.8*inch, 1.5*inch, 1.5*inch, 0.8*inch])
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(table)
        story.append(Spacer(1, 0.3 * inch))

        # Footer
        footer_text = f'Dicetak pada: {datetime.now().strftime("%d %B %Y %H:%M")}'
        story.append(Paragraph(footer_text, ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=1
        )))

        doc.build(story)
        buffer.seek(0)

        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="credentials_{class_obj.id}.pdf"'
        return response
