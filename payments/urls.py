from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Student views
    path('billing/', views.StudentBillingView.as_view(), name='billing'),
    path('bill/<uuid:bill_id>/', views.BillDetailView.as_view(), name='bill_detail'),
    path('bill/<uuid:bill_id>/pay/', views.PayBillView.as_view(), name='pay_bill'),
    path('payment-history/', views.PaymentHistoryView.as_view(), name='payment_history'),

    # Admin/Teacher views
    path('admin/bills/', views.AdminBillsView.as_view(), name='admin_bills'),
]
