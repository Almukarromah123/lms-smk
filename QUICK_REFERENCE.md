# ⚡ Quick Reference: Automatic Deletion System

## TL;DR

- **Exams & Assignments** automatically deleted after deadline + 7 days
- **Notifications** sent 1 day before (email + in-app)
- **Safe test mode**: `python manage.py delete_overdue_items --dry-run`
- **Real deletion**: `python manage.py delete_overdue_items`
- **Auto-run**: Add to cron for daily execution

---

## Files Modified

```
exams/models.py           → Add 2 fields for deletion tracking
exams/signals.py          → NEW: Auto-schedule deletion on save
exams/apps.py             → Register signals

assignments/models.py     → Add 2 fields for deletion tracking
assignments/signals.py    → NEW: Auto-schedule deletion on save
assignments/apps.py       → Register signals

exams/management/
  commands/
    delete_overdue_items.py → NEW: Management command

Database migrations applied ✓
```

---

## Key Workflow

**Timeline Example:**
```
Exam created on April 1, 2024 at 9:00 AM (60 min duration)
↓
Signal fires → deletion_scheduled_at = April 8, 2024 at 10:00 AM
↓
(automatic daily background check)
↓
April 7, 2024 at 10:00 AM → Notification sent: "Exam will be deleted tomorrow"
↓
April 8, 2024 at 10:00 AM → Exam deleted
```

---

## Quick Commands

```bash
# Check what would be deleted
python manage.py delete_overdue_items --dry-run

# Actually delete overdue items
python manage.py delete_overdue_items

# Help & options
python manage.py delete_overdue_items --help
```

---

## Production Setup

### Linux/Mac Cron

```bash
# Add to crontab
crontab -e

# Add this line (daily at 3 AM):
0 3 * * * cd /path/to/lms-smk && /path/to/.venv/bin/python manage.py delete_overdue_items >> /var/log/lms.log 2>&1
```

### Windows Task Scheduler

```
Program: C:\path\to\.venv\Scripts\python.exe
Arguments: manage.py delete_overdue_items
Start in: C:\path\to\lms-smk\
Trigger: Daily at 3:00 AM
```

---

## Customization

### Change Delete Delay (default 7 days)

**Edit exams/signals.py:**
```python
deletion_time = exam_end_time + timedelta(days=14)  # Change to 14 days
```

**Edit assignments/signals.py:**
```python
deletion_time = instance.due_date + timedelta(days=3)  # Change to 3 days
```

### Change Notification Timing (default 1 day before)

```python
notification_time = instance.deletion_scheduled_at - timedelta(hours=12)  # 12 hours before
```

---

## Database Queries

```python
from django.utils import timezone
from exams.models import Exam

# Items scheduled for deletion soon
Exam.objects.filter(deletion_scheduled_at__isnull=False).order_by('deletion_scheduled_at')

# Already overdue
Exam.objects.filter(deletion_scheduled_at__lt=timezone.now())

# Not yet notified
Exam.objects.filter(deletion_notified=False, deletion_scheduled_at__isnull=False)
```

---

## Testing Checklist

- [ ] Create exam/assignment with past due date
- [ ] Run: `python manage.py delete_overdue_items --dry-run`
- [ ] Verify detection: should show 1 exam/assignment
- [ ] Run: `python manage.py delete_overdue_items`
- [ ] Verify deletion: should say "Successfully deleted 2"
- [ ] Check database: items should be gone
- [ ] Check notifications: deletion record created

---

## Important Notes

⚠️ **PERMANENT DELETION** - No recovery/trash
⚠️ **KEEP BACKUPS** - Backup database before enabling
✅ **Submissions Safe** - Only parent record deleted
✅ **Email Optional** - Works even if email fails
✅ **Timezone Safe** - Uses PROJECT_TZ (Asia/Jakarta)

---

## Support Documentation

- **Full Guide**: See `AUTOMATIC_DELETION_GUIDE.md`
- **Technical**: See `IMPLEMENTATION_SUMMARY.md`
- **Test Script**: See `test_auto_deletion.py`

---

## Status: ✅ READY FOR PRODUCTION

All components tested and verified.
Tested with past-due exams/assignments - deletion confirmed successful.
