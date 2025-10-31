# Tags System - Complete Guide

## What Are Tags?

**Tags** are keywords or labels that you attach to equipment to make them easier to find and categorize. Think of them as flexible, searchable attributes beyond the main category.

### Examples:
- A Caterpillar excavator might have tags: `["Heavy Equipment", "Construction", "Mining", "Excavation", "Hydraulic"]`
- A concrete mixer might have tags: `["Construction", "Mixing", "Portable"]`
- A generator might have tags: `["Power", "Emergency", "Diesel", "Portable"]`

### Why Tags Matter:
1. **Better Search**: Users can find equipment by searching for specific features or use cases
2. **Flexible Categorization**: One piece of equipment can belong to multiple categories conceptually
3. **Filtering**: Users can filter equipment lists by multiple tags at once
4. **Discoverability**: Related equipment can be grouped together even if in different categories

---

## How Tags Work Technically

### 1. Database Structure (Many-to-Many Relationship)

Tags use a **Many-to-Many** relationship with Equipment:

```python
# equipment/models.py

class Tag(models.Model):
    """Simple tag model - just a unique name"""
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class Equipment(models.Model):
    # ... other fields ...
    
    # Many-to-Many: One equipment can have many tags
    # One tag can belong to many equipment
    tags = models.ManyToManyField(Tag, related_name='equipment', blank=True)
```

**Visual Representation:**
```
Equipment 1: Excavator ──┐
                         ├──> Tag: "Heavy Equipment"
Equipment 2: Bulldozer ──┘

Equipment 1: Excavator ──┐
                         ├──> Tag: "Construction"
Equipment 3: Mixer    ────┘

Equipment 1: Excavator ────> Tag: "Mining"
```

One excavator has multiple tags, and one tag (like "Heavy Equipment") can apply to multiple pieces of equipment.

---

## 2. Creating Equipment with Tags

### Backend: Auto-Creation of Tags

When you create equipment, you send an array of tag names. The system automatically creates tags if they don't exist:

```python
# equipment/serializers.py (EquipmentCreateSerializer)

def create(self, validated_data):
    tag_names = validated_data.pop('tag_names', [])
    
    # Create equipment first
    equipment = super().create(validated_data)
    
    # Handle tags - get_or_create ensures tags are created if needed
    if tag_names:
        for tag_name in tag_names:
            tag, created = Tag.objects.get_or_create(name=tag_name.strip())
            equipment.tags.add(tag)
    
    return equipment
```

**What happens:**
1. You send: `tag_names: ["Construction", "Heavy Equipment", "New Tag"]`
2. System checks: Does "Construction" exist? → If yes, use it. If no, create it.
3. System checks: Does "Heavy Equipment" exist? → Same process.
4. System checks: Does "New Tag" exist? → Creates it!
5. All tags are linked to your equipment.

### Frontend: Sending Tags

**React/React Native Example:**
```javascript
const createEquipment = async (equipmentData) => {
  const formData = new FormData();
  
  // Basic equipment data
  formData.append('name', 'Caterpillar 320 Excavator');
  formData.append('description', 'Heavy-duty excavator...');
  formData.append('daily_rate', '500');
  formData.append('category_id', '1');
  
  // Add tags as JSON array
  const tags = ['Heavy Equipment', 'Construction', 'Mining'];
  formData.append('tag_names', JSON.stringify(tags));
  
  // ... add images, etc ...
  
  const response = await fetch('http://localhost:8000/api/equipment/equipment/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
    },
    body: formData,
  });
};
```

---

## 3. Filtering Equipment by Tags

### API Usage

You can filter equipment by one or more tags using the `tags` query parameter:

```bash
# Filter by single tag
GET /api/equipment/equipment/?tags=Construction

# Filter by multiple tags (comma-separated)
GET /api/equipment/equipment/?tags=Construction,Mining

# Combined with other filters
GET /api/equipment/equipment/?tags=Heavy Equipment&category=1&status=available
```

### Backend Implementation

```python
# equipment/views.py (EquipmentViewSet)

def get_queryset(self):
    queryset = Equipment.objects.all()
    
    # Tag filtering
    tags = self.request.query_params.get('tags', None)
    if tags:
        # Split comma-separated tags
        tag_list = [tag.strip() for tag in tags.split(',')]
        
        # Filter equipment that has ANY of these tags
        queryset = queryset.filter(tags__name__in=tag_list).distinct()
    
    return queryset
```

**How it works:**
- `tags__name__in=tag_list` → SQL: Find equipment where tag name is in the list
- `.distinct()` → Remove duplicates (equipment with multiple matching tags)

### Frontend: Filtering by Tags

```javascript
const filterEquipment = async (selectedTags) => {
  // selectedTags = ['Construction', 'Mining']
  const tagsParam = selectedTags.join(','); // 'Construction,Mining'
  
  const response = await fetch(
    `http://localhost:8000/api/equipment/equipment/?tags=${tagsParam}`,
    {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
      },
    }
  );
  
  const data = await response.json();
  return data.results; // Filtered equipment
};
```

---

## 4. Getting All Available Tags

### API Endpoint

```bash
GET /api/equipment/equipment/tags/
```

**Response:**
```json
{
  "tags": [
    "Construction",
    "Excavation",
    "Heavy Equipment",
    "Hydraulic",
    "Mining",
    "Portable",
    "Power"
  ]
}
```

### Backend Implementation

```python
# equipment/views.py (EquipmentViewSet)

@action(detail=False, methods=['get'])
def tags(self, request):
    """Get all available tags"""
    tags = Tag.objects.all()
    return Response({'tags': [tag.name for tag in tags]})
```

### Frontend: Fetching Tags for Dropdown/Picker

```javascript
const fetchAvailableTags = async () => {
  const response = await fetch(
    'http://localhost:8000/api/equipment/equipment/tags/',
    {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
      },
    }
  );
  
  const data = await response.json();
  return data.tags; // Array of tag names
};

// Use in a select/picker component
const TagPicker = () => {
  const [availableTags, setAvailableTags] = useState([]);
  const [selectedTags, setSelectedTags] = useState([]);
  
  useEffect(() => {
    fetchAvailableTags().then(setAvailableTags);
  }, []);
  
  // Render tag selection UI...
};
```

---

## 5. Tag Data in API Responses

### Creating Equipment (Response)

```json
POST /api/equipment/equipment/
```

**Response includes tags as objects:**
```json
{
  "id": 1,
  "name": "Caterpillar 320 Excavator",
  "description": "...",
  "daily_rate": "500.00",
  "category": {
    "id": 1,
    "name": "Excavators"
  },
  "tags": [
    {"id": 1, "name": "Heavy Equipment"},
    {"id": 2, "name": "Construction"},
    {"id": 3, "name": "Mining"}
  ],
  "images": [...],
  "created_at": "2024-01-15T10:00:00Z"
}
```

### Listing Equipment (Response)

```json
GET /api/equipment/equipment/
```

**Response includes tags as simple strings for efficiency:**
```json
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "name": "Caterpillar 320 Excavator",
      "description": "...",
      "daily_rate": "500.00",
      "category": "Excavators",
      "tags": ["Heavy Equipment", "Construction", "Mining"],
      "primary_image": "http://localhost:8000/media/...",
      "status": "available"
    },
    {
      "id": 2,
      "name": "Concrete Mixer",
      "tags": ["Construction", "Mixing", "Portable"],
      ...
    }
  ]
}
```

---

## Frontend Integration Examples

### React Native: Tag Input Component

```jsx
import React, { useState, useEffect } from 'react';
import { View, Text, TextInput, TouchableOpacity, FlatList, StyleSheet } from 'react-native';

const TagInput = ({ selectedTags, onTagsChange }) => {
  const [availableTags, setAvailableTags] = useState([]);
  const [searchText, setSearchText] = useState('');
  const [filteredTags, setFilteredTags] = useState([]);

  useEffect(() => {
    // Fetch available tags from API
    fetchAvailableTags().then(setAvailableTags);
  }, []);

  useEffect(() => {
    // Filter tags based on search
    if (searchText) {
      const filtered = availableTags.filter(tag =>
        tag.toLowerCase().includes(searchText.toLowerCase()) &&
        !selectedTags.includes(tag)
      );
      setFilteredTags(filtered);
    } else {
      setFilteredTags([]);
    }
  }, [searchText, availableTags, selectedTags]);

  const addTag = (tag) => {
    if (!selectedTags.includes(tag)) {
      onTagsChange([...selectedTags, tag]);
      setSearchText('');
    }
  };

  const removeTag = (tagToRemove) => {
    onTagsChange(selectedTags.filter(tag => tag !== tagToRemove));
  };

  const addCustomTag = () => {
    if (searchText.trim() && !selectedTags.includes(searchText.trim())) {
      onTagsChange([...selectedTags, searchText.trim()]);
      setSearchText('');
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.label}>Tags</Text>
      
      {/* Selected Tags */}
      <View style={styles.selectedTagsContainer}>
        {selectedTags.map((tag, index) => (
          <TouchableOpacity
            key={index}
            style={styles.tagPill}
            onPress={() => removeTag(tag)}
          >
            <Text style={styles.tagText}>{tag}</Text>
            <Text style={styles.removeIcon}>×</Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Tag Input */}
      <TextInput
        style={styles.input}
        placeholder="Add tags (e.g., Construction, Mining)..."
        value={searchText}
        onChangeText={setSearchText}
        onSubmitEditing={addCustomTag}
      />

      {/* Suggested Tags */}
      {filteredTags.length > 0 && (
        <FlatList
          data={filteredTags}
          keyExtractor={(item, index) => index.toString()}
          renderItem={({ item }) => (
            <TouchableOpacity
              style={styles.suggestionItem}
              onPress={() => addTag(item)}
            >
              <Text style={styles.suggestionText}>{item}</Text>
            </TouchableOpacity>
          )}
          style={styles.suggestions}
        />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginVertical: 10,
  },
  label: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  selectedTagsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 10,
  },
  tagPill: {
    backgroundColor: '#007AFF',
    borderRadius: 16,
    paddingHorizontal: 12,
    paddingVertical: 6,
    marginRight: 8,
    marginBottom: 8,
    flexDirection: 'row',
    alignItems: 'center',
  },
  tagText: {
    color: 'white',
    marginRight: 4,
  },
  removeIcon: {
    color: 'white',
    fontSize: 20,
    fontWeight: 'bold',
  },
  input: {
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
  },
  suggestions: {
    maxHeight: 150,
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 8,
    marginTop: 8,
  },
  suggestionItem: {
    padding: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  suggestionText: {
    fontSize: 16,
  },
});

export default TagInput;
```

### React Web: Tag Filter Component

```jsx
import React, { useState, useEffect } from 'react';
import './TagFilter.css';

const TagFilter = ({ onFilterChange }) => {
  const [availableTags, setAvailableTags] = useState([]);
  const [selectedTags, setSelectedTags] = useState([]);

  useEffect(() => {
    // Fetch all available tags
    fetch('http://localhost:8000/api/equipment/equipment/tags/', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
      },
    })
      .then(res => res.json())
      .then(data => setAvailableTags(data.tags));
  }, []);

  const toggleTag = (tag) => {
    let newSelectedTags;
    if (selectedTags.includes(tag)) {
      newSelectedTags = selectedTags.filter(t => t !== tag);
    } else {
      newSelectedTags = [...selectedTags, tag];
    }
    setSelectedTags(newSelectedTags);
    onFilterChange(newSelectedTags);
  };

  return (
    <div className="tag-filter">
      <h3>Filter by Tags</h3>
      <div className="tag-cloud">
        {availableTags.map((tag, index) => (
          <button
            key={index}
            className={`tag-button ${selectedTags.includes(tag) ? 'active' : ''}`}
            onClick={() => toggleTag(tag)}
          >
            {tag}
            {selectedTags.includes(tag) && <span className="checkmark">✓</span>}
          </button>
        ))}
      </div>
      {selectedTags.length > 0 && (
        <div className="selected-filters">
          <strong>Active Filters:</strong> {selectedTags.join(', ')}
          <button onClick={() => {
            setSelectedTags([]);
            onFilterChange([]);
          }}>
            Clear All
          </button>
        </div>
      )}
    </div>
  );
};

export default TagFilter;
```

**CSS (TagFilter.css):**
```css
.tag-filter {
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  margin-bottom: 20px;
}

.tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 10px;
}

.tag-button {
  padding: 8px 16px;
  border: 2px solid #007AFF;
  background: white;
  color: #007AFF;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.tag-button:hover {
  background: #f0f0f0;
}

.tag-button.active {
  background: #007AFF;
  color: white;
}

.checkmark {
  margin-left: 5px;
  font-weight: bold;
}

.selected-filters {
  margin-top: 15px;
  padding: 10px;
  background: #f9f9f9;
  border-radius: 4px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.selected-filters button {
  padding: 5px 10px;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
```

---

## Complete Workflow Example

### Scenario: User Creates Equipment with Tags

**Step 1: User fills form**
```
Name: Caterpillar 320 Excavator
Description: Heavy-duty excavator...
Category: Excavators
Tags: [Heavy Equipment, Construction, Mining] (user selects/types)
Daily Rate: $500
Images: [photo1.jpg, photo2.jpg]
```

**Step 2: Frontend sends POST request**
```javascript
const formData = new FormData();
formData.append('name', 'Caterpillar 320 Excavator');
formData.append('description', 'Heavy-duty excavator...');
formData.append('category_id', '1');
formData.append('tag_names', JSON.stringify(['Heavy Equipment', 'Construction', 'Mining']));
formData.append('daily_rate', '500');
formData.append('images', photo1);
formData.append('images', photo2);

fetch('http://localhost:8000/api/equipment/equipment/', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` },
  body: formData,
});
```

**Step 3: Backend processes**
1. Creates Equipment object
2. For each tag name:
   - Checks if "Heavy Equipment" exists → Creates if new
   - Checks if "Construction" exists → Creates if new
   - Checks if "Mining" exists → Creates if new
3. Links all tags to equipment via many-to-many relationship
4. Saves images
5. Returns response with full equipment data including tags

**Step 4: User searches for equipment**
```javascript
// User clicks "Construction" filter
fetch('http://localhost:8000/api/equipment/equipment/?tags=Construction')
```

**Step 5: Backend returns all equipment with "Construction" tag**
```json
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "name": "Caterpillar 320 Excavator",
      "tags": ["Heavy Equipment", "Construction", "Mining"],
      ...
    },
    {
      "id": 5,
      "name": "Concrete Mixer",
      "tags": ["Construction", "Mixing"],
      ...
    }
  ]
}
```

---

## Use Cases

### 1. Equipment Search
User searches for "Construction" → Finds all excavators, mixers, loaders tagged with "Construction"

### 2. Multiple Filter Combination
User filters by:
- Category: "Heavy Machinery"
- Tags: "Construction, Mining"
- Status: "Available"
→ Finds excavators available for construction/mining work

### 3. Related Equipment Discovery
User views an excavator → System shows "Equipment with similar tags" → Suggests other construction equipment

### 4. Popular Tags Display
Homepage shows most popular tags as quick filters → Users click to explore equipment

### 5. Tag-based Recommendations
"People who rented equipment tagged with 'Construction' also rented..." → Cross-selling

---

## Summary

**Tags are:**
- ✅ Flexible keywords for equipment
- ✅ Automatically created when used
- ✅ Many-to-many relationship (one equipment → many tags, one tag → many equipment)
- ✅ Used for filtering and search
- ✅ Returned as objects in detail views, strings in list views

**Key Endpoints:**
- `POST /api/equipment/equipment/` with `tag_names: ["tag1", "tag2"]` → Create equipment with tags
- `GET /api/equipment/equipment/?tags=tag1,tag2` → Filter equipment by tags
- `GET /api/equipment/equipment/tags/` → Get all available tags

**Frontend Integration:**
- Use TagInput component for creating equipment
- Use TagFilter component for filtering equipment
- Fetch available tags from `/tags/` endpoint
- Send tag names as JSON array in FormData

---

## Quick Reference

```bash
# Get all tags
GET /api/equipment/equipment/tags/

# Create equipment with tags
POST /api/equipment/equipment/
{
  "name": "Excavator",
  "tag_names": ["Construction", "Mining"],
  ...
}

# Filter by single tag
GET /api/equipment/equipment/?tags=Construction

# Filter by multiple tags
GET /api/equipment/equipment/?tags=Construction,Mining

# Combine with other filters
GET /api/equipment/equipment/?tags=Construction&category=1&status=available
```

**That's it!** Tags provide a powerful, flexible way to categorize and find equipment. 🏷️
