from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import StudentBill, PaymentRecord


class StudentBillingView(LoginRequiredMixin, ListView):
    """View student's bills"""
    template_name = 'payments/billing.html'
    context_object_name = 'bills'
    paginate_by = 20

    def get_queryset(self):
        return StudentBill.objects.filter(student=self.request.user).order_by('-created_at')


class BillDetailView(LoginRequiredMixin, DetailView):
    """View bill details"""
    model = StudentBill
    template_name = 'payments/bill_detail.html'
    context_object_name = 'bill'
    pk_url_kwarg = 'bill_id'

    def get_queryset(self):
        return StudentBill.objects.filter(student=self.request.user)


class PayBillView(LoginRequiredMixin, DetailView):
    """Pay a bill"""
    model = StudentBill
    template_name = 'payments/pay_bill.html'
    context_object_name = 'bill'
    pk_url_kwarg = 'bill_id'

    def get_queryset(self):
        return StudentBill.objects.filter(student=self.request.user)


class PaymentHistoryView(LoginRequiredMixin, ListView):
    """View payment history"""
    template_name = 'payments/payment_history.html'
    context_object_name = 'payments'
    paginate_by = 20

    def get_queryset(self):
        return PaymentRecord.objects.filter(bill__student=self.request.user).order_by('-payment_date')


class AdminBillsView(LoginRequiredMixin, ListView):
    """Admin: View all bills"""
    template_name = 'payments/admin_bills.html'
    context_object_name = 'bills'
    paginate_by = 50

    def get_queryset(self):
        return StudentBill.objects.all().order_by('-created_at')
