# Image Upload System - Complete Guide

## Overview

The Tezrent API has **three different image upload endpoints** for different purposes:

1. **Category Icons** - Small icons for category navigation/cards (64x64px recommended)
2. **Category Promotional Images** - Larger banners for featured sections (400x200px recommended)
3. **Equipment Images** - Multiple high-resolution photos of equipment

---

## 1. Category Icon Upload

**Purpose:** Small icon for category displayed in navigation menus, category cards, and listings.

### Endpoint
```
POST /api/equipment/categories/{category_id}/upload_icon/
```

### Headers
```
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

### Request Body (FormData)
```javascript
{
  "icon": <file>  // Single image file with key "icon"
}
```

### Example - JavaScript/React Native

```javascript
const uploadCategoryIcon = async (categoryId, iconFile) => {
  const formData = new FormData();
  
  // React Native
  formData.append('icon', {
    uri: iconFile.uri,
    type: iconFile.type || 'image/jpeg',
    name: iconFile.fileName || 'category_icon.jpg',
  });
  
  // React Web
  // formData.append('icon', iconFile); // iconFile is from <input type="file" />
  
  const response = await fetch(
    `http://localhost:8000/api/equipment/categories/${categoryId}/upload_icon/`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
      },
      body: formData,
    }
  );
  
  const data = await response.json();
  return data;
};
```

### Response (Success - 200)
```json
{
  "message": "Icon uploaded successfully",
  "category": {
    "id": 1,
    "name": "Excavators",
    "description": "Heavy-duty excavation equipment",
    "icon": "http://localhost:8000/media/category_icons/excavator_icon.jpg",
    "icon_url": "http://localhost:8000/media/category_icons/excavator_icon.jpg",
    "promotional_image": null,
    "promotional_image_url": null,
    "is_featured": true,
    "display_order": 1,
    "color_code": "#FF6B35",
    "equipment_count": 5,
    "slug": "excavators",
    "created_at": "2024-01-15T10:00:00Z",
    "updated_at": "2024-01-15T14:30:00Z"
  }
}
```

### Response (Error - 400)
```json
{
  "error": "No icon file provided. Please send the file with key \"icon\""
}
```

### Notes:
- **Replaces existing icon** - Old icon is deleted when new one is uploaded
- **File key must be "icon"** - FormData key name matters!
- **Recommended size:** 64x64px or 128x128px for retina displays
- **Formats:** JPG, PNG, SVG
- **Authentication required** - Must be logged in

---

## 2. Category Promotional Image Upload

**Purpose:** Larger banner/promotional image for featured category sections, homepage banners, etc.

### Endpoint
```
POST /api/equipment/categories/{category_id}/upload_promotional_image/
```

### Headers
```
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

### Request Body (FormData)
```javascript
{
  "promotional_image": <file>  // Single image file with key "promotional_image"
}
```

### Example - JavaScript/React Native

```javascript
const uploadCategoryPromotionalImage = async (categoryId, imageFile) => {
  const formData = new FormData();
  
  // React Native
  formData.append('promotional_image', {
    uri: imageFile.uri,
    type: imageFile.type || 'image/jpeg',
    name: imageFile.fileName || 'category_promo.jpg',
  });
  
  // React Web
  // formData.append('promotional_image', imageFile);
  
  const response = await fetch(
    `http://localhost:8000/api/equipment/categories/${categoryId}/upload_promotional_image/`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
      },
      body: formData,
    }
  );
  
  const data = await response.json();
  return data;
};
```

### Response (Success - 200)
```json
{
  "message": "Promotional image uploaded successfully",
  "category": {
    "id": 1,
    "name": "Excavators",
    "description": "Heavy-duty excavation equipment",
    "icon": "http://localhost:8000/media/category_icons/excavator_icon.jpg",
    "icon_url": "http://localhost:8000/media/category_icons/excavator_icon.jpg",
    "promotional_image": "http://localhost:8000/media/category_promotions/excavator_promo.jpg",
    "promotional_image_url": "http://localhost:8000/media/category_promotions/excavator_promo.jpg",
    "is_featured": true,
    "display_order": 1,
    "color_code": "#FF6B35",
    "equipment_count": 5,
    "slug": "excavators",
    "created_at": "2024-01-15T10:00:00Z",
    "updated_at": "2024-01-15T14:35:00Z"
  }
}
```

### Response (Error - 400)
```json
{
  "error": "No promotional image file provided. Please send the file with key \"promotional_image\""
}
```

### Notes:
- **Replaces existing promotional image** - Old image is deleted when new one is uploaded
- **File key must be "promotional_image"** - FormData key name matters!
- **Recommended size:** 400x200px or 800x400px for retina displays
- **Formats:** JPG, PNG
- **Authentication required** - Must be logged in

---

## 3. Equipment Images Upload

**Purpose:** Multiple high-resolution photos of equipment (product images). Equipment can have multiple images, and one is marked as primary.

### Endpoint
```
POST /api/equipment/equipment/
```

### Headers
```
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

### Request Body (FormData)
```javascript
{
  "name": "Caterpillar 320 Excavator",
  "description": "Heavy-duty excavator...",
  "category_id": 1,
  "daily_rate": 500,
  "images": <file[]>,  // Multiple files with SAME key "images"
  "tag_names": ["Construction", "Mining"],
  // ... other equipment fields
}
```

### Example - JavaScript/React Native

```javascript
const createEquipmentWithImages = async (equipmentData, imageFiles) => {
  const formData = new FormData();
  
  // Basic equipment data
  formData.append('name', equipmentData.name);
  formData.append('description', equipmentData.description);
  formData.append('category_id', equipmentData.category_id);
  formData.append('daily_rate', equipmentData.daily_rate);
  formData.append('weekly_rate', equipmentData.weekly_rate);
  formData.append('monthly_rate', equipmentData.monthly_rate);
  formData.append('country', equipmentData.country);
  formData.append('city', equipmentData.city);
  formData.append('manufacturer', equipmentData.manufacturer);
  formData.append('model_number', equipmentData.model_number);
  formData.append('year', equipmentData.year);
  formData.append('total_units', equipmentData.total_units);
  
  // Tags as JSON array
  formData.append('tag_names', JSON.stringify(equipmentData.tags || []));
  
  // Multiple images with SAME key "images"
  imageFiles.forEach((image) => {
    // React Native
    formData.append('images', {
      uri: image.uri,
      type: image.type || 'image/jpeg',
      name: image.fileName || `equipment_${Date.now()}.jpg`,
    });
    
    // React Web
    // formData.append('images', image); // image is File object from <input multiple />
  });
  
  const response = await fetch(
    'http://localhost:8000/api/equipment/equipment/',
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
      },
      body: formData,
    }
  );
  
  const data = await response.json();
  return data;
};
```

### Response (Success - 201)
```json
{
  "id": 1,
  "name": "Caterpillar 320 Excavator",
  "description": "Heavy-duty excavation equipment...",
  "manufacturer": "Caterpillar",
  "model_number": "320",
  "year": 2020,
  "daily_rate": "500.00",
  "weekly_rate": "3000.00",
  "monthly_rate": "10000.00",
  "country": "UAE",
  "city": "Dubai",
  "status": "available",
  "total_units": 2,
  "available_units": 2,
  "featured": false,
  "category": {
    "id": 1,
    "name": "Excavators",
    "icon_url": "http://localhost:8000/media/category_icons/excavator_icon.jpg"
  },
  "tags": [
    {"id": 1, "name": "Construction"},
    {"id": 2, "name": "Mining"}
  ],
  "images": [
    {
      "id": 1,
      "image": "http://localhost:8000/media/equipment_images/excavator_1.jpg",
      "is_primary": true,
      "display_order": 1,
      "uploaded_at": "2024-01-15T15:00:00Z"
    },
    {
      "id": 2,
      "image": "http://localhost:8000/media/equipment_images/excavator_2.jpg",
      "is_primary": false,
      "display_order": 2,
      "uploaded_at": "2024-01-15T15:00:01Z"
    },
    {
      "id": 3,
      "image": "http://localhost:8000/media/equipment_images/excavator_3.jpg",
      "is_primary": false,
      "display_order": 3,
      "uploaded_at": "2024-01-15T15:00:02Z"
    }
  ],
  "specifications": [],
  "created_at": "2024-01-15T15:00:00Z",
  "updated_at": "2024-01-15T15:00:02Z"
}
```

### Notes:
- **Multiple images allowed** - All images use the SAME key "images"
- **First image is primary** - Automatically marked as primary and used as main thumbnail
- **File key must be "images"** - FormData key name matters!
- **Recommended size:** 1200x800px or higher for quality
- **Formats:** JPG, PNG
- **Authentication required** - Must be logged in and have company profile

---

## Complete React Native Example

### Category Management Screen with Icon Upload

```jsx
import React, { useState } from 'react';
import { View, Text, TextInput, Button, Image, TouchableOpacity, Alert } from 'react-native';
import * as ImagePicker from 'expo-image-picker';

const CategoryManagement = ({ route }) => {
  const { categoryId } = route.params;
  const [categoryName, setCategoryName] = useState('');
  const [categoryDescription, setCategoryDescription] = useState('');
  const [iconUri, setIconUri] = useState(null);
  const [promoUri, setPromoUri] = useState(null);

  const pickIcon = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [1, 1], // Square for icon
      quality: 1,
    });

    if (!result.canceled) {
      setIconUri(result.assets[0].uri);
    }
  };

  const pickPromoImage = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [2, 1], // Wide banner
      quality: 1,
    });

    if (!result.canceled) {
      setPromoUri(result.assets[0].uri);
    }
  };

  const uploadIcon = async () => {
    if (!iconUri) {
      Alert.alert('Error', 'Please select an icon first');
      return;
    }

    const formData = new FormData();
    formData.append('icon', {
      uri: iconUri,
      type: 'image/jpeg',
      name: 'category_icon.jpg',
    });

    try {
      const response = await fetch(
        `http://localhost:8000/api/equipment/categories/${categoryId}/upload_icon/`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${accessToken}`,
          },
          body: formData,
        }
      );

      const data = await response.json();
      
      if (response.ok) {
        Alert.alert('Success', data.message);
      } else {
        Alert.alert('Error', data.error || 'Failed to upload icon');
      }
    } catch (error) {
      Alert.alert('Error', 'Network error: ' + error.message);
    }
  };

  const uploadPromoImage = async () => {
    if (!promoUri) {
      Alert.alert('Error', 'Please select a promotional image first');
      return;
    }

    const formData = new FormData();
    formData.append('promotional_image', {
      uri: promoUri,
      type: 'image/jpeg',
      name: 'category_promo.jpg',
    });

    try {
      const response = await fetch(
        `http://localhost:8000/api/equipment/categories/${categoryId}/upload_promotional_image/`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${accessToken}`,
          },
          body: formData,
        }
      );

      const data = await response.json();
      
      if (response.ok) {
        Alert.alert('Success', data.message);
      } else {
        Alert.alert('Error', data.error || 'Failed to upload promotional image');
      }
    } catch (error) {
      Alert.alert('Error', 'Network error: ' + error.message);
    }
  };

  return (
    <View style={{ padding: 20 }}>
      <Text style={{ fontSize: 24, fontWeight: 'bold', marginBottom: 20 }}>
        Category Management
      </Text>

      {/* Icon Upload */}
      <View style={{ marginBottom: 20 }}>
        <Text style={{ fontSize: 16, fontWeight: 'bold', marginBottom: 8 }}>
          Category Icon (64x64px)
        </Text>
        {iconUri && (
          <Image 
            source={{ uri: iconUri }} 
            style={{ width: 64, height: 64, marginBottom: 10 }}
          />
        )}
        <Button title="Pick Icon" onPress={pickIcon} />
        <View style={{ height: 10 }} />
        <Button title="Upload Icon" onPress={uploadIcon} disabled={!iconUri} />
      </View>

      {/* Promotional Image Upload */}
      <View style={{ marginBottom: 20 }}>
        <Text style={{ fontSize: 16, fontWeight: 'bold', marginBottom: 8 }}>
          Promotional Image (400x200px)
        </Text>
        {promoUri && (
          <Image 
            source={{ uri: promoUri }} 
            style={{ width: 200, height: 100, marginBottom: 10 }}
          />
        )}
        <Button title="Pick Promotional Image" onPress={pickPromoImage} />
        <View style={{ height: 10 }} />
        <Button title="Upload Promotional Image" onPress={uploadPromoImage} disabled={!promoUri} />
      </View>
    </View>
  );
};

export default CategoryManagement;
```

---

## Complete React Web Example

### Category Form with Image Uploads

```jsx
import React, { useState } from 'react';
import './CategoryForm.css';

const CategoryForm = ({ categoryId }) => {
  const [iconFile, setIconFile] = useState(null);
  const [promoFile, setPromoFile] = useState(null);
  const [iconPreview, setIconPreview] = useState(null);
  const [promoPreview, setPromoPreview] = useState(null);

  const handleIconChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setIconFile(file);
      setIconPreview(URL.createObjectURL(file));
    }
  };

  const handlePromoChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setPromoFile(file);
      setPromoPreview(URL.createObjectURL(file));
    }
  };

  const uploadIcon = async () => {
    if (!iconFile) {
      alert('Please select an icon first');
      return;
    }

    const formData = new FormData();
    formData.append('icon', iconFile);

    try {
      const response = await fetch(
        `http://localhost:8000/api/equipment/categories/${categoryId}/upload_icon/`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
          },
          body: formData,
        }
      );

      const data = await response.json();
      
      if (response.ok) {
        alert(data.message);
      } else {
        alert(data.error || 'Failed to upload icon');
      }
    } catch (error) {
      alert('Network error: ' + error.message);
    }
  };

  const uploadPromoImage = async () => {
    if (!promoFile) {
      alert('Please select a promotional image first');
      return;
    }

    const formData = new FormData();
    formData.append('promotional_image', promoFile);

    try {
      const response = await fetch(
        `http://localhost:8000/api/equipment/categories/${categoryId}/upload_promotional_image/`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
          },
          body: formData,
        }
      );

      const data = await response.json();
      
      if (response.ok) {
        alert(data.message);
      } else {
        alert(data.error || 'Failed to upload promotional image');
      }
    } catch (error) {
      alert('Network error: ' + error.message);
    }
  };

  return (
    <div className="category-form">
      <h2>Category Management</h2>

      {/* Icon Upload */}
      <div className="upload-section">
        <h3>Category Icon (64x64px)</h3>
        {iconPreview && (
          <img src={iconPreview} alt="Icon preview" className="icon-preview" />
        )}
        <input 
          type="file" 
          accept="image/*" 
          onChange={handleIconChange}
        />
        <button onClick={uploadIcon} disabled={!iconFile}>
          Upload Icon
        </button>
      </div>

      {/* Promotional Image Upload */}
      <div className="upload-section">
        <h3>Promotional Image (400x200px)</h3>
        {promoPreview && (
          <img src={promoPreview} alt="Promo preview" className="promo-preview" />
        )}
        <input 
          type="file" 
          accept="image/*" 
          onChange={handlePromoChange}
        />
        <button onClick={uploadPromoImage} disabled={!promoFile}>
          Upload Promotional Image
        </button>
      </div>
    </div>
  );
};

export default CategoryForm;
```

**CSS (CategoryForm.css):**
```css
.category-form {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

.upload-section {
  margin-bottom: 30px;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
}

.icon-preview {
  width: 64px;
  height: 64px;
  object-fit: cover;
  margin: 10px 0;
  border: 2px solid #007AFF;
  border-radius: 4px;
}

.promo-preview {
  width: 400px;
  height: 200px;
  object-fit: cover;
  margin: 10px 0;
  border: 2px solid #007AFF;
  border-radius: 4px;
}

input[type="file"] {
  display: block;
  margin: 10px 0;
}

button {
  padding: 10px 20px;
  background: #007AFF;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

button:hover:not(:disabled) {
  background: #0056b3;
}
```

---

## Summary

### Image Types:
1. **Category Icon** → Small (64x64) → Navigation/Cards → Key: `icon`
2. **Category Promo** → Large (400x200) → Banners/Featured → Key: `promotional_image`
3. **Equipment Images** → High-res → Product Photos → Key: `images` (multiple)

### Key Differences:

| Feature | Category Icon | Category Promo | Equipment Images |
|---------|--------------|----------------|------------------|
| **Endpoint** | `/categories/{id}/upload_icon/` | `/categories/{id}/upload_promotional_image/` | `/equipment/` (on create) |
| **FormData Key** | `icon` | `promotional_image` | `images` |
| **Multiple Files** | ❌ No (single) | ❌ No (single) | ✅ Yes (multiple) |
| **Replaces Old** | ✅ Yes | ✅ Yes | ➕ Adds new |
| **Size** | 64x64px | 400x200px | 1200x800px+ |
| **Purpose** | UI Icons | Banners | Product Photos |

### Common Mistakes to Avoid:
1. ❌ Using wrong FormData key name (must match exactly: `icon`, `promotional_image`, `images`)
2. ❌ Forgetting Authorization header
3. ❌ Not handling file types correctly in React Native (must include uri, type, name)
4. ❌ Trying to upload multiple files for category icons/promos (only single file allowed)
5. ❌ Using different keys for multiple equipment images (all must use "images")

### Testing with cURL:

```bash
# Upload category icon
curl -X POST http://localhost:8000/api/equipment/categories/1/upload_icon/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "icon=@path/to/icon.jpg"

# Upload category promotional image
curl -X POST http://localhost:8000/api/equipment/categories/1/upload_promotional_image/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "promotional_image=@path/to/banner.jpg"

# Create equipment with images
curl -X POST http://localhost:8000/api/equipment/equipment/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "name=Excavator" \
  -F "category_id=1" \
  -F "daily_rate=500" \
  -F "images=@photo1.jpg" \
  -F "images=@photo2.jpg" \
  -F "images=@photo3.jpg"
```

---

**That's it!** You now have complete image upload functionality for both categories and equipment. 📸
