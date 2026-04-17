#!/usr/bin/env python
"""Debug script to test attendance views"""
import os
import django
import sys

# Force UTF-8 output on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

print("=" * 60)
print("TESTING ATTENDANCE VIEWS")
print("=" * 60)

# Test URLs
print("\n1. Testing URL reversals:")
try:
    url1 = reverse('attendance:events_calendar')
    print(f"[OK] attendance:events_calendar -> {url1}")
except Exception as e:
    print(f"[ERROR] attendance:events_calendar: {e}")

try:
    url2 = reverse('attendance:create_session')
    print(f"[OK] attendance:create_session -> {url2}")
except Exception as e:
    print(f"[ERROR] attendance:create_session: {e}")

try:
    url3 = reverse('attendance:student_history')
    print(f"[OK] attendance:student_history -> {url3}")
except Exception as e:
    print(f"[ERROR] attendance:student_history: {e}")

# Test views with client
print("\n2. Testing views as TEACHER:")
teacher = User.objects.filter(role='TEACHER').first()
if teacher:
    client = Client()
    client.force_login(teacher)

    # Test calendar
    print(f"\n  Testing /attendance/events/:")
    try:
        response = client.get('/attendance/events/')
        print(f"  Status: {response.status_code}")
        if response.status_code >= 400:
            print(f"  ERROR: {response.content[:300].decode('utf-8', errors='ignore')}")
    except Exception as e:
        print(f"  EXCEPTION: {type(e).__name__}: {e}")

    # Test create session
    print(f"\n  Testing /attendance/session/create/:")
    try:
        response = client.get('/attendance/session/create/')
        print(f"  Status: {response.status_code}")
        if response.status_code >= 400:
            print(f"  ERROR: {response.content[:300].decode('utf-8', errors='ignore')}")
    except Exception as e:
        print(f"  EXCEPTION: {type(e).__name__}: {e}")
else:
    print("No teacher user found!")

print("\n3. Testing views as STUDENT:")
student = User.objects.filter(role='STUDENT').first()
if student:
    client = Client()
    client.force_login(student)

    # Test calendar
    print(f"\n  Testing /attendance/events/:")
    try:
        response = client.get('/attendance/events/')
        print(f"  Status: {response.status_code}")
        if response.status_code >= 400:
            print(f"  ERROR: {response.content[:300].decode('utf-8', errors='ignore')}")
    except Exception as e:
        print(f"  EXCEPTION: {type(e).__name__}: {e}")
else:
    print("No student user found!")

print("\n" + "=" * 60)

