from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import COUNTRY_CHOICES, UAE_CITY_CHOICES, UZB_CITY_CHOICES, CustomerProfile, CompanyProfile, StaffProfile
from django.db import transaction

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model"""
    country_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'user_type', 'phone_number', 'country', 'country_name')
        read_only_fields = ('id', 'country_name')
    
    def get_country_name(self, obj):
        return dict(COUNTRY_CHOICES).get(obj.country) if obj.country else None

class CustomerProfileSerializer(serializers.ModelSerializer):
    """Serializer for customer profiles"""
    city_name = serializers.ReadOnlyField()
    
    class Meta:
        model = CustomerProfile
        fields = ('address', 'city', 'city_name', 'date_of_birth')

class CompanyProfileSerializer(serializers.ModelSerializer):
    """Serializer for company profiles"""
    city_name = serializers.ReadOnlyField()
    
    class Meta:
        model = CompanyProfile
        fields = ('company_name', 'business_type', 'company_address', 'city', 'city_name', 'tax_number', 'company_phone')

class StaffProfileSerializer(serializers.ModelSerializer):
    """Serializer for staff profiles"""
    class Meta:
        model = StaffProfile
        fields = ('position', 'department', 'employee_id')

class CustomerRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for registering new customer accounts"""
    profile = CustomerProfileSerializer(required=False, write_only=True)
    profile_data = serializers.SerializerMethodField(read_only=True)
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'confirm_password', 'first_name', 'last_name', 'phone_number', 'profile', 'profile_data')
    
    def get_profile_data(self, obj):
        """Get customer profile data if it exists"""
        try:
            profile = obj.customer_profile
            return CustomerProfileSerializer(profile).data
        except CustomerProfile.DoesNotExist:
            return None
    
    def validate(self, data):
        # Existing validation code...
        if data['password'] != data.pop('confirm_password'):
            raise serializers.ValidationError("Passwords do not match.")
        
        # Validate country and city combination if provided
        profile_data = data.get('profile', {})
        user_country = data.get('country')
        profile_city = profile_data.get('city')
        
        if user_country and profile_city:
            valid_cities = []
            if user_country == 'UAE':
                valid_cities = [city[0] for city in UAE_CITY_CHOICES]
            elif user_country == 'UZB':
                valid_cities = [city[0] for city in UZB_CITY_CHOICES]
                
            if profile_city not in valid_cities:
                raise serializers.ValidationError({
                    'profile': {'city': f'Invalid city for {user_country}'}
                })
        
        return data
    
    @transaction.atomic
    def create(self, validated_data):
        profile_data = validated_data.pop('profile', None)
        validated_data['user_type'] = 'customer'
        
        user = User.objects.create_user(**validated_data)
        
        if profile_data:
            CustomerProfile.objects.create(user=user, **profile_data)
        else:
            CustomerProfile.objects.create(user=user)
            
        return user

class CompanyRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for registering new company accounts"""
    profile = CompanyProfileSerializer(write_only=True)
    profile_data = serializers.SerializerMethodField(read_only=True)
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'confirm_password', 'first_name', 'last_name', 'phone_number', 'profile', 'profile_data')
    
    def get_profile_data(self, obj):
        """Get company profile data if it exists"""
        try:
            profile = obj.company_profile
            return CompanyProfileSerializer(profile).data
        except CompanyProfile.DoesNotExist:
            return None
    
    def validate(self, data):
        if data['password'] != data.pop('confirm_password'):
            raise serializers.ValidationError("Passwords do not match.")
        return data
    
    @transaction.atomic
    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        validated_data['user_type'] = 'company'
        
        user = User.objects.create_user(**validated_data)
        CompanyProfile.objects.create(user=user, **profile_data)
            
        return user