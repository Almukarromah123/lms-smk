from django import forms
from django.forms import DateTimeInput
from .models import Exam, ExamQuestion
import json


class ExamForm(forms.ModelForm):
    """Form untuk membuat/edit exam dengan datetime picker"""

    class Meta:
        model = Exam
        fields = ['subject', 'class_obj', 'title', 'description', 'exam_date',
                  'duration_minutes', 'total_points', 'shuffle_questions',
                  'shuffle_options', 'allow_back', 'question_per_page',
                  'display_answer_key', 'show_feedback']

        widgets = {
            'subject': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'
            }),
            'class_obj': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'
            }),
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg',
                'placeholder': 'Nama Ujian'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg',
                'rows': 3,
                'placeholder': 'Deskripsi ujian'
            }),
            'exam_date': DateTimeInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg',
                'type': 'datetime-local'
            }),
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg',
                'min': '1'
            }),
            'total_points': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg',
                'min': '1'
            }),
            'question_per_page': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg',
                'min': '1'
            }),
            'shuffle_questions': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4'
            }),
            'shuffle_options': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4'
            }),
            'allow_back': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4'
            }),
            'display_answer_key': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4'
            }),
            'show_feedback': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4'
            }),
        }


class ExamQuestionForm(forms.ModelForm):
    """Form untuk menambah soal exam dengan berbagai tipe"""

    class Meta:
        model = ExamQuestion
        fields = ['question_type', 'question_text', 'points', 'options_data',
                  'correct_answer', 'image', 'options_images', 'explanation']

        widgets = {
            'question_type': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'
            }),
            'question_text': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg',
                'rows': 3,
                'placeholder': 'Masukkan pertanyaan ujian'
            }),
            'points': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg',
                'min': '0',
                'step': '0.5'
            }),
            'options_data': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg',
                'rows': 4,
                'placeholder': '{"A": "Opsi A", "B": "Opsi B", "C": "Opsi C", "D": "Opsi D"}'
            }),
            'correct_answer': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg',
                'placeholder': 'Jawaban yang benar (misal: A)'
            }),
            'image': forms.FileInput(attrs={
                'class': 'w-full',
                'accept': 'image/*'
            }),
            'options_images': forms.HiddenInput(),
            'explanation': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg',
                'rows': 3,
                'placeholder': 'Penjelasan untuk jawaban yang benar (opsional)'
            }),
        }

    def clean_options_data(self):
        """Convert JSON string to dict, handle empty values"""
        options_data = self.cleaned_data.get('options_data')
        question_type = self.cleaned_data.get('question_type')
        
        # If options_data is empty or not provided
        if not options_data or (isinstance(options_data, str) and not options_data.strip()):
            # Return empty dict - validation untuk MCQ/MATCHING akan dilakukan di clean()
            return {}
        
        # If it's already a dict (dari instance yang ada), return as is
        if isinstance(options_data, dict):
            return options_data
        
        # Try to parse JSON string
        try:
            parsed = json.loads(options_data)
            if not isinstance(parsed, dict):
                raise forms.ValidationError(
                    'Options harus berupa JSON object (dictionary) dengan format: {"A": "Opsi A", "B": "Opsi B"}'
                )
            return parsed
        except json.JSONDecodeError as e:
            raise forms.ValidationError(
                f'Format JSON tidak valid. Gunakan format: {{"A": "Opsi A", "B": "Opsi B"}}. Error: {str(e)}'
            )

    def clean(self):
        """Additional validation"""
        cleaned_data = super().clean()
        question_type = cleaned_data.get('question_type')
        options_data = cleaned_data.get('options_data')
        
        # MCQ dan MATCHING harus memiliki options
        if question_type in ['MCQ', 'MATCHING'] and not options_data:
            raise forms.ValidationError(f'{question_type} harus memiliki options')
        
        return cleaned_data


class ExamQuestionImportForm(forms.Form):
    """Form untuk mengimpor soal ujian dari file XLSX"""

    xlsx_file = forms.FileField(
        label='Pilih file .xlsx',
        help_text='Gunakan template import yang berisi kolom question_type, question_text, points, options_data, correct_answer, explanation.',
        widget=forms.ClearableFileInput(attrs={
            'class': 'w-full',
            'accept': '.xlsx'
        })
    )

    def clean_xlsx_file(self):
        xlsx_file = self.cleaned_data.get('xlsx_file')
        if xlsx_file and not xlsx_file.name.lower().endswith('.xlsx'):
            raise forms.ValidationError('File harus berformat .xlsx')
        return xlsx_file
