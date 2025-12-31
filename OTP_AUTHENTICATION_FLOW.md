# OTP Authentication Flow Guide

## Overview

Your TezRent system supports **dual authentication modes**:

1. **Traditional Email/Password** - Users sign up with email, username, and password
2. **OTP-based Passwordless** - Users can sign in using email and OTP without password

This guide explains how these flows work together and when to use each approach.

## Current System Architecture

### User Model Structure

```python
class User(AbstractUser):
    email = models.EmailField(unique=True)          # Primary identifier
    username = models.CharField()                   # Required by Django admin
    phone_number = models.CharField()
    country = models.CharField()
    user_type = models.CharField()                  # customer/company/staff

    USERNAME_FIELD = 'email'                        # Login with email
    REQUIRED_FIELDS = ['username']                  # Username still required
```

### Key Authentication Endpoints

- **Registration**: `/api/accounts/register/customer/` and `/api/accounts/register/company/`
- **Traditional Login**: `/api/accounts/token/` (email + password → JWT)
- **OTP Request**: `/api/accounts/otp/request/` (email → OTP sent)
- **OTP Verify**: `/api/accounts/otp/verify/` (email + OTP → JWT)

---

## Authentication Flow Options

### Option 1: OTP-Only Signup (Recommended for Mobile)

**For new users who prefer passwordless experience:**

#### Step 1: OTP Registration Request

```http
POST /api/accounts/otp/signup-request/
{
    "email": "newuser@example.com",
    "username": "newuser123",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+971501234567",
    "country": "UAE",
    "user_type": "customer"
}
```

#### Step 2: OTP Verification & Account Creation

```http
POST /api/accounts/otp/signup-verify/
{
    "email": "newuser@example.com",
    "otp": "123456"
}
```

**Response**: JWT tokens + user profile

#### Step 3: Future Logins (Passwordless)

```http
POST /api/accounts/otp/request/
{
    "email": "newuser@example.com"
}
```

```http
POST /api/accounts/otp/verify/
{
    "email": "newuser@example.com",
    "otp": "654321"
}
```

### Option 2: Traditional Signup with OTP Login Option

**For users who want full control:**

#### Step 1: Traditional Registration

```http
POST /api/accounts/register/customer/
{
    "email": "user@example.com",
    "username": "user123",
    "password": "securepassword",
    "confirm_password": "securepassword",
    "first_name": "Jane",
    "last_name": "Smith",
    "phone_number": "+971501234567",
    "country": "UAE"
}
```

#### Step 2A: Traditional Login

```http
POST /api/accounts/token/
{
    "email": "user@example.com",
    "password": "securepassword"
}
```

#### Step 2B: OTP Login (Alternative)

```http
POST /api/accounts/otp/request/
{
    "email": "user@example.com"
}
```

```http
POST /api/accounts/otp/verify/
{
    "email": "user@example.com",
    "otp": "789012"
}
```

---

## Implementation Status

### ✅ Currently Implemented

- Traditional email/password registration
- Traditional JWT login
- OTP request and verify for **existing users**
- Password reset with OTP
- User profiles and address management

### ❌ Missing for Complete OTP Signup

- OTP-based signup endpoints (`/api/accounts/otp/signup-request/` and `/api/accounts/otp/signup-verify/`)
- Logic to create users without password during OTP signup

---

## Required Implementation

### 1. OTP Signup Request View

```python
class OTPSignupRequestView(APIView):
    """
    Request OTP for new user registration
    POST /api/accounts/otp/signup-request/
    """
    permission_classes = (AllowAny,)

    def post(self, request):
        email = request.data.get('email')

        # Check if user already exists
        if User.objects.filter(email=email).exists():
            return Response(
                {'error': 'Account already exists. Use login instead.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Store registration data temporarily
        # (You might want to use cache/session for this)
        request.session['pending_registration'] = {
            'email': request.data.get('email'),
            'username': request.data.get('username'),
            'first_name': request.data.get('first_name'),
            'last_name': request.data.get('last_name'),
            'phone_number': request.data.get('phone_number'),
            'country': request.data.get('country'),
            'user_type': request.data.get('user_type', 'customer'),
        }

        # Generate and send OTP
        code = OTPCode.generate_code()

        # Create temporary OTP record
        otp = OTPCode.objects.create(
            email=email,  # Store email directly since user doesn't exist yet
            code=code,
            purpose='signup'  # New purpose
        )

        # Send OTP email
        # ... email sending logic ...

        return Response({
            'message': 'OTP sent to your email. Please verify to complete registration.'
        })
```

### 2. OTP Signup Verify View

```python
class OTPSignupVerifyView(APIView):
    """
    Verify OTP and create new user account
    POST /api/accounts/otp/signup-verify/
    """
    permission_classes = (AllowAny,)

    @transaction.atomic
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        # Get pending registration data
        pending_data = request.session.get('pending_registration', {})

        if pending_data.get('email') != email:
            return Response(
                {'error': 'Invalid registration session'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verify OTP
        otp_entry = OTPCode.objects.filter(
            email=email,
            code=otp,
            is_used=False,
            purpose='signup'
        ).first()

        if not otp_entry or otp_entry.is_expired:
            return Response(
                {'error': 'Invalid or expired OTP'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create user without password
        user = User.objects.create(
            email=pending_data['email'],
            username=pending_data['username'],
            first_name=pending_data.get('first_name', ''),
            last_name=pending_data.get('last_name', ''),
            phone_number=pending_data.get('phone_number', ''),
            country=pending_data.get('country', ''),
            user_type=pending_data.get('user_type', 'customer'),
            is_active=True
        )

        # Create profile
        if user.user_type == 'customer':
            CustomerProfile.objects.create(user=user)
        elif user.user_type == 'company':
            # You might want to collect company data during signup
            CompanyProfile.objects.create(user=user)

        # Mark OTP as used
        otp_entry.is_used = True
        otp_entry.save()

        # Clear session
        request.session.pop('pending_registration', None)

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            'message': 'Account created successfully',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'user_type': user.user_type,
            }
        })
```

### 3. Update OTP Model

```python
class OTPCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField()  # Add this for signup OTPs
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    PURPOSE_CHOICES = (
        ('login', 'Login'),
        ('signup', 'Signup'),  # Add this
        ('verify_email', 'Email Verification'),
    )
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES, default='login')
```

---

## Mobile App Flow Recommendations

### For User Experience

1. **Primary Flow**: OTP-only signup

   - Faster onboarding
   - No password to remember
   - More secure (no stored passwords)

2. **Optional**: Traditional signup
   - For users who prefer passwords
   - For B2B customers who need stronger account control

### Suggested Mobile UI Flow

```
1. Welcome Screen
   ├── "Sign Up with Email" (OTP Flow)
   └── "Advanced Signup" (Password Flow)

2. OTP Signup Flow:
   Email → User Details → OTP Verification → Success

3. Future Login:
   Email → OTP → Success
```

### React Native Implementation

```javascript
// OTP Signup Service
export const otpSignupRequest = async (userData) => {
  const response = await fetch(`${API_BASE}/accounts/otp/signup-request/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(userData),
  });
  return response.json();
};

export const otpSignupVerify = async (email, otp) => {
  const response = await fetch(`${API_BASE}/accounts/otp/signup-verify/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, otp }),
  });
  return response.json();
};
```

---

## Security Considerations

1. **OTP Expiration**: 10-15 minutes for signup, 5 minutes for login
2. **Rate Limiting**: Limit OTP requests per email/IP
3. **Session Security**: Clear pending registration data after timeout
4. **Email Validation**: Verify email ownership through OTP
5. **Username Uniqueness**: Still validate username uniqueness during signup

---

## Next Steps

To implement complete OTP-based signup:

1. ✅ **Add OTP signup views** (shown above)
2. ✅ **Update OTP model** to support signup purpose
3. ✅ **Add URL patterns** for new endpoints
4. ✅ **Update frontend** to use new signup flow
5. ✅ **Test both flows** thoroughly

Would you like me to implement these missing OTP signup endpoints in your codebase?
