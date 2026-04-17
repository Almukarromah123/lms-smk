# MySQL Migration - Perbaikan Selesai ✓

**Tanggal**: 7 April 2026
**Status**: SELESAI - Server Berjalan Normal

---

## Masalah yang Ditemukan

### 1. **Missing MySQL Driver** (CRITICAL)
```
ModuleNotFoundError: No module named 'MySQLdb'
```
**Penyebab**: Django backend MySQL memerlukan driver `MySQLdb`, tapi requirements.txt hanya punya `PyMySQL` yang tidak compatible langsung.

**Solusi**:
- Ganti `PyMySQL` tetap actif di requirements.txt
- Tambahkan adapter PyMySQL di `manage.py` dan `lms_project/settings.py`
- PyMySQL akan di-install sebagai MySQLdb adapter saat Django startup

### 2. **Cryptography Package Missing**
```
RuntimeError: 'cryptography' package is required for sha256_password...
```
**Penyebab**: PyMySQL memerlukan cryptography untuk MySQL 8.0+ authentication methods.

**Solusi**:
- Install cryptography package (sudah ada di requirements.txt)
- Verifikasi terinstall dengan `pip install cryptography`

### 3. **Database Tidak Ada**
```
OperationalError: (1049, "Unknown database 'lms_smk'")
```
**Penyebab**: Database `lms_smk` belum dibuat di MySQL.

**Solusi**:
- Buat `create_database.py` untuk membuat database otomatis
- Jalankan: `python create_database.py`

---

## File yang Dimodifikasi

### 1. `requirements.txt`
- Ganti `mysqlclient` → `PyMySQL==1.1.1` (lebih mudah di Windows, cryptography-compatible)

### 2. `lms_project/settings.py`
- Tambahkan PyMySQL adapter import di awal file:
```python
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass
```

### 3. `manage.py`
- Tambahkan PyMySQL adapter install sebelum Django setup:
```python
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass
```

### 4. Buat `create_database.py` (Baru)
- Script otomatis membuat database MySQL dengan charset UTF-8
- Jalankan hanya 1 kali: `python create_database.py`

---

## Steps Perbaikan yang Dilakukan

1. ✅ Install PyMySQL: `pip install PyMySQL==1.1.1`
2. ✅ Install Cryptography: `pip install cryptography`
3. ✅ Update `requirements.txt`
4. ✅ Tambah PyMySQL adapter di `manage.py`
5. ✅ Tambah PyMySQL adapter di `settings.py`
6. ✅ Jalankan `python create_database.py`
7. ✅ Jalankan migrations: `python manage.py migrate`
8. ✅ Create superuser: `python manage.py createsuperuser`
9. ✅ Test server: `python manage.py runserver`

---

## Konfigurasi MySQL (dari .env)

```
DB_ENGINE=django.db.backends.mysql
DB_NAME=lms_smk
DB_USER=root
DB_PASSWORD=112233
DB_HOST=127.0.0.1
DB_PORT=3306
```

---

## Cara Menjalankan Server Sekarang

```bash
# Terminal 1: Pastikan MySQL running (jika menggunakan Docker/Local)
# Contoh: docker run -d -p 3306:3306 -e MYSQL_ROOT_PASSWORD=112233 mysql:8.0

# Terminal 2: Jalankan Django server
cd c:/Users/sandi/Documents/lms-smk
python manage.py runserver

# Server akan berjalan di: http://localhost:8000
# Admin panel: http://localhost:8000/admin/
# Username: admin
```

---

## Testing Koneksi

```bash
# Test database connection:
python manage.py shell -c "
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute('SELECT 1')
    print('MySQL Connection OK!')
"

# atau gunakan:
python manage.py check
```

---

## Catatan Penting

1. **MySQL Server harus running** di `127.0.0.1:3306`
2. **Credentials** harus sesuai dengan `.env` file
3. **Database charset** sudah set ke `utf8mb4` untuk support Indonesian characters
4. **PyMySQL adapter** otomatis load saat Django start (tidak perlu manual)
5. **Semua migrations** sudah applied, siap production

---

## Next Steps (Optional)

- [ ] Restore data dari SQLite backup (jika ada)
- [ ] Create test data: `python setup_test_data.py`
- [ ] Test semua features (attendance, assignments, exams, etc)
- [ ] Setup cron untuk automatic deletion feature
- [ ] Configure email untuk notifications
