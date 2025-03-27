from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User

class Prospect(models.Model):
    # Basic info
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    
    # Contact info
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    
    # Location
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    
    # Business details
    business_type = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    hours = models.JSONField(default=dict, blank=True)
    
    # Reviews
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    reviews_count = models.IntegerField(default=0)
    
    # Media
    logo_url = models.URLField(blank=True)
    photo_url = models.URLField(blank=True)
    
    # Demo site
    demo_site_url = models.CharField(max_length=255, blank=True)
    primary_color = models.CharField(max_length=20, default="#336699")
    secondary_color = models.CharField(max_length=20, default="#66aacc")
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Business Login
    username = models.CharField(max_length=255, blank=True)
    password = models.CharField(max_length=255, default="demo123")
    
    def save(self, *args, **kwargs):
        # Generate slug if not provided
        if not self.slug:
            self.slug = slugify(self.name)
        
        # Set demo site URL
        if not self.demo_site_url:
            self.demo_site_url = f"{self.slug}.localhost:8000"
            
        # Set username for backend login
        if not self.username:
            self.username = self.slug
            
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

# Appointment model for scheduling
class Appointment(models.Model):
    prospect = models.ForeignKey(Prospect, on_delete=models.CASCADE, related_name='appointments')
    
    # Customer information
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField(blank=True, null=True)
    customer_phone = models.CharField(max_length=20)
    
    # Service details
    service_type = models.CharField(max_length=100)
    service_address = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    
    # Appointment time
    appointment_date = models.DateField()
    appointment_time_slot = models.CharField(max_length=50)  # e.g., "Morning", "Afternoon"
    
    # Status
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_demo = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.customer_name} - {self.appointment_date} - {self.service_type}"

# Chat messages
class ChatMessage(models.Model):
    prospect = models.ForeignKey(Prospect, on_delete=models.CASCADE, related_name='chat_messages')
    
    # Message details
    SENDER_CHOICES = (
        ('customer', 'Customer'),
        ('business', 'Business'),
        ('system', 'System'),
    )
    sender_type = models.CharField(max_length=20, choices=SENDER_CHOICES)
    sender_name = models.CharField(max_length=255, blank=True)
    message = models.TextField()
    
    # For chat threading
    conversation_id = models.CharField(max_length=255, blank=True)
    
    # Status
    is_read = models.BooleanField(default=False)
    
    # System fields
    timestamp = models.DateTimeField(auto_now_add=True)
    is_demo = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.sender_name} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

# Contact model for customer management
class Contact(models.Model):
    prospect = models.ForeignKey(Prospect, on_delete=models.CASCADE, related_name='contacts')
    
    # Basic information
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Additional information
    notes = models.TextField(blank=True)
    
    # Status/classification
    TYPE_CHOICES = (
        ('lead', 'Lead'),
        ('customer', 'Customer'),
        ('past_customer', 'Past Customer'),
    )
    contact_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='lead')
    
    # Service history count (for quick reference)
    service_count = models.IntegerField(default=0)
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_demo = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} - {self.phone}"

# Simple import utility
class OutscraperImport(models.Model):
    file = models.FileField(upload_to='imports/')
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)