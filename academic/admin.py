from django.contrib import admin
from .models import School, AcademicYear, Subject, Class, ClassSubjectTeacher, StudentEnrollment


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'city', 'is_active')
    search_fields = ('name', 'code', 'email')
    fieldsets = (
        ('Basic Info', {'fields': ('name', 'code', 'logo')}),
        ('Address', {'fields': ('address', 'city', 'province', 'postal_code')}),
        ('Contact', {'fields': ('phone', 'email', 'website')}),
        ('Leadership', {'fields': ('principal_name', 'principal_nip')}),
        ('Status', {'fields': ('is_active', 'established_year')}),
    )


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'start_date', 'end_date', 'is_current')
    list_filter = ('is_current',)
    search_fields = ('year_start', 'year_end')


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'school', 'is_active')
    list_filter = ('school', 'is_active')
    search_fields = ('name', 'code')


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'grade', 'academic_year', 'homeroom_teacher', 'get_student_count')
    list_filter = ('grade', 'academic_year', 'school')
    search_fields = ('name',)
    autocomplete_fields = ('homeroom_teacher',)


@admin.register(ClassSubjectTeacher)
class ClassSubjectTeacherAdmin(admin.ModelAdmin):
    list_display = ('class_obj', 'subject', 'teacher')
    list_filter = ('subject', 'teacher')
    search_fields = ('class_obj__name', 'teacher__username')
    autocomplete_fields = ('class_obj', 'subject', 'teacher')


@admin.register(StudentEnrollment)
class StudentEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'class_obj', 'status', 'enrollment_date')
    list_filter = ('status', 'class_obj', 'enrollment_date')
    search_fields = ('student__username', 'student__first_name', 'student__last_name')
    autocomplete_fields = ('student', 'class_obj')
    readonly_fields = ('enrollment_date', 'created_at', 'updated_at')
