# Revenue API Response Fields

## Issue: Average Rental Value showing as Zero

### Backend Calculation (rentals/views.py line 812):
```python
'average_payout': float(overall_stats['total_payout'] / overall_stats['total_sales']) if overall_stats['total_sales'] > 0 else 0.0
```

**With current data (2 sales):**
- Total Payout: AED 5,706
- Total Sales: 2
- **Average Payout: AED 2,853** ✅

---

## API Response Structure

### GET /api/rentals/rentals/revenue_summary/

```json
{
  "overview": {
    "total_sales": 2,
    "total_revenue": 6340.0,
    "total_commission": 634.0,
    "total_payout": 5706.0,
    "average_payout": 2853.0,          ⬅️ THIS IS THE FIELD
    "average_rental_days": 4.5
  },
  "this_month": {
    "sales": 2,
    "revenue": 6340.0,
    "commission": 634.0,
    "payout": 5706.0
  },
  "last_month": {
    "sales": 0,
    "revenue": 0.0,
    "commission": 0.0,
    "payout": 0.0
  },
  "this_year": {
    "sales": 2,
    "revenue": 6340.0,
    "commission": 634.0,
    "payout": 5706.0
  },
  "all_time": {
    "total_sales": 2,
    "total_revenue": 6340.0,
    "total_commission": 634.0,
    "total_payout": 5706.0,
    "average_payout": 2853.0,          ⬅️ ALSO HERE
    "average_rental_days": 4.5
  },
  "growth": {
    "revenue_percentage": 0.0,
    "payout_percentage": 0.0,
    "sales_percentage": 0.0
  },
  "pending_payouts": {
    "count": 0,
    "amount": 0.0
  }
}
```

---

## Frontend Mapping

### Correct Field Access:

```javascript
// ✅ CORRECT - Access from overview or all_time
const avgPayout = response.data.overview.average_payout;  // 2853.0
const avgPayoutAllTime = response.data.all_time.average_payout;  // 2853.0

// ✅ CORRECT - Format for display
const formattedAvg = `AED ${avgPayout.toLocaleString()}`;  // "AED 2,853"

// ❌ WRONG - These don't exist
const wrong1 = response.data.average_value;  // undefined
const wrong2 = response.data.overview.avg_sale;  // undefined  
const wrong3 = response.data.average_rental_value;  // undefined
```

---

## Common Frontend Issues

### Issue 1: Wrong field path
```javascript
// ❌ WRONG
const avg = data.average_payout;  // undefined

// ✅ CORRECT
const avg = data.overview.average_payout;  // 2853.0
```

### Issue 2: Division by zero check missing
```javascript
// ❌ WRONG - No safety check
const avg = totalPayout / totalSales;  // Could be 0/0 = NaN

// ✅ CORRECT - Backend already handles this
const avg = response.data.overview.average_payout;  // 0.0 if no sales
```

### Issue 3: Type coercion
```javascript
// ❌ WRONG - Treating as string
const avg = "0";  // Always shows 0

// ✅ CORRECT - Use numeric value from API
const avg = response.data.overview.average_payout;  // 2853.0
```

---

## Debugging Steps

### 1. Check API Response
```javascript
const response = await fetch('/api/rentals/rentals/revenue_summary/', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const data = await response.json();

console.log('Full Response:', data);
console.log('Average Payout:', data.overview.average_payout);
```

### 2. Verify Data Path
```javascript
// Log the entire overview object
console.log('Overview:', data.overview);

// Check if field exists
if (data.overview && data.overview.average_payout !== undefined) {
  console.log('✅ Average Payout Found:', data.overview.average_payout);
} else {
  console.log('❌ Average Payout Missing');
}
```

### 3. Check for NaN or undefined
```javascript
const avg = data.overview.average_payout;
console.log('Type:', typeof avg);  // Should be "number"
console.log('Value:', avg);         // Should be 2853.0
console.log('Is NaN?:', isNaN(avg));  // Should be false
console.log('Is Zero?:', avg === 0);  // Should be false
```

---

## Correct Frontend Implementation

### React Example:
```jsx
const DashboardMetrics = () => {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    const fetchData = async () => {
      const response = await fetch('/api/rentals/rentals/revenue_summary/', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      const json = await response.json();
      setData(json);
    };
    fetchData();
  }, []);
  
  if (!data) return <div>Loading...</div>;
  
  return (
    <div>
      <div className="metric">
        <span>Average Payout</span>
        <strong>AED {data.overview.average_payout.toLocaleString()}</strong>
      </div>
      <div className="metric">
        <span>Average Rental Days</span>
        <strong>{data.overview.average_rental_days} days</strong>
      </div>
    </div>
  );
};
```

### Vue Example:
```vue
<template>
  <div>
    <div class="metric">
      <span>Average Payout</span>
      <strong>AED {{ overview.average_payout.toLocaleString() }}</strong>
    </div>
    <div class="metric">
      <span>Average Rental Days</span>
      <strong>{{ overview.average_rental_days }} days</strong>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      overview: null
    }
  },
  async mounted() {
    const response = await fetch('/api/rentals/rentals/revenue_summary/', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    });
    const data = await response.json();
    this.overview = data.overview;
  }
}
</script>
```

---

## Summary

**Expected Values (Current Data):**
- ✅ `overview.average_payout` = **2853.0** (AED 2,853)
- ✅ `overview.average_rental_days` = **4.5** days
- ✅ `overview.total_payout` = **5706.0** (AED 5,706)
- ✅ `overview.total_sales` = **2**

**Common Frontend Mistakes:**
1. ❌ Looking for `data.average_value` instead of `data.overview.average_payout`
2. ❌ Hardcoding `0` in the component
3. ❌ Not checking if API call succeeded
4. ❌ Wrong data path in mapping

**Quick Fix:**
```javascript
// Replace this:
const avg = data.average_rental_value || 0;  // ❌ WRONG

// With this:
const avg = data?.overview?.average_payout || 0;  // ✅ CORRECT
```

---

**Last Updated:** November 4, 2025  
**Current Database:** 2 sales, AED 5,706 total payout, AED 2,853 average
