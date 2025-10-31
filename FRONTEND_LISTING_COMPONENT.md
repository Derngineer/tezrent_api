# Equipment Listing - Complete Frontend Integration

## 🎯 Overview

This guide provides production-ready React components for creating equipment listings that perfectly match your TezRent API.

---

## 📋 API Field Mapping Reference

### Required Fields (Must Include)
```javascript
{
  // Basic Info
  name: string,              // Equipment name
  description: string,       // Detailed description
  
  // Category (choose ONE)
  category_id: number,       // Existing category ID
  // OR
  category_name: string,     // New category name
  
  // Technical
  manufacturer: string,      // e.g., "Caterpillar"
  model_number: string,      // e.g., "320D2 L"
  year: number,             // e.g., 2022
  weight: string,           // e.g., "22500.00" (in kg)
  dimensions: string,       // e.g., "996 x 294 x 323" (LxWxH cm)
  
  // Pricing
  daily_rate: string,       // e.g., "1500.00"
  weekly_rate: string,      // e.g., "9000.00"
  monthly_rate: string,     // e.g., "32000.00"
  
  // Location
  country: string,          // "UAE" or "UZB"
  city: string,            // "DXB", "AUH", "SHJ", etc.
  
  // Availability
  total_units: number,      // e.g., 3
  available_units: number   // e.g., 3
}
```

### Optional Fields
```javascript
{
  fuel_type: string,                    // "Diesel", "Gasoline", "Electric"
  status: string,                       // "available", "maintenance", "rented"
  featured: boolean,                    // true/false
  
  // Tags (array of strings)
  tag_names: ["tag1", "tag2"],
  
  // Specifications (array of objects)
  specifications_data: [
    {name: "Engine Power", value: "121 kW"}
  ],
  
  // Promotional
  is_todays_deal: boolean,
  deal_discount_percentage: number,     // 0-100
  promotion_badge: string,              // "HOT DEAL", "LIMITED TIME"
  promotion_description: string
}
```

### Image Upload
```javascript
// Images must be sent as FormData
// Key name: "images" (plural)
// Max: 7 images
formData.append('images', file1);
formData.append('images', file2);
```

---

## 🚀 Complete React Component

```jsx
import React, { useState, useEffect } from 'react';
import './CreateEquipment.css'; // Add your styles

const API_BASE = 'http://localhost:8000/api';

const CreateEquipmentListing = () => {
  // State for form data
  const [formData, setFormData] = useState({
    // Basic Information
    name: '',
    description: '',
    category_id: '',
    
    // Technical Specifications
    manufacturer: '',
    model_number: '',
    year: new Date().getFullYear(),
    weight: '',
    dimensions: '',
    fuel_type: 'Diesel',
    
    // Pricing
    daily_rate: '',
    weekly_rate: '',
    monthly_rate: '',
    
    // Location
    country: 'UAE',
    city: 'DXB',
    
    // Availability
    total_units: 1,
    available_units: 1,
    status: 'available',
    featured: false,
    
    // Optional promotional
    is_todays_deal: false,
    deal_discount_percentage: 0,
    promotion_badge: '',
    promotion_description: ''
  });

  // State for dynamic fields
  const [categories, setCategories] = useState([]);
  const [images, setImages] = useState([]);
  const [imagePreviews, setImagePreviews] = useState([]);
  const [tags, setTags] = useState([]);
  const [tagInput, setTagInput] = useState('');
  const [specifications, setSpecifications] = useState([]);
  
  // State for UI
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  // City options based on country
  const cityOptions = {
    UAE: [
      { code: 'DXB', name: 'Dubai' },
      { code: 'AUH', name: 'Abu Dhabi' },
      { code: 'SHJ', name: 'Sharjah' },
      { code: 'AJM', name: 'Ajman' },
      { code: 'UAQ', name: 'Umm Al Quwain' },
      { code: 'FUJ', name: 'Fujairah' },
      { code: 'RAK', name: 'Ras Al Khaimah' }
    ],
    UZB: [
      { code: 'TAS', name: 'Tashkent' },
      { code: 'SAM', name: 'Samarkand' },
      { code: 'NAM', name: 'Namangan' },
      { code: 'AND', name: 'Andijan' }
    ]
  };

  // Fetch categories on mount
  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    try {
      const response = await fetch(`${API_BASE}/equipment/categories/choices/`);
      const data = await response.json();
      setCategories(data.categories || []);
    } catch (err) {
      console.error('Error fetching categories:', err);
      setError('Failed to load categories');
    }
  };

  // Handle input changes
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));

    // Reset city when country changes
    if (name === 'country') {
      setFormData(prev => ({
        ...prev,
        city: cityOptions[value][0].code
      }));
    }
  };

  // Handle image selection
  const handleImageChange = (e) => {
    const files = Array.from(e.target.files);
    
    if (files.length + images.length > 7) {
      setError('Maximum 7 images allowed');
      return;
    }

    setImages(prev => [...prev, ...files]);

    // Generate previews
    files.forEach(file => {
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreviews(prev => [...prev, reader.result]);
      };
      reader.readAsDataURL(file);
    });

    setError(null);
  };

  // Remove image
  const removeImage = (index) => {
    setImages(prev => prev.filter((_, i) => i !== index));
    setImagePreviews(prev => prev.filter((_, i) => i !== index));
  };

  // Handle tags
  const addTag = () => {
    const trimmed = tagInput.trim();
    if (trimmed && !tags.includes(trimmed)) {
      setTags(prev => [...prev, trimmed]);
      setTagInput('');
    }
  };

  const removeTag = (tagToRemove) => {
    setTags(prev => prev.filter(tag => tag !== tagToRemove));
  };

  // Handle specifications
  const addSpecification = () => {
    setSpecifications(prev => [...prev, { name: '', value: '' }]);
  };

  const updateSpecification = (index, field, value) => {
    setSpecifications(prev => {
      const updated = [...prev];
      updated[index][field] = value;
      return updated;
    });
  };

  const removeSpecification = (index) => {
    setSpecifications(prev => prev.filter((_, i) => i !== index));
  };

  // Calculate weekly rate suggestion
  const suggestWeeklyRate = () => {
    if (formData.daily_rate) {
      return (parseFloat(formData.daily_rate) * 6).toFixed(2); // 6 days price for weekly
    }
    return '';
  };

  // Calculate monthly rate suggestion
  const suggestMonthlyRate = () => {
    if (formData.daily_rate) {
      return (parseFloat(formData.daily_rate) * 25).toFixed(2); // 25 days price for monthly
    }
    return '';
  };

  // Form validation
  const validateForm = () => {
    const required = [
      'name', 'description', 'category_id', 'manufacturer', 
      'model_number', 'year', 'weight', 'dimensions',
      'daily_rate', 'weekly_rate', 'monthly_rate',
      'country', 'city', 'total_units', 'available_units'
    ];

    for (let field of required) {
      if (!formData[field] || formData[field] === '') {
        setError(`${field.replace('_', ' ')} is required`);
        return false;
      }
    }

    if (parseInt(formData.available_units) > parseInt(formData.total_units)) {
      setError('Available units cannot exceed total units');
      return false;
    }

    if (images.length === 0) {
      if (!window.confirm('No images added. Continue without images?')) {
        return false;
      }
    }

    return true;
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(false);

    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      // Create FormData object
      const data = new FormData();

      // Append all form fields
      Object.keys(formData).forEach(key => {
        if (formData[key] !== '' && formData[key] !== null) {
          data.append(key, formData[key]);
        }
      });

      // Append tags as JSON string
      if (tags.length > 0) {
        data.append('tag_names', JSON.stringify(tags));
      }

      // Append specifications as JSON string
      if (specifications.length > 0) {
        const validSpecs = specifications.filter(spec => spec.name && spec.value);
        if (validSpecs.length > 0) {
          data.append('specifications_data', JSON.stringify(validSpecs));
        }
      }

      // Append images
      images.forEach(image => {
        data.append('images', image);
      });

      // Get auth token
      const token = localStorage.getItem('access_token');
      if (!token) {
        setError('You must be logged in to create equipment listings');
        setLoading(false);
        return;
      }

      // Make API request
      const response = await fetch(`${API_BASE}/equipment/equipment/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
          // Don't set Content-Type - browser will set it with boundary
        },
        body: data
      });

      if (response.ok) {
        const result = await response.json();
        setSuccess(true);
        setError(null);
        console.log('Equipment created:', result);
        
        // Reset form or redirect
        setTimeout(() => {
          window.location.href = `/equipment/${result.id}`;
        }, 2000);
      } else {
        const errorData = await response.json();
        console.error('API Error:', errorData);
        setError(JSON.stringify(errorData, null, 2));
      }
    } catch (err) {
      console.error('Network error:', err);
      setError('Network error. Please check your connection and try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="create-equipment-container">
      <h1>Create Equipment Listing</h1>

      {error && (
        <div className="alert alert-error">
          <strong>Error:</strong> <pre>{error}</pre>
        </div>
      )}

      {success && (
        <div className="alert alert-success">
          ✅ Equipment created successfully! Redirecting...
        </div>
      )}

      <form onSubmit={handleSubmit} encType="multipart/form-data">
        {/* Basic Information */}
        <section className="form-section">
          <h2>📋 Basic Information</h2>
          
          <div className="form-group">
            <label htmlFor="name">Equipment Name *</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              placeholder="e.g., Caterpillar 320D2 Hydraulic Excavator"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="description">Description *</label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              rows="6"
              placeholder="Provide detailed description including features, capabilities, and ideal use cases..."
              required
            />
            <small>{formData.description.length} characters</small>
          </div>

          <div className="form-group">
            <label htmlFor="category_id">Category *</label>
            <select
              id="category_id"
              name="category_id"
              value={formData.category_id}
              onChange={handleChange}
              required
            >
              <option value="">-- Select Category --</option>
              {categories.map(cat => (
                <option key={cat.id} value={cat.id}>
                  {cat.name}
                </option>
              ))}
            </select>
            <small>
              Don't see your category? Contact admin to add new categories.
            </small>
          </div>
        </section>

        {/* Technical Specifications */}
        <section className="form-section">
          <h2>🔧 Technical Specifications</h2>
          
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="manufacturer">Manufacturer *</label>
              <input
                type="text"
                id="manufacturer"
                name="manufacturer"
                value={formData.manufacturer}
                onChange={handleChange}
                placeholder="e.g., Caterpillar"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="model_number">Model Number *</label>
              <input
                type="text"
                id="model_number"
                name="model_number"
                value={formData.model_number}
                onChange={handleChange}
                placeholder="e.g., 320D2 L"
                required
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="year">Year *</label>
              <input
                type="number"
                id="year"
                name="year"
                value={formData.year}
                onChange={handleChange}
                min="1980"
                max={new Date().getFullYear() + 1}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="weight">Weight (kg) *</label>
              <input
                type="number"
                step="0.01"
                id="weight"
                name="weight"
                value={formData.weight}
                onChange={handleChange}
                placeholder="e.g., 22500"
                required
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="dimensions">Dimensions (L x W x H in cm) *</label>
              <input
                type="text"
                id="dimensions"
                name="dimensions"
                value={formData.dimensions}
                onChange={handleChange}
                placeholder="e.g., 996 x 294 x 323"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="fuel_type">Fuel Type</label>
              <select
                id="fuel_type"
                name="fuel_type"
                value={formData.fuel_type}
                onChange={handleChange}
              >
                <option value="Diesel">Diesel</option>
                <option value="Gasoline">Gasoline</option>
                <option value="Electric">Electric</option>
                <option value="Hybrid">Hybrid</option>
                <option value="LPG">LPG</option>
              </select>
            </div>
          </div>
        </section>

        {/* Pricing */}
        <section className="form-section">
          <h2>💰 Pricing</h2>
          
          <div className="form-group">
            <label htmlFor="daily_rate">Daily Rate (AED) *</label>
            <input
              type="number"
              step="0.01"
              id="daily_rate"
              name="daily_rate"
              value={formData.daily_rate}
              onChange={handleChange}
              placeholder="e.g., 1500.00"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="weekly_rate">Weekly Rate (AED) *</label>
            <div className="input-with-suggestion">
              <input
                type="number"
                step="0.01"
                id="weekly_rate"
                name="weekly_rate"
                value={formData.weekly_rate}
                onChange={handleChange}
                placeholder="e.g., 9000.00"
                required
              />
              {suggestWeeklyRate() && (
                <button
                  type="button"
                  className="btn-suggestion"
                  onClick={() => setFormData(prev => ({
                    ...prev,
                    weekly_rate: suggestWeeklyRate()
                  }))}
                >
                  Suggest: {suggestWeeklyRate()} AED
                </button>
              )}
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="monthly_rate">Monthly Rate (AED) *</label>
            <div className="input-with-suggestion">
              <input
                type="number"
                step="0.01"
                id="monthly_rate"
                name="monthly_rate"
                value={formData.monthly_rate}
                onChange={handleChange}
                placeholder="e.g., 32000.00"
                required
              />
              {suggestMonthlyRate() && (
                <button
                  type="button"
                  className="btn-suggestion"
                  onClick={() => setFormData(prev => ({
                    ...prev,
                    monthly_rate: suggestMonthlyRate()
                  }))}
                >
                  Suggest: {suggestMonthlyRate()} AED
                </button>
              )}
            </div>
          </div>
        </section>

        {/* Location */}
        <section className="form-section">
          <h2>📍 Location</h2>
          
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="country">Country *</label>
              <select
                id="country"
                name="country"
                value={formData.country}
                onChange={handleChange}
                required
              >
                <option value="UAE">United Arab Emirates</option>
                <option value="UZB">Uzbekistan</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="city">City *</label>
              <select
                id="city"
                name="city"
                value={formData.city}
                onChange={handleChange}
                required
              >
                {cityOptions[formData.country].map(city => (
                  <option key={city.code} value={city.code}>
                    {city.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </section>

        {/* Availability */}
        <section className="form-section">
          <h2>📦 Availability</h2>
          
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="total_units">Total Units *</label>
              <input
                type="number"
                id="total_units"
                name="total_units"
                value={formData.total_units}
                onChange={handleChange}
                min="1"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="available_units">Available Units *</label>
              <input
                type="number"
                id="available_units"
                name="available_units"
                value={formData.available_units}
                onChange={handleChange}
                min="0"
                max={formData.total_units}
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="status">Status</label>
            <select
              id="status"
              name="status"
              value={formData.status}
              onChange={handleChange}
            >
              <option value="available">Available</option>
              <option value="maintenance">Under Maintenance</option>
              <option value="reserved">Reserved</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>

          <div className="form-group checkbox-group">
            <label>
              <input
                type="checkbox"
                name="featured"
                checked={formData.featured}
                onChange={handleChange}
              />
              <span>⭐ Featured Equipment (Show in featured section)</span>
            </label>
          </div>
        </section>

        {/* Images */}
        <section className="form-section">
          <h2>📸 Images (Max 7)</h2>
          
          <div className="form-group">
            <input
              type="file"
              accept="image/*"
              multiple
              onChange={handleImageChange}
              id="images"
            />
            <label htmlFor="images" className="file-upload-label">
              Choose Images (Max 7)
            </label>
            <small>First image will be the primary image</small>
          </div>

          {imagePreviews.length > 0 && (
            <div className="image-preview-grid">
              {imagePreviews.map((preview, index) => (
                <div key={index} className="image-preview-item">
                  <img src={preview} alt={`Preview ${index + 1}`} />
                  {index === 0 && <span className="primary-badge">Primary</span>}
                  <button
                    type="button"
                    className="btn-remove-image"
                    onClick={() => removeImage(index)}
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Tags */}
        <section className="form-section">
          <h2>🏷️ Tags</h2>
          
          <div className="form-group">
            <div className="tag-input-container">
              <input
                type="text"
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    addTag();
                  }
                }}
                placeholder="Add tag (e.g., Heavy Equipment, Construction)"
              />
              <button type="button" onClick={addTag} className="btn-add">
                Add Tag
              </button>
            </div>
          </div>

          {tags.length > 0 && (
            <div className="tag-list">
              {tags.map(tag => (
                <span key={tag} className="tag-item">
                  {tag}
                  <button type="button" onClick={() => removeTag(tag)}>×</button>
                </span>
              ))}
            </div>
          )}
        </section>

        {/* Additional Specifications */}
        <section className="form-section">
          <h2>📊 Additional Specifications</h2>
          
          <button
            type="button"
            onClick={addSpecification}
            className="btn-add-spec"
          >
            + Add Specification
          </button>

          {specifications.map((spec, index) => (
            <div key={index} className="spec-row">
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
              <button
                type="button"
                onClick={() => removeSpecification(index)}
                className="btn-remove"
              >
                Remove
              </button>
            </div>
          ))}
        </section>

        {/* Promotional (Optional) */}
        <section className="form-section">
          <h2>🎉 Promotional (Optional)</h2>
          
          <div className="form-group checkbox-group">
            <label>
              <input
                type="checkbox"
                name="is_todays_deal"
                checked={formData.is_todays_deal}
                onChange={handleChange}
              />
              <span>🔥 Today's Deal</span>
            </label>
          </div>

          {formData.is_todays_deal && (
            <>
              <div className="form-group">
                <label htmlFor="deal_discount_percentage">Discount Percentage</label>
                <input
                  type="number"
                  id="deal_discount_percentage"
                  name="deal_discount_percentage"
                  value={formData.deal_discount_percentage}
                  onChange={handleChange}
                  min="0"
                  max="100"
                  placeholder="e.g., 15"
                />
              </div>

              <div className="form-group">
                <label htmlFor="promotion_badge">Promotion Badge</label>
                <input
                  type="text"
                  id="promotion_badge"
                  name="promotion_badge"
                  value={formData.promotion_badge}
                  onChange={handleChange}
                  placeholder="e.g., HOT DEAL, LIMITED TIME"
                />
              </div>

              <div className="form-group">
                <label htmlFor="promotion_description">Promotion Description</label>
                <textarea
                  id="promotion_description"
                  name="promotion_description"
                  value={formData.promotion_description}
                  onChange={handleChange}
                  rows="3"
                  placeholder="e.g., Save 300 AED/day! Limited time offer..."
                />
              </div>
            </>
          )}
        </section>

        {/* Submit Button */}
        <div className="form-actions">
          <button
            type="submit"
            className="btn-submit"
            disabled={loading}
          >
            {loading ? 'Creating...' : 'Create Equipment Listing'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default CreateEquipmentListing;
```

---

## 🎨 Basic CSS Styles

```css
/* CreateEquipment.css */

.create-equipment-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
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

.alert-success {
  background: #efe;
  border: 1px solid #cfc;
  color: #3c3;
}

.form-section {
  background: #fff;
  padding: 20px;
  margin-bottom: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.form-section h2 {
  margin-top: 0;
  color: #333;
  border-bottom: 2px solid #f0f0f0;
  padding-bottom: 10px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-weight: 600;
  margin-bottom: 5px;
  color: #555;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.form-group small {
  display: block;
  margin-top: 5px;
  color: #777;
  font-size: 12px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.input-with-suggestion {
  display: flex;
  gap: 10px;
  align-items: center;
}

.btn-suggestion {
  white-space: nowrap;
  padding: 8px 12px;
  background: #e7f3ff;
  border: 1px solid #007bff;
  color: #007bff;
  border-radius: 4px;
  cursor: pointer;
}

.checkbox-group label {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.checkbox-group input[type="checkbox"] {
  width: auto;
  margin-right: 10px;
}

/* Image Upload */
.file-upload-label {
  display: inline-block;
  padding: 10px 20px;
  background: #007bff;
  color: white;
  border-radius: 4px;
  cursor: pointer;
}

input[type="file"] {
  display: none;
}

.image-preview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 15px;
  margin-top: 15px;
}

.image-preview-item {
  position: relative;
  border: 2px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
}

.image-preview-item img {
  width: 100%;
  height: 150px;
  object-fit: cover;
}

.primary-badge {
  position: absolute;
  top: 5px;
  left: 5px;
  background: #28a745;
  color: white;
  padding: 3px 8px;
  border-radius: 3px;
  font-size: 11px;
  font-weight: bold;
}

.btn-remove-image {
  position: absolute;
  top: 5px;
  right: 5px;
  width: 25px;
  height: 25px;
  background: rgba(255, 0, 0, 0.8);
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  font-size: 18px;
  line-height: 1;
}

/* Tags */
.tag-input-container {
  display: flex;
  gap: 10px;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 10px;
}

.tag-item {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 5px 10px;
  background: #e7f3ff;
  border: 1px solid #007bff;
  color: #007bff;
  border-radius: 20px;
  font-size: 14px;
}

.tag-item button {
  background: none;
  border: none;
  color: #007bff;
  font-size: 18px;
  cursor: pointer;
  line-height: 1;
}

/* Specifications */
.spec-row {
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  gap: 10px;
  margin-bottom: 10px;
}

.btn-add-spec,
.btn-add {
  padding: 10px 15px;
  background: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-bottom: 15px;
}

.btn-remove {
  padding: 10px 15px;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

/* Submit */
.form-actions {
  text-align: center;
  margin-top: 30px;
}

.btn-submit {
  padding: 15px 40px;
  font-size: 16px;
  font-weight: bold;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.3s;
}

.btn-submit:hover:not(:disabled) {
  background: #0056b3;
}

.btn-submit:disabled {
  background: #ccc;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .form-row,
  .spec-row {
    grid-template-columns: 1fr;
  }
}
```

---

## ✅ Key Points for Frontend Integration

1. **Use FormData** - Required for file uploads
2. **Key name is "images"** - Not "uploaded_images"
3. **Send tags/specs as JSON strings** - `JSON.stringify(array)`
4. **Don't set Content-Type header** - Let browser handle it
5. **Include Authorization token** - `Bearer ${token}`
6. **Category ID is required** - Fetch categories first
7. **Use city codes** - DXB not "Dubai", AUH not "Abu Dhabi"
8. **Max 7 images** - Validate before submission

---

This component is production-ready and matches your API exactly! 🚀
