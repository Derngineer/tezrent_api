# Equipment Listing - Frontend Integration Guide

## 📋 Required Fields for Creating Equipment

### Minimum Required Fields
```javascript
{
  // Basic Information (REQUIRED)
  "name": "Caterpillar 320D2 Excavator",
  "description": "Heavy-duty hydraulic excavator...",
  
  // Category (REQUIRED - choose one method)
  "category_id": 1,  // Use existing category ID
  // OR
  "category_name": "Excavators",  // Create new category
  
  // Technical Specs (REQUIRED)
  "manufacturer": "Caterpillar",
  "model_number": "320D2 L",
  "year": 2022,
  "weight": "22500.00",  // in kg
  "dimensions": "996 x 294 x 323",  // LxWxH in cm
  
  // Pricing (REQUIRED)
  "daily_rate": "1500.00",
  "weekly_rate": "9000.00",
  "monthly_rate": "32000.00",
  
  // Location (REQUIRED)
  "country": "UAE",  // or "UZB"
  "city": "DXB",     // Use city codes: DXB, AUH, SHJ, etc.
  
  // Availability (REQUIRED)
  "total_units": 3,
  "available_units": 3
}
```

### Optional Fields
```javascript
{
  "fuel_type": "Diesel",
  "status": "available",  // default: 'available'
  "featured": false,      // default: false
  
  // Tags (optional)
  "tag_names": ["Heavy Equipment", "Construction", "Hydraulic"],
  
  // Specifications (optional)
  "specifications_data": [
    {"name": "Engine Power", "value": "121 kW"},
    {"name": "Bucket Capacity", "value": "1.0 m³"}
  ],
  
  // Promotional (optional)
  "is_todays_deal": false,
  "deal_discount_percentage": 0,
  "promotion_badge": "HOT DEAL"
}
```

---

## 🖼️ Image Upload Handling

Images are handled **separately** in the view using `request.FILES.getlist('images')`.

### Important Notes:
- ✅ Maximum **7 images** per equipment
- ✅ First image automatically becomes **primary image**
- ✅ Images must be sent as **FormData** (multipart/form-data)
- ✅ Use the key name `"images"` for all image files

---

## 🚀 Frontend Implementation

### React - Complete Form Example

```jsx
import React, { useState, useEffect } from 'react';

const CreateEquipmentForm = () => {
  const [categories, setCategories] = useState([]);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    category_id: '',
    manufacturer: '',
    model_number: '',
    year: new Date().getFullYear(),
    weight: '',
    dimensions: '',
    fuel_type: 'Diesel',
    daily_rate: '',
    weekly_rate: '',
    monthly_rate: '',
    country: 'UAE',
    city: 'DXB',
    total_units: 1,
    available_units: 1,
    featured: false,
    tag_names: [],
    specifications_data: []
  });
  const [images, setImages] = useState([]);
  const [tagInput, setTagInput] = useState('');

  // Fetch categories on mount
  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    const response = await fetch('http://localhost:8000/api/equipment/categories/choices/');
    const data = await response.json();
    setCategories(data.categories);
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  const handleImageChange = (e) => {
    const files = Array.from(e.target.files);
    if (files.length > 7) {
      alert('Maximum 7 images allowed!');
      return;
    }
    setImages(files);
  };

  const addTag = () => {
    if (tagInput.trim() && !formData.tag_names.includes(tagInput.trim())) {
      setFormData({
        ...formData,
        tag_names: [...formData.tag_names, tagInput.trim()]
      });
      setTagInput('');
    }
  };

  const removeTag = (tagToRemove) => {
    setFormData({
      ...formData,
      tag_names: formData.tag_names.filter(tag => tag !== tagToRemove)
    });
  };

  const addSpecification = () => {
    setFormData({
      ...formData,
      specifications_data: [
        ...formData.specifications_data,
        { name: '', value: '' }
      ]
    });
  };

  const updateSpecification = (index, field, value) => {
    const newSpecs = [...formData.specifications_data];
    newSpecs[index][field] = value;
    setFormData({
      ...formData,
      specifications_data: newSpecs
    });
  };

  const removeSpecification = (index) => {
    setFormData({
      ...formData,
      specifications_data: formData.specifications_data.filter((_, i) => i !== index)
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Create FormData object
    const data = new FormData();

    // Append all text fields
    Object.keys(formData).forEach(key => {
      if (key === 'tag_names') {
        // Send as JSON array
        data.append(key, JSON.stringify(formData[key]));
      } else if (key === 'specifications_data') {
        // Send as JSON array
        data.append(key, JSON.stringify(formData[key]));
      } else if (typeof formData[key] === 'boolean') {
        data.append(key, formData[key]);
      } else if (formData[key] !== '') {
        data.append(key, formData[key]);
      }
    });

    // Append images
    images.forEach((image) => {
      data.append('images', image);
    });

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/api/equipment/equipment/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: data // Don't set Content-Type, let browser handle it
      });

      if (response.ok) {
        const equipment = await response.json();
        alert('Equipment created successfully!');
        console.log('Created equipment:', equipment);
        // Reset form or redirect
      } else {
        const error = await response.json();
        console.error('Error:', error);
        alert(`Error: ${JSON.stringify(error)}`);
      }
    } catch (error) {
      console.error('Network error:', error);
      alert('Failed to create equipment. Check console for details.');
    }
  };

  return (
    <form onSubmit={handleSubmit} encType="multipart/form-data">
      <h2>Create Equipment Listing</h2>

      {/* Basic Information */}
      <section>
        <h3>Basic Information</h3>
        
        <label>
          Equipment Name *
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleInputChange}
            required
            placeholder="e.g., Caterpillar 320D2 Excavator"
          />
        </label>

        <label>
          Description *
          <textarea
            name="description"
            value={formData.description}
            onChange={handleInputChange}
            required
            rows="5"
            placeholder="Detailed description of the equipment..."
          />
        </label>

        <label>
          Category *
          <select
            name="category_id"
            value={formData.category_id}
            onChange={handleInputChange}
            required
          >
            <option value="">Select Category</option>
            {categories.map(cat => (
              <option key={cat.id} value={cat.id}>
                {cat.name}
              </option>
            ))}
          </select>
        </label>
      </section>

      {/* Technical Specifications */}
      <section>
        <h3>Technical Details</h3>
        
        <label>
          Manufacturer *
          <input
            type="text"
            name="manufacturer"
            value={formData.manufacturer}
            onChange={handleInputChange}
            required
            placeholder="e.g., Caterpillar"
          />
        </label>

        <label>
          Model Number *
          <input
            type="text"
            name="model_number"
            value={formData.model_number}
            onChange={handleInputChange}
            required
            placeholder="e.g., 320D2 L"
          />
        </label>

        <label>
          Year *
          <input
            type="number"
            name="year"
            value={formData.year}
            onChange={handleInputChange}
            required
            min="1980"
            max={new Date().getFullYear() + 1}
          />
        </label>

        <label>
          Weight (kg) *
          <input
            type="number"
            step="0.01"
            name="weight"
            value={formData.weight}
            onChange={handleInputChange}
            required
            placeholder="e.g., 22500"
          />
        </label>

        <label>
          Dimensions (LxWxH in cm) *
          <input
            type="text"
            name="dimensions"
            value={formData.dimensions}
            onChange={handleInputChange}
            required
            placeholder="e.g., 996 x 294 x 323"
          />
        </label>

        <label>
          Fuel Type
          <select name="fuel_type" value={formData.fuel_type} onChange={handleInputChange}>
            <option value="Diesel">Diesel</option>
            <option value="Gasoline">Gasoline</option>
            <option value="Electric">Electric</option>
            <option value="Hybrid">Hybrid</option>
          </select>
        </label>
      </section>

      {/* Pricing */}
      <section>
        <h3>Pricing</h3>
        
        <label>
          Daily Rate (AED) *
          <input
            type="number"
            step="0.01"
            name="daily_rate"
            value={formData.daily_rate}
            onChange={handleInputChange}
            required
            placeholder="e.g., 1500.00"
          />
        </label>

        <label>
          Weekly Rate (AED) *
          <input
            type="number"
            step="0.01"
            name="weekly_rate"
            value={formData.weekly_rate}
            onChange={handleInputChange}
            required
            placeholder="e.g., 9000.00"
          />
        </label>

        <label>
          Monthly Rate (AED) *
          <input
            type="number"
            step="0.01"
            name="monthly_rate"
            value={formData.monthly_rate}
            onChange={handleInputChange}
            required
            placeholder="e.g., 32000.00"
          />
        </label>
      </section>

      {/* Location */}
      <section>
        <h3>Location</h3>
        
        <label>
          Country *
          <select name="country" value={formData.country} onChange={handleInputChange} required>
            <option value="UAE">United Arab Emirates</option>
            <option value="UZB">Uzbekistan</option>
          </select>
        </label>

        <label>
          City *
          <select name="city" value={formData.city} onChange={handleInputChange} required>
            {formData.country === 'UAE' ? (
              <>
                <option value="DXB">Dubai</option>
                <option value="AUH">Abu Dhabi</option>
                <option value="SHJ">Sharjah</option>
                <option value="AJM">Ajman</option>
                <option value="UAQ">Umm Al Quwain</option>
                <option value="FUJ">Fujairah</option>
                <option value="RAK">Ras Al Khaimah</option>
              </>
            ) : (
              <>
                <option value="TAS">Tashkent</option>
                <option value="SAM">Samarkand</option>
                <option value="NAM">Namangan</option>
                <option value="AND">Andijan</option>
              </>
            )}
          </select>
        </label>
      </section>

      {/* Availability */}
      <section>
        <h3>Availability</h3>
        
        <label>
          Total Units *
          <input
            type="number"
            name="total_units"
            value={formData.total_units}
            onChange={handleInputChange}
            required
            min="1"
          />
        </label>

        <label>
          Available Units *
          <input
            type="number"
            name="available_units"
            value={formData.available_units}
            onChange={handleInputChange}
            required
            min="0"
            max={formData.total_units}
          />
        </label>

        <label>
          <input
            type="checkbox"
            name="featured"
            checked={formData.featured}
            onChange={handleInputChange}
          />
          Featured Equipment
        </label>
      </section>

      {/* Images */}
      <section>
        <h3>Images (Max 7)</h3>
        <input
          type="file"
          accept="image/*"
          multiple
          onChange={handleImageChange}
          max="7"
        />
        <p>Selected: {images.length} image(s)</p>
        {images.length > 0 && (
          <ul>
            {images.map((img, idx) => (
              <li key={idx}>{img.name} {idx === 0 && '(Primary)'}</li>
            ))}
          </ul>
        )}
      </section>

      {/* Tags */}
      <section>
        <h3>Tags</h3>
        <div>
          <input
            type="text"
            value={tagInput}
            onChange={(e) => setTagInput(e.target.value)}
            placeholder="Add tag"
            onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
          />
          <button type="button" onClick={addTag}>Add Tag</button>
        </div>
        <div>
          {formData.tag_names.map(tag => (
            <span key={tag} style={{ margin: '5px', padding: '5px', background: '#ddd' }}>
              {tag}
              <button type="button" onClick={() => removeTag(tag)}>×</button>
            </span>
          ))}
        </div>
      </section>

      {/* Specifications */}
      <section>
        <h3>Specifications</h3>
        <button type="button" onClick={addSpecification}>+ Add Specification</button>
        {formData.specifications_data.map((spec, index) => (
          <div key={index} style={{ margin: '10px 0' }}>
            <input
              type="text"
              placeholder="Name (e.g., Engine Power)"
              value={spec.name}
              onChange={(e) => updateSpecification(index, 'name', e.target.value)}
            />
            <input
              type="text"
              placeholder="Value (e.g., 121 kW)"
              value={spec.value}
              onChange={(e) => updateSpecification(index, 'value', e.target.value)}
            />
            <button type="button" onClick={() => removeSpecification(index)}>Remove</button>
          </div>
        ))}
      </section>

      <button type="submit">Create Equipment</button>
    </form>
  );
};

export default CreateEquipmentForm;
```

---

## 🔍 Common Issues & Solutions

### Issue 1: "uploaded_images is not valid for model Equipment"
**Solution:** ✅ FIXED - Removed `uploaded_images` from serializer fields

### Issue 2: Images not uploading
**Cause:** Using wrong key name or not sending as FormData
**Solution:**
```javascript
// ✅ CORRECT
const formData = new FormData();
images.forEach(img => formData.append('images', img));

// ❌ WRONG
data.append('uploaded_images', images); // Wrong key name
data.append('images', JSON.stringify(images)); // Don't stringify files
```

### Issue 3: "Only companies can list equipment"
**Cause:** User doesn't have company profile
**Solution:** Ensure user is registered as company type and has completed company profile

### Issue 4: Category validation error
**Cause:** Neither `category_id` nor `category_name` provided
**Solution:** Always provide one:
```javascript
// Option 1: Use existing category
data.append('category_id', '1');

// Option 2: Create new category
data.append('category_name', 'Excavators');
```

### Issue 5: Tags or specifications not saving
**Cause:** Not sending as JSON string
**Solution:**
```javascript
// ✅ CORRECT
data.append('tag_names', JSON.stringify(['tag1', 'tag2']));
data.append('specifications_data', JSON.stringify([
  {name: 'Power', value: '121 kW'}
]));
```

---

## 📝 Testing with cURL

```bash
# Create equipment with all fields
curl -X POST http://localhost:8000/api/equipment/equipment/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "name=Caterpillar 320D2 Excavator" \
  -F "description=Heavy-duty hydraulic excavator" \
  -F "category_id=1" \
  -F "manufacturer=Caterpillar" \
  -F "model_number=320D2 L" \
  -F "year=2022" \
  -F "weight=22500.00" \
  -F "dimensions=996 x 294 x 323" \
  -F "fuel_type=Diesel" \
  -F "daily_rate=1500.00" \
  -F "weekly_rate=9000.00" \
  -F "monthly_rate=32000.00" \
  -F "country=UAE" \
  -F "city=DXB" \
  -F "total_units=3" \
  -F "available_units=3" \
  -F "featured=false" \
  -F 'tag_names=["Heavy Equipment","Construction"]' \
  -F 'specifications_data=[{"name":"Engine Power","value":"121 kW"}]' \
  -F "images=@/path/to/image1.jpg" \
  -F "images=@/path/to/image2.jpg"
```

---

## ✅ Validation Checklist

Before submitting your form, ensure:

- [ ] Name is not empty
- [ ] Description is not empty
- [ ] Category is selected (category_id) or provided (category_name)
- [ ] Manufacturer, model_number, year are provided
- [ ] Weight is a positive decimal number
- [ ] Dimensions are provided (format: "L x W x H")
- [ ] All three rates (daily, weekly, monthly) are positive decimals
- [ ] Country is either "UAE" or "UZB"
- [ ] City code matches the country (DXB for UAE, TAS for UZB, etc.)
- [ ] Total units ≥ 1
- [ ] Available units ≤ total units
- [ ] Images are real File objects (not strings)
- [ ] Maximum 7 images
- [ ] Authorization token is included in request

---

## 🎯 Next Steps

1. **Create categories first** - Run `python create_categories.py`
2. **Test with Postman/Thunder Client** - Verify API works before frontend
3. **Build the form** - Use the React example above
4. **Test incrementally** - Start with minimum fields, add more gradually
5. **Check browser console** - Look for detailed error messages
6. **Check Django logs** - Server will show validation errors

---

**Need help?** Check `CATEGORY_MANAGEMENT_GUIDE.md` for category setup!
