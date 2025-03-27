from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib import messages
from .models import Prospect, Appointment, ChatMessage, Contact
import json
from datetime import datetime

def home(request):
    """Main view that handles both main site and prospect sites."""
    if hasattr(request, 'subdomain') and request.subdomain:
        # Find prospect by subdomain
        prospect = get_object_or_404(Prospect, slug=request.subdomain)
        return render(request, 'prospect_site.html', {'prospect': prospect})
    else:
        # Main site
        prospects = Prospect.objects.all()
        return render(request, 'main_site.html', {'prospects': prospects})

def prospect_page(request, slug):
    """Alternative view for accessing prospect pages via path."""
    prospect = get_object_or_404(Prospect, slug=slug)
    return render(request, 'prospect_site.html', {'prospect': prospect})

# Business Backend Views
def business_login(request):
    """Login page for business."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            # First try to find the prospect by username
            prospect = Prospect.objects.get(username=username)
            
            # Check if the password matches
            if password == prospect.password:
                # Store in session
                request.session['business_id'] = prospect.id
                request.session['business_name'] = prospect.name
                return redirect('business_dashboard', slug=prospect.slug)
            else:
                messages.error(request, "Incorrect password. The password should be the same as your username.")
        except Prospect.DoesNotExist:
            # If username not found, check if it's a slug
            try:
                prospect = Prospect.objects.get(slug=username)
                
                # Check if the password matches
                if password == prospect.password:
                    # Store in session
                    request.session['business_id'] = prospect.id
                    request.session['business_name'] = prospect.name
                    return redirect('business_dashboard', slug=prospect.slug)
                else:
                    messages.error(request, "Incorrect password. The password should be the same as your username.")
            except Prospect.DoesNotExist:
                messages.error(request, "Business not found. Try one of the example logins shown below.")
    
    return render(request, 'business_login.html')

def business_dashboard(request, slug):
    """Dashboard for business to manage appointments and messages."""
    if 'business_id' not in request.session:
        return redirect('business_login')
    
    prospect = get_object_or_404(Prospect, slug=slug)
    
    # Verify this business is logged in
    if request.session['business_id'] != prospect.id:
        return redirect('business_login')
    
    # Get recent appointments
    appointments = Appointment.objects.filter(prospect=prospect).order_by('-appointment_date')[:5]
    
    # Get unread messages
    messages = ChatMessage.objects.filter(
        prospect=prospect, 
        is_read=False, 
        sender_type='customer'
    ).order_by('-timestamp')[:5]
    
    # Get counts
    pending_appointments = Appointment.objects.filter(prospect=prospect, status='pending').count()
    unread_messages = ChatMessage.objects.filter(prospect=prospect, is_read=False, sender_type='customer').count()
    
    # Get lead statistics
    lead_count = Contact.objects.filter(prospect=prospect, contact_type='lead').count()
    chat_lead_count = Contact.objects.filter(
        prospect=prospect, 
        contact_type='lead', 
        notes__contains='Created from chat'
    ).count()
    
    context = {
        'prospect': prospect,
        'appointments': appointments,
        'messages': messages,
        'pending_appointments': pending_appointments,
        'unread_messages': unread_messages,
        'lead_count': lead_count,
        'chat_lead_count': chat_lead_count,
    }
    
    return render(request, 'business_dashboard.html', context)

def business_appointments(request, slug):
    """View to manage appointments."""
    if 'business_id' not in request.session:
        return redirect('business_login')
    
    prospect = get_object_or_404(Prospect, slug=slug)
    
    # Verify this business is logged in
    if request.session['business_id'] != prospect.id:
        return redirect('business_login')
    
    # Get filtered appointments
    status_filter = request.GET.get('status', '')
    if status_filter:
        appointments = Appointment.objects.filter(prospect=prospect, status=status_filter).order_by('-appointment_date')
    else:
        appointments = Appointment.objects.filter(prospect=prospect).order_by('-appointment_date')
    
    # Get unread messages count for the navigation badge
    unread_messages = ChatMessage.objects.filter(
        prospect=prospect, 
        is_read=False, 
        sender_type='customer'
    ).count()
    
    context = {
        'prospect': prospect,
        'appointments': appointments,
        'status_filter': status_filter,
        'unread_messages': unread_messages,
    }
    
    return render(request, 'business_appointments.html', context)

def business_calendar(request, slug):
    """Calendar view for appointments."""
    if 'business_id' not in request.session:
        return redirect('business_login')
    
    prospect = get_object_or_404(Prospect, slug=slug)
    
    # Verify this business is logged in
    if request.session['business_id'] != prospect.id:
        return redirect('business_login')
    
    # Get all appointments for this business
    appointments = Appointment.objects.filter(prospect=prospect).order_by('appointment_date')
    
    # Format appointments for calendar display
    calendar_data = []
    for appointment in appointments:
        # Convert appointment time slot to approximate times for display
        time_start = "09:00"
        if appointment.appointment_time_slot == "Morning":
            time_start = "09:00"
        elif appointment.appointment_time_slot == "Afternoon":
            time_start = "13:00"
        elif appointment.appointment_time_slot == "Evening":
            time_start = "17:00"
        
        # Set colors based on status
        color = "#ffc107"  # default yellow for pending
        if appointment.status == 'confirmed':
            color = "#198754"  # green
        elif appointment.status == 'completed':
            color = "#0d6efd"  # blue
        elif appointment.status == 'cancelled':
            color = "#dc3545"  # red
        
        # Create calendar event
        calendar_data.append({
            'id': appointment.id,
            'title': f"{appointment.customer_name} - {appointment.service_type}",
            'start': f"{appointment.appointment_date.isoformat()}T{time_start}",
            'color': color,
            'extendedProps': {
                'customer': appointment.customer_name,
                'phone': appointment.customer_phone,
                'email': appointment.customer_email,
                'address': appointment.service_address,
                'service': appointment.service_type,
                'notes': appointment.notes,
                'status': appointment.status
            }
        })
    
    # Get unread messages count for the navigation badge
    unread_messages = ChatMessage.objects.filter(
        prospect=prospect, 
        is_read=False, 
        sender_type='customer'
    ).count()
    
    context = {
        'prospect': prospect,
        'calendar_data': json.dumps(calendar_data),
        'unread_messages': unread_messages,
    }
    
    return render(request, 'business_calendar.html', context)

def business_messages(request, slug):
    """View to manage messages."""
    if 'business_id' not in request.session:
        return redirect('business_login')
    
    prospect = get_object_or_404(Prospect, slug=slug)
    
    # Verify this business is logged in
    if request.session['business_id'] != prospect.id:
        return redirect('business_login')
    
    # Get all messages, grouped by conversation
    conversations = {}
    all_messages = ChatMessage.objects.filter(prospect=prospect).order_by('timestamp')
    
    for message in all_messages:
        if not message.conversation_id:
            message.conversation_id = f"conv_{message.sender_name}_{message.id}"
            message.save()
        
        if message.conversation_id not in conversations:
            conversations[message.conversation_id] = {
                'messages': [],
                'latest_timestamp': message.timestamp,
                'sender_name': message.sender_name,
                'unread': 0
            }
        
        conversations[message.conversation_id]['messages'].append(message)
        
        if message.timestamp > conversations[message.conversation_id]['latest_timestamp']:
            conversations[message.conversation_id]['latest_timestamp'] = message.timestamp
        
        if not message.is_read and message.sender_type == 'customer':
            conversations[message.conversation_id]['unread'] += 1
    
    # Sort conversations by latest message timestamp
    sorted_conversations = dict(sorted(
        conversations.items(), 
        key=lambda x: x[1]['latest_timestamp'], 
        reverse=True
    ))
    
    context = {
        'prospect': prospect,
        'conversations': sorted_conversations,
    }
    
    return render(request, 'business_messages.html', context)

def business_contacts(request, slug):
    """View to manage contacts."""
    if 'business_id' not in request.session:
        return redirect('business_login')
    
    prospect = get_object_or_404(Prospect, slug=slug)
    
    # Verify this business is logged in
    if request.session['business_id'] != prospect.id:
        return redirect('business_login')
    
    # Handle new contact form submission
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal_code')
        contact_type = request.POST.get('contact_type')
        notes = request.POST.get('notes')
        
        if name:  # Basic validation
            Contact.objects.create(
                prospect=prospect,
                name=name,
                email=email,
                phone=phone,
                address=address,
                city=city,
                state=state,
                postal_code=postal_code,
                contact_type=contact_type,
                notes=notes
            )
            messages.success(request, f"Contact '{name}' created successfully.")
            return redirect('business_contacts', slug=slug)
    
    # Get filtered contacts
    contact_type_filter = request.GET.get('type', '')
    if contact_type_filter:
        contacts = Contact.objects.filter(prospect=prospect, contact_type=contact_type_filter).order_by('-created_at')
    else:
        contacts = Contact.objects.filter(prospect=prospect).order_by('-created_at')
    
    # Get unread messages count for the navigation badge
    unread_messages = ChatMessage.objects.filter(
        prospect=prospect, 
        is_read=False, 
        sender_type='customer'
    ).count()
    
    context = {
        'prospect': prospect,
        'contacts': contacts,
        'contact_type_filter': contact_type_filter,
        'unread_messages': unread_messages,
    }
    
    return render(request, 'business_contacts.html', context)

def business_logout(request):
    """Logout business user."""
    if 'business_id' in request.session:
        del request.session['business_id']
    if 'business_name' in request.session:
        del request.session['business_name']
    
    return redirect('business_login')

# API for frontend
@csrf_exempt
def api_schedule_appointment(request, slug):
    """API endpoint for scheduling appointments."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
    
    prospect = get_object_or_404(Prospect, slug=slug)
    data = json.loads(request.body)
    
    try:
        appointment = Appointment.objects.create(
            prospect=prospect,
            customer_name=data.get('fullName', ''),
            customer_email=data.get('emailAddress', ''),
            customer_phone=data.get('phoneNumber', ''),
            service_type=data.get('serviceType', ''),
            service_address=data.get('serviceAddress', ''),
            notes=data.get('serviceNotes', ''),
            appointment_date=datetime.strptime(data.get('preferredDate', ''), '%Y-%m-%d').date(),
            appointment_time_slot=data.get('preferredTime', ''),
            status='pending'
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Appointment scheduled successfully',
            'appointment_id': appointment.id
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def api_send_message(request, slug):
    """API endpoint for sending chat messages."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
    
    prospect = get_object_or_404(Prospect, slug=slug)
    data = json.loads(request.body)
    
    try:
        conversation_id = data.get('conversation_id', '')
        if not conversation_id:
            # Create a new conversation ID
            conversation_id = f"conv_{data.get('sender_name', 'customer')}_{timezone.now().timestamp()}"
        
        message = ChatMessage.objects.create(
            prospect=prospect,
            sender_type=data.get('sender_type', 'customer'),
            sender_name=data.get('sender_name', 'Customer'),
            message=data.get('message', ''),
            conversation_id=conversation_id,
            is_read=False
        )
        
        # If this is a system message with contact info, create a Contact record
        contact_info = data.get('contact_info', None)
        add_to_notes = data.get('add_to_contact_notes', False)
        
        if data.get('sender_type') == 'system' and contact_info:
            # Check if a contact with this email or phone already exists
            existing_contact = Contact.objects.filter(
                prospect=prospect,
                email=contact_info.get('email')
            ).first()
            
            if not existing_contact:
                existing_contact = Contact.objects.filter(
                    prospect=prospect,
                    phone=contact_info.get('phone')
                ).first()
            
            if existing_contact:
                # Update existing contact
                existing_contact.name = contact_info.get('name', existing_contact.name)
                existing_contact.phone = contact_info.get('phone', existing_contact.phone)
                existing_contact.email = contact_info.get('email', existing_contact.email)
                if contact_info.get('address'):
                    existing_contact.address = contact_info.get('address')
                # If they're an existing customer, update their contact type if it's currently a lead
                if contact_info.get('is_existing_customer') and existing_contact.contact_type == 'lead':
                    existing_contact.contact_type = 'customer'
                
                # If this message should be added to contact notes
                if add_to_notes:
                    # Append to existing notes or create new notes
                    new_note = data.get('message', '')
                    if existing_contact.notes:
                        existing_contact.notes = f"{existing_contact.notes}\n\n{new_note}"
                    else:
                        existing_contact.notes = new_note
                
                existing_contact.save()
            else:
                # Create new contact
                contact_type = 'customer' if contact_info.get('is_existing_customer') else 'lead'
                initial_notes = f"Created from chat on {timezone.now().strftime('%Y-%m-%d')}"
                
                # Add additional notes if specified
                if add_to_notes:
                    initial_notes += f"\n\n{data.get('message', '')}"
                
                Contact.objects.create(
                    prospect=prospect,
                    name=contact_info.get('name', ''),
                    email=contact_info.get('email', ''),
                    phone=contact_info.get('phone', ''),
                    address=contact_info.get('address', ''),
                    contact_type=contact_type,
                    notes=initial_notes
                )
        
        return JsonResponse({
            'success': True,
            'message_id': message.id,
            'conversation_id': conversation_id,
            'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def api_update_appointment(request, appointment_id):
    """API endpoint for updating appointment status."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
    
    appointment = get_object_or_404(Appointment, id=appointment_id)
    data = json.loads(request.body)
    
    try:
        # Check if business is logged in
        if 'business_id' not in request.session or request.session['business_id'] != appointment.prospect.id:
            return JsonResponse({'error': 'Unauthorized'}, status=401)
        
        appointment.status = data.get('status', appointment.status)
        appointment.notes = data.get('notes', appointment.notes)
        appointment.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Appointment updated successfully'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def api_mark_messages_read(request, conversation_id):
    """API endpoint for marking messages as read."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
    
    try:
        # Check if business is logged in
        if 'business_id' not in request.session:
            return JsonResponse({'error': 'Unauthorized'}, status=401)
        
        messages = ChatMessage.objects.filter(
            conversation_id=conversation_id,
            sender_type='customer',
            is_read=False
        )
        
        # Verify the conversation belongs to the logged in business
        if messages.exists():
            first_message = messages.first()
            if request.session['business_id'] != first_message.prospect.id:
                return JsonResponse({'error': 'Unauthorized'}, status=401)
        
        # Mark all as read
        count = messages.update(is_read=True)
        
        return JsonResponse({
            'success': True,
            'count': count,
            'message': f'{count} messages marked as read'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)