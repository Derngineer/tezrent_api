"""
Quick Category Setup Script
Creates essential equipment categories for TezRent

Usage:
    python create_categories.py
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from equipment.models import Category

def create_categories():
    """Create essential equipment categories"""
    
    print("🏗️  Creating Equipment Categories...")
    print("=" * 60)
    
    categories_data = [
        {
            'name': 'Excavators',
            'description': 'Heavy-duty hydraulic excavators for construction, demolition, and mining projects. Available in various sizes from mini to large excavators.',
            'is_featured': True,
            'display_order': 1,
            'color_code': '#FF6B35'
        },
        {
            'name': 'Loaders',
            'description': 'Wheel loaders and backhoe loaders for material handling, loading trucks, and general construction work.',
            'is_featured': True,
            'display_order': 2,
            'color_code': '#FFD700'
        },
        {
            'name': 'Bulldozers',
            'description': 'Powerful track-type dozers for earthmoving, land clearing, and heavy pushing operations.',
            'is_featured': True,
            'display_order': 3,
            'color_code': '#FF4500'
        },
        {
            'name': 'Cranes',
            'description': 'Mobile cranes, tower cranes, and rough terrain cranes for lifting and hoisting heavy materials.',
            'is_featured': True,
            'display_order': 4,
            'color_code': '#1E90FF'
        },
        {
            'name': 'Forklifts',
            'description': 'Industrial forklifts and material handling equipment for warehouses and construction sites.',
            'is_featured': True,
            'display_order': 5,
            'color_code': '#32CD32'
        },
        {
            'name': 'Compactors',
            'description': 'Road rollers and soil compactors for asphalt paving and soil compaction work.',
            'is_featured': True,
            'display_order': 6,
            'color_code': '#8B4513'
        },
        {
            'name': 'Generators',
            'description': 'Diesel and gas generators for temporary or backup power supply on construction sites.',
            'is_featured': False,
            'display_order': 7,
            'color_code': '#DC143C'
        },
        {
            'name': 'Aerial Lifts',
            'description': 'Boom lifts, scissor lifts, and cherry pickers for working at height safely.',
            'is_featured': False,
            'display_order': 8,
            'color_code': '#9370DB'
        },
        {
            'name': 'Concrete Equipment',
            'description': 'Concrete mixers, pumps, and related equipment for concrete work.',
            'is_featured': False,
            'display_order': 9,
            'color_code': '#696969'
        },
        {
            'name': 'Dump Trucks',
            'description': 'Heavy-duty dump trucks and tipper trucks for hauling materials.',
            'is_featured': False,
            'display_order': 10,
            'color_code': '#FF8C00'
        }
    ]
    
    created_count = 0
    existing_count = 0
    
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={
                'description': cat_data['description'],
                'is_featured': cat_data['is_featured'],
                'display_order': cat_data['display_order'],
                'color_code': cat_data['color_code']
            }
        )
        
        if created:
            created_count += 1
            print(f"✅ Created: {category.name}")
            print(f"   - Featured: {category.is_featured}")
            print(f"   - Color: {category.color_code}")
            print(f"   - Order: {category.display_order}")
        else:
            existing_count += 1
            print(f"⏭️  Already exists: {category.name}")
    
    print("\n" + "=" * 60)
    print(f"✅ Category Setup Complete!")
    print(f"   Created: {created_count} new categories")
    print(f"   Existing: {existing_count} categories")
    print(f"   Total: {Category.objects.count()} categories in database")
    print("\n🔗 View categories:")
    print("   Admin: http://localhost:8000/admin/equipment/category/")
    print("   API: http://localhost:8000/api/equipment/categories/")
    print("\n💡 Next steps:")
    print("   1. Upload icons for each category (optional)")
    print("   2. Start creating equipment listings")
    print("   3. Assign equipment to these categories")
    print("")

if __name__ == '__main__':
    try:
        create_categories()
    except Exception as e:
        print(f"\n❌ Error creating categories: {e}")
        import traceback
        traceback.print_exc()
