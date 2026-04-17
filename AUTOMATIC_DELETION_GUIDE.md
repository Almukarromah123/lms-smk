## 🗑️ Automatic Deletion System for Exams & Assignments

### Fitur

Sistem otomatis menghapus exam dan assignment yang sudah melewati deadline, dengan:

✅ **Signal Handlers** - Deteksi otomatis saat exam/assignment dibuat atau diubah
✅ **Scheduling** - Penundaan 7 hari setelah deadline sebelum penghapusan
✅ **Notifikasi** - Pemberitahuan 1 hari sebelum penghapusan (email + in-app)
✅ **Management Command** - Bisa dijalankan manual atau dijadwalkan cron
✅ **Tracking** - Status deletion_scheduled_at & deletion_notified di database

---

### Cara Kerja

#### 1. **Exam Deletion Timeline**
```
[Exam Date] + [Duration] + 7 days = [Scheduled Deletion Time]

Contoh:
- Exam Date: 1 April 2024, 09:00 (2 jam)
- Exam End Time: 1 April 2024, 11:00
- Deletion Time: 8 April 2024, 11:00
- Notification: 7 April 2024, 11:00
```

#### 2. **Assignment Deletion Timeline**
```
[Due Date] + 7 days = [Scheduled Deletion Time]

Contoh:
- Due Date: 1 April 2024, 17:00
- Deletion Time: 8 April 2024, 17:00
- Notification: 7 April 2024, 17:00
```

#### 3. **Proses Notifikasi**
1. Signal handler mendeteksi saat exam/assignment disimpan
2. Scheduled deletion time dihitung otomatis
3. 1 hari sebelum deletion, sistem:
   - Membuat notifikasi in-app
   - Mengirim email ke teacher/creator
   - Set flag `deletion_notified = True`

#### 4. **Proses Penghapusan Aktual**
Ketika scheduled time tercapai → Exam/Assignment dihapus (perlu menjalankan management command)

---

### Setup & Penggunaan

#### A. Manual Testing

```bash
# Lihat item mana yang akan dihapus (dry-run)
python manage.py delete_overdue_items --dry-run

# Benar-benar hapus
python manage.py delete_overdue_items

# Hapus dengan delay custom (misal 3 hari)
python manage.py delete_overdue_items --delay-days 3
```

#### B. Setup Otomatis dengan Cron

Jalankan setiap hari pada jam 3 pagi:

**Linux/Mac:**
```bash
# Edit crontab
crontab -e

# Tambahkan baris ini:
0 3 * * * cd /path/to/lms-smk && /path/to/.venv/bin/python manage.py delete_overdue_items >> /var/log/lms-delete.log 2>&1
```

**Windows (Task Scheduler):**
```
Program: C:\path\to\.venv\Scripts\python.exe
Arguments: manage.py delete_overdue_items
Start in: C:\path\to\lms-smk\
Schedule: Daily at 3:00 AM
```

#### C. Setup dengan APScheduler (Optional)

Untuk automation yang lebih sophisticated tanpa cron, edit `lms_project/settings.py`:

```python
# Tambahkan di INSTALLED_APPS
INSTALLED_APPS = [
    ...
    'django_apscheduler',
]

# Setup APScheduler di lms_project/apps.py atau create scheduler middleware
```

---

### Tracking Status

#### Model Fields

**Exam & Assignment models:**
```python
deletion_scheduled_at  # DateTimeField - kapan akan dihapus
deletion_notified      # BooleanField - apakah notifikasi sudah dikirim
```

#### Query Examples

```python
from exams.models import Exam
from assignments.models import Assignment
from django.utils import timezone

# Exam yang sudah scheduled untuk dihapus
scheduled_exams = Exam.objects.filter(
    deletion_scheduled_at__isnull=False
).order_by('deletion_scheduled_at')

# Exam yang belum dikirim notifikasi
pending_notification = Exam.objects.filter(
    deletion_scheduled_at__isnull=False,
    deletion_notified=False
)

# Exam yang sudah waktunya dihapus
now = timezone.now()
ready_to_delete = Exam.objects.filter(
    deletion_scheduled_at__lte=now
)
```

---

### Notifikasi

Dua cara notifikasi dikirim:

#### 1. **In-App Notification**
- Tersimpan di database `notifications.Notification`
- User bisa lihat di dashboard
- Type: `SYSTEM`

#### 2. **Email**
- Dikirim ke email teacher/creator
- Hanya jika email address tersedia
- Subject: "Exam Deletion - Pemberitahuan" atau "Assignment Deletion - Pemberitahuan"

---

### Admin Panel Integration

Exam dan Assignment sudah terintegrasi dengan Django Admin. Untuk memonitor:

```
Admin Dashboard → Exams / Assignments
- Filter by: deletion_notified, deletion_scheduled_at
- Search: title
- Lihat scheduled deletion time untuk setiap item
```

---

### Behavior Customization

#### Ubah Delay Period

Edit `exams/signals.py` atau `assignments/signals.py`:

```python
# Ganti `timedelta(days=7)` dengan periode yang diinginkan
deletion_time = exam_end_time + timedelta(days=14)  # 14 hari delay
```

#### Ubah Notification Timing

Edit notify timing (default 1 hari sebelum):

```python
notification_time = instance.deletion_scheduled_at - timedelta(days=1)
# Ubah ke:
notification_time = instance.deletion_scheduled_at - timedelta(hours=6)  # 6 jam sebelum
```

#### Custom Notification Message

Edit message di `send_exam_deletion_notification()`:

```python
message = f"Custom message: {exam.title}"
```

---

### Troubleshooting

#### Signals tidak trigger

1. Pastikan `apps.py` sudah import signals di `ready()` method
2. Restart Django server
3. Check logs untuk errors

#### Email tidak dikirim

1. Verifikasi email configuration di settings.py
2. Check user email address (tidak boleh kosong)
3. Check error logs

#### Management command error

```bash
# Jalankan dengan verbose
python manage.py delete_overdue_items -v 2

# Check log output
```

---

### Files Created/Modified

```
✅ exams/models.py                          - Add deletion fields
✅ exams/signals.py                         - NEW: Signal handlers
✅ exams/apps.py                            - Register signals
✅ exams/management/commands/
   delete_overdue_items.py                  - NEW: Management command

✅ assignments/models.py                    - Add deletion fields
✅ assignments/signals.py                   - NEW: Signal handlers
✅ assignments/apps.py                      - Register signals

✅ Database migrations:
   - assignments/migrations/0002_*.py
   - exams/migrations/0002_*.py
```

---

### Next Steps

1. ✅ Database migrations applied
2. ⏳ Setup cron job untuk automatic deletion (lihat section "Setup Otomatis")
3. 🧪 Test: Buat exam/assignment dengan due date di masa lalu, lihat notification
4. 📊 Monitor: Check Admin panel untuk status deletion_scheduled_at

---

### Example Workflow

```
1. Teacher membuat Assignment dengan due_date = 1 April 2024

2. Signal triggers:
   - deletion_scheduled_at = 8 April 2024
   - deletion_notified = False

3. Cron runs at 3 AM setiap hari...

4. Pada 7 April 2024, 3 AM:
   - Sistem deteksi 1 day until deletion
   - Kirim email + notifikasi ke teacher
   - Set deletion_notified = True

5. Pada 8 April 2024, 3 AM:
   - Sistem jalankan delete_overdue_items command
   - Assignment dihapus dari database
   - Notifikasi "Item Deleted" dikirim ke teacher
```

---

### Notes & Limitations

⚠️ **Penting:**
- Penghapusan PERMANENT - tidak ada trash/recovery
- Submissions tetap aman (hanya parent Exam/Assignment yang dihapus)
- Backup database direkomendasikan sebelum enable automatic deletion

✨ **Improvements untuk maintenance:**
- Soft delete dengan archive table (optional)
- Manual override untuk item tertentu
- Audit log untuk tracking penghapusan
