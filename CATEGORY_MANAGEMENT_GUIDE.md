# Category Management API Guide

Complete guide for managing equipment categories in TezRent API.

## Table of Contents
1. [Overview](#overview)
2. [API Endpoints](#api-endpoints)
3. [Category Model Fields](#category-model-fields)
4. [Permissions](#permissions)
5. [Usage Examples](#usage-examples)
6. [Frontend Integration](#frontend-integration)

---

## Overview

The Category Management system allows administrators and company users to:
- ✅ Create new equipment categories
- ✅ View all categories (list and detail)
- ✅ Update category information
- ✅ Delete categories
- ✅ Upload category icons and promotional images
- ✅ Set featured categories
- ✅ Manage display order

**Base URL:** `http://localhost:8000/api/equipment/categories/`

---

## API Endpoints

### 1. List All Categories
```http
GET /api/equipment/categories/
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Excavators",
    "description": "Heavy-duty excavators for construction",
    "slug": "excavators",
    "is_featured": true,
    "display_order": 1,
    "color_code": "#FF6B35",
    "equipment_count": 12,
    "icon_url": "http://localhost:8000/media/category_icons/excavator.png",
    "promotional_image_url": "http://localhost:8000/media/category_promotions/excavator_banner.jpg",
    "mobile_display_data": {
      "id": 1,
      "name": "Excavators",
      "icon": "http://localhost:8000/media/category_icons/excavator.png",
      "count": 12,
      "color": "#FF6B35"
    }
  }
]
```

**Query Parameters:**
- `search` - Search by name or description
- `ordering` - Sort by: `display_order`, `name`, `equipment_count`, `-created_at`

**Example:**
```bash
# Search for categories
curl http://localhost:8000/api/equipment/categories/?search=excavator

# Sort by name
curl http://localhost:8000/api/equipment/categories/?ordering=name
```

---

### 2. Get Category Details
```http
GET /api/equipment/categories/{id}/
```

**Response:**
```json
{
  "id": 1,
  "name": "Excavators",
  "description": "Heavy-duty excavators for construction and mining projects",
  "slug": "excavators",
  "is_featured": true,
  "display_order": 1,
  "color_code": "#FF6B35",
  "equipment_count": 12,
  "icon_url": "http://localhost:8000/media/category_icons/excavator.png",
  "promotional_image_url": "http://localhost:8000/media/category_promotions/excavator_banner.jpg"
}
```

---

### 3. Create New Category
```http
POST /api/equipment/categories/
Content-Type: application/json
Authorization: Bearer YOUR_JWT_TOKEN
```

**Request Body:**
```json
{
  "name": "Bulldozers",
  "description": "Heavy-duty bulldozers for earthmoving and construction",
  "is_featured": false,
  "display_order": 5,
  "color_code": "#FFD700"
}
```

**Response (201 Created):**
```json
{
  "id": 5,
  "name": "Bulldozers",
  "description": "Heavy-duty bulldozers for earthmoving and construction",
  "slug": "bulldozers",
  "is_featured": false,
  "display_order": 5,
  "color_code": "#FFD700",
  "equipment_count": 0,
  "icon_url": null,
  "promotional_image_url": null
}
```

**JavaScript Example:**
```javascript
const response = await fetch('http://localhost:8000/api/equipment/categories/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${accessToken}`
  },
  body: JSON.stringify({
    name: 'Bulldozers',
    description: 'Heavy-duty bulldozers for earthmoving',
    is_featured: false,
    display_order: 5,
    color_code: '#FFD700'
  })
});

const category = await response.json();
```

---

### 4. Update Category
```http
PUT /api/equipment/categories/{id}/
Content-Type: application/json
Authorization: Bearer YOUR_JWT_TOKEN
```

**Request Body (Full Update):**
```json
{
  "name": "Excavators & Diggers",
  "description": "Updated description for excavators",
  "is_featured": true,
  "display_order": 1,
  "color_code": "#FF6B35"
}
```

**PATCH for Partial Update:**
```http
PATCH /api/equipment/categories/{id}/
Content-Type: application/json
Authorization: Bearer YOUR_JWT_TOKEN
```

```json
{
  "is_featured": true,
  "display_order": 1
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Excavators & Diggers",
  "description": "Updated description for excavators",
  "slug": "excavators-diggers",
  "is_featured": true,
  "display_order": 1,
  "color_code": "#FF6B35",
  "equipment_count": 12,
  "icon_url": "http://localhost:8000/media/category_icons/excavator.png",
  "promotional_image_url": "http://localhost:8000/media/category_promotions/excavator_banner.jpg"
}
```

---

### 5. Delete Category
```http
DELETE /api/equipment/categories/{id}/
Authorization: Bearer YOUR_JWT_TOKEN
```

**Response (204 No Content)**

**⚠️ Warning:** Deleting a category will affect all equipment in that category. Consider soft-delete or reassigning equipment first.

---

### 6. Upload Category Icon
```http
PATCH /api/equipment/categories/{id}/
Content-Type: multipart/form-data
Authorization: Bearer YOUR_JWT_TOKEN
```

**Form Data:**
- `icon` - Image file (PNG, JPG) - Recommended 64x64px

**JavaScript Example (with image upload):**
```javascript
const formData = new FormData();
formData.append('icon', iconFile); // File from input[type="file"]
formData.append('name', 'Excavators');

const response = await fetch(`http://localhost:8000/api/equipment/categories/${categoryId}/`, {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${accessToken}`
  },
  body: formData
});
```

---

### 7. Upload Promotional Image
```http
PATCH /api/equipment/categories/{id}/
Content-Type: multipart/form-data
Authorization: Bearer YOUR_JWT_TOKEN
```

**Form Data:**
- `promotional_image` - Image file (PNG, JPG) - Recommended 400x200px

---

### 8. Get Featured Categories
```http
GET /api/equipment/categories/featured/
```

**Response:**
```json
{
  "count": 6,
  "results": [
    {
      "id": 1,
      "name": "Excavators",
      "equipment_count": 12,
      "icon_url": "http://localhost:8000/media/category_icons/excavator.png",
      "color_code": "#FF6B35"
    }
  ]
}
```

---

### 9. Get Categories for Dropdown/Select
```http
GET /api/equipment/categories/choices/
```

**Response:**
```json
{
  "categories": [
    {
      "id": 1,
      "name": "Excavators",
      "slug": "excavators"
    },
    {
      "id": 2,
      "name": "Loaders",
      "slug": "loaders"
    }
  ]
}
```

**Usage:** Perfect for form dropdowns when creating equipment listings.

---

## Category Model Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | String (100) | ✅ Yes | Category name |
| `description` | Text | ❌ No | Detailed description |
| `slug` | String (100) | ❌ Auto | URL-friendly slug (auto-generated) |
| `is_featured` | Boolean | ❌ No | Show in featured section (default: false) |
| `display_order` | Integer | ❌ No | Display order (default: 1) |
| `color_code` | String (7) | ❌ No | Hex color code (e.g., #FF6B35) |
| `icon` | Image | ❌ No | Small icon (64x64px recommended) |
| `promotional_image` | Image | ❌ No | Banner image (400x200px recommended) |

---

## Permissions

### Read Operations (GET)
- ✅ **Anyone** can view categories (no authentication required)
- Public access for browsing equipment

### Write Operations (POST, PUT, PATCH, DELETE)
- ✅ **Authenticated users** can create/edit/delete categories
- Consider restricting to admin/staff only for production

### Recommended Production Permissions:
```python
# equipment/permissions.py
from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Admin users can do anything.
    Others can only read.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff
```

**Update views.py:**
```python
from .permissions import IsAdminOrReadOnly

class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
```

---

## Usage Examples

### React Frontend - Category Management Component

```jsx
import React, { useState, useEffect } from 'react';

const CategoryManagement = () => {
  const [categories, setCategories] = useState([]);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    is_featured: false,
    display_order: 1,
    color_code: '#000000'
  });

  // Fetch categories
  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    const response = await fetch('http://localhost:8000/api/equipment/categories/');
    const data = await response.json();
    setCategories(data);
  };

  // Create category
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const token = localStorage.getItem('access_token');
    const response = await fetch('http://localhost:8000/api/equipment/categories/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(formData)
    });

    if (response.ok) {
      alert('Category created successfully!');
      fetchCategories();
      setFormData({ name: '', description: '', is_featured: false, display_order: 1, color_code: '#000000' });
    }
  };

  // Delete category
  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this category?')) return;

    const token = localStorage.getItem('access_token');
    const response = await fetch(`http://localhost:8000/api/equipment/categories/${id}/`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (response.ok) {
      alert('Category deleted!');
      fetchCategories();
    }
  };

  return (
    <div>
      <h2>Category Management</h2>
      
      {/* Create Category Form */}
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Category Name"
          value={formData.name}
          onChange={(e) => setFormData({...formData, name: e.target.value})}
          required
        />
        <textarea
          placeholder="Description"
          value={formData.description}
          onChange={(e) => setFormData({...formData, description: e.target.value})}
        />
        <label>
          Featured:
          <input
            type="checkbox"
            checked={formData.is_featured}
            onChange={(e) => setFormData({...formData, is_featured: e.target.checked})}
          />
        </label>
        <input
          type="number"
          placeholder="Display Order"
          value={formData.display_order}
          onChange={(e) => setFormData({...formData, display_order: parseInt(e.target.value)})}
        />
        <input
          type="color"
          value={formData.color_code}
          onChange={(e) => setFormData({...formData, color_code: e.target.value})}
        />
        <button type="submit">Create Category</button>
      </form>

      {/* Category List */}
      <ul>
        {categories.map(category => (
          <li key={category.id}>
            <strong>{category.name}</strong> - {category.equipment_count} items
            <button onClick={() => handleDelete(category.id)}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default CategoryManagement;
```

---

### cURL Examples

**Create Category:**
```bash
curl -X POST http://localhost:8000/api/equipment/categories/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "Cranes",
    "description": "Mobile and tower cranes",
    "is_featured": true,
    "display_order": 3,
    "color_code": "#FF0000"
  }'
```

**Update Category:**
```bash
curl -X PATCH http://localhost:8000/api/equipment/categories/1/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"is_featured": true}'
```

**Delete Category:**
```bash
curl -X DELETE http://localhost:8000/api/equipment/categories/1/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Frontend Integration

### Step 1: Create Category Management Page
1. Add route: `/admin/categories`
2. Create component with form and list
3. Implement CRUD operations

### Step 2: Category Dropdown for Equipment Form
```javascript
// When creating equipment listing
const [categories, setCategories] = useState([]);

useEffect(() => {
  // Fetch categories for dropdown
  fetch('http://localhost:8000/api/equipment/categories/choices/')
    .then(res => res.json())
    .then(data => setCategories(data.categories));
}, []);

// In form:
<select name="category">
  {categories.map(cat => (
    <option key={cat.id} value={cat.id}>{cat.name}</option>
  ))}
</select>
```

### Step 3: Display Featured Categories on Homepage
```javascript
fetch('http://localhost:8000/api/equipment/categories/featured/')
  .then(res => res.json())
  .then(data => setFeaturedCategories(data.results));
```

---

## Next Steps

1. ✅ **Test CRUD operations** using Django Admin or API client (Postman/Thunder Client)
2. ✅ **Create categories** before adding equipment listings
3. ✅ **Upload icons** for better UI/UX
4. ✅ **Set featured categories** for homepage
5. ✅ **Build frontend category management** page
6. ✅ **Add category dropdown** to equipment creation form

---

## Quick Start Commands

```bash
# Using Python shell to create a category
python manage.py shell

from equipment.models import Category
category = Category.objects.create(
    name='Excavators',
    description='Heavy-duty excavators',
    is_featured=True,
    display_order=1,
    color_code='#FF6B35'
)
print(f"Created category: {category.name} (ID: {category.id})")
```

---

**Need help?** Check `EQUIPMENT_API_GUIDE.md` for equipment listing documentation.
