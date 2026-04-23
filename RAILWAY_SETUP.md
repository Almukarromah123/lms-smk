# Setup PostgreSQL Railway untuk Django LMS

## 1️⃣ STEP 1: Copy DATABASE_URL dari Railway

Dari screenshot Anda, di tab **Variables**, cari variable bernama `DATABASE_URL` atau `DATABASE_PUBLIC_URL`. Format-nya kurang lebih:

```
postgresql://username:password@host:port/dbname
```

### Contoh:
```
postgresql://postgres:mVGtDMMzIzUTRZKWy...@postgres.railway.internal:5432/railway
```

---

## 2️⃣ STEP 2: Setup Environment Variable Lokal

### Untuk Development (Local Machine):

**A. Buat atau Edit `.env` file di root project:**

```bash
# Django
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,lms-smk-almukarromah.up.railway.app

# Railway PostgreSQL (copy dari Railway Variables tab)
DATABASE_URL=postgresql://postgres:PASSWORD@postgres.railway.internal:5432/railway

# CSRF Settings
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000,https://lms-smk-almukarromah.up.railway.app,https://*.up.railway.app

# SSL/Security untuk production
# DEBUG_SECURITY=False
# SECURE_SSL_REDIRECT=True
# SECURE_HSTS_SECONDS=31536000
```

**B. Untuk Development lokal dengan SQLite (opsional):**
```bash
DATABASE_URL=sqlite:///db.sqlite3
```

---

## 3️⃣ STEP 3: Install Dependency (jika belum)

Pastikan `psycopg2-binary` sudah terinstall:

```bash
pip install psycopg2-binary
# atau
pip install -r requirements.txt
```

---

## 4️⃣ STEP 4: Run Migrations (Buat Tabel di PostgreSQL)

Dengan DATABASE_URL sudah di `.env`, jalankan:

```bash
# Lihat migration yang belum dijalankan
python manage.py showmigrations

# Run semua migrations
python manage.py migrate

# Jika ada error, check connection dulu:
python manage.py dbshell  # Tekan Ctrl+D untuk keluar
```

**Expected Output:**
```
Operations to perform:
  Apply all migrations: accounts, academic, attendance, assignments, ...
Running migrations:
  Applying admin.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
```

---

## 5️⃣ STEP 5: Setup Data Test (Optional)

Jika ingin membuat data test di Railway PostgreSQL:

```bash
python manage.py shell < setup_test_data.py
```

Atau jalankan manual:

```bash
python manage.py shell
```

```python
from accounts.models import User
from academic.models import School, AcademicYear, Class, Subject

# Create superuser
User.objects.create_superuser('admin', 'admin@test.com', 'Admin@123')

# Create test users
User.objects.create_user(username='teacher1', password='Teacher@123', role='TEACHER')
User.objects.create_user(username='student1', password='Student@123', role='STUDENT')

# Create School
school = School.objects.create(
    name='SMK IT AL - MUKARROMAH',
    address='Jl. Test',
    phone='0812345678'
)

# Create Academic Year
academic_year = AcademicYear.objects.create(
    year='2024/2025',
    school=school,
    is_active=True
)

print("✅ Data setup complete!")
```

---

## 6️⃣ STEP 6: Setup Railway Deployment

### A. Di Railway Dashboard:

1. **Deploy Project:**
   - Push code ke GitHub
   - Railway auto-deploy dari GitHub

2. **Setup Environment Variables:**
   - Di Railway → Project → Variables
   - Tambahkan:
     ```
     DEBUG=False
     ALLOWED_HOSTS=lms-smk-almukarromah.up.railway.app
     SECURE_SSL_REDIRECT=True
     SECURE_HSTS_SECONDS=31536000
     ```

3. **Run Migration di Production:**
   ```
   # Di Railway, untuk menjalankan manage.py:
   railway shell
   python manage.py migrate
   ```

### B. Update `settings.py` (sudah siap):

Settings sudah di-configure untuk menggunakan `DATABASE_URL` via `dj_database_url`.

---

## 7️⃣ STEP 7: Test Connection

```bash
# Test dari Django
python manage.py dbshell

# Atau dari Python
python manage.py shell
```

```python
from django.db import connection
print(connection.get_autocommit_status())  # Jika print True = connected!
```

---

## 🔍 Troubleshooting

### Error: "could not connect to server"
- ✅ Check DATABASE_URL benar
- ✅ Check PostgreSQL public network access enabled di Railway
- ✅ Check firewall tidak blocking port

### Error: "password authentication failed"
- ✅ Copy-paste DATABASE_URL dengan teliti (special chars?)
- ✅ Regenerate password di Railway Settings

### Tabel tidak muncul setelah migrate
```bash
# Check tabel yang ada
python manage.py dbshell
\dt  # List tabel

# Jika belum ada, run migrate lagi
python manage.py migrate --verbose
```

### SQLite masih terpakai
```bash
# Rename database lama
mv db.sqlite3 db.sqlite3.bak
# atau hapus jika tidak perlu
rm db.sqlite3
```

---

## 📊 Verifikasi Setup

Jalankan script test:

```bash
python manage.py check
python manage.py makemigrations --dry-run  # Tidak ada? Good!
python manage.py migrate --plan  # Check all migrations
```

---

## 🚀 Ready untuk Production!

Setelah semua berjalan:
1. Push ke GitHub
2. Railway auto-deploy
3. Monitor di Railway Deployments tab
4. Check logs: `railway logs`

---

**Butuh bantuan?** Tanyakan error message lengkapnya! 🎯
