# Adding Icons to Categories - Complete Guide

## 📊 Current Status

### ✅ What Was Created by `create_categories.py`:
- **10 Categories** with names, descriptions, and color codes
- **NO icons** - Icons are optional image files that need to be uploaded separately
- **NO company profile used** - Categories don't belong to companies (they're global/shared)

### 🎨 Category Icon Fields:
1. **`icon`** - Small icon (64x64px) for navigation, category cards
   - Stored in: `media/category_icons/`
   - Optional (blank=True, null=True)
   
2. **`promotional_image`** - Large banner (400x200px) for featured sections
   - Stored in: `media/category_promotions/`
   - Optional (blank=True, null=True)

---

## 🖼️ Equipment vs Category Icons

### Categories:
- ✅ Icons are **optional**
- ✅ Don't require company profile
- ✅ Shared globally across all users
- ✅ Used for UI/UX decoration

### Equipment Listings:
- ✅ Images are handled separately (max 7 per equipment)
- ✅ **Require company profile** (seller_company field)
- ✅ Stored in: `media/equipment_images/`

---

## 📝 Company Profile Used in `create_sample_listing.py`

The equipment script uses/creates:
```python
Company User Email: demo_company@tezrent.com
Password: DemoPassword123!
Company Name: TezRent Equipment Rentals LLC
License Number: CN-1234567
Tax Number: TAX-987654321
```

**This is ONLY for equipment listings, NOT categories!**

---

## 🎯 How to Add Icons to Categories

### Method 1: Django Admin (Easiest)

1. Go to: http://localhost:8000/admin/equipment/category/
2. Click on a category (e.g., "Excavators")
3. Scroll to "Icon" field
4. Click "Choose File" and upload your icon (64x64px PNG/JPG)
5. Optional: Upload "Promotional image" (400x200px)
6. Click "Save"

### Method 2: API Upload (Programmatic)

```bash
# Upload icon to a category
curl -X PATCH http://localhost:8000/api/equipment/categories/1/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "icon=@/path/to/excavator-icon.png"

# Upload promotional image
curl -X PATCH http://localhost:8000/api/equipment/categories/1/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "promotional_image=@/path/to/excavator-banner.jpg"
```

### Method 3: Python Script (Bulk Upload)

```python
import os
import django
from django.core.files import File

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from equipment.models import Category

# Example: Add icon to Excavators category
category = Category.objects.get(name='Excavators')

with open('/path/to/excavator-icon.png', 'rb') as icon_file:
    category.icon.save('excavator-icon.png', File(icon_file), save=True)

print(f"✅ Icon added to {category.name}")
print(f"   Icon URL: {category.icon_url}")
```

---

## 🎨 Recommended Icon Sizes

### Category Icons (64x64px)
- **Format**: PNG with transparency preferred
- **Size**: 64x64 pixels
- **File size**: < 50KB
- **Style**: Simple, recognizable symbols
- **Colors**: Match category color_code if possible

### Promotional Images (400x200px)
- **Format**: JPG or PNG
- **Size**: 400x200 pixels (2:1 ratio)
- **File size**: < 200KB
- **Style**: Professional, eye-catching
- **Content**: Equipment photo or branded graphic

---

## 📦 Sample Icon Sources

### Free Icon Resources:
1. **Font Awesome** - https://fontawesome.com/icons
2. **Flaticon** - https://www.flaticon.com/
3. **Icons8** - https://icons8.com/
4. **Noun Project** - https://thenounproject.com/

### Icon Ideas by Category:
- **Excavators**: 🚜 Digger/excavator symbol
- **Loaders**: 🏗️ Front loader symbol
- **Bulldozers**: 🚧 Bulldozer blade symbol
- **Cranes**: 🏗️ Tower crane symbol
- **Forklifts**: 📦 Forklift symbol
- **Compactors**: 🛣️ Road roller symbol
- **Generators**: ⚡ Lightning/power symbol
- **Aerial Lifts**: ⬆️ Scissor lift symbol
- **Concrete Equipment**: 🏗️ Cement mixer symbol
- **Dump Trucks**: 🚛 Dump truck symbol

---

## 🚀 Bulk Icon Upload Script

Here's a script to upload icons from a folder:

```python
"""
Bulk Category Icon Upload Script
Place icons in a folder with category names (e.g., excavators.png, loaders.png)
"""

import os
import django
from django.core.files import File

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from equipment.models import Category

def upload_category_icons(icons_folder):
    """
    Upload icons from a folder to categories
    File naming: category-name.png (e.g., excavators.png, loaders.png)
    """
    
    print("🖼️  Uploading Category Icons...")
    print("=" * 60)
    
    if not os.path.exists(icons_folder):
        print(f"❌ Folder not found: {icons_folder}")
        return
    
    categories = Category.objects.all()
    uploaded_count = 0
    
    for category in categories:
        # Try different file extensions
        icon_filename = None
        for ext in ['.png', '.jpg', '.jpeg', '.svg']:
            potential_file = os.path.join(
                icons_folder, 
                f"{category.slug}{ext}"
            )
            if os.path.exists(potential_file):
                icon_filename = potential_file
                break
        
        if icon_filename:
            with open(icon_filename, 'rb') as icon_file:
                category.icon.save(
                    os.path.basename(icon_filename), 
                    File(icon_file), 
                    save=True
                )
            print(f"✅ Uploaded icon for: {category.name}")
            print(f"   File: {os.path.basename(icon_filename)}")
            uploaded_count += 1
        else:
            print(f"⏭️  No icon found for: {category.name}")
            print(f"   Expected: {category.slug}.png or .jpg")
    
    print("\n" + "=" * 60)
    print(f"✅ Icon Upload Complete!")
    print(f"   Uploaded: {uploaded_count} icons")
    print(f"   Skipped: {categories.count() - uploaded_count} categories")
    print("\n🔗 View in admin: http://localhost:8000/admin/equipment/category/")
    print("")

if __name__ == '__main__':
    # Change this to your icons folder path
    ICONS_FOLDER = './category_icons'
    
    print("""
    📂 Place your icon files in: ./category_icons/
    
    File naming convention (use category slug):
    - excavators.png
    - loaders.png
    - bulldozers.png
    - cranes.png
    - forklifts.png
    - compactors.png
    - generators.png
    - aerial-lifts.png
    - concrete-equipment.png
    - dump-trucks.png
    
    Press Enter to continue or Ctrl+C to cancel...
    """)
    
    input()
    
    try:
        upload_category_icons(ICONS_FOLDER)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
```

---

## 🔍 Check Current Categories

### Via API:
```bash
curl http://localhost:8000/api/equipment/categories/
```

### Via Python:
```python
python manage.py shell

from equipment.models import Category

for cat in Category.objects.all():
    print(f"Category: {cat.name}")
    print(f"  - Slug: {cat.slug}")
    print(f"  - Color: {cat.color_code}")
    print(f"  - Icon: {cat.icon_url or 'None'}")
    print(f"  - Featured: {cat.is_featured}")
    print()
```

---

## ✅ Summary

### Categories (created by `create_categories.py`):
- ✅ 10 categories with text data
- ❌ NO icons (optional, need to upload separately)
- ❌ NO company profile (categories are global)
- 🎨 Have color codes for fallback styling

### Equipment (created by `create_sample_listing.py`):
- ✅ Uses company profile: `demo_company@tezrent.com`
- ✅ Belongs to: TezRent Equipment Rentals LLC
- 🖼️ Images handled separately (max 7 per equipment)

### To Add Icons:
1. **Easiest**: Upload via Django Admin
2. **API**: Use PATCH endpoint with FormData
3. **Bulk**: Use the bulk upload script above

Icons are **completely optional** - your categories work fine without them! The frontend can use the `color_code` as a fallback for styling. 🎨

---

**Need help creating icons?** I can guide you through designing or finding suitable icons for each category! 🎨
