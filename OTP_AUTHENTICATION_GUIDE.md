# OTP Authentication Guide

This guide explains how to implement OTP (One-Time Password) based login as an alternative to password authentication.

## Overview

Users can now login in **two ways**:

1. **Traditional**: Email + Password → Get JWT tokens
2. **OTP (New)**: Email → Receive code via email → Enter code → Get JWT tokens

Both methods return the same JWT tokens, so the rest of the app works identically.

---

## API Endpoints

### Base URL

- **Local**: `http://localhost:8000`
- **Production**: `https://tezrentapibackend-bsatbme3eqfkfnc3.canadacentral-01.azurewebsites.net`

---

## Step 1: Request OTP

Send a request to receive a 6-digit code via email.

**Endpoint**: `POST /api/accounts/otp/request/`

**Headers**:

```
Content-Type: application/json
```

**Request Body**:

```json
{
  "email": "user@example.com"
}
```

**Success Response** (200 OK):

```json
{
  "message": "If an account exists with this email, you will receive an OTP code.",
  "expires_in_minutes": 10
}
```

**Note**: For security, the API returns success even if the email doesn't exist (to prevent email enumeration).

---

## Step 2: Verify OTP & Login

After the user receives the email and enters the 6-digit code:

**Endpoint**: `POST /api/accounts/otp/verify/`

**Headers**:

```
Content-Type: application/json
```

**Request Body**:

```json
{
  "email": "user@example.com",
  "otp": "482916"
}
```

**Success Response** (200 OK):

```json
{
  "message": "Login successful",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "user_type": "customer"
  }
}
```

**Error Responses**:

Invalid/Expired OTP (400 Bad Request):

```json
{
  "error": "Invalid or expired OTP"
}
```

OTP Expired (400 Bad Request):

```json
{
  "error": "OTP has expired. Please request a new one."
}
```

---

## Frontend Implementation Guide

### React Native Example

```javascript
// services/authService.js

const API_URL = "https://your-api-url.com";

// Step 1: Request OTP
export const requestOTP = async (email) => {
  try {
    const response = await fetch(`${API_URL}/api/accounts/otp/request/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email }),
    });

    const data = await response.json();
    return { success: true, data };
  } catch (error) {
    return { success: false, error: error.message };
  }
};

// Step 2: Verify OTP and get tokens
export const verifyOTP = async (email, otp) => {
  try {
    const response = await fetch(`${API_URL}/api/accounts/otp/verify/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email, otp }),
    });

    const data = await response.json();

    if (response.ok) {
      // Store tokens securely
      await AsyncStorage.setItem("accessToken", data.access);
      await AsyncStorage.setItem("refreshToken", data.refresh);
      await AsyncStorage.setItem("user", JSON.stringify(data.user));
      return { success: true, data };
    } else {
      return { success: false, error: data.error };
    }
  } catch (error) {
    return { success: false, error: error.message };
  }
};
```

### UI Flow

```
┌─────────────────────────────────────┐
│         Login Screen                │
│                                     │
│  ┌─────────────────────────────┐    │
│  │  Email: [________________]  │    │
│  └─────────────────────────────┘    │
│                                     │
│  [Login with Password]              │
│                                     │
│  ─────── OR ───────                 │
│                                     │
│  [Send OTP Code]  ← NEW             │
│                                     │
└─────────────────────────────────────┘
              │
              │ User taps "Send OTP Code"
              ▼
┌─────────────────────────────────────┐
│         Enter OTP Screen            │
│                                     │
│  A code was sent to your email      │
│                                     │
│  ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐│
│  │ 4 │ │ 8 │ │ 2 │ │ 9 │ │ 1 │ │ 6 ││
│  └───┘ └───┘ └───┘ └───┘ └───┘ └───┘│
│                                     │
│  Code expires in 9:42               │
│                                     │
│  [Verify & Login]                   │
│                                     │
│  Didn't receive code? [Resend]      │
│                                     │
└─────────────────────────────────────┘
              │
              │ User enters code and taps "Verify"
              ▼
┌─────────────────────────────────────┐
│         Success!                    │
│                                     │
│  User is now logged in              │
│  (Same as password login)           │
│                                     │
└─────────────────────────────────────┘
```

---

## Important Notes

1. **OTP Expiration**: Codes expire after **10 minutes**
2. **Single Use**: Each OTP can only be used once
3. **Auto-Invalidation**: Requesting a new OTP automatically invalidates any previous unused codes
4. **Same Tokens**: The JWT tokens returned are identical to password login - no changes needed elsewhere
5. **Email Template**: Users receive a nicely formatted HTML email with the 6-digit code

---

## Comparison: Password vs OTP Login

| Feature  | Password Login              | OTP Login                                     |
| -------- | --------------------------- | --------------------------------------------- |
| Endpoint | `/api/accounts/token/`      | `/api/accounts/otp/request/` + `/otp/verify/` |
| Steps    | 1 step                      | 2 steps                                       |
| Requires | Email + Password            | Email + Code from email                       |
| Returns  | `access` + `refresh` tokens | `access` + `refresh` tokens                   |
| Use Case | Returning users             | Forgot password, quick login                  |

---

## Testing with cURL

**Request OTP**:

```bash
curl -X POST http://localhost:8000/api/accounts/otp/request/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

**Verify OTP**:

```bash
curl -X POST http://localhost:8000/api/accounts/otp/verify/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "otp": "123456"}'
```

---

## Email Preview

The user will receive an email that looks like this:

```
┌────────────────────────────────────────┐
│              TezRent                   │
│         (Blue Header)                  │
├────────────────────────────────────────┤
│                                        │
│   Your Login Code                      │
│                                        │
│   Hello John,                          │
│                                        │
│   Use the following code to log into   │
│   your TezRent account:                │
│                                        │
│        ┌─────────────────┐             │
│        │    4 8 2 9 1 6  │             │
│        └─────────────────┘             │
│                                        │
│   This code will expire in 10 minutes. │
│                                        │
│   If you didn't request this code,     │
│   please ignore this email.            │
│                                        │
├────────────────────────────────────────┤
│   © 2025 TezRent. All rights reserved. │
└────────────────────────────────────────┘
```
