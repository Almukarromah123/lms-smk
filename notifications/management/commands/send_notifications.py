from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from assignments.models import Assignment
from exams.models import Exam
from notifications.models import Notification
from academic.models import StudentEnrollment


class Command(BaseCommand):
    help = 'Send automated notifications for assignments, exams, and other events'

    def handle(self, *args, **options):
        """Run automated notification system"""
        self.stdout.write('Processing automated notifications...')

        # 1. Notify students about upcoming assignment deadlines (24 hours before)
        self.notify_assignment_deadline()

        # 2. Notify students about upcoming exams (1 day before)
        self.notify_exam_reminders()

        # 3. Notify about overdue assignments
        self.notify_overdue_assignments()

        self.stdout.write(self.style.SUCCESS('Notifications sent successfully!'))

    def notify_assignment_deadline(self):
        """Notify students 24 hours before assignment deadline"""
        now = timezone.now()
        tomorrow = now + timedelta(hours=24)

        # Find assignments due within 24 hours
        upcoming_assignments = Assignment.objects.filter(
            due_date__gte=now,
            due_date__lte=tomorrow,
            is_active=True
        )

        for assignment in upcoming_assignments:
            # Get students in the class
            enrollments = StudentEnrollment.objects.filter(
                class_obj=assignment.class_obj,
                status='ACTIVE'
            )

            for enrollment in enrollments:
                # Check if notification already sent
                existing = Notification.objects.filter(
                    recipient=enrollment.student,
                    title__startswith=f'Deadline: {assignment.title}'
                ).exists()

                if not existing:
                    Notification.objects.create(
                        recipient=enrollment.student,
                        title=f'Deadline: {assignment.title}',
                        message=f'Assignment "{assignment.title}" akan berakhir dalam 24 jam. '
                                f'Deadline: {assignment.due_date.strftime("%d %b %Y %H:%M")}',
                        notification_type='ASSIGNMENT'
                    )

        self.stdout.write(f'✓ Assignment deadline notifications sent for {upcoming_assignments.count()} assignments')

    def notify_exam_reminders(self):
        """Notify students 1 day before exam"""
        now = timezone.now()
        tomorrow = now + timedelta(hours=24)

        # Find exams scheduled within 24 hours
        upcoming_exams = Exam.objects.filter(
            exam_date__gte=now,
            exam_date__lte=tomorrow,
            is_published=True
        )

        for exam in upcoming_exams:
            # Get students in the class
            enrollments = StudentEnrollment.objects.filter(
                class_obj=exam.class_obj,
                status='ACTIVE'
            )

            for enrollment in enrollments:
                # Check if notification already sent
                existing = Notification.objects.filter(
                    recipient=enrollment.student,
                    title__startswith=f'Reminder Ujian: {exam.title}'
                ).exists()

                if not existing:
                    Notification.objects.create(
                        recipient=enrollment.student,
                        title=f'Reminder Ujian: {exam.title}',
                        message=f'Ujian "{exam.title}" akan dimulai dalam 24 jam. '
                                f'Siapkan diri Anda sebaik-baiknya! '
                                f'Waktu: {exam.exam_date.strftime("%d %b %Y %H:%M")} '
                                f'Durasi: {exam.duration_minutes} menit',
                        notification_type='EXAM'
                    )

        self.stdout.write(f'✓ Exam reminder notifications sent for {upcoming_exams.count()} exams')

    def notify_overdue_assignments(self):
        """Notify about overdue assignments"""
        now = timezone.now()

        # Find assignments that are overdue
        overdue_assignments = Assignment.objects.filter(
            due_date__lt=now,
            is_active=True
        )

        for assignment in overdue_assignments:
            # Get students who haven't submitted
            from assignments.models import AssignmentSubmission
            not_submitted = StudentEnrollment.objects.filter(
                class_obj=assignment.class_obj,
                status='ACTIVE'
            ).exclude(
                student__assignment_submissions__assignment=assignment
            )

            for enrollment in not_submitted:
                # Check if notification already sent today
                today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
                existing = Notification.objects.filter(
                    recipient=enrollment.student,
                    title__startswith=f'OVERDUE: {assignment.title}',
                    created_at__gte=today_start
                ).exists()

                if not existing:
                    Notification.objects.create(
                        recipient=enrollment.student,
                        title=f'OVERDUE: {assignment.title}',
                        message=f'Assignment "{assignment.title}" sudah melewati deadline! '
                                f'Segera submit pekerjaan Anda.',
                        notification_type='ASSIGNMENT'
                    )

        self.stdout.write(f'✓ Overdue assignment notifications processed')
