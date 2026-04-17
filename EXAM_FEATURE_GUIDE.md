# Panduan Fitur Ujian Multiple Choice - LMS SMK IT AL-MUKARROMAH

## Fitur Utama

### 1. Membuat Ujian Baru (Guru)

**Langkah:**
1. Klik **Exams** di sidebar → **Create Exam**
2. Isi form:
   - **Class**: Pilih kelas
   - **Subject**: Pilih mata pelajaran
   - **Title**: Nama ujian
   - **Description**: Deskripsi ujian
   - **Exam Date & Time**: Tanggal dan jam ujian
   - **Duration**: Durasi ujian (dalam menit)
   - **Total Points**: Nilai maksimal
   - **Questions Per Page**: Berapa soal per halaman (default 1)
   - **Settings**: Pengaturan soal (shuffle, answer key, dll)
3. Klik **Create Exam** → otomatis langsung ke halaman Manage Questions

### 2. Menambah Soal (Guru)

#### A. Menambah Soal Manual per-satu

**Langkah:**
1. Di halaman Manage Questions, klik **Add Question**
2. Isi form:
   - **Question Type**: Pilih tipe soal:
     - **MCQ**: Multiple Choice (Pilihan Ganda)
     - **TF**: True/False
     - **ESSAY**: Essay/Esai
     - **MATCHING**: Matching
   - **Question Text**: Pertanyaan
   - **Points**: Nilai soal (bisa desimal, misal 2.5)
   - **Image**: Upload gambar (opsional) untuk ilustrasi
   - **Options** (untuk MCQ): Isi pilihan A, B, C, D
   - **Correct Answer**: Jawaban benar (A/B/C/D untuk MCQ, True/False untuk TF)
   - **Explanation**: Penjelasan jawaban (opsional)
3. Klik **Save Question**

#### B. Impor Soal dari File .xlsx (Batch)

**Langkah:**
1. Di halaman Manage Questions, klik **Import .xlsx**
2. Download template `exam_import_template.xlsx` (contoh sudah tersedia di folder project)
3. Edit file Excel dengan struktur:

| question_type | question_text | points | options_data | correct_answer | explanation |
|---|---|---|---|---|---|
| MCQ | Apa warna bendera Indonesia? | 1 | {"A": "Merah", "B": "Putih", "C": "Biru"} | A | Bendera Indonesia adalah... |
| TF | Bumi bulat | 1 | | True | Ya, bumi berbentuk bulat |
| ESSAY | Jelaskan fotosintesis | 2 | | | - |

**Format options_data:**
- Gunakan JSON format: `{"A": "Teks opsi A", "B": "Teks opsi B", ...}`
- Kosongkan untuk tipe TF dan ESSAY

4. Upload file di form → **Import Questions**
5. Soal akan langsung ditambahkan ke ujian

### 3. Mengelola Soal (Guru)

**Di halaman Manage Questions:**
- **View soal**: Lihat daftar semua soal beserta gambar (jika ada)
- **Edit soal**: Klik tombol Edit untuk mengubah
- **Delete soal**: Klik tombol Delete untuk menghapus
- **Tambah gambar**: Edit soal → upload gambar

### 4. Mengerjakan Ujian (Siswa)

**Langkah:**
1. Klik **Exams** → **My Exams**
2. Klik ujian yang ingin dikerjakan
3. Klik **Start Exam** → ujian dimulai
4. **Fitur ujian:**
   - **Timer** di atas menunjukkan sisa waktu
   - **Per-soal per-halaman**: Satu soal di satu halaman (sesuai setting)
   - **Next/Previous**: Tombol navigasi soal
   - **Auto-save**: Jawaban disimpan otomatis saat berpindah soal
   - **Auto-submit**: Saat waktu habis, ujian otomatis dikumpulkan
5. **Submit Exam**: Klik tombol hijau untuk selesaikan ujian lebih awal
6. Setelah submit, lihat ringkasan jawaban (jika guru aktifkan display answer key)

### 5. Melihat Hasil Ujian (Guru)

**Langkah:**
1. Klik **Exams** → **My Exams** → Exam tertentu
2. Klik **Results**
3. Lihat tabel daftar siswa + skor mereka

## Setting & Opsi

### Opsi Soal
- **Shuffle Questions**: Acak urutan soal
- **Shuffle Options**: Acak urutan pilihan (untuk MCQ)
- **Allow Back to Previous**: Siswa bisa kembali ke soal sebelumnya
- **Display Answer Key**: Tampilkan kunci jawaban setelah selesai
- **Show Feedback**: Tampilkan penjelasan jawaban
- **Published**: Aktifkan agar siswa bisa mulai ujian

### Tipe Soal

| Tipe | Format | Contoh Kunci |
|---|---|---|
| MCQ | Pilihan ganda A-D | A |
| TF | True atau False | True |
| ESSAY | Teks panjang | (diisi manual oleh guru) |
| MATCHING | Mencocokkan | (belum di-implement) |

## System Behavior

- **Auto-publish**: Ujian otomatis di-publish saat dibuat
- **Auto-save**: Jawaban siswa disimpan saat berpindah soal
- **Auto-submit**: Ujian otomatis dikumpulkan saat waktu habis
- **Grading**: Soal MCQ & TF di-grade otomatis, ESSAY di-grade manual

## Template Import .xlsx

**Download:** `exam_import_template.xlsx` di folder project root

Struktur kolom (WAJIB ada):
1. `question_type` - MCQ, TF, ESSAY, MATCHING
2. `question_text` - Isi pertanyaan
3. `points` - Nilai soal (number)
4. `options_data` - JSON untuk opsi pilihan
5. `correct_answer` - Jawaban benar
6. `explanation` - Penjelasan (opsional)

**Tips:**
- Jangan ubah nama header
- Satu baris = satu soal
- Baris kosong akan dilewati
- options_data untuk ESSAY/TF bisa dikosongkan

## Troubleshooting

1. **"Page not found" saat start exam**
   - Pastikan Anda sudah terdaftar di kelas
   - Pastikan ujian sudah published (guru set Published = Yes)

2. **Soal tidak tampil saat mengerjakan**
   - Pastikan soal sudah ditambahkan di Manage Questions
   - Refresh halaman browser

3. **Jawaban tidak tersimpan**
   - Koneksi internet mungkin terputus
   - Coba pindah soal lagi (akan auto-save)

4. **Timer salah**
   - Server dan local time mungkin beda
   - Contact administrator

## Catatan Penting

- ⚠️ **Jangan close browser** saat mengerjakan ujian → jawaban mungkin tidak tersimpan
- ⚠️ **Tidak bisa edit soal** jika ujian sudah dimulai
- ⚠️ **Soal bergambar** harus di-upload saat edit soal (impor .xlsx tidak support gambar)
- ⚠️ **Hapus soal** tidak bisa diundo
