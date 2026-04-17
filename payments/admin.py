from django.contrib import admin
from .models import BillType, StudentBill, PaymentRecord, PaymentSchedule


@admin.register(BillType)
class BillTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'base_amount', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')


@admin.register(StudentBill)
class StudentBillAdmin(admin.ModelAdmin):
    list_display = ('student', 'bill_type', 'period', 'amount', 'paid_amount', 'get_remaining_amount', 'status', 'due_date')
    list_filter = ('status', 'bill_type', 'due_date', 'academic_year')
    search_fields = ('student__username', 'student__first_name', 'student__last_name', 'bill_type__name')
    autocomplete_fields = ('student', 'bill_type', 'class_obj', 'academic_year')
    readonly_fields = ('created_at', 'updated_at', 'get_remaining_amount')

    fieldsets = (
        ('Student Info', {'fields': ('student', 'class_obj', 'academic_year')}),
        ('Bill Info', {'fields': ('bill_type', 'period', 'due_date')}),
        ('Amount', {'fields': ('amount', 'paid_amount', 'get_remaining_amount')}),
        ('Status', {'fields': ('status', 'notes')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(PaymentRecord)
class PaymentRecordAdmin(admin.ModelAdmin):
    list_display = ('receipt_number', 'student_bill', 'amount_paid', 'payment_method', 'status', 'payment_date')
    list_filter = ('status', 'payment_method', 'payment_date')
    search_fields = ('student_bill__student__username', 'receipt_number', 'transaction_id')
    autocomplete_fields = ('student_bill', 'recorded_by')
    readonly_fields = ('payment_date', 'receipt_number')

    fieldsets = (
        ('Bill Info', {'fields': ('student_bill',)}),
        ('Payment Details', {'fields': ('amount_paid', 'payment_method', 'payment_date', 'status')}),
        ('Transaction', {'fields': ('transaction_id', 'reference_number', 'receipt_number')}),
        ('Recording', {'fields': ('recorded_by', 'notes')}),
    )


@admin.register(PaymentSchedule)
class PaymentScheduleAdmin(admin.ModelAdmin):
    list_display = ('bill_type', 'frequency', 'number_of_periods', 'is_active')
    list_filter = ('frequency', 'is_active')
    search_fields = ('bill_type__name',)
    autocomplete_fields = ('bill_type',)
