# 📈 Revenue Trends API - Line Chart Data

## ✅ New Endpoint Added

### **URL:**
```
GET /api/rentals/rentals/revenue_trends/
```

### **Purpose:**
Provides time-series revenue data for line charts showing revenue trends over time.

---

## 📊 Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `period` | string | `daily` | Time grouping: `daily`, `weekly`, or `monthly` |
| `days` | integer | Varies | Number of days to show (30 for daily, 84 for weekly, 365 for monthly) |

---

## 🎯 Response Structure

```json
{
  "period": "daily",
  "days": 30,
  "data": [
    {
      "date": "2025-10-08",
      "label": "Oct 08",
      "sales": 1,
      "revenue": 2350.0,
      "commission": 235.0,
      "payout": 2115.0
    },
    {
      "date": "2025-10-10",
      "label": "Oct 10",
      "sales": 2,
      "revenue": 4200.0,
      "commission": 420.0,
      "payout": 3780.0
    }
    // ... more data points
  ],
  "summary": {
    "total_sales": 15,
    "total_revenue": 35000.0,
    "total_commission": 3500.0,
    "total_payout": 31500.0,
    "average_daily": 1050.0
  }
}
```

---

## 📋 Data Fields

### Main Response:
- `period`: The grouping period used (`daily`, `weekly`, `monthly`)
- `days`: Number of days included in the dataset
- `data`: Array of data points for the chart
- `summary`: Aggregated totals for the period

### Data Point Fields:
| Field | Type | Description |
|-------|------|-------------|
| `date` | string | ISO date (YYYY-MM-DD) for x-axis |
| `label` | string | Formatted label ("Nov 04", "Week of Nov 04", "November 2025") |
| `sales` | integer | Number of completed rentals on this date |
| `revenue` | float | Total customer payments (AED) |
| `commission` | float | Platform commission (10% of revenue) |
| `payout` | float | **Seller earnings** (90% of revenue) |

---

## 💡 Usage Examples

### **1. Daily Trends (Last 30 Days)**
```http
GET /api/rentals/rentals/revenue_trends/
GET /api/rentals/rentals/revenue_trends/?period=daily&days=30
```

**Response:**
```json
{
  "period": "daily",
  "days": 30,
  "data": [
    {"date": "2025-10-08", "label": "Oct 08", "sales": 1, "revenue": 2350.0, "payout": 2115.0},
    {"date": "2025-10-10", "label": "Oct 10", "sales": 2, "revenue": 4200.0, "payout": 3780.0}
  ],
  "summary": {
    "total_sales": 15,
    "total_revenue": 35000.0,
    "total_payout": 31500.0,
    "average_daily": 1050.0
  }
}
```

### **2. Weekly Trends (Last 12 Weeks)**
```http
GET /api/rentals/rentals/revenue_trends/?period=weekly&days=84
```

**Response:**
```json
{
  "period": "weekly",
  "days": 84,
  "data": [
    {"date": "2025-09-02", "label": "Week of Sep 02", "sales": 5, "revenue": 12000.0, "payout": 10800.0},
    {"date": "2025-09-09", "label": "Week of Sep 09", "sales": 8, "revenue": 18500.0, "payout": 16650.0}
  ]
}
```

### **3. Monthly Trends (Last 12 Months)**
```http
GET /api/rentals/rentals/revenue_trends/?period=monthly&days=365
```

**Response:**
```json
{
  "period": "monthly",
  "days": 365,
  "data": [
    {"date": "2025-01-01", "label": "January 2025", "sales": 45, "revenue": 125000.0, "payout": 112500.0},
    {"date": "2025-02-01", "label": "February 2025", "sales": 52, "revenue": 148000.0, "payout": 133200.0}
  ]
}
```

---

## 🎨 Frontend Integration (React/Vue/Angular)

### **Chart.js Example:**
```javascript
// Fetch data
const response = await fetch('/api/rentals/rentals/revenue_trends/?period=daily&days=30', {
  headers: { 'Authorization': `Bearer ${token}` }
})
const trendsData = await response.json()

// Configure Chart.js
const chartConfig = {
  type: 'line',
  data: {
    labels: trendsData.data.map(d => d.label),  // ["Nov 01", "Nov 02", ...]
    datasets: [
      {
        label: 'Your Earnings (AED)',
        data: trendsData.data.map(d => d.payout),  // Seller's actual income
        borderColor: '#4CAF50',
        backgroundColor: 'rgba(76, 175, 80, 0.1)',
        tension: 0.4,
        fill: true
      },
      {
        label: 'Total Revenue (AED)',
        data: trendsData.data.map(d => d.revenue),  // Customer payments
        borderColor: '#2196F3',
        backgroundColor: 'rgba(33, 150, 243, 0.1)',
        tension: 0.4,
        fill: true
      },
      {
        label: 'Platform Fee (AED)',
        data: trendsData.data.map(d => d.commission),
        borderColor: '#FF9800',
        backgroundColor: 'rgba(255, 152, 0, 0.1)',
        tension: 0.4,
        fill: false,
        borderDash: [5, 5]  // Dashed line
      }
    ]
  },
  options: {
    responsive: true,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: (value) => `AED ${value.toLocaleString()}`
        }
      }
    },
    plugins: {
      tooltip: {
        callbacks: {
          label: (context) => {
            return `${context.dataset.label}: AED ${context.parsed.y.toLocaleString()}`
          }
        }
      }
    }
  }
}

// Create chart
new Chart(document.getElementById('revenueChart'), chartConfig)
```

### **Minimal Example (Single Line):**
```javascript
// Just show seller earnings
const trendsData = await fetch('/api/rentals/rentals/revenue_trends/').then(r => r.json())

const chartConfig = {
  type: 'line',
  data: {
    labels: trendsData.data.map(d => d.label),
    datasets: [{
      label: 'Your Earnings (AED)',
      data: trendsData.data.map(d => d.payout),
      borderColor: '#4CAF50',
      tension: 0.4
    }]
  }
}
```

---

## 📊 Sample Dashboard Layout

```
╔════════════════════════════════════════════════════════════════╗
║                    REVENUE TRENDS (30 DAYS)                    ║
║                                                                ║
║  Your Earnings: AED 31,500  •  Avg/Day: AED 1,050             ║
║                                                                ║
║  [Line Chart: Payout over Time]                               ║
║                                                                ║
║  AED                                                           ║
║  5000 ┤                                        ╭──●            ║
║  4000 ┤                    ●───╮              │                ║
║  3000 ┤          ●───╮     │    ╰──●──╮      │                ║
║  2000 ┤     ●───╯     ╰───╯            ╰──●──╯                ║
║  1000 ┤ ●──╯                                                   ║
║     0 ┼────┬────┬────┬────┬────┬────┬────┬────┬────┬────      ║
║          Nov  Nov  Nov  Nov  Nov  Nov  Nov  Nov  Nov  Nov    ║
║           01   05   09   13   17   21   25   29   02   06    ║
║                                                                ║
║  Period: [Daily ▼]  Days: [30 ▼]  [Refresh]                  ║
╚════════════════════════════════════════════════════════════════╝

Legend:
  ─── Your Earnings (green)
  ─── Total Revenue (blue)
  ┄┄┄ Platform Fee (orange, dashed)
```

---

## 🔧 Implementation Details

### **Database Query:**
```python
# Groups sales by day/week/month
queryset.annotate(
    period=TruncDate('sale_date')  # or TruncWeek, TruncMonth
).values('period').annotate(
    sales=Count('id'),
    revenue=Sum('total_revenue'),
    commission=Sum('platform_commission_amount'),
    payout=Sum('seller_payout')
).order_by('period')
```

### **Label Formatting:**
```python
def _format_period_label(self, date, period):
    if period == 'daily':
        return date.strftime('%b %d')  # "Nov 04"
    elif period == 'weekly':
        return date.strftime('Week of %b %d')  # "Week of Nov 04"
    else:  # monthly
        return date.strftime('%B %Y')  # "November 2025"
```

---

## 🎯 Key Insights

### **What Sellers See:**
- **Payout Line** (green): Money they'll receive (90% of revenue)
- **Revenue Line** (blue): What customers paid
- **Commission Line** (orange): Platform fee (10%)

### **Growth Patterns:**
- Upward trend = Business growing
- Flat line = Stable revenue
- Downward trend = Need marketing/promotions
- Spikes = Seasonal demand or successful campaigns

---

## 📱 Mobile Optimization

### **Responsive Chart:**
```javascript
const isMobile = window.innerWidth < 768

const chartConfig = {
  // ... other options
  options: {
    maintainAspectRatio: !isMobile,
    aspectRatio: isMobile ? 1 : 2,
    scales: {
      x: {
        ticks: {
          maxRotation: isMobile ? 45 : 0,
          autoSkip: true,
          maxTicksLimit: isMobile ? 7 : 30
        }
      }
    }
  }
}
```

---

## ⚠️ Important Notes

1. **Seller Filtering**: Automatically shows only seller's own data
2. **Date Range**: Defaults to sensible ranges (30/84/365 days)
3. **Empty Data**: Returns empty array if no sales in period
4. **Currency**: All amounts in AED (UAE Dirham)
5. **Timezone**: Uses server timezone (UTC for Azure)

---

## 🧪 Testing

### **With Current Data:**
```bash
# You currently have 1 sale, so trends will show 1 data point
curl -H "Authorization: Bearer $TOKEN" \
  "https://your-api.azurewebsites.net/api/rentals/rentals/revenue_trends/"
```

### **After More Sales:**
Once you have more completed rentals with varying dates, the trend line will show meaningful patterns.

---

**Status**: ✅ API Endpoint Ready  
**Location**: `rentals/views.py` line ~898  
**Added**: November 4, 2025  
**Version**: 1.0
