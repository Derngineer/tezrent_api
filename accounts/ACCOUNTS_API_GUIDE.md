# ACCOUNTS APP - Complete API Documentation

## 📋 Overview

The Accounts app handles user authentication, registration, and profile management for the TezRent platform. It supports three types of users: **Customers** (renters), **Companies** (equipment sellers), and **Staff** (internal team).

### Key Features
- JWT-based authentication
- Email-based login (no username required)
- Separate registration flows for customers and companies
- Multi-country support (UAE, Uzbekistan)
- Profile management
- Location-based user data

---

## 🗄️ Models

### **1. User** (Custom User Model)
Extends Django's AbstractUser with email-based authentication.

**Fields:**
- `email` (unique) - Primary login identifier
- `username` - Required by Django admin, auto-generated
- `phone_number` - Optional contact number
- `country` - Country code (UAE, UZB)
- `user_type` - Type of user (customer, company, staff)
- `first_name`, `last_name` - User's name
- `is_active`, `is_staff`, `is_superuser` - Django permissions

**User Types:**
- `customer` - Regular users who rent equipment
- `company` - Equipment sellers/providers
- `staff` - TezRent internal team members

### **2. CustomerProfile**
Extended profile for individual customers.

**Fields:**
- `user` (OneToOne) - Link to User model
- `date_of_birth` - Customer's birthdate
- `city` - City code (AUH, DXB, TAS, etc.)
- `address` - Street address
- `profile_picture` - Avatar image
- `id_document` - ID verification document
- `id_verified` - Verification status
- `preferred_language` - UI language preference
- `total_rentals` - Count of completed rentals
- `average_rating` - Average review rating
- `created_at` - Profile creation timestamp

**Computed Properties:**
- `full_name` - First name + Last name
- `age` - Calculated from date_of_birth
- `profile_picture_url` - Full URL for image

### **3. CompanyProfile**
Extended profile for equipment rental companies/sellers.

**Fields:**
- `user` (OneToOne) - Link to User model
- `company_name` - Business name
- `trade_license_number` - License number
- `trade_license_document` - License upload
- `tax_registration_number` - Tax ID
- `city` - Operating city
- `address` - Business address
- `company_logo` - Brand logo
- `description` - Company bio
- `website` - Company website URL
- `business_hours` - Operating hours
- `is_verified` - TezRent verification status
- `verification_date` - When verified
- `total_equipment` - Number of listed items
- `total_rentals_completed` - Completed rental count
- `average_rating` - Seller rating
- `created_at` - Registration timestamp

**Computed Properties:**
- `company_logo_url` - Full URL for logo

### **4. StaffProfile**
Extended profile for TezRent staff members.

**Fields:**
- `user` (OneToOne) - Link to User model
- `employee_id` - Internal employee number
- `department` - Department name
- `position` - Job title
- `hire_date` - Employment start date
- `profile_picture` - Staff photo
- `created_at` - Profile creation timestamp

---

## 🔗 API Endpoints

### **Authentication**

#### 1. Login (Get JWT Token)
```
POST /api/accounts/token/
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Usage:**
- Use `access` token in Authorization header: `Bearer <access_token>`
- Access tokens expire in 60 minutes (default)
- Use refresh token to get new access token

---

#### 2. Refresh Token
```
POST /api/accounts/token/refresh/
```

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### **Registration**

#### 3. Customer Registration
```
POST /api/accounts/register/customer/
```

**Request Body:**
```json
{
  "email": "customer@example.com",
  "password": "securepass123",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+971501234567",
  "country": "UAE",
  "city": "DXB",
  "address": "Dubai Marina, Building 5, Apt 201",
  "date_of_birth": "1990-05-15"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "email": "customer@example.com",
  "user_type": "customer",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+971501234567",
  "country": "UAE",
  "profile": {
    "id": 1,
    "city": "DXB",
    "address": "Dubai Marina, Building 5, Apt 201",
    "date_of_birth": "1990-05-15",
    "id_verified": false,
    "total_rentals": 0,
    "average_rating": null
  }
}
```

**Validation:**
- Email must be unique
- Password min 8 characters
- Country must be UAE or UZB
- City must match country

---

#### 4. Company Registration
```
POST /api/accounts/register/company/
```

**Request Body:**
```json
{
  "email": "company@example.com",
  "password": "securepass123",
  "phone_number": "+971501234567",
  "country": "UAE",
  "company_name": "Dubai Equipment Rentals LLC",
  "trade_license_number": "TL-12345-2024",
  "tax_registration_number": "TAX-67890",
  "city": "DXB",
  "address": "Al Quoz Industrial Area 3, Warehouse 15",
  "description": "Leading equipment rental provider in Dubai",
  "website": "https://dubaiequipment.ae",
  "business_hours": "Sun-Thu: 8AM-6PM, Sat: 9AM-2PM"
}
```

**With File Uploads (multipart/form-data):**
```
POST /api/accounts/register/company/
Content-Type: multipart/form-data

Fields:
- email, password, company_name, etc. (as above)
- trade_license_document: [file]
- company_logo: [file]
```

**Response (201 Created):**
```json
{
  "id": 2,
  "email": "company@example.com",
  "user_type": "company",
  "phone_number": "+971501234567",
  "country": "UAE",
  "profile": {
    "id": 1,
    "company_name": "Dubai Equipment Rentals LLC",
    "trade_license_number": "TL-12345-2024",
    "tax_registration_number": "TAX-67890",
    "city": "DXB",
    "address": "Al Quoz Industrial Area 3, Warehouse 15",
    "description": "Leading equipment rental provider in Dubai",
    "website": "https://dubaiequipment.ae",
    "business_hours": "Sun-Thu: 8AM-6PM, Sat: 9AM-2PM",
    "is_verified": false,
    "total_equipment": 0,
    "total_rentals_completed": 0,
    "average_rating": null
  }
}
```

---

### **Profile Management**

#### 5. Get Current User Profile
```
GET /api/accounts/profile/
Authorization: Bearer <access_token>
```

**Response (200 OK) - Customer:**
```json
{
  "id": 1,
  "email": "customer@example.com",
  "user_type": "customer",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+971501234567",
  "country": "UAE",
  "profile": {
    "id": 1,
    "full_name": "John Doe",
    "city": "DXB",
    "address": "Dubai Marina, Building 5, Apt 201",
    "date_of_birth": "1990-05-15",
    "age": 35,
    "profile_picture_url": "https://api.tezrent.com/media/profiles/john.jpg",
    "id_verified": true,
    "total_rentals": 12,
    "average_rating": 4.8
  }
}
```

**Response (200 OK) - Company:**
```json
{
  "id": 2,
  "email": "company@example.com",
  "user_type": "company",
  "phone_number": "+971501234567",
  "country": "UAE",
  "profile": {
    "id": 1,
    "company_name": "Dubai Equipment Rentals LLC",
    "company_logo_url": "https://api.tezrent.com/media/logos/company.png",
    "city": "DXB",
    "address": "Al Quoz Industrial Area 3, Warehouse 15",
    "description": "Leading equipment rental provider in Dubai",
    "website": "https://dubaiequipment.ae",
    "is_verified": true,
    "verification_date": "2025-01-15T10:30:00Z",
    "total_equipment": 45,
    "total_rentals_completed": 230,
    "average_rating": 4.9
  }
}
```

---

#### 6. Update User Profile
```
PUT /api/accounts/profile/
Authorization: Bearer <access_token>
```

**Request Body (Customer):**
```json
{
  "first_name": "John",
  "last_name": "Smith",
  "phone_number": "+971509876543",
  "profile": {
    "address": "New Address, Dubai",
    "city": "DXB",
    "preferred_language": "en"
  }
}
```

**Request Body (Company):**
```json
{
  "phone_number": "+971501234567",
  "profile": {
    "company_name": "Dubai Equipment Rentals LLC",
    "description": "Updated description",
    "website": "https://newwebsite.ae",
    "business_hours": "Sun-Thu: 7AM-7PM"
  }
}
```

**With File Upload:**
```
PUT /api/accounts/profile/
Content-Type: multipart/form-data

Fields:
- first_name, last_name, etc.
- profile.profile_picture: [file]  # For customers
- profile.company_logo: [file]     # For companies
```

---

#### 7. Partial Update Profile
```
PATCH /api/accounts/profile/
Authorization: Bearer <access_token>
```

**Request Body (update only phone):**
```json
{
  "phone_number": "+971509999999"
}
```

**Request Body (update only address):**
```json
{
  "profile": {
    "address": "New Address Only"
  }
}
```

---

### **Utility Endpoints**

#### 8. Get Location Choices
```
GET /api/accounts/location-choices/
```

**Response (200 OK):**
```json
{
  "countries": [
    {"code": "UAE", "name": "United Arab Emirates"},
    {"code": "UZB", "name": "Uzbekistan"}
  ],
  "cities": {
    "UAE": [
      {"code": "AUH", "name": "Abu Dhabi"},
      {"code": "DXB", "name": "Dubai"},
      {"code": "SHJ", "name": "Sharjah"},
      {"code": "AJM", "name": "Ajman"},
      {"code": "UAQ", "name": "Umm Al Quwain"},
      {"code": "FUJ", "name": "Fujairah"},
      {"code": "RAK", "name": "Ras Al Khaimah"}
    ],
    "UZB": [
      {"code": "TAS", "name": "Tashkent"},
      {"code": "SAM", "name": "Samarkand"},
      {"code": "NAM", "name": "Namangan"},
      {"code": "AND", "name": "Andijan"}
    ]
  }
}
```

**Usage:** Populate dropdowns in registration forms

---

## 🔐 Authentication Flow

### React Native Example

```javascript
import AsyncStorage from '@react-native-async-storage/async-storage';

// 1. Login
const login = async (email, password) => {
  const response = await fetch('https://api.tezrent.com/api/accounts/token/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  
  const data = await response.json();
  
  // Store tokens
  await AsyncStorage.setItem('access_token', data.access);
  await AsyncStorage.setItem('refresh_token', data.refresh);
  
  return data;
};

// 2. Make authenticated request
const getProfile = async () => {
  const token = await AsyncStorage.getItem('access_token');
  
  const response = await fetch('https://api.tezrent.com/api/accounts/profile/', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return await response.json();
};

// 3. Refresh token when expired
const refreshToken = async () => {
  const refresh = await AsyncStorage.getItem('refresh_token');
  
  const response = await fetch('https://api.tezrent.com/api/accounts/token/refresh/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh })
  });
  
  const data = await response.json();
  await AsyncStorage.setItem('access_token', data.access);
  
  return data.access;
};

// 4. Handle 401 errors (token expired)
const apiCall = async (url, options = {}) => {
  let token = await AsyncStorage.getItem('access_token');
  
  let response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${token}`
    }
  });
  
  // If 401, refresh and retry
  if (response.status === 401) {
    token = await refreshToken();
    response = await fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${token}`
      }
    });
  }
  
  return response;
};
```

---

## 📱 Registration Flow Examples

### Customer Registration (React Native)

```javascript
const registerCustomer = async (formData) => {
  const response = await fetch('https://api.tezrent.com/api/accounts/register/customer/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email: formData.email,
      password: formData.password,
      first_name: formData.firstName,
      last_name: formData.lastName,
      phone_number: formData.phone,
      country: formData.country,
      city: formData.city,
      address: formData.address,
      date_of_birth: formData.dob
    })
  });
  
  if (response.ok) {
    const user = await response.json();
    // Auto-login after registration
    return await login(formData.email, formData.password);
  } else {
    const errors = await response.json();
    throw new Error(JSON.stringify(errors));
  }
};
```

### Company Registration with File Upload

```javascript
const registerCompany = async (formData, files) => {
  const form = new FormData();
  
  // Add text fields
  form.append('email', formData.email);
  form.append('password', formData.password);
  form.append('phone_number', formData.phone);
  form.append('country', formData.country);
  form.append('company_name', formData.companyName);
  form.append('trade_license_number', formData.licenseNumber);
  form.append('city', formData.city);
  form.append('address', formData.address);
  
  // Add files
  if (files.logo) {
    form.append('company_logo', {
      uri: files.logo.uri,
      type: 'image/jpeg',
      name: 'logo.jpg'
    });
  }
  
  if (files.license) {
    form.append('trade_license_document', {
      uri: files.license.uri,
      type: 'application/pdf',
      name: 'license.pdf'
    });
  }
  
  const response = await fetch('https://api.tezrent.com/api/accounts/register/company/', {
    method: 'POST',
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    body: form
  });
  
  return await response.json();
};
```

---

## ⚙️ Common Use Cases

### 1. User Login Flow
```
Customer App:
1. User enters email + password
2. POST /api/accounts/token/
3. Store access & refresh tokens
4. GET /api/accounts/profile/ to get user details
5. Navigate to home screen
```

### 2. Profile Picture Update
```
1. User selects image from gallery
2. Create FormData with image file
3. PATCH /api/accounts/profile/
   Content-Type: multipart/form-data
   Body: profile.profile_picture = [file]
4. Display updated profile_picture_url
```

### 3. Check if Email Exists
```
Try to register with email
If 400 error with "email already exists"
  → Show "Login instead" option
```

### 4. Location Dropdown Population
```
1. GET /api/accounts/location-choices/
2. Populate country dropdown from countries array
3. When country selected, show cities for that country
4. Store selected codes (DXB, UAE) not names
```

---

## 🛠️ Admin Interface

Access: `http://localhost:8000/admin/accounts/`

**Available Models:**
- Users - Manage all users
- Customer Profiles - Customer details
- Company Profiles - Seller details
- Staff Profiles - Internal staff

**Admin Features:**
- Search users by email, name, phone
- Filter by user type, country, verification status
- Verify company accounts
- View user statistics (rentals, ratings)
- Manage user permissions

---

## 🔒 Permissions

| Action | Anonymous | Customer | Company | Staff |
|--------|-----------|----------|---------|-------|
| Register Customer | ✅ | ❌ | ❌ | ❌ |
| Register Company | ✅ | ❌ | ❌ | ❌ |
| Login | ✅ | ✅ | ✅ | ✅ |
| View Own Profile | ❌ | ✅ | ✅ | ✅ |
| Update Own Profile | ❌ | ✅ | ✅ | ✅ |
| View Other Profiles | ❌ | Company Only* | Company Only* | ✅ |
| Verify Company | ❌ | ❌ | ❌ | ✅ |

*Customers/Companies can view basic public info of sellers when browsing equipment

---

## 🐛 Common Errors

### 400 Bad Request
```json
{
  "email": ["This field is required."],
  "password": ["This field may not be blank."]
}
```
**Solution:** Check all required fields are provided

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```
**Solution:** Include `Authorization: Bearer <token>` header

### 401 Token Expired
```json
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid"
}
```
**Solution:** Use refresh token to get new access token

### 400 Email Exists
```json
{
  "email": ["user with this email address already exists."]
}
```
**Solution:** Email already registered, user should login instead

---

## 📊 Field Validation

### Email
- Must be valid email format
- Must be unique
- Case-insensitive

### Password
- Minimum 8 characters (Django default)
- Cannot be too common
- Cannot be entirely numeric

### Phone Number
- Format: +[country code][number]
- Example: +971501234567
- No strict validation (flexible for international)

### Country/City
- Must match predefined choices
- City must belong to selected country

### Company Fields
- `trade_license_number` - Required, max 50 chars
- `company_name` - Required, max 255 chars
- `tax_registration_number` - Optional, max 50 chars

---

## 🚀 Testing with curl

```bash
# Login
curl -X POST http://localhost:8000/api/accounts/token/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'

# Get profile
curl -X GET http://localhost:8000/api/accounts/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Register customer
curl -X POST http://localhost:8000/api/accounts/register/customer/ \
  -H "Content-Type: application/json" \
  -d '{
    "email":"customer@test.com",
    "password":"pass123",
    "first_name":"John",
    "last_name":"Doe",
    "country":"UAE",
    "city":"DXB"
  }'

# Update profile
curl -X PATCH http://localhost:8000/api/accounts/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"phone_number":"+971509999999"}'
```

---

## 📄 Files Reference

- `accounts/models.py` - User, CustomerProfile, CompanyProfile, StaffProfile models
- `accounts/serializers.py` - API serializers for registration and profile
- `accounts/views.py` - Registration and profile views
- `accounts/urls.py` - URL routing
- `accounts/admin.py` - Django admin configuration

---

**End of Accounts API Documentation** 📚
