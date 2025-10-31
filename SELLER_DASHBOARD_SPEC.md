# TezRent Seller Dashboard - Frontend Specification

## Document Overview
**Version:** 1.0  
**Date:** October 22, 2025  
**Target:** Frontend Designer/Developer  
**Platform:** Web Dashboard (React/Vue/Angular)  
**API Base URL:** `http://your-domain.com/api/`  
**Authentication:** JWT Token (Bearer)

---

## Table of Contents
1. [Dashboard Overview](#dashboard-overview)
2. [Authentication & Authorization](#authentication--authorization)
3. [Dashboard Structure & Navigation](#dashboard-structure--navigation)
4. [Page Specifications](#page-specifications)
5. [API Endpoints Reference](#api-endpoints-reference)
6. [Data Models & Interfaces](#data-models--interfaces)
7. [Real-time Features](#real-time-features)
8. [UI/UX Guidelines](#uiux-guidelines)
9. [Sample API Calls](#sample-api-calls)

---

## Dashboard Overview

### Purpose
A comprehensive web dashboard for equipment rental sellers (companies) to manage their:
- Equipment inventory
- Rental requests and bookings
- Customer relationships (CRM)
- Financial tracking
- Support tickets
- Business analytics

### User Roles
**Primary Role:** Company/Seller (`user_type: 'company'`)
- Company owners and staff managing equipment rentals
- Full CRUD access to their own equipment and rentals
- CRM tools for customer management

---

## Authentication & Authorization

### Login Flow
```
POST /api/accounts/token/
Body: {
  "email": "seller@company.com",
  "password": "password123"
}

Response: {
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "seller@company.com",
    "user_type": "company",
    "company_name": "ABC Equipment Rental",
    "is_verified": true
  }
}
```

### Token Management
- **Access Token:** Include in all API calls as `Authorization: Bearer <access_token>`
- **Token Expiry:** Access token expires after 60 minutes
- **Refresh Token:** Use to get new access token without re-login
- **Storage:** Store tokens securely (httpOnly cookies or secure localStorage)

### Token Refresh
```
POST /api/accounts/token/refresh/
Body: {
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

Response: {
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Profile Data
```
GET /api/accounts/profile/
Authorization: Bearer <access_token>

Response: {
  "id": 1,
  "email": "seller@company.com",
  "user_type": "company",
  "company_name": "ABC Equipment Rental",
  "phone": "+971501234567",
  "location": "dubai",
  "trade_license_number": "TL123456",
  "is_verified": true,
  "created_at": "2025-01-15T10:00:00Z"
}
```

---

## Dashboard Structure & Navigation

### Main Layout

```
┌─────────────────────────────────────────────────────────────┐
│  HEADER                                                      │
│  [Logo] [Company Name]              [Notifications] [User]  │
├──────────┬──────────────────────────────────────────────────┤
│          │                                                   │
│  SIDEBAR │  MAIN CONTENT AREA                              │
│          │                                                   │
│  Nav     │  Dashboard widgets, tables, forms, etc.         │
│  Items   │                                                   │
│          │                                                   │
│          │                                                   │
│          │                                                   │
│          │                                                   │
└──────────┴──────────────────────────────────────────────────┘
```

### Sidebar Navigation

#### Primary Navigation
1. **📊 Dashboard** (Home)
   - Overview metrics and charts
   - Quick actions

2. **🏗️ Equipment Management**
   - My Equipment (List)
   - Add New Equipment
   - Categories
   - Unavailable Equipment

3. **📋 Rentals**
   - Pending Approvals (Badge count)
   - Active Rentals
   - Rental History
   - Calendar View

4. **👥 CRM**
   - Leads
   - Sales Opportunities
   - Customer Interactions
   - Support Tickets

5. **💰 Financial**
   - Revenue Dashboard
   - Pending Payments
   - Transaction History
   - Reports

6. **📊 Analytics**
   - Performance Metrics
   - Equipment Utilization
   - Customer Insights
   - Trends

7. **⚙️ Settings**
   - Company Profile
   - Notifications
   - Preferences

8. **❓ Help & Support**
   - Documentation
   - Contact Support

#### Header Items
- **Notifications Icon** (Bell) - Badge with unread count
- **User Dropdown** - Profile, Settings, Logout

---

## Page Specifications

### 1. Dashboard (Home Page)

#### Purpose
Overview of business metrics and quick actions

#### Layout Sections

**A. Key Metrics Cards (Row 1)**
```
┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐
│ Total Equipment │ Active Rentals  │ Pending Approvals│ Monthly Revenue │
│     45          │      12         │       8         │   AED 45,000    │
│  (+5 this month)│  (↑ 15%)        │  [View All]     │   (↑ 22%)       │
└─────────────────┴─────────────────┴─────────────────┴─────────────────┘
```

**B. Revenue Chart (Row 2)**
- Line/Bar chart showing monthly revenue over last 12 months
- Filter by: All, Equipment Category, Date Range

**C. Quick Actions (Row 2)**
- Add New Equipment (Primary button)
- View Pending Approvals (Secondary button with badge)
- Generate Report

**D. Recent Activity (Row 3, Left)**
- Latest rental requests
- Recent bookings
- Support ticket updates
- Format: Timeline/List view

**E. Equipment Performance (Row 3, Right)**
- Top 5 most rented equipment
- Equipment with low utilization
- Recently added equipment

#### API Endpoints Required
```javascript
// Dashboard metrics
GET /api/equipment/my_equipment/          // Count total equipment
GET /api/rentals/rentals/?owner_company=true&status=active  // Active rentals count
GET /api/rentals/rentals/?owner_company=true&status=pending  // Pending approvals
GET /api/rentals/rental_summary/          // Revenue and statistics

// Recent activity
GET /api/rentals/rentals/?owner_company=true&ordering=-created_at&limit=10
GET /api/crm/tickets/?ordering=-created_at&limit=5

// Top equipment
GET /api/equipment/equipment/?ordering=-times_rented&limit=5
```

---

### 2. Equipment Management

#### 2.1 My Equipment (List Page)

**Layout:**
- **Search Bar** - Search by name, category, serial number
- **Filters** (Sidebar or Dropdown)
  - Category
  - Availability Status
  - Condition
  - Price Range
- **View Toggle** - Grid view / Table view
- **Actions** - Add New Equipment (Primary button)

**Table/Grid Columns:**
- Image (thumbnail)
- Name
- Category
- Daily Rate (AED)
- Condition
- Availability Status (Available/Rented/Maintenance)
- Times Rented
- Actions (Edit, Delete, View Details)

**API Endpoints:**
```javascript
// List seller's equipment
GET /api/equipment/my_equipment/
Query params: ?search=excavator&category=1&availability_status=available

// Categories for filter
GET /api/equipment/categories/

// Delete equipment
DELETE /api/equipment/equipment/{id}/
```

#### 2.2 Add/Edit Equipment Form

**Form Fields:**

**Basic Information**
- Name* (text input)
- Category* (dropdown - from API)
- Description* (textarea, rich text)
- Serial Number (text input)

**Pricing**
- Daily Rate* (AED)
- Weekly Rate (AED)
- Monthly Rate (AED)
- Deposit Required (AED)

**Details**
- Condition* (dropdown: new, excellent, good, fair, needs_repair)
- Manufacture Year (number)
- Manufacturer (text)
- Model (text)
- Specifications (textarea/JSON editor)

**Location & Availability**
- Location* (dropdown: dubai, abu_dhabi, sharjah, etc.)
- Availability Status* (dropdown: available, rented, maintenance, unavailable)

**Media**
- Images Upload (multiple files)
  - Primary image selector
  - Drag & drop or click to upload
  - Image preview with delete option
  - Max 10 images per equipment

**Features**
- Is Featured (checkbox)
- Insurance Included (checkbox)
- Delivery Available (checkbox)

**API Endpoints:**
```javascript
// Create equipment
POST /api/equipment/equipment/
Content-Type: multipart/form-data
Body: {
  name, category, description, daily_rate, condition, location, ...
}

// Update equipment
PUT /api/equipment/equipment/{id}/
PATCH /api/equipment/equipment/{id}/  // Partial update

// Upload images
POST /api/equipment/equipment/{id}/upload_image/
Content-Type: multipart/form-data
Body: { image: File }

// Set primary image
POST /api/equipment/equipment/{id}/set_primary_image/
Body: { image_id: 5 }

// Delete image
DELETE /api/equipment/images/{image_id}/
```

#### 2.3 Equipment Detail View

**Sections:**
- Image gallery (carousel)
- Equipment information
- Pricing details
- Rental history table
- Edit/Delete buttons
- Toggle availability button

**API Endpoints:**
```javascript
// Get equipment details
GET /api/equipment/equipment/{id}/

// Get rental history for equipment
GET /api/rentals/rentals/?equipment={id}

// Toggle availability
POST /api/equipment/equipment/{id}/toggle_availability/
```

---

### 3. Rentals Management

#### 3.1 Pending Approvals Page

**Purpose:** Review and approve/reject rental requests

**Layout:**
- List/Table of pending rental requests
- Filters: Date range, Equipment, Customer
- Batch actions (if applicable)

**Card/Row Information:**
- Customer name & contact
- Equipment requested
- Rental period (start - end dates)
- Duration (days)
- Total amount (AED)
- Customer message/notes
- Actions: Approve, Reject, Contact Customer

**API Endpoints:**
```javascript
// Get pending rentals
GET /api/rentals/rentals/?owner_company=true&status=pending

// Approve rental
POST /api/rentals/rentals/{id}/approve/
Body: { 
  message: "Your rental is approved. Please proceed with payment."
}

// Reject rental
POST /api/rentals/rentals/{id}/reject/
Body: { 
  reason: "Equipment not available for selected dates"
}
```

#### 3.2 Active Rentals Page

**Purpose:** Monitor ongoing rentals

**Layout:**
- Table/Cards showing active rentals
- Status indicators
- Quick actions

**Display Information:**
- Equipment name (with image)
- Customer name
- Rental period & progress bar
- Days remaining
- Payment status
- Delivery status
- Actions: Contact Customer, Mark Delivered, Mark Returned, Report Issue

**API Endpoints:**
```javascript
// Get active rentals
GET /api/rentals/rentals/?owner_company=true&status=in_progress,approved,in_use,delivered

// Mark as delivered
POST /api/rentals/rentals/{id}/mark_delivered/
Body: { 
  delivery_notes: "Equipment delivered in excellent condition",
  delivered_at: "2025-10-22T14:30:00Z"
}

// Mark as returned
POST /api/rentals/rentals/{id}/mark_returned/
Body: { 
  return_notes: "Equipment returned with minor scratches",
  returned_at: "2025-10-30T09:00:00Z"
}

// Mark as completed
POST /api/rentals/rentals/{id}/mark_completed/
```

#### 3.3 Rental History Page

**Layout:**
- Filterable table of all past rentals
- Export functionality (CSV/PDF)
- Date range picker

**Filters:**
- Date range
- Equipment
- Customer
- Status (completed, cancelled, disputed)
- Payment status

**Table Columns:**
- Rental ID
- Date
- Equipment
- Customer
- Duration
- Revenue (AED)
- Status
- Review (if available)
- Actions: View Details, Download Invoice

**API Endpoints:**
```javascript
// Get rental history
GET /api/rentals/rentals/?owner_company=true&status=completed,cancelled,disputed
Query params: ?start_date=2025-01-01&end_date=2025-10-22&equipment={id}

// Get rental details
GET /api/rentals/rentals/{id}/

// Get revenue summary
GET /api/rentals/rental_summary/
```

#### 3.4 Calendar View

**Purpose:** Visualize equipment bookings over time

**Layout:**
- Monthly calendar
- Equipment selector (dropdown or sidebar)
- Color-coded rental periods
- Click on date to see details

**Features:**
- Multi-equipment view (stacked)
- Drag to create availability blocks
- Quick booking details on hover
- Navigate months

**API Endpoints:**
```javascript
// Get rentals for calendar
GET /api/rentals/rentals/?owner_company=true&start_date_after=2025-10-01&start_date_before=2025-10-31

// Equipment availability check
GET /api/equipment/equipment/{id}/check_availability/
Query params: ?start_date=2025-10-25&end_date=2025-10-30
```

---

### 4. CRM Section

#### 4.1 Leads Page

**Purpose:** Manage potential customers

**Layout:**
- Table/Kanban board
- Filters: Status, Source, Date, Assigned Staff
- Add Lead button

**Lead Card/Row:**
- Customer name & contact
- Company (if applicable)
- Source (website, referral, phone, etc.)
- Interest/Notes
- Status (new, contacted, qualified, lost)
- Actions: Contact, Convert to Opportunity, Mark Contacted

**API Endpoints:**
```javascript
// Get leads
GET /api/crm/leads/
Query params: ?status=new&ordering=-created_at

// Create lead
POST /api/crm/leads/
Body: {
  customer: customer_id,  // Optional if not existing customer
  customer_name: "John Doe",
  customer_email: "john@example.com",
  customer_phone: "+971501234567",
  source: "website",
  status: "new",
  notes: "Interested in excavators for construction project"
}

// Mark as contacted
POST /api/crm/leads/{id}/mark_contacted/
Body: {
  notes: "Called customer, scheduled follow-up for tomorrow"
}

// Convert to opportunity
POST /api/crm/leads/{id}/convert_to_opportunity/
Body: {
  opportunity_name: "Construction Equipment Rental - Q4 2025",
  value: 50000.00,
  expected_close_date: "2025-11-30"
}
```

#### 4.2 Sales Opportunities Page

**Purpose:** Track potential sales

**Layout:**
- Kanban board or table
- Stages: Lead, Qualified, Proposal, Negotiation, Won, Lost
- Drag & drop to change stage (Kanban)
- Pipeline value summary

**Opportunity Card:**
- Opportunity name
- Customer
- Value (AED)
- Stage
- Probability
- Expected close date
- Actions: View, Edit, Mark Won/Lost

**Pipeline Summary Widget:**
- Total pipeline value
- Opportunities by stage (count & value)
- Win rate
- Average deal size

**API Endpoints:**
```javascript
// Get opportunities
GET /api/crm/opportunities/
Query params: ?stage=qualified&ordering=-value

// Get pipeline summary
GET /api/crm/opportunities/pipeline/

// Update opportunity
PATCH /api/crm/opportunities/{id}/
Body: {
  stage: "negotiation",
  probability: 75
}

// Mark as won
POST /api/crm/opportunities/{id}/mark_won/
Body: {
  won_notes: "Customer signed contract for 6-month rental"
}

// Mark as lost
POST /api/crm/opportunities/{id}/mark_lost/
Body: {
  lost_reason: "Customer chose competitor with lower pricing"
}
```

#### 4.3 Customer Interactions Page

**Purpose:** Log all customer communications

**Layout:**
- Timeline/Table view
- Filter by customer, type, date
- Add Interaction button

**Interaction Entry:**
- Date & time
- Customer name
- Interaction type (call, email, meeting, chat, site_visit)
- Summary/Notes
- Follow-up required (yes/no)
- Actions: Edit, Delete

**API Endpoints:**
```javascript
// Get interactions
GET /api/crm/interactions/
Query params: ?customer={id}&ordering=-interaction_date

// Create interaction
POST /api/crm/interactions/
Body: {
  customer: customer_id,
  interaction_type: "call",
  interaction_date: "2025-10-22T15:30:00Z",
  summary: "Discussed equipment needs for upcoming project",
  follow_up_required: true,
  follow_up_date: "2025-10-25"
}

// Get interactions requiring follow-up
GET /api/crm/interactions/?follow_up_required=true&follow_up_date_before=2025-10-25
```

#### 4.4 Support Tickets Page

**Purpose:** Manage customer support requests

**Layout:**
- Table with status indicators
- Filters: Status, Priority, Category, Assigned Staff
- Create Ticket button

**Ticket Row/Card:**
- Ticket number
- Subject
- Customer name
- Status (open, in_progress, resolved, closed)
- Priority (low, medium, high, urgent)
- Category
- Created date
- Assigned staff
- Actions: View Details, Add Comment, Resolve

**API Endpoints:**
```javascript
// Get tickets
GET /api/crm/tickets/
Query params: ?status=open,in_progress&ordering=-priority,-created_at

// My assigned tickets
GET /api/crm/tickets/my_tickets/

// Get ticket details
GET /api/crm/tickets/{id}/

// Create ticket
POST /api/crm/tickets/
Body: {
  customer: customer_id,
  subject: "Equipment malfunction - Excavator XYZ",
  description: "Customer reports hydraulic issue",
  category: "equipment_issue",
  priority: "high"
}

// Add comment
POST /api/crm/tickets/{id}/add_comment/
Body: {
  comment: "Technician dispatched to check equipment",
  is_internal: false  // Customer can see this
}

// Resolve ticket
POST /api/crm/tickets/{id}/mark_resolved/
Body: {
  resolution_notes: "Issue fixed, replaced hydraulic pump"
}
```

#### 4.5 Ticket Detail Page

**Layout:**
- Ticket header (number, status, priority)
- Customer information panel
- Ticket description
- Comment thread (with internal/external indicators)
- Add comment form
- Related rental (if applicable)
- Status change buttons (In Progress, Resolve, Close)

---

### 5. Financial Section

#### 5.1 Revenue Dashboard

**Purpose:** Financial overview and insights

**Widgets:**

**A. Revenue Summary Cards**
- Today's Revenue
- This Week
- This Month
- This Year

**B. Revenue Chart**
- Line chart: Revenue over time (daily/weekly/monthly)
- Filter by date range
- Breakdown by equipment category (optional)

**C. Payment Status**
- Pending Payments (count & amount)
- Overdue Payments (count & amount)
- Completed This Month

**D. Top Revenue Equipment**
- Table/List of equipment generating most revenue
- Shows: Equipment name, Total revenue, Rental count

**API Endpoints:**
```javascript
// Revenue summary
GET /api/rentals/rental_summary/
Response: {
  total_rentals: 150,
  active_rentals: 12,
  total_revenue: 125000.00,
  monthly_revenue: 45000.00,
  average_rental_value: 833.33
}

// Revenue by period (custom aggregation may be needed)
GET /api/rentals/rentals/?owner_company=true&status=completed
// Frontend calculates totals by date ranges

// Payment tracking
GET /api/rentals/rentals/?owner_company=true&payment_status=pending
GET /api/rentals/rentals/?owner_company=true&payment_status=overdue
```

#### 5.2 Transaction History

**Layout:**
- Table of all transactions
- Export to CSV/PDF
- Date range filter

**Table Columns:**
- Date
- Transaction ID
- Rental ID (link)
- Customer
- Equipment
- Amount (AED)
- Payment Status
- Payment Method
- Actions: View Receipt, Download Invoice

**API Endpoints:**
```javascript
// Get rentals with payment info
GET /api/rentals/rentals/?owner_company=true&ordering=-payment_date

// Individual rental details (includes payment info)
GET /api/rentals/rentals/{id}/
```

---

### 6. Analytics Section

#### 6.1 Performance Metrics

**Widgets:**

**A. Key Performance Indicators (KPIs)**
- Booking Rate (bookings / total views)
- Average Rental Duration
- Customer Acquisition Rate
- Revenue Growth Rate
- Equipment Utilization Rate

**B. Equipment Utilization**
- Chart showing utilization % per equipment
- Identify underutilized equipment
- Target: >60% utilization

**C. Customer Insights**
- New vs Returning Customers
- Average Customer Lifetime Value
- Customer Retention Rate

**D. Booking Trends**
- Peak booking times (seasonality)
- Popular equipment categories
- Average booking value

**API Endpoints:**
```javascript
// Most endpoints will use aggregated data from rentals
GET /api/rentals/rentals/?owner_company=true
GET /api/equipment/my_equipment/
GET /api/accounts/customers/  // If accessible

// Frontend performs calculations for analytics
// Consider adding dedicated analytics endpoints in future
```

---

### 7. Settings Section

#### 7.1 Company Profile

**Form Fields:**
- Company Name
- Email
- Phone Number
- Location (dropdown)
- Trade License Number
- Trade License Expiry Date
- Company Description (textarea)
- Company Logo (image upload)
- Business Hours
- Bank Account Details (for payouts)

**API Endpoints:**
```javascript
// Get current profile
GET /api/accounts/profile/

// Update profile
PATCH /api/accounts/profile/
Body: {
  company_name: "Updated Company Name",
  phone: "+971509876543",
  location: "abu_dhabi"
}

// Upload company logo
POST /api/accounts/profile/upload_logo/
Content-Type: multipart/form-data
```

#### 7.2 Notification Settings

**Options:**
- Email notifications (on/off)
- SMS notifications (on/off)
- Notification types:
  - New rental request
  - Payment received
  - Equipment returned
  - Support ticket created
  - Review received
  - System updates

**API Endpoints:**
```javascript
// Get notification preferences
GET /api/accounts/notification-preferences/

// Update preferences
PATCH /api/accounts/notification-preferences/
Body: {
  email_notifications: true,
  rental_request_notifications: true,
  payment_notifications: true
}
```

---

## API Endpoints Reference

### Complete Endpoint List for Seller Dashboard

#### Authentication
```
POST   /api/accounts/register/                 - Register new account
POST   /api/accounts/token/                    - Login (get JWT tokens)
POST   /api/accounts/token/refresh/            - Refresh access token
POST   /api/accounts/token/verify/             - Verify token validity
GET    /api/accounts/profile/                  - Get user profile
PATCH  /api/accounts/profile/                  - Update profile
```

#### Equipment Management
```
GET    /api/equipment/my_equipment/            - List seller's equipment
GET    /api/equipment/equipment/{id}/          - Get equipment details
POST   /api/equipment/equipment/               - Create equipment
PUT    /api/equipment/equipment/{id}/          - Update equipment (full)
PATCH  /api/equipment/equipment/{id}/          - Update equipment (partial)
DELETE /api/equipment/equipment/{id}/          - Delete equipment
POST   /api/equipment/equipment/{id}/upload_image/          - Upload image
POST   /api/equipment/equipment/{id}/set_primary_image/     - Set primary image
POST   /api/equipment/equipment/{id}/toggle_availability/   - Toggle availability
GET    /api/equipment/equipment/{id}/check_availability/    - Check availability
GET    /api/equipment/categories/              - List categories
GET    /api/equipment/images/                  - List images
DELETE /api/equipment/images/{id}/             - Delete image
```

#### Rentals Management
```
GET    /api/rentals/rentals/                   - List all rentals
GET    /api/rentals/rentals/{id}/              - Get rental details
POST   /api/rentals/rentals/                   - Create rental (customer side)
PATCH  /api/rentals/rentals/{id}/              - Update rental
POST   /api/rentals/rentals/{id}/approve/      - Approve rental request
POST   /api/rentals/rentals/{id}/reject/       - Reject rental request
POST   /api/rentals/rentals/{id}/mark_delivered/    - Mark as delivered
POST   /api/rentals/rentals/{id}/mark_returned/     - Mark as returned
POST   /api/rentals/rentals/{id}/mark_completed/    - Mark as completed
POST   /api/rentals/rentals/{id}/cancel/            - Cancel rental
GET    /api/rentals/rental_summary/            - Get rental statistics
GET    /api/rentals/reviews/                   - List reviews
POST   /api/rentals/reviews/                   - Create review (customer)
```

#### CRM
```
GET    /api/crm/leads/                         - List leads
POST   /api/crm/leads/                         - Create lead
GET    /api/crm/leads/{id}/                    - Get lead details
PATCH  /api/crm/leads/{id}/                    - Update lead
DELETE /api/crm/leads/{id}/                    - Delete lead
POST   /api/crm/leads/{id}/mark_contacted/     - Mark lead contacted
POST   /api/crm/leads/{id}/convert_to_opportunity/  - Convert to opportunity

GET    /api/crm/opportunities/                 - List opportunities
POST   /api/crm/opportunities/                 - Create opportunity
GET    /api/crm/opportunities/{id}/            - Get opportunity details
PATCH  /api/crm/opportunities/{id}/            - Update opportunity
DELETE /api/crm/opportunities/{id}/            - Delete opportunity
GET    /api/crm/opportunities/pipeline/        - Get pipeline summary
POST   /api/crm/opportunities/{id}/mark_won/   - Mark as won
POST   /api/crm/opportunities/{id}/mark_lost/  - Mark as lost

GET    /api/crm/interactions/                  - List interactions
POST   /api/crm/interactions/                  - Create interaction
GET    /api/crm/interactions/{id}/             - Get interaction details
PATCH  /api/crm/interactions/{id}/             - Update interaction
DELETE /api/crm/interactions/{id}/             - Delete interaction

GET    /api/crm/tickets/                       - List support tickets
POST   /api/crm/tickets/                       - Create ticket
GET    /api/crm/tickets/{id}/                  - Get ticket details
PATCH  /api/crm/tickets/{id}/                  - Update ticket
GET    /api/crm/tickets/my_tickets/            - Get assigned tickets
POST   /api/crm/tickets/{id}/add_comment/      - Add ticket comment
POST   /api/crm/tickets/{id}/mark_resolved/    - Mark ticket resolved

GET    /api/crm/ticket-comments/               - List ticket comments
GET    /api/crm/customer-notes/                - List customer notes
POST   /api/crm/customer-notes/                - Create customer note
```

#### Notifications
```
GET    /api/notifications/                     - List notifications
GET    /api/notifications/unread/              - Get unread notifications
POST   /api/notifications/{id}/mark_read/      - Mark as read
POST   /api/notifications/mark_all_read/       - Mark all as read
GET    /api/notifications/unread_count/        - Get unread count
```

---

## Data Models & Interfaces

### TypeScript/JavaScript Interfaces (for Frontend)

```typescript
// User/Profile
interface User {
  id: number;
  email: string;
  user_type: 'customer' | 'company' | 'staff';
  company_name?: string;
  phone?: string;
  location?: string;
  trade_license_number?: string;
  is_verified: boolean;
  created_at: string;
}

// Equipment
interface Equipment {
  id: number;
  name: string;
  description: string;
  category: number;
  category_name: string;
  owner: number;
  owner_company_name: string;
  daily_rate: string;  // Decimal as string
  weekly_rate: string | null;
  monthly_rate: string | null;
  deposit_required: string;
  condition: 'new' | 'excellent' | 'good' | 'fair' | 'needs_repair';
  availability_status: 'available' | 'rented' | 'maintenance' | 'unavailable';
  location: string;
  serial_number?: string;
  manufacture_year?: number;
  manufacturer?: string;
  model?: string;
  specifications?: any;  // JSON object
  is_featured: boolean;
  insurance_included: boolean;
  delivery_available: boolean;
  times_rented: number;
  average_rating: number;
  primary_image?: string;  // URL
  images: EquipmentImage[];
  created_at: string;
  updated_at: string;
}

interface EquipmentImage {
  id: number;
  image: string;  // URL
  is_primary: boolean;
  uploaded_at: string;
}

// Category
interface Category {
  id: number;
  name: string;
  description?: string;
  equipment_count: number;
}

// Rental
interface Rental {
  id: number;
  equipment: number;
  equipment_name: string;
  equipment_image: string;
  renter: number;
  renter_name: string;
  renter_email: string;
  renter_phone: string;
  owner_company: number;
  owner_company_name: string;
  start_date: string;  // ISO date
  end_date: string;
  rental_duration_days: number;
  status: 'pending' | 'approved' | 'rejected' | 'in_progress' | 'delivered' | 
          'in_use' | 'returned' | 'completed' | 'cancelled' | 'overdue' | 
          'disputed' | 'maintenance_needed' | 'payment_pending' | 
          'payment_overdue' | 'refunded';
  total_amount: string;
  payment_status: 'pending' | 'partial' | 'paid' | 'refunded' | 'overdue';
  amount_paid: string;
  delivery_required: boolean;
  delivery_address?: string;
  special_requests?: string;
  rejection_reason?: string;
  cancellation_reason?: string;
  delivered_at?: string;
  returned_at?: string;
  payment_date?: string;
  created_at: string;
  updated_at: string;
}

// CRM Lead
interface Lead {
  id: number;
  customer?: number;
  customer_name: string;
  customer_email: string;
  customer_phone: string;
  company?: number;
  source: 'website' | 'referral' | 'phone' | 'email' | 'social_media' | 'other';
  status: 'new' | 'contacted' | 'qualified' | 'lost';
  notes?: string;
  assigned_to?: number;
  assigned_to_name?: string;
  contacted_at?: string;
  created_at: string;
  updated_at: string;
}

// CRM Sales Opportunity
interface SalesOpportunity {
  id: number;
  name: string;
  customer: number;
  customer_name: string;
  company: number;
  company_name: string;
  stage: 'lead' | 'qualified' | 'proposal' | 'negotiation' | 'won' | 'lost';
  value: string;  // Decimal
  probability: number;  // 0-100
  expected_close_date?: string;
  lead_source?: number;
  assigned_to?: number;
  assigned_to_name?: string;
  won_at?: string;
  lost_at?: string;
  lost_reason?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

// CRM Customer Interaction
interface CustomerInteraction {
  id: number;
  customer: number;
  customer_name: string;
  company: number;
  interaction_type: 'call' | 'email' | 'meeting' | 'chat' | 'site_visit';
  interaction_date: string;  // ISO datetime
  summary: string;
  follow_up_required: boolean;
  follow_up_date?: string;
  staff_member?: number;
  staff_member_name?: string;
  created_at: string;
}

// CRM Support Ticket
interface SupportTicket {
  id: number;
  ticket_number: string;  // Auto-generated
  customer: number;
  customer_name: string;
  company: number;
  company_name: string;
  subject: string;
  description: string;
  status: 'open' | 'in_progress' | 'resolved' | 'closed';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  category: 'general' | 'equipment_issue' | 'billing' | 'delivery' | 'other';
  assigned_to?: number;
  assigned_to_name?: string;
  related_rental?: number;
  resolution_notes?: string;
  resolved_at?: string;
  created_at: string;
  updated_at: string;
  comments: TicketComment[];
}

// Ticket Comment
interface TicketComment {
  id: number;
  ticket: number;
  author: number;
  author_name: string;
  comment: string;
  is_internal: boolean;  // Internal notes not visible to customer
  created_at: string;
}

// Notification
interface Notification {
  id: number;
  recipient: number;
  title: string;
  message: string;
  notification_type: 'info' | 'success' | 'warning' | 'error';
  is_read: boolean;
  related_rental?: number;
  related_equipment?: number;
  created_at: string;
}

// Review
interface Review {
  id: number;
  rental: number;
  equipment: number;
  equipment_name: string;
  reviewer: number;
  reviewer_name: string;
  rating: number;  // 1-5
  comment?: string;
  created_at: string;
}
```

---

## Real-time Features

### Notification Polling
Since this is a REST API (not WebSocket), implement polling for real-time updates:

```javascript
// Poll every 30 seconds for new notifications
setInterval(async () => {
  const response = await fetch('/api/notifications/unread_count/', {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });
  const data = await response.json();
  updateNotificationBadge(data.unread_count);
}, 30000);
```

### Badge Updates
Display badge counts on navigation items:
- **Pending Approvals** badge on Rentals menu
- **Unread Notifications** badge on bell icon
- **Open Tickets** badge on CRM/Support menu

---

## UI/UX Guidelines

### Design Principles
1. **Clean & Professional** - Business-focused design
2. **Data-Dense** - Show relevant information without clutter
3. **Quick Actions** - Primary actions easily accessible
4. **Responsive** - Mobile-friendly for on-the-go management
5. **Loading States** - Show skeletons/spinners during API calls
6. **Error Handling** - Clear error messages with retry options

### Color Scheme Suggestions
- **Primary:** Blue (#2563EB) - Actions, links
- **Success:** Green (#10B981) - Completed, approved
- **Warning:** Orange (#F59E0B) - Pending, attention needed
- **Danger:** Red (#EF4444) - Rejected, errors, urgent
- **Neutral:** Gray (#6B7280) - Text, borders

### Status Color Coding

**Rental Status:**
- Pending: Orange
- Approved: Blue
- In Progress/Delivered: Green
- Completed: Dark Green
- Rejected/Cancelled: Red
- Overdue: Red
- Disputed: Red

**Payment Status:**
- Pending: Orange
- Partial: Yellow
- Paid: Green
- Overdue: Red
- Refunded: Gray

**Ticket Priority:**
- Low: Gray
- Medium: Blue
- High: Orange
- Urgent: Red

### Icons Suggestions
Use icon library like Heroicons, Font Awesome, or Material Icons:
- Dashboard: 📊 (chart icon)
- Equipment: 🏗️ (construction icon)
- Rentals: 📋 (clipboard icon)
- CRM: 👥 (users icon)
- Financial: 💰 (currency icon)
- Analytics: 📈 (trending up icon)
- Settings: ⚙️ (cog icon)
- Notifications: 🔔 (bell icon)

---

## Sample API Calls

### Complete Flow Examples

#### Example 1: Viewing Pending Approvals and Approving a Rental

```javascript
// Step 1: Fetch pending rental requests
const response = await fetch(
  '/api/rentals/rentals/?owner_company=true&status=pending&ordering=-created_at',
  {
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    }
  }
);
const pendingRentals = await response.json();

// Step 2: User reviews rental details
const rentalId = pendingRentals.results[0].id;

// Step 3: Approve the rental
const approveResponse = await fetch(
  `/api/rentals/rentals/${rentalId}/approve/`,
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      message: 'Your rental request has been approved! Please proceed with payment.'
    })
  }
);

if (approveResponse.ok) {
  const approvedRental = await approveResponse.json();
  // Show success notification
  // Refresh pending list
  // Send notification to customer (handled by backend)
}
```

#### Example 2: Adding New Equipment with Images

```javascript
// Step 1: Prepare form data
const formData = new FormData();
formData.append('name', 'Caterpillar 320D Excavator');
formData.append('category', 2);  // Heavy Machinery category ID
formData.append('description', '20-ton hydraulic excavator...');
formData.append('daily_rate', '2500.00');
formData.append('weekly_rate', '15000.00');
formData.append('monthly_rate', '50000.00');
formData.append('deposit_required', '10000.00');
formData.append('condition', 'excellent');
formData.append('availability_status', 'available');
formData.append('location', 'dubai');
formData.append('manufacture_year', 2022);
formData.append('manufacturer', 'Caterpillar');
formData.append('model', '320D');
formData.append('is_featured', false);
formData.append('insurance_included', true);
formData.append('delivery_available', true);

// Step 2: Create equipment
const createResponse = await fetch('/api/equipment/equipment/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`
    // Don't set Content-Type for FormData, browser handles it
  },
  body: formData
});

const equipment = await createResponse.json();
const equipmentId = equipment.id;

// Step 3: Upload images (one by one)
const images = [file1, file2, file3];  // From file input

for (let imageFile of images) {
  const imageFormData = new FormData();
  imageFormData.append('image', imageFile);
  
  await fetch(`/api/equipment/equipment/${equipmentId}/upload_image/`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`
    },
    body: imageFormData
  });
}

// Step 4: Set first image as primary
const imageListResponse = await fetch(
  `/api/equipment/equipment/${equipmentId}/`,
  {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  }
);
const equipmentWithImages = await imageListResponse.json();
const firstImageId = equipmentWithImages.images[0].id;

await fetch(`/api/equipment/equipment/${equipmentId}/set_primary_image/`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ image_id: firstImageId })
});
```

#### Example 3: Dashboard Data Loading

```javascript
// Load all dashboard data in parallel
async function loadDashboard() {
  try {
    const [
      equipmentCountRes,
      activeRentalsRes,
      pendingApprovalsRes,
      revenueRes,
      recentActivityRes,
      topEquipmentRes
    ] = await Promise.all([
      // Total equipment count
      fetch('/api/equipment/my_equipment/', {
        headers: { 'Authorization': `Bearer ${accessToken}` }
      }),
      
      // Active rentals
      fetch('/api/rentals/rentals/?owner_company=true&status=in_progress,in_use,delivered', {
        headers: { 'Authorization': `Bearer ${accessToken}` }
      }),
      
      // Pending approvals
      fetch('/api/rentals/rentals/?owner_company=true&status=pending', {
        headers: { 'Authorization': `Bearer ${accessToken}` }
      }),
      
      // Revenue summary
      fetch('/api/rentals/rental_summary/', {
        headers: { 'Authorization': `Bearer ${accessToken}` }
      }),
      
      // Recent activity
      fetch('/api/rentals/rentals/?owner_company=true&ordering=-created_at&limit=10', {
        headers: { 'Authorization': `Bearer ${accessToken}` }
      }),
      
      // Top rented equipment
      fetch('/api/equipment/equipment/?ordering=-times_rented&limit=5', {
        headers: { 'Authorization': `Bearer ${accessToken}` }
      })
    ]);

    const equipmentData = await equipmentCountRes.json();
    const activeRentals = await activeRentalsRes.json();
    const pendingApprovals = await pendingApprovalsRes.json();
    const revenue = await revenueRes.json();
    const recentActivity = await recentActivityRes.json();
    const topEquipment = await topEquipmentRes.json();

    // Update dashboard UI
    updateDashboardMetrics({
      totalEquipment: equipmentData.count,
      activeRentals: activeRentals.count,
      pendingApprovals: pendingApprovals.count,
      monthlyRevenue: revenue.monthly_revenue
    });

    renderRecentActivity(recentActivity.results);
    renderTopEquipment(topEquipment.results);
    
  } catch (error) {
    console.error('Dashboard loading error:', error);
    showErrorNotification('Failed to load dashboard data');
  }
}
```

#### Example 4: Creating and Managing Support Ticket

```javascript
// Step 1: Customer creates ticket (or seller creates on behalf)
const createTicketRes = await fetch('/api/crm/tickets/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    customer: 15,  // Customer ID
    subject: 'Excavator hydraulic issue',
    description: 'The hydraulic arm is not responding properly',
    category: 'equipment_issue',
    priority: 'high',
    related_rental: 45  // Optional: link to rental
  })
});

const ticket = await createTicketRes.json();
const ticketId = ticket.id;

// Step 2: Add internal comment (not visible to customer)
await fetch(`/api/crm/tickets/${ticketId}/add_comment/`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    comment: 'Assigned to maintenance team, John will check tomorrow',
    is_internal: true
  })
});

// Step 3: Add customer-visible comment
await fetch(`/api/crm/tickets/${ticketId}/add_comment/`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    comment: 'Our technician will visit the site tomorrow morning to inspect the equipment.',
    is_internal: false
  })
});

// Step 4: Update ticket status
await fetch(`/api/crm/tickets/${ticketId}/`, {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    status: 'in_progress'
  })
});

// Step 5: Resolve ticket
await fetch(`/api/crm/tickets/${ticketId}/mark_resolved/`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    resolution_notes: 'Hydraulic pump replaced, equipment tested and working properly'
  })
});
```

---

## Error Handling

### Common HTTP Status Codes

```javascript
// Handle API errors consistently
async function apiCall(url, options) {
  try {
    const response = await fetch(url, options);
    
    if (!response.ok) {
      // Handle different error types
      switch (response.status) {
        case 400:
          // Validation errors
          const errors = await response.json();
          showValidationErrors(errors);
          break;
          
        case 401:
          // Unauthorized - token expired or invalid
          await refreshToken();  // Try to refresh
          // Retry the request or redirect to login
          break;
          
        case 403:
          // Forbidden - user doesn't have permission
          showError('You do not have permission to perform this action');
          break;
          
        case 404:
          // Not found
          showError('Resource not found');
          break;
          
        case 500:
          // Server error
          showError('Server error. Please try again later.');
          break;
          
        default:
          showError('An unexpected error occurred');
      }
      
      throw new Error(`HTTP ${response.status}`);
    }
    
    return await response.json();
    
  } catch (error) {
    if (error.name === 'TypeError') {
      // Network error
      showError('Network error. Please check your connection.');
    }
    throw error;
  }
}
```

### Validation Error Display

```javascript
// Display field-specific validation errors
function showValidationErrors(errors) {
  // errors format: { "field_name": ["Error message 1", "Error message 2"] }
  
  Object.keys(errors).forEach(fieldName => {
    const errorMessages = errors[fieldName];
    const fieldElement = document.querySelector(`[name="${fieldName}"]`);
    
    if (fieldElement) {
      // Add error class to field
      fieldElement.classList.add('error');
      
      // Display error message below field
      const errorDiv = document.createElement('div');
      errorDiv.className = 'error-message';
      errorDiv.textContent = errorMessages.join(', ');
      fieldElement.parentNode.appendChild(errorDiv);
    }
  });
}
```

---

## Performance Optimization

### Recommendations

1. **Pagination**
   - Most list endpoints support pagination
   - Use `?page=1&page_size=20` to limit results
   - Default page size is usually 10-20

2. **Lazy Loading**
   - Load dashboard widgets progressively
   - Implement infinite scroll for long lists

3. **Caching**
   - Cache categories, location choices (rarely change)
   - Cache user profile data
   - Implement cache invalidation on updates

4. **Debouncing**
   - Debounce search inputs (300-500ms)
   - Debounce filter changes

5. **Image Optimization**
   - Use thumbnail URLs for list views
   - Lazy load images below the fold
   - Implement image compression on upload

---

## Testing Checklist

### Authentication Flow
- [ ] Login with seller account
- [ ] Token refresh on expiration
- [ ] Logout clears tokens
- [ ] Unauthorized access redirects to login

### Equipment Management
- [ ] List all equipment with filters
- [ ] Create new equipment with images
- [ ] Edit equipment details
- [ ] Delete equipment (with confirmation)
- [ ] Toggle availability status
- [ ] Search equipment by name

### Rentals
- [ ] View pending approvals
- [ ] Approve rental request
- [ ] Reject rental request
- [ ] Mark rental as delivered
- [ ] Mark rental as returned
- [ ] View rental history with filters
- [ ] Calendar view shows bookings

### CRM
- [ ] Create and manage leads
- [ ] Convert lead to opportunity
- [ ] Update opportunity stage
- [ ] Log customer interactions
- [ ] Create and resolve support tickets
- [ ] Add ticket comments (internal/external)

### Dashboard
- [ ] All metrics load correctly
- [ ] Charts display data
- [ ] Recent activity shows latest items
- [ ] Quick actions work

### Notifications
- [ ] Notification badge shows count
- [ ] Clicking notification marks as read
- [ ] Notification list displays correctly

---

## Deployment Notes

### Environment Variables
Make sure to configure:
```
REACT_APP_API_BASE_URL=https://api.tezrent.com/api/
REACT_APP_JWT_EXPIRY=3600
```

### Build Optimization
- Minify JavaScript and CSS
- Enable gzip compression
- Use CDN for static assets
- Implement code splitting

### Browser Support
- Chrome (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Edge (latest 2 versions)

---

## Future Enhancements

### Phase 2 Features (Consider for future)
1. **Real-time Updates** - Implement WebSocket for live notifications
2. **Advanced Analytics** - More detailed charts and reports
3. **Bulk Operations** - Bulk edit, delete, export
4. **Mobile App** - Native mobile app for sellers
5. **Payment Integration** - Direct payment processing in dashboard
6. **Automated Workflows** - Auto-approve based on rules
7. **Calendar Integration** - Sync with Google Calendar
8. **Multi-language** - Support for Arabic and other languages

---

## Support & Resources

### Documentation
- **Master API Documentation:** See `MASTER_API_DOCUMENTATION.md`
- **Quick References:** Check `QUICK_REFERENCE.txt` files in each app folder
- **App-Specific Guides:** See individual `*_API_GUIDE.md` files

### Contact
For API questions or issues:
- **Developer:** Derngineer
- **Email:** dmatderby@gmail.com
- **Repository:** github.com/Derngineer/tezrent_api

---

## Appendix

### Location Choices (UAE & Uzbekistan)
```json
{
  "uae": [
    "dubai",
    "abu_dhabi",
    "sharjah",
    "ajman",
    "ras_al_khaimah",
    "fujairah",
    "umm_al_quwain"
  ],
  "uzbekistan": [
    "tashkent",
    "samarkand",
    "bukhara",
    "namangan",
    "andijan",
    "fergana",
    "nukus",
    "karshi",
    "termez"
  ]
}
```

### Equipment Categories (Examples)
- Heavy Machinery
- Construction Tools
- Power Tools
- Lifting Equipment
- Earthmoving Equipment
- Concrete Equipment
- Scaffolding
- Safety Equipment
- Others

### Rental Status Flow
```
pending → approved → in_progress → delivered → in_use → returned → completed
              ↓
           rejected
           
(can also go to: cancelled, disputed, overdue, maintenance_needed)
```

### CRM Lead Sources
- website
- referral
- phone
- email
- social_media
- other

### Support Ticket Categories
- general
- equipment_issue
- billing
- delivery
- other

### Priority Levels
- low
- medium
- high
- urgent

---

**End of Document**

This specification provides all the information needed to build a comprehensive seller dashboard for TezRent. For additional details, refer to the API documentation files in the repository.

**Version History:**
- v1.0 (October 22, 2025) - Initial specification
