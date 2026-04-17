# SMK IT AL - MUKARROMAH Learning Management System

A comprehensive, modern LMS built with Django 4.2 and Tailwind CSS for vocational schools (SMK).

## 🚀 Quick Start

### Server Status
- **Django Development Server**: Running on `http://localhost:8000`
- **Admin Panel**: `http://localhost:8000/admin/`
- **Default Superuser**: admin (password needs to be set)

### Initial Setup

#### 1. Set Admin Password
```bash
python manage.py changepassword admin
```

#### 2. Create Test Users

**Teacher:**
```bash
python manage.py shell
```

```python
from accounts.models import User

teacher = User.objects.create_user(
    username='teacher1',
    email='teacher1@smkalimukarromah.sch.id',
    password='Teacher@123',
    first_name='Budi',
    last_name='Santoso',
    role='TEACHER',
    phone='081234567890'
)
print(f"Teacher created: {teacher}")
```

**Student:**
```python
student = User.objects.create_user(
    username='student1',
    email='student1@smkalimukarromah.sch.id',
    password='Student@123',
    first_name='Rina',
    last_name='Wijaya',
    role='STUDENT',
    phone='082345678901'
)
print(f"Student created: {student}")
```

### Access Points

| Role     | URL              | Username  | Dashboard              |
|----------|------------------|-----------|------------------------|
| Admin    | /accounts/login/ | admin     | /accounts/dashboard/admin/ |
| Teacher  | /accounts/login/ | teacher1  | /accounts/dashboard/teacher/ |
| Student  | /accounts/login/ | student1  | /accounts/dashboard/student/ |

---

## 📚 Project Features

### Implemented ✅
- **Authentication System**: Role-based access (Admin/Teacher/Student)
- **Dashboard**: Role-specific dashboards with stats and quick actions
- **Database Models**: Complete database schema with 9 apps
- **Admin Panel**: Fully registered Django admin with custom configs
- **UI/UX**: Modern Tailwind CSS design with gradients and animations
- **Responsive Design**: Mobile-friendly layout with hamburger menu
- **Floating WhatsApp Button**: Direct contact to admin

### Module Structure

#### 1. **Accounts** (Authentication & Users)
- Custom User model with roles
- User profiles with NIP/NIS
- Login/Logout with role-based routing
- User management in admin

#### 2. **Academic** (School Structure)
- School information
- Academic year management
- Classes (Grade grouping)
- Subjects
- Class-Subject-Teacher relationships
- Student enrollment system

#### 3. **Courses** (Learning Materials)
- Course management
- Module organization
- Lesson content (Video/PDF/Text)
- Lesson access tracking
- Course attachments

#### 4. **Assignments** (Task Management)
- Assignment creation by teachers
- Student submissions with files
- Automatic grading with feedback
- Assignment status tracking

#### 5. **Exams** (CBT - Computer Based Test)
- Online exam system
- Multiple question types (MCQ, True/False, Essay)
- Exam sessions with timer
- Auto-grading for objective questions
- Question shuffling & answer key display

#### 6. **Grades** (Assessment & Reporting)
- Grade book with weighted scoring
- Auto-calculated final grades
- Letter grade assignment (A-E)
- PDF report card generation with reportlab

#### 7. **Attendance** (Roll Call)
- Daily attendance marking
- Attendance status tracking (Present/Absent/Late/Excuse/Sick)
- Attendance summaries (Weekly/Monthly/Semester)
- Attendance percentage calculation

#### 8. **Payments** (Billing System)
- Bill types (SPP, exam fees, etc.)
- Student billing
- Payment record tracking
- Payment status management (Pending/Partial/Paid/Overdue)
- Receipt generation

#### 9. **Notifications** (In-app Alerts)
- User notifications
- Notification types (Assignment, Exam, Grade, Payment, etc.)
- Read/Unread tracking

---

## 🧪 Testing Workflow

### Complete Teacher-to-Student Workflow

#### Step 1: Create a Class
1. Login as **admin**
2. Go to Admin → Academic → Classes
3. Create a new class:
   - Name: "XI Teknik Mesin 1"
   - Grade: "XI"
   - Homeroom Teacher: (select teacher1)
   - Academic Year: 2024/2025

#### Step 2: add Subject and Assignment Setup
1. Admin → Subjects → Add Subject "Matematika"
2. Admin → Class Subject Teachers → Assign teacher1 to the class and subject

#### Step 3: Enroll Student
1. Admin → Student Enrollment
2. Create enrollment:
   - Student: student1
   - Class: XI Teknik Mesin 1
   - Status: ACTIVE

#### Step 4: Teacher Creates Assignment
1. Login as **teacher1**
2. Go to Dashboard → Create Assignment
3. Fill details:
   - Title: "Kuis Bab 1 - Persamaan Linear"
   - Description: "Kerjakan soal berikut..."
   - Due Date: Tomorrow at 23:59
   - Total Points: 100

#### Step 5: Student Submits Assignment
1. Login as **student1**
2. Go to Dashboard → Pending Assignments
3. Click assignment → Upload file or write text
4. Submit

#### Step 6: Teacher Grades
1. Login as **teacher1**
2. Go to Dashboard → Pending Grading (should show 1 pending)
3. Click submission → Give score (e.g., 85/100) and feedback
4. Submit grade

#### Step 7: Student Checks Grade
1. Login as **student1**
2. Go to Dashboard → Recent Grades
3. Should see the grade appear automatically

### Testing Exam System

#### Create an Exam
1. Teacher login → Go to Admin (or future "My Exams" page)
2. Create Exam:
   - Subject: Matematika
   - Class: XI Teknik Mesin 1
   - Title: "Midterm Exam"
   - Duration: 60 minutes
   - Total Points: 100

#### Add Questions
1. Add 5 MCQ questions with options
2. Set correct answers
3. Publish exam

#### Student Takes Exam
1. Student login → Dashboard → Upcoming Exams
2. Start exam → Answer questions
3. Timer counts down
4. Submit exam
5. Auto-grading calculates score for MCQs

---

## 📊 Database Schema Overview

```
User (Custom - with roles)
├── UserProfile

Academic Structure
├── School
├── AcademicYear
├── Subject
├── Class
├── ClassSubjectTeacher
└── StudentEnrollment

Learning Materials
├── Course
├── Module
├── Lesson
├── LessonAccess
└── CourseAttachment

Assessment
├── Assignment
├── AssignmentSubmission
├── AssignmentGrade
├── Exam
├── ExamQuestion
├── ExamSession
├── ExamAnswer
├── GradeBook
└── ReportCard

Operations
├── AttendanceRecord
├── AttendanceSummary
├── BillType
├── StudentBill
├── PaymentRecord
├── PaymentSchedule
└── Notification
```

---

## 🎨 UI/UX Features

### Design Elements
- **Gradients**: Blue-to-Indigo primary, Violet-to-Cyan secondary
- **Icons**: Font Awesome 6.4.0 for all icons
- **Typography**: Modern sans-serif with proper hierarchy
- **Color Palette**:
  - Primary: #2563eb (Blue)
  - Secondary: #4f46e5 (Indigo)
  - Success: #10b981 (Green)
  - Warning: #ef6534 (Orange)
  - Danger: #ef4444 (Red)

### Responsive Breakpoints
- Mobile: 0-640px (hidden sidebar, hamburger menu)
- Tablet: 641-1024px (compact sidebar)
- Desktop: 1024px+ (full sidebar)

### Interactive Elements
- Hover animations: scale(1.05), shadow changes
- Transition effects: 0.3s smooth transitions
- Floating WhatsApp button with pulse animation
- Mobile hamburger menu
- Auto-hiding alerts after 5 seconds

---

## 🔧 Configuration

### Admin Panel Customization
All models are registered in Django admin with:
- Custom list displays
- Autocomplete fields for faster entry
- Filterable lists
- Search functionality
- Readonly fields for audit trails
- Inline editing where appropriate

### File Uploads
- **Profile Pictures**: `media/profile_pictures/`
- **Course Materials**: `media/course_attachments/`
- **Lesson Videos**: `media/lesson_videos/`
- **Lesson PDFs**: `media/lesson_pdfs/`
- **Assignment Files**: `media/assignment_files/`
- **Student Work**: `media/student_work/`
- **Report Cards (PDF)**: `media/report_cards/`
- **School Logo**: `media/school_logo/`

---

## 📞 Support Information

**School**: SMK IT AL - MUKARROMAH
**Admin WhatsApp**: +62 898-7874-932
**Email**: info@smkalimukarromah.sch.id

---

## 🛠️ Technology Stack

- **Framework**: Django 4.2 (Python)
- **Database**: SQLite (development) / PostgreSQL (production-ready)
- **Frontend**: Tailwind CSS 3
- **Icons**: Font Awesome 6.4.0
- **PDF Generation**: ReportLab
- **Task Queue**: Celery (optional, for future email tasks)
- **Caching**: Redis (optional)

---

## 📝 Next Steps (To Complete)

### Phase 2: Course Management
- [ ] Create course listing views
- [ ] Module management interface
- [ ] Lesson viewer with video player
- [ ] PDF viewer integration

### Phase 3: Assignment System
- [ ] Assignment submission forms
- [ ] File upload handling
- [ ] Grading interface
- [ ] Feedback system

### Phase 4: Exam System
- [ ] Exam builder UI
- [ ] Question editor
- [ ] Exam session with timer
- [ ] Results display

### Phase 5: Additional Features
- [ ] Email notifications
- [ ] Attendance marking UI
- [ ] Grade report generation
- [ ] Payment tracking UI
- [ ] API endpoints (for mobile app)

---

## 🚀 Deployment Checklist

Before moving to production:
- [ ] Change SECRET_KEY in settings.py
- [ ] Set DEBUG = False
- [ ] Configure ALLOWED_HOSTS
- [ ] Set up PostgreSQL database
- [ ] Configure email backend (SMTP)
- [ ] Set up WhatsApp integration (Twilio)
- [ ] Configure Midtrans for payments
- [ ] Setup SSL certificates
- [ ] Configure static/media file serving (nginx/Apache)
- [ ] Setup celery for async tasks

---

## 📄 License

© 2024 SMK IT AL-MUKARROMAH. All rights reserved.

---

**Version**: 1.0 Beta
**Last Updated**: April 5, 2024
**Status**: Development Phase Complete, Testing Phase Active

---

## MySQL Setup

Project ini sekarang disiapkan untuk memakai MySQL lewat file `.env`.

Default konfigurasi lokal:

```env
DB_ENGINE=django.db.backends.mysql
DB_NAME=lms_smk
DB_USER=root
DB_PASSWORD=112233
DB_HOST=127.0.0.1
DB_PORT=3306
```

Langkah setup:

```bash
pip install -r requirements.txt
```

```sql
CREATE DATABASE lms_smk CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

```bash
python manage.py migrate
```

Jika ingin memindahkan data lama dari SQLite ke MySQL:

```bash
python manage.py dumpdata --exclude contenttypes --exclude auth.permission > data.json
python manage.py loaddata data.json
```

Menjalankan MySQL lokal project:

```powershell
.\start_mysql_local.ps1
.\stop_mysql_local.ps1
```
