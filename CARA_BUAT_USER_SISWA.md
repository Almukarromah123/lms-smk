# 👤 Panduan Membuat User Siswa Baru di Django Admin

## Persiapan

Sebelum bisa memasukkan siswa ke kelas, siswa harus ada sebagai **User** dengan role **STUDENT** di sistem.

---

## Langkah-Langkah Membuat User Siswa

### 1️⃣ MASUK KE DATABASE USER

```
1. Buka: http://localhost:8000/admin/
2. Login dengan akun Admin
3. Klik: ACCOUNTS → Users
```

Atau akses langsung: `http://localhost:8000/admin/accounts/user/`

---

### 2️⃣ TAMBAH USER BARU

Klik tombol hijau **"+ Add User"**

![Add User Button](https://via.placeholder.com/400x100)

---

### 3️⃣ ISI DATA SISWA

### **STEP 1: Username & Password** *(Wajib)*

| Field | Contoh | Keterangan |
|-------|--------|-----------|
| **Username** | `student1` | Username unik, untuk login |
| **Password** | Klik untuk generate | Password siswa (harus aman) |
| **Password (again)** | Auto | Konfirmasi password |

```
Username Tips:
- Gunakan format: student1, student2, student3, dst
- Atau: andi_pratama, budi_santoso, dst
- Jangan ada spasi atau karakter khusus
```

![Step 1](https://via.placeholder.com/400x150)

---

### **STEP 2: Personal Info** *(Wajib)*

Scroll ke bawah, isi section "PERSONAL INFO":

| Field | Contoh | Keterangan |
|-------|--------|-----------|
| **First Name** | `Andi` | Nama depan siswa |
| **Last Name** | `Pratama` | Nama belakang siswa |
| **Email** | `andi@school.com` | Email siswa |

![Step 2](https://via.placeholder.com/400x150)

---

### **STEP 3: Pilih Role** *(PENTING!)*

Scroll ke bawah, isi section "PERMISSIONS":

| Field | Nilai | Keterangan |
|-------|-------|-----------|
| **Role** | 🟢 Pilih **Siswa/Student** | Harus STUDENT, bukan ADMIN atau TEACHER |
| **Is Staff** | ☐ Kosongkan | Jangan centang |
| **Is Superuser** | ☐ Kosongkan | Jangan centang |

⚠️ **PENTING**: Pastikan Role = **Siswa/Student**

![Step 3 - Role Selection](https://via.placeholder.com/400x150)

---

### **STEP 4: Data Tambahan** *(Opsional)*

Scroll ke bawah, ada field tambahan:

| Field | Contoh | Keterangan |
|-------|--------|-----------|
| **Phone** | `081234567890` | Nomor telepon siswa (opsional) |
| **Address** | `Jl. Merdeka No. 123` | Alamat siswa (opsional) |
| **Date of Birth** | `2008-01-15` | Tanggal lahir (opsional) |
| **Gender** | `M / F` | Jenis kelamin (opsional) |
| **Bio** | `Siswa aktif` | Biodata tambahan (opsional) |
| **Profile Picture** | Upload foto | Foto profil (opsional) |

*Field ini bisa diisi nanti kalau ada informasi yang kurang*

---

### ✅ SIMPAN USER

Setelah semua field wajib diisi:

1. **Scroll ke bawah**
2. **Klik tombol "SAVE"** atau "SAVE AND ADD ANOTHER"

```
SAVE                     = Simpan dan kembali ke daftar user
SAVE AND CONTINUE EDITING = Simpan dan edit user yang sama
SAVE AND ADD ANOTHER     = Simpan dan buat user baru
```

![Save Buttons](https://via.placeholder.com/400x100)

---

## 📋 CONTOH LENGKAP: BUAT 3 SISWA BARU

### **Siswa 1: Andi Pratama**

```
Username:    student1
Password:    Andi@1234 (generate atau set manual)
First Name:  Andi
Last Name:   Pratama
Email:       andi.pratama@school.com
Role:        Siswa/Student
Phone:       081234567890
Gender:      M
Status:      ACTIVE
```

→ Klik **SAVE AND ADD ANOTHER**

---

### **Siswa 2: Budi Santoso**

```
Username:    student2
Password:    Budi@1234
First Name:  Budi
Last Name:   Santoso
Email:       budi.santoso@school.com
Role:        Siswa/Student
Phone:       081234567891
Gender:      M
Status:      ACTIVE
```

→ Klik **SAVE AND ADD ANOTHER**

---

### **Siswa 3: Citra Dewi**

```
Username:    student3
Password:    Citra@1234
First Name:  Citra
Last Name:   Dewi
Email:       citra.dewi@school.com
Role:        Siswa/Student
Phone:       081234567892
Gender:      F
Status:      ACTIVE
```

→ Klik **SAVE**

---

## 🔄 LANGKAH LANJUTAN: MASUKKAN KE KELAS

Setelah 3 siswa dibuat, sekarang masukkan ke kelas:

1. **Buka**: `http://localhost:8000/admin/academic/studentenrollment/`
2. **Klik**: "+ Add Student Enrollment"
3. **Enroll** siswa 1, 2, 3 ke kelas yang dikehendaki

📖 Lihat: **CARA_ENROLL_SISWA.md** untuk detail

---

## 👁️ LIHAT DAFTAR USER SISWA

Untuk melihat semua siswa yang sudah dibuat:

1. **Buka**: `http://localhost:8000/admin/accounts/user/`
2. **Filter**: Pilih Role = "Siswa/Student"

Tabel akan menampilkan:

| Username | Full Name | Email | Role | Active |
|----------|-----------|-------|------|--------|
| student1 | Andi Pratama | andi@school.com | Siswa | ✓ |
| student2 | Budi Santoso | budi@school.com | Siswa | ✓ |
| student3 | Citra Dewi | citra@school.com | Siswa | ✓ |

---

## 🔐 RESET PASSWORD SISWA

Jika siswa lupa password:

1. **Buka**: `http://localhost:8000/admin/accounts/user/`
2. **Klik nama siswa** di daftar
3. **Scroll ke section PASSWORD**
4. **Klik "This form has been replaced with a new one"** → **"Change password"**
5. **Masukkan password baru**
6. **Klik SAVE**

---

## ✏️ EDIT DATA SISWA

Untuk mengubah data siswa:

1. **Buka**: `http://localhost:8000/admin/accounts/user/`
2. **Klik nama siswa** yang ingin diubah
3. **Edit data** (nama, email, phone, dll - kecuali role)
4. **Klik SAVE**

---

## ❌ MASALAH DAN SOLUSI

### ❌ Error: "Username sudah ada"

**Penyebab**: Username sudah digunakan user lain

**Solusi**: Gunakan username yang berbeda

```
Coba: student_andi, andi_001, student_01, dst
```

---

### ❌ Error: "Format Email tidak valid"

**Penyebab**: Email tidak sesuai format

**Solusi**: Gunakan format email yang benar

```
Format: nama@domain.com
Contoh: andi@school.com, student1@lms.local
```

---

### ❌ Error: "Password terlalu pendek"

**Penyebab**: Password kurang dari 8 karakter

**Solusi**: Gunakan password minimal 8 karakter

```
✓ Benar:  Andi@1234 (8 karakter)
✗ Salah:  andi123 (7 karakter)
```

---

## 📞 QUICK REFERENCE

### **Buat Siswa Baru**
```
1. Admin → Accounts → Users
2. "+ Add User"
3. Isi: Username, Password, First Name, Last Name, Email, Role=STUDENT
4. SAVE
```

### **Enroll ke Kelas**
```
1. Admin → Academic → Student Enrollments
2. "+ Add Student Enrollment"
3. Pilih: Student, Class, Status=ACTIVE
4. SAVE
```

### **Reset Password Siswa**
```
1. Admin → Accounts → Users
2. Klik siswa
3. "Change password"
4. Isi password baru
5. SAVE
```

---

**Selesai! 🎉 Siswa baru sudah terbuat dan siap di-enroll ke kelas**