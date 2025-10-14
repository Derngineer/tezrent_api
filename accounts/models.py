from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.conf import settings

# Country and city choices
COUNTRY_CHOICES = (
    ('UAE', 'United Arab Emirates'),
    ('UZB', 'Uzbekistan'),
)

# City choices by country
UAE_CITY_CHOICES = (
    ('AUH', 'Abu Dhabi'),
    ('DXB', 'Dubai'),
    ('SHJ', 'Sharjah'),
    ('AJM', 'Ajman'),
    ('UAQ', 'Umm Al Quwain'),
    ('FUJ', 'Fujairah'),
    ('RAK', 'Ras Al Khaimah'),
)

UZB_CITY_CHOICES = (
    ('TAS', 'Tashkent'),
    ('SAM', 'Samarkand'),
    ('NAM', 'Namangan'),
    ('AND', 'Andijan'),
)

class User(AbstractUser):
    """
    Custom User model for TezRent that uses email as the primary identifier
    instead of username for authentication.
    """
    email = models.EmailField(_('email address'), unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    
    # Location fields
    country = models.CharField(max_length=3, choices=COUNTRY_CHOICES, blank=True, null=True)
    
    # User type choices
    USER_TYPE_CHOICES = (
        ('customer', 'Customer'),
        ('company', 'Company'),
        ('staff', 'Staff'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='customer')
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # Username still required by Django's admin
    
    def __str__(self):
        return self.email

class CustomerProfile(models.Model):
    """
    Profile for customers who will rent equipment.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer_profile')
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=3, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    rental_history_count = models.IntegerField(default=0)
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return f"Customer Profile: {self.user.email}"
    
    @property
    def city_name(self):
        """Return the human-readable city name based on country"""
        if not self.city:
            return None
            
        if self.user.country == 'UAE':
            return dict(UAE_CITY_CHOICES).get(self.city)
        elif self.user.country == 'UZB':
            return dict(UZB_CITY_CHOICES).get(self.city)
        return self.city

class CompanyProfile(models.Model):
    """
    Profile for companies that might have multiple users or special requirements.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='company_profile')
    company_name = models.CharField(max_length=255)
    business_type = models.CharField(max_length=100)
    company_address = models.TextField()
    city = models.CharField(max_length=3, blank=True, null=True)
    tax_number = models.CharField(max_length=50, blank=True, null=True)
    company_phone = models.CharField(max_length=20)
    
    def __str__(self):
        return f"Company Profile: {self.company_name}"
    
    @property
    def city_name(self):
        """Return the human-readable city name based on country"""
        if not self.city:
            return None
            
        if self.user.country == 'UAE':
            return dict(UAE_CITY_CHOICES).get(self.city)
        elif self.user.country == 'UZB':
            return dict(UZB_CITY_CHOICES).get(self.city)
        return self.city

class StaffProfile(models.Model):
    """
    Profile for staff members who manage the system.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='staff_profile')
    position = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    employee_id = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return f"Staff Profile: {self.user.email} - {self.position}"
