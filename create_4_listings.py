"""
Create 4 Sample Equipment Listings Script
Creates diverse equipment listings with different categories and specifications.

Usage:
    python create_4_listings.py
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from datetime import timedelta
from accounts.models import User, CompanyProfile
from equipment.models import Category, Tag, Equipment, EquipmentImage, EquipmentSpecification

def get_or_create_company():
    """Get or create a company profile for listings"""
    company_user = User.objects.filter(user_type='company').first()
    
    if not company_user:
        company_user = User.objects.create_user(
            email='demo_company@tezrent.com',
            password='DemoPassword123!',
            user_type='company',
            first_name='TezRent',
            last_name='Equipment',
            phone='+971501234567',
            country='UAE',
            city='DXB'
        )
    
    company_profile = CompanyProfile.objects.filter(user=company_user).first()
    
    if not company_profile:
        company_profile = CompanyProfile.objects.create(
            user=company_user,
            company_name='TezRent Equipment Rentals LLC',
            license_number='CN-1234567',
            tax_number='TAX-987654321'
        )
    
    return company_profile

def create_listings():
    """Create 4 diverse equipment listings"""
    
    print("🏗️  Creating 4 Equipment Listings...")
    print("=" * 70)
    
    company_profile = get_or_create_company()
    print(f"✅ Using company: {company_profile.company_name}\n")
    
    # Define 4 equipment listings
    listings = [
        {
            'name': 'JCB 220X Excavator',
            'description': 'Powerful tracked excavator perfect for construction sites, trenching, and earthmoving. Features advanced hydraulics and comfortable operator cabin with air conditioning.',
            'category_name': 'Excavators',
            'manufacturer': 'JCB',
            'model_number': '220X',
            'year': 2023,
            'weight': 22000.00,
            'dimensions': '950x285x310',
            'fuel_type': 'Diesel',
            'daily_rate': 450.00,
            'weekly_rate': 2700.00,
            'monthly_rate': 9500.00,
            'status': 'available',
            'available_units': 2,
            'featured': True,
            'tags': ['heavy duty', 'construction', 'excavation'],
            'specifications': [
                {'name': 'Engine Power', 'value': '168 HP'},
                {'name': 'Bucket Capacity', 'value': '1.2 m³'},
                {'name': 'Max Digging Depth', 'value': '6.7 m'},
                {'name': 'Operating Weight', 'value': '22000 kg'}
            ]
        },
        {
            'name': 'Komatsu D65PX Bulldozer',
            'description': 'Heavy-duty crawler dozer with excellent productivity for grading, land clearing, and site preparation. Equipped with GPS guidance system and ripper attachment.',
            'category_name': 'Bulldozers',
            'manufacturer': 'Komatsu',
            'model_number': 'D65PX-18',
            'year': 2022,
            'weight': 23500.00,
            'dimensions': '600x390x340',
            'fuel_type': 'Diesel',
            'daily_rate': 550.00,
            'weekly_rate': 3300.00,
            'monthly_rate': 12000.00,
            'status': 'available',
            'available_units': 1,
            'featured': False,
            'tags': ['heavy duty', 'grading', 'land clearing'],
            'specifications': [
                {'name': 'Engine Power', 'value': '217 HP'},
                {'name': 'Blade Capacity', 'value': '4.2 m³'},
                {'name': 'Operating Weight', 'value': '23500 kg'},
                {'name': 'Blade Width', 'value': '3.9 m'}
            ]
        },
        {
            'name': 'Manitou MT 1440 Telehandler',
            'description': 'Versatile telescopic handler ideal for construction, agriculture, and warehouse operations. Features 4-ton lift capacity and 14-meter reach height.',
            'category_name': 'Telehandlers',
            'manufacturer': 'Manitou',
            'model_number': 'MT 1440',
            'year': 2024,
            'weight': 12500.00,
            'dimensions': '580x245x250',
            'fuel_type': 'Diesel',
            'daily_rate': 350.00,
            'weekly_rate': 2100.00,
            'monthly_rate': 7500.00,
            'status': 'available',
            'available_units': 3,
            'featured': True,
            'tags': ['versatile', 'construction', 'new arrival'],
            'specifications': [
                {'name': 'Lift Capacity', 'value': '4000 kg'},
                {'name': 'Max Lift Height', 'value': '14 m'},
                {'name': 'Engine Power', 'value': '100 HP'},
                {'name': 'Max Forward Reach', 'value': '10 m'}
            ]
        },
        {
            'name': 'Bobcat S650 Skid Steer Loader',
            'description': 'Compact and agile skid-steer loader perfect for tight spaces. Ideal for landscaping, small construction, and material handling. Quick-attach system for multiple attachments.',
            'category_name': 'Loaders',
            'manufacturer': 'Bobcat',
            'model_number': 'S650',
            'year': 2023,
            'weight': 3600.00,
            'dimensions': '350x180x205',
            'fuel_type': 'Diesel',
            'daily_rate': 250.00,
            'weekly_rate': 1500.00,
            'monthly_rate': 5500.00,
            'status': 'available',
            'available_units': 4,
            'featured': False,
            'tags': ['compact', 'versatile', 'landscaping'],
            'specifications': [
                {'name': 'Operating Capacity', 'value': '1247 kg'},
                {'name': 'Engine Power', 'value': '74 HP'},
                {'name': 'Operating Weight', 'value': '3600 kg'},
                {'name': 'Bucket Capacity', 'value': '0.6 m³'}
            ]
        }
    ]
    
    created_count = 0
    
    for idx, listing_data in enumerate(listings, 1):
        print(f"\n{'='*70}")
        print(f"📦 Creating Listing {idx}/4: {listing_data['name']}")
        print('='*70)
        
        # Get or create category
        category, cat_created = Category.objects.get_or_create(
            name=listing_data['category_name'],
            defaults={
                'description': f'{listing_data["category_name"]} for construction and industrial use',
                'is_featured': False,
                'display_order': idx
            }
        )
        print(f"   📁 Category: {category.name} {'(created)' if cat_created else '(existing)'}")
        
        # Get or create tags
        tags = []
        for tag_name in listing_data['tags']:
            tag, tag_created = Tag.objects.get_or_create(name=tag_name)
            tags.append(tag)
            print(f"   🏷️  Tag: {tag_name} {'(created)' if tag_created else '(existing)'}")
        
        # Check if equipment already exists
        existing = Equipment.objects.filter(
            name=listing_data['name'],
            model_number=listing_data['model_number']
        ).first()
        
        if existing:
            print(f"   ⚠️  Equipment already exists: {existing.name}")
            print(f"   ℹ️  Skipping creation...")
            continue
        
        # Create equipment
        equipment = Equipment.objects.create(
            seller_company=company_profile,
            name=listing_data['name'],
            description=listing_data['description'],
            category=category,
            manufacturer=listing_data['manufacturer'],
            model_number=listing_data['model_number'],
            year=listing_data['year'],
            weight=listing_data['weight'],
            dimensions=listing_data['dimensions'],
            fuel_type=listing_data['fuel_type'],
            daily_rate=listing_data['daily_rate'],
            weekly_rate=listing_data['weekly_rate'],
            monthly_rate=listing_data['monthly_rate'],
            country='UAE',
            city='DXB',
            status=listing_data['status'],
            available_units=listing_data['available_units'],
            total_units=listing_data['available_units'],
            featured=listing_data['featured']
        )
        
        # Add tags
        equipment.tags.set(tags)
        print(f"   ✅ Created equipment: {equipment.name}")
        
        # Create specifications
        for spec_data in listing_data['specifications']:
            EquipmentSpecification.objects.create(
                equipment=equipment,
                name=spec_data['name'],
                value=spec_data['value']
            )
        print(f"   📊 Added {len(listing_data['specifications'])} specifications")
        
        created_count += 1
        
        # Summary for this listing
        print(f"\n   💰 Pricing:")
        print(f"      Daily: ${equipment.daily_rate}")
        print(f"      Weekly: ${equipment.weekly_rate}")
        print(f"      Monthly: ${equipment.monthly_rate}")
        print(f"   📍 Location: {equipment.city}, {equipment.country}")
        print(f"   📊 Status: {equipment.status}")
        print(f"   🔢 Available Units: {equipment.available_units}")
    
    # Final summary
    print("\n" + "=" * 70)
    print("✨ SUMMARY")
    print("=" * 70)
    print(f"✅ Successfully created {created_count} new equipment listing(s)")
    print(f"📊 Total equipment in database: {Equipment.objects.count()}")
    print(f"🏷️  Total tags in database: {Tag.objects.count()}")
    print(f"📁 Total categories in database: {Category.objects.count()}")
    print("\n🎉 Done! You can now view these listings in your application.")
    print("=" * 70)

if __name__ == '__main__':
    try:
        create_listings()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
