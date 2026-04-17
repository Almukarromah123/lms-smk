# 📖 Panduan Lengkap: Pengelompokan Siswa ke Kelas

## 📚 Dokumentasi Tersedia

Saya sudah membuat 3 file panduan lengkap untuk Anda:

### **1. 📝 CARA_BUAT_USER_SISWA.md**
**Untuk**: Membuat user siswa baru di sistem

**Isi**:
- ✅ Cara membuat user siswa dari awal
- ✅ Mengisi data siswa (username, password, nama, email, role)
- ✅ Contoh lengkap membuat 3 siswa
- ✅ Cara reset password siswa
- ✅ Troubleshooting error

**Kapan digunakan**: Saat ada siswa baru yang belum terdaftar di sistem

---

### **2. 📝 CARA_ENROLL_SISWA.md**
**Untuk**: Memasukkan siswa ke dalam pengelompokan kelas

**Isi**:
- ✅ Langkah-langkah detail memasukkan siswa ke kelas
- ✅ Cara mencari dan memilih siswa
- ✅ Cara mencari dan memilih kelas
- ✅ Pilihan status enrollment (ACTIVE, INACTIVE, GRADUATED, DROPPED)
- ✅ Cara tambah banyak siswa sekaligus
- ✅ Troubleshooting error

**Kapan digunakan**: Saat ingin menambahkan siswa yang sudah ada ke kelas mereka

---

### **3. 📝 STRUKTUR_DATABASE_ENROLLMENT.md**
**Untuk**: Referensi teknis struktur database

**Isi**:
- ✅ Diagram hubungan model (User → Enrollment → Class)
- ✅ Detail field tabel StudentEnrollment
- ✅ Constraints dan business rules
- ✅ Contoh query Python untuk berbagai operasi
- ✅ File-file yang berhubungan di proyek

**Kapan digunakan**: Saat perlu memahami struktur database atau membuat script Python otomatis

---

## 🎯 Quick Start: Workflow Lengkap

### **Skenario: Tambah 5 Siswa Baru ke Kelas XI TM 1**

**STEP 1: Buat User Siswa** (jika belum ada)
```
File: CARA_BUAT_USER_SISWA.md
- Buka Admin → Accounts → Users
- Klik "+ Add User"
- Isi: username, password, nama, email, role=STUDENT
- Lakukan 5x untuk 5 siswa
```

**STEP 2: Enroll ke Kelas** (setelah user terbuat)
```
File: CARA_ENROLL_SISWA.md
- Buka Admin → Academic → Student Enrollments
- Klik "+ Add Student Enrollment"
- Pilih siswa, pilih kelas XI TM 1, status=ACTIVE
- Lakukan 5x untuk 5 siswa
```

**SELESAI** ✅ 5 siswa sudah masuk ke kelas XI TM 1

---

## 🚀 Akses Cepat

### **Halaman Admin yang Sering Digunakan**

```
Tambah User Siswa:
  http://localhost:8000/admin/accounts/user/add/

Lihat Daftar User:
  http://localhost:8000/admin/accounts/user/

Enroll Siswa ke Kelas:
  http://localhost:8000/admin/academic/studentenrollment/add/

Lihat Daftar Enrollment:
  http://localhost:8000/admin/academic/studentenrollment/

Lihat Daftar Kelas:
  http://localhost:8000/admin/academic/class/
```

---

## 📊 Contoh Skenario Penggunaan

### **Skenario 1: Tahun Ajaran Baru - Enrollment Massal**

**Situasi**:
- 120 siswa baru masuk ke 3 kelas paralel
- Belum ada di sistem

**Solusi**:

```
1. STEP 1: Buat semua user siswa
   File: CARA_BUAT_USER_SISWA.md
   - Admin → Accounts → Users
   - Tambah 120 user dengan role=STUDENT
   - Estimasi: 2-3 jam manual, atau gunakan import

2. STEP 2: Enroll ke kelas masing-masing
   File: CARA_ENROLL_SISWA.md
   - Admin → Academic → Student Enrollments
   - Enroll 40 siswa ke XI TM 1
   - Enroll 40 siswa ke XI TM 2
   - Enroll 40 siswa ke XI RPL 1
   - Estimasi: 1-2 jam manual

3. STEP 3 (Opsional): Gunakan Script Python
   File: STRUKTUR_DATABASE_ENROLLMENT.md
   - Buat script untuk bulk enrollment
   - Otomatis dalam hitungan detik
```

---

### **Skenario 2: Siswa Pindah Kelas**

**Situasi**:
- Siswa "Andi Pratama" ingin pindah dari XI TM 1 ke XI TM 2

**Solusi**:

```
1. Buka: http://localhost:8000/admin/academic/studentenrollment/
2. Cari enrollment "Andi Pratama" di kelas XI TM 1
3. Edit: Ubah class_obj menjadi XI TM 2
4. Klik SAVE
5. Selesai ✅
```

---

### **Skenario 3: Siswa Graduation/Lulus**

**Situasi**:
- 35 siswa XII RPL 1 sudah lulus

**Solusi**:

```
1. Buka: http://localhost:8000/admin/academic/studentenrollment/
2. Filter: class_obj = "XII RPL 1"
3. Pilih semua 35 siswa (centang checkbox)
4. Action: "Update status to GRADUATED"
5. Klik GO
6. Selesai ✅
```

---

## 🔍 Field Penting yang Perlu Diketahui

### **Tabel: StudentEnrollment**

| Field | Deskripsi | Contoh |
|-------|-----------|--------|
| **Student** | Siswa yang di-enroll | "Andi Pratama" |
| **Class** | Kelas target | "XI Teknik Mesin 1" |
| **Status** | Status enrollment | "ACTIVE", "INACTIVE", "GRADUATED" |
| **Student ID in Class** | Nomor urut siswa | "001", "002", dst |
| **Enrollment Date** | Tanggal terdaftar | 2026-04-07 (auto) |

---

## ⚠️ Penting: Aturan Sistem

### **✅ Boleh Dilakukan**

```
✓ 1 siswa di 2 kelas berbeda
  Contoh: Andi di XI TM 1 + XI TM 2 (praktik)

✓ Status berbeda untuk 1 siswa
  Contoh: Andi status ACTIVE, Budi status GRADUATED

✓ Ubah status enrollment
  Contoh: ACTIVE → GRADUATED, ACTIVE → INACTIVE

✓ Ubah kelas siswa
  Contoh: Pindah dari XI TM 1 ke XI TM 2
```

### **❌ Tidak Boleh Dilakukan**

```
✗ 1 siswa yang sama di 1 kelas yang sama 2x
  Error: UNIQUE constraint failed
  Contoh: Andi di XI TM 1 (sudah pernah enroll)

✗ User bukan STUDENT ke enrollment
  Error: limit_choices_to failed
  Contoh: Enroll guru/admin ke kelas

✗ Kelas yang tidak ada
  Error: Does not exist
  Contoh: Enroll ke kelas yang sudah dihapus
```

---

## 🎓 Admin Workflow Overview

```
┌─────────────────────────────────────────────────────────┐
│ 1. BUAT USER SISWA                                      │
│    • Accounts → Users → + Add User                      │
│    • Isi: username, password, nama, email, role         │
│    • Save                                               │
└──────────────┬──────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────┐
│ 2. ENROLL KE KELAS                                      │
│    • Academic → Student Enrollments → + Add             │
│    • Pilih: student, class, status                      │
│    • Save                                               │
└──────────────┬──────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────┐
│ 3. SISWA SIAP MENGGUNAKAN SISTEM                        │
│    • Login dengan username/password                     │
│    • Akses dashboard sesuai kelas                       │
│    • Lihat assignments, grades, attendance              │
└─────────────────────────────────────────────────────────┘
```

---

## 📞 Need Help?

### **Jika Ada Pertanyaan**

1. **Cara membuat siswa baru?**
   → Baca: `CARA_BUAT_USER_SISWA.md`

2. **Cara enroll siswa ke kelas?**
   → Baca: `CARA_ENROLL_SISWA.md`

3. **Bagaimana struktur databasenya?**
   → Baca: `STRUKTUR_DATABASE_ENROLLMENT.md`

4. **Ingin membuat script otomatis?**
   → Lihat: Bagian Query Contoh di `STRUKTUR_DATABASE_ENROLLMENT.md`

---

## 📋 Checklist: Setup Awal Sistem

- [ ] ✅ Buat School (Admin → Academic → Schools)
- [ ] ✅ Buat Academic Year (Admin → Academic → Academic Years)
- [ ] ✅ Buat Subjects (Admin → Academic → Subjects)
- [ ] ✅ Buat Classes (Admin → Academic → Classes)
- [ ] ✅ Assign Teachers to Classes (Admin → Academic → Class Subject Teachers)
- [ ] ✅ Buat User Siswa (Admin → Accounts → Users)
- [ ] ✅ Enroll Siswa ke Kelas (Admin → Academic → Student Enrollments)
- [ ] ✅ Test login siswa (http://localhost:8000/accounts/login/)

---

**🎉 Selesai! Anda siap mengelola pengelompokan siswa ke kelas**

Untuk pertanyaan lebih lanjut, lihat dokumentasi terkait di folder ini.