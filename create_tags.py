#!/usr/bin/env python
"""
Script to create sample tags for equipment
Run: python create_tags.py
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from equipment.models import Tag

def create_tags():
    """Create 5 sample tags"""
    
    tags_to_create = [
        'Heavy Equipment',
        'Construction',
        'Mining',
        'Excavation',
        'Hydraulic',
    ]
    
    print("Creating sample tags...\n")
    
    created_count = 0
    existing_count = 0
    
    for tag_name in tags_to_create:
        tag, created = Tag.objects.get_or_create(name=tag_name)
        
        if created:
            print(f"✅ Created tag: {tag.name} (ID: {tag.id})")
            created_count += 1
        else:
            print(f"ℹ️  Tag already exists: {tag.name} (ID: {tag.id})")
            existing_count += 1
    
    print(f"\n{'='*50}")
    print(f"Summary:")
    print(f"  - New tags created: {created_count}")
    print(f"  - Existing tags: {existing_count}")
    print(f"  - Total tags in database: {Tag.objects.count()}")
    print(f"{'='*50}\n")
    
    # List all tags
    print("All tags in database:")
    for tag in Tag.objects.all():
        equipment_count = tag.equipment.count()
        print(f"  - {tag.name} (ID: {tag.id}) - Used by {equipment_count} equipment")

if __name__ == '__main__':
    create_tags()
