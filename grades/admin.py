from django.contrib import admin
from .models import GradeBook, ReportCard


@admin.register(GradeBook)
class GradeBookAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'semester', 'academic_year', 'final_score', 'letter_grade')
    list_filter = ('semester', 'academic_year', 'letter_grade', 'is_locked')
    search_fields = ('student__username', 'subject__name')
    autocomplete_fields = ('student', 'subject', 'class_obj', 'academic_year')
    readonly_fields = ('final_score', 'letter_grade', 'last_updated')

    fieldsets = (
        ('Student Info', {'fields': ('student', 'subject', 'class_obj', 'academic_year', 'semester')}),
        ('Scores', {
            'fields': ('assignment_average', 'exam_average', 'attendance_score', 'practical_score')
        }),
        ('Final Grade', {
            'fields': ('final_score', 'letter_grade', 'remarks', 'is_locked')
        }),
        ('Metadata', {'fields': ('last_updated',)}),
    )


@admin.register(ReportCard)
class ReportCardAdmin(admin.ModelAdmin):
    list_display = ('student', 'academic_year', 'semester', 'gpa', 'is_published', 'generated_at')
    list_filter = ('is_published', 'academic_year', 'semester', 'generated_at')
    search_fields = ('student__username', 'student__first_name', 'student__last_name')
    autocomplete_fields = ('student', 'class_obj', 'academic_year', 'published_by')
    readonly_fields = ('generated_at', 'gpa')

    fieldsets = (
        ('Student Info', {'fields': ('student', 'class_obj', 'academic_year', 'semester')}),
        ('GPA', {'fields': ('gpa', 'total_credits')}),
        ('Publication', {'fields': ('is_published', 'published_by', 'published_at')}),
        ('Notes', {'fields': ('principal_notes', 'homeroom_teacher_notes')}),
        ('Document', {'fields': ('pdf_file', 'generated_at')}),
    )

    actions = ['generate_pdf_action']

    def generate_pdf_action(self, request, queryset):
        """Action to generate PDF for selected report cards"""
        for report_card in queryset:
            report_card.generate_pdf()
        self.message_user(request, f"{queryset.count()} report card(s) PDF generated successfully.")

    generate_pdf_action.short_description = "Generate PDF for selected report cards"
