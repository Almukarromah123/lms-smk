from django.db import models
from django.utils import timezone
from django.urls import reverse
from academic.models import Class, Subject
from accounts.models import User
import uuid
import json


class Exam(models.Model):
    """Online Exam/Test (CBT - Computer Based Test)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='exams')
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='exams')
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_exams',
        limit_choices_to={'role': 'TEACHER'}
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    exam_date = models.DateTimeField()
    display_answer_key = models.BooleanField(default=False)  # Show correct answers after exam

    # Duration
    duration_minutes = models.IntegerField(default=60)
    total_points = models.IntegerField(default=100)

    # Question shuffle
    shuffle_questions = models.BooleanField(default=False)
    shuffle_options = models.BooleanField(default=False)
    allow_back = models.BooleanField(default=True)  # Can student go back to previous questions
    question_per_page = models.IntegerField(default=1)

    # Status
    is_published = models.BooleanField(default=False)
    show_feedback = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Auto-deletion status
    deletion_scheduled_at = models.DateTimeField(blank=True, null=True)
    deletion_notified = models.BooleanField(default=False)

    class Meta:
        ordering = ['-exam_date']
        verbose_name = 'Exam'
        verbose_name_plural = 'Exams'

    def __str__(self):
        return f"{self.title} - {self.class_obj.name}"

    def get_absolute_url(self):
        return reverse('exams:detail', kwargs={'exam_id': self.id})

    def get_question_count(self):
        return self.questions.count()

    def is_active(self):
        now = timezone.now()
        return self.exam_date <= now <= (self.exam_date + timezone.timedelta(minutes=self.duration_minutes))


class ExamQuestion(models.Model):
    """Individual question in an exam"""
    QUESTION_TYPE_CHOICES = (
        ('MCQ', 'Multiple Choice'),
        ('TF', 'True/False'),
        ('ESSAY', 'Essay'),
        ('MATCHING', 'Matching'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES, default='MCQ')
    points = models.FloatField(default=1)
    order = models.IntegerField(default=0)

    # For MCQ questions: store options as JSON
    options_data = models.JSONField(default=dict, blank=True)  # {"A": "Option A", "B": "Option B", ...}
    options_images = models.JSONField(default=dict, blank=True)  # {"A": "image_path.jpg", "B": "image_path.jpg", ...}
    correct_answer = models.CharField(max_length=255)  # "A" for MCQ, "True/False" for TF, or text for Essay

    image = models.ImageField(upload_to='exam_questions/', blank=True, null=True)
    explanation = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']
        unique_together = ('exam', 'order')

    def __str__(self):
        return f"{self.exam.title} - Q{self.order + 1}"


class ExamSession(models.Model):
    """Student exam session/attempt"""
    EXAM_STATUS_CHOICES = (
        ('NOT_STARTED', 'Not Started'),
        ('IN_PROGRESS', 'In Progress'),
        ('SUBMITTED', 'Submitted'),
        ('GRADED', 'Graded'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='sessions')
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='exam_sessions',
        limit_choices_to={'role': 'STUDENT'}
    )

    # Session info
    started_at = models.DateTimeField(blank=True, null=True)
    submitted_at = models.DateTimeField(blank=True, null=True)
    graded_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=EXAM_STATUS_CHOICES, default='NOT_STARTED')

    # Answers: {question_id: answer_text}
    student_answers = models.JSONField(default=dict)

    # Proctoring violations log
    violations_log = models.JSONField(default=list, blank=True)  # [{type, timestamp, ...}]

    # Score
    score = models.FloatField(blank=True, null=True)
    is_submitted = models.BooleanField(default=False)

    class Meta:
        unique_together = ('exam', 'student')
        verbose_name = 'Exam Session'
        verbose_name_plural = 'Exam Sessions'

    def __str__(self):
        return f"{self.exam.title} - {self.student.get_full_name()}"

    def start_exam(self):
        self.started_at = timezone.now()
        self.status = 'IN_PROGRESS'
        self.save()

    def submit_exam(self):
        self.submitted_at = timezone.now()
        self.is_submitted = True
        self.status = 'SUBMITTED'
        self.auto_grade()
        self.save()

    def auto_grade(self):
        """Auto-grade objective questions and essays with keyword matching"""
        score = 0
        for question in self.exam.questions.all():
            student_answer = self.student_answers.get(str(question.id), "").strip()

            if question.question_type in ['MCQ', 'TF']:
                # Exact match for multiple choice and true/false
                if student_answer == question.correct_answer:
                    score += question.points

            elif question.question_type == 'ESSAY':
                # Keyword-based grading for essays
                if self._check_essay_answer(student_answer, question.correct_answer):
                    score += question.points

        self.score = score
        self.status = 'GRADED'
        self.graded_at = timezone.now()

    def _check_essay_answer(self, student_answer, correct_answer):
        """
        Check if essay answer contains key keywords from correct answer.
        Case-insensitive word matching.
        """
        if not student_answer or not correct_answer:
            return False

        # Convert to lowercase for case-insensitive comparison
        student_lower = student_answer.lower()
        correct_lower = correct_answer.lower()

        # Split answer key into words, filter out common/small words
        keywords = [
            word.strip('.,!?;:')
            for word in correct_lower.split()
            if len(word.strip('.,!?;:')) > 2  # Only words longer than 2 chars
        ]

        if not keywords:
            return False

        # Check if at least 50% of keywords are in student answer
        matched_keywords = sum(1 for keyword in keywords if keyword in student_lower)
        return matched_keywords >= len(keywords) * 0.5

    def get_time_remaining_seconds(self):
        """Get remaining time in seconds"""
        if not self.started_at:
            return self.exam.duration_minutes * 60

        elapsed = (timezone.now() - self.started_at).total_seconds()
        remaining = (self.exam.duration_minutes * 60) - elapsed
        return max(0, remaining)

    def is_time_up(self):
        return self.get_time_remaining_seconds() <= 0


class ExamAnswer(models.Model):
    """Individual answer tracking"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ExamSession, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(ExamQuestion, on_delete=models.CASCADE)
    student_answer = models.TextField()
    is_correct = models.BooleanField(blank=True, null=True)  # Null for essay questions
    points_earned = models.FloatField(default=0)
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('session', 'question')

    def __str__(self):
        return f"{self.session} - Q{self.question.order + 1}"
