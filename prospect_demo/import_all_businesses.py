import os
import django
import csv
import re
import random

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prospect_demo.settings')
django.setup()

from demo_app.models import Prospect

def slugify(text):
    """
    Custom slugify function to create URL-friendly slugs
    """
    # Convert to lowercase
    text = text.lower()
    # Remove special characters and replace spaces with hyphens
    text = re.sub(r'[^a-z0-9\s]', '', text)
    # Replace spaces with hyphens
    text = re.sub(r'\s+', '-', text)
    return text

def generate_login(name):
    """
    Generate login credentials from business name
    """
    # Remove all non-alphanumeric characters and spaces, convert to lowercase
    login = re.sub(r'[^a-zA-Z0-9]', '', name).lower()
    return login

def generate_colors():
    """
    Generate a random primary and secondary color
    """
    # List of professional color options
    primary_colors = [
        '#336699',  # Blue
        '#E53935',  # Red
        '#4CAF50',  # Green
        '#FF9800',  # Orange
        '#9C27B0',  # Purple
        '#607D8B',  # Blue Grey
        '#795548',  # Brown
        '#3F51B5',  # Indigo
        '#009688',  # Teal
        '#673AB7',  # Deep Purple
    ]
    
    # Randomly choose a primary color
    primary = random.choice(primary_colors)
    
    # For secondary color, we'll make a lighter or complementary shade
    if random.random() > 0.5:
        # Lighter shade
        r = int(primary[1:3], 16)
        g = int(primary[3:5], 16)
        b = int(primary[5:7], 16)
        
        # Make it lighter
        r = min(255, r + 40)
        g = min(255, g + 40)
        b = min(255, b + 40)
        
        secondary = f"#{r:02x}{g:02x}{b:02x}"
    else:
        # Just use a different color
        remaining_colors = [c for c in primary_colors if c != primary]
        secondary = random.choice(remaining_colors)
    
    return primary, secondary

def import_from_csv(file_path):
    """
    Import businesses from a CSV file
    """
    count = 0
    
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Extract business name
            name = row.get('name', '').strip()
            if not name:
                continue
            
            # Generate slug and login
            slug = slugify(name)
            login = generate_login(name)
            
            # Generate colors
            primary_color, secondary_color = generate_colors()
            
            # Prepare business data
            business_data = {
                'name': name,
                'slug': slug,
                'phone': row.get('phone', ''),
                'address': row.get('address', ''),
                'city': row.get('city', ''),
                'state': row.get('state', ''),
                'business_type': 'HVAC contractor',  # Default
                'rating': float(row.get('rating', 0)) if row.get('rating') else None,
                'reviews_count': int(row.get('reviews', 0)) if row.get('reviews') else 0,
                'primary_color': primary_color,
                'secondary_color': secondary_color,
                'username': login,
                'password': login,  # Set password same as username
            }
            
            # Update or create the prospect
            prospect, created = Prospect.objects.update_or_create(
                slug=slug,
                defaults=business_data
            )
            
            count += 1
            
            # Print progress every 10 businesses
            if count % 10 == 0:
                print(f"Processed {count} businesses...")
    
    return count

if __name__ == "__main__":
    # Path to your CSV file
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'businesses.csv')
    
    # Create data directory if it doesn't exist
    os.makedirs(os.path.join(os.path.dirname(__file__), 'data'), exist_ok=True)
    
    # Check if file exists
    if not os.path.exists(csv_path):
        print(f"CSV file not found at {csv_path}")
        print("Please make sure to place the CSV file in the data directory.")
        exit(1)
    
    # Import businesses
    count = import_from_csv(csv_path)
    print(f"Successfully imported {count} businesses.")
    
    # Show a sample of the imported businesses
    businesses = Prospect.objects.all()[:5]
    print("\nSample of imported businesses:")
    for business in businesses:
        print(f"{business.name} (Login: {business.username})")