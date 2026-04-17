from django.contrib import admin
from .models import Assignment, AssignmentSubmission, AssignmentGrade


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'class_obj', 'subject', 'teacher', 'due_date', 'is_active')
    list_filter = ('is_active', 'due_date', 'class_obj', 'subject')
    search_fields = ('title', 'class_obj__name', 'teacher__username')
    autocomplete_fields = ('class_obj', 'subject', 'teacher')
    readonly_fields = ('created_date', 'get_submission_count')
    fieldsets = (
        ('Basic Info', {'fields': ('class_obj', 'subject', 'teacher', 'title')}),
        ('Content', {'fields': ('description', 'instructions', 'attachment')}),
        ('Dates', {'fields': ('due_date', 'submission_deadline', 'created_date')}),
        ('Grading', {'fields': ('total_points', 'is_active')}),
        ('Stats', {'fields': ('get_submission_count',)}),
    )


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'student', 'submitted_at', 'is_late', 'is_graded')
    list_filter = ('is_late', 'is_graded', 'submitted_at')
    search_fields = ('assignment__title', 'student__username')
    autocomplete_fields = ('assignment', 'student')
    readonly_fields = ('submitted_at',)


@admin.register(AssignmentGrade)
class AssignmentGradeAdmin(admin.ModelAdmin):
    list_display = ('submission', 'score', 'max_score', 'get_percentage', 'graded_by', 'graded_at')
    list_filter = ('graded_at', 'graded_by')
    search_fields = ('submission__assignment__title', 'submission__student__username')
    autocomplete_fields = ('submission', 'graded_by')
    readonly_fields = ('graded_at', 'get_percentage')
    fieldsets = (
        ('Submission', {'fields': ('submission',)}),
        ('Score', {'fields': ('score', 'max_score', 'get_percentage')}),
        ('Feedback', {'fields': ('feedback', 'graded_by', 'graded_at')}),
    )
