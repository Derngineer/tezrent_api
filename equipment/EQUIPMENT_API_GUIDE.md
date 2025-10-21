# EQUIPMENT APP - Complete API Documentation

## 📋 Overview

The Equipment app manages the catalog of rentable machinery and equipment on TezRent. It handles categories, equipment listings, images, specifications, tags, and promotional banners.

### Key Features
- Multi-category equipment catalog
- Featured categories and equipment
- Advanced search and filtering
- Image galleries for equipment
- Detailed specifications
- Daily deals and promotions
- Seller-specific equipment management
- Location-based filtering
- Price range filtering

---

## 🗄️ Models

### **1. Category**
Equipment categories (excavators, loaders, cranes, etc.)

**Fields:**
- `name` - Category name (max 100 chars)
- `description` - Category description
- `icon` - Small icon image (64x64px) for navigation/cards
- `promotional_image` - Large banner image (400x200px)
- `is_featured` - Show in featured section
- `display_order` - Sort order (lower = first)
- `color_code` - Hex color for category theme (e.g., #FF6B35)
- `slug` - URL-friendly name (auto-generated)

**Computed Properties:**
- `icon_url` - Full URL for icon image
- `promotional_image_url` - Full URL for promo image
- `equipment_count` - Count of available equipment

### **2. Tag**
Custom tags for equipment (e.g., "heavy duty", "eco-friendly")

**Fields:**
- `name` - Tag name (max 50 chars, unique)

### **3. Equipment**
Main model for rentable machinery

**Fields:**
**Basic Info:**
- `seller` (FK to CompanyProfile) - Who owns/lists this
- `name` - Equipment name (max 200 chars)
- `description` - Detailed description
- `category` (FK to Category) - Equipment category
- `tags` (ManyToMany to Tag) - Custom tags

**Pricing:**
- `daily_rate` - Price per day (decimal)
- `weekly_rate` - Price per week (optional)
- `monthly_rate` - Price per month (optional)
- `minimum_rental_days` - Minimum rental period (default 1)
- `security_deposit` - Required deposit amount

**Availability:**
- `status` - available, rented, maintenance, inactive
- `quantity_available` - Number of units available
- `condition` - new, like_new, good, fair
- `year_of_manufacture` - Manufacturing year

**Location:**
- `country` - Country code (UAE, UZB)
- `city` - City code (DXB, AUH, etc.)
- `location_details` - Specific location info

**Features:**
- `featured` - Show in featured section
- `is_todays_deal` - Today's deal flag
- `deal_discount_percentage` - Discount % for deals

**Delivery:**
- `delivery_available` - Can be delivered
- `delivery_fee` - Delivery charge
- `pickup_location` - Where to pick up if no delivery

**Insurance:**
- `insurance_required` - Insurance mandatory
- `insurance_fee_per_day` - Daily insurance cost

**Technical:**
- `brand` - Brand name (max 100 chars)
- `model_number` - Model number (max 100 chars)
- `serial_number` - Serial number (optional)
- `weight_kg` - Weight in kilograms
- `dimensions` - Dimensions string

**Metadata:**
- `created_at` - When listed
- `updated_at` - Last modified
- `views_count` - Number of views (for analytics)

**Computed Properties:**
- `main_image_url` - URL of primary image
- `is_available` - Boolean availability status
- `average_rating` - Average review rating

### **4. EquipmentImage**
Image gallery for equipment

**Fields:**
- `equipment` (FK to Equipment) - Parent equipment
- `image` - Image file
- `caption` - Image description (optional)
- `display_order` - Sort order
- `is_primary` - Main/featured image flag

**Computed Properties:**
- `image_url` - Full image URL

### **5. EquipmentSpecification**
Technical specifications (key-value pairs)

**Fields:**
- `equipment` (FK to Equipment) - Parent equipment
- `spec_name` - Specification name (e.g., "Engine Power")
- `spec_value` - Value (e.g., "200 HP")
- `display_order` - Sort order

### **6. Banner**
Promotional banners for homepage/app

**Fields:**
- `title` - Banner title
- `description` - Banner description
- `image` - Banner image
- `link_type` - Where banner links (category, equipment, external, none)
- `link_category` (FK to Category) - Link to category (if link_type=category)
- `link_equipment` (FK to Equipment) - Link to equipment (if link_type=equipment)
- `external_url` - External URL (if link_type=external)
- `display_order` - Sort order
- `is_active` - Show/hide banner
- `start_date` - Banner start date
- `end_date` - Banner end date

**Computed Properties:**
- `image_url` - Full image URL
- `is_currently_active` - Check if active + within date range

---

## 🔗 API Endpoints

### **Categories**

#### 1. List All Categories
```
GET /api/equipment/categories/
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Excavators",
    "description": "Heavy excavation equipment",
    "icon_url": "https://api.tezrent.com/media/category_icons/excavator.png",
    "promotional_image_url": "https://api.tezrent.com/media/category_promotions/excavator_promo.jpg",
    "is_featured": true,
    "display_order": 1,
    "color_code": "#FF6B35",
    "slug": "excavators",
    "equipment_count": 24
  },
  {
    "id": 2,
    "name": "Loaders",
    "description": "Loading and material handling equipment",
    "icon_url": "https://api.tezrent.com/media/category_icons/loader.png",
    "promotional_image_url": null,
    "is_featured": false,
    "display_order": 2,
    "color_code": "#4ECDC4",
    "slug": "loaders",
    "equipment_count": 18
  }
]
```

---

#### 2. Get Category Choices (Dropdown)
```
GET /api/equipment/categories/choices/
```

**Response (200 OK):**
```json
{
  "categories": [
    {"id": 1, "name": "Excavators"},
    {"id": 2, "name": "Loaders"},
    {"id": 3, "name": "Cranes"}
  ]
}
```

**Usage:** Populate category dropdown in equipment listing form

---

#### 3. Get Featured Categories
```
GET /api/equipment/categories/featured/
```

**Response (200 OK):**
```json
{
  "count": 4,
  "results": [
    {
      "id": 1,
      "name": "Excavators",
      "icon_url": "https://...",
      "promotional_image_url": "https://...",
      "color_code": "#FF6B35",
      "equipment_count": 24
    }
  ]
}
```

**Usage:** Homepage featured categories section

---

#### 4. Get Equipment in Category
```
GET /api/equipment/categories/{id}/equipment/
```

**Query Parameters:**
- `featured=true` - Only featured equipment
- `deals=true` - Only today's deals
- `page=1` - Page number
- `page_size=20` - Items per page (default 20)

**Response (200 OK):**
```json
{
  "category": {
    "id": 1,
    "name": "Excavators",
    "icon_url": "https://..."
  },
  "count": 24,
  "page": 1,
  "total_pages": 2,
  "results": [
    {
      "id": 101,
      "name": "CAT 320D Excavator",
      "daily_rate": "500.00",
      "main_image_url": "https://...",
      "seller_name": "Dubai Equipment Rentals",
      "city": "DXB",
      "is_available": true,
      "average_rating": 4.8
    }
  ]
}
```

---

### **Equipment**

#### 5. List All Equipment
```
GET /api/equipment/equipment/
```

**Query Parameters:**
- `search=excavator` - Search in name, description, brand
- `category=1` - Filter by category ID
- `min_price=100` - Minimum daily rate
- `max_price=1000` - Maximum daily rate
- `city=DXB` - Filter by city
- `country=UAE` - Filter by country
- `condition=new` - Filter by condition
- `status=available` - Filter by status
- `featured=true` - Only featured items
- `deals=true` - Only today's deals
- `seller=5` - Filter by seller ID
- `ordering=-created_at` - Sort field (created_at, daily_rate, name, views_count)

**Response (200 OK):**
```json
{
  "count": 150,
  "next": "http://api.tezrent.com/api/equipment/equipment/?page=2",
  "previous": null,
  "results": [
    {
      "id": 101,
      "name": "CAT 320D Excavator",
      "description": "Heavy-duty excavator suitable for large projects",
      "category_name": "Excavators",
      "category_id": 1,
      "seller_id": 5,
      "seller_name": "Dubai Equipment Rentals",
      "seller_logo_url": "https://...",
      "daily_rate": "500.00",
      "weekly_rate": "3000.00",
      "monthly_rate": "10000.00",
      "security_deposit": "2000.00",
      "status": "available",
      "quantity_available": 3,
      "condition": "good",
      "city": "DXB",
      "country": "UAE",
      "featured": true,
      "is_todays_deal": false,
      "main_image_url": "https://...",
      "image_count": 5,
      "average_rating": 4.8,
      "total_reviews": 12,
      "is_available": true,
      "delivery_available": true,
      "delivery_fee": "150.00"
    }
  ]
}
```

---

#### 6. Get Equipment Detail
```
GET /api/equipment/equipment/{id}/
```

**Response (200 OK):**
```json
{
  "id": 101,
  "name": "CAT 320D Excavator",
  "description": "Heavy-duty excavator suitable for large projects. Equipped with GPS and modern safety features.",
  "category": {
    "id": 1,
    "name": "Excavators"
  },
  "seller": {
    "id": 5,
    "company_name": "Dubai Equipment Rentals",
    "company_logo_url": "https://...",
    "city": "DXB",
    "average_rating": 4.9,
    "total_rentals_completed": 230,
    "is_verified": true
  },
  "daily_rate": "500.00",
  "weekly_rate": "3000.00",
  "monthly_rate": "10000.00",
  "minimum_rental_days": 1,
  "security_deposit": "2000.00",
  "status": "available",
  "quantity_available": 3,
  "condition": "good",
  "year_of_manufacture": 2020,
  "brand": "Caterpillar",
  "model_number": "320D",
  "weight_kg": 22000,
  "dimensions": "9.5m x 2.8m x 3.1m",
  "city": "DXB",
  "country": "UAE",
  "location_details": "Al Quoz Industrial Area",
  "delivery_available": true,
  "delivery_fee": "150.00",
  "pickup_location": "Al Quoz Industrial Area 3, Warehouse 15",
  "insurance_required": true,
  "insurance_fee_per_day": "50.00",
  "featured": true,
  "is_todays_deal": false,
  "deal_discount_percentage": null,
  "images": [
    {
      "id": 501,
      "image_url": "https://api.tezrent.com/media/equipment/excavator1.jpg",
      "caption": "Main view",
      "is_primary": true,
      "display_order": 1
    },
    {
      "id": 502,
      "image_url": "https://api.tezrent.com/media/equipment/excavator2.jpg",
      "caption": "Side view",
      "is_primary": false,
      "display_order": 2
    }
  ],
  "specifications": [
    {
      "id": 701,
      "spec_name": "Engine Power",
      "spec_value": "160 HP",
      "display_order": 1
    },
    {
      "id": 702,
      "spec_name": "Bucket Capacity",
      "spec_value": "1.2 m³",
      "display_order": 2
    },
    {
      "id": 703,
      "spec_name": "Operating Weight",
      "spec_value": "22,000 kg",
      "display_order": 3
    }
  ],
  "tags": ["heavy duty", "GPS equipped", "recently serviced"],
  "average_rating": 4.8,
  "total_reviews": 12,
  "views_count": 145,
  "created_at": "2025-09-15T10:30:00Z",
  "updated_at": "2025-10-10T14:22:00Z"
}
```

---

#### 7. Create Equipment (Seller Only)
```
POST /api/equipment/equipment/
Authorization: Bearer <seller_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "CAT 320D Excavator",
  "description": "Heavy-duty excavator for large projects",
  "category": 1,
  "daily_rate": "500.00",
  "weekly_rate": "3000.00",
  "monthly_rate": "10000.00",
  "minimum_rental_days": 1,
  "security_deposit": "2000.00",
  "quantity_available": 3,
  "condition": "good",
  "year_of_manufacture": 2020,
  "brand": "Caterpillar",
  "model_number": "320D",
  "weight_kg": 22000,
  "dimensions": "9.5m x 2.8m x 3.1m",
  "city": "DXB",
  "country": "UAE",
  "delivery_available": true,
  "delivery_fee": "150.00",
  "pickup_location": "Al Quoz Industrial Area 3",
  "insurance_required": true,
  "insurance_fee_per_day": "50.00",
  "tags": ["heavy duty", "GPS equipped"]
}
```

**Response (201 Created):**
```json
{
  "id": 101,
  "name": "CAT 320D Excavator",
  "status": "available",
  "created_at": "2025-10-21T15:30:00Z"
}
```

**Note:** Seller is auto-set from authenticated user's CompanyProfile

---

#### 8. Update Equipment (Seller Only)
```
PUT /api/equipment/equipment/{id}/
Authorization: Bearer <seller_token>
```

**Request Body:** (same as create, all fields)

```
PATCH /api/equipment/equipment/{id}/
Authorization: Bearer <seller_token>
```

**Request Body:** (partial update)
```json
{
  "daily_rate": "550.00",
  "quantity_available": 2
}
```

**Permissions:** Only the seller who owns the equipment can update it

---

#### 9. Delete Equipment (Seller Only)
```
DELETE /api/equipment/equipment/{id}/
Authorization: Bearer <seller_token>
```

**Response (204 No Content)**

**Permissions:** Only the seller who owns the equipment can delete it

---

#### 10. Search Equipment
```
GET /api/equipment/equipment/search/
```

**Query Parameters:**
- `q=excavator` - Search query (searches name, description, brand, category)
- `category=1` - Filter by category
- `city=DXB` - Filter by city
- `min_price=100` - Min daily rate
- `max_price=1000` - Max daily rate

**Response:** Same format as list equipment

---

#### 11. Get Featured Equipment
```
GET /api/equipment/equipment/featured/
```

**Query Parameters:**
- `limit=10` - Number of items (default 10)

**Response (200 OK):**
```json
{
  "count": 10,
  "results": [...]
}
```

**Usage:** Homepage featured equipment section

---

#### 12. Get Today's Deals
```
GET /api/equipment/equipment/todays_deals/
```

**Query Parameters:**
- `limit=10` - Number of items (default 10)

**Response (200 OK):**
```json
{
  "count": 5,
  "results": [
    {
      "id": 102,
      "name": "JCB Loader",
      "daily_rate": "300.00",
      "deal_discount_percentage": 15,
      "discounted_price": "255.00",
      "savings": "45.00",
      "main_image_url": "https://..."
    }
  ]
}
```

---

#### 13. Get Seller's Equipment
```
GET /api/equipment/equipment/my_equipment/
Authorization: Bearer <seller_token>
```

**Response:** List of equipment owned by authenticated seller

---

#### 14. Update Equipment Status
```
POST /api/equipment/equipment/{id}/update_status/
Authorization: Bearer <seller_token>
```

**Request Body:**
```json
{
  "status": "maintenance"
}
```

**Allowed Status Values:**
- `available` - Ready to rent
- `rented` - Currently rented
- `maintenance` - Under maintenance
- `inactive` - Not available for rent

---

### **Equipment Images**

#### 15. List Equipment Images
```
GET /api/equipment/images/
```

**Query Parameters:**
- `equipment=101` - Filter by equipment ID

**Response (200 OK):**
```json
[
  {
    "id": 501,
    "equipment_id": 101,
    "image_url": "https://...",
    "caption": "Main view",
    "display_order": 1,
    "is_primary": true
  }
]
```

---

#### 16. Add Equipment Image
```
POST /api/equipment/images/
Authorization: Bearer <seller_token>
Content-Type: multipart/form-data
```

**Form Data:**
- `equipment` - Equipment ID
- `image` - Image file
- `caption` - Optional caption
- `display_order` - Display order (optional)
- `is_primary` - Boolean (optional)

**Response (201 Created):**
```json
{
  "id": 502,
  "equipment_id": 101,
  "image_url": "https://...",
  "caption": "Side view",
  "display_order": 2,
  "is_primary": false
}
```

---

#### 17. Update/Delete Image
```
PUT /api/equipment/images/{id}/
PATCH /api/equipment/images/{id}/
DELETE /api/equipment/images/{id}/
Authorization: Bearer <seller_token>
```

**Permissions:** Only seller who owns the parent equipment

---

### **Banners**

#### 18. Get Active Banners
```
GET /api/equipment/banners/active/
```

**Response (200 OK):**
```json
{
  "count": 3,
  "results": [
    {
      "id": 1,
      "title": "Summer Sale - 20% Off Excavators",
      "description": "Limited time offer on all excavators",
      "image_url": "https://...",
      "link_type": "category",
      "link_category_id": 1,
      "display_order": 1
    },
    {
      "id": 2,
      "title": "New CAT Equipment Available",
      "description": "Check out our latest arrivals",
      "image_url": "https://...",
      "link_type": "equipment",
      "link_equipment_id": 101,
      "display_order": 2
    }
  ]
}
```

**Usage:** Homepage carousel/banner section

---

## 📱 React Native Examples

### Browse Equipment with Filters

```javascript
import React, { useState, useEffect } from 'react';
import { FlatList, View, TextInput } from 'react-native';

const EquipmentListScreen = () => {
  const [equipment, setEquipment] = useState([]);
  const [filters, setFilters] = useState({
    category: null,
    city: 'DXB',
    min_price: '',
    max_price: '',
    search: ''
  });
  
  useEffect(() => {
    fetchEquipment();
  }, [filters]);
  
  const fetchEquipment = async () => {
    // Build query string
    const params = new URLSearchParams();
    if (filters.category) params.append('category', filters.category);
    if (filters.city) params.append('city', filters.city);
    if (filters.min_price) params.append('min_price', filters.min_price);
    if (filters.max_price) params.append('max_price', filters.max_price);
    if (filters.search) params.append('search', filters.search);
    params.append('ordering', '-created_at');
    
    const response = await fetch(
      `https://api.tezrent.com/api/equipment/equipment/?${params.toString()}`
    );
    
    const data = await response.json();
    setEquipment(data.results);
  };
  
  return (
    <View>
      <TextInput
        placeholder="Search equipment..."
        value={filters.search}
        onChangeText={(text) => setFilters({...filters, search: text})}
      />
      
      <FlatList
        data={equipment}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => (
          <EquipmentCard equipment={item} />
        )}
      />
    </View>
  );
};
```

### Create Equipment Listing (Seller App)

```javascript
const AddEquipmentScreen = () => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    category: null,
    daily_rate: '',
    security_deposit: '',
    quantity_available: 1,
    condition: 'good',
    brand: '',
    city: 'DXB',
    delivery_available: true
  });
  
  const [images, setImages] = useState([]);
  
  const submitEquipment = async () => {
    const token = await AsyncStorage.getItem('access_token');
    
    // 1. Create equipment
    const response = await fetch('https://api.tezrent.com/api/equipment/equipment/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(formData)
    });
    
    const equipment = await response.json();
    
    // 2. Upload images
    for (let i = 0; i < images.length; i++) {
      const imageForm = new FormData();
      imageForm.append('equipment', equipment.id);
      imageForm.append('image', {
        uri: images[i].uri,
        type: 'image/jpeg',
        name: `equipment_${i}.jpg`
      });
      imageForm.append('is_primary', i === 0); // First image is primary
      imageForm.append('display_order', i + 1);
      
      await fetch('https://api.tezrent.com/api/equipment/images/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        },
        body: imageForm
      });
    }
    
    navigation.navigate('EquipmentDetail', { id: equipment.id });
  };
  
  return (
    <ScrollView>
      {/* Form fields */}
      <Button title="Add Equipment" onPress={submitEquipment} />
    </ScrollView>
  );
};
```

### Equipment Detail Screen

```javascript
const EquipmentDetailScreen = ({ route }) => {
  const { id } = route.params;
  const [equipment, setEquipment] = useState(null);
  
  useEffect(() => {
    fetchEquipment();
  }, []);
  
  const fetchEquipment = async () => {
    const response = await fetch(
      `https://api.tezrent.com/api/equipment/equipment/${id}/`
    );
    const data = await response.json();
    setEquipment(data);
  };
  
  if (!equipment) return <Loading />;
  
  return (
    <ScrollView>
      {/* Image Gallery */}
      <Carousel>
        {equipment.images.map(img => (
          <Image key={img.id} source={{ uri: img.image_url }} />
        ))}
      </Carousel>
      
      {/* Title & Price */}
      <Text>{equipment.name}</Text>
      <Text>AED {equipment.daily_rate} / day</Text>
      
      {/* Seller Info */}
      <View>
        <Image source={{ uri: equipment.seller.company_logo_url }} />
        <Text>{equipment.seller.company_name}</Text>
        <Rating value={equipment.seller.average_rating} />
      </View>
      
      {/* Specifications */}
      <View>
        {equipment.specifications.map(spec => (
          <Text key={spec.id}>{spec.spec_name}: {spec.spec_value}</Text>
        ))}
      </View>
      
      {/* Description */}
      <Text>{equipment.description}</Text>
      
      {/* Rent Button */}
      <Button
        title={`Rent for AED ${equipment.daily_rate}/day`}
        onPress={() => navigation.navigate('CreateRental', { equipmentId: id })}
      />
    </ScrollView>
  );
};
```

---

## 🔒 Permissions

| Action | Anonymous | Customer | Seller (Owner) | Seller (Other) | Staff |
|--------|-----------|----------|----------------|----------------|-------|
| **Equipment** |
| List/Search | ✅ | ✅ | ✅ | ✅ | ✅ |
| View Detail | ✅ | ✅ | ✅ | ✅ | ✅ |
| Create | ❌ | ❌ | ✅ | ✅ | ✅ |
| Update | ❌ | ❌ | ✅ Own | ❌ | ✅ |
| Delete | ❌ | ❌ | ✅ Own | ❌ | ✅ |
| **Images** |
| List | ✅ | ✅ | ✅ | ✅ | ✅ |
| Add | ❌ | ❌ | ✅ Own | ❌ | ✅ |
| Update/Delete | ❌ | ❌ | ✅ Own | ❌ | ✅ |
| **Categories** |
| List | ✅ | ✅ | ✅ | ✅ | ✅ |
| Create/Update | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Banners** |
| View Active | ✅ | ✅ | ✅ | ✅ | ✅ |
| Manage | ❌ | ❌ | ❌ | ❌ | ✅ |

---

## ⚙️ Common Use Cases

### 1. Homepage Equipment Feed
```
GET /api/equipment/equipment/featured/?limit=10
GET /api/equipment/equipment/todays_deals/?limit=5
GET /api/equipment/banners/active/
```

### 2. Category Browse
```
GET /api/equipment/categories/featured/
GET /api/equipment/categories/{id}/equipment/?page=1
```

### 3. Search Flow
```
User types "excavator" in search bar
→ GET /api/equipment/equipment/?search=excavator
→ Display results
→ User applies filters (city=DXB, min_price=200)
→ GET /api/equipment/equipment/?search=excavator&city=DXB&min_price=200
```

### 4. Seller Dashboard
```
GET /api/equipment/equipment/my_equipment/
→ Show seller's equipment list
→ Click "Add New Equipment"
→ POST /api/equipment/equipment/ (create)
→ POST /api/equipment/images/ (upload images)
```

---

## 🛠️ Admin Interface

Access: `http://localhost:8000/admin/equipment/`

**Models:**
- Categories - Manage categories
- Equipment - Manage all equipment
- Equipment Images - Image gallery
- Equipment Specifications - Technical specs
- Tags - Custom tags
- Banners - Promotional banners

**Admin Features:**
- Search equipment by name, brand, model
- Filter by category, status, seller, city
- Bulk actions (mark as featured, change status)
- Inline editing (images, specs within equipment)
- Preview images

---

## 🐛 Common Errors

### 403 Forbidden - Update Equipment
```json
{
  "detail": "You do not have permission to perform this action."
}
```
**Cause:** Trying to update equipment owned by another seller
**Solution:** Only update your own equipment

### 400 Bad Request - Invalid Category
```json
{
  "category": ["Invalid pk \"999\" - object does not exist."]
}
```
**Solution:** Use valid category ID from `/api/equipment/categories/`

### 400 - Invalid Price
```json
{
  "daily_rate": ["Ensure that there are no more than 10 digits in total."]
}
```
**Solution:** Check decimal format (max 10 digits, 2 decimals)

---

## 📄 Files Reference

- `equipment/models.py` - Category, Equipment, EquipmentImage, EquipmentSpecification, Tag, Banner
- `equipment/serializers.py` - API serializers (list, detail, create variants)
- `equipment/views.py` - ViewSets with custom actions
- `equipment/urls.py` - URL routing
- `equipment/admin.py` - Django admin configuration

---

**End of Equipment API Documentation** 📚
