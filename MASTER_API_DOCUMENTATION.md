# TEZRENT API - Master Documentation

## 📋 System Overview

TezRent is an equipment rental marketplace connecting customers who need machinery with companies that rent equipment. The platform supports multiple countries (UAE, Uzbekistan) and consists of:

- **Backend API** (Django REST Framework)
- **Customer App** (React Node) - Browse & rent equipment
- **Seller App** (React Native) - Manage equipment & rentals
- **Admin Panel** (Django Admin) - TezRent staff management

---

## 🏗️ Architecture

### Technology Stack
- **Framework**: Django 5.2.7
- **API**: Django REST Framework 3.16.1
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Database**: SQLite (development) / PostgreSQL (production)
- **File Storage**: Local/S3
- **CORS**: django-cors-headers

### Apps Structure

```
tezrent_api/
├── accounts/          # User management & authentication
├── equipment/         # Equipment catalog
├── rentals/           # Rental transactions
├── payments/          # Payment processing
├── crm/              # Customer relationship management
├── notifications/     # Push notifications & alerts
├── favorites/        # User favorites/wishlist
└── utils/            # Shared utilities
```

---

## 📱 Applications

### 1. **ACCOUNTS APP**
**Purpose**: User management, authentication, profiles

**Documentation**: `accounts/ACCOUNTS_API_GUIDE.md`

**Key Endpoints:**
- `POST /api/accounts/token/` - Login (get JWT)
- `POST /api/accounts/register/customer/` - Customer registration
- `POST /api/accounts/register/company/` - Seller registration
- `GET /api/accounts/profile/` - Get user profile
- `PUT /api/accounts/profile/` - Update profile

**Models:**
- User (custom email-based auth)
- CustomerProfile
- CompanyProfile
- StaffProfile

**Use Cases:**
- Customer/seller registration
- Login/logout
- Profile management
- Multi-country support (UAE, Uzbekistan)

---

### 2. **EQUIPMENT APP**
**Purpose**: Equipment catalog management

**Documentation**: `equipment/EQUIPMENT_API_GUIDE.md`

**Key Endpoints:**
- `GET /api/equipment/equipment/` - Browse equipment
- `GET /api/equipment/equipment/{id}/` - Equipment details
- `POST /api/equipment/equipment/` - Add equipment (seller)
- `GET /api/equipment/categories/` - List categories
- `GET /api/equipment/equipment/featured/` - Featured items
- `GET /api/equipment/equipment/todays_deals/` - Today's deals
- `GET /api/equipment/banners/active/` - Homepage banners

**Models:**
- Equipment
- Category
- EquipmentImage
- EquipmentSpecification
- Tag
- Banner

**Use Cases:**
- Browse equipment catalog
- Search & filter equipment
- Seller lists equipment
- Featured equipment homepage
- Daily deals & promotions

---

### 3. **RENTALS APP**
**Purpose**: Rental lifecycle management

**Documentation**: `rentals/RENTALS_API_GUIDE.md`

**Key Endpoints:**
- `GET /api/rentals/rentals/` - List rentals
- `POST /api/rentals/rentals/` - Create rental request
- `GET /api/rentals/rentals/{id}/` - Rental details
- `POST /api/rentals/rentals/{id}/approve/` - Approve rental (seller)
- `POST /api/rentals/rentals/{id}/mark_delivered/` - Mark delivered
- `POST /api/rentals/rentals/{id}/complete/` - Complete rental
- `POST /api/rentals/reviews/` - Submit review
- `GET /api/rentals/rentals/my_rentals/` - Customer's rentals
- `GET /api/rentals/rentals/pending_approvals/` - Seller pending

**Models:**
- Rental (15 statuses)
- RentalStatusUpdate
- RentalImage
- RentalReview
- RentalPayment
- RentalDocument

**Rental Status Flow:**
```
pending → approved → confirmed → preparing → 
ready_for_pickup → out_for_delivery → delivered → 
in_progress → return_requested → returning → completed
```

**Use Cases:**
- Customer requests rental
- Seller approves/rejects
- Payment processing
- Delivery tracking
- Return processing
- Review system

---

### 4. **CRM APP**
**Purpose**: Customer relationship & support management

**Documentation**: `crm/CRM_COMPLETE_GUIDE.md` & `crm/QUICK_REFERENCE.txt`

**Key Endpoints:**
- `GET /api/crm/leads/` - List leads (staff/seller)
- `POST /api/crm/leads/` - Create lead
- `POST /api/crm/leads/{id}/convert_to_opportunity/` - Convert
- `GET /api/crm/opportunities/pipeline/` - Sales pipeline
- `GET /api/crm/tickets/` - Support tickets
- `POST /api/crm/tickets/` - Create ticket
- `POST /api/crm/tickets/{id}/add_comment/` - Add comment
- `GET /api/crm/tickets/my_tickets/` - Customer tickets

**Models:**
- Lead
- SalesOpportunity
- CustomerInteraction
- SupportTicket
- TicketComment
- CustomerNote
- CustomerSegment

**Permissions:**
- **Staff**: Full access to all CRM data
- **Sellers**: Access only their company's data
- **Customers**: Create/view own support tickets

**Automation:**
- Large rentals (≥10k AED or ≥30 days) → Auto-create opportunity
- Rental dispute → Auto-create support ticket
- 5+ favorites in 7 days → Auto-create lead
- Ticket comments → Notifications

**Use Cases:**
- Staff manages sales leads
- Sellers track opportunities
- Customers create support tickets
- Internal customer notes
- Sales pipeline tracking

---

### 5. **FAVORITES APP**
**Purpose**: Customer wishlist & favorites

**Documentation**: `FAVORITES_API.md`

**Key Endpoints:**
- `GET /api/favorites/` - List favorites
- `POST /api/favorites/` - Add to favorites
- `DELETE /api/favorites/{id}/` - Remove favorite
- `GET /api/favorites/check/?equipment={id}` - Check if favorited

**Models:**
- Favorite

**Use Cases:**
- Customer saves favorite equipment
- Quick access to saved items
- CRM lead generation (5+ favorites → lead)

---

### 6. **NOTIFICATIONS APP**
**Purpose**: User notifications

**Documentation**: `notifications/NOTIFICATIONS_API_GUIDE.md`

**Key Endpoints:**
- `GET /api/notifications/` - List notifications
- `POST /api/notifications/{id}/mark_read/` - Mark as read
- `POST /api/notifications/mark_all_read/` - Mark all read
- `GET /api/notifications/unread_count/` - Badge count

**Models:**
- Notification

**Notification Types:**
- Rental status updates
- Payment confirmations
- Review received
- Support ticket responses
- System announcements

**Use Cases:**
- Real-time rental updates
- Push notifications
- In-app notifications
- Notification badges

---

### 7. **PAYMENTS APP**
**Purpose**: Payment processing (placeholder)

**Status**: Structure created, awaiting integration

**Planned Integration:**
- Stripe
- PayPal
- Local payment gateways

---

## 🔗 Complete API Endpoint List

### Authentication & Accounts
```
POST   /api/accounts/token/                        # Login
POST   /api/accounts/token/refresh/                # Refresh token
POST   /api/accounts/register/customer/            # Register customer
POST   /api/accounts/register/company/             # Register seller
GET    /api/accounts/profile/                      # Get profile
PUT    /api/accounts/profile/                      # Update profile
GET    /api/accounts/location-choices/             # Location data
```

### Equipment
```
GET    /api/equipment/categories/                  # List categories
GET    /api/equipment/categories/featured/         # Featured categories
GET    /api/equipment/categories/{id}/equipment/   # Category equipment
GET    /api/equipment/equipment/                   # List equipment
GET    /api/equipment/equipment/{id}/              # Equipment detail
POST   /api/equipment/equipment/                   # Add equipment (seller)
PUT    /api/equipment/equipment/{id}/              # Update equipment
DELETE /api/equipment/equipment/{id}/              # Delete equipment
GET    /api/equipment/equipment/featured/          # Featured equipment
GET    /api/equipment/equipment/todays_deals/      # Daily deals
GET    /api/equipment/equipment/my_equipment/      # Seller's equipment
POST   /api/equipment/images/                      # Upload image
GET    /api/equipment/banners/active/              # Active banners
```

### Rentals
```
GET    /api/rentals/rentals/                       # List rentals
POST   /api/rentals/rentals/                       # Create rental
GET    /api/rentals/rentals/{id}/                  # Rental detail
POST   /api/rentals/rentals/{id}/approve/          # Approve (seller)
POST   /api/rentals/rentals/{id}/cancel/           # Cancel
POST   /api/rentals/rentals/{id}/update_status/    # Update status
POST   /api/rentals/rentals/{id}/mark_delivered/   # Mark delivered
POST   /api/rentals/rentals/{id}/request_return/   # Request return
POST   /api/rentals/rentals/{id}/complete/         # Complete
GET    /api/rentals/rentals/my_rentals/            # Customer rentals
GET    /api/rentals/rentals/pending_approvals/     # Seller pending
GET    /api/rentals/rentals/active_rentals/        # Seller active
GET    /api/rentals/reviews/                       # List reviews
POST   /api/rentals/reviews/                       # Create review
```

### CRM
```
GET    /api/crm/leads/                             # List leads
POST   /api/crm/leads/                             # Create lead
GET    /api/crm/leads/{id}/                        # Lead detail
POST   /api/crm/leads/{id}/mark_contacted/         # Mark contacted
POST   /api/crm/leads/{id}/convert_to_opportunity/ # Convert
GET    /api/crm/opportunities/                     # List opportunities
GET    /api/crm/opportunities/pipeline/            # Pipeline summary
POST   /api/crm/opportunities/{id}/mark_won/       # Mark won
POST   /api/crm/opportunities/{id}/mark_lost/      # Mark lost
GET    /api/crm/tickets/                           # Support tickets
POST   /api/crm/tickets/                           # Create ticket
GET    /api/crm/tickets/{id}/                      # Ticket detail
POST   /api/crm/tickets/{id}/add_comment/          # Add comment
POST   /api/crm/tickets/{id}/mark_resolved/        # Resolve
GET    /api/crm/tickets/my_tickets/                # Customer tickets
POST   /api/crm/customer-notes/                    # Add customer note
GET    /api/crm/interactions/                      # List interactions
```

### Favorites
```
GET    /api/favorites/                             # List favorites
POST   /api/favorites/                             # Add favorite
DELETE /api/favorites/{id}/                        # Remove favorite
GET    /api/favorites/check/?equipment={id}        # Check favorite
```

### Notifications
```
GET    /api/notifications/                         # List notifications
POST   /api/notifications/{id}/mark_read/          # Mark read
POST   /api/notifications/mark_all_read/           # Mark all read
GET    /api/notifications/unread_count/            # Unread count
```

---

## 🔐 Authentication

### JWT Token Flow

1. **Login**
```bash
curl -X POST http://localhost:8000/api/accounts/token/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"pass123"}'
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

2. **Use Access Token**
```bash
curl -X GET http://localhost:8000/api/equipment/equipment/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

3. **Refresh Token (when access expires)**
```bash
curl -X POST http://localhost:8000/api/accounts/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh":"eyJ0eXAiOiJKV1QiLCJhbGc..."}'
```

---

## 👥 User Roles & Permissions

### Customer
- Browse & search equipment
- Create rental requests
- View own rentals & reviews
- Create support tickets
- Manage favorites
- View notifications

### Company/Seller
- List & manage equipment
- Approve/reject rental requests
- Update rental status
- View equipment analytics
- Respond to support tickets
- View company leads & opportunities
- Add customer notes

### Staff
- Full access to all features
- Manage CRM (leads, opportunities)
- View all rentals & equipment
- Handle support tickets
- Access admin panel
- User management
- System configuration

---

## 📱 React Native Integration

### Setup

```javascript
// api.js - API client setup
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_BASE_URL = 'https://api.tezrent.com';

export const api = {
  async get(endpoint, params = {}) {
    const token = await AsyncStorage.getItem('access_token');
    const queryString = new URLSearchParams(params).toString();
    const url = `${API_BASE_URL}${endpoint}${queryString ? '?' + queryString : ''}`;
    
    const response = await fetch(url, {
      headers: {
        'Authorization': token ? `Bearer ${token}` : '',
      }
    });
    
    if (response.status === 401) {
      // Token expired, refresh
      await this.refreshToken();
      return this.get(endpoint, params);
    }
    
    return response.json();
  },
  
  async post(endpoint, data, isFormData = false) {
    const token = await AsyncStorage.getItem('access_token');
    
    const options = {
      method: 'POST',
      headers: {
        'Authorization': token ? `Bearer ${token}` : '',
      },
      body: isFormData ? data : JSON.stringify(data)
    };
    
    if (!isFormData) {
      options.headers['Content-Type'] = 'application/json';
    }
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
    
    if (response.status === 401) {
      await this.refreshToken();
      return this.post(endpoint, data, isFormData);
    }
    
    return response.json();
  },
  
  async refreshToken() {
    const refresh = await AsyncStorage.getItem('refresh_token');
    const response = await fetch(`${API_BASE_URL}/api/accounts/token/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh })
    });
    
    const data = await response.json();
    await AsyncStorage.setItem('access_token', data.access);
    return data.access;
  }
};
```

### Common Patterns

**Browse Equipment:**
```javascript
const equipment = await api.get('/api/equipment/equipment/', {
  category: 1,
  city: 'DXB',
  min_price: 100,
  max_price: 1000
});
```

**Create Rental:**
```javascript
const rental = await api.post('/api/rentals/rentals/', {
  equipment: 101,
  start_date: '2025-10-25',
  end_date: '2025-11-05',
  delivery_address: 'Dubai Marina'
});
```

**Upload Image:**
```javascript
const formData = new FormData();
formData.append('equipment', equipmentId);
formData.append('image', {
  uri: imageUri,
  type: 'image/jpeg',
  name: 'photo.jpg'
});

const result = await api.post('/api/equipment/images/', formData, true);
```

---

## 🧪 Testing

### Run Development Server
```bash
python manage.py runserver
```

### Test with curl

**Login:**
```bash
curl -X POST http://localhost:8000/api/accounts/token/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"pass123"}'
```

**List Equipment:**
```bash
curl http://localhost:8000/api/equipment/equipment/
```

**Create Rental (authenticated):**
```bash
curl -X POST http://localhost:8000/api/rentals/rentals/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "equipment": 1,
    "start_date": "2025-11-01",
    "end_date": "2025-11-10",
    "customer_phone": "+971501234567",
    "customer_email": "test@example.com"
  }'
```

---

## 📊 Database Schema Overview

### Core Relationships

```
User (1) ──── (1) CustomerProfile
     (1) ──── (1) CompanyProfile
     (1) ──── (1) StaffProfile

CustomerProfile (1) ──── (N) Rental
CompanyProfile (1) ──── (N) Equipment
CompanyProfile (1) ──── (N) Rental (as seller)

Equipment (1) ──── (N) Rental
Equipment (1) ──── (N) EquipmentImage
Equipment (1) ──── (N) EquipmentSpecification
Equipment (N) ──── (1) Category

Rental (1) ──── (N) RentalStatusUpdate
Rental (1) ──── (N) RentalImage
Rental (1) ──── (1) RentalReview
Rental (1) ──── (N) RentalPayment

Lead (1) ──── (1) SalesOpportunity
SupportTicket (1) ──── (N) TicketComment
```

---

## 🚀 Deployment

### Environment Variables
```bash
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=api.tezrent.com
DATABASE_URL=postgresql://user:pass@host:5432/db
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_STORAGE_BUCKET_NAME=tezrent-media
```

### Production Checklist
- [ ] Set DEBUG=False
- [ ] Configure PostgreSQL
- [ ] Set up S3 for media files
- [ ] Configure CORS for frontend domains
- [ ] Set up SSL certificate
- [ ] Configure email backend
- [ ] Set up payment gateway (Stripe/PayPal)
- [ ] Configure push notifications
- [ ] Set up monitoring (Sentry)
- [ ] Configure backups

---

## 📞 Support & Contact

**Admin Panel**: `http://localhost:8000/admin/`
**API Base URL**: `http://localhost:8000/api/`

**Documentation Files:**
- `accounts/ACCOUNTS_API_GUIDE.md` - Authentication & user management
- `equipment/EQUIPMENT_API_GUIDE.md` - Equipment catalog
- `rentals/RENTALS_API_GUIDE.md` - Rental transactions
- `crm/CRM_COMPLETE_GUIDE.md` - CRM system (full guide)
- `crm/QUICK_REFERENCE.txt` - CRM quick reference
- `notifications/NOTIFICATIONS_API_GUIDE.md` - Notifications
- `FAVORITES_API.md` - Favorites system
- `ADMIN_GUIDE.md` - Admin panel guide

---

## 🎯 Quick Start Guide

### For Developers

1. **Clone & Setup**
```bash
git clone <repository>
cd tezrent_api
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
pip install -r requirements.txt
```

2. **Database**
```bash
python manage.py migrate
python manage.py createsuperuser
```

3. **Run Server**
```bash
python manage.py runserver
```

4. **Create Test Data**
- Login to admin: `http://localhost:8000/admin/`
- Create categories, equipment, users
- Test API endpoints

### For Mobile Developers

1. **Read Documentation**
- Start with `MASTER_API_DOCUMENTATION.md` (this file)
- Read specific app guides as needed

2. **Authentication**
- Implement JWT login flow
- Store tokens securely (AsyncStorage)
- Handle token refresh

3. **API Integration**
- Use provided React Native examples
- Implement error handling
- Add loading states

4. **Test**
- Test with development server
- Handle offline scenarios
- Implement caching if needed

---

**End of Master API Documentation** 📚

**Version**: 1.0  
**Last Updated**: October 21, 2025  
**API Base URL**: `http://localhost:8000/api/` (development)
