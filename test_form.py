#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_project.settings')
django.setup()

from attendance.forms import AttendanceSessionForm
from accounts.models import User
from datetime import date

# Get a teacher
teacher = User.objects.filter(role='TEACHER').first()

if teacher:
    print(f"Testing form with teacher: {teacher.get_full_name()}")

    # Create form for teacher
    form = AttendanceSessionForm(teacher=teacher)

    print(f"\nForm fields: {list(form.fields.keys())}")
    print(f"\nSession Type choices: {form.fields['session_type'].choices}")
    print(f"\nSession Type initial: {form.fields['session_type'].initial}")

    # Test with data
    class_obj = form.fields['class_obj'].queryset.first()
    subject = form.fields['subject'].queryset.first()

    if class_obj and subject:
        test_data = {
            'class_obj': class_obj.id,
            'subject': subject.id,
            'session_date': date.today(),
            'session_type': 'LURING',
            'description': 'Test Session'
        }

        form = AttendanceSessionForm(data=test_data, teacher=teacher)

        if form.is_valid():
            print("\n[OK] Form is valid!")
            print(f"Cleaned data: {form.cleaned_data}")
        else:
            print(f"\n[ERROR] Form errors: {form.errors}")
    else:
        print("\nNo class or subject found for teacher")
else:
    print("No teacher found")
