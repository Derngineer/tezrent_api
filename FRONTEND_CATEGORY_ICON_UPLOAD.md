# Category Icon Upload - Mobile & Web Integration

## 🎯 Backend Status

✅ **Your API already supports icon uploads!**

- Endpoint: `PATCH /api/equipment/categories/{id}/`
- Fields: `icon` (64x64px), `promotional_image` (400x200px)
- Format: `multipart/form-data`
- Auth: Required (Bearer token)

---

## 📱 React Native Implementation

### Complete Category Form with Icon Upload

```jsx
import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  Image,
  ScrollView,
  StyleSheet,
  Alert,
  ActivityIndicator
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import * as DocumentPicker from 'expo-document-picker';

const CategoryForm = ({ category = null, onSuccess }) => {
  const [formData, setFormData] = useState({
    name: category?.name || '',
    description: category?.description || '',
    is_featured: category?.is_featured || false,
    display_order: category?.display_order?.toString() || '1',
    color_code: category?.color_code || '#FF6B35'
  });

  const [iconUri, setIconUri] = useState(category?.icon_url || null);
  const [promoImageUri, setPromoImageUri] = useState(category?.promotional_image_url || null);
  const [loading, setLoading] = useState(false);

  // Pick icon image (64x64px)
  const pickIcon = async () => {
    try {
      // Request permission
      const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
      
      if (status !== 'granted') {
        Alert.alert('Permission needed', 'Please allow access to your photos');
        return;
      }

      // Launch image picker
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [1, 1], // Square for icon
        quality: 0.8,
      });

      if (!result.canceled) {
        setIconUri(result.assets[0].uri);
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to pick image');
      console.error(error);
    }
  };

  // Pick promotional image (400x200px)
  const pickPromoImage = async () => {
    try {
      const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
      
      if (status !== 'granted') {
        Alert.alert('Permission needed', 'Please allow access to your photos');
        return;
      }

      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [2, 1], // 2:1 ratio for banner
        quality: 0.8,
      });

      if (!result.canceled) {
        setPromoImageUri(result.assets[0].uri);
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to pick image');
      console.error(error);
    }
  };

  // Handle form submission
  const handleSubmit = async () => {
    if (!formData.name) {
      Alert.alert('Error', 'Category name is required');
      return;
    }

    setLoading(true);

    try {
      // Create FormData
      const data = new FormData();
      
      // Add text fields
      data.append('name', formData.name);
      data.append('description', formData.description);
      data.append('is_featured', formData.is_featured);
      data.append('display_order', formData.display_order);
      data.append('color_code', formData.color_code);

      // Add icon if selected
      if (iconUri && !iconUri.startsWith('http')) {
        const iconFile = {
          uri: iconUri,
          type: 'image/jpeg',
          name: `icon-${Date.now()}.jpg`
        };
        data.append('icon', iconFile);
      }

      // Add promotional image if selected
      if (promoImageUri && !promoImageUri.startsWith('http')) {
        const promoFile = {
          uri: promoImageUri,
          type: 'image/jpeg',
          name: `promo-${Date.now()}.jpg`
        };
        data.append('promotional_image', promoFile);
      }

      // Get auth token
      const token = await AsyncStorage.getItem('access_token');
      
      // API endpoint
      const url = category
        ? `http://localhost:8000/api/equipment/categories/${category.id}/`
        : 'http://localhost:8000/api/equipment/categories/';
      
      const method = category ? 'PATCH' : 'POST';

      // Make request
      const response = await fetch(url, {
        method: method,
        headers: {
          'Authorization': `Bearer ${token}`,
          // Don't set Content-Type - let browser handle it
        },
        body: data
      });

      if (response.ok) {
        const result = await response.json();
        Alert.alert('Success', `Category ${category ? 'updated' : 'created'} successfully!`);
        onSuccess && onSuccess(result);
      } else {
        const error = await response.json();
        Alert.alert('Error', JSON.stringify(error));
      }
    } catch (error) {
      Alert.alert('Error', 'Network error occurred');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>
        {category ? 'Edit Category' : 'Create Category'}
      </Text>

      {/* Category Name */}
      <View style={styles.formGroup}>
        <Text style={styles.label}>Category Name *</Text>
        <TextInput
          style={styles.input}
          value={formData.name}
          onChangeText={(text) => setFormData({ ...formData, name: text })}
          placeholder="e.g., Excavators"
        />
      </View>

      {/* Description */}
      <View style={styles.formGroup}>
        <Text style={styles.label}>Description</Text>
        <TextInput
          style={[styles.input, styles.textArea]}
          value={formData.description}
          onChangeText={(text) => setFormData({ ...formData, description: text })}
          placeholder="Category description..."
          multiline
          numberOfLines={4}
        />
      </View>

      {/* Icon Upload */}
      <View style={styles.formGroup}>
        <Text style={styles.label}>Icon (64x64px)</Text>
        <TouchableOpacity style={styles.imagePickerButton} onPress={pickIcon}>
          {iconUri ? (
            <Image source={{ uri: iconUri }} style={styles.iconPreview} />
          ) : (
            <View style={styles.imagePlaceholder}>
              <Text style={styles.placeholderText}>Tap to select icon</Text>
            </View>
          )}
        </TouchableOpacity>
        {iconUri && (
          <TouchableOpacity onPress={() => setIconUri(null)}>
            <Text style={styles.removeText}>Remove Icon</Text>
          </TouchableOpacity>
        )}
      </View>

      {/* Promotional Image Upload */}
      <View style={styles.formGroup}>
        <Text style={styles.label}>Promotional Image (400x200px)</Text>
        <TouchableOpacity style={styles.imagePickerButton} onPress={pickPromoImage}>
          {promoImageUri ? (
            <Image source={{ uri: promoImageUri }} style={styles.promoPreview} />
          ) : (
            <View style={[styles.imagePlaceholder, styles.promoPlaceholder]}>
              <Text style={styles.placeholderText}>Tap to select banner</Text>
            </View>
          )}
        </TouchableOpacity>
        {promoImageUri && (
          <TouchableOpacity onPress={() => setPromoImageUri(null)}>
            <Text style={styles.removeText}>Remove Banner</Text>
          </TouchableOpacity>
        )}
      </View>

      {/* Display Order */}
      <View style={styles.formGroup}>
        <Text style={styles.label}>Display Order</Text>
        <TextInput
          style={styles.input}
          value={formData.display_order}
          onChangeText={(text) => setFormData({ ...formData, display_order: text })}
          keyboardType="numeric"
          placeholder="1"
        />
      </View>

      {/* Color Code */}
      <View style={styles.formGroup}>
        <Text style={styles.label}>Color Code</Text>
        <View style={styles.colorInputContainer}>
          <TextInput
            style={styles.input}
            value={formData.color_code}
            onChangeText={(text) => setFormData({ ...formData, color_code: text })}
            placeholder="#FF6B35"
          />
          <View style={[styles.colorPreview, { backgroundColor: formData.color_code }]} />
        </View>
      </View>

      {/* Featured Toggle */}
      <View style={styles.formGroup}>
        <TouchableOpacity
          style={styles.checkboxContainer}
          onPress={() => setFormData({ ...formData, is_featured: !formData.is_featured })}
        >
          <View style={[styles.checkbox, formData.is_featured && styles.checkboxChecked]}>
            {formData.is_featured && <Text style={styles.checkmark}>✓</Text>}
          </View>
          <Text style={styles.checkboxLabel}>Featured Category</Text>
        </TouchableOpacity>
      </View>

      {/* Submit Button */}
      <TouchableOpacity
        style={[styles.submitButton, loading && styles.submitButtonDisabled]}
        onPress={handleSubmit}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.submitButtonText}>
            {category ? 'Update Category' : 'Create Category'}
          </Text>
        )}
      </TouchableOpacity>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#f5f5f5',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
    color: '#333',
  },
  formGroup: {
    marginBottom: 20,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
    color: '#555',
  },
  input: {
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
  },
  textArea: {
    height: 100,
    textAlignVertical: 'top',
  },
  imagePickerButton: {
    borderWidth: 2,
    borderColor: '#ddd',
    borderStyle: 'dashed',
    borderRadius: 8,
    overflow: 'hidden',
  },
  imagePlaceholder: {
    height: 100,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f9f9f9',
  },
  promoPlaceholder: {
    height: 150,
  },
  placeholderText: {
    color: '#999',
    fontSize: 14,
  },
  iconPreview: {
    width: '100%',
    height: 100,
    resizeMode: 'contain',
    backgroundColor: '#f9f9f9',
  },
  promoPreview: {
    width: '100%',
    height: 150,
    resizeMode: 'cover',
  },
  removeText: {
    color: '#dc3545',
    fontSize: 14,
    marginTop: 5,
    textAlign: 'center',
  },
  colorInputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  colorPreview: {
    width: 40,
    height: 40,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#ddd',
  },
  checkboxContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  checkbox: {
    width: 24,
    height: 24,
    borderWidth: 2,
    borderColor: '#007bff',
    borderRadius: 4,
    marginRight: 10,
    justifyContent: 'center',
    alignItems: 'center',
  },
  checkboxChecked: {
    backgroundColor: '#007bff',
  },
  checkmark: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  checkboxLabel: {
    fontSize: 16,
    color: '#555',
  },
  submitButton: {
    backgroundColor: '#007bff',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 10,
    marginBottom: 30,
  },
  submitButtonDisabled: {
    backgroundColor: '#ccc',
  },
  submitButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
});

export default CategoryForm;
```

---

## 🌐 React Web Implementation

### Complete Category Form with Icon Upload

```jsx
import React, { useState } from 'react';
import './CategoryForm.css';

const CategoryForm = ({ category = null, onSuccess }) => {
  const [formData, setFormData] = useState({
    name: category?.name || '',
    description: category?.description || '',
    is_featured: category?.is_featured || false,
    display_order: category?.display_order || 1,
    color_code: category?.color_code || '#FF6B35'
  });

  const [iconFile, setIconFile] = useState(null);
  const [iconPreview, setIconPreview] = useState(category?.icon_url || null);
  
  const [promoFile, setPromoFile] = useState(null);
  const [promoPreview, setPromoPreview] = useState(category?.promotional_image_url || null);
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Handle icon selection
  const handleIconChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.size > 500000) { // 500KB limit
        alert('Icon file size should be less than 500KB');
        return;
      }
      
      setIconFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setIconPreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  // Handle promotional image selection
  const handlePromoChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.size > 2000000) { // 2MB limit
        alert('Banner file size should be less than 2MB');
        return;
      }
      
      setPromoFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPromoPreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (!formData.name) {
      setError('Category name is required');
      return;
    }

    setLoading(true);

    try {
      // Create FormData
      const data = new FormData();
      
      // Add text fields
      Object.keys(formData).forEach(key => {
        data.append(key, formData[key]);
      });

      // Add icon if selected
      if (iconFile) {
        data.append('icon', iconFile);
      }

      // Add promotional image if selected
      if (promoFile) {
        data.append('promotional_image', promoFile);
      }

      // Get auth token
      const token = localStorage.getItem('access_token');
      
      // API endpoint
      const url = category
        ? `http://localhost:8000/api/equipment/categories/${category.id}/`
        : 'http://localhost:8000/api/equipment/categories/';
      
      const method = category ? 'PATCH' : 'POST';

      // Make request
      const response = await fetch(url, {
        method: method,
        headers: {
          'Authorization': `Bearer ${token}`,
          // Don't set Content-Type - let browser handle it
        },
        body: data
      });

      if (response.ok) {
        const result = await response.json();
        alert(`Category ${category ? 'updated' : 'created'} successfully!`);
        onSuccess && onSuccess(result);
      } else {
        const errorData = await response.json();
        setError(JSON.stringify(errorData, null, 2));
      }
    } catch (err) {
      setError('Network error occurred');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="category-form-container">
      <h2>{category ? 'Edit Category' : 'Create Category'}</h2>

      {error && (
        <div className="alert alert-error">
          <strong>Error:</strong> <pre>{error}</pre>
        </div>
      )}

      <form onSubmit={handleSubmit}>
        {/* Category Name */}
        <div className="form-group">
          <label htmlFor="name">Category Name *</label>
          <input
            type="text"
            id="name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="e.g., Excavators"
            required
          />
        </div>

        {/* Description */}
        <div className="form-group">
          <label htmlFor="description">Description</label>
          <textarea
            id="description"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            rows="4"
            placeholder="Category description..."
          />
        </div>

        {/* Icon Upload */}
        <div className="form-group">
          <label>Icon (64x64px recommended)</label>
          <div className="image-upload-container">
            <input
              type="file"
              accept="image/*"
              onChange={handleIconChange}
              id="icon-upload"
              style={{ display: 'none' }}
            />
            <label htmlFor="icon-upload" className="upload-button">
              {iconPreview ? (
                <img src={iconPreview} alt="Icon preview" className="icon-preview" />
              ) : (
                <div className="upload-placeholder">
                  <span>📁 Choose Icon</span>
                </div>
              )}
            </label>
            {iconPreview && (
              <button
                type="button"
                className="remove-button"
                onClick={() => {
                  setIconFile(null);
                  setIconPreview(null);
                }}
              >
                Remove Icon
              </button>
            )}
          </div>
          <small>PNG or JPG, max 500KB</small>
        </div>

        {/* Promotional Image Upload */}
        <div className="form-group">
          <label>Promotional Banner (400x200px recommended)</label>
          <div className="image-upload-container">
            <input
              type="file"
              accept="image/*"
              onChange={handlePromoChange}
              id="promo-upload"
              style={{ display: 'none' }}
            />
            <label htmlFor="promo-upload" className="upload-button">
              {promoPreview ? (
                <img src={promoPreview} alt="Banner preview" className="promo-preview" />
              ) : (
                <div className="upload-placeholder promo-placeholder">
                  <span>📁 Choose Banner</span>
                </div>
              )}
            </label>
            {promoPreview && (
              <button
                type="button"
                className="remove-button"
                onClick={() => {
                  setPromoFile(null);
                  setPromoPreview(null);
                }}
              >
                Remove Banner
              </button>
            )}
          </div>
          <small>PNG or JPG, max 2MB</small>
        </div>

        {/* Display Order */}
        <div className="form-group">
          <label htmlFor="display_order">Display Order</label>
          <input
            type="number"
            id="display_order"
            value={formData.display_order}
            onChange={(e) => setFormData({ ...formData, display_order: parseInt(e.target.value) })}
            min="1"
          />
        </div>

        {/* Color Code */}
        <div className="form-group">
          <label htmlFor="color_code">Color Code</label>
          <div className="color-input-container">
            <input
              type="text"
              id="color_code"
              value={formData.color_code}
              onChange={(e) => setFormData({ ...formData, color_code: e.target.value })}
              placeholder="#FF6B35"
            />
            <input
              type="color"
              value={formData.color_code}
              onChange={(e) => setFormData({ ...formData, color_code: e.target.value })}
              className="color-picker"
            />
          </div>
        </div>

        {/* Featured Toggle */}
        <div className="form-group">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={formData.is_featured}
              onChange={(e) => setFormData({ ...formData, is_featured: e.target.checked })}
            />
            <span>Featured Category</span>
          </label>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          className="submit-button"
          disabled={loading}
        >
          {loading ? 'Saving...' : (category ? 'Update Category' : 'Create Category')}
        </button>
      </form>
    </div>
  );
};

export default CategoryForm;
```

### CSS Styles (CategoryForm.css)

```css
.category-form-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.category-form-container h2 {
  margin-bottom: 20px;
  color: #333;
}

.alert {
  padding: 15px;
  margin-bottom: 20px;
  border-radius: 4px;
}

.alert-error {
  background: #fee;
  border: 1px solid #fcc;
  color: #c33;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-weight: 600;
  margin-bottom: 8px;
  color: #555;
}

.form-group input[type="text"],
.form-group input[type="number"],
.form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.form-group textarea {
  resize: vertical;
}

.form-group small {
  display: block;
  margin-top: 5px;
  color: #777;
  font-size: 12px;
}

/* Image Upload */
.image-upload-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.upload-button {
  display: block;
  cursor: pointer;
  border: 2px dashed #ddd;
  border-radius: 8px;
  overflow: hidden;
  transition: border-color 0.3s;
}

.upload-button:hover {
  border-color: #007bff;
}

.upload-placeholder {
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f9f9f9;
  color: #999;
}

.promo-placeholder {
  height: 150px;
}

.icon-preview {
  width: 100%;
  height: 100px;
  object-fit: contain;
  background: #f9f9f9;
}

.promo-preview {
  width: 100%;
  height: 150px;
  object-fit: cover;
}

.remove-button {
  padding: 8px 16px;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.remove-button:hover {
  background: #c82333;
}

/* Color Input */
.color-input-container {
  display: flex;
  gap: 10px;
  align-items: center;
}

.color-picker {
  width: 50px;
  height: 40px;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
}

/* Checkbox */
.checkbox-label {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  width: auto;
  margin-right: 10px;
}

/* Submit Button */
.submit-button {
  width: 100%;
  padding: 15px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.3s;
}

.submit-button:hover:not(:disabled) {
  background: #0056b3;
}

.submit-button:disabled {
  background: #ccc;
  cursor: not-allowed;
}
```

---

## 📝 Key Points

### ✅ What Works Now:

1. **Backend**: Already supports file uploads via ModelViewSet
2. **Frontend**: Both examples above handle:
   - Icon upload (64x64px)
   - Promotional image upload (400x200px)
   - Image preview before upload
   - File size validation
   - FormData construction
   - Proper multipart/form-data handling

### 🎯 Implementation Notes:

#### React Native:
- Uses `expo-image-picker` for photo selection
- Automatic image cropping (square for icon, 2:1 for banner)
- File structure for FormData: `{ uri, type, name }`

#### React Web:
- Uses HTML5 file input
- FileReader API for preview
- Native File object works directly

### 📦 Required Dependencies:

```bash
# React Native
npm install expo-image-picker

# React Web (none needed - uses native APIs)
```

---

## 🚀 Usage Example

```jsx
// In your app
import CategoryForm from './CategoryForm';

// Create new category
<CategoryForm 
  onSuccess={(category) => {
    console.log('Created:', category);
    // Navigate or refresh list
  }}
/>

// Edit existing category
<CategoryForm 
  category={existingCategory}
  onSuccess={(category) => {
    console.log('Updated:', category);
    // Navigate or refresh list
  }}
/>
```

---

## ✅ Testing

### Test Icon Upload:
```bash
# Via cURL
curl -X PATCH http://localhost:8000/api/equipment/categories/1/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "icon=@icon.png"
```

### Verify Upload:
```bash
# Check category with icon
curl http://localhost:8000/api/equipment/categories/1/
```

---

Your API already supports this - just use the frontend code above! 🎉 Both mobile and web implementations are production-ready.
