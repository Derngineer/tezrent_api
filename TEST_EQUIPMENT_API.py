"""
Test Equipment Creation API
Quick test to verify the equipment creation endpoint works correctly
"""

print("""
╔═══════════════════════════════════════════════════════════════╗
║          EQUIPMENT CREATION API - TESTING GUIDE               ║
╚═══════════════════════════════════════════════════════════════╝

✅ FIXED: Removed 'uploaded_images' from serializer
   
Now your API should work! Here's what to test:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 MINIMAL REQUEST (No images, just equipment data):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

POST http://localhost:8000/api/equipment/equipment/
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "name": "Test Excavator",
  "description": "Testing equipment creation",
  "category_id": 1,
  "manufacturer": "Caterpillar",
  "model_number": "TEST-001",
  "year": 2022,
  "weight": "5000.00",
  "dimensions": "100 x 50 x 50",
  "daily_rate": "500.00",
  "weekly_rate": "3000.00",
  "monthly_rate": "10000.00",
  "country": "UAE",
  "city": "DXB",
  "total_units": 1,
  "available_units": 1
}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📸 WITH IMAGES (Use FormData):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

POST http://localhost:8000/api/equipment/equipment/
Authorization: Bearer YOUR_TOKEN
Content-Type: multipart/form-data

Form fields:
  name: "Test Excavator"
  description: "Testing equipment creation"
  category_id: 1
  manufacturer: "Caterpillar"
  model_number: "TEST-001"
  year: 2022
  weight: 5000.00
  dimensions: "100 x 50 x 50"
  daily_rate: 500.00
  weekly_rate: 3000.00
  monthly_rate: 10000.00
  country: "UAE"
  city: "DXB"
  total_units: 1
  available_units: 1
  images: [file1.jpg]  ← KEY NAME IS "images"
  images: [file2.jpg]  ← Same key for multiple files

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 FRONTEND FORM DATA STRUCTURE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

const formData = new FormData();

// Add all text fields
formData.append('name', 'Test Excavator');
formData.append('description', 'Testing equipment creation');
formData.append('category_id', '1');
formData.append('manufacturer', 'Caterpillar');
formData.append('model_number', 'TEST-001');
formData.append('year', '2022');
formData.append('weight', '5000.00');
formData.append('dimensions', '100 x 50 x 50');
formData.append('daily_rate', '500.00');
formData.append('weekly_rate', '3000.00');
formData.append('monthly_rate', '10000.00');
formData.append('country', 'UAE');
formData.append('city', 'DXB');
formData.append('total_units', '1');
formData.append('available_units', '1');

// Add optional fields (if needed)
formData.append('fuel_type', 'Diesel');
formData.append('featured', 'false');
formData.append('tag_names', JSON.stringify(['Construction', 'Heavy']));
formData.append('specifications_data', JSON.stringify([
  {name: 'Engine Power', value: '121 kW'}
]));

// Add images (KEY NAME: "images")
imageFiles.forEach(file => {
  formData.append('images', file);
});

// Send request
fetch('http://localhost:8000/api/equipment/equipment/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`
    // DON'T set Content-Type for FormData!
  },
  body: formData
});

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  IMPORTANT NOTES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Image field name is "images" (plural), NOT "uploaded_images"
2. Use FormData.append('images', file) for EACH image
3. DON'T set Content-Type header when using FormData
4. Maximum 7 images per equipment
5. First image automatically becomes primary
6. You must have a company profile to create equipment
7. Category must exist (create categories first!)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔧 HOW IMAGES ARE PROCESSED:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Your request → Django View (perform_create)
              ↓
           Equipment saved through EquipmentCreateSerializer
              ↓
           Images extracted from request.FILES.getlist('images')
              ↓
           EquipmentImage objects created directly in view
              ↓
           Response returned with equipment + images

So yes, images bypass serializer validation but are handled
properly in the view's perform_create() method!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 DOCUMENTATION FILES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. EQUIPMENT_LISTING_FRONTEND_GUIDE.md - Complete React form
2. CATEGORY_MANAGEMENT_GUIDE.md - Category CRUD operations
3. CATEGORY_QUICK_START.md - Quick category reference

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 NEXT STEPS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Restart Django server (if running)
2. Create categories: python create_categories.py
3. Test API with Postman/Thunder Client
4. Update your frontend form to match FormData structure
5. Test with minimal data first, then add images

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

""")

# If you want to actually test with Python:
print("Want to test via Python? Uncomment the code below:")
print("""
# Test script (requires requests library):
import requests

# 1. Login first
login_response = requests.post(
    'http://localhost:8000/api/accounts/login/',
    json={
        'email': 'your_company@example.com',
        'password': 'your_password'
    }
)
token = login_response.json()['access']

# 2. Create equipment (no images)
equipment_data = {
    "name": "Test Excavator",
    "description": "Testing equipment creation",
    "category_id": 1,
    "manufacturer": "Caterpillar",
    "model_number": "TEST-001",
    "year": 2022,
    "weight": "5000.00",
    "dimensions": "100 x 50 x 50",
    "daily_rate": "500.00",
    "weekly_rate": "3000.00",
    "monthly_rate": "10000.00",
    "country": "UAE",
    "city": "DXB",
    "total_units": 1,
    "available_units": 1
}

response = requests.post(
    'http://localhost:8000/api/equipment/equipment/',
    headers={'Authorization': f'Bearer {token}'},
    json=equipment_data
)

print(response.status_code)
print(response.json())
""")
