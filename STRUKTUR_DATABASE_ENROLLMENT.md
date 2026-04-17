# 🏗️ Struktur Database - Enrollment Siswa

## Diagram Hubungan Model

```
┌─────────────────────────────────────────────────────────────┐
│                      USER (accounts_user)                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ id                                                   │   │
│  │ username          (unik)                            │   │
│  │ password          (hashed)                          │   │
│  │ email             (unik)                            │   │
│  │ first_name        (e.g., "Andi")                    │   │
│  │ last_name         (e.g., "Pratama")                 │   │
│  │ role              (ADMIN, TEACHER, STUDENT)         │   │
│  │ is_staff          (boolean)                         │   │
│  │ is_superuser      (boolean)                         │   │
│  │ phone             (opsional)                        │   │
│  │ address           (opsional)                        │   │
│  │ gender            (M/F, opsional)                   │   │
│  │ date_of_birth     (opsional)                        │   │
│  │ created_at        (timestamp)                       │   │
│  │ updated_at        (timestamp)                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│                     Role = "STUDENT" ←─┐                    │
└──────────────────────────────────────────────┐──────────────┘
                                               │
                        (ForeignKey)            │
                                               │
┌───────────────────────────────────────────────▼──────────────┐
│         STUDENT ENROLLMENT (academic_studentenrollment)      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ id                    (UUID, primary key)            │   │
│  │ student_id    ←──────── (FK to User, role=STUDENT)   │   │
│  │ class_obj_id  ←──────── (FK to Class)                │   │
│  │ enrollment_date       (auto_now_add, hari ini)       │   │
│  │ status                (ACTIVE/INACTIVE/GRADUATED)    │   │
│  │ student_id_in_class   (nomor urut di kelas)          │   │
│  │ created_at            (timestamp)                    │   │
│  │ updated_at            (timestamp)                    │   │
│  │                                                      │   │
│  │ unique_together: (student_id, class_obj_id)          │   │
│  │ (tidak boleh 1 siswa masuk kelas yang sama 2x)       │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│                    (ForeignKey)                              │
└──────────────────────────────────────────┬───────────────────┘
                                           │
                                           │
┌──────────────────────────────────────────▼──────────────────┐
│              CLASS (academic_class)                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ id                    (UUID, primary key)            │   │
│  │ school_id     ←──────── (FK to School)               │   │
│  │ name                  (e.g., "XI Teknik Mesin 1")    │   │
│  │ grade                 (X, XI, XII)                   │   │
│  │ academic_year_id      (FK to AcademicYear)           │   │
│  │ homeroom_teacher_id   (FK to User, role=TEACHER)     │   │
│  │ max_students          (e.g., 40)                     │   │
│  │ room_number           (e.g., "R-101")                │   │
│  │ created_at            (timestamp)                    │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  get_student_count() → jumlah siswa aktif di kelas          │
└──────────────────────────────────────────────────────────────┘
```

---

## Tabel: StudentEnrollment

### **Field Details**

| Field | Tipe | Deskripsi | Contoh |
|-------|------|-----------|--------|
| `id` | UUID | Primary key (auto generate) | `a1b2c3d4...` |
| `student_id` | FK | Referensi ke User (role=STUDENT) | `5` |
| `class_obj_id` | FK | Referensi ke Class | `11` |
| `enrollment_date` | Date | Tanggal pendaftaran (auto set) | `2026-04-07` |
| `status` | CharField | Status enrollment | `ACTIVE` |
| `student_id_in_class` | CharField | Nomor urut siswa di kelas | `001`, `002`, ... |
| `created_at` | DateTime | Waktu record dibuat | `2026-04-07 10:30:00` |
| `updated_at` | DateTime | Waktu record diubah | `2026-04-07 10:30:00` |

---

### **Status Values**

```python
STATUS_CHOICES = (
    ('ACTIVE', 'Active'),           # Siswa aktif (default)
    ('INACTIVE', 'Inactive'),       # Siswa tidak aktif/cuti
    ('GRADUATED', 'Graduated'),     # Siswa lulus
    ('DROPPED', 'Dropped'),         # Siswa dropout
)
```

---

## Contoh Data dalam Database

### **Tabel: accounts_user**

```sql
SELECT * FROM accounts_user WHERE role='STUDENT' LIMIT 3;
```

| id | username | first_name | last_name | email | role |
|----|----------|-----------|-----------|-------|------|
| 5 | student1 | Andi | Pratama | andi@school.com | STUDENT |
| 6 | student2 | Budi | Santoso | budi@school.com | STUDENT |
| 7 | student3 | Citra | Dewi | citra@school.com | STUDENT |

---

### **Tabel: academic_class**

```sql
SELECT * FROM academic_class;
```

| id | name | grade | academic_year_id | max_students |
|----|------|-------|------------------|--------------|
| 1 | XI Teknik Mesin 1 | XI | 1 | 40 |
| 2 | XI Teknik Mesin 2 | XI | 1 | 40 |
| 3 | XII RPL 1 | XII | 1 | 35 |

---

### **Tabel: academic_studentenrollment**

```sql
SELECT * FROM academic_studentenrollment;
```

| id | student_id | class_obj_id | enrollment_date | status | student_id_in_class |
|----|------------|-------------|-----------------|--------|-------------------|
| 1 | 5 | 1 | 2026-04-07 | ACTIVE | 001 |
| 2 | 6 | 1 | 2026-04-07 | ACTIVE | 002 |
| 3 | 7 | 2 | 2026-04-07 | ACTIVE | 001 |

---

## Constraints & Business Rules

### **1. Unique Constraint**

```python
unique_together = ('student_id', 'class_obj_id')
```

**Artinya**:
- ✅ **Boleh**: Andi + Kelas XI TM 1
- ✅ **Boleh**: Andi + Kelas XI TM 2 (kelas berbeda)
- ❌ **Tidak Boleh**: Andi + Kelas XI TM 1 (duplikat)

**Error jika coba**:
```
IntegrityError: UNIQUE constraint failed
```

---

### **2. Foreign Key Constraint - Student**

```python
ForeignKey(User, limit_choices_to={'role': 'STUDENT'})
```

**Artinya**:
- ✅ Hanya User dengan role='STUDENT' bisa dipilih
- ❌ User dengan role='ADMIN' atau 'TEACHER' tidak bisa dipilih

---

### **3. Foreign Key Constraint - Class**

```python
ForeignKey(Class, on_delete=models.CASCADE)
```

**Artinya**:
- Jika kelas dihapus, enrollment juga ikut dihapus (cascade delete)

---

## Query Contoh

### **1. Lihat semua siswa di kelas tertentu**

```python
from academic.models import StudentEnrollment, Class

kelas = Class.objects.get(name='XI Teknik Mesin 1')
siswa_list = StudentEnrollment.objects.filter(
    class_obj=kelas,
    status='ACTIVE'
).select_related('student')

for enrollment in siswa_list:
    print(f"{enrollment.student.get_full_name()} - {enrollment.status}")
```

**Output**:
```
Andi Pratama - ACTIVE
Budi Santoso - ACTIVE
```

---

### **2. Lihat semua kelas siswa tertentu**

```python
from accounts.models import User
from academic.models import StudentEnrollment

siswa = User.objects.get(username='student1')
kelas_list = StudentEnrollment.objects.filter(
    student=siswa,
    status='ACTIVE'
).select_related('class_obj')

for enrollment in kelas_list:
    print(f"{enrollment.class_obj.name} - {enrollment.status}")
```

**Output**:
```
XI Teknik Mesin 1 - ACTIVE
```

---

### **3. Jumlah siswa aktif di kelas**

```python
from academic.models import Class

kelas = Class.objects.get(name='XI Teknik Mesin 1')
jumlah_siswa = kelas.get_student_count()
# atau
jumlah_siswa = kelas.enrollments.filter(status='ACTIVE').count()

print(f"Jumlah siswa aktif: {jumlah_siswa}")
```

---

### **4. Enroll siswa ke kelas menggunakan Python**

```python
from accounts.models import User
from academic.models import Class, StudentEnrollment

siswa = User.objects.get(username='student1')
kelas = Class.objects.get(name='XI Teknik Mesin 1')

# Buat enrollment baru
enrollment, created = StudentEnrollment.objects.get_or_create(
    student=siswa,
    class_obj=kelas,
    defaults={
        'status': 'ACTIVE',
        'student_id_in_class': '001'
    }
)

if created:
    print(f"✓ {siswa.get_full_name()} ditambahkan ke {kelas.name}")
else:
    print(f"✗ {siswa.get_full_name()} sudah ada di {kelas.name}")
```

---

### **5. Ubah status enrollment**

```python
from academic.models import StudentEnrollment

enrollment = StudentEnrollment.objects.get(
    student__username='student1',
    class_obj__name='XI Teknik Mesin 1'
)

# Ubah status ke GRADUATED
enrollment.status = 'GRADUATED'
enrollment.save()

print(f"Status berhasil diubah ke: {enrollment.status}")
```

---

### **6. Hapus enrollment**

```python
from academic.models import StudentEnrollment

enrollment = StudentEnrollment.objects.get(
    student__username='student1',
    class_obj__name='XI Teknik Mesin 1'
)

enrollment.delete()
print("Enrollment dihapus")
```

---

## Admin Panel Mappings

### **Django Admin URL**

```
1. Lihat User:
   http://localhost:8000/admin/accounts/user/

2. Lihat Class:
   http://localhost:8000/admin/academic/class/

3. Lihat StudentEnrollment:
   http://localhost:8000/admin/academic/studentenrollment/

4. Tambah Enrollment:
   http://localhost:8000/admin/academic/studentenrollment/add/
```

---

## File-file yang Berhubungan

```
lms-smk/
├── accounts/
│   ├── models.py          ← Model User
│   └── admin.py           ← Admin User
│
├── academic/
│   ├── models.py          ← Model StudentEnrollment, Class
│   ├── admin.py           ← Admin StudentEnrollment
│   ├── forms.py           ← Form Enrollment
│   ├── views.py           ← View Enrollment
│   └── urls.py            ← URL Routing
│
└── CARA_BUAT_USER_SISWA.md      ← Cara membuat User
    CARA_ENROLL_SISWA.md         ← Cara Enroll ke Kelas
```

---

## Summary

| Aspek | Detail |
|-------|--------|
| **Model Utama** | StudentEnrollment |
| **Hubungan** | Student (User) + Class = Enrollment |
| **Admin Panel** | `/admin/academic/studentenrollment/` |
| **Status Default** | ACTIVE |
| **Unique Constraint** | (student_id, class_obj_id) |
| **Relasi Student** | ForeignKey ke User (role=STUDENT only) |
| **Relasi Class** | ForeignKey ke Class |

---

**📚 Dokumentasi Terkait:**
- CARA_BUAT_USER_SISWA.md
- CARA_ENROLL_SISWA.md