from django.db import models
from django.utils import timezone
from academic.models import Class, ClassSubjectTeacher
from accounts.models import User
import uuid
from datetime import date, timedelta


class AttendanceRecord(models.Model):
    """Daily attendance record for students in a specific subject"""
    STATUS_CHOICES = (
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('SICK', 'Sick'),
        ('PERMISSION', 'Permission'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='attendance_records',
        limit_choices_to={'role': 'STUDENT'}
    )
    attendance_session = models.ForeignKey(
        'AttendanceSession',
        on_delete=models.CASCADE,
        related_name='attendance_records',
        null=True,
        blank=True
    )
    attendance_date = models.DateField(default=date.today)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PRESENT')

    # Recording info
    recorded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recorded_attendance',
        limit_choices_to={'role': 'TEACHER'}
    )
    recorded_at = models.DateTimeField(auto_now_add=True)

    # Additional info
    remarks = models.TextField(blank=True, null=True)
    arrival_time = models.TimeField(blank=True, null=True)

    class Meta:
        unique_together = ('student', 'attendance_session', 'attendance_date')
        ordering = ['-attendance_date']
        indexes = [
            models.Index(fields=['attendance_session', 'attendance_date']),
            models.Index(fields=['student', 'attendance_date']),
        ]
        verbose_name = 'Attendance Record'
        verbose_name_plural = 'Attendance Records'

    def __str__(self):
        session_info = ""
        if self.attendance_session and self.attendance_session.class_subject_teacher:
            session_info = f" - {self.attendance_session.class_subject_teacher.subject.name}"
        return f"{self.student.get_full_name()}{session_info} - {self.attendance_date} ({self.status})"


class AttendanceSummary(models.Model):
    """Attendance summary for a student in a period"""
    PERIOD_CHOICES = (
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('SEMESTER', 'Semester'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='attendance_summaries',
        limit_choices_to={'role': 'STUDENT'}
    )
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='attendance_summaries')
    period_type = models.CharField(max_length=20, choices=PERIOD_CHOICES, default='MONTHLY')
    period_start_date = models.DateField()
    period_end_date = models.DateField()

    # Counts
    total_days = models.IntegerField(default=0)
    present_count = models.IntegerField(default=0)
    absent_count = models.IntegerField(default=0)
    late_count = models.IntegerField(default=0)
    excused_count = models.IntegerField(default=0)
    sick_count = models.IntegerField(default=0)

    # Percentage
    attendance_percentage = models.FloatField(default=0)

    # Generated
    generated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'class_obj', 'period_type', 'period_start_date', 'period_end_date')
        ordering = ['-period_end_date']
        verbose_name = 'Attendance Summary'
        verbose_name_plural = 'Attendance Summaries'

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.period_type} ({self.period_start_date} to {self.period_end_date})"

    def calculate_percentage(self):
        """Calculate attendance percentage"""
        if self.total_days == 0:
            self.attendance_percentage = 0
        else:
            self.attendance_percentage = (self.present_count / self.total_days) * 100
        return self.attendance_percentage

    @staticmethod
    def generate_summary(student, class_obj, period_type='MONTHLY', period_start_date=None, period_end_date=None):
        """Generate attendance summary for a period"""
        from datetime import datetime, timedelta

        if not period_start_date or not period_end_date:
            today = date.today()
            if period_type == 'WEEKLY':
                period_start_date = today - timedelta(days=today.weekday())
                period_end_date = period_start_date + timedelta(days=6)
            elif period_type == 'MONTHLY':
                period_start_date = today.replace(day=1)
                if today.month == 12:
                    period_end_date = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
                else:
                    period_end_date = today.replace(month=today.month + 1, day=1) - timedelta(days=1)

        records = AttendanceRecord.objects.filter(
            student=student,
            class_obj=class_obj,
            attendance_date__gte=period_start_date,
            attendance_date__lte=period_end_date
        )

        summary, created = AttendanceSummary.objects.get_or_create(
            student=student,
            class_obj=class_obj,
            period_type=period_type,
            period_start_date=period_start_date,
            period_end_date=period_end_date,
        )

        summary.total_days = records.count()
        summary.present_count = records.filter(status='PRESENT').count()
        summary.absent_count = records.filter(status='ABSENT').count()
        summary.sick_count = records.filter(status='SICK').count()
        summary.late_count = 0  # Deprecated - kept for backward compatibility
        summary.excused_count = 0  # Deprecated - kept for backward compatibility
        summary.calculate_percentage()
        summary.save()

        return summary


class AttendanceSession(models.Model):
    """Attendance session created by teacher for a specific subject in a class on a specific date"""
    SESSION_TYPE_CHOICES = [
        ('LURING', 'Tatap Muka (In-Person)'),
        ('DARING', 'Pembelajaran Daring (Online)'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class_subject_teacher = models.ForeignKey(
        ClassSubjectTeacher,
        on_delete=models.CASCADE,
        related_name='attendance_sessions',
        null=True,
        blank=True
    )
    session_date = models.DateField()
    session_type = models.CharField(
        max_length=20,
        choices=SESSION_TYPE_CHOICES,
        default='LURING',
        help_text='LURING: In-person with QR code scanning, DARING: Online with student submission'
    )
    description = models.CharField(max_length=200, default='Class Attendance')

    # QR Code fields for LURING sessions
    qr_token = models.CharField(
        max_length=64,
        unique=True,
        blank=True,
        null=True,
        help_text='Current valid QR token for this session'
    )
    qr_token_generated_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text='When the current QR token was generated'
    )
    qr_token_expires_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text='When the current QR token expires'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    is_open = models.BooleanField(default=True)

    class Meta:
        unique_together = ('class_subject_teacher', 'session_date')
        ordering = ['-session_date']
        verbose_name = 'Attendance Session'
        verbose_name_plural = 'Attendance Sessions'
        indexes = [
            models.Index(fields=['class_subject_teacher', 'session_date']),
            models.Index(fields=['session_type']),
        ]

    def __str__(self):
        if self.class_subject_teacher:
            return f"{self.class_subject_teacher.class_obj.name} - {self.class_subject_teacher.subject.name} - {self.session_date} ({self.get_session_type_display()})"
        return f"Attendance Session - {self.session_date}"

    def generate_new_qr_token(self):
        """Generate new QR token for LURING sessions"""
        if self.session_type == 'DARING':
            return None

        from django.utils.crypto import get_random_string
        self.qr_token = get_random_string(32)
        self.qr_token_generated_at = timezone.now()
        self.qr_token_expires_at = timezone.now() + timedelta(seconds=60)
        self.save()
        return self.qr_token

    def is_qr_token_valid(self, token):
        """Check if provided token is valid"""
        if not self.qr_token or self.session_type != 'LURING':
            return False

        # Token must match and not be expired
        is_valid = (token == self.qr_token and
                   timezone.now() <= self.qr_token_expires_at)
        return is_valid

    def is_qr_token_expired(self):
        """Check if current QR token has expired"""
        if not self.qr_token_expires_at:
            return True
        return timezone.now() > self.qr_token_expires_at

    def get_qr_image(self):
        """Get current QR code as image (for display)"""
        from .utils import generate_qr_code_image

        if not self.qr_token:
            self.generate_new_qr_token()

        # Generate QR code with token data
        return generate_qr_code_image(self.qr_token, size=250)
