# Rentals Frontend Integration Guide

## 🎯 Quick Reference: Expected API Response Structure

### 1. GET /api/rentals/rentals/ - List View (Seller Dashboard)

**Query Parameters:**
```javascript
// Filter by status (supports comma-separated values)
?status=pending
?status=completed,cancelled,disputed

// Ordering
?ordering=-end_date        // Latest end date first
?ordering=-created_at      // Newest first
?ordering=start_date       // Earliest start date first

// Pagination
?page=1&page_size=10

// Search
?search=RNT123            // Search by rental reference or equipment name

// Date filtering
?start_date__gte=2025-10-27
?end_date__lte=2025-12-31
```

**Expected Response Structure:**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "rental_reference": "RNTF7EC27D3",
      "equipment": {
        "id": 1,
        "name": "Catepillar",
        "category_name": "Heavy Equipment"
      },
      "equipment_image": "http://localhost:8000/media/equipment_images/...",
      "customer_name": "John Smith",
      "customer_email": "customer1@example.com",
      "start_date": "2025-10-30",
      "end_date": "2025-11-06",
      "status": "pending",
      "status_display": "Pending Approval",
      "total_amount": "1825.00",
      "created_at": "2025-10-27T10:30:00Z",
      "days_remaining": 3,
      "is_overdue": false,
      "rental_duration_text": "8 days"
    }
  ]
}
```

### 2. GET /api/rentals/rentals/{id}/ - Detail View

**Expected Response Structure:**
```json
{
  "id": 1,
  "rental_reference": "RNTF7EC27D3",
  "equipment": {
    "id": 1,
    "name": "Catepillar",
    "category": {
      "id": 1,
      "name": "Heavy Equipment"
    },
    "daily_rate": "225.00",
    "available_quantity": 5,
    "main_image": "http://localhost:8000/media/equipment_images/..."
  },
  "customer_details": {
    "id": 1,
    "name": "John Smith",
    "email": "customer1@example.com",
    "phone": "+1234567890",
    "address": "123 Main Street, Apartment 4B",
    "city": "DXB"
  },
  "seller_details": {
    "id": 1,
    "company_name": "Ustasells",
    "email": "seller@ustasells.com",
    "company_phone": "+9711234567"
  },
  "start_date": "2025-10-30",
  "end_date": "2025-11-06",
  "quantity": 1,
  "daily_rate": "225.00",
  "total_days": 8,
  "subtotal": "1800.00",
  "delivery_fee": "150.00",
  "insurance_fee": "75.00",
  "security_deposit": "1000.00",
  "total_amount": "1825.00",
  "status": "pending",
  "status_display": "Pending Approval",
  "delivery_address": "123 Main Street, Apartment 4B, New York, NY 10001",
  "delivery_city": "NYC",
  "delivery_country": "USA",
  "delivery_instructions": "",
  "pickup_required": true,
  "customer_phone": "+1234567890",
  "customer_email": "customer1@example.com",
  "customer_notes": "Need equipment for construction project...",
  "created_at": "2025-10-27T10:30:00Z",
  "approved_at": null,
  "actual_start_date": null,
  "actual_end_date": null,
  "days_remaining": 3,
  "is_overdue": false,
  "rental_duration_text": "8 days",
  "status_updates": [
    {
      "id": 1,
      "old_status": null,
      "new_status": "pending",
      "notes": "Rental request created",
      "updated_by": "John Smith",
      "updated_at": "2025-10-27T10:30:00Z"
    }
  ],
  "images": [],
  "payments": [],
  "documents": [],
  "review": null,
  "available_actions": [
    {
      "action": "approve",
      "label": "Approve Rental",
      "next_status": "approved"
    },
    {
      "action": "reject",
      "label": "Reject Rental",
      "next_status": "cancelled"
    }
  ]
}
```

### 3. POST /api/rentals/rentals/{id}/update_status/ - Update Status

**Request Body:**
```json
{
  "new_status": "approved",
  "notes": "Rental approved. Equipment will be prepared for delivery."
}
```

**Expected Response:**
```json
{
  "id": 1,
  "rental_reference": "RNTF7EC27D3",
  "status": "approved",
  "status_display": "Approved",
  // ... (full rental detail)
}
```

**Valid Status Transitions:**

| Current Status | Allowed Next Status |
|---------------|---------------------|
| `pending` | `approved`, `cancelled` |
| `approved` | `payment_pending`, `confirmed`, `cancelled` |
| `payment_pending` | `confirmed`, `cancelled` |
| `confirmed` | `preparing`, `cancelled` |
| `preparing` | `ready_for_pickup`, `out_for_delivery`, `cancelled` |
| `ready_for_pickup` | `delivered`, `cancelled` |
| `out_for_delivery` | `delivered`, `cancelled` |
| `delivered` | `in_progress` |
| `in_progress` | `return_requested`, `completed` |
| `return_requested` | `returning` |
| `returning` | `completed` |

---

## 🎨 React Seller Dashboard - Component Examples

### Rentals List Page

```tsx
// Expected data structure for the list
interface RentalListItem {
  id: number;
  rental_reference: string;
  equipment: {
    id: number;
    name: string;
    category_name: string;
  };
  equipment_image: string;
  customer_name: string;
  customer_email: string;
  start_date: string;
  end_date: string;
  status: string;
  status_display: string;
  total_amount: string;
  created_at: string;
  days_remaining: number;
  is_overdue: boolean;
  rental_duration_text: string;
}

// Fetch rentals
const fetchRentals = async (filters: {
  status?: string;      // e.g., "pending" or "completed,cancelled,disputed"
  ordering?: string;    // e.g., "-end_date"
  page?: number;
  page_size?: number;
}) => {
  const params = new URLSearchParams();
  if (filters.status) params.append('status', filters.status);
  if (filters.ordering) params.append('ordering', filters.ordering);
  if (filters.page) params.append('page', filters.page.toString());
  if (filters.page_size) params.append('page_size', filters.page_size.toString());
  
  const response = await fetch(
    `http://localhost:8000/api/rentals/rentals/?${params}`,
    {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
      }
    }
  );
  
  return await response.json();
};

// Usage examples:
// Active rentals: status=approved,confirmed,preparing,delivered,in_progress
// Pending approval: status=pending
// Completed: status=completed,cancelled,disputed
```

### Rental Detail Page

```tsx
interface RentalDetail {
  id: number;
  rental_reference: string;
  equipment: {
    id: number;
    name: string;
    category: { id: number; name: string };
    daily_rate: string;
    available_quantity: number;
    main_image: string;
  };
  customer_details: {
    id: number;
    name: string;
    email: string;
    phone: string;
    address: string;
    city: string;
  };
  seller_details: {
    id: number;
    company_name: string;
    email: string;
    company_phone: string;
  };
  start_date: string;
  end_date: string;
  quantity: number;
  daily_rate: string;
  total_days: number;
  subtotal: string;
  delivery_fee: string;
  insurance_fee: string;
  security_deposit: string;
  total_amount: string;
  status: string;
  status_display: string;
  delivery_address: string;
  delivery_city: string;
  delivery_country: string;
  delivery_instructions: string;
  pickup_required: boolean;
  customer_phone: string;
  customer_email: string;
  customer_notes: string;
  created_at: string;
  approved_at: string | null;
  actual_start_date: string | null;
  actual_end_date: string | null;
  days_remaining: number;
  is_overdue: boolean;
  rental_duration_text: string;
  status_updates: StatusUpdate[];
  images: RentalImage[];
  payments: Payment[];
  documents: Document[];
  review: Review | null;
  available_actions: Action[];
}

interface Action {
  action: string;
  label: string;
  next_status: string;
}

// Fetch rental detail
const fetchRentalDetail = async (rentalId: number) => {
  const response = await fetch(
    `http://localhost:8000/api/rentals/rentals/${rentalId}/`,
    {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
      }
    }
  );
  
  return await response.json();
};

// Update rental status
const updateRentalStatus = async (
  rentalId: number,
  newStatus: string,
  notes?: string
) => {
  const response = await fetch(
    `http://localhost:8000/api/rentals/rentals/${rentalId}/update_status/`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        new_status: newStatus,
        notes: notes || ''
      })
    }
  );
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to update status');
  }
  
  return await response.json();
};
```

### Status Badge Component

```tsx
// Status colors for UI
const STATUS_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  pending: { bg: '#FEF3C7', text: '#92400E', border: '#FCD34D' },
  approved: { bg: '#DBEAFE', text: '#1E40AF', border: '#93C5FD' },
  payment_pending: { bg: '#FCE7F3', text: '#9F1239', border: '#FBCFE8' },
  confirmed: { bg: '#D1FAE5', text: '#065F46', border: '#6EE7B7' },
  preparing: { bg: '#E0E7FF', text: '#3730A3', border: '#C7D2FE' },
  ready_for_pickup: { bg: '#DDD6FE', text: '#5B21B6', border: '#C4B5FD' },
  out_for_delivery: { bg: '#BFDBFE', text: '#1E3A8A', border: '#93C5FD' },
  delivered: { bg: '#D1FAE5', text: '#065F46', border: '#6EE7B7' },
  in_progress: { bg: '#D1FAE5', text: '#065F46', border: '#6EE7B7' },
  return_requested: { bg: '#FED7AA', text: '#9A3412', border: '#FDBA74' },
  returning: { bg: '#FEF3C7', text: '#92400E', border: '#FCD34D' },
  completed: { bg: '#D1FAE5', text: '#065F46', border: '#6EE7B7' },
  cancelled: { bg: '#FEE2E2', text: '#991B1B', border: '#FCA5A5' },
  overdue: { bg: '#FEE2E2', text: '#991B1B', border: '#FCA5A5' },
  dispute: { bg: '#FEE2E2', text: '#991B1B', border: '#FCA5A5' }
};

const StatusBadge = ({ status, displayText }: { status: string; displayText: string }) => {
  const colors = STATUS_COLORS[status] || STATUS_COLORS.pending;
  
  return (
    <span
      style={{
        backgroundColor: colors.bg,
        color: colors.text,
        border: `1px solid ${colors.border}`,
        padding: '4px 12px',
        borderRadius: '12px',
        fontSize: '12px',
        fontWeight: 600,
        textTransform: 'uppercase'
      }}
    >
      {displayText}
    </span>
  );
};
```

### Action Buttons Component

```tsx
const RentalActions = ({ rental, onStatusUpdate }: {
  rental: RentalDetail;
  onStatusUpdate: () => void;
}) => {
  const [loading, setLoading] = useState(false);
  
  const handleAction = async (action: Action) => {
    if (!confirm(`Are you sure you want to ${action.label.toLowerCase()}?`)) {
      return;
    }
    
    setLoading(true);
    try {
      await updateRentalStatus(rental.id, action.next_status);
      alert(`Rental ${action.label.toLowerCase()} successfully!`);
      onStatusUpdate();
    } catch (error) {
      alert(error.message);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div style={{ display: 'flex', gap: '8px' }}>
      {rental.available_actions.map((action) => (
        <button
          key={action.action}
          onClick={() => handleAction(action)}
          disabled={loading}
          style={{
            padding: '8px 16px',
            borderRadius: '6px',
            border: 'none',
            cursor: loading ? 'not-allowed' : 'pointer',
            backgroundColor: action.action === 'approve' ? '#10B981' : '#EF4444',
            color: 'white',
            fontWeight: 600
          }}
        >
          {action.label}
        </button>
      ))}
    </div>
  );
};
```

---

## 📱 React Native Customer App - Component Examples

### Rentals List (Customer View)

```tsx
// Customer sees their own rentals only
const MyRentals = () => {
  const [activeRentals, setActiveRentals] = useState([]);
  const [pastRentals, setPastRentals] = useState([]);
  
  useEffect(() => {
    // Active rentals
    fetchRentals({
      status: 'approved,confirmed,preparing,delivered,in_progress',
      ordering: '-start_date'
    }).then(data => setActiveRentals(data.results));
    
    // Past rentals
    fetchRentals({
      status: 'completed,cancelled,disputed',
      ordering: '-end_date'
    }).then(data => setPastRentals(data.results));
  }, []);
  
  return (
    <ScrollView>
      <Text style={{ fontSize: 18, fontWeight: 'bold', marginBottom: 12 }}>
        Active Rentals
      </Text>
      {activeRentals.map(rental => (
        <RentalCard key={rental.id} rental={rental} />
      ))}
      
      <Text style={{ fontSize: 18, fontWeight: 'bold', marginTop: 24, marginBottom: 12 }}>
        Past Rentals
      </Text>
      {pastRentals.map(rental => (
        <RentalCard key={rental.id} rental={rental} />
      ))}
    </ScrollView>
  );
};
```

---

## 🔍 Common Frontend Issues & Solutions

### Issue 1: 400 Bad Request on Status Filter
**Problem:** `?status=completed,cancelled,disputed` returns 400
**Solution:** Backend now supports comma-separated values. Make sure you're using the updated API.

### Issue 2: Empty Results for Seller
**Problem:** Seller sees no rentals even though they exist
**Solution:** 
- Ensure you're logged in with the seller account that owns the equipment
- Backend auto-filters rentals by `seller=user.company_profile`
- Check that rentals have `seller` field set correctly

### Issue 3: Missing Fields in Response
**Problem:** Frontend expects fields that aren't in the response
**Solution:** Use the list serializer for lists (lighter) and detail serializer for detail views (complete). Check the exact field names above.

### Issue 4: Status Display vs Status Value
**Problem:** Using `status_display` instead of `status` for filtering
**Solution:**
- Use `status` (lowercase, underscored) for filtering: `pending`, `approved`, etc.
- Use `status_display` (human-readable) for UI: "Pending Approval", "Approved", etc.

### Issue 5: Date Filtering Not Working
**Problem:** Date filters not working as expected
**Solution:** Use these formats:
```
?start_date__gte=2025-10-27        (greater than or equal)
?start_date__lte=2025-12-31        (less than or equal)
?start_date=2025-10-27             (exact match)
```

---

## ✅ Testing Checklist

### Seller Dashboard
- [ ] Can see all rentals for my company's equipment
- [ ] Can filter by status: `pending`, `approved,confirmed`, `completed,cancelled,disputed`
- [ ] Can sort by: `-end_date`, `-created_at`, `start_date`
- [ ] Can view rental details
- [ ] Can approve/reject pending rentals
- [ ] Can update status through workflow
- [ ] Status badges show correct colors
- [ ] Available actions show only valid transitions

### Customer App
- [ ] Can see only my rentals
- [ ] Can view rental details
- [ ] Can see rental status updates
- [ ] Can track delivery status
- [ ] Can view pricing breakdown

---

## 🚨 Error Responses

### Invalid Status Transition
```json
{
  "error": "Invalid status transition from 'completed' to 'pending'"
}
```

### Missing Required Fields
```json
{
  "new_status": ["This field is required."]
}
```

### Permission Denied
```json
{
  "detail": "You do not have permission to perform this action."
}
```

---

## 📊 Sample API Calls

```bash
# List all rentals (for logged-in seller)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/rentals/rentals/

# Filter pending rentals
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/rentals/rentals/?status=pending"

# Filter multiple statuses
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/rentals/rentals/?status=completed,cancelled,disputed&ordering=-end_date"

# Get rental detail
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/rentals/rentals/1/

# Approve rental
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"new_status": "approved", "notes": "Approved!"}' \
  http://localhost:8000/api/rentals/rentals/1/update_status/
```

---

## 🎯 Key Differences: List vs Detail

**List View** (`RentalListSerializer`):
- Lightweight for performance
- Basic equipment info (id, name, category_name)
- Single equipment_image URL
- Customer name and email only
- Perfect for tables/cards

**Detail View** (`RentalDetailSerializer`):
- Complete information
- Nested equipment with full details
- Nested customer_details and seller_details
- All status_updates, images, payments, documents
- available_actions for workflow buttons
- Perfect for detail pages

---

That's it! Your frontend should now work perfectly with the API. 🚀
