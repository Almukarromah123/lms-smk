from django.contrib import admin
from .models import Exam, ExamQuestion, ExamSession, ExamAnswer


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'class_obj', 'exam_date', 'is_published', 'get_question_count')
    list_filter = ('is_published', 'exam_date', 'subject', 'class_obj')
    search_fields = ('title', 'subject__name', 'class_obj__name')
    autocomplete_fields = ('subject', 'class_obj', 'created_by')
    readonly_fields = ('created_at', 'updated_at', 'get_question_count')
    fieldsets = (
        ('Basic Info', {'fields': ('subject', 'class_obj', 'created_by', 'title')}),
        ('Content', {'fields': ('description', 'get_question_count')}),
        ('Exam Settings', {'fields': ('exam_date', 'duration_minutes', 'total_points')}),
        ('Question Settings', {'fields': ('shuffle_questions', 'shuffle_options', 'allow_back', 'question_per_page')}),
        ('Publication', {'fields': ('is_published', 'display_answer_key', 'show_feedback')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(ExamQuestion)
class ExamQuestionAdmin(admin.ModelAdmin):
    list_display = ('exam', 'order', 'question_type', 'points', 'is_active')
    list_filter = ('question_type', 'is_active', 'exam')
    search_fields = ('question_text', 'exam__title')
    autocomplete_fields = ('exam',)
    fieldsets = (
        ('Question Info', {'fields': ('exam', 'order', 'question_text', 'image')}),
        ('Type & Options', {'fields': ('question_type', 'options_data', 'correct_answer')}),
        ('Scoring', {'fields': ('points', 'is_active')}),
        ('Additional', {'fields': ('explanation',)}),
    )


@admin.register(ExamSession)
class ExamSessionAdmin(admin.ModelAdmin):
    list_display = ('exam', 'student', 'status', 'score', 'started_at', 'submitted_at')
    list_filter = ('status', 'started_at', 'submitted_at')
    search_fields = ('exam__title', 'student__username')
    autocomplete_fields = ('exam', 'student')
    readonly_fields = ('student_answers', 'started_at', 'submitted_at', 'graded_at')


@admin.register(ExamAnswer)
class ExamAnswerAdmin(admin.ModelAdmin):
    list_display = ('session', 'question', 'student_answer', 'is_correct', 'points_earned')
    list_filter = ('is_correct', 'answered_at')
    search_fields = ('session__exam__title', 'session__student__username')
    autocomplete_fields = ('session', 'question')
    readonly_fields = ('answered_at',)
