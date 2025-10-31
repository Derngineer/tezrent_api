# ⚡ Real-Time Availability Check Guide

## 🎯 Problem Solved

**Before:** Customer fills out entire booking form → Clicks submit → Gets error "Not available" 😞

**After:** Customer enters dates → Instant feedback on availability → Only proceeds if available ✅

---

## 🚀 New API Endpoint

### GET /api/equipment/equipment/{id}/check_availability/

**Call this FIRST, before showing the booking form!**

---

## 📱 Frontend Booking Flow (Recommended)

### Step 1: Date Selection Screen
```typescript
// Customer selects dates and quantity
const [startDate, setStartDate] = useState('2025-10-28');
const [endDate, setEndDate] = useState('2025-10-30');
const [quantity, setQuantity] = useState(1);
const [availability, setAvailability] = useState(null);
const [checking, setChecking] = useState(false);

// Check availability as they select dates
const checkAvailability = async () => {
  setChecking(true);
  
  const response = await fetch(
    `http://localhost:8000/api/equipment/equipment/${equipmentId}/check_availability/?` +
    `start_date=${startDate}&end_date=${endDate}&quantity=${quantity}`
  );
  
  const data = await response.json();
  setAvailability(data);
  setChecking(false);
};

// Auto-check when dates change
useEffect(() => {
  if (startDate && endDate && quantity) {
    checkAvailability();
  }
}, [startDate, endDate, quantity]);
```

### Step 2: Show Availability Status
```tsx
{checking && <Spinner />}

{availability && (
  <div className={`availability-card ${availability.available ? 'success' : 'error'}`}>
    <h3>{availability.message}</h3>
    
    <div className="availability-details">
      <p>📅 {availability.dates.total_days} days</p>
      <p>📦 {availability.available_units}/{availability.total_units} units available</p>
      <p>💰 Estimated: AED {availability.price_estimate.total_amount}</p>
    </div>
    
    {availability.available ? (
      <button onClick={proceedToBooking} className="btn-success">
        ✅ Continue to Booking
      </button>
    ) : (
      <div>
        <p className="error-message">{availability.message}</p>
        <button onClick={() => adjustDates()}>
          Try Different Dates
        </button>
      </div>
    )}
  </div>
)}
```

### Step 3: Only Show Booking Form if Available
```tsx
{availability?.available && (
  <BookingForm
    equipmentId={equipmentId}
    startDate={startDate}
    endDate={endDate}
    quantity={quantity}
    priceEstimate={availability.price_estimate}
  />
)}
```

---

## 📊 API Request & Response

### Request Example:
```bash
GET /api/equipment/equipment/1/check_availability/?start_date=2025-10-28&end_date=2025-10-30&quantity=2
```

### Response (Available):
```json
{
  "available": true,
  "can_proceed": true,
  "available_units": 8,
  "total_units": 10,
  "booked_units": 2,
  "requested_quantity": 2,
  "message": "✅ Available! 8 of 10 units free for your dates.",
  "dates": {
    "start_date": "2025-10-28",
    "end_date": "2025-10-30",
    "total_days": 3
  },
  "price_estimate": {
    "daily_rate": "225.00",
    "quantity": 2,
    "total_days": 3,
    "subtotal": "1350.00",
    "delivery_fee": "50.00",
    "insurance_fee": "67.50",
    "total_amount": "1467.50",
    "currency": "AED"
  },
  "next_step": "Proceed to fill out booking details"
}
```

### Response (Not Available):
```json
{
  "available": false,
  "can_proceed": false,
  "available_units": 1,
  "total_units": 10,
  "booked_units": 9,
  "requested_quantity": 2,
  "message": "⚠️ Only 1 unit(s) available. You requested 2.",
  "dates": {
    "start_date": "2025-10-28",
    "end_date": "2025-10-30",
    "total_days": 3
  },
  "price_estimate": {
    "daily_rate": "225.00",
    "quantity": 2,
    "total_days": 3,
    "subtotal": "1350.00",
    "delivery_fee": "50.00",
    "insurance_fee": "67.50",
    "total_amount": "1467.50",
    "currency": "AED"
  },
  "next_step": "Try different dates or reduce quantity"
}
```

### Response (Equipment Unavailable):
```json
{
  "available": false,
  "available_units": 0,
  "total_units": 10,
  "booked_units": 0,
  "message": "This equipment is currently under maintenance",
  "can_proceed": false
}
```

---

## 🎨 React Native Implementation

### Full Booking Flow Component:

```tsx
import React, { useState, useEffect } from 'react';
import { View, Text, Button, ActivityIndicator, StyleSheet } from 'react-native';
import DatePicker from 'react-native-date-picker';

const EquipmentBookingScreen = ({ route }) => {
  const { equipmentId, equipmentName } = route.params;
  
  const [step, setStep] = useState(1); // 1: Dates, 2: Booking Form
  const [startDate, setStartDate] = useState(new Date());
  const [endDate, setEndDate] = useState(new Date(Date.now() + 3 * 24 * 60 * 60 * 1000));
  const [quantity, setQuantity] = useState(1);
  const [availability, setAvailability] = useState(null);
  const [checking, setChecking] = useState(false);
  
  const checkAvailability = async () => {
    setChecking(true);
    
    const startStr = startDate.toISOString().split('T')[0];
    const endStr = endDate.toISOString().split('T')[0];
    
    try {
      const response = await fetch(
        `${API_URL}/api/equipment/equipment/${equipmentId}/check_availability/?` +
        `start_date=${startStr}&end_date=${endStr}&quantity=${quantity}`,
        {
          headers: {
            'Authorization': `Bearer ${accessToken}`,
          }
        }
      );
      
      const data = await response.json();
      setAvailability(data);
    } catch (error) {
      console.error('Availability check failed:', error);
    } finally {
      setChecking(false);
    }
  };
  
  // Auto-check when dates/quantity change
  useEffect(() => {
    const timer = setTimeout(() => {
      checkAvailability();
    }, 500); // Debounce for 500ms
    
    return () => clearTimeout(timer);
  }, [startDate, endDate, quantity]);
  
  if (step === 1) {
    // Step 1: Date & Quantity Selection
    return (
      <View style={styles.container}>
        <Text style={styles.title}>Book {equipmentName}</Text>
        
        {/* Date Pickers */}
        <View style={styles.section}>
          <Text style={styles.label}>Start Date</Text>
          <DatePicker
            date={startDate}
            onDateChange={setStartDate}
            mode="date"
            minimumDate={new Date()}
          />
        </View>
        
        <View style={styles.section}>
          <Text style={styles.label}>End Date</Text>
          <DatePicker
            date={endDate}
            onDateChange={setEndDate}
            mode="date"
            minimumDate={startDate}
          />
        </View>
        
        {/* Quantity Selector */}
        <View style={styles.section}>
          <Text style={styles.label}>Quantity</Text>
          <View style={styles.quantitySelector}>
            <Button title="-" onPress={() => setQuantity(Math.max(1, quantity - 1))} />
            <Text style={styles.quantityText}>{quantity}</Text>
            <Button title="+" onPress={() => setQuantity(quantity + 1)} />
          </View>
        </View>
        
        {/* Availability Status */}
        {checking ? (
          <ActivityIndicator size="large" color="#007AFF" />
        ) : availability && (
          <View style={[
            styles.availabilityCard,
            { backgroundColor: availability.available ? '#D1FAE5' : '#FEE2E2' }
          ]}>
            <Text style={styles.availabilityMessage}>{availability.message}</Text>
            
            <View style={styles.detailsRow}>
              <Text>📅 {availability.dates.total_days} days</Text>
              <Text>📦 {availability.available_units}/{availability.total_units} units</Text>
            </View>
            
            <Text style={styles.priceText}>
              💰 Total: AED {availability.price_estimate.total_amount}
            </Text>
            
            {availability.available ? (
              <Button
                title="✅ Continue to Booking"
                onPress={() => setStep(2)}
                color="#10B981"
              />
            ) : (
              <Text style={styles.errorText}>
                {availability.next_step}
              </Text>
            )}
          </View>
        )}
      </View>
    );
  }
  
  // Step 2: Booking Form (only shown if available)
  return (
    <BookingFormComponent
      equipmentId={equipmentId}
      startDate={startDate}
      endDate={endDate}
      quantity={quantity}
      priceEstimate={availability.price_estimate}
      onBack={() => setStep(1)}
    />
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: '#fff',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
  },
  section: {
    marginBottom: 20,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
  },
  quantitySelector: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 16,
  },
  quantityText: {
    fontSize: 24,
    fontWeight: 'bold',
    minWidth: 40,
    textAlign: 'center',
  },
  availabilityCard: {
    padding: 16,
    borderRadius: 12,
    marginTop: 20,
  },
  availabilityMessage: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 12,
  },
  detailsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  priceText: {
    fontSize: 20,
    fontWeight: 'bold',
    marginVertical: 12,
  },
  errorText: {
    color: '#DC2626',
    fontSize: 14,
    marginTop: 8,
  },
});

export default EquipmentBookingScreen;
```

---

## 🎯 Benefits of This Approach

### ✅ Better User Experience
- **Instant feedback** - Customer knows availability before filling form
- **No wasted time** - Don't fill out form only to get rejected
- **Clear pricing** - See estimated cost upfront
- **Smart suggestions** - Show alternative quantities if not available

### ✅ Better Business
- **Reduced cart abandonment** - Customers only proceed if available
- **Fewer support tickets** - Clear availability messaging
- **Higher conversion** - Smooth, transparent booking flow

### ✅ Technical Benefits
- **Fast API** - Simple GET request, no database writes
- **Cacheable** - Can cache results for same dates/quantity
- **Parallel calls** - Check multiple equipment simultaneously
- **No permissions** - Public endpoint, works for all users

---

## 🔄 Complete Booking Flow

```
1. Customer views equipment detail page
   ↓
2. Selects dates and quantity
   ↓
3. API checks availability in real-time
   ↓
4. IF AVAILABLE:
   - Show green success message
   - Display price estimate
   - Show "Continue to Booking" button
   ↓
5. Customer clicks "Continue"
   ↓
6. Show booking form (delivery address, contact info, notes)
   ↓
7. Submit booking
   ↓
8. Backend validates again (double-check)
   ↓
9. Create rental request

   IF NOT AVAILABLE:
   - Show orange/red warning
   - Suggest: "Try different dates" or "Reduce quantity"
   - Show how many units are available
   - Allow customer to adjust and re-check
```

---

## 🧪 Testing Examples

### Test 1: Available Equipment
```bash
curl "http://localhost:8000/api/equipment/equipment/1/check_availability/?start_date=2025-11-10&end_date=2025-11-15&quantity=2"
```

### Test 2: Partially Booked
```bash
curl "http://localhost:8000/api/equipment/equipment/1/check_availability/?start_date=2025-10-28&end_date=2025-10-30&quantity=5"
```

### Test 3: Fully Booked
```bash
curl "http://localhost:8000/api/equipment/equipment/1/check_availability/?start_date=2025-10-28&end_date=2025-10-30&quantity=20"
```

### Test 4: Invalid Dates
```bash
curl "http://localhost:8000/api/equipment/equipment/1/check_availability/?start_date=2025-10-30&end_date=2025-10-28&quantity=1"
# Error: End date must be after start date
```

---

## 🎨 UI/UX Recommendations

### Availability States:

**✅ Fully Available** (Green)
```
✅ Great news! All 10 units are available for your dates.
📅 3 days | 💰 AED 1,467.50

[Continue to Booking →]
```

**⚠️ Limited Availability** (Orange)
```
⚠️ Only 2 units available. You requested 5.
📅 3 days | 💰 AED 1,467.50

[Adjust Quantity] [Try Different Dates]
```

**❌ Not Available** (Red)
```
❌ Sorry, all units are booked for these dates.
Try dates after November 6th

[Try Different Dates]
```

---

## 🚀 Performance Tips

1. **Debounce** - Wait 500ms after date change before checking
2. **Cache** - Store results for 30 seconds to avoid duplicate checks
3. **Loading state** - Show spinner while checking
4. **Error handling** - Handle network failures gracefully
5. **Offline support** - Show cached results if available

---

That's it! Your customers now get instant feedback on availability before wasting time on booking forms! 🎉
