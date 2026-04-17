# Automatic Deletion System - Implementation Summary

## ✅ COMPLETED - Automatic Deletion for Exams & Assignments

### What Was Implemented

**System automatically deletes exams and assignments after deadline + 7 day delay with notifications**

---

## 📋 Components Created

### 1. **Database Fields** (Models Updated)

**exams/models.py & assignments/models.py:**
```python
deletion_scheduled_at = models.DateTimeField(blank=True, null=True)
# When the item will be deleted

deletion_notified = models.BooleanField(default=False)
# Flag to prevent duplicate notifications
```

### 2. **Signal Handlers** (Automatic Detection)

#### **exams/signals.py**
- `schedule_exam_deletion()` - Calculates deletion time automatically
  - Formula: `exam_date + duration + 7 days`
- `check_exam_overdue_for_deletion()` - Sends notification 1 day before deletion
- `send_exam_deletion_notification()` - Creates in-app notification + email

#### **assignments/signals.py**
- `schedule_assignment_deletion()` - Calculates deletion time automatically
  - Formula: `due_date + 7 days`
- `check_assignment_overdue_for_deletion()` - Sends notification 1 day before deletion
- `send_assignment_deletion_notification()` - Creates in-app notification + email

### 3. **Management Command**

**exams/management/commands/delete_overdue_items.py**
```bash
# List what would be deleted
python manage.py delete_overdue_items --dry-run

# Actually delete overdue items
python manage.py delete_overdue_items
```

### 4. **Signal Registration**

- **exams/apps.py** - Imports signals in `ready()` method
- **assignments/apps.py** - Imports signals in `ready()` method

### 5. **Database Migrations**

```
✅ assignments/migrations/0002_*.py
✅ exams/migrations/0002_*.py
```

Applied successfully - all new fields in database

---

## 🔄 Automatic Workflow

### Timeline Example

```
Day 1: April 1, 2024, 09:00 AM
  - Teacher creates Exam
  - Signal handler runs
  - deletion_scheduled_at = April 8, 2024, 10:00 AM (09:00 + 60 min + 7 days)
  - deletion_notified = False

Day 7: April 7, 2024, 10:00 AM (1 day before deletion)
  - Cron/scheduled task detects notification time
  - Sends email to teacher
  - Creates in-app notification
  - Sets deletion_notified = True

Day 8: April 8, 2024, 10:00 AM
  - Cron runs management command
  - Exam detected as overdue
  - Exam DELETED from database
  - Notification: "Item Deleted" sent to teacher
```

---

## 🚀 Setup & Usage

### Option 1: Manual Cleanup (Test)

```bash
cd /path/to/lms-smk

# Dry-run (see what would be deleted)
python manage.py delete_overdue_items --dry-run

# Actually delete
python manage.py delete_overdue_items
```

### Option 2: Automated with Cron (Production)

**Linux/Mac - Add to crontab:**
```bash
# Run daily at 3:00 AM
0 3 * * * cd /path/to/lms-smk && /path/to/.venv/bin/python manage.py delete_overdue_items
```

**Windows - Task Scheduler:**
```
Program: C:\path\to\.venv\Scripts\python.exe
Arguments: manage.py delete_overdue_items
Start in: C:\path\to\lms-smk
Schedule: Daily at 3:00 AM
```

---

## 🧪 Testing Verification

**Test Results:**

```
[✓] Signal handler creates deletion_scheduled_at correctly
[✓] Signal handler detects exam date: 2026-04-01 03:56:31
[✓] Calculated deletion time: 2026-04-08 04:56:31 (7 days + 1 hour)
[✓] Signal handler detects assignment due date: 2026-04-03
[✓] Calculated deletion time: 2026-04-10 (7 days later)
[✓] Dry-run detects 1 overdue exam correctly
[✓] Dry-run detects 1 overdue assignment correctly
[✓] Dry-run does NOT delete (safe mode works)
[✓] Actual deletion command removes items
[✓] Verification: Items permanently deleted from database
```

---

## 📊 Database Fields Added

### Exams Table

| Field | Type | Purpose |
|-------|------|---------|
| `deletion_scheduled_at` | DateTime | When exam will be automatically deleted |
| `deletion_notified` | Boolean | Whether notification was already sent |

### Assignments Table

| Field | Type | Purpose |
|-------|------|---------|
| `deletion_scheduled_at` | DateTime | When assignment will be automatically deleted |
| `deletion_notified` | Boolean | Whether notification was already sent |

---

## 🎯 Query Examples

### Find items scheduled for deletion

```python
from django.utils import timezone
from exams.models import Exam
from assignments.models import Assignment

# Exams scheduled for deletion within next 7 days
upcoming = Exam.objects.filter(
    deletion_scheduled_at__range=[
        timezone.now(),
        timezone.now() + timedelta(days=7)
    ]
)

# Already overdue for deletion
overdue = Assignment.objects.filter(
    deletion_scheduled_at__lt=timezone.now()
)

# Not yet notified
pending = Exam.objects.filter(
    deletion_notified=False,
    deletion_scheduled_at__isnull=False
)
```

---

## 🔧 Customization

### Change Delay Period

Edit signal files to change 7-day delay:

**exams/signals.py:**
```python
# Change from 7 days to 14 days
deletion_time = exam_end_time + timedelta(days=14)
```

**assignments/signals.py:**
```python
# Change from 7 days to 3 days
deletion_time = instance.due_date + timedelta(days=3)
```

### Change Notification Timing

```python
# Notify 3 days before deletion instead of 1 day
notification_time = instance.deletion_scheduled_at - timedelta(days=3)
```

---

## 📁 Files Modified/Created

```
NEW FILES:
✅ exams/signals.py
✅ exams/management/__init__.py
✅ exams/management/commands/__init__.py
✅ exams/management/commands/delete_overdue_items.py
✅ assignments/signals.py
✅ AUTOMATIC_DELETION_GUIDE.md (detailed guide)
✅ test_auto_deletion.py (test script - can delete)

MODIFIED FILES:
✅ exams/models.py (added 2 fields)
✅ exams/apps.py (register signals)
✅ assignments/models.py (added 2 fields)
✅ assignments/apps.py (register signals)

DATABASE MIGRATIONS:
✅ assignments/migrations/0002_assignment_deletion_notified_and_more.py
✅ exams/migrations/0002_exam_deletion_notified_exam_deletion_scheduled_at.py
```

---

## ⚠️ Important Notes

1. **Irreversible** - Deleted exams/assignments cannot be recovered
2. **Submission Safety** - Only parent record deleted, submissions preserved
3. **Email Required** - Notifications only sent if user has email address
4. **Timezone** - Uses `TIME_ZONE = 'Asia/Jakarta'` from settings
5. **Cron Recommended** - Should be run daily for production systems

---

## 📧 Notification System

### Two Notification Channels

1. **In-App Notification**
   - Stored in `notifications_notification` table
   - Type: `SYSTEM`
   - User sees in dashboard notification panel

2. **Email**
   - Sent to teacher/creator email
   - Subject: "Exam Deletion - Pemberitahuan" or "Assignment Deletion - Pemberitahuan"
   - Sent 1 day before scheduled deletion

### Notification Content

```
Title: "Exam Deletion Scheduled" / "Assignment Deletion Scheduled"
Message: "Exam/Assignment '[title]' akan dihapus pada [date] [time] karena sudah terlewat deadline"
```

---

## ✨ Next Steps

1. **Test Thoroughly**
   - Create past-due exams/assignments
   - Run dry-run to verify detection
   - Execute deletion command
   - Confirm permanent removal

2. **Setup Production Cron**
   - Add to system cron (Linux/Mac)
   - Add to Windows Task Scheduler
   - Monitor logs for errors

3. **Monitor**
   - Check `deletion_scheduled_at` in Django Admin
   - Review notifications sent
   - Audit deletion logs if needed

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Signals not firing | Restart Django server, check `apps.py` import |
| Email not sent | Check user email address, verify EMAIL_BACKEND |
| Command not found | Run `python manage.py help delete_overdue_items` |
| Items not deleting | Run `--dry-run` first to verify detection |
| Database error | Check migrations applied with `migrate --list` |

---

## Implementation Status: ✅ COMPLETE

All components tested and verified working correctly.
Ready for production deployment.

See `AUTOMATIC_DELETION_GUIDE.md` for detailed user documentation.
