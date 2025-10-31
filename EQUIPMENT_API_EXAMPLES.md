# Equipment API - Complete Examples

## Create Equipment - POST /api/equipment/equipment/

### Required Fields
- `name` - Equipment name (string)
- `description` - Equipment description (text)
- `daily_rate` - Daily rental rate (decimal)
- Either `category_id` OR `category_name` - Category selection

### Optional Fields
- `manufacturer` - Manufacturer name
- `model_number` - Model number
- `year` - Year of manufacture
- `weight` - Weight in kg
- `dimensions` - Dimensions (e.g., "10x5x3 meters")
- `fuel_type` - Fuel type (diesel, electric, etc.)
- `weekly_rate` - Weekly rental rate
- `monthly_rate` - Monthly rental rate
- `country` - Country where equipment is located
- `city` - City where equipment is located
- `status` - Equipment status (default: "available")
- `total_units` - Total units available (default: 1)
- `available_units` - Currently available units
- `featured` - Featured status (boolean)
- `tag_names` - Array of tag names (JSON array as string)
- `images` - Multiple image files (max 7)
- `specifications_data` - Equipment specifications (JSON array)

---

## Example 1: Minimal Equipment Creation

### JavaScript/React Native (FormData)
```javascript
const createEquipment = async () => {
  const formData = new FormData();
  
  // Required fields
  formData.append('name', 'Caterpillar 320 Excavator');
  formData.append('description', 'Heavy-duty excavator for construction and mining');
  formData.append('daily_rate', '500');
  formData.append('category_id', '1'); // OR use category_name instead
  
  const response = await fetch('http://127.0.0.1:8000/api/equipment/equipment/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`, // Required!
    },
    body: formData,
  });
  
  if (response.ok) {
    const data = await response.json();
    console.log('Equipment created:', data);
  } else {
    const error = await response.json();
    console.error('Error:', error);
  }
};
```

### cURL
```bash
curl -X POST http://127.0.0.1:8000/api/equipment/equipment/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "name=Caterpillar 320 Excavator" \
  -F "description=Heavy-duty excavator for construction and mining" \
  -F "daily_rate=500" \
  -F "category_id=1"
```

---

## Example 2: Complete Equipment with All Features

### JavaScript/React Native
```javascript
const createCompleteEquipment = async () => {
  const formData = new FormData();
  
  // Basic info
  formData.append('name', 'Caterpillar 320 Excavator');
  formData.append('description', 'Heavy-duty excavator for construction and mining. Perfect for large-scale projects.');
  formData.append('manufacturer', 'Caterpillar');
  formData.append('model_number', '320-GC');
  formData.append('year', '2023');
  
  // Pricing
  formData.append('daily_rate', '500');
  formData.append('weekly_rate', '3000');
  formData.append('monthly_rate', '10000');
  
  // Category
  formData.append('category_id', '1'); // Use existing category
  
  // Tags (as JSON string)
  const tags = ['Heavy Equipment', 'Construction', 'Mining', 'Excavation'];
  formData.append('tag_names', JSON.stringify(tags));
  
  // Physical specs
  formData.append('weight', '20000'); // kg
  formData.append('dimensions', '9.5m x 2.8m x 3.1m');
  formData.append('fuel_type', 'Diesel');
  
  // Location
  formData.append('country', 'USA');
  formData.append('city', 'New York');
  
  // Availability
  formData.append('total_units', '5');
  formData.append('available_units', '5');
  formData.append('status', 'available');
  formData.append('featured', 'true');
  
  // Specifications (as JSON string)
  const specs = [
    { name: 'Engine Power', value: '122 HP' },
    { name: 'Operating Weight', value: '20,000 kg' },
    { name: 'Bucket Capacity', value: '1.2 m³' },
    { name: 'Max Digging Depth', value: '6.5 m' },
  ];
  formData.append('specifications_data', JSON.stringify(specs));
  
  // Images (React Native with expo-image-picker)
  // Add multiple images
  const images = [
    {
      uri: 'file:///path/to/image1.jpg',
      type: 'image/jpeg',
      name: 'excavator1.jpg',
    },
    {
      uri: 'file:///path/to/image2.jpg',
      type: 'image/jpeg',
      name: 'excavator2.jpg',
    },
  ];
  
  images.forEach((image) => {
    formData.append('images', {
      uri: image.uri,
      type: image.type,
      name: image.name,
    });
  });
  
  const response = await fetch('http://127.0.0.1:8000/api/equipment/equipment/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      // Don't set Content-Type - let browser/fetch set it with boundary
    },
    body: formData,
  });
  
  if (response.ok) {
    const data = await response.json();
    console.log('Equipment created:', data);
  } else {
    const error = await response.json();
    console.error('Validation errors:', error);
  }
};
```

### React Web (with file input)
```javascript
const EquipmentForm = () => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    daily_rate: '',
    category_id: '',
  });
  const [images, setImages] = useState([]);
  const [tags, setTags] = useState([]);

  const handleImageChange = (e) => {
    setImages(Array.from(e.target.files));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const data = new FormData();
    
    // Add all text fields
    Object.keys(formData).forEach(key => {
      data.append(key, formData[key]);
    });
    
    // Add tags
    if (tags.length > 0) {
      data.append('tag_names', JSON.stringify(tags));
    }
    
    // Add images
    images.forEach(image => {
      data.append('images', image);
    });
    
    try {
      const response = await fetch('http://127.0.0.1:8000/api/equipment/equipment/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
        },
        body: data,
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log('Success:', result);
        alert('Equipment created successfully!');
      } else {
        const error = await response.json();
        console.error('Error:', error);
        alert(`Error: ${JSON.stringify(error)}`);
      }
    } catch (error) {
      console.error('Network error:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Equipment Name"
        value={formData.name}
        onChange={(e) => setFormData({...formData, name: e.target.value})}
        required
      />
      
      <textarea
        placeholder="Description"
        value={formData.description}
        onChange={(e) => setFormData({...formData, description: e.target.value})}
        required
      />
      
      <input
        type="number"
        placeholder="Daily Rate"
        value={formData.daily_rate}
        onChange={(e) => setFormData({...formData, daily_rate: e.target.value})}
        required
      />
      
      <input
        type="number"
        placeholder="Category ID"
        value={formData.category_id}
        onChange={(e) => setFormData({...formData, category_id: e.target.value})}
        required
      />
      
      <input
        type="file"
        multiple
        accept="image/*"
        onChange={handleImageChange}
        max="7"
      />
      
      <button type="submit">Create Equipment</button>
    </form>
  );
};
```

---

## Example 3: Using Category Name Instead of ID

```javascript
const formData = new FormData();

formData.append('name', 'John Deere Tractor');
formData.append('description', 'Reliable farming tractor');
formData.append('daily_rate', '300');

// Use category_name instead of category_id
// Backend will create category if it doesn't exist
formData.append('category_name', 'Tractors');

const response = await fetch('http://127.0.0.1:8000/api/equipment/equipment/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
  },
  body: formData,
});
```

---

## Common Errors and Solutions

### 1. **400 Bad Request - Missing Required Fields**

**Error:**
```json
{
  "name": ["This field is required."],
  "description": ["This field is required."],
  "daily_rate": ["This field is required."]
}
```

**Solution:** Make sure you're sending all required fields:
- `name`
- `description`
- `daily_rate`
- `category_id` OR `category_name`

---

### 2. **400 Bad Request - No Company Profile**

**Error:**
```json
{
  "error": "Only companies can list equipment. Please complete your company profile first."
}
```

**Solution:** User must create a company profile first. See CRM documentation.

---

### 3. **401 Unauthorized**

**Error:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Solution:** Add Authorization header:
```javascript
headers: {
  'Authorization': `Bearer ${accessToken}`,
}
```

---

### 4. **400 Bad Request - Category Error**

**Error:**
```json
{
  "non_field_errors": ["Either category_id or category_name must be provided"]
}
```

**Solution:** Provide either:
```javascript
formData.append('category_id', '1'); // Use existing category
// OR
formData.append('category_name', 'Excavators'); // Create/use by name
```

---

### 5. **400 Bad Request - Too Many Images**

**Error:**
```json
{
  "images": "Maximum 7 images allowed per equipment"
}
```

**Solution:** Limit images to 7 or fewer.

---

### 6. **400 Bad Request - Invalid Tag Format**

**Error:**
```json
{
  "tag_names": ["This field must be a list."]
}
```

**Solution:** Tags must be sent as JSON string:
```javascript
// ✅ CORRECT
formData.append('tag_names', JSON.stringify(['Construction', 'Mining']));

// ❌ WRONG
formData.append('tag_names', 'Construction, Mining');
```

---

## Testing with cURL

### Minimal Test
```bash
# Get your access token first
ACCESS_TOKEN="your_token_here"

# Create minimal equipment
curl -X POST http://127.0.0.1:8000/api/equipment/equipment/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -F "name=Test Excavator" \
  -F "description=Test description" \
  -F "daily_rate=500" \
  -F "category_id=1"
```

### With Tags
```bash
curl -X POST http://127.0.0.1:8000/api/equipment/equipment/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -F "name=Test Excavator" \
  -F "description=Test description" \
  -F "daily_rate=500" \
  -F "category_id=1" \
  -F 'tag_names=["Construction","Mining"]'
```

### With Images
```bash
curl -X POST http://127.0.0.1:8000/api/equipment/equipment/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -F "name=Test Excavator" \
  -F "description=Test description" \
  -F "daily_rate=500" \
  -F "category_id=1" \
  -F "images=@/path/to/image1.jpg" \
  -F "images=@/path/to/image2.jpg"
```

---

## Response Format

### Success Response (201 Created)
```json
{
  "id": 1,
  "name": "Caterpillar 320 Excavator",
  "description": "Heavy-duty excavator for construction and mining",
  "manufacturer": "Caterpillar",
  "model_number": "320-GC",
  "year": 2023,
  "weight": "20000.00",
  "dimensions": "9.5m x 2.8m x 3.1m",
  "fuel_type": "Diesel",
  "daily_rate": "500.00",
  "weekly_rate": "3000.00",
  "monthly_rate": "10000.00",
  "country": "USA",
  "city": "New York",
  "status": "available",
  "total_units": 5,
  "available_units": 5,
  "featured": true,
  "category": {
    "id": 1,
    "name": "Excavators",
    "description": "Heavy excavation equipment",
    "icon_url": "http://127.0.0.1:8000/media/category_icons/excavator.png"
  },
  "tags": [
    {"id": 1, "name": "Heavy Equipment"},
    {"id": 2, "name": "Construction"},
    {"id": 3, "name": "Mining"},
    {"id": 4, "name": "Excavation"}
  ],
  "images": [
    {
      "id": 1,
      "image_url": "http://127.0.0.1:8000/media/equipment/excavator1.jpg",
      "thumbnail_url": "http://127.0.0.1:8000/media/equipment/thumbnails/excavator1.jpg",
      "is_primary": true,
      "display_order": 1,
      "caption": "Image 1 for Caterpillar 320 Excavator"
    }
  ],
  "specifications": [
    {"id": 1, "name": "Engine Power", "value": "122 HP"},
    {"id": 2, "name": "Operating Weight", "value": "20,000 kg"}
  ],
  "created_at": "2025-10-24T06:26:42.123456Z",
  "updated_at": "2025-10-24T06:26:42.123456Z"
}
```

---

## Quick Checklist

Before sending POST request, verify:

✅ **Authentication**
- [ ] Access token is valid
- [ ] Authorization header is included

✅ **Required Fields**
- [ ] `name` is provided
- [ ] `description` is provided
- [ ] `daily_rate` is provided
- [ ] Either `category_id` OR `category_name` is provided

✅ **Optional Fields** (if using)
- [ ] `tag_names` is JSON array string
- [ ] `specifications_data` is JSON array string
- [ ] Images are 7 or fewer
- [ ] Numeric fields are valid numbers

✅ **Company Profile**
- [ ] User has completed company profile (check via `/api/crm/company-profile/`)

---

## Need Help?

If you're still getting 400 errors:

1. **Check the response body** - It will tell you exactly what's wrong
2. **Check Django console** - Server logs show detailed validation errors
3. **Test with minimal data first** - Just name, description, daily_rate, category_id
4. **Verify company profile exists** - GET `/api/crm/company-profile/`
5. **Check your access token** - Make sure it's valid and not expired

**Endpoint:** `POST http://127.0.0.1:8000/api/equipment/equipment/`

**This is the correct endpoint!** ✅
