#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_project.settings')
django.setup()

from accounts.models import User
from academic.models import School, AcademicYear, Class, Subject, ClassSubjectTeacher, StudentEnrollment
from django.utils import timezone
import datetime

print("="*50)
print("SETTING UP RAILWAY POSTGRESQL")
print("="*50)

# 1. Create superuser
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@test.com',
        password='Admin@123',
        role='ADMIN'
    )
    print("[OK] Superuser 'admin' created")
else:
    print("[SKIP] Superuser 'admin' exists")

# 2. Create teacher
if not User.objects.filter(username='teacher1').exists():
    User.objects.create_user(
        username='teacher1',
        email='teacher1@test.com',
        password='Teacher@123',
        role='TEACHER'
    )
    print("[OK] Teacher 'teacher1' created")
else:
    print("[SKIP] Teacher 'teacher1' exists")

# 3. Create student
if not User.objects.filter(username='student1').exists():
    User.objects.create_user(
        username='student1',
        email='student1@test.com',
        password='Student@123',
        role='STUDENT'
    )
    print("[OK] Student 'student1' created")
else:
    print("[SKIP] Student 'student1' exists")

# 4. Create school
school, created = School.objects.get_or_create(
    name='SMK IT AL - MUKARROMAH',
    defaults={
        'address': 'Jl. Ahmad Yani No. 123',
        'phone': '0812-3456-7890',
    }
)
print(f"[{'OK' if created else 'SKIP'}] School: {school.name}")

# 5. Create academic year
try:
    year = AcademicYear.objects.create(
        year_start=2024,
        year_end=2025,
        start_date=datetime.date(2024, 7, 1),
        end_date=datetime.date(2025, 6, 30),
        is_current=True
    )
    print(f"[OK] Academic Year created: {year}")
except:
    year = AcademicYear.objects.get(year_start=2024, year_end=2025)
    print(f"[SKIP] Academic Year exists: {year}")

# 6. Create subjects
subjects_data = [
    ('Matematika', 'MTK'),
    ('Bahasa Indonesia', 'BI'),
    ('Bahasa Inggris', 'BIng'),
    ('Teknik Mesin', 'TM'),
    ('Sistem Informasi', 'SI'),
]

for name, code in subjects_data:
    subject, created = Subject.objects.get_or_create(
        code=code,
        defaults={'name': name, 'school': school}
    )
    if created:
        print(f"[OK] Subject: {name}")

# 7. Create class
class_obj, created = Class.objects.get_or_create(
    name='XI Teknik Mesin 1',
    academic_year=year,
    defaults={'school': school}
)
print(f"[{'OK' if created else 'SKIP'}] Class: {class_obj.name}")

# 8. Assign teacher to subjects
teacher = User.objects.get(username='teacher1')
for subject in Subject.objects.filter(school=school):
    cst, created = ClassSubjectTeacher.objects.get_or_create(
        class_obj=class_obj,
        subject=subject,
        teacher=teacher
    )

print(f"[OK] Teacher assigned to all subjects")

# 9. Enroll student
student = User.objects.get(username='student1')
enrollment, created = StudentEnrollment.objects.get_or_create(
    student=student,
    class_obj=class_obj,
    defaults={'status': 'ACTIVE'}
)
print(f"[{'OK' if created else 'SKIP'}] Student enrolled in class")

print("\n" + "="*50)
print("SETUP COMPLETE!")
print("="*50)
print("\nTest Credentials:")
print("   Admin:    admin / Admin@123")
print("   Teacher:  teacher1 / Teacher@123")
print("   Student:  student1 / Student@123")
print("\nAccess URLs:")
print("   Login:  http://localhost:8000/accounts/login/")
print("   Admin:  http://localhost:8000/admin/")
print("="*50)
