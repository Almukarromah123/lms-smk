## Fitur Proteksi Ujian (Exam Proctoring)

### ✅ Status
Sistem proteksi ujian sudah diimplementasikan dan siap digunakan.

---

## 📋 Fitur-Fitur Proteksi

### 1. **Deteksi Perubahan Tab/Window** 🔄
- **Aktivitas**: Sistem mendeteksi ketika siswa membuka tab lain atau meminimalkan window
- **Tindakan**: 
  - Menampilkan peringatan real-time
  - Menghitung jumlah tab switch
  - Membatasi maksimal 3 kali tab switch
  - Membatalkan ujian jika melampaui batas
- **Log**: Dicatat sebagai `tab_switch` violation

### 2. **Blokir Copy-Paste** 📋❌
- **Aktivitas**: Mencegah siswa melakukan copy (Ctrl+C), cut (Ctrl+X), dan paste (Ctrl+V)
- **Tindakan**: 
  - Menampilkan warning jika ada percobaan copy-paste
  - Mencegah aksi tersebut berhasil
- **Log**: Dicatat sebagai `attempt_copy`, `attempt_cut`, `attempt_paste` violations

### 3. **Blokir Right-Click** 🖱️❌
- **Aktivitas**: Menonaktifkan context menu saat user klik kanan pada soal
- **Tindakan**: 
  - Menutup context menu
  - Menampilkan peringatan
- **Log**: Dicatat sebagai `right_click` violation

### 4. **Deteksi Developer Tools** 🛠️❌
- **Metode Deteksi**: 
  - Shortcut: F12, Ctrl+Shift+I, Ctrl+Shift+C, Ctrl+Shift+J, Ctrl+Shift+K
  - Window size change detection
- **Tindakan**: 
  - Menonaktifkan shortcut developer tools
  - Menampilkan peringatan kritis
- **Log**: Dicatat sebagai `dev_tools_detected` violation

### 5. **Blokir Keyboard Shortcuts** ⌨️❌
- **Shortcut yang Diblokir**:
  - Ctrl+S (Save)
  - Ctrl+P (Print)
  - Ctrl+A (Select All)
  - Print Screen
- **Log**: Dicatat sebagai `shortcut_*` violations

### 6. **Proteksi Keluar Halaman** 🚪
- **Aktivitas**: Mencegah siswa meninggalkan halaman ujian
- **Tindakan**: 
  - Menampilkan konfirmasi saat user klik link
  - Menampilkan browser warning saat refresh/close
- **Log**: Dicatat sebagai `page_unload`, `window_blur`, `attempted_navigation` violations

### 7. **Mode Fullscreen** 🖥️
- **Aktivitas**: Menyarankan siswa untuk masuk ke mode fullscreen
- **Waktu**: Pop-up muncul 2 detik setelah halaman dimuat
- **Tujuan**: Menyembunyikan toolbar browser agar fokus pada ujian
- **Log**: Dicatat jika siswa keluar dari fullscreen

### 8. **Monitor Inaktivitas** ⏱️
- **Aktivitas**: Mendeteksi jika siswa tidak aktif lebih dari 5 menit
- **Tindakan**: Menampilkan warning untuk kembali aktif
- **Log**: Dicatat sebagai `inactivity_warning` violation

### 9. **Logging Violations** 📝
- **Data yang Tercatat**:
  - Tipe pelanggaran
  - Waktu pelanggaran (timestamp)
  - Jumlah tab switch saat pelanggaran terjadi
- **Lokasi**: Disimpan di field `violations_log` di database ExamSession
- **Pengiriman**: Via API endpoint `/exams/api/log-violation/`

---

## 🎨 UI/UX Features

### Warning Banner
```
🔒 Ujian Terlindungi
Sistem monitoring aktif: Membuka tab lain, menggunakan developer tools, 
atau meninggalkan halaman akan mencatat sebagai pelanggaran.
```

### Real-Time Notifications
- **Info** (Biru): Informasi sistem, contoh "Back to exam window"
- **Warning** (Kuning): Peringatan, contoh "Inactivity warning"
- **Error** (Merah): Pelanggaran, contoh "Tab Switch Detected!"
- **Critical** (Merah Gelap): Pelanggaran berat, contoh "UJIAN DIBATALKAN"

---

## 📊 Database Schema

### ExamSession Model (Update)
```python
violations_log = models.JSONField(default=list, blank=True)
# Format: [{type, timestamp, tab_switches}, ...]

# Contoh:
[
    {
        "type": "tab_switch",
        "timestamp": "{\"iso\": \"2026-04-17T...\", \"timestamp\": \"2026-04-17 ...\"}",
        "tab_switches": 1
    },
    {
        "type": "right_click",
        "timestamp": "{\"iso\": \"2026-04-17T...\", \"timestamp\": \"2026-04-17 ...\"}",
        "tab_switches": 1
    }
]
```

---

## 🔌 API Endpoints

### POST `/exams/api/log-violation/`
**Request Body**:
```json
{
    "session_id": "uuid-here",
    "violation_type": "tab_switch",
    "tab_switches": 1
}
```

**Response**:
```json
{
    "status": "success",
    "message": "Violation logged",
    "violation_count": 3
}
```

---

## 📁 File-File yang Ditambahkan/Dimodifikasi

### Ditambahkan:
- `static/js/exam-proctor.js` - Script utama proteksi ujian

### Dimodifikasi:
- `templates/exams/session.html` - Tambah warning banner, init proctoring
- `exams/views.py` - Tambah `log_violation_api()` endpoint
- `exams/urls.py` - Tambah URL routing untuk API
- `exams/models.py` - Tambah `violations_log` field ke ExamSession

### Migrasi:
- `exams/migrations/0010_examsession_violations_log_and_more.py`

---

## ⚙️ Konfigurasi

Edit file `static/js/exam-proctor.js` untuk mengubah konfigurasi:

```javascript
config: {
    enableFullscreen: true,           // Enable/disable fullscreen prompt
    enableDevToolDetection: true,     // Enable/disable dev tools detection
    enableCopyPasteBlock: true,       // Enable/disable copy-paste blocking
    enableRightClickBlock: true,      // Enable/disable right-click blocking
    enableTabSwitchDetection: true,   // Enable/disable tab switch detection
    enableWarnings: true,             // Enable/disable warnings
    maxTabSwitches: 3,                // Maximum allowed tab switches
    warningMessage: '⚠️ Peringatan: ...',
    tabSwitchWarning: 'Anda sudah membuka tab lain...'
}
```

---

## 🔒 Keamanan Catatan

### Keamahan Client-Side Protection
- ⚠️ Proteksi ini berjalan di client-side JavaScript
- ⚠️ Pengguna yang mahir dapat menemukan cara untuk bypass
- ✅ Direkomendasikan untuk exam dengan monitoring lebih ketat

### Rekomendasi Tambahan
1. **Server-Side Validation**: Cek timestamp submission vs waktu exam
2. **Activity Monitoring**: Log setiap submit jawaban dengan timestamp
3. **Video Proctoring**: Pertimbangkan untuk exam penting dengan software pihak ketiga
4. **Network Monitoring**: Monitor browser requests untuk deteksi anomali
5. **Admin Review**: Admin dapat review violations_log di database

---

## 🧪 Testing

### Test Scenarios
```
1. Tab Switch Detection
   - Buka exam di tab 1, switch ke tab 2 → Warning muncul
   - Ulangi 3x → Exam dibatalkan

2. Copy-Paste Blocking
   - Coba Ctrl+C di soal → "Copy-Paste dilarang" warning
   - Aksi copy gagal

3. Developer Tools
   - Tekan F12 → Tertutup, warning muncul
   - Tekan Ctrl+Shift+I → Sama seperti di atas

4. Right-Click Blocking
   - Klik kanan di soal → Context menu tidak muncul
   - Warning ditampilkan

5. Page Unload
   - Coba close tab → Browser warning "Yakin ingin keluar?"
   - Coba click link → Konfirmasi dialog

6. Violations Log
   - Check database ExamSession.violations_log setelah exam
   - Lihat semua pelanggaran yang tercatat
```

---

## 📖 How It Works

### Initialization Flow
```
1. User masuk halaman exam (session.html)
2. JavaScript load exam-proctor.js
3. ExamProctor.init('session_id') dipanggil
4. Setup semua proteksi (tab detection, copy-paste block, etc)
5. Fullscreen prompt muncul setelah 2 detik
6. Monitoring berjalan selama exam berlangsung
7. Violation terkirim ke API setiap kali terjadi
8. Student submit → Violations log disimpan di database
```

### Violation Detection
```
User Action → Detect → Log Violation → API Send → Database Save → Check Count
    ↓
Tab Switch → visibilitychange event → log_violation API → DB update → Check 3x limit
Right Click → contextmenu event → log_violation API → DB update
Copy → copy event → log_violation API → DB update
Dev Tools → F12/Ctrl+Shift+I → keydown event → log_violation API → DB update
```

---

## 💡 Tips untuk Admin

### Monitor Violations
```python
# Di Django shell
from exams.models import ExamSession

# Lihat semua violations
session = ExamSession.objects.get(id='session-id')
print(session.violations_log)

# Filter sessions dengan violations
sessions_with_violations = ExamSession.objects.filter(
    violations_log__0__isnull=False
).count()

# Lihat total tab switches
for session in ExamSession.objects.all():
    if session.violations_log:
        max_switches = max(v.get('tab_switches', 0) for v in session.violations_log)
        print(f"{session.student}: {max_switches} tab switches")
```

### Export Violations Report
Pertimbangkan untuk menambahkan:
1. Export violations ke CSV/Excel
2. Dashboard untuk monitoring real-time
3. Alert notification untuk pelanggaran berat
4. Statistical analysis (siswa mana yang sering cheat)

---

## ✅ Checklist Deployment

- [x] Code implemented
- [x] Database migration created & applied
- [x] System check passed
- [x] URLs configured
- [x] API endpoint ready
- [ ] Admin dashboard for violations (optional)
- [ ] Email notification for violations (optional)
- [ ] External proctoring integration (future)

---

**Status**: ✅ Ready for Production
**Version**: 1.0
**Last Updated**: 2026-04-17
