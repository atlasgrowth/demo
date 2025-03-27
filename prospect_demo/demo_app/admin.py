from django.contrib import admin
from .models import Prospect, OutscraperImport, Appointment, ChatMessage, Contact

@admin.register(Prospect)
class ProspectAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'state', 'business_type', 'rating', 'demo_site_url')
    search_fields = ('name', 'city', 'state', 'business_type')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('business_type', 'city', 'state')

@admin.register(OutscraperImport)
class OutscraperImportAdmin(admin.ModelAdmin):
    list_display = ('file', 'processed', 'created_at')
    list_filter = ('processed',)

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'prospect', 'service_type', 'appointment_date', 'status')
    list_filter = ('status', 'service_type', 'appointment_date', 'prospect')
    search_fields = ('customer_name', 'customer_email', 'customer_phone', 'service_address')

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('sender_name', 'prospect', 'sender_type', 'timestamp', 'is_read')
    list_filter = ('sender_type', 'is_read', 'prospect')
    search_fields = ('sender_name', 'message')
    readonly_fields = ('timestamp',)

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'prospect', 'contact_type', 'phone', 'email', 'service_count')
    list_filter = ('contact_type', 'prospect', 'is_demo')
    search_fields = ('name', 'email', 'phone', 'address')
    readonly_fields = ('created_at', 'updated_at')