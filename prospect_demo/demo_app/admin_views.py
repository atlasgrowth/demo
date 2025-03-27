from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.contrib import messages
from django.utils import timezone
from .models import Prospect, Appointment, ChatMessage, Contact, ClientSettings
import csv
import json

@staff_member_required
def admin_dashboard(request):
    """Admin dashboard for managing businesses"""
    # Count statistics
    total_businesses = Prospect.objects.count()
    total_prospects = Prospect.objects.filter(status='prospect').count()
    total_clients = Prospect.objects.filter(status='converted').count()
    total_appointments = Appointment.objects.count()
    total_messages = ChatMessage.objects.count()
    total_contacts = Contact.objects.count()
    
    # Filter businesses based on search query and status
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    # Start with base queryset
    businesses = Prospect.objects.all()
    
    # Apply status filter if specified
    if status_filter:
        businesses = businesses.filter(status=status_filter)
    
    # Apply search filter if specified
    if search_query:
        businesses = businesses.filter(
            Q(name__icontains=search_query) | 
            Q(city__icontains=search_query) | 
            Q(state__icontains=search_query) |
            Q(business_type__icontains=search_query)
        )
    
    # Apply sorting
    sort_by = request.GET.get('sort', 'name')
    sort_order = request.GET.get('order', 'asc')
    
    # Handle special sorting cases
    if sort_by == 'activity':
        # Sort by most active (appointments + messages)
        businesses = businesses.annotate(
            activity_count=Count('appointments') + Count('chat_messages')
        ).order_by('-activity_count' if sort_order == 'desc' else 'activity_count')
    else:
        # Apply regular field sorting
        if sort_order == 'desc':
            businesses = businesses.order_by(f'-{sort_by}')
        else:
            businesses = businesses.order_by(sort_by)
    
    # Paginate the results
    paginator = Paginator(businesses, 25)  # Show 25 businesses per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Prepare business data with additional info
    business_data = []
    for business in page_obj:
        # Get activity counts
        appointment_count = Appointment.objects.filter(prospect=business).count()
        message_count = ChatMessage.objects.filter(prospect=business).count()
        contact_count = Contact.objects.filter(prospect=business).count()
        
        business_data.append({
            'business': business,
            'appointment_count': appointment_count,
            'message_count': message_count,
            'contact_count': contact_count,
        })
    
    context = {
        'total_businesses': total_businesses,
        'total_prospects': total_prospects,
        'total_clients': total_clients,
        'total_appointments': total_appointments,
        'total_messages': total_messages,
        'total_contacts': total_contacts,
        'business_data': business_data,
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'sort_by': sort_by,
        'sort_order': sort_order,
    }
    
    return render(request, 'admin/business_dashboard.html', context)

@staff_member_required
def business_detail(request, slug):
    """Detailed view of a single business"""
    business = get_object_or_404(Prospect, slug=slug)
    
    # Get activity data
    appointments = Appointment.objects.filter(prospect=business).order_by('-created_at')[:10]
    messages = ChatMessage.objects.filter(prospect=business).order_by('-timestamp')[:10]
    contacts = Contact.objects.filter(prospect=business).order_by('-created_at')[:10]
    
    # Appointment stats
    appointment_counts = {
        'pending': Appointment.objects.filter(prospect=business, status='pending').count(),
        'confirmed': Appointment.objects.filter(prospect=business, status='confirmed').count(),
        'completed': Appointment.objects.filter(prospect=business, status='completed').count(),
        'cancelled': Appointment.objects.filter(prospect=business, status='cancelled').count(),
    }
    
    # Contact stats
    contact_counts = {
        'lead': Contact.objects.filter(prospect=business, contact_type='lead').count(),
        'customer': Contact.objects.filter(prospect=business, contact_type='customer').count(),
        'past_customer': Contact.objects.filter(prospect=business, contact_type='past_customer').count(),
    }
    
    # Get client settings if this is a converted client
    client_settings = None
    if business.status == 'converted':
        try:
            client_settings = ClientSettings.objects.get(prospect=business)
        except ClientSettings.DoesNotExist:
            pass
    
    context = {
        'business': business,
        'appointments': appointments,
        'messages': messages,
        'contacts': contacts,
        'appointment_counts': appointment_counts,
        'contact_counts': contact_counts,
        'client_settings': client_settings,
    }
    
    return render(request, 'admin/business_detail.html', context)

@staff_member_required
def bulk_action(request):
    """Handle bulk actions on selected businesses"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
    
    # Get selected business IDs
    selected_ids = request.POST.getlist('selected_businesses', [])
    action = request.POST.get('action', '')
    
    if not selected_ids:
        messages.error(request, "No businesses were selected")
        return redirect('admin_dashboard')
        
    businesses = Prospect.objects.filter(id__in=selected_ids)
    count = businesses.count()
    
    if action == 'delete':
        # Delete selected businesses
        businesses.delete()
        messages.success(request, f"Successfully deleted {count} businesses")
    
    elif action == 'export':
        # Export selected businesses to CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="businesses.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Name', 'Address', 'City', 'State', 'Phone', 'Email', 'Website', 'Rating', 'Status'])
        
        for business in businesses:
            writer.writerow([
                business.name,
                business.address,
                business.city,
                business.state,
                business.phone,
                business.email,
                business.website,
                business.rating,
                business.status
            ])
        
        return response
    
    elif action == 'convert':
        # Convert selected businesses to clients
        now = timezone.now()
        converted_count = 0
        
        for business in businesses:
            if business.status != 'converted':
                business.status = 'converted'
                business.conversion_date = now
                business.save()
                
                # Create default client settings
                ClientSettings.objects.get_or_create(
                    prospect=business,
                    defaults={
                        'plan': 'basic',
                        'enable_email_notifications': True
                    }
                )
                
                converted_count += 1
                
        messages.success(request, f"Successfully converted {converted_count} businesses to clients")
    
    elif action == 'mark_inactive':
        # Mark selected businesses as inactive
        businesses.update(status='inactive')
        messages.success(request, f"Successfully marked {count} businesses as inactive")
    
    elif action == 'mark_prospect':
        # Mark selected businesses as prospects
        businesses.update(status='prospect', conversion_date=None)
        messages.success(request, f"Successfully marked {count} businesses as prospects")
    
    return redirect('admin_dashboard')

@staff_member_required
def business_preview(request, slug):
    """Show a preview of a business's demo site"""
    business = get_object_or_404(Prospect, slug=slug)
    return render(request, 'admin/business_preview.html', {'business': business})

@staff_member_required
def convert_to_client(request, slug):
    """Convert a prospect to a full client"""
    business = get_object_or_404(Prospect, slug=slug)
    
    if request.method == 'POST':
        # Update the prospect status
        business.status = 'converted'
        business.conversion_date = timezone.now()
        business.save()
        
        # Create or update client settings
        client_settings, created = ClientSettings.objects.get_or_create(prospect=business)
        
        # Update client settings with form data
        client_settings.custom_domain = request.POST.get('custom_domain', '')
        client_settings.plan = request.POST.get('plan', 'basic')
        
        # Set feature flags based on selected plan
        if client_settings.plan == 'premium' or client_settings.plan == 'enterprise':
            client_settings.enable_sms_notifications = True
            client_settings.enable_email_notifications = True
            
        if client_settings.plan == 'enterprise':
            client_settings.enable_online_payments = True
            client_settings.enable_staff_accounts = True
            client_settings.max_staff_accounts = 5
            
        # Save client settings
        client_settings.save()
        
        messages.success(request, f"Successfully converted {business.name} to a full client!")
        return redirect('admin_business_detail', slug=slug)
    
    # For GET requests, show the conversion form
    # Check if client settings already exist
    try:
        client_settings = ClientSettings.objects.get(prospect=business)
    except ClientSettings.DoesNotExist:
        client_settings = None
    
    return render(request, 'admin/convert_to_client.html', {
        'business': business,
        'client_settings': client_settings,
    })