# 📈 Revenue Trends Chart - Frontend Integration Guide

## 🎯 API Endpoint

```
GET /api/rentals/rentals/revenue_trends/
```

### Query Parameters:
- `period` (optional): `daily` | `weekly` | `monthly` (default: `daily`)
- `days` (optional): Number of days to fetch (default: 30 for daily)

---

## 📊 API Response

```json
{
  "period": "daily",
  "days": 30,
  "data": [
    {
      "date": "2025-11-03",
      "label": "Nov 03",
      "sales": 1,
      "revenue": 2350.0,
      "commission": 235.0,
      "payout": 2115.0
    },
    {
      "date": "2025-11-04",
      "label": "Nov 04",
      "sales": 1,
      "revenue": 3990.0,
      "commission": 399.0,
      "payout": 3591.0
    }
  ],
  "summary": {
    "total_sales": 2,
    "total_revenue": 6340.0,
    "total_commission": 634.0,
    "total_payout": 5706.0,
    "average_daily": 2853.0
  }
}
```

---

## 🔧 Frontend Integration

### **Option 1: React + Chart.js**

```jsx
import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const RevenueTrendsChart = () => {
  const [trendsData, setTrendsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState('daily');

  useEffect(() => {
    fetchTrends();
  }, [period]);

  const fetchTrends = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(
        `/api/rentals/rentals/revenue_trends/?period=${period}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      const data = await response.json();
      setTrendsData(data);
    } catch (error) {
      console.error('Error fetching revenue trends:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading chart...</div>;
  if (!trendsData || trendsData.data.length === 0) {
    return <div>No revenue data available</div>;
  }

  // Chart configuration
  const chartData = {
    labels: trendsData.data.map(d => d.label),
    datasets: [
      {
        label: 'Your Earnings (AED)',
        data: trendsData.data.map(d => d.payout),
        borderColor: '#4CAF50',
        backgroundColor: 'rgba(76, 175, 80, 0.2)',
        tension: 0.4,
        fill: true,
        pointRadius: 4,
        pointHoverRadius: 6
      },
      {
        label: 'Total Revenue (AED)',
        data: trendsData.data.map(d => d.revenue),
        borderColor: '#2196F3',
        backgroundColor: 'rgba(33, 150, 243, 0.2)',
        tension: 0.4,
        fill: true,
        pointRadius: 4,
        pointHoverRadius: 6
      }
    ]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
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
      legend: {
        position: 'top',
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            return `${context.dataset.label}: AED ${context.parsed.y.toLocaleString()}`;
          }
        }
      }
    }
  };

  return (
    <div className="revenue-chart-container">
      <div className="chart-header">
        <h3>Revenue Trends</h3>
        <div className="period-selector">
          <select 
            value={period} 
            onChange={(e) => setPeriod(e.target.value)}
            className="form-select"
          >
            <option value="daily">Daily (30 days)</option>
            <option value="weekly">Weekly (12 weeks)</option>
            <option value="monthly">Monthly (12 months)</option>
          </select>
        </div>
      </div>

      <div className="chart-summary">
        <div className="summary-item">
          <span>Total Sales</span>
          <strong>{trendsData.summary.total_sales}</strong>
        </div>
        <div className="summary-item">
          <span>Your Earnings</span>
          <strong>AED {trendsData.summary.total_payout.toLocaleString()}</strong>
        </div>
        <div className="summary-item">
          <span>Average/Day</span>
          <strong>AED {trendsData.summary.average_daily.toLocaleString()}</strong>
        </div>
      </div>

      <div className="chart-wrapper" style={{ height: '400px' }}>
        <Line data={chartData} options={options} />
      </div>
    </div>
  );
};

export default RevenueTrendsChart;
```

### **CSS for React Component:**

```css
.revenue-chart-container {
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.chart-header h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.period-selector select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.chart-summary {
  display: flex;
  gap: 24px;
  margin-bottom: 24px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 6px;
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.summary-item span {
  font-size: 13px;
  color: #666;
}

.summary-item strong {
  font-size: 18px;
  color: #333;
}

.chart-wrapper {
  position: relative;
}
```

---

### **Option 2: Vue.js + Chart.js**

```vue
<template>
  <div class="revenue-chart-container">
    <div class="chart-header">
      <h3>Revenue Trends</h3>
      <select v-model="period" @change="fetchTrends" class="form-select">
        <option value="daily">Daily (30 days)</option>
        <option value="weekly">Weekly (12 weeks)</option>
        <option value="monthly">Monthly (12 months)</option>
      </select>
    </div>

    <div v-if="trendsData" class="chart-summary">
      <div class="summary-item">
        <span>Total Sales</span>
        <strong>{{ trendsData.summary.total_sales }}</strong>
      </div>
      <div class="summary-item">
        <span>Your Earnings</span>
        <strong>AED {{ trendsData.summary.total_payout.toLocaleString() }}</strong>
      </div>
      <div class="summary-item">
        <span>Average/Day</span>
        <strong>AED {{ trendsData.summary.average_daily.toLocaleString() }}</strong>
      </div>
    </div>

    <div class="chart-wrapper" style="height: 400px">
      <canvas ref="chartCanvas"></canvas>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue';
import { Chart } from 'chart.js/auto';

export default {
  name: 'RevenueTrendsChart',
  setup() {
    const chartCanvas = ref(null);
    const trendsData = ref(null);
    const period = ref('daily');
    let chartInstance = null;

    const fetchTrends = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await fetch(
          `/api/rentals/rentals/revenue_trends/?period=${period.value}`,
          {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          }
        );
        trendsData.value = await response.json();
        renderChart();
      } catch (error) {
        console.error('Error fetching revenue trends:', error);
      }
    };

    const renderChart = () => {
      if (!trendsData.value || !chartCanvas.value) return;

      // Destroy previous chart
      if (chartInstance) {
        chartInstance.destroy();
      }

      const ctx = chartCanvas.value.getContext('2d');
      chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
          labels: trendsData.value.data.map(d => d.label),
          datasets: [{
            label: 'Your Earnings (AED)',
            data: trendsData.value.data.map(d => d.payout),
            borderColor: '#4CAF50',
            backgroundColor: 'rgba(76, 175, 80, 0.2)',
            tension: 0.4,
            fill: true
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                callback: (value) => `AED ${value.toLocaleString()}`
              }
            }
          }
        }
      });
    };

    onMounted(() => {
      fetchTrends();
    });

    watch(period, () => {
      fetchTrends();
    });

    return {
      chartCanvas,
      trendsData,
      period,
      fetchTrends
    };
  }
};
</script>
```

---

### **Option 3: Vanilla JavaScript + Chart.js**

```html
<!DOCTYPE html>
<html>
<head>
  <title>Revenue Trends</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    .chart-container {
      max-width: 1200px;
      margin: 0 auto;
      padding: 20px;
    }
    .chart-wrapper {
      position: relative;
      height: 400px;
    }
    .period-selector {
      margin-bottom: 20px;
    }
  </style>
</head>
<body>
  <div class="chart-container">
    <h2>Revenue Trends</h2>
    
    <div class="period-selector">
      <select id="periodSelect" onchange="loadChart()">
        <option value="daily">Daily (30 days)</option>
        <option value="weekly">Weekly (12 weeks)</option>
        <option value="monthly">Monthly (12 months)</option>
      </select>
    </div>

    <div class="chart-wrapper">
      <canvas id="revenueChart"></canvas>
    </div>
  </div>

  <script>
    let chart = null;

    async function loadChart() {
      const period = document.getElementById('periodSelect').value;
      const token = localStorage.getItem('token');

      try {
        const response = await fetch(
          `/api/rentals/rentals/revenue_trends/?period=${period}`,
          {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          }
        );
        const data = await response.json();

        renderChart(data);
      } catch (error) {
        console.error('Error loading chart:', error);
      }
    }

    function renderChart(data) {
      const ctx = document.getElementById('revenueChart').getContext('2d');

      // Destroy previous chart
      if (chart) {
        chart.destroy();
      }

      chart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: data.data.map(d => d.label),
          datasets: [{
            label: 'Your Earnings (AED)',
            data: data.data.map(d => d.payout),
            borderColor: '#4CAF50',
            backgroundColor: 'rgba(76, 175, 80, 0.2)',
            tension: 0.4,
            fill: true,
            pointRadius: 4,
            pointHoverRadius: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
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
                  return `${context.dataset.label}: AED ${context.parsed.y.toLocaleString()}`;
                }
              }
            }
          }
        }
      });
    }

    // Load chart on page load
    loadChart();
  </script>
</body>
</html>
```

---

## 🎨 Multiple Lines (Revenue vs Earnings)

```javascript
const chartData = {
  labels: data.data.map(d => d.label),
  datasets: [
    {
      label: 'Your Earnings (AED)',
      data: data.data.map(d => d.payout),  // 90% - What seller gets
      borderColor: '#4CAF50',
      backgroundColor: 'rgba(76, 175, 80, 0.2)',
      tension: 0.4,
      fill: true
    },
    {
      label: 'Total Revenue (AED)',
      data: data.data.map(d => d.revenue),  // 100% - What customer paid
      borderColor: '#2196F3',
      backgroundColor: 'rgba(33, 150, 243, 0.2)',
      tension: 0.4,
      fill: false
    },
    {
      label: 'Platform Fee (AED)',
      data: data.data.map(d => d.commission),  // 10% - Platform keeps
      borderColor: '#FF9800',
      backgroundColor: 'rgba(255, 152, 0, 0.2)',
      tension: 0.4,
      fill: false,
      borderDash: [5, 5]  // Dashed line
    }
  ]
};
```

---

## 📱 Mobile Responsive

```javascript
const isMobile = window.innerWidth < 768;

const options = {
  responsive: true,
  maintainAspectRatio: !isMobile,
  aspectRatio: isMobile ? 1 : 2,
  scales: {
    x: {
      ticks: {
        maxRotation: isMobile ? 45 : 0,
        autoSkip: true,
        maxTicksLimit: isMobile ? 7 : 30
      }
    },
    y: {
      beginAtZero: true
    }
  }
};
```

---

## 🔗 Full Production URL

```javascript
const API_URL = 'https://tezrentapibackend-bsatbme3eqfkfnc3.canadacentral-01.azurewebsites.net';

const response = await fetch(`${API_URL}/api/rentals/rentals/revenue_trends/`, {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

---

## ✅ Quick Start Checklist

1. ✅ Install Chart.js: `npm install chart.js react-chartjs-2`
2. ✅ Copy component code from above
3. ✅ Add to your dashboard page
4. ✅ Ensure authentication token is available
5. ✅ Test with: `GET /api/rentals/rentals/revenue_trends/`

---

**Last Updated**: November 4, 2025  
**Your Current Data**: 2 sales (AED 5,706 total payout)
