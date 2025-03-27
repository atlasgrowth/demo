from django.urls import path
from . import views
from . import admin_views

urlpatterns = [
    path('', views.home, name='home'),
    path('prospect/<slug:slug>/', views.prospect_page, name='prospect_page'),
    
    # Business portal - place these BEFORE the catch-all slug route
    path('business/login/', views.business_login, name='business_login'),
    path('business/dashboard/<slug:slug>/', views.business_dashboard, name='business_dashboard'),
    path('business/appointments/<slug:slug>/', views.business_appointments, name='business_appointments'),
    path('business/calendar/<slug:slug>/', views.business_calendar, name='business_calendar'),
    path('business/messages/<slug:slug>/', views.business_messages, name='business_messages'),
    path('business/contacts/<slug:slug>/', views.business_contacts, name='business_contacts'),
    path('business/logout/', views.business_logout, name='business_logout'),
    
    # Custom admin dashboard
    path('manage/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('manage/business/<slug:slug>/', admin_views.business_detail, name='admin_business_detail'),
    path('manage/business/<slug:slug>/preview/', admin_views.business_preview, name='admin_business_preview'),
    path('manage/business/<slug:slug>/convert/', admin_views.convert_to_client, name='admin_convert_to_client'),
    path('manage/bulk-action/', admin_views.bulk_action, name='admin_bulk_action'),
    
    # API endpoints - place these BEFORE the catch-all slug route
    path('api/<slug:slug>/schedule/', views.api_schedule_appointment, name='api_schedule_appointment'),
    path('api/<slug:slug>/send-message/', views.api_send_message, name='api_send_message'),
    path('api/appointment/<int:appointment_id>/update/', views.api_update_appointment, name='api_update_appointment'),
    path('api/messages/<str:conversation_id>/mark-read/', views.api_mark_messages_read, name='api_mark_messages_read'),
    
    # This catch-all route must come LAST
    path('<slug:slug>/', views.prospect_page, name='prospect_direct'),
]