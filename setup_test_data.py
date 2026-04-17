#!/usr/bin/env python
"""
Quick setup script to create test users and sample data
Run: python manage.py shell < setup_test_data.py
"""

from django.utils import timezone
from datetime import datetime, timedelta
from accounts.models import User
from academic.models import School, AcademicYear, Subject, Class, ClassSubjectTeacher, StudentEnrollment

# Create test users if they don't exist
print("🔧 Creating test users...")

# Admin
admin, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@smkalimukarromah.sch.id',
        'first_name': 'Kepala',
        'last_name': 'Sekolah',
        'role': 'ADMIN',
        'is_staff': True,
        'is_superuser': True,
    }
)
if created:
    admin.set_password('Admin@123')
    admin.save()
    print(f"✅ Admin user created: {admin.username}")
else:
    print(f"ℹ️ Admin user already exists: {admin.username}")

# Teacher
teacher, created = User.objects.get_or_create(
    username='teacher1',
    defaults={
        'email': 'teacher1@smkalimukarromah.sch.id',
        'first_name': 'Budi',
        'last_name': 'Santoso',
        'role': 'TEACHER',
        'phone': '081234567890',
    }
)
if created:
    teacher.set_password('Teacher@123')
    teacher.save()
    print(f"✅ Teacher user created: {teacher.username}")
else:
    print(f"ℹ️ Teacher user already exists: {teacher.username}")

# Student
student, created = User.objects.get_or_create(
    username='student1',
    defaults={
        'email': 'student1@smkalimukarromah.sch.id',
        'first_name': 'Rina',
        'last_name': 'Wijaya',
        'role': 'STUDENT',
        'phone': '082345678901',
    }
)
if created:
    student.set_password('Student@123')
    student.save()
    print(f"✅ Student user created: {student.username}")
else:
    print(f"ℹ️ Student user already exists: {student.username}")

print("\n🏫 Creating school and academic data...")

# School
school, created = School.objects.get_or_create(
    name='SMK IT AL - MUKARROMAH',
    defaults={
        'code': 'SMKIT-001',
        'address': 'Jl. Pendidikan No. 1, Jakarta',
        'city': 'Jakarta Timur',
        'province': 'DKI Jakarta',
        'postal_code': '12345',
        'phone': '021-1234567',
        'email': 'info@smkalimukarromah.sch.id',
        'principal_name': 'Drs. Kepala Sekolah',
    }
)
if created:
    print(f"✅ School created: {school.name}")
else:
    print(f"ℹ️ School already exists: {school.name}")

# Academic Year
current_year = datetime.now().year
academic_year, created = AcademicYear.objects.get_or_create(
    year_start=current_year,
    year_end=current_year + 1,
    defaults={
        'is_current': True,
        'start_date': datetime(current_year, 7, 1).date(),
        'end_date': datetime(current_year + 1, 6, 30).date(),
    }
)
if created:
    print(f"✅ Academic year created: {academic_year}")
else:
    print(f"ℹ️ Academic year already exists: {academic_year}")

# Subjects
subjects_data = [
    ('Matematika', 'MTK001'),
    ('Bahasa Indonesia', 'IND001'),
    ('Bahasa Inggris', 'ENG001'),
    ('Teknik Mesin', 'TM001'),
    ('Dasar Kompetensi Kejuruan', 'DKK001'),
]

print("\n📖 Creating subjects...")
for subject_name, subject_code in subjects_data:
    subject, created = Subject.objects.get_or_create(
        school=school,
        code=subject_code,
        defaults={'name': subject_name}
    )
    if created:
        print(f"✅ Subject created: {subject_name}")

# Class
class_obj, created = Class.objects.get_or_create(
    school=school,
    name='XI Teknik Mesin 1',
    academic_year=academic_year,
    defaults={
        'grade': 'XI',
        'homeroom_teacher': teacher,
        'max_students': 40,
        'room_number': '11A',
    }
)
if created:
    print(f"\n✅ Class created: {class_obj.name}")
else:
    print(f"ℹ️ Class already exists: {class_obj.name}")

# Assign teacher to subjects in the class
print("\n👨‍🏫 Assigning teacher to subjects...")
for subject in Subject.objects.filter(school=school):
    assignment, created = ClassSubjectTeacher.objects.get_or_create(
        class_obj=class_obj,
        subject=subject,
        teacher=teacher,
    )
    if created:
        print(f"✅ Assigned {subject.name} to {teacher.get_full_name()}")

# Enroll student
print("\n📚 Enrolling student...")
enrollment, created = StudentEnrollment.objects.get_or_create(
    student=student,
    class_obj=class_obj,
    defaults={
        'status': 'ACTIVE',
        'student_id_in_class': '001',
    }
)
if created:
    print(f"✅ Student enrolled: {student.get_full_name()} in {class_obj.name}")
else:
    print(f"ℹ️ Student already enrolled")

print("\n" + "="*60)
print("🎉 Setup complete!")
print("="*60)
print("\n📝 Test Credentials:")
print(f"  Admin:    username='admin'      password='Admin@123'")
print(f"  Teacher:  username='teacher1'   password='Teacher@123'")
print(f"  Student:  username='student1'   password='Student@123'")
print("\n🌐 Access URLs:")
print(f"  Login:    http://localhost:8000/accounts/login/")
print(f"  Admin:    http://localhost:8000/admin/")
print(f"  Dashboard:http://localhost:8000/accounts/dashboard/")
print("\n" + "="*60)
