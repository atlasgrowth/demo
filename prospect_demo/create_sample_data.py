import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prospect_demo.settings')
django.setup()

from demo_app.models import Prospect

# Sample data for prospects
sample_prospects = [
    {
        'name': 'Stegall Heating & Air',
        'slug': 'stegall-heating-air',
        'phone': '+1 205-251-0330',
        'email': 'info@stegallheating.com',
        'website': 'https://callstegall.com/',
        'address': '2800 5th Ave S, Birmingham, AL 35233',
        'city': 'Birmingham',
        'state': 'Alabama',
        'business_type': 'HVAC contractor',
        'description': 'Professional heating, air conditioning, and plumbing services for residential and commercial customers. We pride ourselves on quality workmanship and exceptional customer service.',
        'rating': 4.6,
        'reviews_count': 134,
        'logo_url': 'https://lh3.googleusercontent.com/-UGqf5vM7ANk/AAAAAAAAAAI/AAAAAAAAAAA/OcfY-4qxdvY/s44-p-k-no-ns-nd/photo.jpg',
        'photo_url': 'https://lh5.googleusercontent.com/p/AF1QipNxEj83bMk8PSthd1fh1Bo1zaVb0fRQqxhE_Bwo=w800-h500-k-no',
        'primary_color': '#336699',
        'secondary_color': '#66aacc',
    },
    {
        'name': 'Coolray Heating & Cooling',
        'slug': 'coolray-heating-cooling',
        'phone': '+1 205-315-0411',
        'email': 'info@coolray.com',
        'website': 'https://www.coolray.com/al/birmingham',
        'address': '240A Lyon Ln, Birmingham, AL 35211',
        'city': 'Birmingham',
        'state': 'Alabama',
        'business_type': 'HVAC contractor',
        'description': 'Coolray is your trusted partner for heating, cooling, plumbing, and electrical services throughout Birmingham and surrounding areas. Our licensed technicians are dedicated to providing the highest quality service.',
        'rating': 4.8,
        'reviews_count': 1801,
        'logo_url': 'https://lh5.googleusercontent.com/-lM6X5sbWg_E/AAAAAAAAAAI/AAAAAAAAAAA/f59vXW4KoGE/s44-p-k-no-ns-nd/photo.jpg',
        'photo_url': 'https://lh5.googleusercontent.com/p/AF1QipPXjQ538U8Hwl8zetfaoonA2eNXjhhBKrKkV8iS=w800-h500-k-no',
        'primary_color': '#E53935',
        'secondary_color': '#FF6F61',
    },
    {
        'name': 'TemperaturePro Birmingham',
        'slug': 'temperaturepro-birmingham',
        'phone': '+1 205-737-3821',
        'email': 'contact@temperaturepro.com',
        'website': 'https://temperatureprobirmingham.com/',
        'address': '402 Office Park Dr Suite 208, Birmingham, AL 35223',
        'city': 'Birmingham',
        'state': 'Alabama',
        'business_type': 'HVAC contractor',
        'description': 'TemperaturePro offers a full range of heating and cooling services to keep your home comfortable all year round. Our team specializes in installation, maintenance, and repair of all HVAC systems.',
        'rating': 5.0,
        'reviews_count': 57,
        'logo_url': 'https://lh5.googleusercontent.com/-pA4G0PGsRKA/AAAAAAAAAAI/AAAAAAAAAAA/pBOyQOKzAsw/s44-p-k-no-ns-nd/photo.jpg',
        'photo_url': 'https://lh5.googleusercontent.com/p/AF1QipNXAf5pNQ6K09WNb4uyPWJExcxXNHWZ7vqnKweT=w800-h500-k-no',
        'primary_color': '#4CAF50',
        'secondary_color': '#8BC34A',
    }
]

# Create the prospects
for prospect_data in sample_prospects:
    Prospect.objects.update_or_create(
        slug=prospect_data['slug'],
        defaults=prospect_data
    )

print(f"Created {len(sample_prospects)} sample prospects.")