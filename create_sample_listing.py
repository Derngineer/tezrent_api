"""
Sample Equipment Listing Script
Creates a complete equipment listing with category, tags, specifications, and images.

Usage:
    python create_sample_listing.py
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

def create_sample_listing():
    """Create a complete sample equipment listing"""
    
    print("🔧 Creating Sample Equipment Listing...")
    print("=" * 60)
    
    # Step 1: Get or create a company profile
    print("\n1️⃣  Finding/Creating Company Profile...")
    
    # Find first company user or create one
    company_user = User.objects.filter(user_type='company').first()
    
    if not company_user:
        print("   ❌ No company users found. Creating one...")
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
        print(f"   ✅ Created company user: {company_user.email}")
    else:
        print(f"   ✅ Using existing company user: {company_user.email}")
    
    # Get or create company profile
    company_profile = CompanyProfile.objects.filter(user=company_user).first()
    
    if not company_profile:
        company_profile = CompanyProfile.objects.create(
            user=company_user,
            company_name='TezRent Equipment Rentals LLC',
            license_number='CN-1234567',
            tax_number='TAX-987654321'
        )
        print(f"   ✅ Created company profile: {company_profile.company_name}")
    else:
        print(f"   ✅ Using existing company profile: {company_profile.company_name}")
    
    # Step 2: Create or get category
    print("\n2️⃣  Creating/Getting Category...")
    category, created = Category.objects.get_or_create(
        name='Excavators',
        defaults={
            'description': 'Heavy-duty excavators for construction and mining projects',
            'is_featured': True,
            'display_order': 1,
            'color_code': '#FF6B35'
        }
    )
    
    if created:
        print(f"   ✅ Created category: {category.name}")
    else:
        print(f"   ✅ Using existing category: {category.name}")
    
    # Step 3: Create tags
    print("\n3️⃣  Creating Tags...")
    tag_names = ['Heavy Equipment', 'Construction', 'Mining', 'Excavation', 'Hydraulic']
    tags = []
    
    for tag_name in tag_names:
        tag, created = Tag.objects.get_or_create(name=tag_name)
        tags.append(tag)
        status = "✅ Created" if created else "✅ Found"
        print(f"   {status} tag: {tag_name}")
    
    # Step 4: Create equipment listing
    print("\n4️⃣  Creating Equipment Listing...")
    
    equipment = Equipment.objects.create(
        seller_company=company_profile,
        name='Caterpillar 320D2 L Hydraulic Excavator',
        description="""High-performance hydraulic excavator ideal for heavy construction, demolition, and mining operations. 
        
Features:
• Advanced hydraulic system for maximum efficiency
• Spacious, ergonomic cab with climate control
• Fuel-efficient Cat C4.4 ACERT engine
• 360-degree rotation capability
• Multiple attachment options available
• Advanced safety features and monitoring systems

Perfect for:
✓ Large-scale construction projects
✓ Demolition work
✓ Mining operations
✓ Site preparation
✓ Trenching and excavation

Includes operator manual and safety guidelines. Delivery and setup available.""",
        category=category,
        manufacturer='Caterpillar',
        model_number='320D2 L',
        year=2022,
        weight=22500.00,  # 22.5 tons in kg
        dimensions='996 x 294 x 323',  # LxWxH in cm
        fuel_type='Diesel',
        
        # Pricing
        daily_rate=1500.00,
        weekly_rate=9000.00,
        monthly_rate=32000.00,
        
        # Location
        country='UAE',
        city='DXB',
        
        # Availability
        status='available',
        total_units=3,
        available_units=3,
        
        # Promotional features
        featured=True,
        is_new_listing=True,
        is_todays_deal=True,
        original_daily_rate=1800.00,
        deal_discount_percentage=17,  # ~300 AED off
        deal_expires_at=timezone.now() + timedelta(days=7),
        promotion_badge='HOT DEAL',
        promotion_description='Save 300 AED/day! Limited time offer - Book now for your next project.'
    )
    
    # Add tags to equipment
    equipment.tags.set(tags)
    
    print(f"   ✅ Created equipment: {equipment.name}")
    print(f"   📍 Location: {equipment.city_name}, {equipment.country_name}")
    print(f"   💰 Daily Rate: AED {equipment.daily_rate}")
    print(f"   🏷️  Deal Price: AED {equipment.discounted_daily_rate} (Save AED {equipment.savings_amount})")
    print(f"   📦 Available Units: {equipment.available_units}/{equipment.total_units}")
    
    # Step 5: Add specifications
    print("\n5️⃣  Adding Technical Specifications...")
    
    specs = [
        ('Engine Model', 'Cat C4.4 ACERT'),
        ('Engine Power', '121 kW (162 hp)'),
        ('Operating Weight', '22.5 tonnes'),
        ('Bucket Capacity', '1.0 m³'),
        ('Max Digging Depth', '6.7 m'),
        ('Max Reach at Ground Level', '10.0 m'),
        ('Max Dumping Height', '7.1 m'),
        ('Swing Speed', '11.1 rpm'),
        ('Travel Speed', '5.5 km/h (high) / 3.5 km/h (low)'),
        ('Hydraulic System Pressure', '350 bar'),
        ('Fuel Tank Capacity', '400 L'),
        ('Hydraulic Tank Capacity', '215 L'),
        ('Undercarriage', 'Triple Grouser Track Shoes'),
        ('Track Width', '600 mm'),
        ('Ground Clearance', '450 mm'),
    ]
    
    for spec_name, spec_value in specs:
        EquipmentSpecification.objects.create(
            equipment=equipment,
            name=spec_name,
            value=spec_value
        )
        print(f"   ✅ Added spec: {spec_name} = {spec_value}")
    
    # Step 6: Note about images
    print("\n6️⃣  Equipment Images...")
    print("   ⚠️  Note: Image upload requires actual image files.")
    print("   📝 To add images, you can:")
    print("      1. Use Django Admin: http://localhost:8000/admin/equipment/equipmentimage/")
    print("      2. Upload via API endpoint")
    print("      3. Manually create EquipmentImage objects with image files")
    print("")
    print("   Example code to add images programmatically:")
    print("   ```python")
    print("   from equipment.models import EquipmentImage")
    print(f"   equipment = Equipment.objects.get(id={equipment.id})")
    print("   ")
    print("   EquipmentImage.objects.create(")
    print("       equipment=equipment,")
    print("       image='path/to/image.jpg',  # Upload to media/equipment_images/")
    print("       is_primary=True,")
    print("       display_order=1,")
    print("       caption='Front view of excavator'")
    print("   )")
    print("   ```")
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ SAMPLE LISTING CREATED SUCCESSFULLY!")
    print("=" * 60)
    print(f"\n📋 Equipment ID: {equipment.id}")
    print(f"📋 Equipment Name: {equipment.name}")
    print(f"📋 Category: {equipment.category.name}")
    print(f"📋 Seller: {equipment.seller_company.company_name}")
    print(f"📋 Status: {equipment.get_status_display()}")
    print(f"📋 Tags: {', '.join([tag.name for tag in equipment.tags.all()])}")
    print(f"📋 Specifications: {equipment.specifications.count()} specs added")
    print(f"\n🔗 View in admin: http://localhost:8000/admin/equipment/equipment/{equipment.id}/change/")
    print(f"🔗 API Endpoint: http://localhost:8000/api/equipment/{equipment.id}/")
    print("\n💡 Next Steps:")
    print("   1. Add images through Django Admin")
    print("   2. Test API endpoints")
    print("   3. Create more listings using this as a template")
    print("")

if __name__ == '__main__':
    try:
        create_sample_listing()
    except Exception as e:
        print(f"\n❌ Error creating sample listing: {e}")
        import traceback
        traceback.print_exc()
