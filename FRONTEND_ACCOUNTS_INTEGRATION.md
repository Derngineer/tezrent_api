# TezRent Accounts API - React Frontend Integration Guide

## 🚨 CRITICAL FIX FOR REGISTRATION

**Your registration is failing because:**
1. **Missing `country` field** - You MUST include `"country": "UAE"` or `"country": "UZB"` in the top-level data
2. **Wrong city format** - Send city **CODES** like `"DXB"` (not `"dubai"`)

**Correct format:**
```json
{
  "email": "linzhang2242@gmail.com",
  "username": "Usta",
  "password": "DerbyMatoma@99",
  "confirm_password": "DerbyMatoma@99",
  "first_name": "Usta",
  "last_name": "King",
  "phone_number": "+971507398212",
  "country": "UAE",  ← ADD THIS!
  "profile": {
    "company_name": "Ustasell",
    "business_type": "LLC",
    "company_address": "Zahra Breeze 4 B1, Nshama, Apartment 213",
    "city": "DXB",  ← CHANGE from "dubai" to "DXB"
    "tax_number": "057478711132908",
    "company_phone": "+971507398212"
  }
}
```

---

## Overview
Complete guide for integrating authentication, registration, and password management in your React frontend.

**Base URL:** `http://localhost:8000/api/accounts/`

---

## Table of Contents
1. [Registration](#registration)
2. [Login (JWT Authentication)](#login)
3. [Password Management](#password-management)
4. [Profile Management](#profile-management)
5. [React Integration Examples](#react-integration-examples)
6. [Error Handling](#error-handling)

---

## Frontend Accounts Integration - Quick Reference

## ⚠️ IMPORTANT: Country and City Codes

### Country Codes (Required Field!)
- **UAE** - United Arab Emirates
- **UZB** - Uzbekistan

### UAE City Codes (Use CODES, not names!)
- **AUH** - Abu Dhabi
- **DXB** - Dubai
- **SHJ** - Sharjah
- **AJM** - Ajman
- **UAQ** - Umm Al Quwain
- **FUJ** - Fujairah
- **RAK** - Ras Al Khaimah

### Uzbekistan City Codes
- **TAS** - Tashkent
- **SAM** - Samarkand
- **NAM** - Namangan
- **AND** - Andijan

---

## Registration Endpoints

### 1. Customer Registration

**Endpoint:** `POST /api/accounts/register/customer/`  
**Authentication:** None (Public)

**Request Body:**
```json
{
  "email": "customer@example.com",
  "username": "customer123",
  "password": "securepassword123",
  "password2": "securepassword123",
  "phone_number": "+971501234567",
  "country": "UAE",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Success Response (201 Created):**
```json
{
  "id": 1,
  "email": "customer@example.com",
  "username": "customer123",
  "user_type": "customer",
  "phone_number": "+971501234567",
  "country": "UAE",
  "first_name": "John",
  "last_name": "Doe",
  "is_verified": false
}
```

**React Example:**
```javascript
const registerCustomer = async (formData) => {
  try {
    const response = await fetch('http://localhost:8000/api/accounts/register/customer/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: formData.email,
        username: formData.username,
        password: formData.password,
        password2: formData.confirmPassword,
        phone_number: formData.phone,
        country: formData.country,
        first_name: formData.firstName,
        last_name: formData.lastName,
      })
    });

    if (!response.ok) {
      const errors = await response.json();
      throw errors;
    }

    const data = await response.json();
    console.log('Registration successful:', data);
    
    // Redirect to login page
    // navigate('/login');
    
    return data;
  } catch (error) {
    console.error('Registration error:', error);
    throw error;
  }
};
```

---

### 2. Company/Seller Registration

**Endpoint:** `POST /api/accounts/register/company/`  
**Authentication:** None (Public)

**Request Body:**
```json
{
  "email": "company@example.com",
  "username": "company123",
  "password": "securepassword123",
  "password2": "securepassword123",
  "phone_number": "+971501234567",
  "country": "UAE",
  "company_name": "ABC Equipment Rental",
  "trade_license_number": "TL123456",
  "first_name": "Jane",
  "last_name": "Smith"
}
```

**Success Response (201 Created):**
```json
{
  "id": 2,
  "email": "company@example.com",
  "username": "company123",
  "user_type": "company",
  "phone_number": "+971501234567",
  "country": "UAE",
  "company_name": "ABC Equipment Rental",
  "trade_license_number": "TL123456",
  "first_name": "Jane",
  "last_name": "Smith",
  "is_verified": false
}
```

**React Example:**
```javascript
const registerCompany = async (formData) => {
  try {
    const response = await fetch('http://localhost:8000/api/accounts/register/company/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: formData.email,
        username: formData.username,
        password: formData.password,
        password2: formData.confirmPassword,
        phone_number: formData.phone,
        country: formData.country,
        company_name: formData.companyName,
        trade_license_number: formData.tradeLicense,
        first_name: formData.firstName,
        last_name: formData.lastName,
      })
    });

    if (!response.ok) {
      const errors = await response.json();
      throw errors;
    }

    const data = await response.json();
    console.log('Company registration successful:', data);
    return data;
  } catch (error) {
    console.error('Registration error:', error);
    throw error;
  }
};
```

---

### 3. Get Location Choices

**Endpoint:** `GET /api/accounts/location-choices/`  
**Authentication:** None (Public)

**Success Response (200 OK):**
```json
{
  "countries": [
    ["UAE", "United Arab Emirates"],
    ["UZB", "Uzbekistan"]
  ],
  "cities": {
    "UAE": [
      ["AUH", "Abu Dhabi"],
      ["DXB", "Dubai"],
      ["SHJ", "Sharjah"],
      ["AJM", "Ajman"],
      ["UAQ", "Umm Al Quwain"],
      ["FUJ", "Fujairah"],
      ["RAK", "Ras Al Khaimah"]
    ],
    "UZB": [
      ["TAS", "Tashkent"],
      ["SAM", "Samarkand"],
      ["NAM", "Namangan"],
      ["AND", "Andijan"]
    ]
  }
}
```

**React Example:**
```javascript
const [locationData, setLocationData] = useState(null);

useEffect(() => {
  const fetchLocations = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/accounts/location-choices/');
      const data = await response.json();
      setLocationData(data);
    } catch (error) {
      console.error('Error fetching locations:', error);
    }
  };
  
  fetchLocations();
}, []);

// Use in your form
{locationData && (
  <>
    <select name="country" onChange={handleCountryChange}>
      <option value="">Select Country</option>
      {locationData.countries.map(([code, name]) => (
        <option key={code} value={code}>{name}</option>
      ))}
    </select>
    
    {selectedCountry && (
      <select name="city">
        <option value="">Select City</option>
        {locationData.cities[selectedCountry].map(([code, name]) => (
          <option key={code} value={code}>{name}</option>
        ))}
      </select>
    )}
  </>
)}
```

---

## Login

### JWT Authentication

**Endpoint:** `POST /api/accounts/token/`  
**Authentication:** None (Public)

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Success Response (200 OK):**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**React Example with Context:**
```javascript
// AuthContext.js
import { createContext, useState, useContext, useEffect } from 'react';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [accessToken, setAccessToken] = useState(localStorage.getItem('accessToken'));
  const [refreshToken, setRefreshToken] = useState(localStorage.getItem('refreshToken'));

  const login = async (email, password) => {
    try {
      const response = await fetch('http://localhost:8000/api/accounts/token/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Login failed');
      }

      const data = await response.json();
      
      // Save tokens
      localStorage.setItem('accessToken', data.access);
      localStorage.setItem('refreshToken', data.refresh);
      setAccessToken(data.access);
      setRefreshToken(data.refresh);

      // Fetch user profile
      await fetchUserProfile(data.access);

      return data;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  const fetchUserProfile = async (token) => {
    try {
      const response = await fetch('http://localhost:8000/api/accounts/profile/', {
        headers: {
          'Authorization': `Bearer ${token || accessToken}`,
        }
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      }
    } catch (error) {
      console.error('Error fetching profile:', error);
    }
  };

  const logout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    setAccessToken(null);
    setRefreshToken(null);
    setUser(null);
  };

  const refreshAccessToken = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/accounts/token/refresh/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh: refreshToken })
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('accessToken', data.access);
        setAccessToken(data.access);
        return data.access;
      } else {
        logout();
      }
    } catch (error) {
      console.error('Token refresh error:', error);
      logout();
    }
  };

  useEffect(() => {
    if (accessToken) {
      fetchUserProfile();
    }
  }, [accessToken]);

  return (
    <AuthContext.Provider value={{ 
      user, 
      accessToken, 
      login, 
      logout, 
      refreshAccessToken 
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
```

**Login Component Example:**
```javascript
import { useState } from 'react';
import { useAuth } from './AuthContext';
import { useNavigate } from 'react-router-dom';

const LoginForm = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.message || 'Invalid email or password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Login</h2>
      
      {error && <div className="error">{error}</div>}
      
      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
      />
      
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
      />
      
      <button type="submit" disabled={loading}>
        {loading ? 'Logging in...' : 'Login'}
      </button>
      
      <a href="/forgot-password">Forgot Password?</a>
    </form>
  );
};
```

---

### Token Refresh

**Endpoint:** `POST /api/accounts/token/refresh/`  
**Authentication:** None (but requires valid refresh token)

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Success Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## Password Management

### 1. Forgot Password (Request Reset)

**Endpoint:** `POST /api/accounts/password-reset/`  
**Authentication:** None (Public)

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Success Response (200 OK):**
```json
{
  "message": "Password reset email sent successfully",
  "detail": "If an account exists with this email, you will receive password reset instructions.",
  "reset_url": "http://localhost:3000/reset-password/MQ/abc123-xyz456/",
  "uid": "MQ",
  "token": "abc123-xyz456",
  "email_sent": false
}
```

**Note:** In production, `reset_url`, `uid`, `token`, and `email_sent` won't be included. The user will receive an email with the reset link.

**React Example:**
```javascript
const ForgotPasswordForm = () => {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setMessage('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/accounts/password-reset/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email })
      });

      const data = await response.json();
      
      if (response.ok) {
        setMessage(data.detail);
        
        // For development: auto-redirect to reset page
        if (data.uid && data.token) {
          console.log('Reset URL:', data.reset_url);
          // Optionally redirect: navigate(`/reset-password/${data.uid}/${data.token}`);
        }
      } else {
        setError(data.error || 'Something went wrong');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Forgot Password</h2>
      
      {message && <div className="success">{message}</div>}
      {error && <div className="error">{error}</div>}
      
      <p>Enter your email address and we'll send you a link to reset your password.</p>
      
      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
      />
      
      <button type="submit" disabled={loading}>
        {loading ? 'Sending...' : 'Send Reset Link'}
      </button>
      
      <a href="/login">Back to Login</a>
    </form>
  );
};
```

---

### 2. Verify Reset Token

**Endpoint:** `POST /api/accounts/password-reset/verify/`  
**Authentication:** None (Public)

**Request Body:**
```json
{
  "uid": "MQ",
  "token": "abc123-xyz456"
}
```

**Success Response (200 OK):**
```json
{
  "valid": true,
  "message": "Token is valid",
  "email": "user@example.com"
}
```

**Error Response (400 Bad Request):**
```json
{
  "valid": false,
  "error": "Invalid or expired token"
}
```

---

### 3. Reset Password (Confirm)

**Endpoint:** `POST /api/accounts/password-reset/confirm/`  
**Authentication:** None (Public)

**Request Body:**
```json
{
  "uid": "MQ",
  "token": "abc123-xyz456",
  "new_password": "newsecurepassword123",
  "confirm_password": "newsecurepassword123"
}
```

**Success Response (200 OK):**
```json
{
  "message": "Password reset successfully",
  "detail": "You can now login with your new password"
}
```

**React Example:**
```javascript
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

const ResetPasswordForm = () => {
  const { uid, token } = useParams();
  const navigate = useNavigate();
  
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [tokenValid, setTokenValid] = useState(false);
  const [verifying, setVerifying] = useState(true);

  // Verify token on component mount
  useEffect(() => {
    const verifyToken = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/accounts/password-reset/verify/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ uid, token })
        });

        const data = await response.json();
        
        if (data.valid) {
          setTokenValid(true);
        } else {
          setError('Invalid or expired reset link');
        }
      } catch (err) {
        setError('Error verifying reset link');
      } finally {
        setVerifying(false);
      }
    };

    verifyToken();
  }, [uid, token]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (newPassword !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    
    if (newPassword.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }
    
    setError('');
    setMessage('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/accounts/password-reset/confirm/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          uid,
          token,
          new_password: newPassword,
          confirm_password: confirmPassword
        })
      });

      const data = await response.json();
      
      if (response.ok) {
        setMessage(data.message);
        
        // Redirect to login after 2 seconds
        setTimeout(() => {
          navigate('/login');
        }, 2000);
      } else {
        setError(data.error || 'Password reset failed');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (verifying) {
    return <div>Verifying reset link...</div>;
  }

  if (!tokenValid) {
    return (
      <div>
        <h2>Invalid Reset Link</h2>
        <p>{error}</p>
        <a href="/forgot-password">Request a new reset link</a>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit}>
      <h2>Reset Password</h2>
      
      {message && <div className="success">{message}</div>}
      {error && <div className="error">{error}</div>}
      
      <input
        type="password"
        placeholder="New Password"
        value={newPassword}
        onChange={(e) => setNewPassword(e.target.value)}
        required
        minLength={8}
      />
      
      <input
        type="password"
        placeholder="Confirm Password"
        value={confirmPassword}
        onChange={(e) => setConfirmPassword(e.target.value)}
        required
        minLength={8}
      />
      
      <button type="submit" disabled={loading}>
        {loading ? 'Resetting...' : 'Reset Password'}
      </button>
    </form>
  );
};
```

---

### 4. Change Password (Authenticated Users)

**Endpoint:** `POST /api/accounts/change-password/`  
**Authentication:** Required (Bearer Token)

**Request Body:**
```json
{
  "old_password": "currentpassword",
  "new_password": "newsecurepassword123",
  "confirm_password": "newsecurepassword123"
}
```

**Success Response (200 OK):**
```json
{
  "message": "Password changed successfully",
  "detail": "Please login again with your new password"
}
```

**React Example:**
```javascript
const ChangePasswordForm = () => {
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { accessToken, logout } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (newPassword !== confirmPassword) {
      setError('New passwords do not match');
      return;
    }
    
    setError('');
    setMessage('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/accounts/change-password/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        },
        body: JSON.stringify({
          old_password: oldPassword,
          new_password: newPassword,
          confirm_password: confirmPassword
        })
      });

      const data = await response.json();
      
      if (response.ok) {
        setMessage(data.message);
        
        // Log user out after password change
        setTimeout(() => {
          logout();
        }, 2000);
      } else {
        setError(data.error || 'Password change failed');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Change Password</h2>
      
      {message && <div className="success">{message}</div>}
      {error && <div className="error">{error}</div>}
      
      <input
        type="password"
        placeholder="Current Password"
        value={oldPassword}
        onChange={(e) => setOldPassword(e.target.value)}
        required
      />
      
      <input
        type="password"
        placeholder="New Password"
        value={newPassword}
        onChange={(e) => setNewPassword(e.target.value)}
        required
        minLength={8}
      />
      
      <input
        type="password"
        placeholder="Confirm New Password"
        value={confirmPassword}
        onChange={(e) => setConfirmPassword(e.target.value)}
        required
        minLength={8}
      />
      
      <button type="submit" disabled={loading}>
        {loading ? 'Changing...' : 'Change Password'}
      </button>
    </form>
  );
};
```

---

## Profile Management

### Get User Profile

**Endpoint:** `GET /api/accounts/profile/`  
**Authentication:** Required (Bearer Token)

**Success Response (200 OK):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "user123",
  "user_type": "customer",
  "phone_number": "+971501234567",
  "country": "UAE",
  "first_name": "John",
  "last_name": "Doe",
  "is_verified": true,
  "profile": {
    "date_of_birth": "1990-01-01",
    "address": "123 Street, Dubai",
    "city": "DXB"
  }
}
```

**React Example:**
```javascript
const ProfilePage = () => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const { accessToken } = useAuth();

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/accounts/profile/', {
          headers: {
            'Authorization': `Bearer ${accessToken}`
          }
        });

        if (response.ok) {
          const data = await response.json();
          setProfile(data);
        }
      } catch (error) {
        console.error('Error fetching profile:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, [accessToken]);

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h2>My Profile</h2>
      <p>Email: {profile.email}</p>
      <p>Name: {profile.first_name} {profile.last_name}</p>
      <p>Phone: {profile.phone_number}</p>
      <p>User Type: {profile.user_type}</p>
      {profile.user_type === 'company' && (
        <p>Company: {profile.company_name}</p>
      )}
    </div>
  );
};
```

---

## Error Handling

### Common Error Responses

**400 Bad Request - Validation Error:**
```json
{
  "email": ["This field is required."],
  "password": ["This field may not be blank."]
}
```

**400 Bad Request - Password Mismatch:**
```json
{
  "error": "Passwords do not match"
}
```

**401 Unauthorized:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**401 Unauthorized - Invalid Credentials:**
```json
{
  "detail": "No active account found with the given credentials"
}
```

### React Error Handler

```javascript
const handleApiError = (error) => {
  if (typeof error === 'object') {
    // Validation errors
    const messages = Object.entries(error).map(([field, errors]) => {
      return `${field}: ${Array.isArray(errors) ? errors.join(', ') : errors}`;
    });
    return messages.join('\n');
  }
  
  return error.error || error.detail || 'An error occurred';
};

// Usage in component
try {
  // API call
} catch (error) {
  const errorMessage = handleApiError(error);
  setError(errorMessage);
}
```

---

## Complete React Router Setup

```javascript
// App.js
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';

// Components
import LoginForm from './components/LoginForm';
import CustomerRegistration from './components/CustomerRegistration';
import CompanyRegistration from './components/CompanyRegistration';
import ForgotPasswordForm from './components/ForgotPasswordForm';
import ResetPasswordForm from './components/ResetPasswordForm';
import Dashboard from './components/Dashboard';
import ProfilePage from './components/ProfilePage';
import ChangePasswordForm from './components/ChangePasswordForm';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { accessToken } = useAuth();
  return accessToken ? children : <Navigate to="/login" />;
};

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<LoginForm />} />
          <Route path="/register/customer" element={<CustomerRegistration />} />
          <Route path="/register/company" element={<CompanyRegistration />} />
          <Route path="/forgot-password" element={<ForgotPasswordForm />} />
          <Route path="/reset-password/:uid/:token" element={<ResetPasswordForm />} />
          
          {/* Protected Routes */}
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } />
          <Route path="/profile" element={
            <ProtectedRoute>
              <ProfilePage />
            </ProtectedRoute>
          } />
          <Route path="/change-password" element={
            <ProtectedRoute>
              <ChangePasswordForm />
            </ProtectedRoute>
          } />
          
          {/* Default Route */}
          <Route path="/" element={<Navigate to="/login" />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
```

---

## API Testing with cURL

### Register Customer
```bash
curl -X POST http://localhost:8000/api/accounts/register/customer/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@test.com",
    "username": "testcustomer",
    "password": "testpass123",
    "password2": "testpass123",
    "phone_number": "+971501234567",
    "country": "UAE",
    "first_name": "Test",
    "last_name": "Customer"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/accounts/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@test.com",
    "password": "testpass123"
  }'
```

### Get Profile
```bash
curl -X GET http://localhost:8000/api/accounts/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Forgot Password
```bash
curl -X POST http://localhost:8000/api/accounts/password-reset/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@test.com"
  }'
```

### Reset Password
```bash
curl -X POST http://localhost:8000/api/accounts/password-reset/confirm/ \
  -H "Content-Type: application/json" \
  -d '{
    "uid": "MQ",
    "token": "abc123-xyz456",
    "new_password": "newpass123",
    "confirm_password": "newpass123"
  }'
```

---

## Important Notes

1. **Token Expiry:**
   - Access tokens expire after 24 hours
   - Refresh tokens expire after 7 days
   - Implement automatic token refresh in your app

2. **Email Configuration:**
   - Update `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` in `settings.py`
   - For development, password reset returns the token in the response
   - In production, remove the development fields from the response

3. **CORS:**
   - Already configured for `http://localhost:3000`
   - Update `CORS_ALLOWED_ORIGINS` for production

4. **Security:**
   - Always use HTTPS in production
   - Store tokens securely (consider httpOnly cookies)
   - Implement CSRF protection for sensitive operations

5. **Password Requirements:**
   - Minimum 8 characters
   - Can add more validators in Django settings

---

## Next Steps

1. Test all endpoints with the provided cURL commands
2. Implement the React components using the examples above
3. Add form validation on the frontend
4. Style your forms and add loading states
5. Implement error handling consistently
6. Test the complete flow: Register → Login → Use API → Logout

---

**Version:** 1.0  
**Last Updated:** October 23, 2025  
**Contact:** dmatderby@gmail.com
