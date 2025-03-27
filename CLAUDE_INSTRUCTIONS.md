# Prospect Demo Platform - Complete Technical Documentation

## Project Overview

This document provides comprehensive technical details about the Prospect Demo Platform, a Django-based system that allows businesses to showcase their services to potential clients through customized demo websites.

### Core Concept

The platform creates individual demo websites for service businesses (HVAC contractors, plumbers, etc.), each with:
- Custom subdomain (e.g., business-name.example.com)
- Functional features (appointment scheduling, chat, customer management)
- Branded colors and business information
- Complete backend management portal

When a prospect is interested, they get immediate access to a working demo. If they convert to a client, their demo site transitions to a full client site with additional features.

## System Architecture

### Technology Stack

- **Backend Framework**: Django 4.x with SQLite database
- **Frontend**: Bootstrap 5, custom CSS, JavaScript, Font Awesome icons
- **Database Models**: Prospect, Appointment, ChatMessage, Contact
- **Authentication**: Session-based with custom username/password login
- **Data Import**: CSV-based business data import

### File Structure

```
/prospect_demo/
├── create_demo_data.py           # Script to generate demo appointments, messages, etc.
├── create_sample_data.py         # Script to create sample prospects
├── import_all_businesses.py      # Script to import businesses from CSV
├── data/
│   └── businesses.csv            # Sample business data for import
├── demo_app/
│   ├── models.py                 # Database models
│   ├── views.py                  # View controllers
│   ├── urls.py                   # URL routing
│   ├── middleware.py             # Subdomain handling
│   └── templates/
│       ├── prospect_site.html    # Customer-facing demo site
│       ├── business_dashboard.html
│       ├── business_appointments.html
│       ├── business_calendar.html
│       ├── business_messages.html
│       ├── business_contacts.html
│       └── business_login.html
└── prospect_demo/
    ├── settings.py               # Django settings
    ├── urls.py                   # Main URL routing
    └── wsgi.py                   # WSGI configuration
```

## Core Models

### Prospect Model

The central entity representing a business prospect:

- **Basic Info**: name, slug, business_type, description
- **Contact Info**: phone, email, website, address, city, state
- **Business Details**: hours (JSON), rating, reviews_count
- **Media**: logo_url, photo_url
- **Design**: primary_color, secondary_color
- **Authentication**: username, password (auto-generated from business name)

Key methods:
- `save()`: Automatically generates slug, demo site URL, and login credentials

### Appointment Model

Tracks customer service appointments:

- **Customer Info**: customer_name, customer_email, customer_phone
- **Service Details**: service_type, service_address, notes
- **Scheduling**: appointment_date, appointment_time_slot
- **Status**: pending, confirmed, completed, cancelled
- **System Fields**: created_at, updated_at, is_demo

### ChatMessage Model

Stores all chat communications:

- **Sender Info**: sender_type (customer, business, system), sender_name
- **Content**: message
- **Metadata**: conversation_id for threading, is_read status
- **System Fields**: timestamp, is_demo

### Contact Model

Manages customer/lead information:

- **Basic Info**: name, email, phone
- **Address**: address, city, state, postal_code
- **Status**: contact_type (lead, customer, past_customer)
- **Metadata**: notes, service_count
- **System Fields**: created_at, updated_at, is_demo

## Key Features Implementation

### 1. Dynamic Subdomain Routing

The platform uses Django middleware to handle subdomain routing:

```python
# In middleware.py
class SubdomainMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Extract subdomain from host
        host = request.get_host().split('.')
        if len(host) > 2 and host[0] != 'www':
            request.subdomain = host[0]
        else:
            request.subdomain = None
        return self.get_response(request)
```

This allows each business to have its own subdomain, which directs to their customized demo site.

### 2. Business Authentication

Authentication uses standard Django sessions with a custom login mechanism:

1. Usernames and passwords are automatically generated from the business name by:
   - Removing all spaces and special characters
   - Converting to lowercase

2. Login view checks credentials and creates a session with business ID and name.

3. Protected views check for session data before allowing access.

### 3. Chat Widget with Lead Capture

The chat widget is implemented using:

1. Frontend JavaScript for the chat interface
2. Backend API endpoints to store messages
3. A lead capture form that collects customer information on first contact
4. Integration with the Contact model to store lead data

Key workflow:
- When a visitor starts a chat, they see a welcome message
- After first message, they're prompted to fill out a contact form
- Form data creates a Contact record and adds customer information to chat
- Additional notes from chat can be appended to the contact record

### 4. Appointment Scheduling

The appointment system allows:

1. Customers to schedule appointments through the demo site
2. Business users to view, manage, and update appointment status
3. Calendar visualization of all appointments
4. Filtering by appointment status (pending, confirmed, completed, cancelled)

### 5. Data Import System

The system can import businesses from CSV files:

1. `import_all_businesses.py` processes CSV data
2. For each business, it:
   - Creates a Prospect record
   - Generates a unique slug
   - Creates login credentials
   - Assigns random brand colors

CSV format includes: name, address, city, state, phone, website, rating, reviews

### 6. Styling and Branding

Each prospect site is dynamically styled using:

1. CSS variables for primary and secondary colors
2. Responsive design for all device sizes
3. Consistent UI components across all pages
4. Modern, professional look and feel

## API Endpoints

The platform provides several API endpoints:

1. `/api/<slug>/schedule/` - Schedule a new appointment
2. `/api/<slug>/send-message/` - Send a chat message
3. `/api/appointment/<id>/update/` - Update appointment status
4. `/api/messages/<conversation_id>/mark-read/` - Mark messages as read

## Deployment Considerations

When deploying this platform:

1. **Domain Configuration**: Set up wildcard DNS records to handle subdomains
2. **Database**: Consider migrating to PostgreSQL for production
3. **Static Files**: Configure proper static file serving
4. **Security**: Update SECRET_KEY, disable DEBUG, configure HTTPS
5. **Scaling**: Implement caching and optimize database queries

## Additional Development Tips

For future developers enhancing this platform:

1. **Username Generation**: The system creates usernames and passwords by removing all spaces and special characters from the business name. Always ensure the business name property is populated.

2. **Contact Creation from Chat**: When a visitor submits the chat intake form, the system automatically creates a Contact record. The form collects first name, last name, email, phone, and address.

3. **Subdomain Testing**: To test different business subdomains locally, use `<slug>.localhost:8000` in your browser. You may need to configure your hosts file.

4. **Demo Data**: Use the `create_demo_data.py` script to populate test data for development and demonstrations.

5. **CSV Import**: The `import_all_businesses.py` script can be used to batch import businesses from a CSV file in the data directory.

6. **Login System**: Business logins use the format: `businessnamewithnospaces` for both username and password (all lowercase, no spaces or special characters).

7. **UI Customization**: The platform uses CSS variables for styling. The primary color variables are defined at the root level and can be customized per business.

## Future Enhancement Roadmap

1. **Client Conversion Process**: Implement the workflow to convert a prospect to a client
2. **Custom Domain Support**: Allow clients to use their own domains
3. **Advanced Analytics**: Add reporting on lead conversion, appointment stats
4. **Payment Processing**: Integrate payment capabilities
5. **SMS Notifications**: Add Twilio integration for appointment reminders
6. **Review Collection**: Implement a system for collecting and displaying reviews
7. **Service Area Maps**: Add map integration to show service areas
8. **Multi-user Access**: Allow businesses to create staff accounts with different permissions

## Troubleshooting

Common issues and solutions:

1. **Subdomain Not Working**: Check middleware registration in settings.py
2. **Login Issues**: Verify username/password generation in models.py
3. **Message Threading**: Check conversation_id generation in the chat system
4. **Appointment Calendar**: Ensure appointment date formats are consistent
5. **CSS Variables**: Check for proper propagation of custom colors

---

This document should give future Claude instances a comprehensive understanding of the Prospect Demo Platform architecture, implementation details, and key features. For specific code questions, refer to the actual source files in the repository.