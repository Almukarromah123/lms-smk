from django import forms
from .models import AssignmentSubmission


class AssignmentSubmissionForm(forms.ModelForm):
    """Form untuk student submit assignment dengan file optional"""

    class Meta:
        model = AssignmentSubmission
        fields = ['submitted_file', 'submission_text']
        widgets = {
            'submitted_file': forms.FileInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg',
                'accept': '.pdf,.doc,.docx,.txt,.zip,.rar'
            }),
            'submission_text': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg',
                'rows': 6,
                'placeholder': 'Tulis jawaban atau penjelasan tugas Anda di sini...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make file field optional
        self.fields['submitted_file'].required = False
        self.fields['submitted_file'].help_text = 'Accepted formats: PDF, DOC, DOCX, TXT, ZIP, RAR'

        # Make text field optional too
        self.fields['submission_text'].required = False
        self.fields['submission_text'].label = 'Submission Text (Optional)'

    def clean(self):
        """Validate that at least one of the fields is filled"""
        cleaned_data = super().clean()
        submitted_file = cleaned_data.get('submitted_file')
        submission_text = cleaned_data.get('submission_text')

        if not submitted_file and not submission_text:
            raise forms.ValidationError(
                'Anda harus mengunggah file atau menulis teks. Setidaknya satu dari keduanya harus diisi!'
            )

        return cleaned_data
