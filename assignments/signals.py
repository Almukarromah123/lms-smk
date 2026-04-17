"""Signal handlers for automatic assignment deletion after deadline"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.mail import send_mail
from datetime import timedelta
from .models import Assignment
from notifications.models import Notification


@receiver(post_save, sender=Assignment)
def schedule_assignment_deletion(sender, instance, created, **kwargs):
    """
    Schedule assignment deletion after due_date + delay period
    Adds 7 days delay after deadline
    """
    if not instance.deletion_scheduled_at:
        # Calculate deletion time: due_date + 1 day delay after notification
        deletion_time = instance.due_date + timedelta(days=1)

        instance.deletion_scheduled_at = deletion_time
        # Use update to avoid recursive signals
        Assignment.objects.filter(pk=instance.pk).update(deletion_scheduled_at=deletion_time)


@receiver(post_save, sender=Assignment)
def check_assignment_overdue_for_notification(sender, instance, **kwargs):
    """
    Check if assignment is overdue and send notification immediately
    Notification sent as soon as deadline passes, deletion 1 day later
    """
    now = timezone.now()

    if now >= instance.due_date and not instance.deletion_notified:
        send_assignment_deletion_notification(instance)
        Assignment.objects.filter(pk=instance.pk).update(deletion_notified=True)


def send_assignment_deletion_notification(assignment):
    """Send notification to admin and teacher about upcoming deletion"""
    # Create notification
    message = f"Assignment '{assignment.title}' akan dihapus pada {assignment.deletion_scheduled_at.strftime('%d/%m/%Y %H:%M')} (1 hari setelah notifikasi ini)"

    # Notify teacher
    Notification.objects.create(
        recipient=assignment.teacher,
        title="Assignment akan Dihapus",
        message=message,
        notification_type='SYSTEM'
    )

    # Send email
    try:
        send_mail(
            subject="Assignment Deletion - Pemberitahuan",
            message=message,
            from_email='noreply@lms-smk.local',
            recipient_list=[assignment.teacher.email],
            fail_silently=True,
        )
    except:
        pass
