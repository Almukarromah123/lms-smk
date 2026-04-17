from django.shortcuts import render
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import GradeBook, ReportCard


class StudentGradesView(LoginRequiredMixin, ListView):
    """View student's grades"""
    template_name = 'grades/my_grades.html'
    context_object_name = 'grades'
    paginate_by = 20

    def get_queryset(self):
        return GradeBook.objects.filter(student=self.request.user).order_by('-academic_year__year_start')


class ReportCardView(LoginRequiredMixin, ListView):
    """View student's report cards"""
    template_name = 'grades/report_card.html'
    context_object_name = 'report_cards'

    def get_queryset(self):
        return ReportCard.objects.filter(student=self.request.user).order_by('-academic_year__year_start')


class TeacherGradebookView(LoginRequiredMixin, ListView):
    """List teacher's gradebooks"""
    template_name = 'grades/gradebook_list.html'
    context_object_name = 'gradebooks'

    def get_queryset(self):
        # Get classes taught by teacher
        from academic.models import ClassSubjectTeacher
        classes = ClassSubjectTeacher.objects.filter(
            teacher=self.request.user
        ).values_list('class_obj', flat=True).distinct()

        return GradeBook.objects.filter(class_obj__in=classes).order_by('-academic_year__year_start')


class ClassGradebookView(LoginRequiredMixin, ListView):
    """View gradebook for a specific class"""
    template_name = 'grades/class_gradebook.html'
    context_object_name = 'grades'
    paginate_by = 50

    def get_queryset(self):
        class_id = self.kwargs['class_id']
        return GradeBook.objects.filter(class_obj__id=class_id).order_by('student__last_name')
