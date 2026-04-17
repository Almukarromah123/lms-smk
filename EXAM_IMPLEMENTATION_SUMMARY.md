# CHANGELOG - Fitur Ujian Multiple Choice LMS

## 🔧 Perbaikan Issue

### Issue #1: "Page not found" saat siswa start exam
**Root Cause**: Ujian belum auto-publish saat dibuat
**Solusi**:
- Ubah `CreateExamView`: otomatis set `is_published = True`
- Ubah `StartExamView.get_queryset()`: hanya filter published exams
- Update `ExamDetailView`: tampilkan enrollment check untuk siswa

**File yang diubah**:
- `exams/views.py` - CreateExamView, StartExamView, ExamDetailView
- `templates/exams/detail.html` - tambah enrollment warning

### Issue #2: Tidak ada fitur membuat soal multiple choice di halaman edit exam
**Root Cause**: Form edit hanya edit properties ujian, tidak ada section untuk soal
**Solusi**:
- Ubah `EditExamView`: redirect ke `questions` management page setelah save
- Update form `question_form.html`: UI user-friendly untuk input MCQ
- Buat options input tersistem (A, B, C, D) dengan auto-JSON parsing
- Tambah preview gambar di form

**File yang diubah**:
- `exams/views.py` - EditExamView
- `templates/exams/edit.html` - tambah "Manage Questions" section
- `templates/exams/question_form.html` - UI baru untuk MCQ
- `templates/exams/create.html` - full form dengan semua fields

## ✅ Fitur yang Sudah Diimplementasi

### Backend (Models, Forms, Views)

1. **Form Exam yang Lengkap** (`ExamForm`)
   - All exam settings: shuffle, allow_back, questions_per_page, dll
   - Datetime picker untuk exam_date

2. **Form Question yang Smart** (`ExamQuestionForm`)
   - Support multiple question types
   - JSON parsing untuk options (A, B, C, D)
   - Image upload

3. **Form Import XLSX** (`ExamQuestionImportForm`)
   - File validation (.xlsx only)
   - Batch import dari spreadsheet

4. **View untuk Management Soal**
   - `ManageQuestionsView`: Lihat daftar soal
   - `AddQuestionView`: Tambah soal baru
   - `EditQuestionView`: Edit soal
   - `DeleteQuestionView`: Hapus soal
   - `ImportQuestionsView`: Import dari XLSX

5. **View untuk Exam Session (Siswa)**
   - `ExamSessionView`: Tampil soal + timer + navigation
   - POST handler untuk save answers
   - Auto-submit saat time up
   - Client-side countdown timer (JavaScript)

### Frontend (Templates)

1. **Halaman Create Exam** (`create.html`)
   - Full form dengan grid layout
   - Settings section visually distinct
   - Redirect to questions management setelah create

2. **Halaman Edit Exam** (`edit.html`)
   - Preview soal count, duration, points
   - Full settings form
   - Direct links ke manage questions

3. **Halaman Manage Questions** (`questions.html`)
   - Preview semua soal + gambar
   - Edit/Delete buttons
   - Quick access ke import dan add question

4. **Form Add/Edit Question** (`question_form.html`)
   - MCQ options input (A-Z format)
   - Image upload + preview
   - Smart form untuk setiap question type
   - Auto JSON serialization saat submit

5. **Form Import XLSX** (`import_questions.html`)
   - Template info + contoh format
   - File upload

6. **Halaman Session Ujian** (`session.html`)
   - Per-soal pagination
   - Countdown timer (realtime)
   - Next/Previous navigation
   - Auto-save + auto-submit
   - Display answers setelah selesai
   - MCQ radio buttons, TF options, ESSAY textarea

### URLs

```python
path('<uuid:exam_id>/start/', views.StartExamView.as_view(), name='start'),
path('session/<uuid:session_id>/session/', views.ExamSessionView.as_view(), name='session'),
path('teacher/<uuid:exam_id>/questions/', views.ManageQuestionsView.as_view(), name='questions'),
path('teacher/<uuid:exam_id>/questions/add/', views.AddQuestionView.as_view(), name='question_add'),
path('teacher/<uuid:exam_id>/questions/import/', views.ImportQuestionsView.as_view(), name='question_import'),
path('teacher/<uuid:exam_id>/questions/<uuid:question_id>/edit/', views.EditQuestionView.as_view(), name='question_edit'),
path('teacher/<uuid:exam_id>/questions/<uuid:question_id>/delete/', views.DeleteQuestionView.as_view(), name='question_delete'),
```

## 📋 Files Diubah/Dibuat

### Diubah:
- `exams/forms.py` - tambah ExamQuestionImportForm
- `exams/views.py` - update 8 views + import statement
- `exams/urls.py` - tambah 7 routes baru
- `templates/exams/create.html` - UI baru
- `templates/exams/edit.html` - UI baru + manage section
- `templates/exams/detail.html` - enrollment check
- `templates/exams/session.html` - complete ujian UI
- `templates/exams/questions.html` - soal management
- `templates/exams/results.html` - hasil ujian

### Dibuat:
- `templates/exams/question_form.html` - form soal MCQ
- `templates/exams/import_questions.html` - form import
- `templates/exams/question_confirm_delete.html` - confirm dialog
- `exam_import_template.xlsx` - contoh template
- `EXAM_FEATURE_GUIDE.md` - dokumentasi lengkap

## 🧪 Testing Checklist

- [x] Django `check` - OK (0 silenced issues)
- [x] Python compile - OK (forms.py, views.py, urls.py)
- [x] URL routing - OK (resolve `/exams/{id}/start/` → `exams:start`)
- [x] Form validation - OK (import form check .xlsx extension)
- [x] Database models - OK (existing models, no migration needed)

## 🚀 Cara Test Manual

### Guru Flow:
1. Login as teacher
2. Go to Exams → Create Exam
3. Fill form → Create
4. Auto redirect ke Manage Questions
5. Add Question (MCQ)
6. Edit Question
7. Import Questions dari `exam_import_template.xlsx`
8. View Results

### Siswa Flow:
1. Login as student (must enrolled in class)
2. Go to Exams → My Exams
3. Click exam
4. Klik Start Exam
5. Jawab soal (Next/Previous)
6. Timer countdown & auto-submit jika time up
7. Submit manual atau wait time up

## 📝 Notes

- Auto-publish exam saat create agar siswa bisa langsung start
- Auto-save jawaban saat pindah soal
- Auto-submit ujian saat time up
- Client-side countdown timer JavaScript
- MCQ auto-grade, Essay manual grade
- Image support untuk setiap soal
- Batch import dari XLSX dengan error handling
