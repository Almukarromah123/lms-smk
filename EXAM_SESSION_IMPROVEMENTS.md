# Perbaikan Session Ujian - Submission & Answer Display

## Perubahan yang Dilakukan

### 1. Submit Button di Akhir Soal Saja
**Sebelum:**
- Submit button ada di setiap page soal
- Siswa bisa submit lebih awal tanpa warning

**Sesudah:**
- Submit button hanya muncul di soal terakhir
- Tombol Next/Previous hilang saat di soal akhir
- Navigasi lebih jelas dan lebih sulit mistake

**Implementation:**
- `submit-btn` hidden by default (class="hidden")
- JavaScript show/hide button based on isLastPage
- NextBtn hidden saat di halaman terakhir

### 2. Confirmation Dialog Sebelum Submit
**Sebelum:**
- Klik submit langsung submit, tidak ada konfirmasi
- Siswa bisa accidentally submit sebelum siap

**Sesudah:**
- Muncul dialog: "Apakah Anda yakin ingin submit ujian? Anda tidak bisa mengubah jawaban setelah submit."
- Submit hanya jika user confirm dengan OK

**Implementation:**
- Event listener di submit button
- `confirm()` dialog sebelum form submit
- Jika confirm OK, tambah hidden input dan submit form

### 3. Display Jawaban yang Lebih Readable
**Sebelum:**
```
Jawaban siswa: {'04bda703-285f-4cf1-9132-ff035aebc578': 'C', 'fff7402c-4226-4b2f-8b1f-c39c68af61e2': 'A'}
```
(Raw JSON dict dengan UUID - tidak jelas)

**Sesudah:**
```
Jawaban Anda: C
(atau "Tidak dijawab" jika kosong)
```
Ditampilkan dalam box biru yang rapi di bawah setiap soal

**Implementation:**
- Custom template filter: `get_dict_value` di `exams/templatetags/exam_filters.py`
- Filter mengambil value dari dict menggunakan UUID key
- Display dalam blue box dengan styling lebih baik
- "Tidak dijawab" untuk jawaban kosong

## Files yang Diubah/Dibuat

### Diubah:
- `templates/exams/session.html`
  - Load custom filter: `{% load exam_filters %}`
  - Update button layout - submit button hidden
  - Update summary display - gunakan filter get_dict_value
  - Update JavaScript - handle button visibility & confirmation

### Dibuat:
- `exams/templatetags/__init__.py` - Package init
- `exams/templatetags/exam_filters.py` - Custom template filter

## Testing Hasil

```
✓ Django check: 0 silenced issues
✓ Template compile: session.html OK
✓ Template tag module: exam_filters.py OK
```

## Behavior Baru

1. **Navigasi Ujian**
   - Page 1-n: Lihat Previous/Next, tidak ada Submit
   - Page terakhir: Submit button muncul, Next button hilang

2. **Submit**
   - Klik "Submit Exam" → dialog confirma
   - Jika cancel (Batal) → ulang mengerjakan
   - Jika OK → form submit, ujian selesai

3. **Ringkasan Jawaban**
   - Soal 1: [pertanyaan] → Jawaban Anda: C
   - Soal 2: [pertanyaan] → Jawaban Anda: (Tidak dijawab)
   - Soal 3: [pertanyaan] → Jawaban Anda: Penjelasan lengkap untuk essay
   - Kunci Jawaban: [jika guru enable display_answer_key]
