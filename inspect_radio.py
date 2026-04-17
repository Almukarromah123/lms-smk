import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_project.settings')
import django
django.setup()
from attendance.forms import AttendanceSessionForm
form = AttendanceSessionForm()
print('field type:', type(form['session_type']))
print('field name:', form['session_type'].name)
print('field value:', form['session_type'].value())
for i, radio in enumerate(form['session_type'], start=1):
    print('--- option', i)
    print('repr:', repr(radio))
    print('choice_value:', getattr(radio, 'choice_value', None))
    print('choice_label:', getattr(radio, 'choice_label', None))
    print('data:', getattr(radio, 'data', None))
    print('value:', getattr(radio, 'value', None))
    print('type:', type(radio))
