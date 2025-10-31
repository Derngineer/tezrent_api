# Financial Section Integration Guide

## Overview

This guide shows you how to integrate the **Revenue** and **Transactions** sections in your financial dashboard using the new sales tracking APIs.

---

## 🎯 Available Endpoints

### 1. Revenue Summary
```http
GET /api/rentals/rentals/revenue_summary/
Authorization: Bearer {token}
```

### 2. Sales List (with filters)
```http
GET /api/rentals/rentals/sales/
Authorization: Bearer {token}
```

### 3. Transactions
```http
GET /api/rentals/rentals/transactions/
Authorization: Bearer {token}
```

---

## 📊 Revenue Section Integration

### Endpoint Response

```http
GET /api/rentals/rentals/revenue_summary/
```

**Response:**
```json
{
  "overview": {
    "total_sales": 150,
    "total_revenue": 750000.00,
    "total_commission": 75000.00,
    "total_payout": 675000.00,
    "average_sale_value": 5000.00,
    "average_rental_days": 5.2
  },
  "this_month": {
    "sales": 45,
    "revenue": 225000.00,
    "payout": 202500.00
  },
  "last_month": {
    "sales": 38,
    "revenue": 190000.00,
    "payout": 171000.00
  },
  "this_year": {
    "sales": 450,
    "revenue": 2250000.00,
    "payout": 2025000.00
  },
  "growth": {
    "revenue_percentage": 18.42,
    "sales_percentage": 18.42
  },
  "pending_payouts": {
    "count": 12,
    "amount": 54000.00
  }
}
```

### Frontend Implementation (React/Vue/Angular)

#### React Example:

```jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const RevenueSection = () => {
  const [revenue, setRevenue] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRevenueSummary();
  }, []);

  const fetchRevenueSummary = async () => {
    try {
      const response = await axios.get(
        '/api/rentals/rentals/revenue_summary/',
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );
      setRevenue(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching revenue:', error);
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="revenue-section">
      {/* Overview Cards */}
      <div className="revenue-cards">
        <div className="card">
          <h3>Total Sales</h3>
          <p className="value">{revenue.overview.total_sales}</p>
        </div>
        
        <div className="card">
          <h3>Total Revenue</h3>
          <p className="value">
            AED {revenue.overview.total_revenue.toLocaleString()}
          </p>
        </div>
        
        <div className="card">
          <h3>Your Earnings</h3>
          <p className="value">
            AED {revenue.overview.total_payout.toLocaleString()}
          </p>
          <small>After {revenue.overview.total_commission.toLocaleString()} commission</small>
        </div>
        
        <div className="card">
          <h3>Average Sale</h3>
          <p className="value">
            AED {revenue.overview.average_sale_value.toLocaleString()}
          </p>
        </div>
      </div>

      {/* Monthly Comparison */}
      <div className="monthly-stats">
        <h3>This Month vs Last Month</h3>
        <div className="comparison">
          <div className="month">
            <h4>This Month</h4>
            <p>Sales: {revenue.this_month.sales}</p>
            <p>Revenue: AED {revenue.this_month.revenue.toLocaleString()}</p>
            <p>Earnings: AED {revenue.this_month.payout.toLocaleString()}</p>
          </div>
          
          <div className="month">
            <h4>Last Month</h4>
            <p>Sales: {revenue.last_month.sales}</p>
            <p>Revenue: AED {revenue.last_month.revenue.toLocaleString()}</p>
            <p>Earnings: AED {revenue.last_month.payout.toLocaleString()}</p>
          </div>
          
          <div className="growth">
            <h4>Growth</h4>
            <p className={revenue.growth.revenue_percentage > 0 ? 'positive' : 'negative'}>
              {revenue.growth.revenue_percentage > 0 ? '↑' : '↓'} 
              {Math.abs(revenue.growth.revenue_percentage)}% Revenue
            </p>
            <p className={revenue.growth.sales_percentage > 0 ? 'positive' : 'negative'}>
              {revenue.growth.sales_percentage > 0 ? '↑' : '↓'} 
              {Math.abs(revenue.growth.sales_percentage)}% Sales
            </p>
          </div>
        </div>
      </div>

      {/* Pending Payouts Alert */}
      {revenue.pending_payouts.count > 0 && (
        <div className="pending-payouts alert">
          <h4>⏳ Pending Payouts</h4>
          <p>
            {revenue.pending_payouts.count} transactions pending
          </p>
          <p className="amount">
            AED {revenue.pending_payouts.amount.toLocaleString()}
          </p>
        </div>
      )}

      {/* Year to Date */}
      <div className="ytd-summary">
        <h3>Year to Date</h3>
        <p>Total Sales: {revenue.this_year.sales}</p>
        <p>Total Revenue: AED {revenue.this_year.revenue.toLocaleString()}</p>
        <p>Your Earnings: AED {revenue.this_year.payout.toLocaleString()}</p>
      </div>
    </div>
  );
};

export default RevenueSection;
```

#### Vue Example:

```vue
<template>
  <div class="revenue-section">
    <div v-if="loading">Loading...</div>
    
    <div v-else>
      <!-- Overview Cards -->
      <div class="revenue-cards">
        <div class="card">
          <h3>Total Sales</h3>
          <p class="value">{{ revenue.overview.total_sales }}</p>
        </div>
        
        <div class="card">
          <h3>Total Revenue</h3>
          <p class="value">AED {{ formatNumber(revenue.overview.total_revenue) }}</p>
        </div>
        
        <div class="card">
          <h3>Your Earnings</h3>
          <p class="value">AED {{ formatNumber(revenue.overview.total_payout) }}</p>
        </div>
      </div>

      <!-- Growth Indicators -->
      <div class="growth-section">
        <div :class="['growth-badge', revenue.growth.revenue_percentage > 0 ? 'positive' : 'negative']">
          <span>{{ revenue.growth.revenue_percentage > 0 ? '↑' : '↓' }}</span>
          {{ Math.abs(revenue.growth.revenue_percentage) }}% Revenue
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RevenueSection',
  data() {
    return {
      revenue: null,
      loading: true
    }
  },
  mounted() {
    this.fetchRevenueSummary();
  },
  methods: {
    async fetchRevenueSummary() {
      try {
        const response = await this.$axios.get('/api/rentals/rentals/revenue_summary/');
        this.revenue = response.data;
        this.loading = false;
      } catch (error) {
        console.error('Error:', error);
        this.loading = false;
      }
    },
    formatNumber(num) {
      return new Intl.NumberFormat('en-AE').format(num);
    }
  }
}
</script>
```

---

## 💳 Transactions Section Integration

### Endpoint Response

```http
GET /api/rentals/rentals/transactions/
GET /api/rentals/rentals/transactions/?payout_status=pending
GET /api/rentals/rentals/transactions/?start_date=2025-01-01&end_date=2025-01-31
```

**Response:**
```json
{
  "count": 45,
  "totals": {
    "revenue": 225000.00,
    "commission": 22500.00,
    "payout": 202500.00
  },
  "results": [
    {
      "id": 1,
      "rental_reference": "RENT-2025-001",
      "seller_name": "Equipment Masters LLC",
      "customer_name": "John Doe",
      "equipment_name": "Hydraulic Excavator CAT 320D",
      "equipment_category": "Construction Equipment",
      
      "total_revenue": "5000.00",
      "subtotal": "4500.00",
      "delivery_fee": "300.00",
      "insurance_fee": "150.00",
      "late_fees": "50.00",
      "damage_fees": "0.00",
      
      "platform_commission_percentage": "10.00",
      "platform_commission_amount": "500.00",
      "seller_payout": "4500.00",
      
      "formatted_revenue": "AED 5,000.00",
      "formatted_commission": "AED 500.00",
      "formatted_payout": "AED 4,500.00",
      
      "rental_days": 7,
      "rental_start_date": "2025-01-15",
      "rental_end_date": "2025-01-22",
      "equipment_quantity": 1,
      
      "payout_status": "completed",
      "payout_status_display": "Paid Out",
      "payout_date": "2025-01-25T10:30:00Z",
      "payout_reference": "PAY-2025-12345",
      
      "sale_date": "2025-01-23T10:30:00Z",
      "created_at": "2025-01-23T10:30:00Z"
    }
  ]
}
```

### Frontend Implementation

#### React Example:

```jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const TransactionsSection = () => {
  const [transactions, setTransactions] = useState([]);
  const [totals, setTotals] = useState(null);
  const [filters, setFilters] = useState({
    payout_status: '',
    start_date: '',
    end_date: ''
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTransactions();
  }, [filters]);

  const fetchTransactions = async () => {
    try {
      const params = new URLSearchParams();
      if (filters.payout_status) params.append('payout_status', filters.payout_status);
      if (filters.start_date) params.append('start_date', filters.start_date);
      if (filters.end_date) params.append('end_date', filters.end_date);

      const response = await axios.get(
        `/api/rentals/rentals/transactions/?${params.toString()}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );
      
      setTransactions(response.data.results);
      setTotals(response.data.totals);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching transactions:', error);
      setLoading(false);
    }
  };

  const getStatusBadgeClass = (status) => {
    const statusClasses = {
      'pending': 'badge-warning',
      'processing': 'badge-info',
      'completed': 'badge-success',
      'failed': 'badge-danger',
      'on_hold': 'badge-secondary'
    };
    return statusClasses[status] || 'badge-default';
  };

  if (loading) return <div>Loading transactions...</div>;

  return (
    <div className="transactions-section">
      {/* Filters */}
      <div className="filters">
        <select 
          value={filters.payout_status}
          onChange={(e) => setFilters({...filters, payout_status: e.target.value})}
        >
          <option value="">All Statuses</option>
          <option value="pending">Pending</option>
          <option value="processing">Processing</option>
          <option value="completed">Completed</option>
          <option value="failed">Failed</option>
          <option value="on_hold">On Hold</option>
        </select>

        <input
          type="date"
          value={filters.start_date}
          onChange={(e) => setFilters({...filters, start_date: e.target.value})}
          placeholder="Start Date"
        />

        <input
          type="date"
          value={filters.end_date}
          onChange={(e) => setFilters({...filters, end_date: e.target.value})}
          placeholder="End Date"
        />

        <button onClick={() => setFilters({payout_status: '', start_date: '', end_date: ''})}>
          Clear Filters
        </button>
      </div>

      {/* Summary Totals */}
      {totals && (
        <div className="totals-summary">
          <div className="total-card">
            <span>Total Revenue:</span>
            <strong>AED {totals.revenue.toLocaleString()}</strong>
          </div>
          <div className="total-card">
            <span>Commission:</span>
            <strong>AED {totals.commission.toLocaleString()}</strong>
          </div>
          <div className="total-card">
            <span>Your Earnings:</span>
            <strong>AED {totals.payout.toLocaleString()}</strong>
          </div>
        </div>
      )}

      {/* Transactions Table */}
      <div className="transactions-table">
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Rental Ref</th>
              <th>Customer</th>
              <th>Equipment</th>
              <th>Duration</th>
              <th>Revenue</th>
              <th>Commission</th>
              <th>Your Earning</th>
              <th>Status</th>
              <th>Payout Date</th>
            </tr>
          </thead>
          <tbody>
            {transactions.map((transaction) => (
              <tr key={transaction.id}>
                <td>{new Date(transaction.sale_date).toLocaleDateString()}</td>
                <td>
                  <strong>{transaction.rental_reference}</strong>
                </td>
                <td>{transaction.customer_name}</td>
                <td>
                  <div className="equipment-cell">
                    <strong>{transaction.equipment_name}</strong>
                    <small>{transaction.equipment_category}</small>
                  </div>
                </td>
                <td>{transaction.rental_days} days</td>
                <td className="amount">{transaction.formatted_revenue}</td>
                <td className="amount commission">{transaction.formatted_commission}</td>
                <td className="amount payout">
                  <strong>{transaction.formatted_payout}</strong>
                </td>
                <td>
                  <span className={`badge ${getStatusBadgeClass(transaction.payout_status)}`}>
                    {transaction.payout_status_display}
                  </span>
                </td>
                <td>
                  {transaction.payout_date 
                    ? new Date(transaction.payout_date).toLocaleDateString()
                    : '-'
                  }
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Transaction Count */}
      <div className="transaction-count">
        Showing {transactions.length} transactions
      </div>
    </div>
  );
};

export default TransactionsSection;
```

#### Vue Example:

```vue
<template>
  <div class="transactions-section">
    <!-- Filters -->
    <div class="filters">
      <select v-model="filters.payout_status" @change="fetchTransactions">
        <option value="">All Statuses</option>
        <option value="pending">Pending</option>
        <option value="completed">Completed</option>
      </select>

      <input type="date" v-model="filters.start_date" @change="fetchTransactions" />
      <input type="date" v-model="filters.end_date" @change="fetchTransactions" />
    </div>

    <!-- Totals -->
    <div v-if="totals" class="totals">
      <div class="total-card">
        <span>Revenue:</span>
        <strong>AED {{ formatNumber(totals.revenue) }}</strong>
      </div>
      <div class="total-card">
        <span>Your Earnings:</span>
        <strong>AED {{ formatNumber(totals.payout) }}</strong>
      </div>
    </div>

    <!-- Table -->
    <table class="transactions-table">
      <thead>
        <tr>
          <th>Date</th>
          <th>Reference</th>
          <th>Customer</th>
          <th>Equipment</th>
          <th>Revenue</th>
          <th>Your Earning</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="tx in transactions" :key="tx.id">
          <td>{{ formatDate(tx.sale_date) }}</td>
          <td>{{ tx.rental_reference }}</td>
          <td>{{ tx.customer_name }}</td>
          <td>{{ tx.equipment_name }}</td>
          <td>{{ tx.formatted_revenue }}</td>
          <td class="payout">{{ tx.formatted_payout }}</td>
          <td>
            <span :class="['badge', getStatusClass(tx.payout_status)]">
              {{ tx.payout_status_display }}
            </span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
export default {
  name: 'TransactionsSection',
  data() {
    return {
      transactions: [],
      totals: null,
      filters: {
        payout_status: '',
        start_date: '',
        end_date: ''
      }
    }
  },
  mounted() {
    this.fetchTransactions();
  },
  methods: {
    async fetchTransactions() {
      try {
        const params = new URLSearchParams();
        if (this.filters.payout_status) params.append('payout_status', this.filters.payout_status);
        if (this.filters.start_date) params.append('start_date', this.filters.start_date);
        if (this.filters.end_date) params.append('end_date', this.filters.end_date);

        const response = await this.$axios.get(
          `/api/rentals/rentals/transactions/?${params.toString()}`
        );
        
        this.transactions = response.data.results;
        this.totals = response.data.totals;
      } catch (error) {
        console.error('Error:', error);
      }
    },
    formatNumber(num) {
      return new Intl.NumberFormat('en-AE').format(num);
    },
    formatDate(date) {
      return new Date(date).toLocaleDateString();
    },
    getStatusClass(status) {
      const classes = {
        'pending': 'badge-warning',
        'completed': 'badge-success',
        'failed': 'badge-danger'
      };
      return classes[status] || 'badge-default';
    }
  }
}
</script>
```

---

## 🎨 Sample CSS Styling

```css
/* Revenue Section */
.revenue-section {
  padding: 20px;
}

.revenue-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.revenue-cards .card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.revenue-cards .card h3 {
  font-size: 14px;
  color: #666;
  margin-bottom: 10px;
}

.revenue-cards .card .value {
  font-size: 28px;
  font-weight: bold;
  color: #333;
}

.monthly-stats {
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.comparison {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.growth .positive {
  color: #10b981;
}

.growth .negative {
  color: #ef4444;
}

.pending-payouts {
  background: #fef3c7;
  border: 1px solid #f59e0b;
  padding: 15px;
  border-radius: 8px;
  margin-top: 20px;
}

/* Transactions Section */
.transactions-section {
  padding: 20px;
}

.filters {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.filters select,
.filters input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.totals-summary {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
  margin-bottom: 20px;
}

.total-card {
  background: white;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.total-card span {
  display: block;
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.total-card strong {
  font-size: 20px;
  color: #333;
}

.transactions-table {
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.transactions-table table {
  width: 100%;
  border-collapse: collapse;
}

.transactions-table th {
  background: #f9fafb;
  padding: 12px;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #e5e7eb;
}

.transactions-table td {
  padding: 12px;
  border-bottom: 1px solid #f3f4f6;
}

.transactions-table .amount {
  font-family: monospace;
  text-align: right;
}

.transactions-table .payout {
  color: #10b981;
  font-weight: bold;
}

.transactions-table .commission {
  color: #ef4444;
}

.badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.badge-warning {
  background: #fef3c7;
  color: #92400e;
}

.badge-success {
  background: #d1fae5;
  color: #065f46;
}

.badge-info {
  background: #dbeafe;
  color: #1e40af;
}

.badge-danger {
  background: #fee2e2;
  color: #991b1b;
}

.badge-secondary {
  background: #f3f4f6;
  color: #4b5563;
}

.equipment-cell {
  display: flex;
  flex-direction: column;
}

.equipment-cell strong {
  font-size: 14px;
  color: #111827;
}

.equipment-cell small {
  font-size: 12px;
  color: #6b7280;
}
```

---

## 🔄 Real-time Updates

### Polling for New Transactions

```javascript
// Refresh revenue every 30 seconds
useEffect(() => {
  const interval = setInterval(() => {
    fetchRevenueSummary();
  }, 30000); // 30 seconds

  return () => clearInterval(interval);
}, []);
```

### Manual Refresh Button

```jsx
<button onClick={fetchTransactions} className="refresh-button">
  🔄 Refresh
</button>
```

---

## 📱 Mobile Responsive Design

```css
@media (max-width: 768px) {
  .revenue-cards {
    grid-template-columns: 1fr;
  }

  .comparison {
    grid-template-columns: 1fr;
  }

  .transactions-table {
    overflow-x: auto;
  }

  .transactions-table table {
    min-width: 800px;
  }
}
```

---

## 🚀 Quick Start Checklist

### Revenue Section:
- [ ] Create revenue component
- [ ] Fetch `/api/rentals/rentals/revenue_summary/`
- [ ] Display overview cards (total sales, revenue, earnings)
- [ ] Show monthly comparison
- [ ] Display growth percentages with up/down arrows
- [ ] Show pending payouts alert
- [ ] Add year-to-date summary

### Transactions Section:
- [ ] Create transactions component
- [ ] Fetch `/api/rentals/rentals/transactions/`
- [ ] Add filters (status, date range)
- [ ] Display totals summary
- [ ] Create transactions table
- [ ] Add status badges with colors
- [ ] Show formatted currency
- [ ] Add pagination support

---

## 🎯 Example Data Flow

```
User Opens Financial Dashboard
         ↓
    Fetch Revenue Summary
         ↓
    Display Overview Cards
         ↓
    Show Growth Trends
         ↓
    User Clicks Transactions Tab
         ↓
    Fetch Transaction List
         ↓
    Display Table with Filters
         ↓
    User Filters by "Pending"
         ↓
    Re-fetch with Filter
         ↓
    Update Table
```

---

## 💡 Pro Tips

1. **Cache Data:** Store revenue summary in state/store to avoid unnecessary API calls
2. **Pagination:** Use page size of 25-50 transactions for better UX
3. **Export:** Add CSV export button for accountants
4. **Charts:** Use Chart.js or Recharts to visualize revenue trends
5. **Currency:** Always display with proper currency symbol based on country
6. **Loading States:** Show skeleton loaders while fetching
7. **Error Handling:** Display friendly messages on API errors
8. **Filters:** Save filter preferences in localStorage

---

## 📊 Advanced Features

### Revenue Charts

```jsx
import { Line } from 'react-chartjs-2';

const RevenueChart = ({ monthlyData }) => {
  const data = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [{
      label: 'Revenue',
      data: monthlyData,
      borderColor: 'rgb(16, 185, 129)',
      backgroundColor: 'rgba(16, 185, 129, 0.1)',
    }]
  };

  return <Line data={data} />;
};
```

### Export Transactions

```javascript
const exportToCSV = () => {
  const csv = transactions.map(tx => 
    `${tx.sale_date},${tx.rental_reference},${tx.customer_name},${tx.total_revenue},${tx.seller_payout}`
  ).join('\n');
  
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'transactions.csv';
  a.click();
};
```

---

## 🔗 Related Documentation

- `SALES_TRACKING_GUIDE.md` - Complete sales system documentation
- `SALES_QUICK_ANSWER.md` - Quick reference
- `MASTER_API_DOCUMENTATION.md` - All API endpoints
- `SELLER_DASHBOARD_SPEC.md` - Seller dashboard features

---

**You're now ready to integrate the financial section!** 🎉

The APIs are live and ready to use. Just call the endpoints and display the data as shown in the examples above.
