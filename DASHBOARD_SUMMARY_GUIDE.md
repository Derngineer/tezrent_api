# Dashboard Summary Integration Guide

Complete guide for integrating the platform dashboard summary with your frontend.

## Table of Contents
1. [API Endpoint](#api-endpoint)
2. [Response Structure](#response-structure)
3. [Frontend Integration](#frontend-integration)
4. [React Implementation](#react-implementation)
5. [Vue Implementation](#vue-implementation)
6. [Mobile (React Native)](#mobile-react-native)
7. [CSS Styling](#css-styling)

---

## API Endpoint

### Dashboard Summary
Get comprehensive platform statistics for the main dashboard page.

**Endpoint:** `GET /api/rentals/rentals/dashboard_summary/`

**Authentication:** Required (Admin/Staff recommended)

**Response:** Platform-wide statistics including equipment, rentals, approvals, and revenue

---

## Response Structure

```json
{
  "summary": {
    "total_equipment": 45,
    "active_rentals": 12,
    "pending_approvals": 3,
    "monthly_revenue": 15250.50
  },
  "monthly_stats": {
    "revenue": 15250.50,
    "commission": 1525.05,
    "sales_count": 18,
    "revenue_growth_percentage": 23.45,
    "sales_growth_percentage": 15.20
  },
  "comparison": {
    "this_month": {
      "revenue": 15250.50,
      "sales": 18
    },
    "last_month": {
      "revenue": 12350.00,
      "sales": 15
    }
  },
  "platform_stats": {
    "total_rentals": 145,
    "completed_rentals": 128,
    "completion_rate": 88.28
  },
  "equipment_by_category": [
    {
      "category__name": "Construction Equipment",
      "count": 15
    },
    {
      "category__name": "Power Tools",
      "count": 12
    }
  ],
  "top_equipment": [
    {
      "equipment__name": "Excavator CAT 320",
      "equipment__id": 5,
      "rental_count": 25,
      "total_revenue": 45000.00
    }
  ],
  "recent_activity": [
    {
      "id": 123,
      "rental_reference": "RNT2B915512",
      "equipment__name": "Bobcat S570",
      "customer__user__username": "john_doe",
      "status": "in_progress",
      "total_amount": 1250.00,
      "created_at": "2024-10-28T10:30:00Z"
    }
  ],
  "pending_payouts": {
    "count": 5,
    "total_amount": 12450.00
  }
}
```

---

## Frontend Integration

### Key Metrics Displayed

1. **Total Equipment** - All active equipment on platform
2. **Active Rentals** - Currently ongoing rentals
3. **Pending Approvals** - Rentals waiting for seller approval
4. **Monthly Revenue** - Revenue from completed rentals this month

### Additional Insights

- Revenue growth comparison (month-over-month)
- Sales count and trends
- Platform completion rate
- Equipment distribution by category
- Top performing equipment
- Recent rental activity
- Pending payouts to sellers

---

## React Implementation

### Complete Dashboard Component

```jsx
import React, { useState, useEffect } from 'react';
import { 
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer 
} from 'recharts';
import './DashboardSummary.css';

const DashboardSummary = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardData();
    
    // Auto-refresh every 5 minutes
    const interval = setInterval(fetchDashboardData, 300000);
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem('accessToken');
      const response = await fetch(
        'http://localhost:8000/api/rentals/rentals/dashboard_summary/',
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }

      const data = await response.json();
      setDashboardData(data);
      setLoading(false);
    } catch (err) {
      console.error('Failed to fetch dashboard data:', err);
      setError(err.message);
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'AED',
    }).format(amount);
  };

  const getGrowthIcon = (percentage) => {
    if (percentage > 0) return '📈';
    if (percentage < 0) return '📉';
    return '➖';
  };

  const getStatusColor = (status) => {
    const colors = {
      'in_progress': '#3b82f6',
      'completed': '#10b981',
      'pending': '#f59e0b',
      'confirmed': '#8b5cf6',
      'cancelled': '#ef4444',
    };
    return colors[status] || '#6b7280';
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="spinner"></div>
        <p>Loading dashboard...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-error">
        <h3>Error loading dashboard</h3>
        <p>{error}</p>
        <button onClick={fetchDashboardData}>Retry</button>
      </div>
    );
  }

  const { summary, monthly_stats, comparison, platform_stats, 
          equipment_by_category, top_equipment, recent_activity, 
          pending_payouts } = dashboardData;

  // Prepare chart data
  const COLORS = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444'];

  return (
    <div className="dashboard-summary">
      {/* Header */}
      <div className="dashboard-header">
        <h1>Dashboard Overview</h1>
        <button onClick={fetchDashboardData} className="refresh-btn">
          🔄 Refresh
        </button>
      </div>

      {/* Key Metrics Cards */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-icon">📦</div>
          <div className="metric-content">
            <h3>Total Equipment</h3>
            <p className="metric-value">{summary.total_equipment}</p>
            <span className="metric-label">Active listings</span>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">🔄</div>
          <div className="metric-content">
            <h3>Active Rentals</h3>
            <p className="metric-value">{summary.active_rentals}</p>
            <span className="metric-label">Currently ongoing</span>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">⏳</div>
          <div className="metric-content">
            <h3>Pending Approvals</h3>
            <p className="metric-value">{summary.pending_approvals}</p>
            <span className="metric-label">Awaiting seller approval</span>
          </div>
        </div>

        <div className="metric-card highlight">
          <div className="metric-icon">💰</div>
          <div className="metric-content">
            <h3>Monthly Revenue</h3>
            <p className="metric-value">{formatCurrency(summary.monthly_revenue)}</p>
            <span className="metric-label">
              {getGrowthIcon(monthly_stats.revenue_growth_percentage)}
              {Math.abs(monthly_stats.revenue_growth_percentage)}% vs last month
            </span>
          </div>
        </div>
      </div>

      {/* Revenue Analysis */}
      <div className="dashboard-section">
        <h2>Revenue Analytics</h2>
        <div className="analytics-grid">
          <div className="analytics-card">
            <h3>Monthly Performance</h3>
            <div className="performance-stats">
              <div className="stat-item">
                <label>Sales Count</label>
                <p className="stat-value">{monthly_stats.sales_count}</p>
                <span className={`stat-change ${monthly_stats.sales_growth_percentage >= 0 ? 'positive' : 'negative'}`}>
                  {monthly_stats.sales_growth_percentage >= 0 ? '+' : ''}
                  {monthly_stats.sales_growth_percentage}%
                </span>
              </div>
              <div className="stat-item">
                <label>Platform Commission</label>
                <p className="stat-value">{formatCurrency(monthly_stats.commission)}</p>
              </div>
              <div className="stat-item">
                <label>Completion Rate</label>
                <p className="stat-value">{platform_stats.completion_rate}%</p>
              </div>
            </div>
          </div>

          <div className="analytics-card">
            <h3>Month Comparison</h3>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={[
                { name: 'Last Month', revenue: comparison.last_month.revenue, sales: comparison.last_month.sales },
                { name: 'This Month', revenue: comparison.this_month.revenue, sales: comparison.this_month.sales }
              ]}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="revenue" fill="#3b82f6" name="Revenue" />
                <Bar dataKey="sales" fill="#10b981" name="Sales Count" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Equipment Distribution */}
      <div className="dashboard-section">
        <h2>Equipment Overview</h2>
        <div className="equipment-grid">
          <div className="equipment-card">
            <h3>Equipment by Category</h3>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={equipment_by_category}
                  dataKey="count"
                  nameKey="category__name"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  label
                >
                  {equipment_by_category.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="equipment-card">
            <h3>Top Performing Equipment</h3>
            <div className="top-equipment-list">
              {top_equipment.map((item, index) => (
                <div key={item.equipment__id} className="top-equipment-item">
                  <span className="rank">#{index + 1}</span>
                  <div className="equipment-info">
                    <p className="equipment-name">{item.equipment__name}</p>
                    <small>{item.rental_count} rentals · {formatCurrency(item.total_revenue)}</small>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="dashboard-section">
        <h2>Recent Activity</h2>
        <div className="activity-table">
          <table>
            <thead>
              <tr>
                <th>Reference</th>
                <th>Equipment</th>
                <th>Customer</th>
                <th>Status</th>
                <th>Amount</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {recent_activity.map((rental) => (
                <tr key={rental.id}>
                  <td><strong>{rental.rental_reference}</strong></td>
                  <td>{rental.equipment__name}</td>
                  <td>{rental.customer__user__username}</td>
                  <td>
                    <span 
                      className="status-badge" 
                      style={{ backgroundColor: getStatusColor(rental.status) }}
                    >
                      {rental.status.replace('_', ' ')}
                    </span>
                  </td>
                  <td>{formatCurrency(rental.total_amount)}</td>
                  <td>{new Date(rental.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Pending Payouts Alert */}
      {pending_payouts.count > 0 && (
        <div className="dashboard-section">
          <div className="alert-card warning">
            <div className="alert-icon">⚠️</div>
            <div className="alert-content">
              <h3>Pending Payouts</h3>
              <p>
                {pending_payouts.count} seller payouts pending totaling {formatCurrency(pending_payouts.total_amount)}
              </p>
              <button className="view-payouts-btn">View Payouts</button>
            </div>
          </div>
        </div>
      )}

      {/* Platform Stats Footer */}
      <div className="dashboard-footer">
        <div className="footer-stat">
          <label>Total Rentals (All Time)</label>
          <p>{platform_stats.total_rentals}</p>
        </div>
        <div className="footer-stat">
          <label>Completed Rentals</label>
          <p>{platform_stats.completed_rentals}</p>
        </div>
        <div className="footer-stat">
          <label>Success Rate</label>
          <p>{platform_stats.completion_rate}%</p>
        </div>
      </div>
    </div>
  );
};

export default DashboardSummary;
```

---

## Vue Implementation

### Vue 3 Composition API

```vue
<template>
  <div class="dashboard-summary">
    <!-- Loading State -->
    <div v-if="loading" class="dashboard-loading">
      <div class="spinner"></div>
      <p>Loading dashboard...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="dashboard-error">
      <h3>Error loading dashboard</h3>
      <p>{{ error }}</p>
      <button @click="fetchDashboardData">Retry</button>
    </div>

    <!-- Dashboard Content -->
    <div v-else>
      <!-- Header -->
      <div class="dashboard-header">
        <h1>Dashboard Overview</h1>
        <button @click="fetchDashboardData" class="refresh-btn">
          🔄 Refresh
        </button>
      </div>

      <!-- Key Metrics -->
      <div class="metrics-grid">
        <div class="metric-card">
          <div class="metric-icon">📦</div>
          <div class="metric-content">
            <h3>Total Equipment</h3>
            <p class="metric-value">{{ summary.total_equipment }}</p>
            <span class="metric-label">Active listings</span>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon">🔄</div>
          <div class="metric-content">
            <h3>Active Rentals</h3>
            <p class="metric-value">{{ summary.active_rentals }}</p>
            <span class="metric-label">Currently ongoing</span>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon">⏳</div>
          <div class="metric-content">
            <h3>Pending Approvals</h3>
            <p class="metric-value">{{ summary.pending_approvals }}</p>
            <span class="metric-label">Awaiting seller approval</span>
          </div>
        </div>

        <div class="metric-card highlight">
          <div class="metric-icon">💰</div>
          <div class="metric-content">
            <h3>Monthly Revenue</h3>
            <p class="metric-value">{{ formatCurrency(summary.monthly_revenue) }}</p>
            <span class="metric-label">
              {{ getGrowthIcon(monthlyStats.revenue_growth_percentage) }}
              {{ Math.abs(monthlyStats.revenue_growth_percentage) }}% vs last month
            </span>
          </div>
        </div>
      </div>

      <!-- Revenue Analytics -->
      <div class="dashboard-section">
        <h2>Revenue Analytics</h2>
        <div class="analytics-grid">
          <div class="analytics-card">
            <h3>Monthly Performance</h3>
            <div class="performance-stats">
              <div class="stat-item">
                <label>Sales Count</label>
                <p class="stat-value">{{ monthlyStats.sales_count }}</p>
                <span :class="['stat-change', monthlyStats.sales_growth_percentage >= 0 ? 'positive' : 'negative']">
                  {{ monthlyStats.sales_growth_percentage >= 0 ? '+' : '' }}{{ monthlyStats.sales_growth_percentage }}%
                </span>
              </div>
              <div class="stat-item">
                <label>Platform Commission</label>
                <p class="stat-value">{{ formatCurrency(monthlyStats.commission) }}</p>
              </div>
              <div class="stat-item">
                <label>Completion Rate</label>
                <p class="stat-value">{{ platformStats.completion_rate }}%</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Activity -->
      <div class="dashboard-section">
        <h2>Recent Activity</h2>
        <div class="activity-table">
          <table>
            <thead>
              <tr>
                <th>Reference</th>
                <th>Equipment</th>
                <th>Customer</th>
                <th>Status</th>
                <th>Amount</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="rental in recentActivity" :key="rental.id">
                <td><strong>{{ rental.rental_reference }}</strong></td>
                <td>{{ rental.equipment__name }}</td>
                <td>{{ rental.customer__user__username }}</td>
                <td>
                  <span 
                    class="status-badge" 
                    :style="{ backgroundColor: getStatusColor(rental.status) }"
                  >
                    {{ rental.status.replace('_', ' ') }}
                  </span>
                </td>
                <td>{{ formatCurrency(rental.total_amount) }}</td>
                <td>{{ formatDate(rental.created_at) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Pending Payouts Alert -->
      <div v-if="pendingPayouts.count > 0" class="dashboard-section">
        <div class="alert-card warning">
          <div class="alert-icon">⚠️</div>
          <div class="alert-content">
            <h3>Pending Payouts</h3>
            <p>
              {{ pendingPayouts.count }} seller payouts pending totaling {{ formatCurrency(pendingPayouts.total_amount) }}
            </p>
            <button class="view-payouts-btn">View Payouts</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

const dashboardData = ref(null);
const loading = ref(true);
const error = ref(null);
let refreshInterval = null;

const summary = ref({});
const monthlyStats = ref({});
const comparison = ref({});
const platformStats = ref({});
const equipmentByCategory = ref([]);
const topEquipment = ref([]);
const recentActivity = ref([]);
const pendingPayouts = ref({});

const fetchDashboardData = async () => {
  try {
    const token = localStorage.getItem('accessToken');
    const response = await fetch(
      'http://localhost:8000/api/rentals/rentals/dashboard_summary/',
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }

    const data = await response.json();
    
    summary.value = data.summary;
    monthlyStats.value = data.monthly_stats;
    comparison.value = data.comparison;
    platformStats.value = data.platform_stats;
    equipmentByCategory.value = data.equipment_by_category;
    topEquipment.value = data.top_equipment;
    recentActivity.value = data.recent_activity;
    pendingPayouts.value = data.pending_payouts;
    
    loading.value = false;
  } catch (err) {
    console.error('Failed to fetch dashboard data:', err);
    error.value = err.message;
    loading.value = false;
  }
};

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'AED',
  }).format(amount);
};

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString();
};

const getGrowthIcon = (percentage) => {
  if (percentage > 0) return '📈';
  if (percentage < 0) return '📉';
  return '➖';
};

const getStatusColor = (status) => {
  const colors = {
    'in_progress': '#3b82f6',
    'completed': '#10b981',
    'pending': '#f59e0b',
    'confirmed': '#8b5cf6',
    'cancelled': '#ef4444',
  };
  return colors[status] || '#6b7280';
};

onMounted(() => {
  fetchDashboardData();
  refreshInterval = setInterval(fetchDashboardData, 300000); // 5 minutes
});

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval);
  }
});
</script>

<style scoped>
/* Import the CSS from the styling section below */
</style>
```

---

## Mobile (React Native)

### React Native Implementation

```jsx
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  RefreshControl,
  ActivityIndicator,
  StyleSheet,
  TouchableOpacity,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

const DashboardSummary = ({ navigation }) => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const token = await AsyncStorage.getItem('accessToken');
      const response = await fetch(
        'http://localhost:8000/api/rentals/rentals/dashboard_summary/',
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }

      const data = await response.json();
      setDashboardData(data);
      setLoading(false);
      setRefreshing(false);
    } catch (err) {
      console.error('Failed to fetch dashboard data:', err);
      setError(err.message);
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    fetchDashboardData();
  };

  const formatCurrency = (amount) => {
    return `AED ${amount.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,')}`;
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#3b82f6" />
        <Text style={styles.loadingText}>Loading dashboard...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorTitle}>Error loading dashboard</Text>
        <Text style={styles.errorMessage}>{error}</Text>
        <TouchableOpacity style={styles.retryButton} onPress={fetchDashboardData}>
          <Text style={styles.retryButtonText}>Retry</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const { summary, monthly_stats, platform_stats, recent_activity, pending_payouts } = dashboardData;

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Dashboard Overview</Text>
      </View>

      {/* Key Metrics */}
      <View style={styles.metricsGrid}>
        <View style={styles.metricCard}>
          <Text style={styles.metricIcon}>📦</Text>
          <Text style={styles.metricLabel}>Total Equipment</Text>
          <Text style={styles.metricValue}>{summary.total_equipment}</Text>
        </View>

        <View style={styles.metricCard}>
          <Text style={styles.metricIcon}>🔄</Text>
          <Text style={styles.metricLabel}>Active Rentals</Text>
          <Text style={styles.metricValue}>{summary.active_rentals}</Text>
        </View>

        <View style={styles.metricCard}>
          <Text style={styles.metricIcon}>⏳</Text>
          <Text style={styles.metricLabel}>Pending Approvals</Text>
          <Text style={styles.metricValue}>{summary.pending_approvals}</Text>
        </View>

        <View style={[styles.metricCard, styles.metricCardHighlight]}>
          <Text style={styles.metricIcon}>💰</Text>
          <Text style={styles.metricLabel}>Monthly Revenue</Text>
          <Text style={styles.metricValue}>{formatCurrency(summary.monthly_revenue)}</Text>
          <Text style={styles.metricGrowth}>
            {monthly_stats.revenue_growth_percentage >= 0 ? '📈' : '📉'} 
            {Math.abs(monthly_stats.revenue_growth_percentage)}%
          </Text>
        </View>
      </View>

      {/* Monthly Performance */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Monthly Performance</Text>
        <View style={styles.performanceCard}>
          <View style={styles.performanceItem}>
            <Text style={styles.performanceLabel}>Sales Count</Text>
            <Text style={styles.performanceValue}>{monthly_stats.sales_count}</Text>
          </View>
          <View style={styles.performanceItem}>
            <Text style={styles.performanceLabel}>Commission</Text>
            <Text style={styles.performanceValue}>{formatCurrency(monthly_stats.commission)}</Text>
          </View>
          <View style={styles.performanceItem}>
            <Text style={styles.performanceLabel}>Completion Rate</Text>
            <Text style={styles.performanceValue}>{platform_stats.completion_rate}%</Text>
          </View>
        </View>
      </View>

      {/* Recent Activity */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Recent Activity</Text>
        {recent_activity.map((rental) => (
          <View key={rental.id} style={styles.activityItem}>
            <View style={styles.activityHeader}>
              <Text style={styles.activityReference}>{rental.rental_reference}</Text>
              <Text style={styles.activityAmount}>{formatCurrency(rental.total_amount)}</Text>
            </View>
            <Text style={styles.activityEquipment}>{rental.equipment__name}</Text>
            <View style={styles.activityFooter}>
              <Text style={styles.activityCustomer}>{rental.customer__user__username}</Text>
              <View style={[styles.statusBadge, { backgroundColor: getStatusColor(rental.status) }]}>
                <Text style={styles.statusBadgeText}>{rental.status.replace('_', ' ')}</Text>
              </View>
            </View>
          </View>
        ))}
      </View>

      {/* Pending Payouts Alert */}
      {pending_payouts.count > 0 && (
        <View style={styles.alertCard}>
          <Text style={styles.alertIcon}>⚠️</Text>
          <Text style={styles.alertTitle}>Pending Payouts</Text>
          <Text style={styles.alertMessage}>
            {pending_payouts.count} seller payouts pending totaling {formatCurrency(pending_payouts.total_amount)}
          </Text>
          <TouchableOpacity 
            style={styles.alertButton}
            onPress={() => navigation.navigate('Payouts')}
          >
            <Text style={styles.alertButtonText}>View Payouts</Text>
          </TouchableOpacity>
        </View>
      )}
    </ScrollView>
  );
};

const getStatusColor = (status) => {
  const colors = {
    'in_progress': '#3b82f6',
    'completed': '#10b981',
    'pending': '#f59e0b',
    'confirmed': '#8b5cf6',
    'cancelled': '#ef4444',
  };
  return colors[status] || '#6b7280';
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9fafb',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f9fafb',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#6b7280',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#f9fafb',
  },
  errorTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#ef4444',
    marginBottom: 8,
  },
  errorMessage: {
    fontSize: 16,
    color: '#6b7280',
    textAlign: 'center',
    marginBottom: 16,
  },
  retryButton: {
    backgroundColor: '#3b82f6',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  retryButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  header: {
    padding: 20,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#111827',
  },
  metricsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: 10,
  },
  metricCard: {
    width: '48%',
    margin: '1%',
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  metricCardHighlight: {
    backgroundColor: '#3b82f6',
  },
  metricIcon: {
    fontSize: 32,
    marginBottom: 8,
  },
  metricLabel: {
    fontSize: 12,
    color: '#6b7280',
    marginBottom: 4,
  },
  metricValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#111827',
  },
  metricGrowth: {
    fontSize: 12,
    color: 'white',
    marginTop: 4,
  },
  section: {
    padding: 16,
    backgroundColor: 'white',
    marginTop: 8,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#111827',
    marginBottom: 12,
  },
  performanceCard: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  performanceItem: {
    alignItems: 'center',
  },
  performanceLabel: {
    fontSize: 12,
    color: '#6b7280',
    marginBottom: 4,
  },
  performanceValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#111827',
  },
  activityItem: {
    backgroundColor: '#f9fafb',
    borderRadius: 8,
    padding: 12,
    marginBottom: 8,
  },
  activityHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  activityReference: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#111827',
  },
  activityAmount: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#3b82f6',
  },
  activityEquipment: {
    fontSize: 13,
    color: '#6b7280',
    marginBottom: 8,
  },
  activityFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  activityCustomer: {
    fontSize: 12,
    color: '#6b7280',
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  statusBadgeText: {
    fontSize: 10,
    color: 'white',
    fontWeight: '600',
    textTransform: 'capitalize',
  },
  alertCard: {
    margin: 16,
    backgroundColor: '#fef3c7',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
  },
  alertIcon: {
    fontSize: 32,
    marginBottom: 8,
  },
  alertTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#92400e',
    marginBottom: 4,
  },
  alertMessage: {
    fontSize: 14,
    color: '#78350f',
    textAlign: 'center',
    marginBottom: 12,
  },
  alertButton: {
    backgroundColor: '#f59e0b',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 8,
  },
  alertButtonText: {
    color: 'white',
    fontSize: 14,
    fontWeight: '600',
  },
});

export default DashboardSummary;
```

---

## CSS Styling

### Complete Stylesheet for Web

```css
/* DashboardSummary.css */

.dashboard-summary {
  padding: 20px;
  background-color: #f9fafb;
  min-height: 100vh;
}

/* Loading & Error States */
.dashboard-loading,
.dashboard-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  padding: 40px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #e5e7eb;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.dashboard-error h3 {
  color: #ef4444;
  font-size: 24px;
  margin-bottom: 10px;
}

.dashboard-error p {
  color: #6b7280;
  margin-bottom: 20px;
}

.dashboard-error button {
  background-color: #3b82f6;
  color: white;
  padding: 10px 24px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
}

/* Header */
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.dashboard-header h1 {
  font-size: 32px;
  font-weight: bold;
  color: #111827;
}

.refresh-btn {
  background-color: white;
  border: 1px solid #e5e7eb;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.refresh-btn:hover {
  background-color: #f9fafb;
  border-color: #d1d5db;
}

/* Metrics Grid */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.metric-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.metric-card.highlight {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
}

.metric-card.highlight .metric-content h3,
.metric-card.highlight .metric-content .metric-value {
  color: white;
}

.metric-icon {
  font-size: 48px;
  line-height: 1;
}

.metric-content {
  flex: 1;
}

.metric-content h3 {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 8px;
  font-weight: 500;
}

.metric-value {
  font-size: 32px;
  font-weight: bold;
  color: #111827;
  margin-bottom: 4px;
}

.metric-label {
  font-size: 12px;
  color: #9ca3af;
}

/* Dashboard Sections */
.dashboard-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.dashboard-section h2 {
  font-size: 24px;
  font-weight: bold;
  color: #111827;
  margin-bottom: 20px;
}

/* Analytics Grid */
.analytics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.analytics-card {
  background: #f9fafb;
  border-radius: 8px;
  padding: 20px;
}

.analytics-card h3 {
  font-size: 18px;
  font-weight: 600;
  color: #111827;
  margin-bottom: 16px;
}

.performance-stats {
  display: flex;
  justify-content: space-around;
  gap: 16px;
}

.stat-item {
  text-align: center;
}

.stat-item label {
  display: block;
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #111827;
  margin-bottom: 4px;
}

.stat-change {
  font-size: 14px;
  font-weight: 600;
}

.stat-change.positive {
  color: #10b981;
}

.stat-change.negative {
  color: #ef4444;
}

/* Equipment Grid */
.equipment-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 20px;
}

.equipment-card {
  background: #f9fafb;
  border-radius: 8px;
  padding: 20px;
}

.equipment-card h3 {
  font-size: 18px;
  font-weight: 600;
  color: #111827;
  margin-bottom: 16px;
}

.top-equipment-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.top-equipment-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: white;
  border-radius: 6px;
}

.top-equipment-item .rank {
  font-size: 20px;
  font-weight: bold;
  color: #3b82f6;
  width: 32px;
  text-align: center;
}

.equipment-info {
  flex: 1;
}

.equipment-name {
  font-size: 14px;
  font-weight: 600;
  color: #111827;
  margin-bottom: 4px;
}

.equipment-info small {
  font-size: 12px;
  color: #6b7280;
}

/* Activity Table */
.activity-table {
  overflow-x: auto;
}

.activity-table table {
  width: 100%;
  border-collapse: collapse;
}

.activity-table th {
  text-align: left;
  padding: 12px;
  background-color: #f9fafb;
  font-size: 14px;
  font-weight: 600;
  color: #6b7280;
  border-bottom: 2px solid #e5e7eb;
}

.activity-table td {
  padding: 12px;
  border-bottom: 1px solid #e5e7eb;
  font-size: 14px;
  color: #111827;
}

.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  color: white;
  text-transform: capitalize;
}

/* Alert Card */
.alert-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  border-radius: 8px;
}

.alert-card.warning {
  background-color: #fef3c7;
  border: 1px solid #fbbf24;
}

.alert-icon {
  font-size: 32px;
}

.alert-content {
  flex: 1;
}

.alert-content h3 {
  font-size: 18px;
  font-weight: bold;
  color: #92400e;
  margin-bottom: 4px;
}

.alert-content p {
  font-size: 14px;
  color: #78350f;
  margin-bottom: 12px;
}

.view-payouts-btn {
  background-color: #f59e0b;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
}

.view-payouts-btn:hover {
  background-color: #d97706;
}

/* Footer Stats */
.dashboard-footer {
  display: flex;
  justify-content: space-around;
  padding: 24px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.footer-stat {
  text-align: center;
}

.footer-stat label {
  display: block;
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 8px;
}

.footer-stat p {
  font-size: 28px;
  font-weight: bold;
  color: #111827;
}

/* Responsive Design */
@media (max-width: 768px) {
  .metrics-grid {
    grid-template-columns: 1fr;
  }

  .analytics-grid,
  .equipment-grid {
    grid-template-columns: 1fr;
  }

  .performance-stats {
    flex-direction: column;
  }

  .dashboard-footer {
    flex-direction: column;
    gap: 20px;
  }

  .activity-table {
    font-size: 12px;
  }

  .activity-table th,
  .activity-table td {
    padding: 8px;
  }
}
```

---

## Usage Examples

### Example API Call

```javascript
// Fetch dashboard summary
const fetchDashboard = async () => {
  const response = await fetch(
    'http://localhost:8000/api/rentals/rentals/dashboard_summary/',
    {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
      },
    }
  );
  
  const data = await response.json();
  console.log('Dashboard:', data);
};
```

### View Analytics Button

Add a button to navigate to detailed analytics:

```jsx
<button 
  className="view-analytics-btn"
  onClick={() => navigate('/analytics')}
>
  📊 View Detailed Analytics
</button>
```

---

## API Testing

### cURL Example

```bash
curl -X GET \
  'http://localhost:8000/api/rentals/rentals/dashboard_summary/' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'
```

### Expected Response (Example)

```json
{
  "summary": {
    "total_equipment": 45,
    "active_rentals": 12,
    "pending_approvals": 3,
    "monthly_revenue": 15250.50
  },
  "monthly_stats": {
    "revenue": 15250.50,
    "commission": 1525.05,
    "sales_count": 18,
    "revenue_growth_percentage": 23.45,
    "sales_growth_percentage": 15.20
  }
}
```

---

## Key Features

✅ **Real-time Metrics** - Live dashboard data  
✅ **Growth Tracking** - Month-over-month comparisons  
✅ **Equipment Analytics** - Category distribution and top performers  
✅ **Recent Activity** - Last 5 rental transactions  
✅ **Payout Alerts** - Pending seller payouts  
✅ **Auto-refresh** - Updates every 5 minutes  
✅ **Responsive Design** - Works on all screen sizes  
✅ **Mobile Support** - React Native implementation included  

---

## Next Steps

1. **Integrate the endpoint** in your frontend application
2. **Test with real data** by creating test rentals and completions
3. **Customize styling** to match your brand
4. **Add navigation** to detailed analytics pages
5. **Set up notifications** for pending approvals
6. **Add export functionality** for reports

---

## Support

For additional help or customization:
- Check the main API documentation: `MASTER_API_DOCUMENTATION.md`
- Review financial integration: `FINANCIALS_INTEGRATION_GUIDE.md`
- Test the endpoint using the provided code examples

The dashboard summary endpoint provides everything you need to create a comprehensive overview of your rental platform!
