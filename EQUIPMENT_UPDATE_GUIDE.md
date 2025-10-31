# Equipment Update & Tag Management Guide

## Overview

This guide explains how to update equipment and manage tags (add/remove) properly.

---

## Understanding Tag Operations

### 1. **Remove Tag from Equipment** (Common Operation)
When editing equipment, you can add or remove tag associations. This doesn't delete the tag from the database - it just removes the link between the equipment and the tag.

### 2. **Delete Tag from Database** (Admin Only)
Completely removes a tag from the system. Requires admin permissions.

---

## Updating Equipment with Tags

### API Endpoint
```
PUT/PATCH /api/equipment/equipment/{id}/
```

### How Tag Updates Work

When you send `tag_names` in an update request:
1. **All existing tags are removed** from the equipment
2. **New tags are added** based on the provided list
3. Tags are created if they don't exist

**Example:**
```
Equipment currently has: ["Construction", "Mining", "Old Tag"]

You send update with: ["Construction", "New Tag"]

Result: ["Construction", "New Tag"]
  - "Mining" and "Old Tag" removed ✅
  - "New Tag" added ✅
  - "Construction" kept ✅
```

---

## Frontend Implementation

### React/Next.js - Edit Equipment Form

```javascript
'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import TagSelector from './TagSelector'
import { equipmentAPI } from '@/services/api'

const EditEquipment = ({ equipmentId }) => {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [equipment, setEquipment] = useState(null)
  const [tags, setTags] = useState([])
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    daily_rate: '',
    // ... other fields
  })

  // Load existing equipment data
  useEffect(() => {
    loadEquipment()
  }, [equipmentId])

  const loadEquipment = async () => {
    try {
      const data = await equipmentAPI.getEquipment(equipmentId)
      
      // Populate form with existing data
      setFormData({
        name: data.name,
        description: data.description,
        daily_rate: data.daily_rate,
        category_id: data.category.id,
        manufacturer: data.manufacturer,
        model_number: data.model_number,
        year: data.year,
        weight: data.weight,
        dimensions: data.dimensions,
        fuel_type: data.fuel_type,
        weekly_rate: data.weekly_rate,
        monthly_rate: data.monthly_rate,
        country: data.country,
        city: data.city,
        status: data.status,
        total_units: data.total_units,
        available_units: data.available_units,
        featured: data.featured,
      })
      
      // Extract tag names from tag objects
      // Backend returns: [{id: 1, name: "Construction"}, ...]
      // We need: ["Construction", ...]
      const tagNames = data.tags.map(tag => tag.name)
      setTags(tagNames)
      
      setEquipment(data)
    } catch (error) {
      console.error('Failed to load equipment:', error)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    try {
      setLoading(true)
      
      const formDataToSend = new FormData()
      
      // Add all form fields
      Object.keys(formData).forEach(key => {
        if (formData[key] !== '' && formData[key] !== null) {
          if (typeof formData[key] === 'boolean') {
            formDataToSend.append(key, formData[key] ? 'true' : 'false')
          } else {
            formDataToSend.append(key, formData[key])
          }
        }
      })
      
      // Add tags - this will REPLACE all existing tags
      formDataToSend.append('tag_names', JSON.stringify(tags))
      
      // Update equipment
      const updated = await equipmentAPI.updateEquipment(equipmentId, formDataToSend)
      
      console.log('Equipment updated:', updated)
      alert('Equipment updated successfully!')
      router.push('/equipment')
    } catch (error) {
      console.error('Failed to update equipment:', error)
      alert('Failed to update equipment')
    } finally {
      setLoading(false)
    }
  }

  if (!equipment) {
    return <div>Loading...</div>
  }

  return (
    <form onSubmit={handleSubmit}>
      {/* Basic fields */}
      <input
        type="text"
        value={formData.name}
        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
      />
      
      {/* Tag Selector - allows adding/removing tags */}
      <TagSelector
        selectedTags={tags}
        onTagsChange={setTags}
      />
      
      <button type="submit" disabled={loading}>
        {loading ? 'Updating...' : 'Update Equipment'}
      </button>
    </form>
  )
}

export default EditEquipment
```

### API Service Example

```javascript
// services/api.js

export const equipmentAPI = {
  // Get single equipment
  getEquipment: async (id) => {
    const response = await fetch(`http://127.0.0.1:8000/api/equipment/equipment/${id}/`, {
      headers: {
        'Authorization': `Bearer ${getAccessToken()}`,
      },
    })
    return await response.json()
  },

  // Update equipment
  updateEquipment: async (id, formData) => {
    const response = await fetch(`http://127.0.0.1:8000/api/equipment/equipment/${id}/`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${getAccessToken()}`,
        // Don't set Content-Type - browser sets it with boundary for FormData
      },
      body: formData,
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(JSON.stringify(error))
    }
    
    return await response.json()
  },
}
```

---

## Tag Removal Examples

### Example 1: Remove One Tag

**Current tags:** `["Construction", "Mining", "Heavy Equipment"]`

**User removes "Mining":**
```javascript
const handleRemoveTag = (tagToRemove) => {
  const newTags = tags.filter(tag => tag !== tagToRemove)
  setTags(newTags)  // ["Construction", "Heavy Equipment"]
}
```

**On submit:**
```javascript
formData.append('tag_names', JSON.stringify(["Construction", "Heavy Equipment"]))
```

**Result:** Equipment now has only `["Construction", "Heavy Equipment"]`

---

### Example 2: Remove All Tags

```javascript
const handleClearAllTags = () => {
  setTags([])  // Empty array
}
```

**On submit:**
```javascript
formData.append('tag_names', JSON.stringify([]))
```

**Result:** Equipment has no tags

---

### Example 3: Replace All Tags

**Current tags:** `["Old Tag 1", "Old Tag 2"]`

**User selects new tags:** `["New Tag 1", "New Tag 2", "New Tag 3"]`

```javascript
setTags(["New Tag 1", "New Tag 2", "New Tag 3"])
```

**Result:** All old tags removed, new tags added

---

## React Native Implementation

```javascript
import React, { useState, useEffect } from 'react'
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
  Alert,
  StyleSheet
} from 'react-native'

const EditEquipment = ({ route, navigation }) => {
  const { equipmentId } = route.params
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    daily_rate: '',
  })
  const [tags, setTags] = useState([])
  const [tagInput, setTagInput] = useState('')

  useEffect(() => {
    loadEquipment()
  }, [])

  const loadEquipment = async () => {
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/api/equipment/equipment/${equipmentId}/`,
        {
          headers: {
            'Authorization': `Bearer ${accessToken}`,
          },
        }
      )
      const data = await response.json()
      
      setFormData({
        name: data.name,
        description: data.description,
        daily_rate: data.daily_rate.toString(),
      })
      
      // Extract tag names
      setTags(data.tags.map(tag => tag.name))
    } catch (error) {
      Alert.alert('Error', 'Failed to load equipment')
    }
  }

  const handleRemoveTag = (tagToRemove) => {
    setTags(tags.filter(tag => tag !== tagToRemove))
  }

  const handleAddTag = () => {
    if (tagInput.trim() && !tags.includes(tagInput.trim())) {
      setTags([...tags, tagInput.trim()])
      setTagInput('')
    }
  }

  const handleUpdate = async () => {
    try {
      setLoading(true)
      
      const formDataToSend = new FormData()
      formDataToSend.append('name', formData.name)
      formDataToSend.append('description', formData.description)
      formDataToSend.append('daily_rate', formData.daily_rate)
      
      // Update tags
      formDataToSend.append('tag_names', JSON.stringify(tags))
      
      const response = await fetch(
        `http://127.0.0.1:8000/api/equipment/equipment/${equipmentId}/`,
        {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${accessToken}`,
          },
          body: formDataToSend,
        }
      )
      
      if (response.ok) {
        Alert.alert('Success', 'Equipment updated successfully!')
        navigation.goBack()
      } else {
        const error = await response.json()
        Alert.alert('Error', JSON.stringify(error))
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to update equipment')
    } finally {
      setLoading(false)
    }
  }

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.label}>Name</Text>
      <TextInput
        style={styles.input}
        value={formData.name}
        onChangeText={(text) => setFormData({ ...formData, name: text })}
      />

      {/* Tags Section */}
      <Text style={styles.label}>Tags</Text>
      <View style={styles.tagsContainer}>
        {tags.map((tag, index) => (
          <View key={index} style={styles.tag}>
            <Text style={styles.tagText}>{tag}</Text>
            <TouchableOpacity onPress={() => handleRemoveTag(tag)}>
              <Text style={styles.removeIcon}>×</Text>
            </TouchableOpacity>
          </View>
        ))}
      </View>

      {/* Add Tag Input */}
      <View style={styles.addTagContainer}>
        <TextInput
          style={styles.tagInput}
          placeholder="Add tag"
          value={tagInput}
          onChangeText={setTagInput}
          onSubmitEditing={handleAddTag}
        />
        <TouchableOpacity style={styles.addButton} onPress={handleAddTag}>
          <Text style={styles.addButtonText}>Add</Text>
        </TouchableOpacity>
      </View>

      {/* Update Button */}
      <TouchableOpacity
        style={styles.updateButton}
        onPress={handleUpdate}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color="white" />
        ) : (
          <Text style={styles.updateButtonText}>Update Equipment</Text>
        )}
      </TouchableOpacity>
    </ScrollView>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: 'white',
  },
  label: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 8,
    marginTop: 16,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
  },
  tagsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 8,
  },
  tag: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#007AFF',
    borderRadius: 16,
    paddingHorizontal: 12,
    paddingVertical: 6,
    marginRight: 8,
    marginBottom: 8,
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
  addTagContainer: {
    flexDirection: 'row',
    gap: 8,
  },
  tagInput: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 8,
    padding: 12,
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
  updateButton: {
    backgroundColor: '#007AFF',
    borderRadius: 8,
    padding: 16,
    alignItems: 'center',
    marginTop: 24,
    marginBottom: 32,
  },
  updateButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
})

export default EditEquipment
```

---

## API Examples

### Get Equipment (to load existing tags)

```bash
curl -X GET http://127.0.0.1:8000/api/equipment/equipment/1/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "id": 1,
  "name": "Excavator",
  "tags": [
    {"id": 1, "name": "Construction"},
    {"id": 2, "name": "Mining"},
    {"id": 3, "name": "Heavy Equipment"}
  ],
  ...
}
```

### Update Equipment with Modified Tags

```bash
curl -X PUT http://127.0.0.1:8000/api/equipment/equipment/1/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "name=Updated Excavator" \
  -F "description=Updated description" \
  -F "daily_rate=550" \
  -F "category_id=1" \
  -F 'tag_names=["Construction","New Tag"]'
```

**Response:**
```json
{
  "id": 1,
  "name": "Updated Excavator",
  "tags": [
    {"id": 1, "name": "Construction"},
    {"id": 4, "name": "New Tag"}
  ],
  ...
}
```

---

## Admin-Only: Delete Tag from Database

If you're an admin and want to completely delete a tag:

```bash
DELETE /api/equipment/tags/{id}/
```

**Requirements:**
- Must be authenticated as admin user
- Will remove tag from ALL equipment that uses it

```bash
curl -X DELETE http://127.0.0.1:8000/api/equipment/tags/5/ \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

---

## Troubleshooting

### Issue: Tags not updating

**Check:**
1. Are you sending `tag_names` as JSON string? `JSON.stringify(tags)`
2. Is the tag list an array? `["Tag1", "Tag2"]`
3. Are you authenticated?
4. Is the equipment owned by your company?

### Issue: Tags appearing as one string

**Problem:** Tags sent as string instead of array
```javascript
// ❌ Wrong
formData.append('tag_names', 'Construction, Mining')

// ✅ Correct
formData.append('tag_names', JSON.stringify(['Construction', 'Mining']))
```

### Issue: Can't remove all tags

**Solution:** Send empty array
```javascript
formData.append('tag_names', JSON.stringify([]))  // Remove all tags
```

---

## Summary

✅ **Tag removal works by sending updated tag list**
✅ **Backend clears old tags and adds new ones**
✅ **JSON parsing fixed in both create and update**
✅ **Admin-only deletion for database-level tag removal**
✅ **Tags properly rendered as individual items**

Your tag management should now work perfectly! 🏷️
