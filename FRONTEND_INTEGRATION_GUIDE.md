# Frontend Integration Guide - Rental Status Flow & Actions

## 🎯 Purpose
This guide provides clear instructions for frontend developers on:
1. All 15 rental statuses and what they mean
2. Required UI components for each status
3. API endpoints to call for status transitions
4. Required data/files for each action
5. User permissions (who can do what)

---

## 📊 Complete Rental Status Flow

### Visual Flow Diagram
```
Customer Creates Booking
         ↓
    [PENDING] ← (if quantity >= 5)
         ↓
    [APPROVED] ← (if quantity < 5, auto-approved)
         ↓
    💰 Customer Pays
         ↓
    [CONFIRMED]
         ↓
    [PREPARING] (Seller preparing equipment)
         ↓
    [READY_FOR_PICKUP]
         ↓
    [OUT_FOR_DELIVERY] (Driver en route)
         ↓
    [DELIVERED] ← 📸 REQUIRES: Delivery photo + signature
         ↓
    [IN_PROGRESS] (Rental active)
         ↓
    [RETURN_REQUESTED] (Customer wants to return)
         ↓
    [RETURNING] (Being picked up)
         ↓
    [COMPLETED] ← 📸 REQUIRES: Return photo
    
Side branches:
- [CANCELLED] (Cancelled before delivery)
- [OVERDUE] (Past return date)
- [DISPUTE] (Issues being resolved)
```

---

## 📋 Status-by-Status Frontend Requirements

### Status 1: PENDING (quantity >= 5)
**Meaning:** Waiting for seller approval

**Customer App:**
```javascript
// UI Elements
- Status Badge: "⏳ Pending Approval"
- Info Message: "Your rental request is pending seller approval"
- Action Button: "Cancel Request"

// API Call for Cancel
POST /api/rentals/rentals/{rental_id}/cancel/
Body: {
  "reason": "Changed my mind"
}
```

**Seller Dashboard:**
```javascript
// UI Elements
- Status Badge: "🔔 New Request - Needs Approval"
- Rental Details Card
- Action Buttons: "✅ Approve" | "❌ Reject"

// API Call for Approve
POST /api/rentals/rentals/{rental_id}/approve/
Body: {} // No body required

// API Call for Reject
POST /api/rentals/rentals/{rental_id}/reject/
Body: {
  "reason": "Equipment unavailable for those dates"
}
```

---

### Status 2: APPROVED (auto-approved if quantity < 5)
**Meaning:** Approved, waiting for payment

**Customer App:**
```javascript
// UI Elements
- Status Badge: "✅ Approved - Ready to Pay"
- Info Message: "Your rental has been approved!"
- Action Button: "💳 Make Payment"
- Pricing Summary
- Action Button: "Cancel Booking"

// Payment Flow
1. Show payment options (Credit Card, Cash on Delivery)
2. If Credit Card:
   - Process payment via payment gateway
   - Create payment record
   
POST /api/rentals/payments/
Body: {
  "rental": rental_id,
  "payment_type": "full",
  "amount": total_amount,
  "payment_method": "credit_card",
  "transaction_id": "txn_123456"
}

3. Status auto-changes to CONFIRMED after payment
```

**Seller Dashboard:**
```javascript
// UI Elements
- Status Badge: "✅ Approved - Awaiting Payment"
- Info Message: "Customer has been notified to make payment"
- No action buttons (waiting for customer)
```

---

### Status 3: CONFIRMED
**Meaning:** Payment received, ready to prepare equipment

**Customer App:**
```javascript
// UI Elements
- Status Badge: "✅ Payment Confirmed"
- Info Message: "Payment received. Equipment is being prepared."
- Timeline showing next steps
- View Receipt button
```

**Seller Dashboard:**
```javascript
// UI Elements
- Status Badge: "💰 Paid - Start Preparing"
- Action Button: "📦 Start Preparing Equipment"

// API Call
POST /api/rentals/rentals/{rental_id}/update_status/
Body: {
  "new_status": "preparing",
  "notes": "Starting equipment preparation",
  "is_visible_to_customer": true
}
```

---

### Status 4: PREPARING
**Meaning:** Seller is preparing/checking equipment

**Customer App:**
```javascript
// UI Elements
- Status Badge: "📦 Equipment Being Prepared"
- Info Message: "Your equipment is being prepared and checked"
- Estimated ready time
```

**Seller Dashboard:**
```javascript
// UI Elements
- Status Badge: "📦 Preparing Equipment"
- Checklist UI:
  ☐ Equipment cleaned
  ☐ Equipment tested
  ☐ Accessories packed
  ☐ Documentation ready
- Action Button: "✅ Mark Ready for Pickup"

// API Call when ready
POST /api/rentals/rentals/{rental_id}/update_status/
Body: {
  "new_status": "ready_for_pickup",
  "notes": "Equipment ready for pickup/delivery",
  "is_visible_to_customer": true
}
```

---

### Status 5: READY_FOR_PICKUP
**Meaning:** Equipment ready, waiting for delivery/pickup

**Customer App:**
```javascript
// UI Elements
- Status Badge: "✅ Ready - Awaiting Delivery"
- Info Message: "Your equipment is ready and will be delivered soon"
- Delivery address displayed
- Contact seller button
```

**Seller Dashboard:**
```javascript
// UI Elements
- Status Badge: "📍 Ready - Start Delivery"
- Delivery address displayed
- Action Button: "🚚 Start Delivery"

// API Call when driver starts
POST /api/rentals/rentals/{rental_id}/update_status/
Body: {
  "new_status": "out_for_delivery",
  "notes": "Driver John started delivery",
  "is_visible_to_customer": true
}
```

---

### Status 6: OUT_FOR_DELIVERY
**Meaning:** Driver is delivering equipment to customer

**Customer App:**
```javascript
// UI Elements
- Status Badge: "🚚 Out for Delivery"
- Info Message: "Your equipment is on the way!"
- Delivery tracking (if available)
- Driver contact info
- Estimated arrival time
```

**Seller Dashboard:**
```javascript
// UI Elements
- Status Badge: "🚚 Out for Delivery"
- Driver name/contact
- Action Button: "📸 Confirm Delivery" ← IMPORTANT!

// ⚠️ CRITICAL: This requires proof of delivery!
// API Call - WRONG WAY (current):
POST /api/rentals/rentals/{rental_id}/update_status/
Body: {
  "new_status": "delivered",
  "notes": "Delivered to customer"
}

// ✅ CORRECT WAY (should implement):
POST /api/rentals/rentals/{rental_id}/confirm_delivery/
FormData: {
  "delivery_photo": File,          // REQUIRED
  "customer_signature": string,    // Base64 or signature data
  "delivery_notes": string,
  "gps_latitude": float,
  "gps_longitude": float
}
```

**🚨 IMPORTANT Frontend Implementation:**
```javascript
// Delivery Confirmation Component
function DeliveryConfirmation({ rental }) {
  const [photo, setPhoto] = useState(null);
  const [signature, setSignature] = useState(null);
  const [notes, setNotes] = useState('');
  const [location, setLocation] = useState(null);
  
  // Get GPS location
  useEffect(() => {
    navigator.geolocation.getCurrentPosition((pos) => {
      setLocation({
        latitude: pos.coords.latitude,
        longitude: pos.coords.longitude
      });
    });
  }, []);
  
  const handleConfirmDelivery = async () => {
    const formData = new FormData();
    formData.append('delivery_photo', photo); // From camera
    formData.append('customer_signature', signature); // From signature pad
    formData.append('delivery_notes', notes);
    formData.append('gps_latitude', location.latitude);
    formData.append('gps_longitude', location.longitude);
    
    const response = await fetch(
      `/api/rentals/rentals/${rental.id}/confirm_delivery/`,
      {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      }
    );
    
    if (response.ok) {
      alert('Delivery confirmed!');
      // Refresh rental details
    }
  };
  
  return (
    <div>
      <h3>Confirm Delivery</h3>
      
      {/* Photo Capture */}
      <div>
        <label>Take Photo of Delivered Equipment</label>
        <input 
          type="file" 
          accept="image/*" 
          capture="environment"
          onChange={(e) => setPhoto(e.target.files[0])}
          required
        />
        {!photo && <p className="error">Photo required!</p>}
      </div>
      
      {/* Signature Pad (Optional but recommended) */}
      <div>
        <label>Customer Signature (Optional)</label>
        <SignaturePad 
          onEnd={(signature) => setSignature(signature)}
        />
      </div>
      
      {/* Notes */}
      <textarea
        placeholder="Delivery notes..."
        value={notes}
        onChange={(e) => setNotes(e.target.value)}
      />
      
      <button 
        onClick={handleConfirmDelivery}
        disabled={!photo}
      >
        Confirm Delivery
      </button>
    </div>
  );
}
```

---

### Status 7: DELIVERED
**Meaning:** Equipment delivered to customer

**Customer App:**
```javascript
// UI Elements
- Status Badge: "✅ Equipment Delivered"
- Info Message: "Equipment has been delivered. Enjoy your rental!"
- Action Button: "📄 View Documents" (rental agreement, operating manual)
- Operating manual now UNLOCKED 🔓
- Action Button: "⚠️ Report Issue"
- Rental countdown timer
```

**Seller Dashboard:**
```javascript
// UI Elements
- Status Badge: "✅ Delivered"
- Delivery timestamp
- View delivery photo
- Upload Payment Receipt (if cash on delivery)

// Upload Receipt (for cash on delivery)
POST /api/rentals/rentals/{rental_id}/upload_payment_receipt/
FormData: {
  "receipt_file": File,
  "receipt_number": "RCT-001",
  "notes": "Cash collected by driver John"
}
```

---

### Status 8: IN_PROGRESS
**Meaning:** Rental period is active

**Customer App:**
```javascript
// UI Elements
- Status Badge: "🔄 Rental Active"
- Days remaining countdown
- Equipment details
- Operating manual available
- Action Button: "🔙 Request Return"

// Request Return
POST /api/rentals/rentals/{rental_id}/update_status/
Body: {
  "new_status": "return_requested",
  "notes": "Ready to return equipment",
  "is_visible_to_customer": true
}
```

**Seller Dashboard:**
```javascript
// UI Elements
- Status Badge: "🔄 Active Rental"
- Days remaining
- Customer contact info
- No actions required (waiting for return request)
```

---

### Status 9: RETURN_REQUESTED
**Meaning:** Customer wants to return equipment

**Customer App:**
```javascript
// UI Elements
- Status Badge: "🔙 Return Requested"
- Info Message: "Your return request has been received"
- Pickup address/instructions
- Wait for seller confirmation
```

**Seller Dashboard:**
```javascript
// UI Elements
- Status Badge: "🔔 Return Requested"
- Customer location
- Action Button: "🚚 Start Return Pickup"

// Start return process
POST /api/rentals/rentals/{rental_id}/update_status/
Body: {
  "new_status": "returning",
  "notes": "Driver dispatched for pickup",
  "is_visible_to_customer": true
}
```

---

### Status 10: RETURNING
**Meaning:** Equipment being picked up from customer

**Customer App:**
```javascript
// UI Elements
- Status Badge: "🚚 Equipment Being Picked Up"
- Driver contact info
- Estimated pickup time
```

**Seller Dashboard:**
```javascript
// UI Elements
- Status Badge: "🚚 Pickup in Progress"
- Action Button: "✅ Confirm Return Received"

// ⚠️ This should also require photo proof!
// Current way:
POST /api/rentals/rentals/{rental_id}/update_status/
Body: {
  "new_status": "completed",
  "notes": "Equipment returned in good condition",
  "is_visible_to_customer": true
}

// Better way (implement later):
POST /api/rentals/rentals/{rental_id}/confirm_return/
FormData: {
  "return_photo": File,
  "condition_notes": string,
  "damage_found": boolean,
  "damage_photos": File[]
}
```

---

### Status 11: COMPLETED ⭐
**Meaning:** Rental successfully completed

**🎯 THIS IS WHERE SALE RECORD SHOULD BE CREATED!**

**Customer App:**
```javascript
// UI Elements
- Status Badge: "✅ Completed"
- Info Message: "Thank you for renting with us!"
- Action Button: "⭐ Write Review"
- View invoice
- Download receipt
- Rental summary

// Submit Review
POST /api/rentals/rentals/{rental_id}/submit_review/
Body: {
  "equipment_rating": 5,
  "service_rating": 5,
  "delivery_rating": 4,
  "review_text": "Great experience!",
  "would_recommend": true
}
```

**Seller Dashboard:**
```javascript
// UI Elements
- Status Badge: "✅ Completed"
- Rental summary
- Revenue earned
- View review (if submitted)
- Download invoice

// 🎯 BACKEND AUTO-CREATES SALE RECORD
// No manual action needed - signal creates RentalSale automatically
// See sales in analytics dashboard
```

---

### Status 12: CANCELLED
**Meaning:** Rental cancelled before delivery

**Customer App:**
```javascript
// UI Elements
- Status Badge: "❌ Cancelled"
- Cancellation reason
- Refund info (if applicable)
```

**Seller Dashboard:**
```javascript
// UI Elements
- Status Badge: "❌ Cancelled"
- Cancellation reason
- Who cancelled (customer/seller)
```

---

### Status 13: OVERDUE
**Meaning:** Past return date, not returned

**Customer App:**
```javascript
// UI Elements
- Status Badge: "⚠️ OVERDUE"
- Alert: "Please return equipment immediately!"
- Late fees accruing
- Action Button: "Request Return Pickup NOW"
- Contact seller button
```

**Seller Dashboard:**
```javascript
// UI Elements
- Status Badge: "⚠️ OVERDUE"
- Days overdue
- Late fees calculation
- Action Button: "📞 Contact Customer"
- Action Button: "⚠️ File Dispute"
```

---

### Status 14: DISPUTE
**Meaning:** Issues being resolved (damage, loss, payment)

**Customer App:**
```javascript
// UI Elements
- Status Badge: "⚠️ Under Review"
- Dispute details
- Support ticket link
- Upload evidence button
```

**Seller Dashboard:**
```javascript
// UI Elements
- Status Badge: "⚠️ Dispute"
- Dispute reason
- Evidence uploads
- Support ticket link
- Action Buttons: "Resolve" | "Escalate"
```

---

## 📱 Mobile App Components Required

### 1. Camera Component
```javascript
// For delivery/return photo capture
import { Camera } from 'react-native-camera';

<Camera
  ref={cameraRef}
  type={Camera.Constants.Type.back}
  onPictureTaken={(photo) => setDeliveryPhoto(photo)}
/>
```

### 2. Signature Pad Component
```javascript
// For customer signatures
import SignatureCapture from 'react-native-signature-capture';

<SignatureCapture
  onSaveEvent={(result) => {
    setSignature(result.encoded); // Base64
  }}
/>
```

### 3. GPS Location Component
```javascript
// For delivery location tracking
import Geolocation from '@react-native-community/geolocation';

Geolocation.getCurrentPosition(
  (position) => {
    setLocation({
      latitude: position.coords.latitude,
      longitude: position.coords.longitude
    });
  }
);
```

### 4. Status Badge Component
```javascript
function StatusBadge({ status }) {
  const badges = {
    'pending': { icon: '⏳', color: '#FFA500', text: 'Pending' },
    'approved': { icon: '✅', color: '#4CAF50', text: 'Approved' },
    'confirmed': { icon: '💰', color: '#2196F3', text: 'Confirmed' },
    'preparing': { icon: '📦', color: '#9C27B0', text: 'Preparing' },
    'ready_for_pickup': { icon: '✅', color: '#4CAF50', text: 'Ready' },
    'out_for_delivery': { icon: '🚚', color: '#FF9800', text: 'Delivering' },
    'delivered': { icon: '✅', color: '#4CAF50', text: 'Delivered' },
    'in_progress': { icon: '🔄', color: '#2196F3', text: 'Active' },
    'return_requested': { icon: '🔙', color: '#FF9800', text: 'Return Requested' },
    'returning': { icon: '🚚', color: '#FF9800', text: 'Returning' },
    'completed': { icon: '⭐', color: '#4CAF50', text: 'Completed' },
    'cancelled': { icon: '❌', color: '#F44336', text: 'Cancelled' },
    'overdue': { icon: '⚠️', color: '#F44336', text: 'OVERDUE' },
    'dispute': { icon: '⚠️', color: '#FF5722', text: 'Dispute' },
  };
  
  const badge = badges[status] || badges.pending;
  
  return (
    <View style={[styles.badge, { backgroundColor: badge.color }]}>
      <Text>{badge.icon} {badge.text}</Text>
    </View>
  );
}
```

---

## 🔒 Permission Matrix

| Status | Customer Can | Seller Can |
|--------|-------------|-----------|
| pending | Cancel | Approve/Reject |
| approved | Pay, Cancel | View |
| confirmed | View | Start Preparing |
| preparing | View | Mark Ready |
| ready_for_pickup | View | Start Delivery |
| out_for_delivery | View | Confirm Delivery + Photo |
| delivered | View Docs, Report Issue | Upload Receipt |
| in_progress | Request Return | View |
| return_requested | View | Start Return Pickup |
| returning | View | Confirm Return + Photo |
| completed | Write Review | View |
| cancelled | View | View |
| overdue | Request Pickup | Contact, Dispute |
| dispute | Upload Evidence | Upload Evidence, Resolve |

---

## 🚨 Critical Implementation Notes

### 1. Photo Upload REQUIRED for:
- ✅ Delivery confirmation (status: out_for_delivery → delivered)
- ✅ Return confirmation (status: returning → completed)
- ❌ Currently NOT enforced - needs implementation!

### 2. Operating Manual Unlock Logic:
```javascript
// Manual is locked until payment completed
const isManualLocked = (rental) => {
  const hasCompletedPayment = rental.payments.some(
    p => p.payment_status === 'completed'
  );
  return !hasCompletedPayment;
};
```

### 3. Auto-Approval Logic:
```javascript
// Frontend should show immediate approval for quantity < 5
if (rental.quantity < 5) {
  // Show: "✅ Auto-Approved! Proceed to payment"
} else {
  // Show: "⏳ Pending seller approval"
}
```

### 4. Sale Record Creation:
```javascript
// Backend auto-creates sale when status → 'completed'
// Frontend should refresh analytics after completion
// No manual action needed from frontend
```

---

## 📋 Frontend TODO Checklist

### Immediate (Critical):
- [ ] Add camera component for delivery photos
- [ ] Add signature pad component
- [ ] Implement delivery confirmation screen
- [ ] Add photo upload to `confirm_delivery` call
- [ ] Show operating manual lock/unlock status
- [ ] Add status badges to all rental cards
- [ ] Show correct action buttons per status

### Important:
- [ ] Add return confirmation with photo
- [ ] GPS location capture on delivery
- [ ] Status timeline/progress indicator
- [ ] Upload payment receipt form
- [ ] Document viewing screen with lock indicators
- [ ] Review submission form

### Nice to Have:
- [ ] Real-time status updates (websockets)
- [ ] Push notifications on status changes
- [ ] Delivery tracking map
- [ ] In-app chat with seller
- [ ] Photo gallery for rental history

---

## 🎯 Summary

**Key Problems Identified:**
1. ❌ Delivery confirmation has NO photo requirement
2. ❌ No clear status flow guidance for frontend
3. ❌ Missing required components (camera, signature)
4. ❌ No sale tracking when rental completes

**Frontend Must Implement:**
1. ✅ Photo capture on delivery
2. ✅ Signature pad (optional but recommended)
3. ✅ Status-specific action buttons
4. ✅ Operating manual lock/unlock UI
5. ✅ Receipt upload for sellers

**Backend Must Implement:**
1. ✅ `confirm_delivery` endpoint requiring photo
2. ✅ `RentalSale` model + auto-creation
3. ✅ Status validation enforcement
4. ✅ Sales analytics endpoints

---

Would you like me to create React Native screen templates for the critical flows (delivery confirmation, document viewing, etc.)?
