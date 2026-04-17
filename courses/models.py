from django.db import models
from django.core.exceptions import ValidationError
from academic.models import Subject, Class, AcademicYear
from accounts.models import User
import uuid


class Course(models.Model):
    """Course/Subject class instance"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='courses')
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='courses')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='courses')
    teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='teaching_courses',
        limit_choices_to={'role': 'TEACHER'}
    )
    description = models.TextField(blank=True, null=True)
    syllabus = models.FileField(upload_to='course_syllabi/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('subject', 'class_obj', 'academic_year')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subject.name} - {self.class_obj.name} ({self.academic_year})"


class Module(models.Model):
    """Course module (collection of lessons)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']
        unique_together = ('course', 'title')

    def __str__(self):
        return f"Module {self.order}: {self.title}"


class Lesson(models.Model):
    """Individual lesson within a module"""
    CONTENT_TYPE_CHOICES = (
        ('TEXT', 'Text'),
        ('VIDEO', 'Video'),
        ('PDF', 'PDF Document'),
        ('MIXED', 'Mixed Content'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES, default='TEXT')

    # Content fields
    text_content = models.TextField(blank=True, null=True)
    video_file = models.FileField(upload_to='lesson_videos/', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)  # YouTube/external video URL
    pdf_file = models.FileField(upload_to='lesson_pdfs/', blank=True, null=True)

    # Metadata
    duration_minutes = models.IntegerField(blank=True, null=True)  # Duration for videos
    order = models.IntegerField(default=0)
    is_mandatory = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"{self.title}"


class LessonAccess(models.Model):
    """Track student access to lessons"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='accesses')
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='lesson_accesses',
        limit_choices_to={'role': 'STUDENT'}
    )
    first_accessed = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)
    is_completed = models.BooleanField(default=False)
    completion_date = models.DateTimeField(blank=True, null=True)
    time_spent_seconds = models.IntegerField(default=0)

    class Meta:
        unique_together = ('lesson', 'student')
        verbose_name = 'Lesson Access'
        verbose_name_plural = 'Lesson Accesses'

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.lesson.title}"


class CourseAttachment(models.Model):
    """Additional course attachments/resources"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='attachments')
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='course_attachments/')
    file_type = models.CharField(max_length=50)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
