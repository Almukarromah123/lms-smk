from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Assignment, AssignmentSubmission, AssignmentGrade
from .forms import AssignmentSubmissionForm


class StudentAssignmentListView(LoginRequiredMixin, ListView):
    """List assignments for student"""
    template_name = 'assignments/student_list.html'
    context_object_name = 'assignments'
    paginate_by = 20

    def get_queryset(self):
        return Assignment.objects.all().order_by('-due_date')


class AssignmentDetailView(LoginRequiredMixin, DetailView):
    """View assignment details"""
    model = Assignment
    template_name = 'assignments/detail.html'
    context_object_name = 'assignment'
    pk_url_kwarg = 'assignment_id'


class SubmitAssignmentView(LoginRequiredMixin, UpdateView):
    """Submit or update assignment submission"""
    model = AssignmentSubmission
    form_class = AssignmentSubmissionForm
    template_name = 'assignments/submit.html'

    def get_object(self):
        """Get or create assignment submission for current student and assignment"""
        assignment_id = self.kwargs['assignment_id']
        submission, _ = AssignmentSubmission.objects.get_or_create(
            assignment_id=assignment_id,
            student=self.request.user
        )
        return submission

    def form_valid(self, form):
        form.instance.mark_as_submitted()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assignment'] = Assignment.objects.get(id=self.kwargs['assignment_id'])
        return context

    def get_success_url(self):
        return reverse_lazy('assignments:student_list')


class TeacherAssignmentListView(LoginRequiredMixin, ListView):
    """List assignments created by teacher"""
    template_name = 'assignments/teacher_list.html'
    context_object_name = 'assignments'
    paginate_by = 20

    def get_queryset(self):
        return Assignment.objects.filter(teacher=self.request.user).order_by('-created_date')


class CreateAssignmentView(LoginRequiredMixin, CreateView):
    """Create new assignment"""
    model = Assignment
    template_name = 'assignments/create.html'
    fields = ['class_obj', 'subject', 'title', 'description', 'instructions', 'due_date', 'total_points', 'attachment']

    def form_valid(self, form):
        form.instance.teacher = self.request.user
        return super().form_valid(form)


class EditAssignmentView(LoginRequiredMixin, UpdateView):
    """Edit assignment"""
    model = Assignment
    template_name = 'assignments/edit.html'
    fields = ['title', 'description', 'instructions', 'due_date', 'total_points', 'attachment']
    pk_url_kwarg = 'assignment_id'


class DeleteAssignmentView(LoginRequiredMixin, DeleteView):
    """Delete assignment"""
    model = Assignment
    template_name = 'assignments/delete_confirm.html'
    pk_url_kwarg = 'assignment_id'
    success_url = reverse_lazy('assignments:teacher_list')

    def get_queryset(self):
        """Only allow teacher to delete own assignments"""
        return Assignment.objects.filter(teacher=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Assignment berhasil dihapus!')
        return super().delete(request, *args, **kwargs)


class ViewSubmissionsView(LoginRequiredMixin, ListView):
    """View all submissions for an assignment"""
    template_name = 'assignments/submissions.html'
    context_object_name = 'submissions'

    def get_queryset(self):
        assignment_id = self.kwargs['assignment_id']
        return AssignmentSubmission.objects.filter(assignment_id=assignment_id).order_by('-submitted_at')


class GradeSubmissionView(LoginRequiredMixin, UpdateView):
    """Grade a submission"""
    model = AssignmentGrade
    template_name = 'assignments/grade.html'
    fields = ['score', 'max_score', 'feedback']
    pk_url_kwarg = 'submission_id'

    def get_object(self, queryset=None):
        submission_id = self.kwargs['submission_id']
        submission = AssignmentSubmission.objects.get(id=submission_id)
        grade, _ = AssignmentGrade.objects.get_or_create(submission=submission)
        return grade

    def get_success_url(self):
        submission = self.object.submission
        return reverse_lazy('assignments:submissions', kwargs={'assignment_id': submission.assignment.id})
