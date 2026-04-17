from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.NotificationListView.as_view(), name='list'),
    path('create/', views.CreateNotificationView.as_view(), name='create'),
    path('<uuid:notification_id>/', views.NotificationDetailView.as_view(), name='detail'),
    path('<uuid:notification_id>/mark-read/', views.MarkAsReadView.as_view(), name='mark_read'),
    path('mark-all-read/', views.MarkAllAsReadView.as_view(), name='mark_all_read'),
    path('api/unread-count/', views.GetUnreadCountView.as_view(), name='unread_count'),
]
