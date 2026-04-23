# 🚀 Setup PostgreSQL Railway - Otomatis (Tanpa Input URL Manual)

## 📋 Langkah-Langkah Sederhana

### **STEP 1: Buka Railway dan Login**
1. Pergi ke https://railway.app
2. Login dengan akun Anda (GitHub/Google)
3. Buat project baru atau pilih project yang sudah ada

---

### **STEP 2: Tambah PostgreSQL Service di Railway**
1. Di dashboard project, klik **"+ New"** atau **"Add Service"**
2. Pilih **"Database"** → **"PostgreSQL"**
3. Railway otomatis akan:
   - ✅ Membuat database PostgreSQL
   - ✅ Membuat username dan password random (aman)
   - ✅ **Otomatis set environment variables** → TIDAK perlu copy-paste URL!

---

### **STEP 3: Verifikasi Environment Variables di Railway**
1. Klik service PostgreSQL yang baru dibuat
2. Lihat tab **"Variables"** → Akan ada:
   - `DATABASE_URL` (otomatis terisi)
   - `PGHOST`
   - `PGPORT`
   - `PGDATABASE`
   - `PGUSER`
   - `PGPASSWORD`

**Tidak perlu copy-paste! Railway handle semuanya.**

---

### **STEP 4: Deploy/Push Django App ke Railway**

#### **Opsi A: Connect GitHub (Recommended)**
```bash
# 1. Push project ke GitHub
git add .
git commit -m "Setup Railway PostgreSQL"
git push origin main

# 2. Di Railway dashboard:
#    - Klik "+ New"
#    - Pilih "GitHub Repo"
#    - Pilih repo lms-smk Anda
#    - Railway otomatis deploy setiap ada push ke main
```

#### **Opsi B: Deploy Manual via Railway CLI**
```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login ke Railway
railway login

# 3. Link project ke Railway
railway init

# 4. Deploy
railway up
```

---

### **STEP 5: Settings.py Sudah Siap (Tidak Perlu Edit!)**

File `lms_project/settings.py` sudah benar:

```python
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}
```

**Railway otomatis inject `DATABASE_URL` ke environment → Django langsung terkoneksi!**

---

### **STEP 6: Railway Run Migrations Otomatis**

Ada 2 cara:

#### **Opsi 1: Set Procfile dengan Migration Command**
Buat file `Procfile` di root project:
```
release: python manage.py migrate
web: gunicorn lms_project.wsgi
```

**Railway akan:**
1. Jalankan `python manage.py migrate` sebelum deploy
2. Jalankan Django app dengan `gunicorn`

#### **Opsi 2: Railway Deployment Tab**
1. Di Railway → Project → Settings
2. Cari "Deploy" atau "Build & Deploy"
3. Set **Build Command**: 
   ```bash
   python manage.py migrate
   ```

---

### **STEP 7: Verifikasi Koneksi**

Railway CLI:
```bash
# Check logs
railway logs

# Shell ke container
railway shell
python manage.py shell
>>> from accounts.models import User
>>> User.objects.count()
```

Atau di Django dashboard/admin:
```
https://your-railway-app.up.railway.app/admin/
```

---

## 📦 requirements.txt (Pastikan Lengkap)

```
Django==4.2.0
python-decouple==3.8
dj-database-url==2.1.0
psycopg2-binary==2.9.9
gunicorn==21.2.0
whitenoise==6.5.0
Pillow==10.0.0
crispy-forms==2.1
crispy-tailwind==0.5.1
django-filter==23.3
django-import-export==3.3.1
reportlab==4.0.7
pytz==2023.3
```

---

## ⚙️ Railway Environment Variables (Otomatis dari PostgreSQL Service)

**Tidak perlu setting manual, Railway set otomatis:**

| Variable | Contoh | Sumber |
|----------|--------|--------|
| `DATABASE_URL` | `postgresql://user:pass@host:5432/db` | PostgreSQL Service |
| `PGHOST` | `postgres-xxx.railway.app` | PostgreSQL Service |
| `PGPORT` | `5432` | PostgreSQL Service |
| `PGDATABASE` | `railway` | PostgreSQL Service |
| `PGUSER` | `postgres` | PostgreSQL Service |
| `PGPASSWORD` | `xxxxx` | PostgreSQL Service |

**Plus ini dari Django app settings:**
```
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=your-app.up.railway.app
```

---

## 🔐 File .env Local (Untuk Development)

Buat `.env` di root project untuk testing lokal:
```env
DEBUG=True
SECRET_KEY=dev-secret-key-only
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgresql://postgres:password@localhost:5432/lms_smk
```

---

## 🆘 Troubleshooting Railway

### **❌ Error: "No module named 'psycopg2'"**
**Solusi:** Pastikan di `requirements.txt` ada:
```
psycopg2-binary==2.9.9
```

### **❌ Error: "Connection refused"**
**Solusi:**
1. Verifikasi PostgreSQL service sudah running di Railway
2. Check DATABASE_URL di Railway Variables tab
3. Railway logs: `railway logs`

### **❌ Error: "SECRET_KEY not set"**
**Solusi:** Set di Railway project Variables:
```
SECRET_KEY=your-very-long-random-secret-key-here
DEBUG=False
```

### **❌ Error: "Static files not found"**
**Solusi:** Django collect static otomatis jika ada di Procfile:
```
release: python manage.py migrate && python manage.py collectstatic --noinput
```

---

## ✅ Checklist Setup Railway

- [ ] Create Railway project
- [ ] Add PostgreSQL service (otomatis set DATABASE_URL)
- [ ] Add Django app service (GitHub atau CLI)
- [ ] Set environment variables (DEBUG, SECRET_KEY, ALLOWED_HOSTS)
- [ ] Create `Procfile` dengan migration & gunicorn commands
- [ ] Push ke GitHub atau deploy via CLI
- [ ] Check logs: `railway logs`
- [ ] Test di: `https://your-app.up.railway.app`
- [ ] Test admin: `https://your-app.up.railway.app/admin/`
- [ ] Create superuser: `railway shell` → `python manage.py createsuperuser`

---

## 🎯 Ringkasan Proses

```
GitHub Repo
    ↓
Railway + PostgreSQL Service
    ↓
Railway Auto Set DATABASE_URL env var
    ↓
Django Connect via dj-database-url
    ↓
Procfile Run Migrations
    ↓
App Running! ✅
```

**Tidak perlu copy-paste URL, Railway handle semuanya!** 🚀
