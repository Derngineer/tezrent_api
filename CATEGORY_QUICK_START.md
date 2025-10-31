# Category Management - Quick Reference

## 🎯 What You Can Do

### ✅ View Categories
```bash
# List all categories
curl http://localhost:8000/api/equipment/categories/

# Get one category
curl http://localhost:8000/api/equipment/categories/1/

# Get featured categories only
curl http://localhost:8000/api/equipment/categories/featured/

# Get categories for dropdown (simple format)
curl http://localhost:8000/api/equipment/categories/choices/
```

### ✅ Create Category
```bash
curl -X POST http://localhost:8000/api/equipment/categories/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "Excavators",
    "description": "Heavy-duty excavators",
    "is_featured": true,
    "display_order": 1,
    "color_code": "#FF6B35"
  }'
```

### ✅ Update Category
```bash
# Full update
curl -X PUT http://localhost:8000/api/equipment/categories/1/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{...all fields...}'

# Partial update
curl -X PATCH http://localhost:8000/api/equipment/categories/1/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"is_featured": true}'
```

### ✅ Delete Category
```bash
curl -X DELETE http://localhost:8000/api/equipment/categories/1/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### ✅ Upload Images
```bash
# Upload icon (64x64px recommended)
curl -X PATCH http://localhost:8000/api/equipment/categories/1/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "icon=@/path/to/icon.png"

# Upload promotional image (400x200px recommended)
curl -X PATCH http://localhost:8000/api/equipment/categories/1/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "promotional_image=@/path/to/banner.jpg"
```

---

## 🚀 Quick Setup Scripts

### Create Initial Categories
```bash
python create_categories.py
```
This creates 10 essential categories:
- Excavators ⭐
- Loaders ⭐
- Bulldozers ⭐
- Cranes ⭐
- Forklifts ⭐
- Compactors ⭐
- Generators
- Aerial Lifts
- Concrete Equipment
- Dump Trucks

---

## 📝 Category Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | ✅ | Category name |
| `description` | ❌ | Detailed description |
| `is_featured` | ❌ | Show on homepage (default: false) |
| `display_order` | ❌ | Sort order (default: 1) |
| `color_code` | ❌ | Hex color like #FF6B35 |
| `icon` | ❌ | Small icon image |
| `promotional_image` | ❌ | Banner image |
| `slug` | ❌ | Auto-generated from name |

---

## 🔐 Permissions

- **View (GET)**: Anyone (no auth required)
- **Create/Edit/Delete**: Authenticated users only
- **Production**: Recommend admin-only for modifications

---

## 📱 React Integration

### Fetch Categories for Dropdown
```javascript
const [categories, setCategories] = useState([]);

useEffect(() => {
  fetch('http://localhost:8000/api/equipment/categories/choices/')
    .then(res => res.json())
    .then(data => setCategories(data.categories));
}, []);

// Use in form
<select name="category">
  {categories.map(cat => (
    <option key={cat.id} value={cat.id}>{cat.name}</option>
  ))}
</select>
```

### Create Category
```javascript
const createCategory = async (formData) => {
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
    const category = await response.json();
    console.log('Created:', category);
  }
};
```

### Delete Category
```javascript
const deleteCategory = async (id) => {
  if (!confirm('Delete this category?')) return;
  
  const token = localStorage.getItem('access_token');
  
  await fetch(`http://localhost:8000/api/equipment/categories/${id}/`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
};
```

---

## 🎨 Recommended Color Codes

- **Excavators**: `#FF6B35` (Orange-Red)
- **Loaders**: `#FFD700` (Gold)
- **Bulldozers**: `#FF4500` (Orange)
- **Cranes**: `#1E90FF` (Dodger Blue)
- **Forklifts**: `#32CD32` (Lime Green)
- **Compactors**: `#8B4513` (Brown)
- **Generators**: `#DC143C` (Crimson)
- **Aerial Lifts**: `#9370DB` (Purple)
- **Concrete Equipment**: `#696969` (Gray)
- **Dump Trucks**: `#FF8C00` (Dark Orange)

---

## 📚 Full Documentation

See **CATEGORY_MANAGEMENT_GUIDE.md** for complete documentation with:
- All API endpoints
- Full React examples
- Permission configuration
- Image upload details
- Frontend integration guide

---

## ✅ Workflow

1. **Setup**: Run `python create_categories.py`
2. **Customize**: Edit categories via API or admin
3. **Add Icons**: Upload category icons (optional)
4. **Create Equipment**: Select category when creating listings
5. **Frontend**: Fetch categories for dropdowns and display
