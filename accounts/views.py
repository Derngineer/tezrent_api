from django.shortcuts import render
from rest_framework import generics, permissions, status
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
from .models import COUNTRY_CHOICES, UAE_CITY_CHOICES, UZB_CITY_CHOICES, CustomerProfile, CompanyProfile, StaffProfile
from .serializers import (
    UserSerializer, CustomerRegistrationSerializer, 
    CompanyRegistrationSerializer, CustomerProfileSerializer,
    CompanyProfileSerializer, StaffProfileSerializer
)

User = get_user_model()

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
            except CustomerProfile.DoesNotExist:
                data['profile'] = None
                
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
