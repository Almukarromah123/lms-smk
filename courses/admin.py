from django.contrib import admin
from .models import Course, Module, Lesson, LessonAccess, CourseAttachment


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('subject', 'class_obj', 'academic_year', 'teacher', 'is_active')
    list_filter = ('is_active', 'academic_year', 'subject')
    search_fields = ('subject__name', 'class_obj__name')
    autocomplete_fields = ('subject', 'class_obj', 'academic_year', 'teacher')


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    list_filter = ('course',)
    search_fields = ('title', 'course__subject__name')
    ordering = ('course', 'order')


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'content_type', 'order', 'is_mandatory')
    list_filter = ('content_type', 'is_mandatory', 'module__course')
    search_fields = ('title', 'module__title')
    ordering = ('module', 'order')
    fieldsets = (
        ('Basic Info', {'fields': ('module', 'title', 'description', 'content_type')}),
        ('Content', {'fields': ('text_content', 'video_file', 'video_url', 'pdf_file')}),
        ('Metadata', {'fields': ('duration_minutes', 'order', 'is_mandatory')}),
    )


@admin.register(LessonAccess)
class LessonAccessAdmin(admin.ModelAdmin):
    list_display = ('student', 'lesson', 'is_completed', 'first_accessed', 'time_spent_seconds')
    list_filter = ('is_completed', 'first_accessed')
    search_fields = ('student__username', 'lesson__title')
    readonly_fields = ('first_accessed', 'last_accessed', 'time_spent_seconds')


@admin.register(CourseAttachment)
class CourseAttachmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'file_type', 'uploaded_at')
    list_filter = ('file_type', 'uploaded_at')
    search_fields = ('title', 'course__subject__name')
