# 📚 Panduan Memasukkan Siswa ke Kelas di Django Administrator

## Persiapan Awal

Sebelum memasukkan siswa ke kelas, pastikan sudah memiliki:
1. **Siswa** - User dengan role "STUDENT"
2. **Kelas** - Class yang sudah dibuat
3. **Tahun Akademik** - Academic Year yang sudah dibuat

---

## Langkah-Langkah

### 1️⃣ MASUK KE DJANGO ADMIN

```
1. Buka browser → http://localhost:8000/admin/
2. Login dengan akun Admin
   - Username: admin
   - Password: Admin@123
```

![Admin Login](https://via.placeholder.com/300x150)

---

### 2️⃣ NAVIGASI KE ENROLLMENT

Setelah login, Anda akan melihat halaman admin. Cari dan klik:

```
ACADEMIC
  └─ Student Enrollments ← KLIK DI SINI
```

Atau akses langsung: `http://localhost:8000/admin/academic/studentenrollment/`

![Admin Home](https://via.placeholder.com/400x200)

---

### 3️⃣ TAMBAH ENROLLMENT BARU

Di halaman **Student Enrollments**, klik tombol hijau **"+ Add Student Enrollment"**

![Add Button](https://via.placeholder.com/400x100)

---

### 4️⃣ ISI FORM ENROLLMENT

Setelah klik "Add", akan muncul form dengan field berikut:

#### **Field yang Harus Diisi:**

| Field | Tipe | Keterangan |
|-------|------|-----------|
| **Student** | Dropdown Search | Pilih siswa dari daftar |
| **Class** | Dropdown Search | Pilih kelas tujuan |
| **Status** | Dropdown | Pilih status (ACTIVE, INACTIVE, GRADUATED, DROPPED) |
| **Student ID in Class** | Text | Nomor identitas siswa di kelas (opsional) |

---

### 🔍 CARA MEMILIH STUDENT

1. **Klik field "Student"**

![Student Field](https://via.placeholder.com/400x200)

2. **Akan muncul search box**, ketik nama atau username siswa

```
Contoh:
- Ketik: "student1" → akan muncul daftar siswa dengan username "student1"
- Ketik: "Andi" → akan muncul daftar siswa dengan nama "Andi"
```

3. **Pilih siswa dari dropdown** yang muncul

![Student Search](https://via.placeholder.com/400x250)

---

### 🔍 CARA MEMILIH CLASS

1. **Klik field "Class"**

![Class Field](https://via.placeholder.com/400x200)

2. **Akan muncul search box**, ketik nama kelas

```
Contoh:
- Ketik: "XI Teknik" → akan muncul kelas "XI Teknik Mesin 1"
- Ketik: "2024" → akan muncul semua kelas tahun akademik 2024
```

3. **Pilih kelas dari dropdown**

![Class Search](https://via.placeholder.com/400x250)

---

### 📊 PILIH STATUS

**Status Enrollment:**

| Status | Keterangan |
|--------|-----------|
| **ACTIVE** | Siswa aktif di kelas (pilihan default) |
| **INACTIVE** | Siswa tidak aktif (cuti/menunggu) |
| **GRADUATED** | Siswa telah lulus |
| **DROPPED** | Siswa dropout/berhenti |

- Untuk siswa baru, pilih: **ACTIVE**

![Status Dropdown](https://via.placeholder.com/400x150)

---

### 🆔 NOMOR IDENTITAS SISWA (Opsional)

**Student ID in Class** = Nomor identitas siswa di kelas tertentu

```
Contoh:
- Kelas XI Teknik Mesin 1:
  - Siswa 1: NIS = 001
  - Siswa 2: NIS = 002
  - Siswa 3: NIS = 003

Bisa diisi atau kosongkan (opsional)
```

---

### ✅ SIMPAN DATA

Setelah semua field terisi:

1. **Scroll ke bawah**
2. **Klik tombol "SAVE"** atau "SAVE AND ADD ANOTHER"

```
SAVE                    = Simpan dan kembali ke daftar
SAVE AND CONTINUE       = Simpan dan edit enrollment yang sama
SAVE AND ADD ANOTHER    = Simpan dan tambah enrollment baru
DELETE                  = Hapus enrollment (warning!)
```

![Save Buttons](https://via.placeholder.com/400x100)

---

## 📋 TAMBAH BANYAK SISWA SEKALIGUS

Jika ingin menambah banyak siswa ke satu kelas:

### **Metode 1: Satu per Satu (Recommended)**

```
1. Klik "+ Add Student Enrollment"
2. Pilih Siswa 1, Kelas A, Status ACTIVE → SAVE AND ADD ANOTHER
3. Pilih Siswa 2, Kelas A, Status ACTIVE → SAVE AND ADD ANOTHER
4. Pilih Siswa 3, Kelas A, Status ACTIVE → SAVE
```

---

### **Metode 2: Menggunakan Django Shell (Admin Advanced)**

Jika Anda terbiasa command line, bisa menggunakan:

```bash
python manage.py shell
```

```python
from accounts.models import User
from academic.models import Class, StudentEnrollment

# Ambil kelas target
kelas = Class.objects.get(name='XI Teknik Mesin 1')

# Ambil semua siswa dengan role STUDENT
siswa_list = User.objects.filter(role='STUDENT')

# Enroll semua siswa ke kelas
for siswa in siswa_list:
    enrollment, created = StudentEnrollment.objects.get_or_create(
        student=siswa,
        class_obj=kelas,
        defaults={'status': 'ACTIVE'}
    )
    if created:
        print(f"✓ {siswa.get_full_name()} ditambahkan ke {kelas.name}")
    else:
        print(f"✗ {siswa.get_full_name()} sudah terdaftar")
```

---

## 👁️ LIHAT DAFTAR ENROLLMENT

Untuk melihat siswa yang sudah terdaftar:

1. **Buka**: `http://localhost:8000/admin/academic/studentenrollment/`
2. **Anda akan melihat tabel:**

| Student | Class | Status | Enrollment Date |
|---------|-------|--------|-----------------|
| Andi Pratama | XI Teknik Mesin 1 | Active | 2026-04-07 |
| Budi Santoso | XI Teknik Mesin 1 | Active | 2026-04-07 |
| Citra Dewi | XI Teknik Mesin 2 | Active | 2026-04-07 |

---

## 🔍 MENCARI ENROLLMENT

Di halaman Student Enrollments, ada fitur search:

```
Search box: Ketik nama siswa atau username

Contoh:
- Ketik: "Andi" → tampilkan enrollment Andi
- Ketik: "student1" → tampilkan enrollment student1
```

---

## 📊 FILTER ENROLLMENT

Gunakan filter di panel kanan untuk melihat enrollment berdasarkan:

- **Status**: ACTIVE, INACTIVE, GRADUATED, DROPPED
- **Class**: Filter per kelas
- **Enrollment Date**: Filter berdasarkan tanggal pendaftaran

---

## ✏️ EDIT ENROLLMENT

Untuk mengubah enrollment yang sudah ada:

1. **Klik nama siswa** di daftar enrollment
2. **Ubah data** (status, ID siswa, dll)
3. **Klik SAVE**

---

## 🗑️ HAPUS ENROLLMENT

Untuk menghapus enrollment:

1. **Di halaman daftar**, centang checkbox siswa
2. **Pilih action**: "Delete selected enrollments"
3. **Klik GO**
4. **Konfirmasi penghapusan** di halaman berikutnya

⚠️ **HATI-HATI**: Penghapusan tidak bisa dibatalkan!

---

## ❌ MASALAH DAN SOLUSI

### ❌ Error: "Siswa tidak muncul di dropdown"

**Penyebab**: User belum dibuat atau role bukan STUDENT

**Solusi**:
1. Buka: `http://localhost:8000/admin/accounts/user/`
2. Tambah user baru dengan role "Siswa/Student"
3. Kembali ke form enrollment

---

### ❌ Error: "Kelas tidak muncul di dropdown"

**Penyebab**: Kelas belum dibuat

**Solusi**:
1. Buka: `http://localhost:8000/admin/academic/class/`
2. Klik "+ Add Class" untuk buat kelas baru
3. Kembali ke form enrollment

---

### ❌ Error: "Siswa sudah terdaftar di kelas ini"

**Penyebab**: Kombinasi siswa + kelas sudah ada di database (unique constraint)

**Solusi**:
- Edit enrollment yang sudah ada, atau
- Hapus enrollment lama, lalu buat yang baru

---

## 📞 BANTUAN LEBIH LANJUT

Jika ada pertanyaan, hubungi:
- **Admin**: http://localhost:8000/admin/
- **Dashboard**: http://localhost:8000/accounts/dashboard/

---

## 🎓 RINGKASAN WORKFLOW

```
1. Buka: http://localhost:8000/admin/
2. Navigasi: ACADEMIC → Student Enrollments
3. Klik: "+ Add Student Enrollment"
4. Isi Form:
   - Student: [Cari dan pilih siswa]
   - Class: [Cari dan pilih kelas]
   - Status: ACTIVE (default)
   - ID Siswa: [Opsional]
5. Klik: SAVE
6. ✅ Siswa berhasil di-enroll ke kelas
```

---

**Selesai! 🎉 Siswa sudah terdaftar di kelas**