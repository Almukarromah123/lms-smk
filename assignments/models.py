from django.db import models
from django.utils import timezone
from django.urls import reverse
from academic.models import Class, Subject
from accounts.models import User
import uuid


class Assignment(models.Model):
    """Assignment/Task for students"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='assignments')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='assignments')
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_assignments',
        limit_choices_to={'role': 'TEACHER'}
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    instructions = models.TextField(blank=True, null=True)
    attachment = models.FileField(upload_to='assignment_files/', blank=True, null=True)

    # Dates
    created_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    submission_deadline = models.DateTimeField(blank=True, null=True)

    # Grading
    total_points = models.IntegerField(default=100)
    is_active = models.BooleanField(default=True)

    # Auto-deletion status
    deletion_scheduled_at = models.DateTimeField(blank=True, null=True)
    deletion_notified = models.BooleanField(default=False)

    class Meta:
        ordering = ['-due_date']

    def __str__(self):
        return f"{self.title} - {self.class_obj.name}"

    def get_absolute_url(self):
        return reverse('assignments:detail', kwargs={'assignment_id': self.id})

    def is_overdue(self):
        return timezone.now() > self.due_date

    def get_submission_count(self):
        return self.submissions.filter(submitted_at__isnull=False).count()


class AssignmentSubmission(models.Model):
    """Student submission for assignment"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assignment_submissions',
        limit_choices_to={'role': 'STUDENT'}
    )

    # Submission details
    submitted_file = models.FileField(upload_to='student_work/')
    submission_text = models.TextField(blank=True, null=True)  # For text submissions
    submitted_at = models.DateTimeField(blank=True, null=True)
    is_late = models.BooleanField(default=False)

    # Status
    is_graded = models.BooleanField(default=False)

    class Meta:
        unique_together = ('assignment', 'student')
        verbose_name = 'Assignment Submission'
        verbose_name_plural = 'Assignment Submissions'

    def __str__(self):
        return f"{self.assignment.title} - {self.student.get_full_name()}"

    def mark_as_submitted(self):
        self.submitted_at = timezone.now()
        self.is_late = self.submitted_at > self.assignment.due_date
        self.save()


class AssignmentGrade(models.Model):
    """Grade/Feedback for assignment submission"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission = models.OneToOneField(
        AssignmentSubmission,
        on_delete=models.CASCADE,
        related_name='grade'
    )
    score = models.FloatField(default=0)
    max_score = models.FloatField(default=100)
    feedback = models.TextField(blank=True, null=True)
    graded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='graded_assignments',
        limit_choices_to={'role': 'TEACHER'}
    )
    graded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Assignment Grade'
        verbose_name_plural = 'Assignment Grades'

    def __str__(self):
        return f"{self.submission.assignment.title} - {self.submission.student.get_full_name()}: {self.score}/{self.max_score}"

    def get_percentage(self):
        if self.max_score == 0:
            return 0
        return (self.score / self.max_score) * 100

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Mark submission as graded
        self.submission.is_graded = True
        self.submission.save()
