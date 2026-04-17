## 🚀 Migrasi Database: MySQL → PostgreSQL Supabase - COMPLETED ✅

### ✅ Yang Sudah Dilakukan:

#### 1. **Update settings.py** ✓
- ✅ Hapus PyMySQL adapter (`pymysql.install_as_MySQLdb()`)
- ✅ Tambah import `dj_database_url`
- ✅ Ganti konfigurasi database lama dengan `dj-database-url`
- ✅ Database URL sekarang dari environment variable `DATABASE_URL`

**Sebelum:**
```python
DB_ENGINE = config('DB_ENGINE', default='django.db.backends.mysql')
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        # ... dsb
    }
}
```

**Sesudah:**
```python
import dj_database_url

DATABASE_URL = config('DATABASE_URL', default='postgresql://localhost:5432/lms_smk')
DATABASES = {
    'default': dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,
        conn_health_checks=True,
    )
}
```

#### 2. **Update requirements.txt** ✓
- ✅ Hapus `PyMySQL==1.1.1`
- ✅ Tambah `psycopg2-binary==2.9.9`
- ✅ Tambah `dj-database-url==2.1.0`
- ✅ Dependencies sudah diinstall

**Perubahan:**
```diff
- PyMySQL==1.1.1
+ psycopg2-binary==2.9.9
+ dj-database-url==2.1.0
```

#### 3. **Update Environment Variables** ✓
- ✅ `.env` sudah diupdate dengan DATABASE_URL Supabase
- ✅ `.env.example` sudah diupdate dengan contoh konfigurasi

**File .env:**
```env
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,*
SECRET_KEY=django-insecure-e7ju0#*n99&7qo80q!wvo3#h*njp_n&&gki^4ug2!9us7vcl&+
DATABASE_URL=postgresql://postgres:Almukarromah.2022@db.szmwnoiaqphblekvxemu.supabase.co:5432/postgres
```

#### 4. **System Check** ✓
- ✅ `python manage.py check` passed (0 issues)

---

## 📋 Langkah Selanjutnya untuk Migrasi Data:

### **Step 1: Backup Data MySQL Lama (PENTING!)**
```bash
# Export semua data dari MySQL ke file SQL
mysqldump -u root -p112233 -h 127.0.0.1 lms_smk > backup_mysql.sql
```

### **Step 2: Test Koneksi ke Supabase**
Pastikan Supabase instance sudah aktif dan IP Anda sudah di-whitelist:
1. Login ke https://supabase.com
2. Pergi ke Project Settings → Database
3. Scroll ke "Connection String" dan gunakan format PostgreSQL
4. Pastikan "Allow connections from anywhere" atau add your IP

### **Step 3: Jalankan Migrations ke PostgreSQL**
```bash
# Buat migrations baru (jika ada)
python manage.py makemigrations

# Terapkan migrations ke PostgreSQL
python manage.py migrate
```

### **Step 4: Migrasi Data dari MySQL ke PostgreSQL (Pilih salah satu)**

**Opsi A: Menggunakan Django Data Migration (Recommended)**
```bash
# 1. Export data dari MySQL ke JSON
python manage.py dumpdata > data_mysql.json

# 2. Load data ke PostgreSQL
python manage.py loaddata data_mysql.json
```

**Opsi B: Menggunakan SQL Direct (Jika data besar)**
```bash
# Gunakan tool seperti pgAdmin atau DBeaver untuk import data
# atau gunakan psycopg2 script custom
```

### **Step 5: Verifikasi Data**
```bash
# Login ke Django shell dan check data
python manage.py shell
>>> from accounts.models import User
>>> User.objects.count()  # Pastikan data sudah terimport

# atau
python manage.py dbshell
# Di psql prompt:
# SELECT COUNT(*) FROM accounts_user;
```

---

## 🔧 Konfigurasi Detail

### **dj-database-url Features:**
```python
DATABASES = {
    'default': dj_database_url.config(
        default=DATABASE_URL,           # URL dari .env
        conn_max_age=600,              # Connection pooling: 600 detik
        conn_health_checks=True,       # Automatic health checks
    )
}
```

### **Environment Variable Options:**

**For Local PostgreSQL:**
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/lms_smk
```

**For Supabase:**
```env
DATABASE_URL=postgresql://postgres:password@host.supabase.co:5432/postgres
```

**For SQLite (fallback):**
```env
DATABASE_URL=sqlite:///db.sqlite3
```

**For MySQL (jika masih diperlukan):**
```env
DATABASE_URL=mysql://user:password@localhost:3306/lms_smk
```

---

## 🔐 Security Notes

### ✅ Best Practices untuk Supabase:

1. **Jangan hardcode password di settings.py**
   - ✅ Sudah menggunakan environment variable via decouple

2. **IP Whitelisting di Supabase:**
   - Buka Supabase project → Settings → Database
   - Add IP address Anda atau server yang akan akses

3. **Password Management:**
   - Change default password di Supabase console
   - Gunakan strong password (sudah Anda lakukan)

4. **SSL Connection (Opsional tapi Recommended):**
   ```env
   DATABASE_URL=postgresql://...?sslmode=require
   ```

---

## 📝 File-File yang Diubah:

| File | Perubahan |
|------|-----------|
| `lms_project/settings.py` | Hapus PyMySQL, tambah dj-database-url |
| `requirements.txt` | Hapus PyMySQL, tambah psycopg2-binary & dj-database-url |
| `.env` | Update DATABASE_URL ke Supabase |
| `.env.example` | Update contoh konfigurasi |

---

## ✅ Checklist Migrasi:

- [x] Update settings.py dengan dj-database-url
- [x] Tambah psycopg2-binary ke requirements.txt
- [x] Install dependencies baru (psycopg2-binary, dj-database-url)
- [x] Update .env dengan DATABASE_URL Supabase
- [x] System check passed
- [ ] Backup data MySQL lama (PENTING!)
- [ ] Verifikasi koneksi ke Supabase
- [ ] Run migrations: `python manage.py migrate`
- [ ] Migrasi data dari MySQL ke PostgreSQL
- [ ] Verifikasi data di PostgreSQL
- [ ] Update CI/CD pipelines (jika ada) untuk DATABASE_URL
- [ ] Test aplikasi di staging environment
- [ ] Deploy ke production

---

## 🆘 Troubleshooting:

### Error: "could not translate host name to address"
**Penyebab:** Network issue atau Supabase instance not active
**Solusi:**
1. Check internet connection
2. Verify Supabase project is active
3. Verify DATABASE_URL format benar
4. Test dengan ping ke host: `ping db.szmwnoiaqphblekvxemu.supabase.co`

### Error: "FATAL: password authentication failed"
**Penyebab:** Password salah atau user tidak ada
**Solusi:**
1. Verify DATABASE_URL password benar
2. Check Supabase database users
3. Reset password di Supabase console

### Error: "psycopg2.OperationalError: could not connect to server"
**Penyebab:** Connection timeout atau IP tidak whitelisted
**Solusi:**
1. Whitelist IP di Supabase settings
2. Check if Supabase is in a maintenance window
3. Try from different network

---

## 📚 Referensi:

- **dj-database-url Documentation:** https://github.com/jacobian/dj-database-url
- **Supabase PostgreSQL Setup:** https://supabase.com/docs/guides/getting-started
- **Django Database Configuration:** https://docs.djangoproject.com/en/4.2/ref/settings/#databases
- **psycopg2 Documentation:** https://www.psycopg.org/

---

**Status:** ✅ Configuration Complete, Ready for Data Migration

**Next Step:** Follow "Langkah Selanjutnya untuk Migrasi Data" section above
