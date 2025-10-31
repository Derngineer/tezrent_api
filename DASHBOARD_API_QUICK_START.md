# Dashboard API Quick Reference

## Dashboard Summary Endpoint

**Purpose:** Get all key metrics for the main dashboard page in a single API call.

### Endpoint
```
GET /api/rentals/rentals/dashboard_summary/
```

### Authentication
Required: Bearer token

### What You Get

1. **Total Equipment** - Count of all active equipment
2. **Active Rentals** - Currently ongoing rentals  
3. **Pending Approvals** - Rentals awaiting seller approval
4. **Monthly Revenue** - Revenue from completed rentals this month
5. **Revenue Growth** - Month-over-month comparison
6. **Equipment by Category** - Top 5 categories
7. **Top Equipment** - Most rented items
8. **Recent Activity** - Last 5 rental transactions
9. **Pending Payouts** - Seller payouts awaiting processing

### Quick Integration

```javascript
// Fetch dashboard data
const response = await fetch(
  'http://localhost:8000/api/rentals/rentals/dashboard_summary/',
  {
    headers: {
      'Authorization': `Bearer ${accessToken}`,
    },
  }
);

const data = await response.json();

// Use the data
console.log(`Total Equipment: ${data.summary.total_equipment}`);
console.log(`Active Rentals: ${data.summary.active_rentals}`);
console.log(`Pending Approvals: ${data.summary.pending_approvals}`);
console.log(`Monthly Revenue: ${data.summary.monthly_revenue}`);
```

### Response Example

```json
{
  "summary": {
    "total_equipment": 4,
    "active_rentals": 1,
    "pending_approvals": 0,
    "monthly_revenue": 1825.00
  },
  "monthly_stats": {
    "revenue": 1825.00,
    "commission": 182.50,
    "sales_count": 1,
    "revenue_growth_percentage": 0.0,
    "sales_growth_percentage": 0.0
  },
  "comparison": {
    "this_month": {
      "revenue": 1825.00,
      "sales": 1
    },
    "last_month": {
      "revenue": 0.0,
      "sales": 0
    }
  },
  "platform_stats": {
    "total_rentals": 5,
    "completed_rentals": 1,
    "completion_rate": 20.0
  },
  "equipment_by_category": [
    {
      "category__name": "Construction Equipment",
      "count": 2
    }
  ],
  "top_equipment": [
    {
      "equipment__name": "Bobcat S570",
      "equipment__id": 1,
      "rental_count": 1,
      "total_revenue": 1825.00
    }
  ],
  "recent_activity": [
    {
      "id": 1,
      "rental_reference": "RNT2B915512",
      "equipment__name": "Bobcat S570",
      "customer__user__username": "john_customer",
      "status": "completed",
      "total_amount": 1825.00,
      "created_at": "2024-10-25T10:30:00Z"
    }
  ],
  "pending_payouts": {
    "count": 1,
    "total_amount": 1642.50
  }
}
```

## Related Endpoints

These endpoints also exist and can be used individually:

### 1. Active Rentals
```
GET /api/rentals/rentals/active_rentals/
```
Returns list of currently active rentals.

### 2. Pending Approvals  
```
GET /api/rentals/rentals/pending_approvals/
```
Returns rentals awaiting seller approval.

### 3. Revenue Summary
```
GET /api/rentals/rentals/revenue_summary/
```
Detailed financial analytics with monthly comparisons.

### 4. Transactions
```
GET /api/rentals/rentals/transactions/
```
Complete transaction history with filtering.

### 5. Equipment List
```
GET /api/equipment/equipment/
```
All equipment with filtering and search.

## Display the Data

### Main Dashboard Cards

```jsx
<div className="dashboard-cards">
  <div className="card">
    <h3>📦 Total Equipment</h3>
    <p className="value">{data.summary.total_equipment}</p>
  </div>
  
  <div className="card">
    <h3>🔄 Active Rentals</h3>
    <p className="value">{data.summary.active_rentals}</p>
  </div>
  
  <div className="card">
    <h3>⏳ Pending Approvals</h3>
    <p className="value">{data.summary.pending_approvals}</p>
  </div>
  
  <div className="card highlight">
    <h3>💰 Monthly Revenue</h3>
    <p className="value">AED {data.summary.monthly_revenue.toFixed(2)}</p>
    <small>{data.monthly_stats.revenue_growth_percentage}% vs last month</small>
  </div>
</div>
```

### View Analytics Link

```jsx
<button onClick={() => navigate('/analytics')}>
  📊 View Detailed Analytics
</button>
```

## Testing

```bash
# Test with cURL
curl -X GET \
  'http://localhost:8000/api/rentals/rentals/dashboard_summary/' \
  -H 'Authorization: Bearer YOUR_TOKEN'
```

## Full Documentation

For complete implementation with React, Vue, and React Native examples:
- See `DASHBOARD_SUMMARY_GUIDE.md`
- For financial integration: `FINANCIALS_INTEGRATION_GUIDE.md`
- For main API docs: `MASTER_API_DOCUMENTATION.md`
