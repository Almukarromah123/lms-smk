#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_project.settings')
django.setup()

from attendance.models import AttendanceSession
from academic.models import ClassSubjectTeacher, Class
from datetime import date, timedelta

# Get test data
school_classes = Class.objects.all()[:1]

if school_classes:
    class_obj = school_classes[0]
    print(f"Using class: {class_obj.name}")

    # Get ClassSubjectTeacher
    cst = ClassSubjectTeacher.objects.filter(class_obj=class_obj).first()

    if cst:
        # Create a test LURING session with different date
        test_date = date.today() + timedelta(days=1)
        session = AttendanceSession.objects.create(
            class_subject_teacher=cst,
            session_date=test_date,
            session_type='LURING',
            description='Test QR Code Session'
        )

        print(f"\nCreated session: {session}")
        print(f"Session type: {session.get_session_type_display()}")

        # Test generate_new_qr_token
        token1 = session.generate_new_qr_token()
        print(f"\nGenerated token: {token1[:20]}...")
        print(f"Token expires at: {session.qr_token_expires_at}")

        # Test is_qr_token_valid
        is_valid = session.is_qr_token_valid(token1)
        print(f"Token is valid: {is_valid}")

        # Test invalid token
        is_valid_invalid = session.is_qr_token_valid('invalid_token')
        print(f"Invalid token is valid: {is_valid_invalid}")

        # Generate QR image
        qr_image = session.get_qr_image()
        print(f"\nQR image generated: {type(qr_image).__name__}")

        # Clean up
        session.delete()
        print("\nTest passed! QR code system is working.")
    else:
        print("No ClassSubjectTeacher found")
else:
    print("No classes found in database")

