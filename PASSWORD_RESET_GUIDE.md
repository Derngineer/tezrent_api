# Password Reset API - Frontend Integration Guide

## ⚠️ Email Configuration Status

**Development Mode:** ✅ Emails print to console/terminal  
**Production Mode:** ⏳ Needs SMTP setup (see `EMAIL_SETUP_GUIDE.md`)

### How It Works Now (Development)
When you test password reset:
1. API generates the reset link
2. **Check your Django server terminal** - the email with reset link prints there
3. Copy the token from terminal to test frontend
4. No actual emails are sent (perfect for testing!)

### For Production
See `EMAIL_SETUP_GUIDE.md` for:
- Gmail SMTP setup (free, easy)
- SendGrid setup (100 emails/day free)
- AWS SES setup (cheapest for high volume)
- Complete configuration steps

---

## Overview
This guide covers the password reset functionality for TezRent API. The process uses a secure token-based system where users receive a reset link via email.

---

## Password Reset Flow

```
1. User enters email on "Forgot Password" page
2. Frontend sends POST request to /api/accounts/password-reset/
3. Backend generates token and sends email with reset link
4. User clicks link in email (contains token)
5. Frontend extracts token from URL and shows "Reset Password" form
6. User enters new password
7. Frontend sends POST request to /api/accounts/password-reset-confirm/ with token + new password
8. Password is reset, user can login with new password
```

---

## API Endpoints

### 1. Request Password Reset

**Endpoint:** `POST /api/accounts/password-reset/`

**Purpose:** Initiates password reset process by sending reset email to user

**Request:**
```http
POST /api/accounts/password-reset/
Content-Type: application/json

{
  "email": "user@example.com"
}
```

**Response (Success - 200):**
```json
{
  "message": "Password reset email has been sent. Please check your email.",
  "email": "user@example.com"
}
```

**Response (Error - 400):**
```json
{
  "email": ["This field is required."]
}
```

**Response (User Not Found - 200):**
```json
{
  "message": "Password reset email has been sent. Please check your email.",
  "email": "nonexistent@example.com"
}
```
*Note: For security, we return success even if email doesn't exist to prevent email enumeration attacks*

**Frontend Implementation:**
```javascript
async function requestPasswordReset(email) {
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
      // Show success message
      alert('Password reset email sent! Please check your inbox.');
      return true;
    } else {
      // Handle validation errors
      console.error('Error:', data);
      return false;
    }
  } catch (error) {
    console.error('Network error:', error);
    return false;
  }
}

// Usage
requestPasswordReset('user@example.com');
```

---

### 2. Confirm Password Reset

**Endpoint:** `POST /api/accounts/password-reset-confirm/`

**Purpose:** Resets user's password using the token from email

**Request:**
```http
POST /api/accounts/password-reset-confirm/
Content-Type: application/json

{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "password": "NewSecurePassword123!"
}
```

**Response (Success - 200):**
```json
{
  "message": "Password has been reset successfully. You can now login with your new password."
}
```

**Response (Invalid Token - 400):**
```json
{
  "error": "Invalid or expired reset token"
}
```

**Response (Validation Error - 400):**
```json
{
  "password": ["This password is too short. It must contain at least 8 characters."]
}
```

**Frontend Implementation:**
```javascript
async function confirmPasswordReset(token, newPassword) {
  try {
    const response = await fetch('http://localhost:8000/api/accounts/password-reset-confirm/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        token: token,
        password: newPassword
      })
    });
    
    const data = await response.json();
    
    if (response.ok) {
      // Password reset successful
      alert('Password reset successful! Please login with your new password.');
      // Redirect to login page
      window.location.href = '/login';
      return true;
    } else {
      // Handle errors
      if (data.error) {
        alert(data.error);
      } else if (data.password) {
        alert(data.password.join(' '));
      }
      return false;
    }
  } catch (error) {
    console.error('Network error:', error);
    return false;
  }
}

// Usage
const urlParams = new URLSearchParams(window.location.search);
const token = urlParams.get('token');
confirmPasswordReset(token, 'NewPassword123!');
```

---

## Email Reset Link Format

The email sent to users will contain a link in this format:

```
http://localhost:3000/reset-password?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

**Frontend must:**
1. Create a `/reset-password` route
2. Extract the `token` from URL query parameter
3. Display a form for entering new password
4. Submit token + new password to confirm endpoint

---

## React Component Examples

### 1. Forgot Password Page

```jsx
import React, { useState } from 'react';

function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');
    setError('');

    try {
      const response = await fetch('http://localhost:8000/api/accounts/password-reset/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();

      if (response.ok) {
        setMessage('Password reset email sent! Please check your inbox.');
        setEmail('');
      } else {
        setError(data.email ? data.email[0] : 'An error occurred');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="forgot-password-page">
      <h2>Forgot Password</h2>
      <p>Enter your email address and we'll send you a link to reset your password.</p>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="email">Email Address</label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            placeholder="your@email.com"
            disabled={loading}
          />
        </div>

        {message && <div className="success-message">{message}</div>}
        {error && <div className="error-message">{error}</div>}

        <button type="submit" disabled={loading}>
          {loading ? 'Sending...' : 'Send Reset Link'}
        </button>
      </form>

      <div className="links">
        <a href="/login">Back to Login</a>
      </div>
    </div>
  );
}

export default ForgotPasswordPage;
```

### 2. Reset Password Page

```jsx
import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  
  const [token, setToken] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    const tokenFromUrl = searchParams.get('token');
    if (!tokenFromUrl) {
      setError('Invalid reset link. Please request a new password reset.');
    } else {
      setToken(tokenFromUrl);
    }
  }, [searchParams]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validate passwords match
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    // Validate password length
    if (password.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }

    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/accounts/password-reset-confirm/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token: token,
          password: password,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess(true);
        // Redirect to login after 2 seconds
        setTimeout(() => {
          navigate('/login');
        }, 2000);
      } else {
        setError(data.error || data.password?.[0] || 'Failed to reset password');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!token) {
    return (
      <div className="reset-password-page">
        <div className="error-message">
          Invalid or missing reset token. Please request a new password reset.
        </div>
        <a href="/forgot-password">Request New Reset Link</a>
      </div>
    );
  }

  if (success) {
    return (
      <div className="reset-password-page">
        <div className="success-message">
          <h2>Password Reset Successful!</h2>
          <p>Your password has been reset. Redirecting to login...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="reset-password-page">
      <h2>Reset Your Password</h2>
      <p>Enter your new password below.</p>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="password">New Password</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={8}
            placeholder="Enter new password"
            disabled={loading}
          />
        </div>

        <div className="form-group">
          <label htmlFor="confirmPassword">Confirm Password</label>
          <input
            type="password"
            id="confirmPassword"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
            minLength={8}
            placeholder="Confirm new password"
            disabled={loading}
          />
        </div>

        {error && <div className="error-message">{error}</div>}

        <button type="submit" disabled={loading}>
          {loading ? 'Resetting...' : 'Reset Password'}
        </button>
      </form>
    </div>
  );
}

export default ResetPasswordPage;
```

---

## Password Requirements

The API enforces Django's default password validation:
- Minimum 8 characters
- Cannot be too similar to user's email or name
- Cannot be a commonly used password
- Cannot be entirely numeric

**Frontend should validate before submission:**
```javascript
function validatePassword(password) {
  const errors = [];
  
  if (password.length < 8) {
    errors.push('Password must be at least 8 characters long');
  }
  
  if (!/[a-z]/.test(password)) {
    errors.push('Password must contain at least one lowercase letter');
  }
  
  if (!/[A-Z]/.test(password)) {
    errors.push('Password must contain at least one uppercase letter');
  }
  
  if (!/[0-9]/.test(password)) {
    errors.push('Password must contain at least one number');
  }
  
  return errors;
}
```

---

## Token Security

- Reset tokens are JWT tokens that expire after **1 hour**
- Tokens are single-use (recommended to invalidate after use)
- Tokens are securely signed with Django's SECRET_KEY
- Always use HTTPS in production to prevent token interception

---

## Error Handling

### Common Errors and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| Invalid or expired reset token | Token is older than 1 hour or malformed | Request new password reset |
| This field is required | Missing email or password field | Validate form inputs |
| User with this email does not exist | Email not in database | User should register instead |
| Password too short | Password < 8 characters | Enforce minimum length in frontend |
| Password too common | Using common password | Suggest stronger password |

---

## Testing the API

### Using cURL

**Request Password Reset:**
```bash
curl -X POST http://localhost:8000/api/accounts/password-reset/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

**Confirm Password Reset:**
```bash
curl -X POST http://localhost:8000/api/accounts/password-reset-confirm/ \
  -H "Content-Type: application/json" \
  -d '{
    "token": "your-token-here",
    "password": "NewPassword123!"
  }'
```

### Using Postman

1. **Request Reset:**
   - Method: POST
   - URL: `http://localhost:8000/api/accounts/password-reset/`
   - Body (JSON): `{"email": "test@example.com"}`

2. **Confirm Reset:**
   - Method: POST
   - URL: `http://localhost:8000/api/accounts/password-reset-confirm/`
   - Body (JSON): `{"token": "...", "password": "NewPassword123!"}`

---

## Email Configuration

**For Development:**
The API is configured to print emails to console. Check the Django server terminal to see reset links during testing.

**For Production:**
Update `config/settings.py` with real SMTP settings:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'TezRent <noreply@tezrent.com>'
```

---

## Frontend Routes Required

Your React app needs these routes:

```javascript
// In your router (e.g., App.js or Routes.js)
<Route path="/forgot-password" element={<ForgotPasswordPage />} />
<Route path="/reset-password" element={<ResetPasswordPage />} />
<Route path="/login" element={<LoginPage />} />
```

---

## Complete User Flow Example

```javascript
// 1. User on login page clicks "Forgot Password?"
<a href="/forgot-password">Forgot Password?</a>

// 2. User enters email and submits
// Frontend calls: POST /api/accounts/password-reset/

// 3. User receives email with link:
// http://localhost:3000/reset-password?token=eyJ0eXAi...

// 4. User clicks link, arrives at /reset-password page
// Frontend extracts token from URL

// 5. User enters new password
// Frontend calls: POST /api/accounts/password-reset-confirm/

// 6. Success! Redirect to /login
// User logs in with new password
```

---

## Security Best Practices

1. **Always use HTTPS in production** to prevent token interception
2. **Tokens expire after 1 hour** - inform users to use link quickly
3. **Rate limit password reset requests** to prevent abuse (implement in frontend)
4. **Don't reveal if email exists** - always return success message
5. **Log password reset attempts** for security monitoring
6. **Require strong passwords** - enforce complexity in frontend
7. **Consider 2FA** for sensitive accounts (future enhancement)

---

## Troubleshooting

### Email not received?
- Check spam/junk folder
- Verify email address is correct
- Check Django console for email output (development mode)
- Verify SMTP settings (production)

### Invalid token error?
- Token may have expired (1 hour limit)
- Token may have been used already
- URL may be corrupted - check for complete token
- Request new password reset

### Password not meeting requirements?
- Check Django's password validators
- Ensure minimum 8 characters
- Use mix of letters, numbers, and symbols
- Avoid common passwords

---

## Support

For issues or questions:
- **Developer:** Derngineer
- **Email:** dmatderby@gmail.com
- **Repository:** github.com/Derngineer/tezrent_api

---

**Last Updated:** October 23, 2025
