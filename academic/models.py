from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from accounts.models import User
import uuid


class AcademicYear(models.Model):
    """Academic year (e.g., 2023/2024)"""
    year_start = models.IntegerField()
    year_end = models.IntegerField()
    is_current = models.BooleanField(default=False)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-year_start']
        unique_together = ('year_start', 'year_end')

    def __str__(self):
        return f"{self.year_start}/{self.year_end}"


class School(models.Model):
    """School information"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, default="SMK IT AL - MUKARROMAH")
    code = models.CharField(max_length=50, unique=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to='school_logo/', blank=True, null=True)
    principal_name = models.CharField(max_length=255, blank=True)
    principal_nip = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    established_year = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'School'
        verbose_name_plural = 'Schools'

    def __str__(self):
        return self.name


class Subject(models.Model):
    """School subjects/courses"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='subjects')
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('school', 'code')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class Class(models.Model):
    """School class (e.g., XI Teknik Mesin 1)"""
    GRADE_CHOICES = (
        ('X', 'Grade X'),
        ('XI', 'Grade XI'),
        ('XII', 'Grade XII'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='classes')
    name = models.CharField(max_length=100)  # e.g., "XI Teknik Mesin 1"
    grade = models.CharField(max_length=3, choices=GRADE_CHOICES)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='classes')
    homeroom_teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='homeroom_classes',
        limit_choices_to={'role': 'TEACHER'}
    )
    max_students = models.IntegerField(default=40)
    room_number = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('school', 'name', 'academic_year')
        ordering = ['name']
        verbose_name = 'Class'
        verbose_name_plural = 'Classes'

    def __str__(self):
        return f"{self.name} ({self.academic_year})"

    def get_student_count(self):
        return self.enrollments.filter(status='ACTIVE').count()


class ClassSubjectTeacher(models.Model):
    """Relationship between Class, Subject, and Teacher"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='subject_teachers')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='teaching_assignments',
        limit_choices_to={'role': 'TEACHER'}
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('class_obj', 'subject', 'teacher')
        verbose_name = 'Class Subject Teacher'
        verbose_name_plural = 'Class Subject Teachers'

    def __str__(self):
        return f"{self.class_obj.name} - {self.subject.name} - {self.teacher.get_full_name()}"


class StudentEnrollment(models.Model):
    """Student enrollment in class"""
    STATUS_CHOICES = (
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('GRADUATED', 'Graduated'),
        ('DROPPED', 'Dropped'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='enrollments',
        limit_choices_to={'role': 'STUDENT'}
    )
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='enrollments')
    enrollment_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    student_id_in_class = models.CharField(max_length=50, blank=True)  # Nomor induk siswa per kelas
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'class_obj')
        ordering = ['student__last_name', 'student__first_name']
        verbose_name = 'Student Enrollment'
        verbose_name_plural = 'Student Enrollments'

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.class_obj.name}"
