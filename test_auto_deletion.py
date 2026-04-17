"""
Test script untuk automatic deletion system
Jalankan dengan: python manage.py shell < test_auto_deletion.py
"""
from django.utils import timezone
from datetime import timedelta
from exams.models import Exam
from assignments.models import Assignment
from academic.models import Class, Subject
from accounts.models import User
import uuid

def test_automatic_deletion():
    print("\n=== Testing Automatic Deletion System ===\n")

    # Get test data
    try:
        teacher = User.objects.get(username='teacher1')
        class_obj = Class.objects.first()
        subject = Subject.objects.first()
    except:
        print("❌ Test data tidak ditemukan. Setup test data terlebih dahulu.")
        return

    print(f"✅ Using Teacher: {teacher.username}")
    print(f"✅ Using Class: {class_obj.name}")
    print(f"✅ Using Subject: {subject.name}\n")

    # Test 1: Create Exam with past date
    print("📝 Test 1: Creating exam with past exam_date...")
    past_date = timezone.now() - timedelta(days=5)

    exam = Exam.objects.create(
        id=uuid.uuid4(),
        subject=subject,
        class_obj=class_obj,
        created_by=teacher,
        title=f"Test Exam - {timezone.now()}",
        exam_date=past_date,
        duration_minutes=60,
        total_points=100,
        is_published=True
    )

    print(f"✅ Exam created: {exam.title}")
    print(f"   ID: {exam.id}")
    print(f"   Exam Date: {exam.exam_date}")
    print(f"   Deletion Scheduled: {exam.deletion_scheduled_at}")
    print(f"   Notification Sent: {exam.deletion_notified}\n")

    # Verify signal triggered
    exam.refresh_from_db()
    if exam.deletion_scheduled_at:
        print("✅ Signal handler WORKS - deletion_scheduled_at is set")
        expected_deletion = past_date + timedelta(minutes=60, days=7)
        print(f"   Expected: {expected_deletion}")
        print(f"   Actual: {exam.deletion_scheduled_at}\n")
    else:
        print("❌ Signal handler FAILED - deletion_scheduled_at is None\n")

    # Test 2: Create Assignment with past due_date
    print("📝 Test 2: Creating assignment with past due_date...")
    past_due = timezone.now() - timedelta(days=3)

    assignment = Assignment.objects.create(
        id=uuid.uuid4(),
        class_obj=class_obj,
        subject=subject,
        teacher=teacher,
        title=f"Test Assignment - {timezone.now()}",
        description="Test Description",
        due_date=past_due,
        total_points=100
    )

    print(f"✅ Assignment created: {assignment.title}")
    print(f"   ID: {assignment.id}")
    print(f"   Due Date: {assignment.due_date}")
    print(f"   Deletion Scheduled: {assignment.deletion_scheduled_at}")
    print(f"   Notification Sent: {assignment.deletion_notified}\n")

    # Verify signal triggered
    assignment.refresh_from_db()
    if assignment.deletion_scheduled_at:
        print("✅ Signal handler WORKS - deletion_scheduled_at is set")
        expected_deletion = past_due + timedelta(days=7)
        print(f"   Expected: {expected_deletion}")
        print(f"   Actual: {assignment.deletion_scheduled_at}\n")
    else:
        print("❌ Signal handler FAILED - deletion_scheduled_at is None\n")

    # Test 3: Dry-run delete command
    print("📝 Test 3: Running delete command with --dry-run...")
    from django.core.management import call_command
    from io import StringIO

    out = StringIO()
    call_command('delete_overdue_items', '--dry-run', stdout=out)
    output = out.getvalue()
    print("Command output:")
    for line in output.split('\n'):
        if line.strip():
            print(f"  {line}")

    # Verify items still exist after dry-run
    exam_exists = Exam.objects.filter(id=exam.id).exists()
    assignment_exists = Assignment.objects.filter(id=assignment.id).exists()

    if exam_exists and assignment_exists:
        print("\n✅ DRY-RUN works correctly - items still in database\n")
    else:
        print("\n❌ Items were deleted during dry-run (should not happen)\n")

    # Test 4: Check Query for overdue items
    print("📝 Test 4: Querying overdue items...")
    from django.utils import timezone

    now = timezone.now()
    notification_time_exam = exam.deletion_scheduled_at - timedelta(days=1) if exam.deletion_scheduled_at else None
    notification_time_assignment = assignment.deletion_scheduled_at - timedelta(days=1) if assignment.deletion_scheduled_at else None

    print(f"Current time: {now}")
    print(f"Exam notification time: {notification_time_exam}")
    print(f"Assignment notification time: {notification_time_assignment}")

    if notification_time_exam and now >= notification_time_exam:
        print("✅ Exam is eligible for notification")
    if notification_time_assignment and now >= notification_time_assignment:
        print("✅ Assignment is eligible for notification\n")

    # Summary
    print("\n=== Test Summary ===")
    print(f"✅ Test Exam ID: {exam.id}")
    print(f"✅ Test Assignment ID: {assignment.id}")
    print("\nNext steps:")
    print("1. Check notifications table: SELECT * FROM notifications_notification;")
    print("2. Run: python manage.py delete_overdue_items --dry-run")
    print("3. Run: python manage.py delete_overdue_items")
    print("4. Verify items are deleted from database\n")

if __name__ == "__main__":
    test_automatic_deletion()
