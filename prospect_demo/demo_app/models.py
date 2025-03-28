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
    
    # Conversion status
    STATUS_CHOICES = (
        ('prospect', 'Prospect'),
        ('converted', 'Converted Client'),
        ('inactive', 'Inactive'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='prospect')
    conversion_date = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        # Generate username using the format (all lowercase, no spaces, no special characters)
        if not self.username:
            # Remove any non-alphanumeric characters and make lowercase
            self.username = ''.join(e for e in self.name if e.isalnum()).lower()
        
        # Generate base slug from business name (all lowercase, no spaces, no special characters)
        base_slug = ''.join(e for e in self.name if e.isalnum()).lower()
        
        # Check for slug uniqueness and add a number suffix if necessary
        if not self.slug or self.slug != base_slug:
            self.slug = base_slug
            
            # Check if this slug already exists
            from django.db.models import Q
            if self.pk:  # If this is an existing object
                slug_exists = type(self).objects.filter(~Q(pk=self.pk), slug=self.slug).exists()
            else:  # This is a new object
                slug_exists = type(self).objects.filter(slug=self.slug).exists()
                
            # If the slug exists, append a number until we find a unique slug
            if slug_exists:
                counter = 1
                while type(self).objects.filter(slug=f"{base_slug}{counter}").exists():
                    counter += 1
                self.slug = f"{base_slug}{counter}"
        
        # Set demo site URL
        if not self.demo_site_url:
            self.demo_site_url = f"{self.slug}.localhost:8000"
            
        # Set password same as username if not provided
        if not self.password or self.password == "demo123":
            self.password = self.username
            
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

# Client settings for converted prospects
class ClientSettings(models.Model):
    prospect = models.OneToOneField(Prospect, on_delete=models.CASCADE, related_name='client_settings')
    
    # Domain settings
    custom_domain = models.CharField(max_length=255, blank=True)
    domain_verified = models.BooleanField(default=False)
    
    # Billing information
    PLAN_CHOICES = (
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('enterprise', 'Enterprise'),
    )
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='basic')
    subscription_active = models.BooleanField(default=True)
    
    # Feature flags
    enable_sms_notifications = models.BooleanField(default=False)
    enable_email_notifications = models.BooleanField(default=True)
    enable_online_payments = models.BooleanField(default=False)
    enable_staff_accounts = models.BooleanField(default=False)
    max_staff_accounts = models.IntegerField(default=1)
    
    # API Integration
    twilio_account_sid = models.CharField(max_length=255, blank=True)
    twilio_auth_token = models.CharField(max_length=255, blank=True)
    twilio_phone_number = models.CharField(max_length=20, blank=True)
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Client settings for {self.prospect.name}"