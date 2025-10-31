# Complete Rentals API Guide - React Native (Customer) & React (Seller)

## 📱 Overview

This guide covers the complete rental flow for:
- **React Native App** - Customer mobile app (renting equipment)
- **React Web Dashboard** - Seller dashboard (managing rental requests)

## 🔄 Rental Workflow

```
Customer (React Native)          Seller (React Web)
┌──────────────────────┐         ┌──────────────────────┐
│ 1. Browse Equipment  │         │                      │
│ 2. Request Rental    │────────>│ 3. Approve/Reject    │
│                      │         │ 4. Prepare Equipment │
│ 5. Make Payment      │<────────│                      │
│                      │         │ 6. Deliver Equipment │
│ 7. Use Equipment     │         │                      │
│ 8. Request Return    │────────>│ 9. Pickup Equipment  │
│ 10. Leave Review     │         │ 10. Complete Rental  │
└──────────────────────┘         └──────────────────────┘
```

---

## 📋 Rental Status Flow

```
pending → approved → payment_pending → confirmed → preparing 
  → ready_for_pickup → out_for_delivery → delivered 
  → in_progress → return_requested → returning → completed
```

**Status Descriptions:**
- `pending` - Customer submitted, waiting for seller
- `approved` - Seller approved, waiting for payment
- `payment_pending` - Payment in progress
- `confirmed` - Paid and confirmed
- `preparing` - Seller preparing equipment
- `ready_for_pickup` - Equipment ready
- `out_for_delivery` - Being delivered
- `delivered` - Customer has equipment
- `in_progress` - Active rental period
- `return_requested` - Customer wants to return
- `returning` - Being picked up/returned
- `completed` - Successfully completed
- `cancelled` - Cancelled before delivery
- `overdue` - Past return date
- `dispute` - Issues being resolved

---

## 🚀 Complete API Reference

### Base URL
```
http://127.0.0.1:8000/api/rentals/
```

### Authentication
All rental endpoints require authentication:
```javascript
headers: {
  'Authorization': `Bearer ${accessToken}`
}
```

---

## 📱 CUSTOMER FLOW (React Native)

### 1. Create Rental Request

**Endpoint:** `POST /api/rentals/rentals/`

**Customer creates a rental request when they want to rent equipment.**

#### Request Example (React Native)

```javascript
const createRentalRequest = async (equipmentId, rentalDetails) => {
  const formData = new FormData();
  
  // Required fields
  formData.append('equipment', equipmentId);
  formData.append('start_date', rentalDetails.startDate);  // YYYY-MM-DD
  formData.append('end_date', rentalDetails.endDate);      // YYYY-MM-DD
  formData.append('quantity', rentalDetails.quantity || 1);
  
  // Contact information
  formData.append('customer_phone', rentalDetails.phone);
  formData.append('customer_email', rentalDetails.email);
  
  // Delivery information
  formData.append('delivery_address', rentalDetails.address);
  formData.append('delivery_city', rentalDetails.city);
  formData.append('delivery_country', rentalDetails.country);
  formData.append('pickup_required', rentalDetails.needsDelivery);
  
  // Optional
  formData.append('customer_notes', rentalDetails.notes || '');
  formData.append('delivery_instructions', rentalDetails.deliveryNotes || '');
  
  try {
    const response = await fetch('http://YOUR_API/api/rentals/rentals/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
      },
      body: formData,
    });
    
    if (response.ok) {
      const rental = await response.json();
      console.log('Rental created:', rental);
      // Navigate to rental details or confirmation screen
      navigation.navigate('RentalSuccess', { rentalId: rental.id });
    } else {
      const error = await response.json();
      console.error('Error:', error);
    }
  } catch (error) {
    console.error('Network error:', error);
  }
};
```

#### Response (201 Created)

```json
{
  "id": 1,
  "rental_reference": "RNTABCD1234",
  "equipment": {
    "id": 5,
    "name": "CAT 320 Excavator",
    "daily_rate": "500.00"
  },
  "customer_details": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890"
  },
  "seller_details": {
    "id": 1,
    "company_name": "ABC Equipment Rentals",
    "phone": "+0987654321"
  },
  "start_date": "2025-11-01",
  "end_date": "2025-11-07",
  "quantity": 1,
  "daily_rate": "500.00",
  "total_days": 7,
  "subtotal": "3500.00",
  "delivery_fee": "100.00",
  "insurance_fee": "50.00",
  "security_deposit": "1000.00",
  "total_amount": "3650.00",
  "status": "pending",
  "status_display": "Pending Approval",
  "created_at": "2025-10-27T10:30:00Z",
  "available_actions": [
    {"action": "cancel", "label": "Cancel Request"}
  ]
}
```

---

### 2. View My Rentals (Customer)

**Endpoint:** `GET /api/rentals/rentals/`

**Customer sees only their own rentals. Automatically filtered by backend.**

#### Request Example

```javascript
const fetchMyRentals = async (status = null) => {
  let url = 'http://YOUR_API/api/rentals/rentals/';
  
  // Optional: filter by status
  if (status) {
    url += `?status=${status}`;
  }
  
  try {
    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
      },
    });
    
    const rentals = await response.json();
    return rentals;
  } catch (error) {
    console.error('Error:', error);
  }
};
```

#### Response

```json
[
  {
    "id": 1,
    "rental_reference": "RNTABCD1234",
    "equipment_name": "CAT 320 Excavator",
    "equipment_image": "http://api.com/media/equipment/cat320.jpg",
    "seller_name": "ABC Equipment Rentals",
    "start_date": "2025-11-01",
    "end_date": "2025-11-07",
    "total_amount": "3650.00",
    "status": "pending",
    "status_display": "Pending Approval",
    "is_overdue": false,
    "days_remaining": 0,
    "rental_duration_text": "1 week",
    "created_at": "2025-10-27T10:30:00Z",
    "mobile_display_data": {
      "id": 1,
      "reference": "RNTABCD1234",
      "equipment": "CAT 320 Excavator",
      "image": "http://api.com/media/equipment/cat320.jpg",
      "status": "pending",
      "status_text": "Pending Approval",
      "start_date": "2025-11-01",
      "end_date": "2025-11-07",
      "duration": "1 week",
      "total_amount": "3650.00",
      "is_overdue": false,
      "days_remaining": 0,
      "status_color": "#FFA500"
    }
  }
]
```

---

### 3. View Rental Details (Customer)

**Endpoint:** `GET /api/rentals/rentals/{id}/`

```javascript
const fetchRentalDetails = async (rentalId) => {
  const response = await fetch(
    `http://YOUR_API/api/rentals/rentals/${rentalId}/`,
    {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
      },
    }
  );
  
  return await response.json();
};
```

#### Response (Full Details)

```json
{
  "id": 1,
  "rental_reference": "RNTABCD1234",
  "equipment": {
    "id": 5,
    "name": "CAT 320 Excavator",
    "category": "Excavators",
    "images": [...]
  },
  "customer_details": {...},
  "seller_details": {...},
  "start_date": "2025-11-01",
  "end_date": "2025-11-07",
  "total_amount": "3650.00",
  "status": "approved",
  "status_display": "Approved",
  "status_updates": [
    {
      "id": 1,
      "old_status": "pending",
      "new_status": "approved",
      "updated_by_name": "Seller Admin",
      "notes": "Rental approved. Please proceed with payment.",
      "created_at": "2025-10-27T11:00:00Z"
    }
  ],
  "payments": [],
  "images": [],
  "documents": [],
  "available_actions": [
    {"action": "pay", "label": "Make Payment"}
  ]
}
```

---

### 4. Make Payment (Customer)

**Endpoint:** `POST /api/rentals/rentals/{id}/make_payment/`

```javascript
const makePayment = async (rentalId, paymentDetails) => {
  const response = await fetch(
    `http://YOUR_API/api/rentals/rentals/${rentalId}/make_payment/`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        payment_method: 'card',  // card, mobile_money, bank_transfer
        transaction_id: paymentDetails.transactionId,
        amount: paymentDetails.amount
      }),
    }
  );
  
  return await response.json();
};
```

---

### 5. Cancel Rental (Customer)

**Endpoint:** `POST /api/rentals/rentals/{id}/cancel/`

**Only available when status is `pending` or `approved`**

```javascript
const cancelRental = async (rentalId, reason) => {
  const response = await fetch(
    `http://YOUR_API/api/rentals/rentals/${rentalId}/cancel/`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        cancellation_reason: reason
      }),
    }
  );
  
  return await response.json();
};
```

---

### 6. Request Return (Customer)

**Endpoint:** `POST /api/rentals/rentals/{id}/update_status/`

**When customer wants to return equipment early**

```javascript
const requestReturn = async (rentalId) => {
  const response = await fetch(
    `http://YOUR_API/api/rentals/rentals/${rentalId}/update_status/`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        new_status: 'return_requested',
        notes: 'Customer requesting equipment pickup'
      }),
    }
  );
  
  return await response.json();
};
```

---

### 7. Leave Review (Customer)

**Endpoint:** `POST /api/rentals/reviews/`

**After rental is completed**

```javascript
const leaveReview = async (rentalId, reviewData) => {
  const response = await fetch(
    'http://YOUR_API/api/rentals/reviews/',
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        rental: rentalId,
        equipment_rating: reviewData.equipmentRating,  // 1-5
        service_rating: reviewData.serviceRating,      // 1-5
        delivery_rating: reviewData.deliveryRating,    // 1-5
        review_text: reviewData.reviewText,
        would_recommend: reviewData.wouldRecommend
      }),
    }
  );
  
  return await response.json();
};
```

---

## 💼 SELLER FLOW (React Web Dashboard)

### 1. View All Rental Requests

**Endpoint:** `GET /api/rentals/rentals/`

**Seller sees only rentals for their equipment. Automatically filtered by backend.**

#### Request Example (React)

```javascript
const fetchRentalOrders = async (status = null) => {
  let url = '/api/rentals/rentals/';
  
  // Filter by status
  if (status) {
    url += `?status=${status}`;
  }
  
  // Sort by newest first
  url += `${status ? '&' : '?'}ordering=-created_at`;
  
  try {
    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
      },
    });
    
    const rentals = await response.json();
    return rentals;
  } catch (error) {
    console.error('Error:', error);
  }
};

// Usage
const pendingRentals = await fetchRentalOrders('pending');
const activeRentals = await fetchRentalOrders('in_progress');
```

---

### 2. Approve/Reject Rental Request

**Endpoint:** `POST /api/rentals/rentals/{id}/update_status/`

#### Approve Rental

```javascript
const approveRental = async (rentalId, notes) => {
  const response = await fetch(
    `/api/rentals/rentals/${rentalId}/update_status/`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        new_status: 'approved',
        notes: notes || 'Rental request approved. Please proceed with payment.'
      }),
    }
  );
  
  if (response.ok) {
    const data = await response.json();
    console.log('Rental approved:', data);
    // Send notification to customer
  }
  
  return await response.json();
};
```

#### Reject Rental

```javascript
const rejectRental = async (rentalId, reason) => {
  const response = await fetch(
    `/api/rentals/rentals/${rentalId}/update_status/`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        new_status: 'cancelled',
        notes: `Rental rejected. Reason: ${reason}`
      }),
    }
  );
  
  return await response.json();
};
```

---

### 3. Update Rental Status (Seller)

**Different status updates throughout the rental lifecycle**

```javascript
// Mark equipment as preparing
const markPreparing = async (rentalId) => {
  return updateRentalStatus(rentalId, 'preparing', 'Started preparing equipment');
};

// Mark ready for pickup
const markReady = async (rentalId) => {
  return updateRentalStatus(rentalId, 'ready_for_pickup', 'Equipment ready for pickup');
};

// Mark out for delivery
const markDelivering = async (rentalId) => {
  return updateRentalStatus(rentalId, 'out_for_delivery', 'Equipment is being delivered');
};

// Confirm delivery
const confirmDelivery = async (rentalId) => {
  return updateRentalStatus(rentalId, 'delivered', 'Equipment delivered to customer');
};

// Complete rental
const completeRental = async (rentalId) => {
  return updateRentalStatus(rentalId, 'completed', 'Rental completed successfully');
};

// Helper function
const updateRentalStatus = async (rentalId, newStatus, notes) => {
  const response = await fetch(
    `/api/rentals/rentals/${rentalId}/update_status/`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        new_status: newStatus,
        notes: notes
      }),
    }
  );
  
  return await response.json();
};
```

---

### 4. Upload Documentation (Seller)

**Upload delivery photos, condition reports, etc.**

**Endpoint:** `POST /api/rentals/rentals/{id}/upload_image/`

```javascript
const uploadRentalImage = async (rentalId, imageFile, imageType) => {
  const formData = new FormData();
  formData.append('image', imageFile);
  formData.append('image_type', imageType);
  formData.append('description', 'Equipment condition before delivery');
  
  const response = await fetch(
    `/api/rentals/rentals/${rentalId}/upload_image/`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
      },
      body: formData,
    }
  );
  
  return await response.json();
};

// Image types:
// - 'delivery_confirmation'
// - 'equipment_condition_before'
// - 'equipment_condition_after'
// - 'damage_report'
// - 'pickup_confirmation'
// - 'other'
```

---

## 🎨 React Native UI Components

### Rental Card Component

```javascript
import React from 'react';
import { View, Text, Image, TouchableOpacity, StyleSheet } from 'react-native';

const RentalCard = ({ rental, onPress }) => {
  const getStatusColor = (status) => {
    const colors = {
      pending: '#FFA500',
      approved: '#4CAF50',
      confirmed: '#2196F3',
      delivered: '#9C27B0',
      completed: '#4CAF50',
      cancelled: '#F44336',
    };
    return colors[status] || '#757575';
  };
  
  return (
    <TouchableOpacity style={styles.card} onPress={onPress}>
      <Image 
        source={{ uri: rental.equipment_image }} 
        style={styles.image}
      />
      <View style={styles.content}>
        <Text style={styles.reference}>{rental.rental_reference}</Text>
        <Text style={styles.title}>{rental.equipment_name}</Text>
        <Text style={styles.seller}>{rental.seller_name}</Text>
        
        <View style={styles.row}>
          <Text style={styles.label}>Period:</Text>
          <Text style={styles.value}>{rental.rental_duration_text}</Text>
        </View>
        
        <View style={styles.row}>
          <Text style={styles.label}>Total:</Text>
          <Text style={styles.price}>${rental.total_amount}</Text>
        </View>
        
        <View style={[styles.status, { backgroundColor: getStatusColor(rental.status) }]}>
          <Text style={styles.statusText}>{rental.status_display}</Text>
        </View>
        
        {rental.is_overdue && (
          <View style={styles.overdueFlag}>
            <Text style={styles.overdueText}>⚠️ OVERDUE</Text>
          </View>
        )}
      </View>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  card: {
    flexDirection: 'row',
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 12,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  image: {
    width: 100,
    height: 100,
    borderRadius: 8,
  },
  content: {
    flex: 1,
    marginLeft: 12,
  },
  reference: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  title: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  seller: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  label: {
    fontSize: 14,
    color: '#666',
  },
  value: {
    fontSize: 14,
    color: '#333',
  },
  price: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#4CAF50',
  },
  status: {
    alignSelf: 'flex-start',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
    marginTop: 8,
  },
  statusText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  overdueFlag: {
    backgroundColor: '#FF0000',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
    marginTop: 8,
  },
  overdueText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  },
});

export default RentalCard;
```

---

## ⚠️ Common Issues & Solutions

### 1. **No Customer Profile**

**Error:**
```json
{
  "error": "Customer profile required to create rental"
}
```

**Solution:** User must create a customer profile first.

---

### 2. **Equipment Not Available**

**Error:**
```json
{
  "error": "Equipment not available for selected dates"
}
```

**Solution:** Check equipment availability before allowing rental request.

---

### 3. **Invalid Date Range**

**Error:**
```json
{
  "end_date": ["End date must be after start date"]
}
```

**Solution:** Validate dates on frontend before submitting.

---

## 📊 Rental Filtering & Search

```javascript
// Filter by status
GET /api/rentals/rentals/?status=pending
GET /api/rentals/rentals/?status=in_progress

// Search by reference or equipment name
GET /api/rentals/rentals/?search=RNT1234
GET /api/rentals/rentals/?search=excavator

// Filter by date range
GET /api/rentals/rentals/?start_date=2025-11-01&end_date=2025-11-30

// Sort
GET /api/rentals/rentals/?ordering=-created_at  // Newest first
GET /api/rentals/rentals/?ordering=start_date    // Upcoming first
GET /api/rentals/rentals/?ordering=-total_amount // Highest value first
```

---

## ✅ Quick Testing Checklist

### Customer Flow:
1. ✅ Create rental request
2. ✅ View my rentals
3. ✅ View rental details
4. ✅ Cancel pending rental
5. ✅ Make payment
6. ✅ Request return
7. ✅ Leave review

### Seller Flow:
1. ✅ View rental requests
2. ✅ Approve/reject request
3. ✅ Update status through lifecycle
4. ✅ Upload documentation
5. ✅ Complete rental

---

## 🎯 Summary

- ✅ **Customers** use React Native app to browse, request, and manage rentals
- ✅ **Sellers** use React web dashboard to manage rental requests and lifecycle
- ✅ Both apps use the **same API** with different permissions
- ✅ Backend automatically filters data based on user type
- ✅ Complete status flow from request to completion
- ✅ Payment integration ready
- ✅ Review system included
- ✅ Documentation and image upload supported

The API is ready for both your React Native customer app and React seller dashboard! 🎉

## 📋 Overview

The Rentals app manages the entire rental lifecycle - from booking equipment to completion. It handles rental requests, approvals, payments, status tracking, delivery, returns, reviews, and dispute resolution.

### Key Features
- Customer rental requests
- Seller approval workflow
- Multi-status tracking (15 statuses)
- Payment integration
- Delivery tracking
- Review system
- Document management (contracts, receipts)
- Dispute handling
- Late fee calculation
- Rental history

---

## 🗄️ Models

### **1. Rental**
Main rental transaction model

**Core Fields:**
- `customer` (FK to CustomerProfile) - Who is renting
- `equipment` (FK to Equipment) - What is being rented
- `seller` (FK to CompanyProfile) - Equipment owner
- `start_date` - Rental start date
- `end_date` - Rental end date
- `actual_start_date` - When actually delivered
- `actual_end_date` - When actually returned
- `quantity` - Number of units (default 1)

**Pricing:**
- `daily_rate` - Price per day
- `total_days` - Duration in days
- `subtotal` - Base cost (daily_rate × total_days)
- `delivery_fee` - Delivery charge
- `insurance_fee` - Insurance cost
- `security_deposit` - Refundable deposit
- `late_fees` - Late return penalties
- `damage_fees` - Damage charges
- `total_amount` - Grand total

**Status & Tracking:**
- `status` - Current status (15 choices)
- `rental_reference` - Unique reference number (AUTO-GENERATED)
- `created_at`, `updated_at` - Timestamps
- `approved_at`, `cancelled_at` - Status timestamps

**Delivery:**
- `delivery_address` - Delivery location
- `delivery_city`, `delivery_country` - Location
- `delivery_instructions` - Special instructions
- `pickup_required` - Needs delivery or self-pickup

**Contact:**
- `customer_phone`, `customer_email` - Contact info

**Status Choices:**
1. `pending` - Awaiting seller approval
2. `approved` - Seller approved, awaiting payment
3. `payment_pending` - Payment in progress
4. `confirmed` - Paid and confirmed
5. `preparing` - Seller preparing equipment
6. `ready_for_pickup` - Ready for collection
7. `out_for_delivery` - Being delivered
8. `delivered` - Customer received equipment
9. `in_progress` - Active rental period
10. `return_requested` - Customer wants to return
11. `returning` - Equipment being returned
12. `completed` - Successfully completed
13. `cancelled` - Cancelled before delivery
14. `overdue` - Past return date
15. `dispute` - Under dispute resolution

### **2. RentalStatusUpdate**
Status change log

**Fields:**
- `rental` (FK to Rental) - Parent rental
- `old_status` - Previous status
- `new_status` - New status
- `updated_by` (FK to User) - Who changed it
- `notes` - Status change notes
- `is_visible_to_customer` - Show to customer
- `updated_at` - When changed

### **3. RentalImage**
Photos of equipment at delivery/return

**Fields:**
- `rental` (FK to Rental) - Parent rental
- `image` - Image file
- `caption` - Description
- `uploaded_by` (FK to User) - Who uploaded
- `image_type` - delivery, return, damage, other
- `uploaded_at` - Timestamp

### **4. RentalReview**
Customer reviews after rental

**Fields:**
- `rental` (OneToOne to Rental) - Reviewed rental
- `customer` (FK to CustomerProfile) - Reviewer
- `equipment` (FK to Equipment) - Reviewed equipment
- `seller` (FK to CompanyProfile) - Reviewed seller
- `equipment_rating` - 1-5 stars
- `seller_rating` - 1-5 stars
- `delivery_rating` - 1-5 stars
- `value_rating` - 1-5 stars
- `review_text` - Written review
- `would_recommend` - Boolean
- `created_at` - Review date

### **5. RentalPayment**
Payment records

**Fields:**
- `rental` (FK to Rental) - Parent rental
- `amount` - Payment amount
- `payment_type` - rental_fee, deposit, late_fee, damage_fee, refund
- `payment_method` - card, cash, bank_transfer
- `payment_status` - pending, completed, failed, refunded
- `transaction_id` - External payment ID
- `payment_gateway` - stripe, paypal, etc.
- `paid_by` (FK to User) - Who paid
- `created_at`, `processed_at` - Timestamps

### **6. RentalDocument**
Contracts, receipts, agreements

**Fields:**
- `rental` (FK to Rental) - Parent rental
- `document` - File upload
- `document_type` - contract, receipt, invoice, insurance, other
- `title` - Document title
- `uploaded_by` (FK to User) - Who uploaded
- `uploaded_at` - Timestamp

---

## 🔗 API Endpoints

### **Rentals**

#### 1. List Rentals
```
GET /api/rentals/rentals/
Authorization: Bearer <token>
```

**Query Parameters:**
- `status=pending` - Filter by status
- `equipment=101` - Filter by equipment ID
- `start_date=2025-10-01` - Filter by start date
- `search=REF-123` - Search reference or equipment name
- `ordering=-created_at` - Sort field

**Response (200 OK) - Customer:**
```json
{
  "count": 12,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 501,
      "rental_reference": "RNT-20251021-0001",
      "equipment": {
        "id": 101,
        "name": "CAT 320D Excavator",
        "main_image_url": "https://..."
      },
      "seller": {
        "id": 5,
        "company_name": "Dubai Equipment Rentals"
      },
      "start_date": "2025-10-25",
      "end_date": "2025-11-05",
      "total_days": 11,
      "total_amount": "5650.00",
      "status": "confirmed",
      "status_display": "Confirmed",
      "created_at": "2025-10-21T10:30:00Z"
    }
  ]
}
```

**Response (Seller):**
```json
{
  "count": 45,
  "results": [
    {
      "id": 501,
      "rental_reference": "RNT-20251021-0001",
      "customer": {
        "id": 23,
        "full_name": "John Smith",
        "phone_number": "+971501234567"
      },
      "equipment": {
        "id": 101,
        "name": "CAT 320D Excavator"
      },
      "start_date": "2025-10-25",
      "end_date": "2025-11-05",
      "total_amount": "5650.00",
      "status": "pending",
      "created_at": "2025-10-21T10:30:00Z"
    }
  ]
}
```

---

#### 2. Get Rental Detail
```
GET /api/rentals/rentals/{id}/
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "id": 501,
  "rental_reference": "RNT-20251021-0001",
  "customer": {
    "id": 23,
    "full_name": "John Smith",
    "email": "john@example.com",
    "phone_number": "+971501234567"
  },
  "equipment": {
    "id": 101,
    "name": "CAT 320D Excavator",
    "category_name": "Excavators",
    "main_image_url": "https://...",
    "brand": "Caterpillar"
  },
  "seller": {
    "id": 5,
    "company_name": "Dubai Equipment Rentals",
    "company_logo_url": "https://...",
    "phone_number": "+971509876543"
  },
  "start_date": "2025-10-25",
  "end_date": "2025-11-05",
  "actual_start_date": "2025-10-25T08:30:00Z",
  "actual_end_date": null,
  "quantity": 1,
  "daily_rate": "500.00",
  "total_days": 11,
  "subtotal": "5500.00",
  "delivery_fee": "150.00",
  "insurance_fee": "0.00",
  "security_deposit": "2000.00",
  "late_fees": "0.00",
  "damage_fees": "0.00",
  "total_amount": "5650.00",
  "status": "in_progress",
  "status_display": "Rental in Progress",
  "delivery_address": "Dubai Marina, Building 5",
  "delivery_city": "DXB",
  "delivery_country": "UAE",
  "delivery_instructions": "Call 30 minutes before delivery",
  "pickup_required": true,
  "status_history": [
    {
      "id": 1001,
      "old_status": null,
      "new_status": "pending",
      "updated_by_name": "System",
      "notes": "Rental request created",
      "updated_at": "2025-10-21T10:30:00Z"
    },
    {
      "id": 1002,
      "old_status": "pending",
      "new_status": "approved",
      "updated_by_name": "Dubai Equipment Rentals",
      "notes": "Request approved",
      "updated_at": "2025-10-21T11:15:00Z"
    },
    {
      "id": 1003,
      "old_status": "approved",
      "new_status": "confirmed",
      "updated_by_name": "John Smith",
      "notes": "Payment completed",
      "updated_at": "2025-10-21T12:00:00Z"
    }
  ],
  "images": [
    {
      "id": 2001,
      "image_url": "https://...",
      "caption": "Equipment condition at delivery",
      "image_type": "delivery",
      "uploaded_at": "2025-10-25T08:30:00Z"
    }
  ],
  "payments": [
    {
      "id": 3001,
      "amount": "5650.00",
      "payment_type": "rental_fee",
      "payment_status": "completed",
      "transaction_id": "txn_abc123",
      "created_at": "2025-10-21T12:00:00Z"
    }
  ],
  "documents": [],
  "review": null,
  "can_review": false,
  "created_at": "2025-10-21T10:30:00Z",
  "updated_at": "2025-10-25T08:30:00Z"
}
```

---

#### 3. Create Rental Request (Customer)
```
POST /api/rentals/rentals/
Authorization: Bearer <customer_token>
```

**Request Body:**
```json
{
  "equipment": 101,
  "start_date": "2025-10-25",
  "end_date": "2025-11-05",
  "quantity": 1,
  "delivery_address": "Dubai Marina, Building 5, Apt 201",
  "delivery_city": "DXB",
  "delivery_country": "UAE",
  "delivery_instructions": "Call 30 minutes before delivery. Gate code: 1234",
  "customer_phone": "+971501234567",
  "customer_email": "john@example.com"
}
```

**Response (201 Created):**
```json
{
  "id": 501,
  "rental_reference": "RNT-20251021-0001",
  "equipment": {...},
  "seller": {...},
  "start_date": "2025-10-25",
  "end_date": "2025-11-05",
  "total_days": 11,
  "daily_rate": "500.00",
  "subtotal": "5500.00",
  "delivery_fee": "150.00",
  "security_deposit": "2000.00",
  "total_amount": "5650.00",
  "status": "pending",
  "message": "Rental request created. Awaiting seller approval."
}
```

**Notes:**
- Customer is auto-set from authenticated user
- Seller is auto-set from equipment's seller
- daily_rate copied from equipment
- total_days auto-calculated
- total_amount auto-calculated
- rental_reference auto-generated
- Status starts as "pending"

---

#### 4. Update Rental Status
```
POST /api/rentals/rentals/{id}/update_status/
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "new_status": "delivered",
  "notes": "Equipment delivered successfully",
  "is_visible_to_customer": true
}
```

**Response (200 OK):**
```json
{
  "message": "Rental status updated to delivered",
  "rental": {...}
}
```

**Allowed Status Transitions:**
- Seller can: pending→approved, approved→preparing, preparing→ready_for_pickup, ready_for_pickup→out_for_delivery, out_for_delivery→delivered, returning→completed
- Customer can: delivered→return_requested
- System can: Any status (staff)

---

#### 5. Approve Rental (Seller)
```
POST /api/rentals/rentals/{id}/approve/
Authorization: Bearer <seller_token>
```

**Response (200 OK):**
```json
{
  "message": "Rental approved. Customer will be notified to complete payment.",
  "rental": {...}
}
```

**Requirements:**
- Must be seller who owns the equipment
- Rental must be in "pending" status

---

#### 6. Reject/Cancel Rental
```
POST /api/rentals/rentals/{id}/cancel/
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "reason": "Equipment not available on requested dates"
}
```

**Response (200 OK):**
```json
{
  "message": "Rental cancelled",
  "rental": {...}
}
```

**Permissions:**
- Customer can cancel before "confirmed"
- Seller can cancel/reject "pending" rentals
- Staff can cancel any status

---

#### 7. Mark Delivered
```
POST /api/rentals/rentals/{id}/mark_delivered/
Authorization: Bearer <seller_token>
```

**With Images:**
```
POST /api/rentals/rentals/{id}/mark_delivered/
Content-Type: multipart/form-data

Fields:
- notes: "Delivered at 8:30 AM"
- image_1: [file]
- image_2: [file]
- image_caption_1: "Equipment condition - front"
- image_caption_2: "Equipment condition - side"
```

**Response (200 OK):**
```json
{
  "message": "Rental marked as delivered",
  "rental": {...}
}
```

---

#### 8. Request Return (Customer)
```
POST /api/rentals/rentals/{id}/request_return/
Authorization: Bearer <customer_token>
```

**Request Body:**
```json
{
  "return_date": "2025-11-05",
  "return_notes": "Equipment no longer needed. Ready for pickup."
}
```

**Response (200 OK):**
```json
{
  "message": "Return requested. Seller will coordinate pickup.",
  "rental": {...}
}
```

---

#### 9. Complete Rental (Seller)
```
POST /api/rentals/rentals/{id}/complete/
Authorization: Bearer <seller_token>
```

**With Images:**
```
POST /api/rentals/rentals/{id}/complete/
Content-Type: multipart/form-data

Fields:
- notes: "Equipment returned in good condition"
- damage_fees: 0 (or amount if damaged)
- late_fees: 0 (or amount if late)
- image_1: [file] (return condition photos)
```

**Response (200 OK):**
```json
{
  "message": "Rental completed successfully",
  "rental": {...},
  "refund_amount": "2000.00"
}
```

---

#### 10. Get My Rentals (Customer)
```
GET /api/rentals/rentals/my_rentals/
Authorization: Bearer <customer_token>
```

**Query Parameters:**
- `status=in_progress` - Filter by status
- `active=true` - Only active rentals (not completed/cancelled)

**Response:** List of customer's rentals

---

#### 11. Get Pending Approvals (Seller)
```
GET /api/rentals/rentals/pending_approvals/
Authorization: Bearer <seller_token>
```

**Response:** List of rentals awaiting seller approval

---

#### 12. Get Active Rentals (Seller)
```
GET /api/rentals/rentals/active_rentals/
Authorization: Bearer <seller_token>
```

**Response:** Rentals in progress for seller's equipment

---

### **Reviews**

#### 13. List Reviews
```
GET /api/rentals/reviews/
```

**Query Parameters:**
- `equipment=101` - Filter by equipment
- `seller=5` - Filter by seller
- `customer=23` - Filter by customer

**Response (200 OK):**
```json
[
  {
    "id": 401,
    "customer_name": "John Smith",
    "equipment_name": "CAT 320D Excavator",
    "seller_name": "Dubai Equipment Rentals",
    "equipment_rating": 5,
    "seller_rating": 5,
    "delivery_rating": 4,
    "value_rating": 5,
    "overall_rating": 4.75,
    "review_text": "Excellent equipment! Worked perfectly for our project.",
    "would_recommend": true,
    "created_at": "2025-11-06T10:00:00Z"
  }
]
```

---

#### 14. Create Review (Customer)
```
POST /api/rentals/reviews/
Authorization: Bearer <customer_token>
```

**Request Body:**
```json
{
  "rental": 501,
  "equipment_rating": 5,
  "seller_rating": 5,
  "delivery_rating": 4,
  "value_rating": 5,
  "review_text": "Excellent equipment! Worked perfectly for our project. Delivery was on time and the seller was very professional.",
  "would_recommend": true
}
```

**Response (201 Created):**
```json
{
  "id": 401,
  "rental_id": 501,
  "equipment_rating": 5,
  "seller_rating": 5,
  "overall_rating": 4.75,
  "review_text": "...",
  "created_at": "2025-11-06T10:00:00Z"
}
```

**Requirements:**
- Rental must be "completed"
- Customer must be the renter
- Can only review once per rental

---

### **Images**

#### 15. Upload Rental Image
```
POST /api/rentals/rental-images/
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Form Data:**
- `rental` - Rental ID
- `image` - Image file
- `caption` - Image description
- `image_type` - delivery, return, damage, other

**Response (201 Created):**
```json
{
  "id": 2001,
  "rental_id": 501,
  "image_url": "https://...",
  "caption": "Equipment condition at delivery",
  "image_type": "delivery",
  "uploaded_at": "2025-10-25T08:30:00Z"
}
```

---

## 📱 React Native Examples

### Customer: Create Rental Request

```javascript
const CreateRentalScreen = ({ route }) => {
  const { equipmentId } = route.params;
  const [formData, setFormData] = useState({
    start_date: '',
    end_date: '',
    delivery_address: '',
    delivery_city: 'DXB',
    delivery_instructions: ''
  });
  
  const calculateTotal = async () => {
    // Fetch equipment to get daily_rate
    const response = await fetch(
      `https://api.tezrent.com/api/equipment/equipment/${equipmentId}/`
    );
    const equipment = await response.json();
    
    const days = calculateDays(formData.start_date, formData.end_date);
    const subtotal = equipment.daily_rate * days;
    const total = subtotal + equipment.delivery_fee + equipment.security_deposit;
    
    return { subtotal, total, days };
  };
  
  const submitRental = async () => {
    const token = await AsyncStorage.getItem('access_token');
    
    const response = await fetch('https://api.tezrent.com/api/rentals/rentals/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        equipment: equipmentId,
        ...formData,
        customer_phone: userProfile.phone_number,
        customer_email: userProfile.email
      })
    });
    
    const rental = await response.json();
    
    // Navigate to rental detail
    navigation.navigate('RentalDetail', { id: rental.id });
  };
  
  return (
    <ScrollView>
      <DatePicker
        value={formData.start_date}
        onChange={(date) => setFormData({...formData, start_date: date})}
      />
      <DatePicker
        value={formData.end_date}
        onChange={(date) => setFormData({...formData, end_date: date})}
      />
      <TextInput
        placeholder="Delivery Address"
        value={formData.delivery_address}
        onChangeText={(text) => setFormData({...formData, delivery_address: text})}
      />
      <Button title="Request Rental" onPress={submitRental} />
    </ScrollView>
  );
};
```

### Seller: Approve Rental

```javascript
const PendingApprovalsScreen = () => {
  const [pendingRentals, setPendingRentals] = useState([]);
  
  useEffect(() => {
    fetchPendingRentals();
  }, []);
  
  const fetchPendingRentals = async () => {
    const token = await AsyncStorage.getItem('access_token');
    
    const response = await fetch(
      'https://api.tezrent.com/api/rentals/rentals/pending_approvals/',
      {
        headers: { 'Authorization': `Bearer ${token}` }
      }
    );
    
    const data = await response.json();
    setPendingRentals(data.results);
  };
  
  const approveRental = async (rentalId) => {
    const token = await AsyncStorage.getItem('access_token');
    
    await fetch(
      `https://api.tezrent.com/api/rentals/rentals/${rentalId}/approve/`,
      {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      }
    );
    
    // Refresh list
    fetchPendingRentals();
  };
  
  return (
    <FlatList
      data={pendingRentals}
      renderItem={({ item }) => (
        <View>
          <Text>{item.rental_reference}</Text>
          <Text>{item.customer.full_name}</Text>
          <Text>{item.equipment.name}</Text>
          <Text>AED {item.total_amount}</Text>
          <Button title="Approve" onPress={() => approveRental(item.id)} />
        </View>
      )}
    />
  );
};
```

### Customer: Track Rental Status

```javascript
const RentalDetailScreen = ({ route }) => {
  const { id } = route.params;
  const [rental, setRental] = useState(null);
  
  useEffect(() => {
    fetchRental();
    const interval = setInterval(fetchRental, 30000); // Poll every 30s
    return () => clearInterval(interval);
  }, []);
  
  const fetchRental = async () => {
    const token = await AsyncStorage.getItem('access_token');
    
    const response = await fetch(
      `https://api.tezrent.com/api/rentals/rentals/${id}/`,
      {
        headers: { 'Authorization': `Bearer ${token}` }
      }
    );
    
    const data = await response.json();
    setRental(data);
  };
  
  const getStatusColor = (status) => {
    const colors = {
      pending: '#FFA500',
      confirmed: '#4CAF50',
      delivered: '#2196F3',
      completed: '#4CAF50',
      cancelled: '#F44336'
    };
    return colors[status] || '#757575';
  };
  
  if (!rental) return <Loading />;
  
  return (
    <ScrollView>
      <Text>Rental: {rental.rental_reference}</Text>
      
      {/* Status Timeline */}
      <View>
        {rental.status_history.map((update, index) => (
          <View key={update.id}>
            <View style={{ backgroundColor: getStatusColor(update.new_status) }}>
              <Text>{update.new_status}</Text>
              <Text>{update.notes}</Text>
              <Text>{formatDate(update.updated_at)}</Text>
            </View>
          </View>
        ))}
      </View>
      
      {/* Equipment Info */}
      <View>
        <Image source={{ uri: rental.equipment.main_image_url }} />
        <Text>{rental.equipment.name}</Text>
      </View>
      
      {/* Pricing Breakdown */}
      <View>
        <Text>Subtotal: AED {rental.subtotal}</Text>
        <Text>Delivery: AED {rental.delivery_fee}</Text>
        <Text>Deposit: AED {rental.security_deposit}</Text>
        <Text>Total: AED {rental.total_amount}</Text>
      </View>
      
      {/* Actions */}
      {rental.status === 'delivered' && (
        <Button title="Request Return" onPress={requestReturn} />
      )}
      {rental.status === 'completed' && !rental.review && (
        <Button title="Write Review" onPress={openReviewForm} />
      )}
    </ScrollView>
  );
};
```

---

## 🔒 Permissions

| Action | Customer | Seller (Owner) | Seller (Other) | Staff |
|--------|----------|----------------|----------------|-------|
| List Rentals | ✅ Own | ✅ Own | ❌ | ✅ All |
| Create Rental | ✅ | ❌ | ❌ | ✅ |
| View Detail | ✅ Own | ✅ Own | ❌ | ✅ All |
| Approve | ❌ | ✅ | ❌ | ✅ |
| Cancel | ✅ Own (before confirmed) | ✅ Own | ❌ | ✅ |
| Update Status | ❌ | ✅ Own | ❌ | ✅ |
| Mark Delivered | ❌ | ✅ | ❌ | ✅ |
| Request Return | ✅ Own | ❌ | ❌ | ✅ |
| Complete | ❌ | ✅ | ❌ | ✅ |
| Create Review | ✅ Own | ❌ | ❌ | ❌ |

---

## 📄 Files Reference

- `rentals/models.py` - Rental, RentalStatusUpdate, RentalImage, RentalReview, RentalPayment, RentalDocument
- `rentals/serializers.py` - List, detail, create serializers
- `rentals/views.py` - RentalViewSet, RentalReviewViewSet
- `rentals/urls.py` - URL routing
- `rentals/admin.py` - Django admin

---

**End of Rentals API Documentation** 📚
