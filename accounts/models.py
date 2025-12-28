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

class DeliveryAddress(models.Model):
    """
    Multiple delivery locations for a user.
    Stores detailed address information and coordinates.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='delivery_addresses')
    label = models.CharField(max_length=50, help_text="e.g. Home, Office, Warehouse")
    
    # Detailed address fields
    apartment_room = models.CharField(max_length=50, blank=True, help_text="Apartment, Suite, or Room number")
    building = models.CharField(max_length=100, blank=True, help_text="Building name or number")
    street_landmark = models.CharField(max_length=255, help_text="Street name and nearby landmark")
    city = models.CharField(max_length=50)
    contact_number = models.CharField(max_length=20, help_text="Contact number for this location")
    
    # Geo coordinates
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_default', '-created_at']
        verbose_name_plural = "Delivery Addresses"

    def __str__(self):
        return f"{self.label} - {self.street_landmark}"

    def save(self, *args, **kwargs):
        # If this is set as default, unset others
        if self.is_default:
            DeliveryAddress.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

class StaffProfile(models.Model):
    """
    Profile for internal staff members.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='staff_profile')
    employee_id = models.CharField(max_length=20, unique=True)
    position = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    
    def __str__(self):
        return f"Staff: {self.user.email} - {self.position}"


class OTPCode(models.Model):
    """
    OTP codes for passwordless authentication.
    Users can login via email OTP as an alternative to password.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='otp_codes')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    # Track purpose
    PURPOSE_CHOICES = (
        ('login', 'Login'),
        ('verify_email', 'Email Verification'),
    )
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES, default='login')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'OTP Code'
        verbose_name_plural = 'OTP Codes'
    
    def __str__(self):
        return f"OTP for {self.user.email} - {'Used' if self.is_used else 'Active'}"
    
    @property
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at
    
    @property
    def is_valid(self):
        return not self.is_used and not self.is_expired
    
    @classmethod
    def generate_code(cls):
        """Generate a random 6-digit OTP"""
        import random
        return str(random.randint(100000, 999999))
