from django.shortcuts import render
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from .models import COUNTRY_CHOICES, UAE_CITY_CHOICES, UZB_CITY_CHOICES, CustomerProfile, CompanyProfile, StaffProfile, DeliveryAddress, OTPCode
from .serializers import (
    UserSerializer, CustomerRegistrationSerializer, 
    CompanyRegistrationSerializer, CustomerProfileSerializer,
    CompanyProfileSerializer, StaffProfileSerializer,
    DeliveryAddressSerializer
)

User = get_user_model()

class DeliveryAddressViewSet(viewsets.ModelViewSet):
    """
    Manage user delivery addresses.
    """
    serializer_class = DeliveryAddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return DeliveryAddress.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CustomerRegistrationView(generics.CreateAPIView):
    """
    Register a new customer user
    """
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = CustomerRegistrationSerializer

class CompanyRegistrationView(generics.CreateAPIView):
    """
    Register a new company user
    """
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = CompanyRegistrationSerializer

class UserProfileView(APIView):
    """
    Get user profile based on user type
    """
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self, request):
        user = request.user
        data = UserSerializer(user).data
        
        if user.user_type == 'customer':
            try:
                profile = CustomerProfile.objects.get(user=user)
                profile_data = CustomerProfileSerializer(profile).data
                data['profile'] = profile_data
                
                # Include delivery addresses in profile response
                addresses = DeliveryAddress.objects.filter(user=user)
                data['addresses'] = DeliveryAddressSerializer(addresses, many=True).data
                
            except CustomerProfile.DoesNotExist:
                data['profile'] = None
                data['addresses'] = []
                
        elif user.user_type == 'company':
            try:
                profile = CompanyProfile.objects.get(user=user)
                profile_data = CompanyProfileSerializer(profile).data
                data['profile'] = profile_data
            except CompanyProfile.DoesNotExist:
                data['profile'] = None
                
        elif user.user_type == 'staff':
            try:
                profile = StaffProfile.objects.get(user=user)
                profile_data = StaffProfileSerializer(profile).data
                data['profile'] = profile_data
            except StaffProfile.DoesNotExist:
                data['profile'] = None
        
        return Response(data)

    def patch(self, request):
        """
        Update user profile
        """
        user = request.user
        
        # 1. Update User model fields
        user_serializer = UserSerializer(user, data=request.data, partial=True)
        if user_serializer.is_valid():
            user_serializer.save()
        else:
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        # 2. Update Profile model fields
        profile_data = request.data.get('profile', {})
        if profile_data:
            if user.user_type == 'customer':
                try:
                    profile = CustomerProfile.objects.get(user=user)
                    profile_serializer = CustomerProfileSerializer(profile, data=profile_data, partial=True)
                    if profile_serializer.is_valid():
                        profile_serializer.save()
                    else:
                        return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except CustomerProfile.DoesNotExist:
                    pass
                    
            elif user.user_type == 'company':
                try:
                    profile = CompanyProfile.objects.get(user=user)
                    profile_serializer = CompanyProfileSerializer(profile, data=profile_data, partial=True)
                    if profile_serializer.is_valid():
                        profile_serializer.save()
                    else:
                        return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except CompanyProfile.DoesNotExist:
                    pass

        # Return updated profile data
        return self.get(request)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_location_choices(request):
    """Return country and city choices for registration forms"""
    return Response({
        'countries': COUNTRY_CHOICES,
        'cities': {
            'UAE': UAE_CITY_CHOICES,
            'UZB': UZB_CITY_CHOICES,
        }
    })


class PasswordResetRequestView(APIView):
    """
    Request password reset - sends reset email with token
    POST /api/accounts/password-reset/
    Body: { "email": "user@example.com" }
    """
    permission_classes = (AllowAny,)
    
    def post(self, request):
        email = request.data.get('email')
        
        if not email:
            return Response(
                {'error': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(email=email)
            
            # Generate token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Create reset URL for frontend
            reset_url = f"http://localhost:3000/reset-password?uid={uid}&token={token}"
            
            print(f"Password reset URL: {reset_url}")
            
            # Send email using EmailMultiAlternatives (same as your signup flow)
            try:
                mail_subject = 'Reset Your TezRent Password'
                
                # HTML email message
                html_message = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                        .header {{ background-color: #2563EB; color: white; padding: 20px; text-align: center; }}
                        .content {{ padding: 30px; background-color: #f9f9f9; }}
                        .button {{ display: inline-block; padding: 12px 30px; background-color: #2563EB; 
                                  color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>TezRent</h1>
                        </div>
                        <div class="content">
                            <h2>Password Reset Request</h2>
                            <p>Hello {user.first_name or user.username},</p>
                            <p>You requested to reset your password for your TezRent account.</p>
                            <p>Click the button below to reset your password:</p>
                            <a href="{reset_url}" class="button">Reset Password</a>
                            <p>Or copy and paste this link into your browser:</p>
                            <p style="word-break: break-all; color: #2563EB;">{reset_url}</p>
                            <p><strong>This link will expire in 4 hours.</strong></p>
                            <p>If you didn't request this password reset, please ignore this email.</p>
                        </div>
                        <div class="footer">
                            <p>&copy; 2025 TezRent. All rights reserved.</p>
                            <p>This is an automated email. Please do not reply.</p>
                        </div>
                    </div>
                </body>
                </html>
                """
                
                # Plain text fallback
                plain_message = f"""
                Hello {user.first_name or user.username},
                
                You requested to reset your password for your TezRent account.
                
                Click the link below to reset your password:
                {reset_url}
                
                This link will expire in 4 hours.
                
                If you didn't request this password reset, please ignore this email.
                
                Best regards,
                TezRent Team
                """
                
                # Send email with both HTML and plain text
                email_message = EmailMultiAlternatives(
                    mail_subject,
                    plain_message,  # Plain text message
                    'dmatderby@gmail.com',  # From email
                    [email]  # To email
                )
                email_message.attach_alternative(html_message, "text/html")  # Attach HTML version
                email_message.send()
                
                email_sent = True
                print(f"✅ Password reset email sent successfully to {email}")
            except Exception as e:
                # If email fails, still return success for security
                # But log the error
                print(f"❌ Email error: {e}")
                import traceback
                traceback.print_exc()
                email_sent = False
            
            return Response({
                'message': 'Password reset email sent successfully',
                'detail': 'If an account exists with this email, you will receive password reset instructions.',
                # For development/testing only - remove in production:
                'reset_url': reset_url,
                'uid': uid,
                'token': token,
                'email_sent': email_sent
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            # For security, don't reveal if email exists
            return Response({
                'message': 'Password reset email sent successfully',
                'detail': 'If an account exists with this email, you will receive password reset instructions.',
            }, status=status.HTTP_200_OK)


class PasswordResetVerifyView(APIView):
    """
    Verify password reset token
    POST /api/accounts/password-reset/verify/
    Body: { "uid": "...", "token": "..." }
    """
    permission_classes = (AllowAny,)
    
    def post(self, request):
        uid = request.data.get('uid')
        token = request.data.get('token')
        
        if not uid or not token:
            return Response(
                {'error': 'UID and token are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
            
            if default_token_generator.check_token(user, token):
                return Response({
                    'valid': True,
                    'message': 'Token is valid',
                    'email': user.email
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'valid': False,
                    'error': 'Invalid or expired token'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({
                'valid': False,
                'error': 'Invalid token'
            }, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    """
    Reset password with token
    POST /api/accounts/password-reset-confirm/
    
    Accepts two formats:
    Format 1 (simple): { "token": "...", "password": "newpassword123" }
    Format 2 (with uid): { "uid": "...", "token": "...", "new_password": "newpassword123", "confirm_password": "newpassword123" }
    """
    permission_classes = (AllowAny,)
    
    def post(self, request):
        # Try simple format first (token + password)
        token = request.data.get('token')
        password = request.data.get('password')
        
        # Try format with uid
        uid = request.data.get('uid')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        
        # Use whichever format was provided
        if password:
            # Simple format
            final_password = password
        elif new_password:
            # Format with confirm
            if new_password != confirm_password:
                return Response(
                    {'error': 'Passwords do not match'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            final_password = new_password
        else:
            return Response(
                {'error': 'Password is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not token:
            return Response(
                {'error': 'Token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(final_password) < 8:
            return Response(
                {'error': 'Password must be at least 8 characters long'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # If uid is provided, use it; otherwise try to decode from token
            if uid:
                user_id = force_str(urlsafe_base64_decode(uid))
                user = User.objects.get(pk=user_id)
            else:
                # Try to find user by checking token against all users (less efficient but works)
                user = None
                for potential_user in User.objects.all():
                    if default_token_generator.check_token(potential_user, token):
                        user = potential_user
                        break
                
                if not user:
                    return Response(
                        {'error': 'Invalid or expired token'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            if default_token_generator.check_token(user, token):
                user.set_password(final_password)
                user.save()
                
                print(f"✅ Password reset successfully for {user.email}")
                
                return Response({
                    'message': 'Password has been reset successfully. You can now login with your new password.'
                }, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': 'Invalid or expired reset token'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {'error': 'Invalid token'},
                status=status.HTTP_400_BAD_REQUEST
            )


class ChangePasswordView(APIView):
    """
    Change password for authenticated user
    POST /api/accounts/change-password/
    Body: { 
        "old_password": "currentpassword",
        "new_password": "newpassword123",
        "confirm_password": "newpassword123"
    }
    """
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self, request):
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        
        if not all([old_password, new_password, confirm_password]):
            return Response(
                {'error': 'All fields are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if new_password != confirm_password:
            return Response(
                {'error': 'New passwords do not match'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(new_password) < 8:
            return Response(
                {'error': 'Password must be at least 8 characters long'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = request.user
        
        if not user.check_password(old_password):
            return Response(
                {'error': 'Current password is incorrect'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(new_password)
        user.save()
        
        return Response({
            'message': 'Password changed successfully',
            'detail': 'Please login again with your new password'
        }, status=status.HTTP_200_OK)


class OTPRequestView(APIView):
    """
    Request OTP for passwordless login
    POST /api/accounts/otp/request/
    Body: { "email": "user@example.com" }
    """
    permission_classes = (AllowAny,)
    
    def post(self, request):
        from django.utils import timezone
        from datetime import timedelta
        
        email = request.data.get('email')
        
        if not email:
            return Response(
                {'error': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # For security, don't reveal if email exists
            return Response({
                'message': 'If an account exists with this email, you will receive an OTP code.',
            }, status=status.HTTP_200_OK)
        
        # Invalidate any existing unused OTPs for this user
        OTPCode.objects.filter(user=user, is_used=False).update(is_used=True)
        
        # Generate new OTP
        code = OTPCode.generate_code()
        expires_at = timezone.now() + timedelta(minutes=10)
        
        otp = OTPCode.objects.create(
            user=user,
            code=code,
            expires_at=expires_at,
            purpose='login'
        )
        
        # Send email
        try:
            html_message = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px; }}
                    .container {{ max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    .header {{ background-color: #2563EB; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 30px; }}
                    .otp-code {{ font-size: 36px; font-weight: bold; text-align: center; color: #2563EB; letter-spacing: 8px; padding: 20px; background-color: #f0f7ff; border-radius: 8px; margin: 20px 0; }}
                    .footer {{ background-color: #f9f9f9; padding: 20px; text-align: center; font-size: 12px; color: #888; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>TezRent</h1>
                    </div>
                    <div class="content">
                        <h2>Your Login Code</h2>
                        <p>Hello {user.first_name or user.username},</p>
                        <p>Use the following code to log into your TezRent account:</p>
                        <div class="otp-code">{code}</div>
                        <p><strong>This code will expire in 10 minutes.</strong></p>
                        <p>If you didn't request this code, please ignore this email.</p>
                    </div>
                    <div class="footer">
                        <p>&copy; 2025 TezRent. All rights reserved.</p>
                        <p>This is an automated email. Please do not reply.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            plain_message = f"""
            Hello {user.first_name or user.username},
            
            Your TezRent login code is: {code}
            
            This code will expire in 10 minutes.
            
            If you didn't request this code, please ignore this email.
            
            Best regards,
            TezRent Team
            """
            
            email_message = EmailMultiAlternatives(
                'Your TezRent Login Code',
                plain_message,
                'dmatderby@gmail.com',
                [email]
            )
            email_message.attach_alternative(html_message, "text/html")
            email_message.send()
            
            print(f"✅ OTP email sent successfully to {email}")
            
        except Exception as e:
            print(f"❌ Email error: {e}")
            # Still return success for security
        
        return Response({
            'message': 'If an account exists with this email, you will receive an OTP code.',
            # For development only - remove in production:
            'otp': code,
            'expires_in_minutes': 10
        }, status=status.HTTP_200_OK)


class OTPVerifyView(APIView):
    """
    Verify OTP and return JWT tokens
    POST /api/accounts/otp/verify/
    Body: { "email": "user@example.com", "otp": "123456" }
    """
    permission_classes = (AllowAny,)
    
    def post(self, request):
        from rest_framework_simplejwt.tokens import RefreshToken
        
        email = request.data.get('email')
        otp = request.data.get('otp')
        
        if not email or not otp:
            return Response(
                {'error': 'Email and OTP are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'error': 'Invalid email or OTP'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Find valid OTP
        otp_entry = OTPCode.objects.filter(
            user=user,
            code=otp,
            is_used=False,
            purpose='login'
        ).first()
        
        if not otp_entry:
            return Response(
                {'error': 'Invalid or expired OTP'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if otp_entry.is_expired:
            return Response(
                {'error': 'OTP has expired. Please request a new one.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Mark OTP as used
        otp_entry.is_used = True
        otp_entry.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Login successful',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'user_type': user.user_type,
            }
        }, status=status.HTTP_200_OK)


class OTPSignupRequestView(APIView):
    """
    Request OTP for new user registration (passwordless signup)
    POST /api/accounts/otp/signup-request/
    Body: {
        "email": "newuser@example.com",
        "username": "newuser123",
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": "+971501234567",
        "country": "UAE",
        "user_type": "customer"
    }
    """
    permission_classes = (AllowAny,)
    
    def post(self, request):
        from django.utils import timezone
        from datetime import timedelta
        
        email = request.data.get('email')
        username = request.data.get('username')
        
        if not email:
            return Response(
                {'error': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not username:
            return Response(
                {'error': 'Username is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            return Response(
                {'error': 'An account with this email already exists. Please use login instead.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if username is taken
        if User.objects.filter(username=username).exists():
            return Response(
                {'error': 'This username is already taken. Please choose another.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Invalidate any existing unused signup OTPs for this email
        OTPCode.objects.filter(email=email, is_used=False, purpose='signup').update(is_used=True)
        
        # Generate new OTP
        code = OTPCode.generate_code()
        expires_at = timezone.now() + timedelta(minutes=15)  # 15 minutes for signup
        
        # Store registration data with the OTP
        registration_data = {
            'email': email,
            'username': username,
            'first_name': request.data.get('first_name', ''),
            'last_name': request.data.get('last_name', ''),
            'phone_number': request.data.get('phone_number', ''),
            'country': request.data.get('country', ''),
            'user_type': request.data.get('user_type', 'customer'),
        }
        
        otp = OTPCode.objects.create(
            email=email,
            code=code,
            expires_at=expires_at,
            purpose='signup',
            registration_data=registration_data
        )
        
        # Send OTP via email
        try:
            subject = 'TezRent - Verify Your Email'
            html_message = f'''
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    .container {{ font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #2563EB; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                    .content {{ background-color: #f8f9fa; padding: 30px; border-radius: 0 0 8px 8px; }}
                    .otp-code {{ font-size: 36px; font-weight: bold; text-align: center; color: #2563EB; letter-spacing: 8px; padding: 20px; background-color: #e8f4ff; border-radius: 8px; margin: 20px 0; }}
                    .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Welcome to TezRent!</h1>
                    </div>
                    <div class="content">
                        <p>Hi {registration_data.get('first_name', 'there')}!</p>
                        <p>Thank you for signing up with TezRent. Use the code below to verify your email and complete your registration:</p>
                        <div class="otp-code">{code}</div>
                        <p><strong>This code will expire in 15 minutes.</strong></p>
                        <p>If you didn't request this, you can safely ignore this email.</p>
                    </div>
                    <div class="footer">
                        <p>&copy; 2025 TezRent. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            '''
            
            email_message = EmailMultiAlternatives(
                subject=subject,
                body=f'Your TezRent verification code is: {code}. This code expires in 15 minutes.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email]
            )
            email_message.attach_alternative(html_message, "text/html")
            email_message.send(fail_silently=False)
            
            print(f"✅ Signup OTP email sent successfully to {email}")
            
        except Exception as e:
            print(f"❌ Failed to send signup OTP email: {str(e)}")
        
        return Response({
            'message': 'Verification code sent to your email. Please check your inbox.',
            'email': email,
            # Include OTP in response for testing (remove in production)
            'otp': code if settings.DEBUG else None,
        }, status=status.HTTP_200_OK)


class OTPSignupVerifyView(APIView):
    """
    Verify OTP and create new user account
    POST /api/accounts/otp/signup-verify/
    Body: { "email": "newuser@example.com", "otp": "123456" }
    """
    permission_classes = (AllowAny,)
    
    def post(self, request):
        from rest_framework_simplejwt.tokens import RefreshToken
        from django.db import transaction
        
        email = request.data.get('email')
        otp = request.data.get('otp')
        
        if not email or not otp:
            return Response(
                {'error': 'Email and OTP are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user already exists (race condition protection)
        if User.objects.filter(email=email).exists():
            return Response(
                {'error': 'An account with this email already exists. Please use login instead.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Find valid OTP
        otp_entry = OTPCode.objects.filter(
            email=email,
            code=otp,
            is_used=False,
            purpose='signup'
        ).first()
        
        if not otp_entry:
            return Response(
                {'error': 'Invalid verification code'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if otp_entry.is_expired:
            return Response(
                {'error': 'Verification code has expired. Please request a new one.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get registration data
        registration_data = otp_entry.registration_data
        if not registration_data:
            return Response(
                {'error': 'Registration data not found. Please start signup again.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                # Create user without password (passwordless account)
                user = User.objects.create(
                    email=registration_data['email'],
                    username=registration_data['username'],
                    first_name=registration_data.get('first_name', ''),
                    last_name=registration_data.get('last_name', ''),
                    phone_number=registration_data.get('phone_number', ''),
                    country=registration_data.get('country', ''),
                    user_type=registration_data.get('user_type', 'customer'),
                    is_active=True
                )
                # Set unusable password for passwordless accounts
                user.set_unusable_password()
                user.save()
                
                # Create profile based on user type
                if user.user_type == 'customer':
                    CustomerProfile.objects.create(user=user)
                elif user.user_type == 'company':
                    CompanyProfile.objects.create(user=user)
                
                # Mark OTP as used
                otp_entry.is_used = True
                otp_entry.save()
                
                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                
                return Response({
                    'message': 'Account created successfully! Welcome to TezRent.',
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'username': user.username,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'user_type': user.user_type,
                        'phone_number': user.phone_number,
                        'country': user.country,
                    }
                }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response(
                {'error': f'Failed to create account: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
