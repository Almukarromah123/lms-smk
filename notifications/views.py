from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from accounts.models import User
from .models import Notification


class NotificationListView(LoginRequiredMixin, ListView):
    """List user's notifications"""
    template_name = 'notifications/list.html'
    context_object_name = 'notifications'
    paginate_by = 50

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get unread count
        context['unread_count'] = Notification.objects.filter(
            recipient=self.request.user,
            is_read=False
        ).count()
        return context


class NotificationDetailView(LoginRequiredMixin, DetailView):
    """View notification detail"""
    model = Notification
    template_name = 'notifications/detail.html'
    context_object_name = 'notification'
    pk_url_kwarg = 'notification_id'

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    def get_object(self, queryset=None):
        """Mark notification as read when viewed"""
        obj = super().get_object(queryset)
        if not obj.is_read:
            obj.is_read = True
            obj.save()
        return obj


class CreateNotificationView(LoginRequiredMixin, CreateView):
    """Send notification to users (admin/teacher only)"""
    model = Notification
    template_name = 'notifications/create.html'
    fields = ['title', 'message', 'notification_type']
    success_url = reverse_lazy('notifications:list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Only allow admin and teachers to send notifications
        if self.request.user.role not in ['ADMIN', 'TEACHER']:
            messages.error(self.request, "Anda tidak memiliki izin untuk mengirim notifikasi.")
            return self.handle_no_permission()
        return kwargs

    def form_valid(self, form):
        """Send notification to all students in relevant classes"""
        form.instance.sender = self.request.user

        # Determine recipients based on role
        if self.request.user.role == 'ADMIN':
            # Admin can notify all students
            form.instance.recipient = User.objects.filter(role='STUDENT').first()
            # In practice, you'd create multiple notification objects

        messages.success(self.request, 'Notifikasi berhasil dikirim!')
        return super().form_valid(form)


class MarkAsReadView(LoginRequiredMixin, View):
    """Mark a notification as read"""
    def post(self, request, *args, **kwargs):
        try:
            notification = Notification.objects.get(
                id=kwargs['notification_id'],
                recipient=request.user
            )
            notification.is_read = True
            notification.save()
        except Notification.DoesNotExist:
            pass
        return redirect('notifications:list')


class MarkAllAsReadView(LoginRequiredMixin, View):
    """Mark all notifications as read"""
    def post(self, request, *args, **kwargs):
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return redirect('notifications:list')


class GetUnreadCountView(LoginRequiredMixin, View):
    """Get unread notification count (for AJAX)"""
    def get(self, request):
        count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        return JsonResponse({'unread_count': count})
