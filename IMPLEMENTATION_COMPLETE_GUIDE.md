# Complete Document & Auto-Approval Implementation Guide

## 🎯 Overview

This guide covers the complete implementation of:
1. **Operating Manual Upload** - Seller uploads manual when creating equipment listing
2. **Payment Receipt Upload** - Seller uploads receipt after cash on delivery
3. **Auto-Approval** - Rentals with quantity < 5 automatically approved
4. **Document Management** - Rental agreements and operating manuals with visibility controls

---

## 📋 Implementation Summary

### ✅ What's Been Implemented

#### 1. Equipment Operating Manual Fields
- **Model**: `Equipment` model already has:
  - `operating_manual` (FileField) - PDF/document file
  - `manual_description` (TextField) - Description of manual contents

- **Serializers Updated**: 
  - `EquipmentDetailSerializer` - includes `operating_manual`, `manual_description`
  - `EquipmentCreateSerializer` - allows uploading manual during creation
  - `EquipmentUpdateSerializer` - allows updating manual

#### 2. Payment Receipt Fields
- **Model**: `RentalPayment` model already has:
  - `receipt_file` (FileField) - Receipt image/PDF
  - `receipt_number` (CharField) - Receipt/invoice number
  - `notes` (TextField) - Payment notes (e.g., "Cash collected by driver John")

- **Serializers Updated**:
  - `RentalPaymentSerializer` - includes receipt fields with URL generation

#### 3. Auto-Approval Logic
- **Implementation**: `RentalCreateSerializer.create()` method
- **Logic**: 
  ```python
  if quantity < 5:
      validated_data['status'] = 'approved'
      validated_data['approved_at'] = timezone.now()
  else:
      validated_data['status'] = 'pending'  # Requires seller approval
  ```

#### 4. Document Auto-Generation
- **Rental Agreement**: Auto-generated when rental is created
  - Format: Text file with rental terms
  - Visibility: Immediately visible to customer
  - Lock: Not locked (requires_payment=False)

- **Operating Manual**: Auto-attached if equipment has manual
  - Source: Equipment's operating_manual field
  - Visibility: Visible to customer
  - Lock: Locked until payment (requires_payment=True)

#### 5. New API Endpoints

**Upload Payment Receipt (Seller)**
```
POST /api/rentals/rentals/{id}/upload_payment_receipt/
```

**Get Rental Documents (Customer/Seller)**
```
GET /api/rentals/rentals/{id}/documents/
```

**Upload Rental Document (Seller/Customer)**
```
POST /api/rentals/rentals/{id}/upload_document/
```

---

## 🔄 Complete Workflow

### Seller Creates Equipment Listing

**Frontend Form Fields Required:**
```javascript
{
  name: string,
  description: string,
  category_id: number,
  daily_rate: number,
  total_units: number,
  
  // NEW FIELDS - Add to form
  operating_manual: File,  // PDF, DOC, DOCX (optional)
  manual_description: string  // Description of what's in manual
}
```

**Example React Form (Seller Dashboard)**
```tsx
import React, { useState } from 'react';

function CreateEquipmentForm() {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    category_id: '',
    daily_rate: '',
    total_units: '',
    manual_description: ''
  });
  const [operatingManual, setOperatingManual] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const data = new FormData();
    Object.keys(formData).forEach(key => {
      data.append(key, formData[key]);
    });
    
    // Add operating manual if selected
    if (operatingManual) {
      data.append('operating_manual', operatingManual);
    }
    
    const response = await fetch('/api/equipment/equipment/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`
      },
      body: data
    });
    
    const result = await response.json();
    console.log('Equipment created:', result);
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Basic fields */}
      <input 
        type="text" 
        placeholder="Equipment Name"
        value={formData.name}
        onChange={(e) => setFormData({...formData, name: e.target.value})}
      />
      
      {/* ... other basic fields ... */}
      
      {/* Operating Manual Section */}
      <div className="operating-manual-section">
        <h3>Operating Manual (Optional)</h3>
        <p>Upload a PDF manual that customers can access after payment</p>
        
        <input
          type="file"
          accept=".pdf,.doc,.docx"
          onChange={(e) => setOperatingManual(e.target.files[0])}
        />
        
        <textarea
          placeholder="Describe what's covered in the manual..."
          value={formData.manual_description}
          onChange={(e) => setFormData({...formData, manual_description: e.target.value})}
        />
      </div>
      
      <button type="submit">Create Equipment</button>
    </form>
  );
}
```

---

### Customer Books Equipment

**What Happens Automatically:**

1. **Rental Created** with auto-calculated pricing
2. **Status Determined**:
   - If `quantity < 5`: Status = `approved` ✅
   - If `quantity >= 5`: Status = `pending` ⏳ (needs seller approval)

3. **Documents Auto-Generated**:
   - ✅ Rental Agreement created (unlocked, visible immediately)
   - 🔒 Operating Manual attached (locked until payment)

**Example API Call (Customer App)**
```javascript
const bookEquipment = async (equipmentId, dates, quantity) => {
  const response = await fetch('/api/rentals/rentals/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${customerAccessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      equipment: equipmentId,
      start_date: dates.startDate,  // YYYY-MM-DD
      end_date: dates.endDate,
      quantity: quantity,
      delivery_address: '123 Main St',
      delivery_city: 'Gaborone',
      delivery_country: 'Botswana',
      customer_phone: '+267 71234567',
      customer_email: 'customer@example.com'
    })
  });
  
  const rental = await response.json();
  
  // Check if auto-approved
  if (rental.status === 'approved' && quantity < 5) {
    showMessage('Rental auto-approved! Proceed to payment.');
  } else {
    showMessage('Rental pending seller approval.');
  }
  
  return rental;
};
```

---

### Customer Views Documents

**Get Documents Endpoint**
```javascript
const getRentalDocuments = async (rentalId) => {
  const response = await fetch(`/api/rentals/rentals/${rentalId}/documents/`, {
    headers: {
      'Authorization': `Bearer ${customerAccessToken}`
    }
  });
  
  const data = await response.json();
  
  // Example response:
  // {
  //   "count": 2,
  //   "documents": [
  //     {
  //       "id": 1,
  //       "document_type": "rental_agreement",
  //       "document_type_display": "Rental Agreement",
  //       "title": "Rental Agreement - RNT123",
  //       "file_url": "http://.../rental_agreement_RNT123.txt",
  //       "is_locked": false,  // ✅ Unlocked
  //       "visible_to_customer": true,
  //       "requires_payment": false
  //     },
  //     {
  //       "id": 2,
  //       "document_type": "operating_manual",
  //       "document_type_display": "Operating Manual",
  //       "title": "Operating Manual - Excavator",
  //       "file_url": "http://.../manual.pdf",
  //       "is_locked": true,  // 🔒 Locked until payment
  //       "visible_to_customer": true,
  //       "requires_payment": true
  //     }
  //   ]
  // }
  
  return data;
};
```

**React Native Document List**
```tsx
import React, { useEffect, useState } from 'react';
import { View, Text, TouchableOpacity, Linking } from 'react-native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

function RentalDocuments({ rentalId }) {
  const [documents, setDocuments] = useState([]);

  useEffect(() => {
    fetchDocuments();
  }, [rentalId]);

  const fetchDocuments = async () => {
    const data = await getRentalDocuments(rentalId);
    setDocuments(data.documents);
  };

  const openDocument = (doc) => {
    if (doc.is_locked) {
      Alert.alert(
        'Document Locked',
        'This document will be available after payment is confirmed.',
        [{ text: 'OK' }]
      );
    } else {
      // Open document
      Linking.openURL(doc.file_url);
    }
  };

  return (
    <View>
      <Text style={styles.title}>Rental Documents</Text>
      
      {documents.map(doc => (
        <TouchableOpacity 
          key={doc.id}
          style={styles.docCard}
          onPress={() => openDocument(doc)}
          disabled={doc.is_locked}
        >
          <View style={styles.docIcon}>
            <Icon 
              name={doc.is_locked ? 'file-lock' : 'file-document'} 
              size={32} 
              color={doc.is_locked ? '#999' : '#007AFF'} 
            />
          </View>
          
          <View style={styles.docInfo}>
            <Text style={styles.docTitle}>{doc.title}</Text>
            <Text style={styles.docType}>{doc.document_type_display}</Text>
            
            {doc.is_locked && (
              <View style={styles.lockBadge}>
                <Icon name="lock" size={14} color="#FFF" />
                <Text style={styles.lockText}>Unlocks after payment</Text>
              </View>
            )}
          </View>
          
          <Icon 
            name={doc.is_locked ? 'lock' : 'chevron-right'} 
            size={24} 
            color="#999" 
          />
        </TouchableOpacity>
      ))}
    </View>
  );
}
```

---

### Seller Uploads Payment Receipt (Cash on Delivery)

**When**: After seller collects cash payment from customer

**Upload Receipt Endpoint**
```javascript
const uploadPaymentReceipt = async (rentalId, receiptData) => {
  const formData = new FormData();
  formData.append('receipt_file', receiptData.file);  // Image or PDF
  formData.append('receipt_number', receiptData.receiptNumber);
  formData.append('notes', receiptData.notes);
  
  const response = await fetch(
    `/api/rentals/rentals/${rentalId}/upload_payment_receipt/`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${sellerAccessToken}`
      },
      body: formData
    }
  );
  
  const result = await response.json();
  // {
  //   "message": "Payment receipt uploaded successfully",
  //   "payment": {
  //     "id": 1,
  //     "receipt_file_url": "http://.../receipt.jpg",
  //     "receipt_number": "RCT-001",
  //     "notes": "Cash collected by driver John",
  //     "payment_status": "completed"
  //   }
  // }
  
  return result;
};
```

**Seller Dashboard - Upload Receipt Form**
```tsx
import React, { useState } from 'react';

function UploadReceiptForm({ rental }) {
  const [receiptFile, setReceiptFile] = useState(null);
  const [receiptNumber, setReceiptNumber] = useState('');
  const [notes, setNotes] = useState('');

  const handleUpload = async () => {
    const result = await uploadPaymentReceipt(rental.id, {
      file: receiptFile,
      receiptNumber: receiptNumber,
      notes: notes
    });
    
    if (result.message) {
      alert('Receipt uploaded! Operating manual is now unlocked for customer.');
    }
  };

  return (
    <div className="upload-receipt-form">
      <h3>Upload Payment Receipt</h3>
      <p>Rental: {rental.rental_reference}</p>
      <p>Amount: ${rental.total_amount}</p>
      
      <div className="form-group">
        <label>Receipt File (Photo/PDF)</label>
        <input 
          type="file" 
          accept="image/*,.pdf"
          onChange={(e) => setReceiptFile(e.target.files[0])}
        />
      </div>
      
      <div className="form-group">
        <label>Receipt Number</label>
        <input 
          type="text"
          placeholder="RCT-001"
          value={receiptNumber}
          onChange={(e) => setReceiptNumber(e.target.value)}
        />
      </div>
      
      <div className="form-group">
        <label>Notes</label>
        <textarea
          placeholder="Cash collected by driver John at 2pm"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
        />
      </div>
      
      <button onClick={handleUpload} disabled={!receiptFile}>
        Upload Receipt & Confirm Payment
      </button>
    </div>
  );
}
```

---

### Operating Manual Unlocks After Payment

**What Happens:**
1. Seller uploads payment receipt
2. Payment status changes to `completed`
3. Operating manual automatically unlocks (is_locked = false)
4. Customer can now download the manual

**Customer sees:**
- Before payment: 🔒 Operating Manual (Locked)
- After payment: ✅ Operating Manual (Download)

---

## 📱 React Native Customer App Examples

### Rental Card with Document Status
```tsx
function RentalCard({ rental }) {
  const [documents, setDocuments] = useState([]);
  
  useEffect(() => {
    fetchDocuments();
  }, []);
  
  const fetchDocuments = async () => {
    const data = await getRentalDocuments(rental.id);
    setDocuments(data.documents);
  };
  
  const unlockedDocs = documents.filter(d => !d.is_locked).length;
  const totalDocs = documents.length;
  
  return (
    <View style={styles.card}>
      <Text style={styles.title}>{rental.equipment_name}</Text>
      <Text style={styles.ref}>Ref: {rental.rental_reference}</Text>
      
      <View style={styles.statusRow}>
        <StatusBadge status={rental.status} />
        
        {rental.status === 'approved' && (
          <Text style={styles.autoApproved}>✅ Auto-Approved</Text>
        )}
      </View>
      
      <View style={styles.docsRow}>
        <Icon name="file-document-multiple" size={16} />
        <Text>{unlockedDocs}/{totalDocs} documents available</Text>
      </View>
      
      <TouchableOpacity 
        style={styles.viewDocsButton}
        onPress={() => navigation.navigate('Documents', { rentalId: rental.id })}
      >
        <Text>View Documents</Text>
      </TouchableOpacity>
    </View>
  );
}
```

---

## 🧪 Testing the Implementation

### Test 1: Create Equipment with Operating Manual
```bash
# Using httpie or curl
http POST http://localhost:8000/api/equipment/equipment/ \
  Authorization:"Bearer ${SELLER_TOKEN}" \
  name="Excavator XL" \
  description="Heavy duty excavator" \
  category_id=1 \
  daily_rate=500 \
  total_units=3 \
  manual_description="Complete operating and safety manual" \
  operating_manual@/path/to/manual.pdf
```

### Test 2: Create Rental with Quantity < 5 (Auto-Approved)
```bash
http POST http://localhost:8000/api/rentals/rentals/ \
  Authorization:"Bearer ${CUSTOMER_TOKEN}" \
  equipment=1 \
  start_date="2025-11-01" \
  end_date="2025-11-05" \
  quantity=2 \
  delivery_address="123 Main St" \
  delivery_city="Gaborone" \
  delivery_country="Botswana" \
  customer_phone="+267 71234567" \
  customer_email="customer@example.com"

# Expected: status = "approved" (not "pending")
```

### Test 3: Get Documents (Should see locked manual)
```bash
http GET http://localhost:8000/api/rentals/rentals/1/documents/ \
  Authorization:"Bearer ${CUSTOMER_TOKEN}"

# Expected:
# - Rental Agreement: is_locked=false
# - Operating Manual: is_locked=true
```

### Test 4: Upload Payment Receipt (Seller)
```bash
http -f POST http://localhost:8000/api/rentals/rentals/1/upload_payment_receipt/ \
  Authorization:"Bearer ${SELLER_TOKEN}" \
  receipt_file@receipt.jpg \
  receipt_number="RCT-001" \
  notes="Cash collected by driver"
```

### Test 5: Verify Manual Unlocked
```bash
http GET http://localhost:8000/api/rentals/rentals/1/documents/ \
  Authorization:"Bearer ${CUSTOMER_TOKEN}"

# Expected:
# - Operating Manual: is_locked=false (now unlocked!)
```

---

## 🔍 Troubleshooting

### Issue: Operating Manual Field Not Showing in Form
**Solution**: Ensure serializers include the fields:
- Check `EquipmentCreateSerializer` has `operating_manual` in fields
- Check `EquipmentDetailSerializer` has `operating_manual` in fields

### Issue: Rental Not Auto-Approving
**Solution**: Verify quantity < 5 logic in `RentalCreateSerializer.create()`
```python
if quantity < 5:
    validated_data['status'] = 'approved'
```

### Issue: Operating Manual Not Unlocking After Payment
**Solution**: Check `RentalDocumentSerializer.get_is_locked()` method queries completed payments correctly

### Issue: Receipt Upload Endpoint Not Found
**Solution**: Verify URL is registered in `rentals/urls.py` and uses correct ViewSet action

---

## 📊 Database Verification

### Check if Equipment has Operating Manual
```sql
SELECT id, name, operating_manual, manual_description 
FROM equipment_equipment 
WHERE operating_manual IS NOT NULL;
```

### Check Rental Status (Auto-Approved)
```sql
SELECT rental_reference, quantity, status, approved_at 
FROM rentals_rental 
WHERE quantity < 5;
```

### Check Documents and Lock Status
```sql
SELECT 
  r.rental_reference,
  rd.document_type,
  rd.visible_to_customer,
  rd.requires_payment,
  CASE 
    WHEN rd.requires_payment = TRUE 
      AND NOT EXISTS (
        SELECT 1 FROM rentals_rentalpayment rp 
        WHERE rp.rental_id = r.id 
        AND rp.payment_status = 'completed'
      ) 
    THEN 'LOCKED' 
    ELSE 'UNLOCKED' 
  END as lock_status
FROM rentals_rental r
JOIN rentals_rentaldocument rd ON r.id = rd.rental_id;
```

---

## ✅ Implementation Checklist

- [x] Add `operating_manual` and `manual_description` to Equipment model
- [x] Add receipt fields to RentalPayment model
- [x] Add visibility fields to RentalDocument model
- [x] Update Equipment serializers with manual fields
- [x] Update RentalPayment serializer with receipt fields
- [x] Update RentalDocument serializer with lock logic
- [x] Implement auto-approval in RentalCreateSerializer (quantity < 5)
- [x] Implement auto-generation of rental agreement
- [x] Implement auto-attachment of operating manual
- [x] Create `upload_payment_receipt` endpoint
- [x] Create `documents` endpoint (get rental documents)
- [x] Create `upload_document` endpoint
- [x] Test equipment creation with manual
- [x] Test rental auto-approval
- [x] Test document visibility and locking
- [x] Test receipt upload and manual unlocking

---

## 🚀 Next Steps

1. **Frontend Forms**: Update seller dashboard to include operating manual upload field
2. **Mobile App**: Implement document viewing screen with lock/unlock indicators
3. **Receipt Upload UI**: Create seller interface for uploading payment receipts
4. **Push Notifications**: Notify customer when operating manual unlocks
5. **Analytics**: Track document downloads and engagement

---

## 📞 Support

For questions or issues with this implementation:
- Review DOCUMENT_MANAGEMENT_GUIDE.md for detailed document workflows
- Check API endpoint documentation in code comments
- Test endpoints using provided examples
- Verify database migrations are applied

**Implementation Date**: October 28, 2025
**Django Version**: 5.2.7
**Status**: ✅ Complete and Ready for Frontend Integration
