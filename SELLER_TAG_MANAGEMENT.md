# Seller Dashboard - Tag Management Guide

## Overview

Sellers can now manage tags from their dashboard - create, update, and delete tags. Tags are shared across the platform, so deleting a tag that's in use by equipment is prevented.

---

## API Endpoints

### 1. List All Tags
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
  }
]
```

### 2. Create Tag
```bash
POST /api/equipment/tags/
```

**Request:**
```json
{
  "name": "New Tag"
}
```

**Response:**
```json
{
  "id": 4,
  "name": "New Tag"
}
```

### 3. Update Tag
```bash
PUT/PATCH /api/equipment/tags/{id}/
```

**Request:**
```json
{
  "name": "Updated Tag Name"
}
```

### 4. Delete Tag
```bash
DELETE /api/equipment/tags/{id}/
```

**Success Response (tag not in use):**
```json
{
  "message": "Tag \"Old Tag\" deleted successfully.",
  "deleted_tag": "Old Tag"
}
```

**Error Response (tag in use):**
```json
{
  "error": "Cannot delete tag \"Construction\". It is currently used by 5 equipment listing(s).",
  "equipment_count": 5,
  "tag_name": "Construction"
}
```

---

## Safety Features

### ✅ Prevents Breaking Equipment Listings

When you try to delete a tag, the system checks:
1. **How many equipment listings use this tag?**
2. **If count > 0:** Deletion is blocked with an error message
3. **If count = 0:** Tag is safely deleted

**Example:**
```
Tag "Construction" used by 3 equipment → ❌ Cannot delete
Tag "Unused Tag" used by 0 equipment → ✅ Can delete
```

---

## Frontend Implementation

### React/Next.js - Tag Management Component

```javascript
'use client'

import { useState, useEffect } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  IconButton,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Chip,
  CircularProgress,
  Grid
} from '@mui/material'

const TagManagement = () => {
  const [tags, setTags] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  
  // Create dialog
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [newTagName, setNewTagName] = useState('')
  const [creating, setCreating] = useState(false)
  
  // Edit dialog
  const [editDialogOpen, setEditDialogOpen] = useState(false)
  const [editingTag, setEditingTag] = useState(null)
  const [editTagName, setEditTagName] = useState('')
  const [updating, setUpdating] = useState(false)
  
  // Delete confirmation
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [deletingTag, setDeletingTag] = useState(null)
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    loadTags()
  }, [])

  const loadTags = async () => {
    try {
      setLoading(true)
      const response = await fetch('http://127.0.0.1:8000/api/equipment/tags/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
        },
      })
      const data = await response.json()
      setTags(data)
    } catch (err) {
      setError('Failed to load tags')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateTag = async () => {
    if (!newTagName.trim()) {
      setError('Tag name cannot be empty')
      return
    }

    try {
      setCreating(true)
      setError(null)
      
      const response = await fetch('http://127.0.0.1:8000/api/equipment/tags/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: newTagName.trim() }),
      })

      if (response.ok) {
        const newTag = await response.json()
        setTags([...tags, newTag])
        setSuccess(`Tag "${newTag.name}" created successfully!`)
        setCreateDialogOpen(false)
        setNewTagName('')
      } else {
        const errorData = await response.json()
        setError(errorData.name?.[0] || 'Failed to create tag')
      }
    } catch (err) {
      setError('Failed to create tag')
    } finally {
      setCreating(false)
    }
  }

  const handleUpdateTag = async () => {
    if (!editTagName.trim()) {
      setError('Tag name cannot be empty')
      return
    }

    try {
      setUpdating(true)
      setError(null)
      
      const response = await fetch(
        `http://127.0.0.1:8000/api/equipment/tags/${editingTag.id}/`,
        {
          method: 'PATCH',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ name: editTagName.trim() }),
        }
      )

      if (response.ok) {
        const updatedTag = await response.json()
        setTags(tags.map(tag => tag.id === updatedTag.id ? updatedTag : tag))
        setSuccess(`Tag updated to "${updatedTag.name}"`)
        setEditDialogOpen(false)
        setEditingTag(null)
      } else {
        const errorData = await response.json()
        setError(errorData.name?.[0] || 'Failed to update tag')
      }
    } catch (err) {
      setError('Failed to update tag')
    } finally {
      setUpdating(false)
    }
  }

  const handleDeleteTag = async () => {
    try {
      setDeleting(true)
      setError(null)
      
      const response = await fetch(
        `http://127.0.0.1:8000/api/equipment/tags/${deletingTag.id}/`,
        {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
          },
        }
      )

      if (response.ok) {
        const result = await response.json()
        setTags(tags.filter(tag => tag.id !== deletingTag.id))
        setSuccess(result.message || `Tag "${deletingTag.name}" deleted successfully!`)
        setDeleteDialogOpen(false)
        setDeletingTag(null)
      } else {
        const errorData = await response.json()
        setError(errorData.error || 'Failed to delete tag')
        setDeleteDialogOpen(false)
        setDeletingTag(null)
      }
    } catch (err) {
      setError('Failed to delete tag')
    } finally {
      setDeleting(false)
    }
  }

  const openEditDialog = (tag) => {
    setEditingTag(tag)
    setEditTagName(tag.name)
    setEditDialogOpen(true)
  }

  const openDeleteDialog = (tag) => {
    setDeletingTag(tag)
    setDeleteDialogOpen(true)
  }

  if (loading) {
    return (
      <Box display='flex' justifyContent='center' alignItems='center' minHeight='400px'>
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Box>
      {/* Header */}
      <Box display='flex' justifyContent='space-between' alignItems='center' mb={4}>
        <Box>
          <Typography variant='h4'>Tag Management</Typography>
          <Typography variant='body2' color='text.secondary' sx={{ mt: 1 }}>
            Create and manage tags for your equipment listings
          </Typography>
        </Box>
        <Button
          variant='contained'
          startIcon={<i className='ri-add-line' />}
          onClick={() => setCreateDialogOpen(true)}
        >
          Create Tag
        </Button>
      </Box>

      {/* Alerts */}
      {error && (
        <Alert severity='error' onClose={() => setError(null)} sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      {success && (
        <Alert severity='success' onClose={() => setSuccess(null)} sx={{ mb: 3 }}>
          {success}
        </Alert>
      )}

      {/* Tags Grid */}
      <Card>
        <CardContent>
          <Typography variant='h6' sx={{ mb: 3 }}>
            All Tags ({tags.length})
          </Typography>

          {tags.length === 0 ? (
            <Box textAlign='center' py={4}>
              <Typography color='text.secondary'>
                No tags yet. Create your first tag to get started.
              </Typography>
            </Box>
          ) : (
            <Grid container spacing={2}>
              {tags.map((tag) => (
                <Grid item xs={12} sm={6} md={4} lg={3} key={tag.id}>
                  <Box
                    sx={{
                      border: '1px solid',
                      borderColor: 'divider',
                      borderRadius: 1,
                      p: 2,
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      '&:hover': {
                        borderColor: 'primary.main',
                        bgcolor: 'action.hover',
                      },
                    }}
                  >
                    <Chip label={tag.name} color='primary' variant='outlined' />
                    <Box>
                      <IconButton
                        size='small'
                        onClick={() => openEditDialog(tag)}
                        sx={{ mr: 0.5 }}
                      >
                        <i className='ri-edit-line' />
                      </IconButton>
                      <IconButton
                        size='small'
                        color='error'
                        onClick={() => openDeleteDialog(tag)}
                      >
                        <i className='ri-delete-bin-line' />
                      </IconButton>
                    </Box>
                  </Box>
                </Grid>
              ))}
            </Grid>
          )}
        </CardContent>
      </Card>

      {/* Create Tag Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth='sm' fullWidth>
        <DialogTitle>Create New Tag</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            fullWidth
            label='Tag Name'
            placeholder='e.g., Heavy Equipment, Construction'
            value={newTagName}
            onChange={(e) => setNewTagName(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                handleCreateTag()
              }
            }}
            sx={{ mt: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button
            variant='contained'
            onClick={handleCreateTag}
            disabled={creating || !newTagName.trim()}
            startIcon={creating ? <CircularProgress size={20} /> : null}
          >
            Create
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Tag Dialog */}
      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth='sm' fullWidth>
        <DialogTitle>Edit Tag</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            fullWidth
            label='Tag Name'
            value={editTagName}
            onChange={(e) => setEditTagName(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                handleUpdateTag()
              }
            }}
            sx={{ mt: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
          <Button
            variant='contained'
            onClick={handleUpdateTag}
            disabled={updating || !editTagName.trim()}
            startIcon={updating ? <CircularProgress size={20} /> : null}
          >
            Update
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)} maxWidth='sm' fullWidth>
        <DialogTitle>Delete Tag</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete the tag <strong>"{deletingTag?.name}"</strong>?
          </Typography>
          <Alert severity='warning' sx={{ mt: 2 }}>
            If this tag is being used by equipment listings, deletion will be blocked.
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button
            variant='contained'
            color='error'
            onClick={handleDeleteTag}
            disabled={deleting}
            startIcon={deleting ? <CircularProgress size={20} /> : <i className='ri-delete-bin-line' />}
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default TagManagement
```

---

## React Native Implementation

```javascript
import React, { useState, useEffect } from 'react'
import {
  View,
  Text,
  TouchableOpacity,
  FlatList,
  TextInput,
  Modal,
  Alert,
  ActivityIndicator,
  StyleSheet
} from 'react-native'

const TagManagement = () => {
  const [tags, setTags] = useState([])
  const [loading, setLoading] = useState(true)
  const [createModalVisible, setCreateModalVisible] = useState(false)
  const [editModalVisible, setEditModalVisible] = useState(false)
  const [newTagName, setNewTagName] = useState('')
  const [editingTag, setEditingTag] = useState(null)
  const [editTagName, setEditTagName] = useState('')

  useEffect(() => {
    loadTags()
  }, [])

  const loadTags = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/equipment/tags/', {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
        },
      })
      const data = await response.json()
      setTags(data)
    } catch (error) {
      Alert.alert('Error', 'Failed to load tags')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateTag = async () => {
    if (!newTagName.trim()) {
      Alert.alert('Error', 'Tag name cannot be empty')
      return
    }

    try {
      const response = await fetch('http://127.0.0.1:8000/api/equipment/tags/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: newTagName.trim() }),
      })

      if (response.ok) {
        const newTag = await response.json()
        setTags([...tags, newTag])
        setCreateModalVisible(false)
        setNewTagName('')
        Alert.alert('Success', `Tag "${newTag.name}" created!`)
      } else {
        const error = await response.json()
        Alert.alert('Error', error.name?.[0] || 'Failed to create tag')
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to create tag')
    }
  }

  const handleUpdateTag = async () => {
    if (!editTagName.trim()) {
      Alert.alert('Error', 'Tag name cannot be empty')
      return
    }

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/api/equipment/tags/${editingTag.id}/`,
        {
          method: 'PATCH',
          headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ name: editTagName.trim() }),
        }
      )

      if (response.ok) {
        const updatedTag = await response.json()
        setTags(tags.map(tag => tag.id === updatedTag.id ? updatedTag : tag))
        setEditModalVisible(false)
        setEditingTag(null)
        Alert.alert('Success', 'Tag updated successfully')
      } else {
        const error = await response.json()
        Alert.alert('Error', error.name?.[0] || 'Failed to update tag')
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to update tag')
    }
  }

  const handleDeleteTag = (tag) => {
    Alert.alert(
      'Delete Tag',
      `Are you sure you want to delete "${tag.name}"?`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              const response = await fetch(
                `http://127.0.0.1:8000/api/equipment/tags/${tag.id}/`,
                {
                  method: 'DELETE',
                  headers: {
                    'Authorization': `Bearer ${accessToken}`,
                  },
                }
              )

              if (response.ok) {
                const result = await response.json()
                setTags(tags.filter(t => t.id !== tag.id))
                Alert.alert('Success', result.message)
              } else {
                const error = await response.json()
                Alert.alert('Error', error.error || 'Failed to delete tag')
              }
            } catch (error) {
              Alert.alert('Error', 'Failed to delete tag')
            }
          },
        },
      ]
    )
  }

  const renderTag = ({ item }) => (
    <View style={styles.tagItem}>
      <View style={styles.tagPill}>
        <Text style={styles.tagText}>{item.name}</Text>
      </View>
      <View style={styles.tagActions}>
        <TouchableOpacity
          onPress={() => {
            setEditingTag(item)
            setEditTagName(item.name)
            setEditModalVisible(true)
          }}
          style={styles.actionButton}
        >
          <Text style={styles.editText}>Edit</Text>
        </TouchableOpacity>
        <TouchableOpacity
          onPress={() => handleDeleteTag(item)}
          style={[styles.actionButton, styles.deleteButton]}
        >
          <Text style={styles.deleteText}>Delete</Text>
        </TouchableOpacity>
      </View>
    </View>
  )

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size='large' color='#007AFF' />
      </View>
    )
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Tag Management</Text>
        <TouchableOpacity
          style={styles.createButton}
          onPress={() => setCreateModalVisible(true)}
        >
          <Text style={styles.createButtonText}>+ Create Tag</Text>
        </TouchableOpacity>
      </View>

      <FlatList
        data={tags}
        renderItem={renderTag}
        keyExtractor={(item) => item.id.toString()}
        contentContainerStyle={styles.list}
        ListEmptyComponent={
          <Text style={styles.emptyText}>No tags yet. Create your first tag!</Text>
        }
      />

      {/* Create Modal */}
      <Modal visible={createModalVisible} transparent animationType='slide'>
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Create New Tag</Text>
            <TextInput
              style={styles.input}
              placeholder='Tag name'
              value={newTagName}
              onChangeText={setNewTagName}
            />
            <View style={styles.modalActions}>
              <TouchableOpacity
                style={styles.modalButton}
                onPress={() => setCreateModalVisible(false)}
              >
                <Text>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.modalButton, styles.primaryButton]}
                onPress={handleCreateTag}
              >
                <Text style={styles.primaryButtonText}>Create</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>

      {/* Edit Modal */}
      <Modal visible={editModalVisible} transparent animationType='slide'>
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Edit Tag</Text>
            <TextInput
              style={styles.input}
              placeholder='Tag name'
              value={editTagName}
              onChangeText={setEditTagName}
            />
            <View style={styles.modalActions}>
              <TouchableOpacity
                style={styles.modalButton}
                onPress={() => setEditModalVisible(false)}
              >
                <Text>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.modalButton, styles.primaryButton]}
                onPress={handleUpdateTag}
              >
                <Text style={styles.primaryButtonText}>Update</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#ddd',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  createButton: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
  },
  createButtonText: {
    color: 'white',
    fontWeight: 'bold',
  },
  list: {
    padding: 16,
  },
  tagItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  tagPill: {
    backgroundColor: '#e3f2fd',
    borderRadius: 16,
    paddingHorizontal: 16,
    paddingVertical: 8,
  },
  tagText: {
    color: '#1976d2',
    fontWeight: 'bold',
  },
  tagActions: {
    flexDirection: 'row',
    gap: 8,
  },
  actionButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 4,
  },
  editText: {
    color: '#007AFF',
  },
  deleteButton: {
    backgroundColor: '#ffebee',
  },
  deleteText: {
    color: '#d32f2f',
  },
  emptyText: {
    textAlign: 'center',
    color: '#999',
    marginTop: 32,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 24,
    width: '80%',
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    marginBottom: 16,
  },
  modalActions: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    gap: 12,
  },
  modalButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
  },
  primaryButton: {
    backgroundColor: '#007AFF',
  },
  primaryButtonText: {
    color: 'white',
    fontWeight: 'bold',
  },
})

export default TagManagement
```

---

## API Examples

### Create Tag
```bash
curl -X POST http://127.0.0.1:8000/api/equipment/tags/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Portable"}'
```

### Update Tag
```bash
curl -X PATCH http://127.0.0.1:8000/api/equipment/tags/5/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Name"}'
```

### Delete Tag (Unused)
```bash
curl -X DELETE http://127.0.0.1:8000/api/equipment/tags/5/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Success:**
```json
{
  "message": "Tag \"Portable\" deleted successfully.",
  "deleted_tag": "Portable"
}
```

### Delete Tag (In Use) - Will Fail
```bash
curl -X DELETE http://127.0.0.1:8000/api/equipment/tags/1/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Error:**
```json
{
  "error": "Cannot delete tag \"Construction\". It is currently used by 5 equipment listing(s).",
  "equipment_count": 5,
  "tag_name": "Construction"
}
```

---

## Summary

✅ **Authenticated sellers can now manage tags**
✅ **Safety check prevents deleting tags in use**
✅ **Clear error messages show equipment count**
✅ **Complete CRUD operations: Create, Read, Update, Delete**
✅ **Tag management UI ready for dashboard**

Your seller dashboard tag management is now fully functional! 🏷️
