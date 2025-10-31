# TezRent API - Accounts Quick Reference

## � REGISTRATION FIX - READ THIS FIRST!

### Your Registration Needs:
1. **`country` field** (Required!) - Add `"country": "UAE"` or `"country": "UZB"`
2. **City CODES not names** - Use `"DXB"` NOT `"dubai"`

**Working Example:**
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "Pass123!",
  "confirm_password": "Pass123!",
  "first_name": "First",
  "last_name": "Last",
  "phone_number": "+971507398212",
  "country": "UAE",  ← ADD THIS!
  "profile": {
    "company_name": "Company Name",
    "business_type": "LLC",
    "company_address": "Address",
    "city": "DXB",  ← Use DXB not dubai
    "tax_number": "TAX123",
    "company_phone": "+971507398212"
  }
}
```

**City Codes:** AUH (Abu Dhabi), DXB (Dubai), SHJ (Sharjah), AJM (Ajman), UAQ (Umm Al Quwain), FUJ (Fujairah), RAK (Ras Al Khaimah)

---

## �🔐 Authentication Endpoints

### Registration
```
POST /api/accounts/register/customer/     - Register new customer
POST /api/accounts/register/company/      - Register new seller/company
POST /api/accounts/seller/register/       - Register seller (alias for company)
```

### Login & Tokens
```
POST /api/accounts/token/                 - Login (get JWT tokens)
POST /api/accounts/token/refresh/         - Refresh access token
```

### Password Management
```
POST /api/accounts/password-reset/         - Request password reset (send email)
POST /api/accounts/password-reset/verify/  - Verify reset token validity
POST /api/accounts/password-reset/confirm/ - Reset password with token
POST /api/accounts/change-password/        - Change password (authenticated)
```

### Profile
```
GET  /api/accounts/profile/               - Get user profile
```

### Utility
```
GET  /api/accounts/location-choices/      - Get countries and cities
```

---

## 📝 Quick Examples

### Customer Registration
```javascript
POST /api/accounts/register/customer/
{
  "email": "customer@example.com",
  "username": "customer123",
  "password": "password123",
  "password2": "password123",
  "phone_number": "+971501234567",
  "country": "UAE",
  "first_name": "John",
  "last_name": "Doe"
}
```

### Company Registration
```javascript
POST /api/accounts/register/company/
{
  "email": "company@example.com",
  "username": "company123",
  "password": "password123",
  "password2": "password123",
  "phone_number": "+971501234567",
  "country": "UAE",
  "company_name": "ABC Equipment Rental",
  "trade_license_number": "TL123456",
  "first_name": "Jane",
  "last_name": "Smith"
}
```

### Login
```javascript
POST /api/accounts/token/
{
  "email": "user@example.com",
  "password": "password123"
}

Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Forgot Password
```javascript
POST /api/accounts/password-reset/
{
  "email": "user@example.com"
}
```

### Reset Password
```javascript
POST /api/accounts/password-reset/confirm/
{
  "uid": "MQ",
  "token": "abc123-xyz456",
  "new_password": "newpassword123",
  "confirm_password": "newpassword123"
}
```

### Change Password (Authenticated)
```javascript
POST /api/accounts/change-password/
Headers: Authorization: Bearer <access_token>
{
  "old_password": "currentpassword",
  "new_password": "newpassword123",
  "confirm_password": "newpassword123"
}
```

### Get Profile
```javascript
GET /api/accounts/profile/
Headers: Authorization: Bearer <access_token>
```

---

## 🔑 Authentication Headers

All protected endpoints require JWT token:
```
Authorization: Bearer <your_access_token>
```

---

## ⏱️ Token Lifetimes

- **Access Token:** 24 hours
- **Refresh Token:** 7 days

---

## 🌍 Location Choices

### Countries
- `UAE` - United Arab Emirates
- `UZB` - Uzbekistan

### UAE Cities
- `AUH` - Abu Dhabi
- `DXB` - Dubai
- `SHJ` - Sharjah
- `AJM` - Ajman
- `UAQ` - Umm Al Quwain
- `FUJ` - Fujairah
- `RAK` - Ras Al Khaimah

### Uzbekistan Cities
- `TAS` - Tashkent
- `SAM` - Samarkand
- `NAM` - Namangan
- `AND` - Andijan

---

## 👥 User Types

- `customer` - Regular customer renting equipment
- `company` - Seller/company offering equipment
- `staff` - Admin/staff user

---

## ⚠️ Common Errors

### 400 - Validation Error
```json
{
  "email": ["This field is required."],
  "password": ["This field may not be blank."]
}
```

### 401 - Invalid Credentials
```json
{
  "detail": "No active account found with the given credentials"
}
```

### 401 - Token Required
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

## 🧪 Test with cURL

### Register
```bash
curl -X POST http://localhost:8000/api/accounts/register/customer/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","username":"test","password":"test1234","password2":"test1234","phone_number":"+971501234567","country":"UAE","first_name":"Test","last_name":"User"}'
```

### Login
```bash
curl -X POST http://localhost:8000/api/accounts/token/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test1234"}'
```

### Get Profile
```bash
curl -X GET http://localhost:8000/api/accounts/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 📚 Full Documentation

See `FRONTEND_ACCOUNTS_INTEGRATION.md` for:
- Complete React component examples
- Authentication context setup
- Error handling patterns
- Protected routes implementation
- Full integration guide

---

## ✅ What's Ready

- ✅ Customer registration
- ✅ Company/seller registration
- ✅ JWT login & token refresh
- ✅ Password reset flow (3 steps)
- ✅ Change password for logged-in users
- ✅ User profile endpoint
- ✅ Location choices API
- ✅ CORS configured for localhost:3000
- ✅ Complete React examples provided

---

## 🚀 Next Steps for Frontend

1. Install dependencies: `react-router-dom` for routing
2. Create AuthContext using examples provided
3. Implement registration forms (customer & company)
4. Implement login form
5. Implement forgot password flow
6. Test all endpoints
7. Add error handling and loading states

---

**Base URL:** `http://localhost:8000/api/accounts/`  
**Frontend URL:** `http://localhost:3000` (already configured in CORS)
