# Frontend Development Guide - Equipment Listing & Order Management

## 🎯 Overview
This guide provides complete specifications for frontend developers to build:
1. Equipment listing with operating manual upload
2. Complete order/rental status management system
3. Required UI components and flows

---

## Part 1: Equipment Listing Management

### 📋 Equipment Create/Edit Form

#### Required Fields & Components

```javascript
// Equipment Creation/Edit Form Structure
const equipmentFormFields = {
  // Basic Information
  name: {
    type: 'text',
    required: true,
    placeholder: 'e.g., CAT 320 Excavator',
    validation: 'Min 3 chars, max 255'
  },
  
  description: {
    type: 'textarea',
    required: true,
    placeholder: 'Detailed description of the equipment...',
    rows: 5
  },
  
  category_id: {
    type: 'select',
    required: true,
    apiEndpoint: '/api/equipment/categories/',
    displayField: 'name',
    valueField: 'id'
  },
  
  // Specifications
  manufacturer: {
    type: 'text',
    required: false,
    placeholder: 'e.g., Caterpillar'
  },
  
  model_number: {
    type: 'text',
    required: false,
    placeholder: 'e.g., 320GC'
  },
  
  year: {
    type: 'number',
    required: false,
    placeholder: '2023'
  },
  
  weight: {
    type: 'text',
    required: false,
    placeholder: 'e.g., 20 tons',
    helper: 'Include units'
  },
  
  dimensions: {
    type: 'text',
    required: false,
    placeholder: 'e.g., 9.5m x 3m x 3m'
  },
  
  fuel_type: {
    type: 'select',
    required: false,
    options: ['diesel', 'petrol', 'electric', 'hybrid', 'other']
  },
  
  // Pricing
  daily_rate: {
    type: 'number',
    required: true,
    min: 0,
    step: 0.01,
    prefix: '$',
    placeholder: '500.00'
  },
  
  weekly_rate: {
    type: 'number',
    required: false,
    min: 0,
    step: 0.01,
    prefix: '$',
    helper: 'Optional discount for weekly rentals'
  },
  
  monthly_rate: {
    type: 'number',
    required: false,
    min: 0,
    step: 0.01,
    prefix: '$',
    helper: 'Optional discount for monthly rentals'
  },
  
  // Location
  country: {
    type: 'select',
    required: true,
    apiEndpoint: '/api/countries/',
    placeholder: 'Select country'
  },
  
  city: {
    type: 'select',
    required: true,
    dependsOn: 'country',
    placeholder: 'Select city'
  },
  
  // Availability
  status: {
    type: 'select',
    required: true,
    options: [
      { value: 'available', label: 'Available for Rent' },
      { value: 'rented', label: 'Currently Rented' },
      { value: 'maintenance', label: 'Under Maintenance' },
      { value: 'unavailable', label: 'Unavailable' }
    ],
    default: 'available'
  },
  
  total_units: {
    type: 'number',
    required: true,
    min: 1,
    default: 1,
    helper: 'How many units of this equipment do you have?'
  },
  
  available_units: {
    type: 'number',
    required: true,
    min: 0,
    helper: 'How many are currently available? (Must be ≤ total units)',
    validation: 'Must not exceed total_units'
  },
  
  // Promotional
  featured: {
    type: 'checkbox',
    required: false,
    label: 'Featured listing',
    helper: 'Show this equipment prominently'
  },
  
  is_todays_deal: {
    type: 'checkbox',
    required: false,
    label: "Today's Deal",
    helper: 'Apply special discount'
  },
  
  deal_discount_percentage: {
    type: 'number',
    required: false,
    min: 0,
    max: 100,
    dependsOn: 'is_todays_deal',
    placeholder: '10',
    helper: 'Discount percentage (e.g., 10 for 10% off)'
  },
  
  // 🆕 OPERATING MANUAL SECTION - CRITICAL!
  operating_manual: {
    type: 'file',
    required: false,
    accept: '.pdf,.doc,.docx',
    maxSize: '10MB',
    label: 'Operating Manual (Optional)',
    helper: 'Upload equipment operating manual (PDF, DOC, DOCX)',
    icon: '📄',
    note: '⚠️ Manual will be locked until customer completes payment'
  },
  
  manual_description: {
    type: 'textarea',
    required: false,
    placeholder: 'Describe what\'s covered in the manual...\ne.g., Safety procedures, operating instructions, maintenance schedules',
    rows: 3,
    dependsOn: 'operating_manual',
    helper: 'Help customers understand what information the manual contains'
  },
  
  // Images (handled separately with drag-drop)
  images: {
    type: 'image-upload',
    required: false,
    multiple: true,
    maxFiles: 7,
    maxSize: '5MB per image',
    accept: 'image/*',
    helper: 'Upload up to 7 images. First image will be primary.'
  },
  
  // Tags
  tag_names: {
    type: 'multi-select-creatable',
    required: false,
    placeholder: 'Add tags (e.g., heavy-duty, new, hydraulic)',
    helper: 'Press Enter to add each tag'
  },
  
  // Specifications (dynamic list)
  specifications_data: {
    type: 'dynamic-list',
    required: false,
    fields: [
      { name: 'name', type: 'text', placeholder: 'e.g., Max Digging Depth' },
      { name: 'value', type: 'text', placeholder: 'e.g., 6.5 meters' }
    ],
    addButtonLabel: '+ Add Specification'
  }
};
```

---

### 🎨 Equipment Form UI Component (React)

```jsx
import React, { useState } from 'react';
import { Form, Input, Select, Button, Upload, Tag, message } from 'antd';
import { UploadOutlined, FileTextOutlined } from '@ant-design/icons';

function EquipmentForm({ equipment = null, onSubmit }) {
  const [form] = Form.useForm();
  const [operatingManual, setOperatingManual] = useState(null);
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (values) => {
    setLoading(true);
    
    try {
      // Create FormData for file uploads
      const formData = new FormData();
      
      // Add all text fields
      Object.keys(values).forEach(key => {
        if (values[key] !== undefined && values[key] !== null) {
          if (key === 'tag_names' && Array.isArray(values[key])) {
            formData.append(key, JSON.stringify(values[key]));
          } else if (key === 'specifications_data' && Array.isArray(values[key])) {
            formData.append(key, JSON.stringify(values[key]));
          } else {
            formData.append(key, values[key]);
          }
        }
      });
      
      // 🆕 Add operating manual if uploaded
      if (operatingManual) {
        formData.append('operating_manual', operatingManual);
      }
      
      // Add images
      images.forEach((img, index) => {
        formData.append(`image_${index}`, img.file);
        if (index === 0) {
          formData.append('primary_image_index', '0');
        }
      });
      
      // API Call
      const endpoint = equipment 
        ? `/api/equipment/equipment/${equipment.id}/`
        : '/api/equipment/equipment/';
      
      const method = equipment ? 'PUT' : 'POST';
      
      const response = await fetch(endpoint, {
        method,
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: formData
      });
      
      if (response.ok) {
        const data = await response.json();
        message.success(equipment ? 'Equipment updated!' : 'Equipment created!');
        onSubmit(data);
      } else {
        const error = await response.json();
        message.error(error.message || 'Failed to save equipment');
      }
    } catch (error) {
      message.error('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Form
      form={form}
      layout="vertical"
      onFinish={handleSubmit}
      initialValues={equipment}
    >
      {/* Basic Information */}
      <h3>Basic Information</h3>
      
      <Form.Item
        name="name"
        label="Equipment Name"
        rules={[{ required: true, message: 'Name is required' }]}
      >
        <Input placeholder="e.g., CAT 320 Excavator" />
      </Form.Item>
      
      <Form.Item
        name="description"
        label="Description"
        rules={[{ required: true, message: 'Description is required' }]}
      >
        <Input.TextArea 
          rows={5}
          placeholder="Detailed description of the equipment..."
        />
      </Form.Item>
      
      <Form.Item
        name="category_id"
        label="Category"
        rules={[{ required: true, message: 'Category is required' }]}
      >
        <Select placeholder="Select category">
          {/* Load from /api/equipment/categories/ */}
        </Select>
      </Form.Item>
      
      {/* Pricing */}
      <h3>Pricing</h3>
      
      <Form.Item
        name="daily_rate"
        label="Daily Rate ($)"
        rules={[{ required: true, message: 'Daily rate is required' }]}
      >
        <Input type="number" step="0.01" min="0" prefix="$" />
      </Form.Item>
      
      {/* Availability */}
      <h3>Availability</h3>
      
      <Form.Item
        name="total_units"
        label="Total Units"
        rules={[{ required: true, message: 'Total units is required' }]}
      >
        <Input type="number" min="1" />
      </Form.Item>
      
      <Form.Item
        name="available_units"
        label="Available Units"
        rules={[{ required: true, message: 'Available units is required' }]}
      >
        <Input type="number" min="0" />
      </Form.Item>
      
      {/* 🆕 OPERATING MANUAL SECTION */}
      <h3>📄 Operating Manual (Optional)</h3>
      <div style={{ background: '#f0f7ff', padding: 16, borderRadius: 8, marginBottom: 16 }}>
        <p style={{ margin: 0, marginBottom: 8 }}>
          <strong>ℹ️ About Operating Manuals:</strong>
        </p>
        <ul style={{ margin: 0, paddingLeft: 20 }}>
          <li>Upload equipment operating manual for customers</li>
          <li>Manual will be <strong>locked 🔒</strong> until customer completes payment</li>
          <li>After payment, manual automatically <strong>unlocks 🔓</strong></li>
          <li>Accepted formats: PDF, DOC, DOCX (Max 10MB)</li>
        </ul>
      </div>
      
      <Form.Item
        name="operating_manual"
        label="Upload Operating Manual"
      >
        <Upload
          accept=".pdf,.doc,.docx"
          maxCount={1}
          beforeUpload={(file) => {
            // Validate file size
            const isLt10M = file.size / 1024 / 1024 < 10;
            if (!isLt10M) {
              message.error('File must be smaller than 10MB!');
              return false;
            }
            setOperatingManual(file);
            return false; // Prevent auto upload
          }}
          onRemove={() => setOperatingManual(null)}
        >
          <Button icon={<FileTextOutlined />}>
            Choose Manual File
          </Button>
        </Upload>
        <p style={{ color: '#666', fontSize: 12, marginTop: 8 }}>
          {operatingManual && `Selected: ${operatingManual.name}`}
        </p>
      </Form.Item>
      
      <Form.Item
        name="manual_description"
        label="Manual Description"
        help="Describe what's covered in the manual to help customers"
      >
        <Input.TextArea
          rows={3}
          placeholder="e.g., Complete operating instructions, safety procedures, maintenance schedules, troubleshooting guide"
          disabled={!operatingManual}
        />
      </Form.Item>
      
      {/* Images */}
      <h3>Images</h3>
      <Form.Item label="Equipment Images (Up to 7)">
        <Upload
          accept="image/*"
          multiple
          maxCount={7}
          listType="picture-card"
          beforeUpload={(file) => {
            setImages(prev => [...prev, { file }]);
            return false;
          }}
          onRemove={(file) => {
            setImages(prev => prev.filter(img => img.file !== file));
          }}
        >
          {images.length < 7 && (
            <div>
              <UploadOutlined />
              <div>Upload</div>
            </div>
          )}
        </Upload>
      </Form.Item>
      
      {/* Submit */}
      <Form.Item>
        <Button 
          type="primary" 
          htmlType="submit" 
          loading={loading}
          size="large"
        >
          {equipment ? 'Update Equipment' : 'Create Equipment'}
        </Button>
      </Form.Item>
    </Form>
  );
}

export default EquipmentForm;
```

---

### 📱 Mobile Equipment Form (React Native)

```jsx
import React, { useState } from 'react';
import { View, Text, TextInput, Button, ScrollView, Alert } from 'react-native';
import DocumentPicker from 'react-native-document-picker';
import { launchImageLibrary } from 'react-native-image-picker';

function MobileEquipmentForm({ navigation }) {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    daily_rate: '',
    total_units: '1',
    available_units: '1',
    manual_description: ''
  });
  
  const [operatingManual, setOperatingManual] = useState(null);
  const [images, setImages] = useState([]);

  const pickManual = async () => {
    try {
      const result = await DocumentPicker.pick({
        type: [
          DocumentPicker.types.pdf,
          DocumentPicker.types.doc,
          DocumentPicker.types.docx
        ]
      });
      
      if (result[0].size > 10 * 1024 * 1024) {
        Alert.alert('Error', 'File must be less than 10MB');
        return;
      }
      
      setOperatingManual(result[0]);
      Alert.alert('Success', `Manual selected: ${result[0].name}`);
    } catch (err) {
      if (!DocumentPicker.isCancel(err)) {
        Alert.alert('Error', 'Failed to pick document');
      }
    }
  };

  const pickImages = () => {
    launchImageLibrary({
      mediaType: 'photo',
      maxWidth: 1024,
      maxHeight: 1024,
      quality: 0.8,
      selectionLimit: 7
    }, (response) => {
      if (response.assets) {
        setImages(response.assets);
      }
    });
  };

  const handleSubmit = async () => {
    // Validate required fields
    if (!formData.name || !formData.description || !formData.daily_rate) {
      Alert.alert('Error', 'Please fill all required fields');
      return;
    }

    const data = new FormData();
    
    // Add text fields
    Object.keys(formData).forEach(key => {
      data.append(key, formData[key]);
    });
    
    // Add operating manual
    if (operatingManual) {
      data.append('operating_manual', {
        uri: operatingManual.uri,
        type: operatingManual.type,
        name: operatingManual.name
      });
    }
    
    // Add images
    images.forEach((img, index) => {
      data.append(`image_${index}`, {
        uri: img.uri,
        type: img.type,
        name: img.fileName || `image_${index}.jpg`
      });
    });

    try {
      const response = await fetch('/api/equipment/equipment/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: data
      });

      if (response.ok) {
        Alert.alert('Success', 'Equipment created!');
        navigation.goBack();
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to create equipment');
    }
  };

  return (
    <ScrollView style={{ padding: 16 }}>
      <Text style={styles.heading}>Add Equipment</Text>
      
      {/* Basic Fields */}
      <TextInput
        placeholder="Equipment Name *"
        value={formData.name}
        onChangeText={(text) => setFormData({...formData, name: text})}
        style={styles.input}
      />
      
      <TextInput
        placeholder="Description *"
        value={formData.description}
        onChangeText={(text) => setFormData({...formData, description: text})}
        multiline
        numberOfLines={4}
        style={styles.input}
      />
      
      <TextInput
        placeholder="Daily Rate ($) *"
        value={formData.daily_rate}
        onChangeText={(text) => setFormData({...formData, daily_rate: text})}
        keyboardType="decimal-pad"
        style={styles.input}
      />
      
      {/* Operating Manual Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>📄 Operating Manual (Optional)</Text>
        <Text style={styles.helperText}>
          Upload manual - customers can access after payment
        </Text>
        
        <Button
          title={operatingManual ? `✅ ${operatingManual.name}` : "Choose Manual File"}
          onPress={pickManual}
        />
        
        {operatingManual && (
          <TextInput
            placeholder="Describe what's in the manual..."
            value={formData.manual_description}
            onChangeText={(text) => setFormData({...formData, manual_description: text})}
            multiline
            numberOfLines={3}
            style={[styles.input, { marginTop: 10 }]}
          />
        )}
      </View>
      
      {/* Images */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Images</Text>
        <Button
          title={`Choose Images (${images.length}/7)`}
          onPress={pickImages}
        />
      </View>
      
      {/* Submit */}
      <Button
        title="Create Equipment"
        onPress={handleSubmit}
        color="#4CAF50"
      />
    </ScrollView>
  );
}

const styles = {
  heading: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    marginBottom: 16
  },
  section: {
    backgroundColor: '#f0f7ff',
    padding: 16,
    borderRadius: 8,
    marginBottom: 16
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 8
  },
  helperText: {
    fontSize: 12,
    color: '#666',
    marginBottom: 12
  }
};

export default MobileEquipmentForm;
```

---

## Part 2: Order/Rental Status Management

### 📊 Complete Status Flow Implementation

#### Status Configuration Object

```javascript
// Central status configuration
export const RENTAL_STATUSES = {
  pending: {
    label: 'Pending Approval',
    icon: '⏳',
    color: '#FFA500',
    description: 'Waiting for seller approval',
    customerActions: ['cancel'],
    sellerActions: ['approve', 'reject'],
    nextStatuses: ['approved', 'cancelled']
  },
  approved: {
    label: 'Approved - Ready to Pay',
    icon: '✅',
    color: '#4CAF50',
    description: 'Approved, awaiting payment',
    customerActions: ['pay', 'cancel'],
    sellerActions: [],
    nextStatuses: ['confirmed', 'cancelled']
  },
  confirmed: {
    label: 'Payment Confirmed',
    icon: '💰',
    color: '#2196F3',
    description: 'Payment received, preparing equipment',
    customerActions: [],
    sellerActions: ['start_preparing'],
    nextStatuses: ['preparing', 'cancelled']
  },
  preparing: {
    label: 'Equipment Being Prepared',
    icon: '📦',
    color: '#9C27B0',
    description: 'Seller is preparing equipment',
    customerActions: [],
    sellerActions: ['mark_ready'],
    nextStatuses: ['ready_for_pickup']
  },
  ready_for_pickup: {
    label: 'Ready for Pickup/Delivery',
    icon: '✅',
    color: '#4CAF50',
    description: 'Equipment ready, awaiting delivery',
    customerActions: [],
    sellerActions: ['start_delivery'],
    nextStatuses: ['out_for_delivery']
  },
  out_for_delivery: {
    label: 'Out for Delivery',
    icon: '🚚',
    color: '#FF9800',
    description: 'Driver delivering equipment',
    customerActions: [],
    sellerActions: ['confirm_delivery'], // REQUIRES PHOTO!
    nextStatuses: ['delivered'],
    requiresProof: true
  },
  delivered: {
    label: 'Equipment Delivered',
    icon: '✅',
    color: '#4CAF50',
    description: 'Equipment delivered to customer',
    customerActions: ['view_documents', 'report_issue'],
    sellerActions: ['upload_receipt'], // If cash on delivery
    nextStatuses: ['in_progress'],
    documentsUnlocked: true // Operating manual now accessible!
  },
  in_progress: {
    label: 'Rental Active',
    icon: '🔄',
    color: '#2196F3',
    description: 'Rental period ongoing',
    customerActions: ['request_return'],
    sellerActions: [],
    nextStatuses: ['return_requested', 'overdue']
  },
  return_requested: {
    label: 'Return Requested',
    icon: '🔙',
    color: '#FF9800',
    description: 'Customer requested return',
    customerActions: [],
    sellerActions: ['start_return_pickup'],
    nextStatuses: ['returning']
  },
  returning: {
    label: 'Equipment Returning',
    icon: '🚚',
    color: '#FF9800',
    description: 'Equipment being picked up',
    customerActions: [],
    sellerActions: ['confirm_return'], // REQUIRES PHOTO!
    nextStatuses: ['completed'],
    requiresProof: true
  },
  completed: {
    label: 'Rental Completed',
    icon: '⭐',
    color: '#4CAF50',
    description: 'Rental successfully completed',
    customerActions: ['write_review'],
    sellerActions: ['view_analytics'],
    nextStatuses: [],
    createsSaleRecord: true // Backend creates RentalSale automatically
  },
  cancelled: {
    label: 'Cancelled',
    icon: '❌',
    color: '#F44336',
    description: 'Rental cancelled',
    customerActions: [],
    sellerActions: [],
    nextStatuses: []
  },
  overdue: {
    label: 'OVERDUE',
    icon: '⚠️',
    color: '#F44336',
    description: 'Past return date',
    customerActions: ['request_return'],
    sellerActions: ['contact_customer', 'file_dispute'],
    nextStatuses: ['returning', 'dispute']
  },
  dispute: {
    label: 'Under Dispute',
    icon: '⚠️',
    color: '#FF5722',
    description: 'Issues being resolved',
    customerActions: ['upload_evidence'],
    sellerActions: ['upload_evidence', 'resolve'],
    nextStatuses: ['completed', 'cancelled']
  }
};
```

---

### 🎨 Status Display Component

```jsx
import React from 'react';
import { Badge, Tooltip } from 'antd';
import { RENTAL_STATUSES } from './statusConfig';

function RentalStatusBadge({ status }) {
  const config = RENTAL_STATUSES[status] || RENTAL_STATUSES.pending;
  
  return (
    <Tooltip title={config.description}>
      <Badge
        count={`${config.icon} ${config.label}`}
        style={{ 
          backgroundColor: config.color,
          cursor: 'pointer'
        }}
      />
    </Tooltip>
  );
}

export default RentalStatusBadge;
```

---

### 📱 Mobile Status Badge

```jsx
import React from 'react';
import { View, Text } from 'react-native';
import { RENTAL_STATUSES } from './statusConfig';

function MobileStatusBadge({ status }) {
  const config = RENTAL_STATUSES[status] || RENTAL_STATUSES.pending;
  
  return (
    <View style={{
      backgroundColor: config.color,
      paddingHorizontal: 12,
      paddingVertical: 6,
      borderRadius: 16,
      alignSelf: 'flex-start'
    }}>
      <Text style={{ color: '#fff', fontWeight: 'bold' }}>
        {config.icon} {config.label}
      </Text>
    </View>
  );
}
```

---

### 🎯 Action Buttons Component

```jsx
import React from 'react';
import { Button, Space } from 'antd';
import { RENTAL_STATUSES } from './statusConfig';

function RentalActions({ rental, userType, onAction }) {
  const config = RENTAL_STATUSES[rental.status];
  const actions = userType === 'customer' 
    ? config.customerActions 
    : config.sellerActions;
  
  const actionButtons = {
    // Customer Actions
    cancel: {
      label: 'Cancel Request',
      type: 'default',
      danger: true,
      onClick: () => onAction('cancel', rental.id)
    },
    pay: {
      label: '💳 Make Payment',
      type: 'primary',
      onClick: () => onAction('pay', rental.id)
    },
    request_return: {
      label: '🔙 Request Return',
      type: 'default',
      onClick: () => onAction('request_return', rental.id)
    },
    write_review: {
      label: '⭐ Write Review',
      type: 'primary',
      onClick: () => onAction('write_review', rental.id)
    },
    view_documents: {
      label: '📄 View Documents',
      type: 'default',
      onClick: () => onAction('view_documents', rental.id)
    },
    report_issue: {
      label: '⚠️ Report Issue',
      type: 'default',
      danger: true,
      onClick: () => onAction('report_issue', rental.id)
    },
    
    // Seller Actions
    approve: {
      label: '✅ Approve',
      type: 'primary',
      onClick: () => onAction('approve', rental.id)
    },
    reject: {
      label: '❌ Reject',
      type: 'default',
      danger: true,
      onClick: () => onAction('reject', rental.id)
    },
    start_preparing: {
      label: '📦 Start Preparing',
      type: 'primary',
      onClick: () => onAction('start_preparing', rental.id)
    },
    mark_ready: {
      label: '✅ Mark Ready',
      type: 'primary',
      onClick: () => onAction('mark_ready', rental.id)
    },
    start_delivery: {
      label: '🚚 Start Delivery',
      type: 'primary',
      onClick: () => onAction('start_delivery', rental.id)
    },
    confirm_delivery: {
      label: '📸 Confirm Delivery',
      type: 'primary',
      onClick: () => onAction('confirm_delivery', rental.id),
      requiresPhoto: true
    },
    upload_receipt: {
      label: '📄 Upload Receipt',
      type: 'default',
      onClick: () => onAction('upload_receipt', rental.id)
    },
    start_return_pickup: {
      label: '🚚 Start Pickup',
      type: 'primary',
      onClick: () => onAction('start_return_pickup', rental.id)
    },
    confirm_return: {
      label: '✅ Confirm Return',
      type: 'primary',
      onClick: () => onAction('confirm_return', rental.id),
      requiresPhoto: true
    }
  };
  
  return (
    <Space>
      {actions.map(action => {
        const button = actionButtons[action];
        if (!button) return null;
        
        return (
          <Button
            key={action}
            type={button.type}
            danger={button.danger}
            onClick={button.onClick}
          >
            {button.label}
          </Button>
        );
      })}
    </Space>
  );
}

export default RentalActions;
```

---

### 📸 Delivery Confirmation Screen

```jsx
import React, { useState, useEffect } from 'react';
import { Form, Button, Upload, Input, message, Modal } from 'antd';
import { CameraOutlined } from '@ant-design/icons';
import SignatureCanvas from 'react-signature-canvas';

function DeliveryConfirmationModal({ rental, visible, onClose, onConfirm }) {
  const [form] = Form.useForm();
  const [photo, setPhoto] = useState(null);
  const [signature, setSignature] = useState(null);
  const [location, setLocation] = useState(null);
  const signatureRef = useRef();

  useEffect(() => {
    // Get GPS location
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLocation({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          });
        },
        (error) => console.log('GPS error:', error)
      );
    }
  }, []);

  const handleSubmit = async (values) => {
    if (!photo) {
      message.error('Delivery photo is required!');
      return;
    }

    const formData = new FormData();
    formData.append('delivery_photo', photo);
    
    if (signature) {
      formData.append('customer_signature', signature);
    }
    
    formData.append('delivery_notes', values.delivery_notes || '');
    
    if (location) {
      formData.append('gps_latitude', location.latitude);
      formData.append('gps_longitude', location.longitude);
    }

    try {
      const response = await fetch(
        `/api/rentals/rentals/${rental.id}/confirm_delivery/`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: formData
        }
      );

      if (response.ok) {
        message.success('Delivery confirmed!');
        onConfirm();
        onClose();
      } else {
        message.error('Failed to confirm delivery');
      }
    } catch (error) {
      message.error('Network error');
    }
  };

  const saveSignature = () => {
    if (signatureRef.current) {
      const dataURL = signatureRef.current.toDataURL();
      setSignature(dataURL);
      message.success('Signature saved');
    }
  };

  return (
    <Modal
      title="📸 Confirm Delivery"
      visible={visible}
      onCancel={onClose}
      footer={null}
      width={600}
    >
      <Form form={form} layout="vertical" onFinish={handleSubmit}>
        {/* Photo Upload */}
        <Form.Item
          label="Delivery Photo (Required)"
          required
        >
          <Upload
            accept="image/*"
            maxCount={1}
            listType="picture-card"
            beforeUpload={(file) => {
              const isLt5M = file.size / 1024 / 1024 < 5;
              if (!isLt5M) {
                message.error('Image must be smaller than 5MB!');
                return false;
              }
              setPhoto(file);
              return false;
            }}
            onRemove={() => setPhoto(null)}
          >
            {!photo && (
              <div>
                <CameraOutlined />
                <div>Take Photo</div>
              </div>
            )}
          </Upload>
          <p style={{ color: '#999', fontSize: 12 }}>
            Photo of delivered equipment at customer location
          </p>
        </Form.Item>

        {/* Signature (Optional) */}
        <Form.Item label="Customer Signature (Optional)">
          <div style={{ border: '1px solid #d9d9d9', borderRadius: 4 }}>
            <SignatureCanvas
              ref={signatureRef}
              canvasProps={{
                width: 500,
                height: 200,
                className: 'signature-canvas',
                style: { width: '100%' }
              }}
            />
          </div>
          <Button
            size="small"
            onClick={() => signatureRef.current?.clear()}
            style={{ marginTop: 8, marginRight: 8 }}
          >
            Clear
          </Button>
          <Button
            size="small"
            type="primary"
            onClick={saveSignature}
            style={{ marginTop: 8 }}
          >
            Save Signature
          </Button>
        </Form.Item>

        {/* Notes */}
        <Form.Item
          name="delivery_notes"
          label="Delivery Notes"
        >
          <Input.TextArea
            rows={3}
            placeholder="e.g., Equipment delivered in perfect condition. Customer satisfied."
          />
        </Form.Item>

        {/* GPS Info */}
        {location && (
          <p style={{ color: '#52c41a', fontSize: 12 }}>
            ✅ GPS Location captured: {location.latitude.toFixed(6)}, {location.longitude.toFixed(6)}
          </p>
        )}

        {/* Submit */}
        <Form.Item>
          <Button type="primary" htmlType="submit" block size="large">
            Confirm Delivery
          </Button>
        </Form.Item>
      </Form>
    </Modal>
  );
}

export default DeliveryConfirmationModal;
```

---

### 📱 Mobile Delivery Confirmation

```jsx
import React, { useState, useEffect } from 'react';
import { View, Text, Button, Image, Alert, ScrollView } from 'react-native';
import { launchCamera } from 'react-native-image-picker';
import SignatureCapture from 'react-native-signature-capture';
import Geolocation from '@react-native-community/geolocation';

function MobileDeliveryConfirmation({ rental, onConfirm }) {
  const [photo, setPhoto] = useState(null);
  const [signature, setSignature] = useState(null);
  const [location, setLocation] = useState(null);
  const signatureRef = useRef();

  useEffect(() => {
    Geolocation.getCurrentPosition(
      (position) => {
        setLocation({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude
        });
      },
      (error) => console.log(error)
    );
  }, []);

  const takePhoto = () => {
    launchCamera({
      mediaType: 'photo',
      quality: 0.8,
      maxWidth: 1024,
      maxHeight: 1024
    }, (response) => {
      if (response.assets?.[0]) {
        setPhoto(response.assets[0]);
      }
    });
  };

  const handleConfirm = async () => {
    if (!photo) {
      Alert.alert('Error', 'Delivery photo is required!');
      return;
    }

    const formData = new FormData();
    formData.append('delivery_photo', {
      uri: photo.uri,
      type: photo.type,
      name: photo.fileName || 'delivery.jpg'
    });

    if (signature) {
      formData.append('customer_signature', signature);
    }

    if (location) {
      formData.append('gps_latitude', location.latitude);
      formData.append('gps_longitude', location.longitude);
    }

    try {
      const response = await fetch(
        `/api/rentals/rentals/${rental.id}/confirm_delivery/`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          },
          body: formData
        }
      );

      if (response.ok) {
        Alert.alert('Success', 'Delivery confirmed!');
        onConfirm();
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to confirm delivery');
    }
  };

  return (
    <ScrollView style={{ padding: 16 }}>
      <Text style={styles.title}>📸 Confirm Delivery</Text>
      
      {/* Photo */}
      <View style={styles.section}>
        <Text style={styles.label}>Delivery Photo (Required) *</Text>
        <Button
          title={photo ? "✅ Photo Taken" : "📸 Take Photo"}
          onPress={takePhoto}
          color={photo ? "#4CAF50" : "#2196F3"}
        />
        {photo && (
          <Image
            source={{ uri: photo.uri }}
            style={{ width: '100%', height: 200, marginTop: 10, borderRadius: 8 }}
          />
        )}
      </View>

      {/* Signature */}
      <View style={styles.section}>
        <Text style={styles.label}>Customer Signature (Optional)</Text>
        <SignatureCapture
          ref={signatureRef}
          style={{ height: 200, backgroundColor: '#F0F0F0' }}
          onSaveEvent={(result) => {
            setSignature(result.encoded);
            Alert.alert('Success', 'Signature saved');
          }}
        />
        <View style={{ flexDirection: 'row', marginTop: 10 }}>
          <Button
            title="Clear"
            onPress={() => signatureRef.current?.resetImage()}
          />
          <Button
            title="Save Signature"
            onPress={() => signatureRef.current?.saveImage()}
          />
        </View>
      </View>

      {/* GPS Status */}
      {location && (
        <Text style={styles.gpsText}>
          ✅ GPS Location: {location.latitude.toFixed(6)}, {location.longitude.toFixed(6)}
        </Text>
      )}

      {/* Confirm Button */}
      <Button
        title="Confirm Delivery"
        onPress={handleConfirm}
        color="#4CAF50"
        disabled={!photo}
      />
    </ScrollView>
  );
}

const styles = {
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20
  },
  section: {
    marginBottom: 20,
    padding: 16,
    backgroundColor: '#f9f9f9',
    borderRadius: 8
  },
  label: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 10
  },
  gpsText: {
    color: '#4CAF50',
    fontSize: 12,
    marginBottom: 20
  }
};
```

---

### 📄 Document Viewer with Lock Indicators

```jsx
import React, { useState, useEffect } from 'react';
import { List, Card, Button, Tag, Modal } from 'antd';
import { FileTextOutlined, LockOutlined, UnlockOutlined, DownloadOutlined } from '@ant-design/icons';

function RentalDocuments({ rentalId }) {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDocuments();
  }, [rentalId]);

  const fetchDocuments = async () => {
    try {
      const response = await fetch(
        `/api/rentals/rentals/${rentalId}/documents/`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );
      const data = await response.json();
      setDocuments(data.documents);
    } catch (error) {
      console.error('Failed to fetch documents');
    } finally {
      setLoading(false);
    }
  };

  const downloadDocument = (doc) => {
    if (doc.is_locked) {
      Modal.warning({
        title: 'Document Locked',
        content: 'This document will be available after payment is confirmed.',
      });
      return;
    }
    
    window.open(doc.file_url, '_blank');
  };

  return (
    <Card title="📄 Rental Documents" loading={loading}>
      <List
        dataSource={documents}
        renderItem={(doc) => (
          <List.Item
            actions={[
              doc.is_locked ? (
                <Tag color="default">
                  <LockOutlined /> Locked
                </Tag>
              ) : (
                <Button
                  type="primary"
                  icon={<DownloadOutlined />}
                  onClick={() => downloadDocument(doc)}
                >
                  Download
                </Button>
              )
            ]}
          >
            <List.Item.Meta
              avatar={
                doc.is_locked ? (
                  <LockOutlined style={{ fontSize: 24, color: '#999' }} />
                ) : (
                  <FileTextOutlined style={{ fontSize: 24, color: '#1890ff' }} />
                )
              }
              title={doc.title}
              description={
                <>
                  <div>{doc.document_type_display}</div>
                  {doc.is_locked && (
                    <Tag color="orange" style={{ marginTop: 8 }}>
                      Unlocks after payment
                    </Tag>
                  )}
                  {doc.requires_payment && !doc.is_locked && (
                    <Tag color="green" style={{ marginTop: 8 }}>
                      <UnlockOutlined /> Unlocked
                    </Tag>
                  )}
                </>
              }
            />
          </List.Item>
        )}
      />
    </Card>
  );
}

export default RentalDocuments;
```

---

### 🎯 Status Progress Timeline

```jsx
import React from 'react';
import { Steps } from 'antd';
import { RENTAL_STATUSES } from './statusConfig';

function RentalProgressTimeline({ rental }) {
  const statusFlow = [
    'pending',
    'approved',
    'confirmed',
    'preparing',
    'ready_for_pickup',
    'out_for_delivery',
    'delivered',
    'in_progress',
    'return_requested',
    'returning',
    'completed'
  ];

  const currentIndex = statusFlow.indexOf(rental.status);

  return (
    <Steps
      current={currentIndex}
      status={rental.status === 'cancelled' ? 'error' : 'process'}
    >
      {statusFlow.map((status) => {
        const config = RENTAL_STATUSES[status];
        return (
          <Steps.Step
            key={status}
            title={config.icon + ' ' + config.label}
            description={config.description}
          />
        );
      })}
    </Steps>
  );
}

export default RentalProgressTimeline;
```

---

## 📋 API Integration Summary

### Equipment Endpoints

```javascript
// Create Equipment
POST /api/equipment/equipment/
Content-Type: multipart/form-data
Body: FormData with all fields + operating_manual file

// Update Equipment
PUT /api/equipment/equipment/{id}/
Content-Type: multipart/form-data

// Get Equipment List
GET /api/equipment/equipment/

// Get Equipment Detail
GET /api/equipment/equipment/{id}/
```

### Rental Status Endpoints

```javascript
// Create Rental (Booking)
POST /api/rentals/rentals/
Body: { equipment, start_date, end_date, quantity, ... }

// Get Rental Details
GET /api/rentals/rentals/{id}/

// Approve Rental (Seller)
POST /api/rentals/rentals/{id}/approve/

// Update Status (Most transitions)
POST /api/rentals/rentals/{id}/update_status/
Body: { new_status, notes, is_visible_to_customer }

// 🚨 Confirm Delivery (WITH PHOTO)
POST /api/rentals/rentals/{id}/confirm_delivery/
Content-Type: multipart/form-data
Body: {
  delivery_photo: File,
  customer_signature: string,
  delivery_notes: string,
  gps_latitude: float,
  gps_longitude: float
}

// Upload Payment Receipt (Seller)
POST /api/rentals/rentals/{id}/upload_payment_receipt/
Content-Type: multipart/form-data
Body: {
  receipt_file: File,
  receipt_number: string,
  notes: string
}

// Get Documents
GET /api/rentals/rentals/{id}/documents/
Response: { count, documents: [...] }

// Submit Review
POST /api/rentals/rentals/{id}/submit_review/
Body: { equipment_rating, service_rating, review_text, ... }
```

---

## ✅ Implementation Checklist

### Equipment Listing:
- [ ] Add operating manual file upload to equipment form
- [ ] Add manual description textarea
- [ ] Show file selection feedback
- [ ] Validate file size (< 10MB)
- [ ] Validate file types (PDF, DOC, DOCX)
- [ ] Display selected filename
- [ ] Handle file removal
- [ ] Test FormData submission

### Order Status Management:
- [ ] Implement status badge component
- [ ] Create status-specific action buttons
- [ ] Build delivery confirmation screen with photo
- [ ] Add signature pad component
- [ ] Implement GPS location capture
- [ ] Create document viewer with lock indicators
- [ ] Build return confirmation with photo
- [ ] Add progress timeline component
- [ ] Test all status transitions
- [ ] Add error handling for all actions
- [ ] Implement loading states

### Mobile Specific:
- [ ] Camera integration for photos
- [ ] Signature capture library
- [ ] GPS permission handling
- [ ] Image compression for uploads
- [ ] Offline status indicators
- [ ] Push notification handling

---

## 🎯 Critical Notes for Frontend Developers

1. **Operating Manual Upload:**
   - File input MUST support PDF, DOC, DOCX
   - Max file size: 10MB
   - Show clear indication that manual locks until payment
   - Manual description is optional but encouraged

2. **Delivery Confirmation:**
   - Photo is REQUIRED (not optional!)
   - Signature is optional but recommended
   - GPS capture improves accountability
   - Use `confirm_delivery` endpoint, NOT `update_status`

3. **Document Lock Status:**
   - Check `is_locked` field in document response
   - Show lock icon and "Unlocks after payment" message
   - Prevent download attempts on locked documents
   - Refresh documents after payment completed

4. **Status Transitions:**
   - Always show correct actions based on current status
   - Check user type (customer vs seller) for permissions
   - Validate status before allowing transitions
   - Show loading states during API calls
   - Handle errors gracefully

5. **Auto-Approval:**
   - If quantity < 5: Status = "approved" immediately
   - Show "Auto-Approved" badge
   - Allow immediate payment
   - If quantity >= 5: Status = "pending", wait for seller

---

**Ready to implement! All backend endpoints are live and documented.**
