"""Signal handlers for automatic exam deletion after deadline"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from datetime import timedelta
from .models import Exam
from notifications.models import Notification


@receiver(post_save, sender=Exam)
def schedule_exam_deletion(sender, instance, created, **kwargs):
    """
    Schedule exam deletion after it ends + delay period
    Notifies admin/teacher before deletion
    """
    if not instance.deletion_scheduled_at:
        # Calculate deletion time: exam_date + duration + 1 day delay after notification
        exam_end_time = instance.exam_date + timedelta(minutes=instance.duration_minutes)
        deletion_time = exam_end_time + timedelta(days=1)

        instance.deletion_scheduled_at = deletion_time
        # Use update to avoid recursive signals
        Exam.objects.filter(pk=instance.pk).update(deletion_scheduled_at=deletion_time)


@receiver(post_save, sender=Exam)
def check_exam_overdue_for_notification(sender, instance, **kwargs):
    """
    Check if exam is overdue and send notification immediately
    Notification sent as soon as exam ends, deletion 1 day later
    """
    now = timezone.now()
    exam_end_time = instance.exam_date + timedelta(minutes=instance.duration_minutes)

    if now >= exam_end_time and not instance.deletion_notified:
        send_exam_deletion_notification(instance)
        Exam.objects.filter(pk=instance.pk).update(deletion_notified=True)


def send_exam_deletion_notification(exam):
    """Send notification to admin and teacher about upcoming deletion"""
    # Create notification
    message = f"Exam '{exam.title}' akan dihapus pada {exam.deletion_scheduled_at.strftime('%d/%m/%Y %H:%M')} (1 hari setelah notifikasi ini)"

    # Notify creator (teacher)
    if exam.created_by:
        Notification.objects.create(
            recipient=exam.created_by,
            title="Exam akan Dihapus",
            message=message,
            notification_type='SYSTEM'
        )

        # Send email
        try:
            send_mail(
                subject="Exam Deletion - Pemberitahuan",
                message=message,
                from_email='noreply@lms-smk.local',
                recipient_list=[exam.created_by.email],
                fail_silently=True,
            )
        except:
            pass
