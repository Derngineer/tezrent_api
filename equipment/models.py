from django.db import models
from django.conf import settings
from accounts.models import COUNTRY_CHOICES, UAE_CITY_CHOICES, UZB_CITY_CHOICES

class Category(models.Model):
    """Equipment categories like excavators, loaders, etc."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.ImageField(upload_to='category_icons/', blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"

class Tag(models.Model):
    """Custom tag model for equipment"""
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class Equipment(models.Model):
    """Main equipment model for rentable machinery"""
    
    # Basic information
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='equipment')
    
    # Using custom Tag model with M2M relationship
    tags = models.ManyToManyField(Tag, related_name='equipment', blank=True)
    
    # Technical specs
    manufacturer = models.CharField(max_length=100)
    model_number = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    weight = models.DecimalField(max_digits=10, decimal_places=2, help_text="Weight in kg")
    dimensions = models.CharField(max_length=100, help_text="LxWxH in cm")
    fuel_type = models.CharField(max_length=50, blank=True)
    
    # Pricing
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2)
    weekly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    monthly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Location
    country = models.CharField(max_length=3, choices=COUNTRY_CHOICES)
    city = models.CharField(max_length=3)
    
    # Availability
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('maintenance', 'Under Maintenance'),
        ('rented', 'Currently Rented'),
        ('reserved', 'Reserved'),
        ('inactive', 'Inactive'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    total_units = models.PositiveIntegerField(default=1)
    available_units = models.PositiveIntegerField(default=1)
    
    # Other fields
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.model_number}"
    
    @property
    def city_name(self):
        """Return human-readable city name"""
        if self.country == 'UAE':
            return dict(UAE_CITY_CHOICES).get(self.city)
        elif self.country == 'UZB':
            return dict(UZB_CITY_CHOICES).get(self.city)
        return self.city
    
    @property
    def country_name(self):
        """Return human-readable country name"""
        return dict(COUNTRY_CHOICES).get(self.country)
    
    def is_available_on_dates(self, start_date, end_date):
        """Check if equipment is available for the given date range"""
        from rentals.models import Rental
        
        # Calculate number of units rented during this period
        rented_units = Rental.objects.filter(
            equipment=self,
            status__in=['confirmed', 'out_for_delivery', 'delivered'],
            start_date__lte=end_date,
            end_date__gte=start_date
        ).count()
        
        return self.available_units > rented_units

class EquipmentImage(models.Model):
    """Images for equipment listings"""
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='equipment_images/')
    is_primary = models.BooleanField(default=False)
    caption = models.CharField(max_length=255, blank=True)
    
    def __str__(self):
        return f"Image for {self.equipment}"
    
    def save(self, *args, **kwargs):
        """Ensure only one primary image per equipment"""
        if self.is_primary:
            EquipmentImage.objects.filter(
                equipment=self.equipment, 
                is_primary=True
            ).update(is_primary=False)
        super().save(*args, **kwargs)

class EquipmentSpecification(models.Model):
    """Additional specifications for equipment"""
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='specifications')
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=255)
    
    def __str__(self):
        return f"{self.name}: {self.value}"
