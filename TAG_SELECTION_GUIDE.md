# Tag Selection Guide - Using Existing Tags

## Overview

When creating equipment listings, users can either:
1. ✅ **Select from existing tags** (recommended for consistency)
2. ✅ **Create new tags** (typed manually)
3. ✅ **Mix both** (select existing + add new)

This guide shows how to fetch available tags and build a tag selection UI.

---

## API Endpoints

### 1. Get All Available Tags

```bash
GET /api/equipment/tags/
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Heavy Equipment"
  },
  {
    "id": 2,
    "name": "Construction"
  },
  {
    "id": 3,
    "name": "Mining"
  },
  {
    "id": 4,
    "name": "Excavation"
  },
  {
    "id": 5,
    "name": "Hydraulic"
  }
]
```

**Features:**
- ✅ No authentication required
- ✅ Returns all tags in alphabetical order
- ✅ Supports search: `?search=Construction`
- ✅ Can be used in dropdowns, autocomplete, or chip selectors

---

## Frontend Implementation

### React/Next.js - Tag Selection Component

```javascript
'use client'

import { useState, useEffect } from 'react'
import {
  Box,
  TextField,
  Chip,
  Autocomplete,
  Typography,
  Button,
  Paper
} from '@mui/material'

const TagSelector = ({ selectedTags, onTagsChange }) => {
  const [availableTags, setAvailableTags] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [loading, setLoading] = useState(true)

  // Fetch available tags on mount
  useEffect(() => {
    fetchAvailableTags()
  }, [])

  const fetchAvailableTags = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/equipment/tags/')
      const data = await response.json()
      
      // Extract just the tag names
      const tagNames = data.map(tag => tag.name)
      setAvailableTags(tagNames)
    } catch (error) {
      console.error('Failed to load tags:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleTagSelect = (event, newValue) => {
    onTagsChange(newValue)
  }

  return (
    <Box>
      <Typography variant='body2' color='text.secondary' gutterBottom>
        Tags - Select existing or type new ones
      </Typography>
      
      <Autocomplete
        multiple
        freeSolo
        options={availableTags}
        value={selectedTags}
        onChange={handleTagSelect}
        inputValue={inputValue}
        onInputChange={(event, newInputValue) => {
          setInputValue(newInputValue)
        }}
        loading={loading}
        renderTags={(value, getTagProps) =>
          value.map((option, index) => (
            <Chip
              label={option}
              {...getTagProps({ index })}
              color='primary'
              variant='outlined'
            />
          ))
        }
        renderInput={(params) => (
          <TextField
            {...params}
            placeholder='Select or type tags...'
            helperText='Start typing to see suggestions or create new tags'
          />
        )}
        renderOption={(props, option) => (
          <li {...props}>
            <Box display='flex' alignItems='center' gap={1}>
              <i className='ri-price-tag-3-line' />
              <Typography>{option}</Typography>
            </Box>
          </li>
        )}
        noOptionsText='No matching tags - press Enter to create new'
      />
      
      {/* Popular tags quick selection */}
      {selectedTags.length === 0 && (
        <Box mt={2}>
          <Typography variant='caption' color='text.secondary' gutterBottom>
            Popular tags:
          </Typography>
          <Box display='flex' gap={1} flexWrap='wrap' mt={1}>
            {availableTags.slice(0, 5).map((tag) => (
              <Chip
                key={tag}
                label={tag}
                size='small'
                variant='outlined'
                onClick={() => onTagsChange([...selectedTags, tag])}
                icon={<i className='ri-add-line' />}
              />
            ))}
          </Box>
        </Box>
      )}
    </Box>
  )
}

export default TagSelector
```

---

### Usage in Equipment Form

```javascript
'use client'

import { useState, useEffect } from 'react'
import TagSelector from './TagSelector'
import { equipmentAPI } from '@/services/api'

const AddEquipment = () => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    daily_rate: '',
    category_id: '',
    // ... other fields
  })
  
  const [tags, setTags] = useState([])

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    const formDataToSend = new FormData()
    
    // Add basic fields
    Object.keys(formData).forEach(key => {
      if (formData[key] !== '' && formData[key] !== null) {
        formDataToSend.append(key, formData[key])
      }
    })
    
    // Add tags as JSON string
    if (tags.length > 0) {
      formDataToSend.append('tag_names', JSON.stringify(tags))
    }
    
    // Submit to API
    try {
      const equipment = await equipmentAPI.createEquipment(formDataToSend)
      console.log('Equipment created:', equipment)
    } catch (error) {
      console.error('Error:', error)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      {/* ... other form fields ... */}
      
      {/* Tag Selector */}
      <TagSelector
        selectedTags={tags}
        onTagsChange={setTags}
      />
      
      <button type='submit'>Create Equipment</button>
    </form>
  )
}
```

---

## Alternative: Manual Tag Picker

For more control, here's a manual implementation:

```javascript
const ManualTagPicker = ({ selectedTags, onTagsChange }) => {
  const [availableTags, setAvailableTags] = useState([])
  const [customTagInput, setCustomTagInput] = useState('')
  
  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/equipment/tags/')
      .then(res => res.json())
      .then(data => setAvailableTags(data))
  }, [])

  const toggleTag = (tagName) => {
    if (selectedTags.includes(tagName)) {
      onTagsChange(selectedTags.filter(t => t !== tagName))
    } else {
      onTagsChange([...selectedTags, tagName])
    }
  }

  const addCustomTag = () => {
    const newTag = customTagInput.trim()
    if (newTag && !selectedTags.includes(newTag)) {
      onTagsChange([...selectedTags, newTag])
      setCustomTagInput('')
    }
  }

  return (
    <Box>
      {/* Selected Tags Display */}
      <Box display='flex' gap={1} flexWrap='wrap' mb={2}>
        {selectedTags.map((tag, index) => (
          <Chip
            key={index}
            label={tag}
            onDelete={() => toggleTag(tag)}
            color='primary'
          />
        ))}
      </Box>

      {/* Available Tags Grid */}
      <Typography variant='body2' gutterBottom>
        Select from existing tags:
      </Typography>
      <Box display='flex' gap={1} flexWrap='wrap' mb={2}>
        {availableTags.map((tag) => (
          <Chip
            key={tag.id}
            label={tag.name}
            onClick={() => toggleTag(tag.name)}
            variant={selectedTags.includes(tag.name) ? 'filled' : 'outlined'}
            color={selectedTags.includes(tag.name) ? 'primary' : 'default'}
            icon={selectedTags.includes(tag.name) ? 
              <i className='ri-check-line' /> : 
              <i className='ri-add-line' />
            }
          />
        ))}
      </Box>

      {/* Custom Tag Input */}
      <Typography variant='body2' gutterBottom>
        Or add a custom tag:
      </Typography>
      <Box display='flex' gap={2}>
        <TextField
          fullWidth
          size='small'
          label='Custom Tag'
          placeholder='e.g., Portable'
          value={customTagInput}
          onChange={(e) => setCustomTagInput(e.target.value)}
          onKeyPress={(e) => {
            if (e.key === 'Enter') {
              e.preventDefault()
              addCustomTag()
            }
          }}
        />
        <Button variant='outlined' onClick={addCustomTag}>
          Add
        </Button>
      </Box>
    </Box>
  )
}
```

---

## React Native Implementation

```javascript
import React, { useState, useEffect } from 'react'
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  FlatList,
  StyleSheet,
  ActivityIndicator
} from 'react-native'

const TagSelector = ({ selectedTags, onTagsChange }) => {
  const [availableTags, setAvailableTags] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [customTagInput, setCustomTagInput] = useState('')

  useEffect(() => {
    fetchTags()
  }, [])

  const fetchTags = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/equipment/tags/')
      const data = await response.json()
      setAvailableTags(data)
    } catch (error) {
      console.error('Failed to load tags:', error)
    } finally {
      setLoading(false)
    }
  }

  const toggleTag = (tagName) => {
    if (selectedTags.includes(tagName)) {
      onTagsChange(selectedTags.filter(t => t !== tagName))
    } else {
      onTagsChange([...selectedTags, tagName])
    }
  }

  const addCustomTag = () => {
    const newTag = customTagInput.trim()
    if (newTag && !selectedTags.includes(newTag)) {
      onTagsChange([...selectedTags, newTag])
      setCustomTagInput('')
    }
  }

  const filteredTags = availableTags.filter(tag =>
    tag.name.toLowerCase().includes(searchQuery.toLowerCase())
  )

  if (loading) {
    return <ActivityIndicator size='large' color='#007AFF' />
  }

  return (
    <View style={styles.container}>
      {/* Selected Tags */}
      <Text style={styles.label}>Selected Tags</Text>
      <View style={styles.tagsContainer}>
        {selectedTags.map((tag, index) => (
          <TouchableOpacity
            key={index}
            style={styles.selectedTag}
            onPress={() => toggleTag(tag)}
          >
            <Text style={styles.selectedTagText}>{tag}</Text>
            <Text style={styles.removeIcon}>×</Text>
          </TouchableOpacity>
        ))}
        {selectedTags.length === 0 && (
          <Text style={styles.placeholder}>No tags selected</Text>
        )}
      </View>

      {/* Search Available Tags */}
      <Text style={styles.label}>Available Tags</Text>
      <TextInput
        style={styles.searchInput}
        placeholder='Search tags...'
        value={searchQuery}
        onChangeText={setSearchQuery}
      />

      {/* Available Tags Grid */}
      <View style={styles.tagsContainer}>
        {filteredTags.map((tag) => (
          <TouchableOpacity
            key={tag.id}
            style={[
              styles.availableTag,
              selectedTags.includes(tag.name) && styles.availableTagSelected
            ]}
            onPress={() => toggleTag(tag.name)}
          >
            <Text
              style={[
                styles.availableTagText,
                selectedTags.includes(tag.name) && styles.availableTagTextSelected
              ]}
            >
              {tag.name}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Custom Tag Input */}
      <Text style={styles.label}>Add Custom Tag</Text>
      <View style={styles.customTagContainer}>
        <TextInput
          style={styles.customTagInput}
          placeholder='e.g., Portable'
          value={customTagInput}
          onChangeText={setCustomTagInput}
          onSubmitEditing={addCustomTag}
        />
        <TouchableOpacity style={styles.addButton} onPress={addCustomTag}>
          <Text style={styles.addButtonText}>Add</Text>
        </TouchableOpacity>
      </View>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    marginVertical: 16,
  },
  label: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 8,
    color: '#333',
  },
  tagsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 16,
    minHeight: 40,
  },
  selectedTag: {
    backgroundColor: '#007AFF',
    borderRadius: 16,
    paddingHorizontal: 12,
    paddingVertical: 6,
    marginRight: 8,
    marginBottom: 8,
    flexDirection: 'row',
    alignItems: 'center',
  },
  selectedTagText: {
    color: 'white',
    marginRight: 4,
  },
  removeIcon: {
    color: 'white',
    fontSize: 20,
    fontWeight: 'bold',
  },
  placeholder: {
    color: '#999',
    fontStyle: 'italic',
  },
  searchInput: {
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 8,
    padding: 12,
    marginBottom: 12,
    fontSize: 16,
  },
  availableTag: {
    borderWidth: 1,
    borderColor: '#007AFF',
    borderRadius: 16,
    paddingHorizontal: 12,
    paddingVertical: 6,
    marginRight: 8,
    marginBottom: 8,
  },
  availableTagSelected: {
    backgroundColor: '#007AFF',
  },
  availableTagText: {
    color: '#007AFF',
  },
  availableTagTextSelected: {
    color: 'white',
  },
  customTagContainer: {
    flexDirection: 'row',
    gap: 8,
  },
  customTagInput: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
  },
  addButton: {
    backgroundColor: '#007AFF',
    borderRadius: 8,
    paddingHorizontal: 20,
    justifyContent: 'center',
  },
  addButtonText: {
    color: 'white',
    fontWeight: 'bold',
  },
})

export default TagSelector
```

---

## API Usage Examples

### Fetch All Tags
```javascript
const fetchTags = async () => {
  const response = await fetch('http://127.0.0.1:8000/api/equipment/tags/')
  const tags = await response.json()
  // tags = [{id: 1, name: "Heavy Equipment"}, ...]
  return tags
}
```

### Search Tags
```javascript
const searchTags = async (query) => {
  const response = await fetch(
    `http://127.0.0.1:8000/api/equipment/tags/?search=${query}`
  )
  const tags = await response.json()
  return tags
}
```

### Create Equipment with Selected Tags
```javascript
const createEquipment = async (equipmentData, selectedTagNames) => {
  const formData = new FormData()
  
  formData.append('name', equipmentData.name)
  formData.append('description', equipmentData.description)
  formData.append('daily_rate', equipmentData.daily_rate)
  formData.append('category_id', equipmentData.category_id)
  
  // Add tags - can be existing or new
  formData.append('tag_names', JSON.stringify(selectedTagNames))
  // Example: ["Heavy Equipment", "Construction", "Custom New Tag"]
  
  const response = await fetch('http://127.0.0.1:8000/api/equipment/equipment/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
    },
    body: formData,
  })
  
  return await response.json()
}
```

---

## Benefits of Using Existing Tags

### ✅ Consistency
- Users see standardized tags across all listings
- Easier to filter and search equipment

### ✅ Better UX
- Quick selection with autocomplete
- No spelling mistakes
- See popular tags at a glance

### ✅ Flexibility
- Can still add custom tags when needed
- Tags auto-created if they don't exist
- Mix existing and new tags in one listing

---

## Tag Management Workflow

```
1. User opens equipment creation form
   ↓
2. Component fetches all available tags from /api/equipment/tags/
   ↓
3. User sees:
   - Autocomplete/dropdown with existing tags
   - Option to type custom tags
   ↓
4. User selects/types tags: ["Heavy Equipment", "Construction", "NewTag"]
   ↓
5. Form submits with tag_names: ["Heavy Equipment", "Construction", "NewTag"]
   ↓
6. Backend:
   - Finds "Heavy Equipment" (exists) → Links it
   - Finds "Construction" (exists) → Links it  
   - Doesn't find "NewTag" → Creates it → Links it
   ↓
7. Equipment saved with all 3 tags
```

---

## Quick Implementation Checklist

For adding tag selection to your form:

- [ ] Add API call to fetch tags: `GET /api/equipment/tags/`
- [ ] Store available tags in state: `const [availableTags, setAvailableTags] = useState([])`
- [ ] Create tag selector UI (Autocomplete or manual picker)
- [ ] Allow both selection and custom input
- [ ] Display selected tags as chips/pills
- [ ] Send selected tags as JSON array: `tag_names: ["Tag1", "Tag2"]`
- [ ] Test with existing tags
- [ ] Test with new tags
- [ ] Test with mixed existing + new tags

---

## Summary

**Backend automatically handles:**
- Creating new tags if they don't exist
- Linking existing tags
- Maintaining tag uniqueness

**Frontend should:**
- Fetch available tags on component mount
- Show tags in an autocomplete or picker
- Allow custom tag input
- Send all tags (existing + new) as a JSON array

**Result:**
- Users get suggestions for consistency
- Users can still add custom tags
- System prevents duplicate tags
- Better search and filtering experience

🏷️ **Your tag system is now fully functional with selection support!**
