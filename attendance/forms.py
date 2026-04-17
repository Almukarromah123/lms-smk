from django import forms
from .models import AttendanceSession, AttendanceRecord
from academic.models import Class, Subject, ClassSubjectTeacher


class AttendanceSessionForm(forms.ModelForm):
    """Form untuk teacher membuat attendance session per subject"""
    class_obj = forms.ModelChoiceField(
        queryset=Class.objects.none(),
        label='Select Class',
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:border-blue-500',
            'id': 'id_class_obj'
        })
    )

    subject = forms.ModelChoiceField(
        queryset=Subject.objects.none(),
        label='Select Subject',
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:border-blue-500',
            'id': 'id_subject'
        })
    )

    session_type = forms.ChoiceField(
        label='Session Type',
        choices=AttendanceSession.SESSION_TYPE_CHOICES,
        initial='LURING',
        widget=forms.RadioSelect(attrs={
            'class': 'mr-3'
        }),
        help_text='LURING: In-person with QR code scanning, DARING: Online with student submission'
    )

    class Meta:
        model = AttendanceSession
        fields = ['session_date', 'session_type', 'description']
        widgets = {
            'session_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:border-blue-500'
            }),
            'description': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:border-blue-500',
                'placeholder': 'e.g., Morning Attendance, Afternoon Class'
            }),
        }

    def __init__(self, *args, teacher=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter classes to only those taught by the teacher
        if teacher:
            self.fields['class_obj'].queryset = Class.objects.filter(
                subject_teachers__teacher=teacher
            ).distinct()

            # Populate subject field with all subjects the teacher teaches
            self.fields['subject'].queryset = Subject.objects.filter(
                classsubjectteacher__teacher=teacher
            ).distinct().order_by('name')
        else:
            self.fields['class_obj'].queryset = Class.objects.none()
            self.fields['subject'].queryset = Subject.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        class_obj = cleaned_data.get('class_obj')
        subject = cleaned_data.get('subject')

        if class_obj and subject:
            # Validate that this class-subject combination exists
            if not ClassSubjectTeacher.objects.filter(
                class_obj=class_obj,
                subject=subject
            ).exists():
                raise forms.ValidationError(
                    "This subject is not taught in this class."
                )

        return cleaned_data



class BulkAttendanceMarkForm(forms.Form):
    """Dynamic form untuk teacher mark attendance secara bulk"""

    def __init__(self, enrollment_queryset, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Dynamically add field untuk setiap student
        for enrollment in enrollment_queryset:
            student = enrollment.student
            field_name = f'student_{enrollment.id}'

            self.fields[field_name] = forms.ChoiceField(
                label=f"{student.get_full_name()} ({enrollment.student_id_in_class or 'N/A'})",
                choices=[
                    ('PRESENT', 'Present'),
                    ('ABSENT', 'Absent'),
                    ('SICK', 'Sick'),
                    ('PERMISSION', 'Permission'),
                ],
                initial='PRESENT',
                widget=forms.RadioSelect(attrs={
                    'class': 'mr-2'
                })
            )

            # Arrival time field (optional)
            arrival_field_name = f'arrival_{enrollment.id}'
            self.fields[arrival_field_name] = forms.TimeField(
                label=f"Arrival Time for {student.get_full_name()}",
                required=False,
                widget=forms.TimeInput(attrs={
                    'type': 'time',
                    'class': 'px-3 py-1 rounded border border-gray-300 text-sm'
                })
            )


class StudentAttendanceSubmitForm(forms.ModelForm):
    """Form untuk student submit attendance confirmation"""

    status = forms.ChoiceField(
        choices=[
            ('PRESENT', 'Present'),
            ('ABSENT', 'Absent'),
            ('SICK', 'Sick'),
            ('PERMISSION', 'Permission'),
        ],
        widget=forms.RadioSelect(attrs={
            'class': 'mr-3 space-y-2'
        }),
        label='Mark Your Attendance'
    )

    class Meta:
        model = AttendanceRecord
        fields = ['status', 'arrival_time']
        widgets = {
            'arrival_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:border-blue-500',
            }),
        }
        labels = {
            'arrival_time': 'Arrival Time (Optional)',
        }
