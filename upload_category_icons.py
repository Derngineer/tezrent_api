"""
Bulk Category Icon Upload Script
Uploads icons from a folder to categories based on filename matching

Usage:
    1. Create a folder: ./category_icons/
    2. Add icon files named after category slugs (e.g., excavators.png, loaders.png)
    3. Run: python upload_category_icons.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.files import File
from equipment.models import Category

def upload_category_icons(icons_folder):
    """
    Upload icons from a folder to categories
    File naming: category-slug.png (e.g., excavators.png, loaders.png)
    """
    
    print("🖼️  Uploading Category Icons...")
    print("=" * 60)
    
    if not os.path.exists(icons_folder):
        print(f"❌ Folder not found: {icons_folder}")
        print(f"   Creating folder: {icons_folder}")
        os.makedirs(icons_folder)
        print(f"   ✅ Folder created. Please add icon files and run again.")
        return
    
    categories = Category.objects.all()
    
    if not categories.exists():
        print("❌ No categories found in database.")
        print("   Run: python create_categories.py first")
        return
    
    uploaded_count = 0
    skipped_count = 0
    
    print(f"\nSearching for icons in: {os.path.abspath(icons_folder)}\n")
    
    for category in categories:
        # Try different file extensions
        icon_filename = None
        for ext in ['.png', '.jpg', '.jpeg', '.svg', '.webp']:
            # Try exact slug match
            potential_file = os.path.join(icons_folder, f"{category.slug}{ext}")
            
            if os.path.exists(potential_file):
                icon_filename = potential_file
                break
            
            # Also try lowercase name without spaces
            alt_name = category.name.lower().replace(' ', '-')
            potential_file = os.path.join(icons_folder, f"{alt_name}{ext}")
            
            if os.path.exists(potential_file):
                icon_filename = potential_file
                break
        
        if icon_filename:
            try:
                with open(icon_filename, 'rb') as icon_file:
                    category.icon.save(
                        os.path.basename(icon_filename), 
                        File(icon_file), 
                        save=True
                    )
                print(f"✅ Uploaded icon for: {category.name}")
                print(f"   File: {os.path.basename(icon_filename)}")
                print(f"   URL: {category.icon_url}")
                uploaded_count += 1
            except Exception as e:
                print(f"❌ Error uploading icon for {category.name}: {e}")
                skipped_count += 1
        else:
            print(f"⏭️  No icon found for: {category.name}")
            print(f"   Expected filename: {category.slug}.png (or .jpg, .jpeg, .svg)")
            skipped_count += 1
    
    print("\n" + "=" * 60)
    print(f"✅ Icon Upload Complete!")
    print(f"   Uploaded: {uploaded_count} icons")
    print(f"   Skipped: {skipped_count} categories")
    print(f"   Total Categories: {categories.count()}")
    
    if uploaded_count > 0:
        print("\n🔗 View categories with icons:")
        print("   Admin: http://localhost:8000/admin/equipment/category/")
        print("   API: http://localhost:8000/api/equipment/categories/")
    
    if skipped_count > 0:
        print("\n📝 Missing icons for:")
        for category in categories:
            if not category.icon:
                print(f"   - {category.name} → {category.slug}.png")
    
    print("")

def show_instructions():
    """Show setup instructions"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║          CATEGORY ICON UPLOAD - INSTRUCTIONS                  ║
╚═══════════════════════════════════════════════════════════════╝

📂 Step 1: Create Icons Folder
   Create a folder named 'category_icons' in this directory

📁 Step 2: Add Icon Files
   Name your icon files after category slugs:
   
   Required Filenames:
   ├── excavators.png (or .jpg, .jpeg, .svg)
   ├── loaders.png
   ├── bulldozers.png
   ├── cranes.png
   ├── forklifts.png
   ├── compactors.png
   ├── generators.png
   ├── aerial-lifts.png
   ├── concrete-equipment.png
   └── dump-trucks.png

📐 Recommended Icon Specs:
   - Size: 64x64 pixels
   - Format: PNG with transparency (preferred) or JPG
   - File size: < 50KB
   - Style: Simple, clear, recognizable

🎨 Where to Get Icons:
   - Font Awesome: https://fontawesome.com/icons
   - Flaticon: https://www.flaticon.com/
   - Icons8: https://icons8.com/
   - Noun Project: https://thenounproject.com/

🚀 Step 3: Run This Script
   python upload_category_icons.py

═══════════════════════════════════════════════════════════════

""")

if __name__ == '__main__':
    ICONS_FOLDER = './category_icons'
    
    show_instructions()
    
    # Check if categories exist
    try:
        from equipment.models import Category
        if not Category.objects.exists():
            print("⚠️  No categories found in database!")
            print("   Run this first: python create_categories.py\n")
            exit(1)
    except Exception as e:
        print(f"❌ Error checking categories: {e}\n")
        exit(1)
    
    # Check if folder exists
    if not os.path.exists(ICONS_FOLDER):
        print(f"📂 Creating icons folder: {ICONS_FOLDER}")
        os.makedirs(ICONS_FOLDER)
        print(f"✅ Folder created!\n")
        print("📝 Next steps:")
        print("   1. Add your icon files to ./category_icons/")
        print("   2. Run this script again\n")
        exit(0)
    
    # Check if folder has any image files
    image_extensions = ('.png', '.jpg', '.jpeg', '.svg', '.webp')
    icon_files = [f for f in os.listdir(ICONS_FOLDER) if f.lower().endswith(image_extensions)]
    
    if not icon_files:
        print(f"⚠️  No icon files found in {ICONS_FOLDER}/")
        print(f"   Add icon files and run again.\n")
        exit(0)
    
    print(f"📊 Found {len(icon_files)} icon file(s) in {ICONS_FOLDER}/")
    print("   Files:", ", ".join(icon_files))
    print("\nPress Enter to start uploading or Ctrl+C to cancel...")
    
    try:
        input()
        upload_category_icons(ICONS_FOLDER)
    except KeyboardInterrupt:
        print("\n\n❌ Upload cancelled by user.\n")
        exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
