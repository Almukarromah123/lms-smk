"""
Management command to delete overdue exams and assignments
Run periodically using: python manage.py delete_overdue_items
Or schedule with cron:
  0 3 * * * cd /path/to/lms && python manage.py delete_overdue_items

Deletion happens 1 day after notifikasi when deadline passed.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
from exams.models import Exam
from assignments.models import Assignment
from notifications.models import Notification


class Command(BaseCommand):
    help = 'Delete exams and assignments 1 day after deadline when notification sent'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        now = timezone.now()

        # Delete overdue exams
        overdue_exams = Exam.objects.filter(
            deletion_scheduled_at__lte=now,
            deletion_scheduled_at__isnull=False
        )

        exam_count = overdue_exams.count()
        if exam_count > 0:
            self.stdout.write(
                self.style.WARNING(f'Found {exam_count} overdue exam(s) for deletion')
            )
            for exam in overdue_exams:
                self.stdout.write(f'  - {exam.title} (scheduled: {exam.deletion_scheduled_at})')
                if not dry_run:
                    # Log deletion
                    self.log_deletion(f'Exam: {exam.title}', exam.created_by)
                    exam.delete()

        # Delete overdue assignments
        overdue_assignments = Assignment.objects.filter(
            deletion_scheduled_at__lte=now,
            deletion_scheduled_at__isnull=False
        )

        assignment_count = overdue_assignments.count()
        if assignment_count > 0:
            self.stdout.write(
                self.style.WARNING(f'Found {assignment_count} overdue assignment(s) for deletion')
            )
            for assignment in overdue_assignments:
                self.stdout.write(f'  - {assignment.title} (scheduled: {assignment.deletion_scheduled_at})')
                if not dry_run:
                    # Log deletion
                    self.log_deletion(f'Assignment: {assignment.title}', assignment.teacher)
                    assignment.delete()

        if dry_run:
            self.stdout.write(
                self.style.SUCCESS('DRY RUN - No items were actually deleted')
            )
        else:
            total = exam_count + assignment_count
            if total > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully deleted {total} overdue item(s)')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS('No overdue items to delete')
                )

    def log_deletion(self, item_name, user):
        """Create notification about deletion"""
        try:
            if user:
                Notification.objects.create(
                    recipient=user,
                    title="Item Deleted",
                    message=f"{item_name} telah dihapus karena sudah melewati deadline.",
                    notification_type='SYSTEM'
                )
        except:
            pass
