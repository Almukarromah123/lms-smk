# Fix: IntegrityError saat Edit Exam Question

## Problem
Ketika guru mencoba edit exam question dan save, terjadi IntegrityError:
```
(1048, "Column 'options_data' cannot be null")
```

## Root Cause
Form `ExamQuestionForm` menerima `options_data` sebagai Textarea (string), tetapi:
1. Tidak ada validasi/cleaning untuk konversi JSON string → dict
2. Ketika field kosong atau tidak valid, NULL nilai dikirim ke database
3. Model field `options_data` adalah JSONField yang tidak membolehkan NULL

## Solution
Ditambahkan method di `ExamQuestionForm`:

### 1. `clean_options_data()` 
- Konversi JSON string dari textarea ke Python dict
- Handle empty values dengan return empty dict `{}`
- Validasi JSON format dengan error message yang jelas

### 2. `clean()`
- Validasi business logic: MCQ dan MATCHING harus memiliki options
- Prevent save jika question type membutuhkan options tapi kosong

## Files Modified
- `exams/forms.py` - Ditambahkan import json dan dua method validation

## Testing
Sudah ditest dengan scenarios:
- ✓ Edit question dengan text baru
- ✓ Edit question dengan tambah/ubah options
- ✓ Change question type dari MCQ ke ESSAY
- ✓ Form validation dengan invalid JSON
- ✓ Proper save ke database tanpa error

## Changelog
**2026-04-08**
- Added `clean_options_data()` method untuk handle JSON conversion
- Added `clean()` method untuk validasi question type requirements
- Lebih user-friendly error messages untuk invalid JSON
- Semua save operations sekarang terlindungi dari IntegrityError
