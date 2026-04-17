from django.db import models
from django.utils import timezone
from academic.models import Class, AcademicYear
from accounts.models import User
import uuid


class BillType(models.Model):
    """Types of bills (SPP, exam fees, registration, etc.)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)  # e.g., "SPP Bulanan", "Biaya Ujian"
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    base_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} (Rp {self.base_amount:,.2f})"


class StudentBill(models.Model):
    """Individual bill for a student"""
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PARTIAL', 'Partial Payment'),
        ('PAID', 'Paid'),
        ('OVERDUE', 'Overdue'),
        ('CANCELLED', 'Cancelled'),
    )

    PERIOD_CHOICES = (
        ('1', 'January'),
        ('2', 'February'),
        ('3', 'March'),
        ('4', 'April'),
        ('5', 'May'),
        ('6', 'June'),
        ('7', 'July'),
        ('8', 'August'),
        ('9', 'September'),
        ('10', 'October'),
        ('11', 'November'),
        ('12', 'December'),
        ('S1', 'Semester 1'),
        ('S2', 'Semester 2'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bills',
        limit_choices_to={'role': 'STUDENT'}
    )
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='student_bills')
    bill_type = models.ForeignKey(BillType, on_delete=models.CASCADE, related_name='student_bills')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='student_bills')

    # Period
    period = models.CharField(max_length=3, choices=PERIOD_CHOICES)  # Month or Semester
    due_date = models.DateField()

    # Amount
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    # Additional info
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'bill_type', 'academic_year', 'period')
        ordering = ['-due_date']
        verbose_name = 'Student Bill'
        verbose_name_plural = 'Student Bills'
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['due_date', 'status']),
        ]

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.bill_type.name} ({self.period})"

    def get_remaining_amount(self):
        """Get remaining amount to be paid"""
        return self.amount - self.paid_amount

    def is_overdue(self):
        """Check if bill is overdue"""
        return timezone.now().date() > self.due_date and self.status != 'PAID'

    def update_status(self):
        """Update bill status based on payment"""
        remaining = self.get_remaining_amount()
        if remaining <= 0:
            self.status = 'PAID'
        elif self.paid_amount > 0:
            self.status = 'PARTIAL'
        elif self.is_overdue():
            self.status = 'OVERDUE'
        self.save()


class PaymentRecord(models.Model):
    """Individual payment transaction"""
    PAYMENT_METHOD_CHOICES = (
        ('CASH', 'Cash'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('CREDIT_CARD', 'Credit Card'),
        ('E_WALLET', 'E-Wallet (Midtrans)'),
        ('DEBIT_CARD', 'Debit Card'),
    )

    PAYMENT_STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student_bill = models.ForeignKey(
        StudentBill,
        on_delete=models.CASCADE,
        related_name='payment_records'
    )
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='CASH')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='SUCCESS')

    # Transaction tracking
    transaction_id = models.CharField(max_length=255, unique=True, blank=True, null=True)
    reference_number = models.CharField(max_length=255, blank=True, null=True)  # Receipt number

    # Receipt info
    receipt_number = models.CharField(max_length=50, unique=True)
    notes = models.TextField(blank=True, null=True)

    # Recording
    recorded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recorded_payments',
        limit_choices_to={'role': 'ADMIN'}
    )

    class Meta:
        ordering = ['-payment_date']
        verbose_name = 'Payment Record'
        verbose_name_plural = 'Payment Records'
        indexes = [
            models.Index(fields=['student_bill', 'payment_date']),
            models.Index(fields=['status', 'payment_date']),
        ]

    def __str__(self):
        return f"Payment: {self.student_bill.student.get_full_name()} - Rp {self.amount_paid:,.2f} ({self.receipt_number})"

    def save(self, *args, **kwargs):
        # Generate receipt number if not set
        if not self.receipt_number:
            from django.utils.text import slugify
            timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
            self.receipt_number = f"RCP-{timestamp}"

        super().save(*args, **kwargs)

        # Update student bill paid amount and status
        if self.status == 'SUCCESS':
            self.student_bill.paid_amount += self.amount_paid
            self.student_bill.update_status()


class PaymentSchedule(models.Model):
    """Payment schedule template for billing"""
    FREQUENCY_CHOICES = (
        ('MONTHLY', 'Monthly'),
        ('QUARTERLY', 'Quarterly'),
        ('SEMESTER', 'Semester'),
        ('ANNUAL', 'Annual'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bill_type = models.ForeignKey(BillType, on_delete=models.CASCADE, related_name='schedules')
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='MONTHLY')
    start_month = models.IntegerField(default=1)  # 1-12 for months
    number_of_periods = models.IntegerField(default=12)  # How many periods
    days_before_due = models.IntegerField(default=7)  # Due date = period end + this days

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.bill_type.name} - {self.frequency}"
