## Frontend Form Field Corrections

### ❌ WRONG Fields (Your Current Form)
```javascript
formData = {
  serial_number: '',        // ❌ Backend doesn't have this field
  deposit_required: '',     // ❌ Backend doesn't have this field
  manufacture_year: '',     // ❌ Should be 'year'
  model: '',                // ❌ Should be 'model_number'
  specifications: '',       // ❌ Should be 'specifications_data' (array format)
  location: '',             // ❌ Should be 'city' and 'country' separately
  is_featured: false,       // ❌ Should be 'featured'
  insurance_included: false,// ❌ Backend doesn't have this field
  delivery_available: false // ❌ Backend doesn't have this field
}
```

### ✅ CORRECT Fields (What Backend Expects)

```javascript
const [formData, setFormData] = useState({
  // Basic Information (REQUIRED)
  name: '',
  category_id: '',
  description: '',
  
  // Technical Specs
  manufacturer: '',
  model_number: '',    // ✅ Changed from 'model'
  year: '',           // ✅ Changed from 'manufacture_year'
  weight: '',         // Weight in kg
  dimensions: '',     // e.g., "500x200x250" (LxWxH in cm)
  fuel_type: '',      // e.g., 'Diesel', 'Electric', 'Gasoline'
  
  // Pricing (REQUIRED - at least daily_rate)
  daily_rate: '',
  weekly_rate: '',
  monthly_rate: '',
  
  // Location (REQUIRED)
  country: 'UAE',     // ✅ 3-letter country code
  city: 'DXB',        // ✅ 3-letter city code
  
  // Availability
  status: 'available',
  total_units: 1,
  available_units: 1,
  
  // Promotional
  featured: false,    // ✅ Changed from 'is_featured'
})
```

---

## Complete Corrected Form Component

Replace your entire component with this corrected version:

```javascript
'use client'

// React Imports
import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'

// MUI Imports
import Card from '@mui/material/Card'
import CardContent from '@mui/material/CardContent'
import Typography from '@mui/material/Typography'
import Button from '@mui/material/Button'
import TextField from '@mui/material/TextField'
import MenuItem from '@mui/material/MenuItem'
import Box from '@mui/material/Box'
import Grid from '@mui/material/Grid'
import FormControlLabel from '@mui/material/FormControlLabel'
import Checkbox from '@mui/material/Checkbox'
import Alert from '@mui/material/Alert'
import CircularProgress from '@mui/material/CircularProgress'
import IconButton from '@mui/material/IconButton'
import Chip from '@mui/material/Chip'

// API Imports
import { equipmentAPI } from '@/services/api'

const AddEquipment = () => {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [categories, setCategories] = useState([])
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)

  // CORRECTED Form data - matches backend exactly
  const [formData, setFormData] = useState({
    // Basic Information (REQUIRED)
    name: '',
    category_id: '',
    description: '',
    
    // Technical Specs
    manufacturer: '',
    model_number: '',    // ✅ NOT 'model'
    year: '',           // ✅ NOT 'manufacture_year'
    weight: '',         // in kg
    dimensions: '',     // LxWxH in cm
    fuel_type: '',
    
    // Pricing
    daily_rate: '',
    weekly_rate: '',
    monthly_rate: '',
    
    // Location (3-letter codes)
    country: 'UAE',     // ✅ Country code
    city: 'DXB',        // ✅ City code
    
    // Availability
    status: 'available',
    total_units: 1,
    available_units: 1,
    
    // Promotional
    featured: false,    // ✅ NOT 'is_featured'
  })

  // Tags
  const [tags, setTags] = useState([])
  const [tagInput, setTagInput] = useState('')

  // Image handling
  const [selectedImages, setSelectedImages] = useState([])
  const [imagePreviews, setImagePreviews] = useState([])

  // Specifications (as array of objects)
  const [specifications, setSpecifications] = useState([])
  const [specName, setSpecName] = useState('')
  const [specValue, setSpecValue] = useState('')

  // Form validation
  const [errors, setErrors] = useState({})

  // City options with 3-letter codes
  const cityOptions = [
    { code: 'DXB', name: 'Dubai' },
    { code: 'AUH', name: 'Abu Dhabi' },
    { code: 'SHJ', name: 'Sharjah' },
    { code: 'AJM', name: 'Ajman' },
    { code: 'RAK', name: 'Ras Al Khaimah' },
    { code: 'FUJ', name: 'Fujairah' },
    { code: 'UAQ', name: 'Umm Al Quwain' },
  ]

  useEffect(() => {
    loadCategories()
  }, [])

  const loadCategories = async () => {
    try {
      const data = await equipmentAPI.getCategories()
      setCategories(data.results || data)
    } catch (err) {
      console.error('Failed to load categories:', err)
    }
  }

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: null }))
    }
  }

  const handleImageSelect = e => {
    const files = Array.from(e.target.files)
    if (files.length + selectedImages.length > 7) {
      setError('Maximum 7 images allowed')
      return
    }

    setSelectedImages(prev => [...prev, ...files])

    files.forEach(file => {
      const reader = new FileReader()
      reader.onloadend = () => {
        setImagePreviews(prev => [...prev, reader.result])
      }
      reader.readAsDataURL(file)
    })
  }

  const handleRemoveImage = index => {
    setSelectedImages(prev => prev.filter((_, i) => i !== index))
    setImagePreviews(prev => prev.filter((_, i) => i !== index))
  }

  const handleAddTag = () => {
    if (tagInput.trim() && !tags.includes(tagInput.trim())) {
      setTags([...tags, tagInput.trim()])
      setTagInput('')
    }
  }

  const handleRemoveTag = tagToRemove => {
    setTags(tags.filter(tag => tag !== tagToRemove))
  }

  const handleAddSpecification = () => {
    if (specName.trim() && specValue.trim()) {
      setSpecifications([...specifications, { name: specName.trim(), value: specValue.trim() }])
      setSpecName('')
      setSpecValue('')
    }
  }

  const handleRemoveSpecification = index => {
    setSpecifications(specifications.filter((_, i) => i !== index))
  }

  const validateForm = () => {
    const newErrors = {}

    // Required fields
    if (!formData.name.trim()) newErrors.name = 'Equipment name is required'
    if (!formData.category_id) newErrors.category_id = 'Category is required'
    if (!formData.description.trim()) newErrors.description = 'Description is required'
    if (!formData.daily_rate || parseFloat(formData.daily_rate) <= 0)
      newErrors.daily_rate = 'Valid daily rate is required'
    if (!formData.city) newErrors.city = 'City is required'
    
    // Numeric validations
    if (formData.year && (formData.year < 1900 || formData.year > new Date().getFullYear() + 1)) {
      newErrors.year = 'Invalid year'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async e => {
    e.preventDefault()

    if (!validateForm()) {
      setError('Please fix the errors in the form')
      return
    }

    try {
      setLoading(true)
      setError(null)

      const formDataToSend = new FormData()

      // Add all form fields (only non-empty values)
      Object.keys(formData).forEach(key => {
        const value = formData[key]
        if (value !== '' && value !== null && value !== undefined) {
          if (typeof value === 'boolean') {
            formDataToSend.append(key, value ? 'true' : 'false')
          } else {
            formDataToSend.append(key, value)
          }
        }
      })

      // Add tags as JSON string
      if (tags.length > 0) {
        formDataToSend.append('tag_names', JSON.stringify(tags))
      }

      // Add specifications as JSON string
      if (specifications.length > 0) {
        formDataToSend.append('specifications_data', JSON.stringify(specifications))
      }

      // Add images
      selectedImages.forEach(image => {
        formDataToSend.append('images', image)
      })

      // Log for debugging
      console.log('Submitting equipment data:')
      for (let [key, value] of formDataToSend.entries()) {
        if (key !== 'images') {
          console.log(`  ${key}: ${value}`)
        }
      }

      const equipment = await equipmentAPI.createEquipment(formDataToSend)

      setSuccess('Equipment added successfully!')
      setTimeout(() => {
        router.push('/equipment')
      }, 2000)
    } catch (err) {
      console.error('Failed to create equipment:', err)
      console.error('Error response:', err.response?.data)
      
      let errorMessage = 'Failed to create equipment'
      if (err.response?.data) {
        if (typeof err.response.data === 'object') {
          const fieldErrors = Object.entries(err.response.data)
            .map(([field, messages]) => {
              const msgArray = Array.isArray(messages) ? messages : [messages]
              return `${field}: ${msgArray.join(', ')}`
            })
            .join(' | ')
          errorMessage = fieldErrors || errorMessage
        } else {
          errorMessage = err.response.data.message || err.response.data || errorMessage
        }
      }
      
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box>
      {/* Header */}
      <Box display='flex' justifyContent='space-between' alignItems='center' mb={6}>
        <Box>
          <Typography variant='h4'>Add New Equipment</Typography>
          <Typography variant='body2' color='text.secondary' sx={{ mt: 1 }}>
            Fill in the details to add equipment to your inventory
          </Typography>
        </Box>
        <Button variant='outlined' onClick={() => router.push('/equipment')}>
          Cancel
        </Button>
      </Box>

      {/* Alerts */}
      {error && (
        <Alert severity='error' onClose={() => setError(null)} sx={{ mb: 4 }}>
          {error}
        </Alert>
      )}
      {success && (
        <Alert severity='success' onClose={() => setSuccess(null)} sx={{ mb: 4 }}>
          {success}
        </Alert>
      )}

      <form onSubmit={handleSubmit}>
        <Grid container spacing={6}>
          {/* Basic Information */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant='h6' sx={{ mb: 4 }}>
                  Basic Information
                </Typography>
                <Grid container spacing={4}>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      required
                      label='Equipment Name'
                      placeholder='e.g., Caterpillar 320D Excavator'
                      value={formData.name}
                      onChange={e => handleInputChange('name', e.target.value)}
                      error={!!errors.name}
                      helperText={errors.name}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      required
                      select
                      label='Category'
                      value={formData.category_id}
                      onChange={e => handleInputChange('category_id', e.target.value)}
                      error={!!errors.category_id}
                      helperText={errors.category_id}
                    >
                      <MenuItem value=''>Select Category</MenuItem>
                      {categories.map(cat => (
                        <MenuItem key={cat.id} value={cat.id}>
                          {cat.name}
                        </MenuItem>
                      ))}
                    </TextField>
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      required
                      multiline
                      rows={4}
                      label='Description'
                      placeholder='Detailed description of the equipment...'
                      value={formData.description}
                      onChange={e => handleInputChange('description', e.target.value)}
                      error={!!errors.description}
                      helperText={errors.description}
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Pricing */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant='h6' sx={{ mb: 4 }}>
                  Pricing
                </Typography>
                <Grid container spacing={4}>
                  <Grid item xs={12} md={4}>
                    <TextField
                      fullWidth
                      required
                      type='number'
                      label='Daily Rate (AED)'
                      placeholder='0.00'
                      value={formData.daily_rate}
                      onChange={e => handleInputChange('daily_rate', e.target.value)}
                      error={!!errors.daily_rate}
                      helperText={errors.daily_rate}
                      InputProps={{
                        startAdornment: <Typography sx={{ mr: 1 }}>AED</Typography>
                      }}
                    />
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <TextField
                      fullWidth
                      type='number'
                      label='Weekly Rate (AED)'
                      placeholder='Optional'
                      value={formData.weekly_rate}
                      onChange={e => handleInputChange('weekly_rate', e.target.value)}
                      InputProps={{
                        startAdornment: <Typography sx={{ mr: 1 }}>AED</Typography>
                      }}
                    />
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <TextField
                      fullWidth
                      type='number'
                      label='Monthly Rate (AED)'
                      placeholder='Optional'
                      value={formData.monthly_rate}
                      onChange={e => handleInputChange('monthly_rate', e.target.value)}
                      InputProps={{
                        startAdornment: <Typography sx={{ mr: 1 }}>AED</Typography>
                      }}
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Equipment Details */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant='h6' sx={{ mb: 4 }}>
                  Equipment Details
                </Typography>
                <Grid container spacing={4}>
                  <Grid item xs={12} md={4}>
                    <TextField
                      fullWidth
                      label='Manufacturer'
                      placeholder='e.g., Caterpillar'
                      value={formData.manufacturer}
                      onChange={e => handleInputChange('manufacturer', e.target.value)}
                    />
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <TextField
                      fullWidth
                      label='Model Number'
                      placeholder='e.g., 320D'
                      value={formData.model_number}
                      onChange={e => handleInputChange('model_number', e.target.value)}
                    />
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <TextField
                      fullWidth
                      type='number'
                      label='Year'
                      placeholder='e.g., 2022'
                      value={formData.year}
                      onChange={e => handleInputChange('year', e.target.value)}
                      error={!!errors.year}
                      helperText={errors.year}
                      inputProps={{ min: 1900, max: new Date().getFullYear() + 1 }}
                    />
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <TextField
                      fullWidth
                      label='Weight (kg)'
                      placeholder='e.g., 20000'
                      value={formData.weight}
                      onChange={e => handleInputChange('weight', e.target.value)}
                    />
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <TextField
                      fullWidth
                      label='Dimensions (cm)'
                      placeholder='e.g., 950x280x310 (LxWxH)'
                      value={formData.dimensions}
                      onChange={e => handleInputChange('dimensions', e.target.value)}
                      helperText='Length x Width x Height in cm'
                    />
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <TextField
                      fullWidth
                      label='Fuel Type'
                      placeholder='e.g., Diesel, Electric'
                      value={formData.fuel_type}
                      onChange={e => handleInputChange('fuel_type', e.target.value)}
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Tags */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant='h6' sx={{ mb: 2 }}>
                  Tags
                </Typography>
                <Box display='flex' gap={1} flexWrap='wrap' mb={2}>
                  {tags.map((tag, index) => (
                    <Chip
                      key={index}
                      label={tag}
                      onDelete={() => handleRemoveTag(tag)}
                      color='primary'
                      variant='outlined'
                    />
                  ))}
                </Box>
                <Box display='flex' gap={2}>
                  <TextField
                    fullWidth
                    size='small'
                    label='Add Tag'
                    placeholder='e.g., Heavy Equipment, Construction'
                    value={tagInput}
                    onChange={e => setTagInput(e.target.value)}
                    onKeyPress={e => {
                      if (e.key === 'Enter') {
                        e.preventDefault()
                        handleAddTag()
                      }
                    }}
                  />
                  <Button variant='outlined' onClick={handleAddTag}>
                    Add
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Specifications */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant='h6' sx={{ mb: 2 }}>
                  Specifications
                </Typography>
                {specifications.length > 0 && (
                  <Box sx={{ mb: 2 }}>
                    {specifications.map((spec, index) => (
                      <Box
                        key={index}
                        display='flex'
                        justifyContent='space-between'
                        alignItems='center'
                        sx={{ py: 1, borderBottom: '1px solid', borderColor: 'divider' }}
                      >
                        <Typography>
                          <strong>{spec.name}:</strong> {spec.value}
                        </Typography>
                        <IconButton size='small' onClick={() => handleRemoveSpecification(index)}>
                          <i className='ri-delete-bin-line' />
                        </IconButton>
                      </Box>
                    ))}
                  </Box>
                )}
                <Grid container spacing={2}>
                  <Grid item xs={12} md={5}>
                    <TextField
                      fullWidth
                      size='small'
                      label='Specification Name'
                      placeholder='e.g., Engine Power'
                      value={specName}
                      onChange={e => setSpecName(e.target.value)}
                    />
                  </Grid>
                  <Grid item xs={12} md={5}>
                    <TextField
                      fullWidth
                      size='small'
                      label='Value'
                      placeholder='e.g., 122 HP'
                      value={specValue}
                      onChange={e => setSpecValue(e.target.value)}
                    />
                  </Grid>
                  <Grid item xs={12} md={2}>
                    <Button fullWidth variant='outlined' onClick={handleAddSpecification}>
                      Add
                    </Button>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Location & Availability */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant='h6' sx={{ mb: 4 }}>
                  Location & Availability
                </Typography>
                <Grid container spacing={4}>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      required
                      select
                      label='City'
                      value={formData.city}
                      onChange={e => handleInputChange('city', e.target.value)}
                      error={!!errors.city}
                      helperText={errors.city}
                    >
                      <MenuItem value=''>Select City</MenuItem>
                      {cityOptions.map(city => (
                        <MenuItem key={city.code} value={city.code}>
                          {city.name}
                        </MenuItem>
                      ))}
                    </TextField>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      select
                      label='Status'
                      value={formData.status}
                      onChange={e => handleInputChange('status', e.target.value)}
                    >
                      <MenuItem value='available'>Available</MenuItem>
                      <MenuItem value='rented'>Rented</MenuItem>
                      <MenuItem value='maintenance'>Maintenance</MenuItem>
                      <MenuItem value='reserved'>Reserved</MenuItem>
                      <MenuItem value='inactive'>Inactive</MenuItem>
                    </TextField>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      type='number'
                      label='Total Units'
                      value={formData.total_units}
                      onChange={e => handleInputChange('total_units', e.target.value)}
                      inputProps={{ min: 1 }}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      type='number'
                      label='Available Units'
                      value={formData.available_units}
                      onChange={e => handleInputChange('available_units', e.target.value)}
                      inputProps={{ min: 0 }}
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Images */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant='h6' sx={{ mb: 2 }}>
                  Images
                </Typography>
                <Typography variant='body2' color='text.secondary' sx={{ mb: 3 }}>
                  Upload up to 7 images. First image will be primary.
                </Typography>

                {imagePreviews.length > 0 && (
                  <Box sx={{ mb: 3 }}>
                    <Grid container spacing={2}>
                      {imagePreviews.map((preview, index) => (
                        <Grid item xs={6} sm={4} md={3} lg={2} key={index}>
                          <Box
                            sx={{
                              position: 'relative',
                              paddingTop: '100%',
                              borderRadius: 1,
                              overflow: 'hidden',
                              border: '2px solid',
                              borderColor: index === 0 ? 'primary.main' : 'divider'
                            }}
                          >
                            <Box
                              sx={{
                                position: 'absolute',
                                top: 0,
                                left: 0,
                                right: 0,
                                bottom: 0,
                                backgroundImage: `url(${preview})`,
                                backgroundSize: 'cover',
                                backgroundPosition: 'center'
                              }}
                            />
                            {index === 0 && (
                              <Chip
                                label='Primary'
                                size='small'
                                color='primary'
                                sx={{ position: 'absolute', top: 8, left: 8 }}
                              />
                            )}
                            <IconButton
                              size='small'
                              onClick={() => handleRemoveImage(index)}
                              sx={{
                                position: 'absolute',
                                top: 8,
                                right: 8,
                                bgcolor: 'background.paper',
                                '&:hover': { bgcolor: 'error.main', color: 'white' }
                              }}
                            >
                              <i className='ri-close-line' />
                            </IconButton>
                          </Box>
                        </Grid>
                      ))}
                    </Grid>
                  </Box>
                )}

                <Button variant='outlined' component='label' disabled={selectedImages.length >= 7}>
                  <i className='ri-upload-2-line' style={{ marginRight: 8 }} />
                  Choose Images
                  <input type='file' hidden multiple accept='image/*' onChange={handleImageSelect} />
                </Button>
                <Typography variant='caption' color='text.secondary' sx={{ ml: 2 }}>
                  {selectedImages.length}/7 images
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Additional Options */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant='h6' sx={{ mb: 3 }}>
                  Additional Options
                </Typography>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={formData.featured}
                      onChange={e => handleInputChange('featured', e.target.checked)}
                    />
                  }
                  label='Feature this equipment'
                />
              </CardContent>
            </Card>
          </Grid>

          {/* Submit Button */}
          <Grid item xs={12}>
            <Box display='flex' gap={2} justifyContent='flex-end'>
              <Button variant='outlined' onClick={() => router.push('/equipment')} disabled={loading}>
                Cancel
              </Button>
              <Button
                type='submit'
                variant='contained'
                disabled={loading}
                startIcon={loading ? <CircularProgress size={20} /> : <i className='ri-add-line' />}
              >
                {loading ? 'Creating...' : 'Add Equipment'}
              </Button>
            </Box>
          </Grid>
        </Grid>
      </form>
    </Box>
  )
}

export default AddEquipment
```

---

## Key Changes Made:

1. ✅ **`manufacture_year` → `year`**
2. ✅ **`model` → `model_number`**
3. ✅ **`location` → `city` (with 3-letter codes)**
4. ✅ **Added `country` field (defaults to 'UAE')**
5. ✅ **`is_featured` → `featured`**
6. ✅ **Removed** `serial_number`, `deposit_required`, `insurance_included`, `delivery_available`
7. ✅ **Added specifications management** (array of {name, value} objects)
8. ✅ **Added `total_units` field**
9. ✅ **City uses 3-letter codes** (DXB, AUH, SHJ, etc.)

Now your form should work perfectly with the backend! 🎉
