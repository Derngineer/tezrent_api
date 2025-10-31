# Frontend Quick Reference - Rental Status Actions

## 🎯 One-Page Status → Action Mapping

| Status | Display | Customer Action | Seller Action | Required Data |
|--------|---------|----------------|---------------|---------------|
| **pending** | ⏳ Pending Approval | Cancel Request | Approve/Reject | None |
| **approved** | ✅ Approved - Pay Now | Make Payment | Wait | Payment details |
| **confirmed** | 💰 Payment Confirmed | View Details | Start Preparing | None |
| **preparing** | 📦 Being Prepared | Wait | Mark Ready | None |
| **ready_for_pickup** | ✅ Ready | Wait | Start Delivery | None |
| **out_for_delivery** | 🚚 On The Way | Wait | **Confirm Delivery** | **📸 Photo + Signature** |
| **delivered** | ✅ Delivered | View Docs | Upload Receipt | Receipt file |
| **in_progress** | 🔄 Active Rental | Request Return | Wait | None |
| **return_requested** | 🔙 Return Pending | Wait | Start Pickup | None |
| **returning** | 🚚 Returning | Wait | **Confirm Return** | **📸 Photo** |
| **completed** | ⭐ Completed | Write Review | View Analytics | None |
| **cancelled** | ❌ Cancelled | View Reason | View Reason | None |
| **overdue** | ⚠️ OVERDUE | Request Pickup | Contact/Dispute | None |
| **dispute** | ⚠️ Under Review | Upload Evidence | Resolve | Evidence files |

---

## 📞 Critical API Endpoints

### Customer Endpoints
```javascript
// Book Equipment
POST /api/rentals/rentals/
Body: { equipment, start_date, end_date, quantity, delivery_address, ... }

// Make Payment
POST /api/rentals/payments/
Body: { rental, payment_type, amount, payment_method, transaction_id }

// Cancel Rental
POST /api/rentals/rentals/{id}/cancel/
Body: { reason }

// Request Return
POST /api/rentals/rentals/{id}/update_status/
Body: { new_status: "return_requested", notes }

// Submit Review
POST /api/rentals/rentals/{id}/submit_review/
Body: { equipment_rating, service_rating, review_text, would_recommend }

// Get Rental Documents
GET /api/rentals/rentals/{id}/documents/
```

### Seller Endpoints
```javascript
// Approve Rental
POST /api/rentals/rentals/{id}/approve/

// Reject Rental
POST /api/rentals/rentals/{id}/reject/
Body: { reason }

// Update Status (most transitions)
POST /api/rentals/rentals/{id}/update_status/
Body: { new_status, notes, is_visible_to_customer }

// 🚨 CRITICAL: Confirm Delivery (with photo)
POST /api/rentals/rentals/{id}/confirm_delivery/
FormData: {
  delivery_photo: File,          // REQUIRED
  customer_signature: string,    // Optional
  delivery_notes: string,
  gps_latitude: float,
  gps_longitude: float
}

// Upload Payment Receipt
POST /api/rentals/rentals/{id}/upload_payment_receipt/
FormData: {
  receipt_file: File,
  receipt_number: string,
  notes: string
}

// Get Dashboard Data
GET /api/rentals/rentals/seller_dashboard/
```

---

## 🔒 Document Lock Status

### Operating Manual Lock Logic
```javascript
// Manual is LOCKED until payment completed
const isManualLocked = (document) => {
  if (!document.requires_payment) {
    return false; // Rental agreements always unlocked
  }
  
  // Check if rental has completed payment
  const hasPayment = rental.payments.some(
    p => p.payment_status === 'completed'
  );
  
  return !hasPayment; // Locked if no payment
};

// UI Display
{isManualLocked(doc) ? (
  <Badge color="gray">🔒 Unlocks after payment</Badge>
) : (
  <Button onClick={() => downloadDocument(doc.file_url)}>
    📄 Download Manual
  </Button>
)}
```

---

## 🎨 Status Colors

```javascript
const statusColors = {
  pending: '#FFA500',      // Orange
  approved: '#4CAF50',     // Green
  confirmed: '#2196F3',    // Blue
  preparing: '#9C27B0',    // Purple
  ready_for_pickup: '#4CAF50',
  out_for_delivery: '#FF9800',
  delivered: '#4CAF50',
  in_progress: '#2196F3',
  return_requested: '#FF9800',
  returning: '#FF9800',
  completed: '#4CAF50',
  cancelled: '#F44336',    // Red
  overdue: '#F44336',      // Red
  dispute: '#FF5722',      // Deep Orange
};
```

---

## 📸 Photo Upload Component Template

```jsx
import React, { useState } from 'react';
import { View, Button, Image } from 'react-native';
import { launchCamera } from 'react-native-image-picker';

function DeliveryPhotoCapture({ onPhotoTaken }) {
  const [photo, setPhoto] = useState(null);
  
  const takePhoto = () => {
    launchCamera({
      mediaType: 'photo',
      quality: 0.8,
      maxWidth: 1024,
      maxHeight: 1024,
    }, (response) => {
      if (response.assets?.[0]) {
        const photoData = {
          uri: response.assets[0].uri,
          type: response.assets[0].type,
          name: response.assets[0].fileName,
        };
        setPhoto(photoData);
        onPhotoTaken(photoData);
      }
    });
  };
  
  return (
    <View>
      <Button title="📸 Take Delivery Photo" onPress={takePhoto} />
      {photo && (
        <Image 
          source={{ uri: photo.uri }} 
          style={{ width: 200, height: 200 }}
        />
      )}
    </View>
  );
}
```

---

## 🖊️ Signature Pad Template

```jsx
import React, { useRef } from 'react';
import SignatureCapture from 'react-native-signature-capture';

function CustomerSignature({ onSignatureCapture }) {
  const signatureRef = useRef(null);
  
  const saveSignature = () => {
    signatureRef.current.saveImage();
  };
  
  const resetSignature = () => {
    signatureRef.current.resetImage();
  };
  
  return (
    <View>
      <Text>Customer Signature</Text>
      <SignatureCapture
        ref={signatureRef}
        style={{ height: 200, backgroundColor: '#F0F0F0' }}
        onSaveEvent={(result) => {
          onSignatureCapture(result.encoded); // Base64
        }}
      />
      <Button title="Clear" onPress={resetSignature} />
      <Button title="Save Signature" onPress={saveSignature} />
    </View>
  );
}
```

---

## 🚨 Critical Implementation Rules

### 1. NEVER skip status transitions
```javascript
// ❌ WRONG - Can't jump from confirmed to delivered
changeStatus('confirmed' → 'delivered')

// ✅ CORRECT - Follow proper flow
changeStatus('confirmed' → 'preparing')
changeStatus('preparing' → 'ready_for_pickup')
changeStatus('ready_for_pickup' → 'out_for_delivery')
changeStatus('out_for_delivery' → 'delivered')  // With photo!
```

### 2. ALWAYS require photo for delivery
```javascript
// ❌ WRONG - No photo
fetch(`/api/rentals/rentals/${id}/update_status/`, {
  body: JSON.stringify({ new_status: 'delivered' })
})

// ✅ CORRECT - With photo
const formData = new FormData();
formData.append('delivery_photo', photoFile);
fetch(`/api/rentals/rentals/${id}/confirm_delivery/`, {
  body: formData
})
```

### 3. ALWAYS check permissions
```javascript
const canPerformAction = (user, rental, action) => {
  // Customer actions
  if (user.userType === 'customer') {
    if (action === 'cancel' && ['pending', 'approved'].includes(rental.status)) {
      return true;
    }
    if (action === 'pay' && rental.status === 'approved') {
      return true;
    }
    if (action === 'request_return' && rental.status === 'in_progress') {
      return true;
    }
  }
  
  // Seller actions
  if (user.userType === 'seller' && rental.seller_id === user.company_id) {
    if (action === 'approve' && rental.status === 'pending') {
      return true;
    }
    if (action === 'start_preparing' && rental.status === 'confirmed') {
      return true;
    }
    // ... etc
  }
  
  return false;
};
```

### 4. ALWAYS show loading states
```javascript
const [isUpdating, setIsUpdating] = useState(false);

const handleStatusChange = async () => {
  setIsUpdating(true);
  try {
    await updateRentalStatus();
    // Success
  } catch (error) {
    // Handle error
  } finally {
    setIsUpdating(false);
  }
};
```

---

## 📋 Pre-Launch Checklist

### Must Have:
- [ ] Status badge component with correct colors
- [ ] Photo capture for delivery confirmation
- [ ] Operating manual lock/unlock UI
- [ ] Payment flow (credit card + cash on delivery)
- [ ] Receipt upload form for sellers
- [ ] Review submission form
- [ ] Error handling for all API calls
- [ ] Loading states for all actions

### Should Have:
- [ ] Signature pad for delivery
- [ ] GPS location capture
- [ ] Return photo capture
- [ ] Status timeline/progress bar
- [ ] Document download functionality
- [ ] Push notifications on status changes

### Nice to Have:
- [ ] Real-time status updates
- [ ] Delivery tracking map
- [ ] In-app chat
- [ ] Photo gallery
- [ ] Offline support

---

## 🎯 Common Mistakes to Avoid

1. ❌ Calling wrong endpoint for delivery
2. ❌ Not requiring photo upload
3. ❌ Allowing status skipping
4. ❌ Not checking user permissions
5. ❌ Not showing loading states
6. ❌ Not handling errors properly
7. ❌ Not refreshing data after updates
8. ❌ Not showing document lock status

---

## 📱 Sample Screens Needed

### Customer App (8 screens):
1. Browse/Search Equipment
2. Equipment Details
3. Booking Form
4. Payment Screen
5. My Rentals List
6. Rental Details (with status-specific actions)
7. Documents Viewer (with lock indicators)
8. Review Submission

### Seller Dashboard (10 screens):
1. Dashboard Home (stats + pending approvals)
2. Equipment Listings
3. Add/Edit Equipment (with manual upload)
4. Rental Orders List
5. Rental Details (with status-specific actions)
6. Delivery Confirmation (photo + signature)
7. Receipt Upload
8. Sales Analytics
9. Payout History
10. Customer Reviews

---

**Full details:** See `FRONTEND_INTEGRATION_GUIDE.md`
**Architecture:** See `ARCHITECTURE_IMPROVEMENTS.md`
**Document system:** See `DOCUMENT_MANAGEMENT_GUIDE.md`
