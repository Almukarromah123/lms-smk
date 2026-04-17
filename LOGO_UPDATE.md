# Logo Update - Media/School Logo Integration

## Summary
Mengganti semua logo hardcoded di templates dengan logo yang ada di folder `media/school_logo/logosmk.png`.

## What Changed

### 1. **Database Setup**
- Mengassociate file `logosmk.png` ke School model di database
- Field `School.logo` sekarang berisi path ke logo file

### 2. **Context Processor** 
- Created: `lms_project/context_processors.py`
- Adds `school` object to all template contexts
- Automatically fetches active school or first available school

### 3. **Settings Configuration**
- Updated: `lms_project/settings.py`
- Added `'lms_project.context_processors.school_context'` to TEMPLATES context_processors

### 4. **Template Updates**

#### `templates/base.html`
- Removed hardcoded graduation-cap icon
- Added `{% if school.logo %}` to display logo from database
- Fallback to icon if logo not available

#### `templates/accounts/login.html`
- Removed hardcoded graduation-cap icon
- Added `{% if school.logo %}` to display logo from database
- Fallback to icon if logo not available

## Files Modified
1. `lms_project/context_processors.py` - **Created**
2. `lms_project/settings.py` - Added context processor
3. `templates/base.html` - Updated logo display
4. `templates/accounts/login.html` - Updated logo display

## Result
✓ Logo sekarang ditampilkan di semua halaman (navbar, login page)
✓ Logo dimuat dari database School model
✓ Fallback ke icon jika logo tidak ada
✓ Semua logo references unified di satu tempat (database)

## Testing
- Logo akan muncul di navigasi bar di semua halaman
- Logo akan muncul di halaman login
- Jika ingin change logo, cukup update School.logo di admin panel

## Notes
- Logo di-reference via context processor, jadi tidak perlu update setiap template secara manual
- Semua routes otomatis punya akses ke `{{ school }}` context variable
