from django.contrib import admin
from .models import AttendanceRecord, AttendanceSummary, AttendanceSession


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'attendance_session', 'attendance_date', 'status', 'recorded_by', 'recorded_at')
    list_filter = ('status', 'attendance_date', 'attendance_session__class_subject_teacher__class_obj')
    search_fields = ('student__username', 'student__first_name', 'student__last_name')
    autocomplete_fields = ('student', 'recorded_by')
    date_hierarchy = 'attendance_date'
    readonly_fields = ('recorded_at',)

    fieldsets = (
        ('Attendance Info', {'fields': ('student', 'attendance_session', 'attendance_date', 'status')}),
        ('Time Info', {'fields': ('arrival_time', 'remarks')}),
        ('Recording', {'fields': ('recorded_by', 'recorded_at')}),
    )


@admin.register(AttendanceSummary)
class AttendanceSummaryAdmin(admin.ModelAdmin):
    list_display = ('student', 'class_obj', 'period_type', 'total_days', 'present_count', 'absent_count', 'attendance_percentage')
    list_filter = ('period_type', 'period_start_date', 'period_end_date', 'class_obj')
    search_fields = ('student__username', 'student__first_name', 'student__last_name', 'class_obj__name')
    autocomplete_fields = ('student', 'class_obj')
    readonly_fields = ('generated_at', 'attendance_percentage', 'total_days')

    fieldsets = (
        ('Student Info', {'fields': ('student', 'class_obj')}),
        ('Period', {'fields': ('period_type', 'period_start_date', 'period_end_date')}),
        ('Counts', {
            'fields': ('total_days', 'present_count', 'absent_count', 'late_count', 'excused_count', 'sick_count')
        }),
        ('Summary', {'fields': ('attendance_percentage', 'generated_at')}),
    )


@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    def teacher_name(self, obj):
        return obj.class_subject_teacher.teacher.get_full_name()
    teacher_name.short_description = 'Teacher'

    def class_name(self, obj):
        return obj.class_subject_teacher.class_obj.name
    class_name.short_description = 'Class'

    def subject_name(self, obj):
        return obj.class_subject_teacher.subject.name
    subject_name.short_description = 'Subject'

    def qr_token_status(self, obj):
        """Display QR token status"""
        if obj.session_type == 'DARING':
            return "N/A (DARING)"
        if not obj.qr_token:
            return "Not Generated"
        if obj.is_qr_token_expired():
            return "❌ Expired"
        return "✅ Active"
    qr_token_status.short_description = 'QR Status'

    def regenerate_qr_token(self, request, queryset):
        """Admin action to regenerate QR tokens"""
        count = 0
        for session in queryset:
            if session.session_type == 'LURING':
                session.generate_new_qr_token()
                count += 1
        self.message_user(request, f'Regenerated QR tokens for {count} LURING sessions.')
    regenerate_qr_token.short_description = "Regenerate QR tokens for selected LURING sessions"

    list_display = ('class_name', 'subject_name', 'teacher_name', 'session_date', 'session_type', 'qr_token_status', 'is_open', 'created_at')
    list_filter = ('session_date', 'session_type', 'is_open', 'class_subject_teacher__class_obj', 'class_subject_teacher__subject')
    search_fields = ('class_subject_teacher__class_obj__name', 'class_subject_teacher__subject__name', 'class_subject_teacher__teacher__first_name', 'class_subject_teacher__teacher__last_name')
    autocomplete_fields = ('class_subject_teacher',)
    date_hierarchy = 'session_date'
    readonly_fields = ('created_at', 'qr_token_generated_at', 'qr_token')
    actions = ['regenerate_qr_token']

    fieldsets = (
        ('Session Info', {'fields': ('class_subject_teacher',)}),
        ('Session Details', {'fields': ('session_date', 'session_type', 'description', 'is_open')}),
        ('QR Code (LURING only)', {
            'fields': ('qr_token', 'qr_token_generated_at', 'qr_token_expires_at'),
            'classes': ('collapse',),
            'description': 'These fields are only used for LURING (in-person) sessions.',
        }),
        ('Created', {'fields': ('created_at',)}),
    )

