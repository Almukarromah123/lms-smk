from django.db import models
from academic.models import Subject, Class, AcademicYear
from accounts.models import User
import uuid


class GradeBook(models.Model):
    """Grade book tracking student performance"""
    SEMESTER_CHOICES = (
        ('1', 'Semester 1'),
        ('2', 'Semester 2'),
    )

    GRADE_CHOICES = (
        ('A', 'A (90-100)'),
        ('B', 'B (80-89)'),
        ('C', 'C (70-79)'),
        ('D', 'D (60-69)'),
        ('E', 'E (< 60)'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='grades',
        limit_choices_to={'role': 'STUDENT'}
    )
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='grade_books')
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='grade_books')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='grade_books')

    semester = models.CharField(max_length=1, choices=SEMESTER_CHOICES)

    # Scores
    assignment_average = models.FloatField(default=0)  # Average from assignments
    exam_average = models.FloatField(default=0)  # Average from exams
    attendance_score = models.FloatField(default=0)  # Attendance-based score
    practical_score = models.FloatField(default=0)  # Practical/lab score

    # Final Grade
    final_score = models.FloatField(default=0)  # Weighted average
    letter_grade = models.CharField(max_length=1, choices=GRADE_CHOICES, blank=True)
    remarks = models.TextField(blank=True, null=True)

    # Metadata
    is_locked = models.BooleanField(default=False)  # Prevent changes after finalization
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'subject', 'class_obj', 'academic_year', 'semester')
        ordering = ['-academic_year', 'subject']
        verbose_name = 'Grade Book'
        verbose_name_plural = 'Grade Books'
        indexes = [
            models.Index(fields=['student', 'academic_year']),
            models.Index(fields=['class_obj', 'semester']),
        ]

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.subject.name} ({self.academic_year})"

    def calculate_final_score(self, assignment_weight=0.3, exam_weight=0.5, attendance_weight=0.1, practical_weight=0.1):
        """Calculate weighted final score"""
        if self.is_locked:
            return self.final_score

        total_weight = assignment_weight + exam_weight + attendance_weight + practical_weight
        if total_weight == 0:
            return 0

        weighted_score = (
            (self.assignment_average * assignment_weight) +
            (self.exam_average * exam_weight) +
            (self.attendance_score * attendance_weight) +
            (self.practical_score * practical_weight)
        ) / total_weight

        self.final_score = round(weighted_score, 2)
        self.determine_letter_grade()
        return self.final_score

    def determine_letter_grade(self):
        """Determine letter grade based on final score"""
        if self.final_score >= 90:
            self.letter_grade = 'A'
        elif self.final_score >= 80:
            self.letter_grade = 'B'
        elif self.final_score >= 70:
            self.letter_grade = 'C'
        elif self.final_score >= 60:
            self.letter_grade = 'D'
        else:
            self.letter_grade = 'E'


class ReportCard(models.Model):
    """Generated report card for student"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='report_cards',
        limit_choices_to={'role': 'STUDENT'}
    )
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='report_cards')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='report_cards')

    SEMESTER_CHOICES = (
        ('1', 'Semester 1'),
        ('2', 'Semester 2'),
    )

    semester = models.CharField(max_length=1, choices=SEMESTER_CHOICES)

    # GPA
    gpa = models.FloatField(default=0)  # Cumulative GPA for this semester
    total_credits = models.IntegerField(default=0)

    # Status
    is_published = models.BooleanField(default=False)
    published_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='published_report_cards',
        limit_choices_to={'role': 'ADMIN'}
    )
    published_at = models.DateTimeField(blank=True, null=True)

    # Document
    pdf_file = models.FileField(upload_to='report_cards/', blank=True, null=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    # Metadata
    principal_notes = models.TextField(blank=True, null=True)
    homeroom_teacher_notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('student', 'class_obj', 'academic_year', 'semester')
        ordering = ['-academic_year', '-semester']
        verbose_name = 'Report Card'
        verbose_name_plural = 'Report Cards'

    def __str__(self):
        return f"Report Card - {self.student.get_full_name()} ({self.academic_year}, {self.semester})"

    def calculate_gpa(self):
        """Calculate GPA from grade book entries"""
        grade_books = GradeBook.objects.filter(
            student=self.student,
            class_obj=self.class_obj,
            academic_year=self.academic_year,
            semester=self.semester
        )

        if not grade_books.exists():
            return 0

        total_score = sum(gb.final_score for gb in grade_books)
        self.gpa = round(total_score / grade_books.count(), 2)
        return self.gpa

    def generate_pdf(self):
        """Generate PDF report card"""
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.units import inch
        from io import BytesIO
        from django.core.files.base import ContentFile

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=6,
            alignment=1  # Center
        )
        story.append(Paragraph("SMK IT AL - MUKARROMAH", title_style))
        story.append(Paragraph("LAPORAN HASIL BELAJAR (RAPORT)", styles['Heading2']))
        story.append(Spacer(1, 0.3 * inch))

        # Student Info
        info_data = [
            ['Nama Siswa:', self.student.get_full_name()],
            ['NIS:', getattr(self.student.profile, 'nis', 'N/A')],
            ['Kelas:', str(self.class_obj)],
            ['Tahun Ajaran:', str(self.academic_year)],
            ['Semester:', self.get_semester_display()],
        ]
        info_table = Table(info_data, colWidths=[2 * inch, 4 * inch])
        info_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.3 * inch))

        # Grades Table
        grade_data = [['No.', 'Mata Pelajaran', 'Nilai Akhir', 'Grade']]
        grade_books = GradeBook.objects.filter(
            student=self.student,
            class_obj=self.class_obj,
            academic_year=self.academic_year,
            semester=self.semester
        )

        for i, gb in enumerate(grade_books, 1):
            grade_data.append([
                str(i),
                gb.subject.name,
                f"{gb.final_score:.2f}",
                gb.letter_grade or 'N/A'
            ])

        grades_table = Table(grade_data, colWidths=[0.5 * inch, 3 * inch, 1.5 * inch, 1 * inch])
        grades_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]))
        story.append(grades_table)
        story.append(Spacer(1, 0.3 * inch))

        # Summary
        summary_data = [
            ['IPK/GPA:', f"{self.gpa:.2f}"],
            ['Status:', 'Lulus' if self.gpa >= 2.0 else 'Perlu Perbaikan'],
        ]
        summary_table = Table(summary_data, colWidths=[2 * inch, 4 * inch])
        summary_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ]))
        story.append(summary_table)

        # Build PDF
        doc.build(story)
        buffer.seek(0)

        # Save PDF file
        filename = f"raport_{self.student.username}_{self.academic_year}_{self.semester}.pdf"
        self.pdf_file.save(filename, ContentFile(buffer.getvalue()), save=True)

        return self.pdf_file
