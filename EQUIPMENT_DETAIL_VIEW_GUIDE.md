# Equipment Detail View & Status Filtering Guide

## ❌ The Status Filter Issue

**Your Request:** `GET /api/equipment/equipment/?status=unavailable`
**Result:** `400 Bad Request`

**Why?** The status value `unavailable` is **not a valid status choice**!

## ✅ Valid Status Values

The Equipment model has these **specific status choices**:

```python
STATUS_CHOICES = (
    ('available', 'Available'),           # Equipment ready to rent
    ('maintenance', 'Under Maintenance'), # Being serviced
    ('rented', 'Currently Rented'),       # Out on rental
    ('reserved', 'Reserved'),             # Reserved for upcoming rental
    ('inactive', 'Inactive'),             # Not available for listing
)
```

## 📋 Correct API Endpoints for Status Filtering

### Get Available Equipment
```bash
GET /api/equipment/equipment/?status=available
```

### Get Rented Equipment
```bash
GET /api/equipment/equipment/?status=rented
```

### Get Equipment Under Maintenance
```bash
GET /api/equipment/equipment/?status=maintenance
```

### Get Reserved Equipment
```bash
GET /api/equipment/equipment/?status=reserved
```

### Get Inactive Equipment
```bash
GET /api/equipment/equipment/?status=inactive
```

### Get Multiple Statuses (if you want "unavailable" = rented OR maintenance OR reserved)
You'll need to make separate requests and combine results in frontend, OR:

```javascript
// Frontend approach - fetch all and filter
const response = await equipmentAPI.getEquipment()
const unavailableEquipment = response.data.filter(eq => 
  ['rented', 'maintenance', 'reserved', 'inactive'].includes(eq.status)
)
```

---

## 🔍 Equipment Detail View Implementation

### API Endpoint for Single Equipment Details
```bash
GET /api/equipment/equipment/{id}/

# Example:
GET /api/equipment/equipment/5/
```

### Response Structure
```json
{
  "id": 5,
  "name": "CAT 320 Excavator",
  "description": "Heavy-duty excavator suitable for construction...",
  "category": {
    "id": 2,
    "name": "Excavators",
    "icon": "/media/category_icons/excavator.png"
  },
  "seller_company": {
    "id": 1,
    "company_name": "ABC Equipment Rentals",
    "email": "contact@abcrentals.com",
    "phone": "+1234567890",
    "city": "NYC",
    "country": "USA"
  },
  "manufacturer": "Caterpillar",
  "model_number": "320GC",
  "year": 2022,
  "weight": "23000.00",
  "dimensions": "980x290x310",
  "fuel_type": "Diesel",
  "daily_rate": "500.00",
  "weekly_rate": "3000.00",
  "monthly_rate": "10000.00",
  "country": "USA",
  "city": "NYC",
  "status": "available",
  "available_units": 3,
  "featured": true,
  "images": [
    {
      "id": 10,
      "image": "/media/equipment_images/cat320_1.jpg",
      "is_primary": true
    },
    {
      "id": 11,
      "image": "/media/equipment_images/cat320_2.jpg",
      "is_primary": false
    }
  ],
  "specifications": [
    {
      "id": 5,
      "name": "Operating Weight",
      "value": "23000 kg"
    },
    {
      "id": 6,
      "name": "Engine Power",
      "value": "121 HP"
    }
  ],
  "tags": ["heavy duty", "construction", "excavation"],
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-10-20T14:45:00Z"
}
```

---

## 🎨 React Detail View Component

### Complete Detail Page Component

```tsx
'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import {
  Card,
  CardContent,
  CardHeader,
  Typography,
  Box,
  Chip,
  Grid,
  Button,
  CircularProgress,
  Alert,
  Divider,
  Avatar,
  ImageList,
  ImageListItem,
  Dialog,
  DialogContent,
  IconButton
} from '@mui/material'
import { equipmentAPI } from '@/services/api'

const EquipmentDetailView = () => {
  const params = useParams()
  const router = useRouter()
  const equipmentId = params.id

  // States
  const [equipment, setEquipment] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedImage, setSelectedImage] = useState(null)
  const [imageDialogOpen, setImageDialogOpen] = useState(false)

  // Fetch equipment details
  useEffect(() => {
    if (equipmentId) {
      fetchEquipmentDetails()
    }
  }, [equipmentId])

  const fetchEquipmentDetails = async () => {
    try {
      setLoading(true)
      const response = await equipmentAPI.getEquipmentById(equipmentId)
      setEquipment(response.data)
      
      // Set primary image as selected
      const primaryImage = response.data.images?.find(img => img.is_primary)
      setSelectedImage(primaryImage || response.data.images?.[0] || null)
    } catch (err) {
      console.error('Error fetching equipment:', err)
      setError('Failed to load equipment details')
    } finally {
      setLoading(false)
    }
  }

  // Status badge color
  const getStatusColor = (status) => {
    switch (status) {
      case 'available': return 'success'
      case 'rented': return 'error'
      case 'maintenance': return 'warning'
      case 'reserved': return 'info'
      case 'inactive': return 'default'
      default: return 'default'
    }
  }

  // Open image dialog
  const handleImageClick = (image) => {
    setSelectedImage(image)
    setImageDialogOpen(true)
  }

  if (loading) {
    return (
      <Box display='flex' justifyContent='center' alignItems='center' minHeight='400px'>
        <CircularProgress />
      </Box>
    )
  }

  if (error || !equipment) {
    return (
      <Box>
        <Alert severity='error'>{error || 'Equipment not found'}</Alert>
        <Button onClick={() => router.back()} sx={{ mt: 2 }}>
          Go Back
        </Button>
      </Box>
    )
  }

  return (
    <Box>
      {/* Back Button */}
      <Button 
        startIcon={<i className='ri-arrow-left-line' />}
        onClick={() => router.back()}
        sx={{ mb: 2 }}
      >
        Back to Listings
      </Button>

      <Grid container spacing={3}>
        {/* Left Column - Images */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              {/* Main Image */}
              {selectedImage && (
                <Box
                  component='img'
                  src={selectedImage.image}
                  alt={equipment.name}
                  sx={{
                    width: '100%',
                    height: 400,
                    objectFit: 'cover',
                    borderRadius: 1,
                    cursor: 'pointer',
                    mb: 2
                  }}
                  onClick={() => handleImageClick(selectedImage)}
                />
              )}

              {/* Image Thumbnails */}
              {equipment.images?.length > 1 && (
                <ImageList cols={4} gap={8}>
                  {equipment.images.map((image) => (
                    <ImageListItem
                      key={image.id}
                      onClick={() => setSelectedImage(image)}
                      sx={{
                        cursor: 'pointer',
                        border: selectedImage?.id === image.id ? 2 : 0,
                        borderColor: 'primary.main',
                        borderRadius: 1
                      }}
                    >
                      <img
                        src={image.image}
                        alt={equipment.name}
                        loading='lazy'
                        style={{ height: 80, objectFit: 'cover' }}
                      />
                    </ImageListItem>
                  ))}
                </ImageList>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Right Column - Details */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              title={equipment.name}
              subheader={
                <Box display='flex' alignItems='center' gap={1} mt={1}>
                  <Chip 
                    label={equipment.status} 
                    color={getStatusColor(equipment.status)}
                    size='small'
                  />
                  {equipment.featured && (
                    <Chip 
                      label='Featured' 
                      color='primary'
                      size='small'
                      icon={<i className='ri-star-fill' />}
                    />
                  )}
                </Box>
              }
            />
            <CardContent>
              {/* Pricing */}
              <Box mb={3}>
                <Typography variant='h5' color='primary' gutterBottom>
                  ${equipment.daily_rate} / day
                </Typography>
                <Box display='flex' gap={2}>
                  <Typography variant='body2' color='text.secondary'>
                    Weekly: ${equipment.weekly_rate}
                  </Typography>
                  <Typography variant='body2' color='text.secondary'>
                    Monthly: ${equipment.monthly_rate}
                  </Typography>
                </Box>
              </Box>

              <Divider sx={{ my: 2 }} />

              {/* Description */}
              <Box mb={3}>
                <Typography variant='h6' gutterBottom>
                  Description
                </Typography>
                <Typography variant='body2' color='text.secondary'>
                  {equipment.description}
                </Typography>
              </Box>

              <Divider sx={{ my: 2 }} />

              {/* Technical Specs */}
              <Box mb={3}>
                <Typography variant='h6' gutterBottom>
                  Technical Specifications
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant='body2' color='text.secondary'>
                      Manufacturer
                    </Typography>
                    <Typography variant='body1'>{equipment.manufacturer}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant='body2' color='text.secondary'>
                      Model
                    </Typography>
                    <Typography variant='body1'>{equipment.model_number}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant='body2' color='text.secondary'>
                      Year
                    </Typography>
                    <Typography variant='body1'>{equipment.year}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant='body2' color='text.secondary'>
                      Weight
                    </Typography>
                    <Typography variant='body1'>{equipment.weight} kg</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant='body2' color='text.secondary'>
                      Dimensions
                    </Typography>
                    <Typography variant='body1'>{equipment.dimensions} cm</Typography>
                  </Grid>
                  {equipment.fuel_type && (
                    <Grid item xs={6}>
                      <Typography variant='body2' color='text.secondary'>
                        Fuel Type
                      </Typography>
                      <Typography variant='body1'>{equipment.fuel_type}</Typography>
                    </Grid>
                  )}
                </Grid>
              </Box>

              {/* Additional Specifications */}
              {equipment.specifications?.length > 0 && (
                <>
                  <Divider sx={{ my: 2 }} />
                  <Box mb={3}>
                    <Typography variant='h6' gutterBottom>
                      Additional Specifications
                    </Typography>
                    <Grid container spacing={2}>
                      {equipment.specifications.map((spec) => (
                        <Grid item xs={6} key={spec.id}>
                          <Typography variant='body2' color='text.secondary'>
                            {spec.name}
                          </Typography>
                          <Typography variant='body1'>{spec.value}</Typography>
                        </Grid>
                      ))}
                    </Grid>
                  </Box>
                </>
              )}

              {/* Tags */}
              {equipment.tags?.length > 0 && (
                <>
                  <Divider sx={{ my: 2 }} />
                  <Box mb={3}>
                    <Typography variant='h6' gutterBottom>
                      Tags
                    </Typography>
                    <Box display='flex' gap={1} flexWrap='wrap'>
                      {equipment.tags.map((tag, index) => (
                        <Chip key={index} label={tag} size='small' />
                      ))}
                    </Box>
                  </Box>
                </>
              )}

              <Divider sx={{ my: 2 }} />

              {/* Location */}
              <Box mb={3}>
                <Typography variant='h6' gutterBottom>
                  Location
                </Typography>
                <Typography variant='body1'>
                  {equipment.city}, {equipment.country}
                </Typography>
              </Box>

              {/* Availability */}
              <Box mb={3}>
                <Typography variant='body2' color='text.secondary'>
                  Available Units: {equipment.available_units}
                </Typography>
              </Box>

              <Divider sx={{ my: 2 }} />

              {/* Seller Info */}
              <Box mb={3}>
                <Typography variant='h6' gutterBottom>
                  Seller Information
                </Typography>
                <Box display='flex' alignItems='center' gap={2}>
                  <Avatar sx={{ width: 48, height: 48 }}>
                    {equipment.seller_company?.company_name?.[0] || 'S'}
                  </Avatar>
                  <Box>
                    <Typography variant='body1' fontWeight='bold'>
                      {equipment.seller_company?.company_name || 'Unknown'}
                    </Typography>
                    <Typography variant='body2' color='text.secondary'>
                      {equipment.seller_company?.email}
                    </Typography>
                    {equipment.seller_company?.phone && (
                      <Typography variant='body2' color='text.secondary'>
                        {equipment.seller_company.phone}
                      </Typography>
                    )}
                  </Box>
                </Box>
              </Box>

              {/* Action Buttons */}
              <Box display='flex' gap={2} mt={3}>
                <Button 
                  variant='contained' 
                  fullWidth
                  disabled={equipment.status !== 'available'}
                  startIcon={<i className='ri-shopping-cart-line' />}
                >
                  {equipment.status === 'available' ? 'Request Rental' : `Currently ${equipment.status}`}
                </Button>
                <IconButton color='primary'>
                  <i className='ri-heart-line' />
                </IconButton>
                <IconButton color='primary'>
                  <i className='ri-share-line' />
                </IconButton>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Image Full Screen Dialog */}
      <Dialog
        open={imageDialogOpen}
        onClose={() => setImageDialogOpen(false)}
        maxWidth='lg'
        fullWidth
      >
        <DialogContent sx={{ p: 0, position: 'relative' }}>
          <IconButton
            onClick={() => setImageDialogOpen(false)}
            sx={{
              position: 'absolute',
              right: 8,
              top: 8,
              bgcolor: 'background.paper',
              '&:hover': { bgcolor: 'background.default' }
            }}
          >
            <i className='ri-close-line' />
          </IconButton>
          {selectedImage && (
            <img
              src={selectedImage.image}
              alt={equipment.name}
              style={{ width: '100%', height: 'auto' }}
            />
          )}
        </DialogContent>
      </Dialog>
    </Box>
  )
}

export default EquipmentDetailView
```

---

## 🔧 API Service Methods

Add these to your `equipmentAPI` service:

```javascript
// services/api.js or services/equipmentAPI.js

export const equipmentAPI = {
  // ... existing methods

  // Get single equipment by ID
  getEquipmentById: (id) => axios.get(`/api/equipment/equipment/${id}/`),

  // Get equipment by status
  getEquipmentByStatus: (status) => axios.get(`/api/equipment/equipment/?status=${status}`),

  // Get equipment by multiple filters
  getEquipmentFiltered: (filters) => {
    const params = new URLSearchParams(filters).toString()
    return axios.get(`/api/equipment/equipment/?${params}`)
  }
}
```

---

## 📱 Usage Examples

### Navigate to Detail View
```javascript
// From equipment card
<Card onClick={() => router.push(`/equipment/${equipment.id}`)}>
  ...
</Card>
```

### Filter by Status
```javascript
// Get only available equipment
const availableEquipment = await equipmentAPI.getEquipmentByStatus('available')

// Get rented equipment
const rentedEquipment = await equipmentAPI.getEquipmentByStatus('rented')

// Get equipment under maintenance
const maintenanceEquipment = await equipmentAPI.getEquipmentByStatus('maintenance')
```

### Multiple Filters
```javascript
const filters = {
  status: 'available',
  category: 5,
  city: 'NYC',
  featured: true
}
const filteredEquipment = await equipmentAPI.getEquipmentFiltered(filters)
```

---

## ✅ Summary

1. **❌ `status=unavailable`** - Not valid! Use the correct status values.
2. **✅ Valid statuses:** `available`, `rented`, `maintenance`, `reserved`, `inactive`
3. **🔍 Detail View:** Use `GET /api/equipment/equipment/{id}/` for full details
4. **🎨 Frontend:** Complete React component provided above

The detail view component includes:
- Image gallery with thumbnails
- Full technical specifications
- Pricing information
- Seller contact details
- Status badges
- Action buttons (rent, favorite, share)
- Responsive layout
