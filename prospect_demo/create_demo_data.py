import os
import django
import random
from datetime import datetime, timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prospect_demo.settings')
django.setup()

from demo_app.models import Prospect, Appointment, ChatMessage, Contact

# Demo appointment data
def create_demo_appointments():
    # Get all prospects
    prospects = Prospect.objects.all()
    
    if not prospects:
        print("No prospects found. Please run create_sample_data.py first.")
        return
    
    # Clear existing demo appointments
    Appointment.objects.filter(is_demo=True).delete()
    
    # Customer names for demo appointments
    customer_names = [
        "John Smith", "Emma Johnson", "Michael Williams", "Olivia Brown", 
        "James Jones", "Sophia Miller", "Robert Davis", "Ava Wilson",
        "David Taylor", "Isabella Martinez", "William Anderson", "Mia Thomas"
    ]
    
    # Service types
    service_types = [
        "AC Repair", "Heating System Maintenance", "New AC Installation",
        "Furnace Repair", "Ductwork Cleaning", "HVAC System Tune-up",
        "Thermostat Replacement", "Emergency Heating Repair"
    ]
    
    # Statuses with weights (pending will be more common)
    statuses = [
        ("pending", 0.4),
        ("confirmed", 0.3),
        ("completed", 0.2),
        ("cancelled", 0.1)
    ]
    
    # Time slots
    time_slots = [
        "Morning (8:00 AM - 12:00 PM)",
        "Afternoon (12:00 PM - 4:00 PM)",
        "Evening (4:00 PM - 7:00 PM)"
    ]
    
    # Create 5-10 appointments for each prospect
    appointments_created = 0
    for prospect in prospects:
        # Choose random number of appointments for this prospect
        num_appointments = random.randint(5, 10)
        
        for i in range(num_appointments):
            # Random date between today and 14 days from now
            days_offset = random.randint(-7, 14)  # Some in the past, some in future
            appointment_date = (datetime.now() + timedelta(days=days_offset)).date()
            
            # Choose status based on date
            if days_offset < 0:
                # Past appointments are either completed or cancelled
                status = random.choices(["completed", "cancelled"], weights=[0.8, 0.2])[0]
            else:
                # Future appointments use weighted distribution
                status = random.choices(
                    [s[0] for s in statuses], 
                    weights=[s[1] for s in statuses]
                )[0]
            
            # Create the appointment
            appointment = Appointment.objects.create(
                prospect=prospect,
                customer_name=random.choice(customer_names),
                customer_email=f"customer{random.randint(1, 100)}@example.com",
                customer_phone=f"+1 555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                service_type=random.choice(service_types),
                service_address=f"{random.randint(100, 9999)} Main St, {prospect.city}, {prospect.state}",
                notes=f"Customer requested service for their {random.choice(['heating', 'cooling', 'HVAC'])} system.",
                appointment_date=appointment_date,
                appointment_time_slot=random.choice(time_slots),
                status=status,
                is_demo=True,
                created_at=datetime.now() - timedelta(days=random.randint(1, 10))
            )
            appointments_created += 1
    
    print(f"Created {appointments_created} demo appointments.")

# Demo chat messages
def create_demo_chats():
    # Get all prospects
    prospects = Prospect.objects.all()
    
    if not prospects:
        print("No prospects found. Please run create_sample_data.py first.")
        return
    
    # Clear existing demo messages
    ChatMessage.objects.filter(is_demo=True).delete()
    
    # Customer names for demo chats
    customer_names = [
        "Alex Johnson", "Sarah Williams", "Marcus Lee", "Rachel Garcia", 
        "Daniel Smith", "Taylor Brown", "Chris Davis", "Jessica Martinez"
    ]
    
    # Customer message templates
    customer_messages = [
        "Hi, I'm interested in getting a quote for {service}.",
        "Hello, my {system} isn't working properly. Can someone come take a look?",
        "I need help with my heating system. It's making strange noises.",
        "Do you offer services in the {city} area?",
        "What are your rates for AC installation?",
        "I'd like to schedule an appointment for next week.",
        "My AC is not cooling effectively. What could be the issue?",
        "Do you offer maintenance plans?",
        "How soon can someone come out to look at my furnace?",
        "I'm building a new home and need HVAC installation quotes."
    ]
    
    # Business message templates
    business_messages = [
        "Thank you for reaching out to {business}. We'd be happy to help with your {service} needs.",
        "Hello {customer}, we provide service in {city} and surrounding areas. When would be a good time for a technician to visit?",
        "We offer free estimates for new installations. Would you like to schedule an appointment?",
        "Our technician can be available as early as tomorrow. Does that work for you?",
        "I'd be happy to provide information about our maintenance plans. They start at $149/year and include two tune-ups.",
        "Could you provide more details about the issue you're experiencing?",
        "We'll need to inspect your system to diagnose the problem. Is there a preferred time for a technician to visit?",
        "Our service call fee is $89, which is waived if you proceed with the repairs. How does that sound?",
        "We appreciate your interest! I'll have our installation specialist contact you.",
        "Thank you for choosing {business}. We look forward to serving you!"
    ]
    
    # Sample services
    services = ["AC repair", "furnace maintenance", "HVAC replacement", "duct cleaning"]
    
    # Create 3-7 conversations for each prospect
    chats_created = 0
    for prospect in prospects:
        # Choose random number of conversations for this prospect
        num_conversations = random.randint(3, 7)
        
        for i in range(num_conversations):
            # Create a conversation
            conversation_id = f"conv_demo_{prospect.slug}_{i}"
            customer_name = random.choice(customer_names)
            
            # Choose random number of messages in this conversation (3-10)
            num_messages = random.randint(3, 10)
            
            # Messages alternate between customer and business
            is_customer_turn = True  # Start with customer
            
            # Create messages with timestamps spaced out
            base_time = datetime.now() - timedelta(days=random.randint(0, 14), hours=random.randint(0, 23))
            
            for j in range(num_messages):
                # Increment time for each message
                message_time = base_time + timedelta(minutes=random.randint(1, 30) * j)
                
                if is_customer_turn:
                    # Customer message
                    message_template = random.choice(customer_messages)
                    message = message_template.format(
                        service=random.choice(services),
                        system=random.choice(["AC", "furnace", "heat pump"]),
                        city=prospect.city
                    )
                    
                    ChatMessage.objects.create(
                        prospect=prospect,
                        sender_type="customer",
                        sender_name=customer_name,
                        message=message,
                        conversation_id=conversation_id,
                        is_read=random.choice([True, False]),
                        timestamp=message_time,
                        is_demo=True
                    )
                else:
                    # Business message
                    message_template = random.choice(business_messages)
                    message = message_template.format(
                        business=prospect.name,
                        customer=customer_name,
                        service=random.choice(services),
                        city=prospect.city
                    )
                    
                    ChatMessage.objects.create(
                        prospect=prospect,
                        sender_type="business",
                        sender_name=prospect.name,
                        message=message,
                        conversation_id=conversation_id,
                        is_read=True,  # Business messages are always read
                        timestamp=message_time,
                        is_demo=True
                    )
                
                chats_created += 1
                is_customer_turn = not is_customer_turn  # Alternate turns
    
    print(f"Created {chats_created} demo chat messages.")

# Demo contacts
def create_demo_contacts():
    # Get all prospects
    prospects = Prospect.objects.all()
    
    if not prospects:
        print("No prospects found. Please run create_sample_data.py first.")
        return
    
    # Clear existing demo contacts
    Contact.objects.filter(is_demo=True).delete()
    
    # Contact names
    first_names = [
        "John", "Michael", "David", "James", "Robert", "William", "Richard", "Thomas", 
        "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica",
        "Sarah", "Karen", "Nancy", "Lisa", "Margaret", "Betty", "Sandra", "Ashley"
    ]
    
    last_names = [
        "Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson",
        "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin",
        "Thompson", "Garcia", "Martinez", "Robinson", "Clark", "Rodriguez", "Lewis", "Lee"
    ]
    
    # Contact types with weights
    contact_types = [
        ("lead", 0.5),       # 50% leads
        ("customer", 0.3),   # 30% customers
        ("past_customer", 0.2)  # 20% past customers
    ]
    
    # Create 5-15 contacts for each prospect
    contacts_created = 0
    for prospect in prospects:
        # Choose random number of contacts for this prospect
        num_contacts = random.randint(5, 15)
        
        for i in range(num_contacts):
            # Generate random contact
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            name = f"{first_name} {last_name}"
            
            # Choose contact type based on weights
            contact_type = random.choices(
                [t[0] for t in contact_types], 
                weights=[t[1] for t in contact_types]
            )[0]
            
            # Service count - more services for customers than leads
            if contact_type == "lead":
                service_count = 0
            elif contact_type == "past_customer":
                service_count = random.randint(1, 3)
            else:  # customer
                service_count = random.randint(2, 8)
            
            # Create notes based on contact type
            if contact_type == "lead":
                notes = random.choice([
                    f"Potential {prospect.business_type} client. Called about pricing.",
                    f"Inquired about {random.choice(['AC repair', 'furnace maintenance', 'HVAC installation'])}.",
                    "Requested a quote for a new installation.",
                    "Found us through Google search.",
                    "Referred by an existing customer."
                ])
            elif contact_type == "customer":
                notes = random.choice([
                    f"Regular customer since {random.randint(2020, 2024)}.",
                    "Prefers appointments in the morning.",
                    "Has a service contract for annual maintenance.",
                    "Has multiple properties that need servicing.",
                    "Very particular about technicians removing shoes in the house."
                ])
            else:  # past_customer
                notes = random.choice([
                    "Haven't scheduled service in over 2 years.",
                    "Moved to a different area.",
                    "Previously used our services but switched providers.",
                    "May be worth following up for seasonal maintenance.",
                    "Had some issues with last service call."
                ])
            
            # Contact details
            email = f"{first_name.lower()}.{last_name.lower()}@example.com"
            phone = f"+1 {random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
            
            # Create contact
            Contact.objects.create(
                prospect=prospect,
                name=name,
                email=email,
                phone=phone,
                address=f"{random.randint(100, 9999)} {random.choice(['Main', 'Oak', 'Maple', 'Cedar', 'Pine'])} {random.choice(['St', 'Ave', 'Rd', 'Blvd', 'Dr'])}",
                city=prospect.city or "Birmingham",
                state=prospect.state or "Alabama",
                postal_code=f"{random.randint(10000, 99999)}",
                contact_type=contact_type,
                notes=notes,
                service_count=service_count,
                is_demo=True
            )
            contacts_created += 1
    
    print(f"Created {contacts_created} demo contacts.")

if __name__ == "__main__":
    create_demo_appointments()
    create_demo_chats()
    create_demo_contacts()
    print("Demo data creation complete!")