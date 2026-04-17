from django.db import models
from accounts.models import User
import uuid


class Notification(models.Model):
    """In-app notifications for users"""
    NOTIFICATION_TYPE_CHOICES = (
        ('ASSIGNMENT', 'New Assignment'),
        ('EXAM', 'New Exam'),
        ('GRADE', 'Grade Published'),
        ('PAYMENT', 'Payment Reminder'),
        ('MESSAGE', 'Message'),
        ('ANNOUNCEMENT', 'Announcement'),
        ('SYSTEM', 'System'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES, default='SYSTEM')
    title = models.CharField(max_length=255)
    message = models.TextField()
    related_id = models.CharField(max_length=255, blank=True, null=True)  # ID of related object (assignment, exam, etc)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['is_read']),
        ]

    def __str__(self):
        return f"{self.title} - {self.recipient.username}"

    def mark_as_read(self):
        from django.utils import timezone
        self.is_read = True
        self.read_at = timezone.now()
        self.save()
