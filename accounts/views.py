from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
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
