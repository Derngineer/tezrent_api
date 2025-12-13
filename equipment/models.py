from django.db import models
from django.conf import settings
from accounts.models import COUNTRY_CHOICES, UAE_CITY_CHOICES, UZB_CITY_CHOICES

class Category(models.Model):
    """Equipment categories like excavators, loaders, etc."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Icon for category (small, used in navigation, cards, etc.)
    icon = models.ImageField(
        upload_to='category_icons/', 
        blank=True, 
        null=True,
        help_text="Small icon for category (64x64px recommended) - used in navigation, category cards"
    )
    
    # Promotional/banner image (larger, used for featured sections)
    promotional_image = models.ImageField(
        upload_to='category_promotions/',
        blank=True,
        null=True,
        help_text="Larger promotional image (400x200px recommended) - used in featured sections, banners"
    )
    
    # Category display settings
    is_featured = models.BooleanField(default=False, help_text="Show in featured categories section")
    display_order = models.PositiveIntegerField(default=1, help_text="Order for displaying categories")
    color_code = models.CharField(
        max_length=7, 
        blank=True, 
        help_text="Hex color code for category theme (e.g., #FF6B35)"
    )
    
    # SEO and mobile optimization
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['display_order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Auto-generate slug from name if not provided"""
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    @property
    def icon_url(self):
        """Get icon URL for React Native"""
        return self.icon.url if self.icon else None
    
    @property
    def promotional_image_url(self):
        """Get promotional image URL for React Native"""
        return self.promotional_image.url if self.promotional_image else None
    
    @property
    def equipment_count(self):
        """Count of equipment in this category"""
        return self.equipment.filter(status='available').count()

class Tag(models.Model):
    """Custom tag model for equipment"""
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class Equipment(models.Model):
    """Main equipment model for rentable machinery"""
    
    # Seller information - which company listed this equipment
    seller_company = models.ForeignKey(
        'accounts.CompanyProfile', 
        on_delete=models.CASCADE, 
        related_name='listed_equipment',
        help_text="The company that listed this equipment"
    )
    
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
    
    # Promotional and Marketing Features
    featured = models.BooleanField(default=False, help_text="Show in featured brands section")
    is_new_listing = models.BooleanField(default=True, help_text="Mark as new listing (auto-expires after 30 days)")
    is_todays_deal = models.BooleanField(default=False, help_text="Show in today's deals section")
    # Soft-active flag used across codebase to show/hide equipment listings
    is_active = models.BooleanField(default=True, help_text="Show/hide this equipment in listings")
    
    # Deal pricing
    original_daily_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Original price before discount")
    deal_discount_percentage = models.PositiveIntegerField(default=0, help_text="Discount percentage (0-100)")
    deal_expires_at = models.DateTimeField(null=True, blank=True, help_text="When the deal expires")
    
    # Banner and promotion content
    promotion_badge = models.CharField(max_length=50, blank=True, help_text="Badge text like 'HOT DEAL', 'LIMITED TIME'")
    promotion_description = models.TextField(blank=True, help_text="Special promotion description")
    
    # Operating Manual (available after payment)
    operating_manual = models.FileField(
        upload_to='equipment_manuals/',
        blank=True,
        null=True,
        help_text="Operating manual/user guide (PDF) - Available to customers after booking confirmation"
    )
    manual_description = models.TextField(
        blank=True,
        help_text="Description of what's included in the manual"
    )
    
    # Other fields
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
    
    def is_available_on_dates(self, start_date, end_date, requested_quantity=1):
        """Check if equipment is available for the given date range"""
        from rentals.models import Rental
        from django.db.models import Sum
        
        # Calculate total quantity rented during this period
        # Only count confirmed/active rentals, not pending or cancelled
        rented_quantity = Rental.objects.filter(
            equipment=self,
            status__in=['confirmed', 'preparing', 'ready_for_pickup', 
                       'out_for_delivery', 'delivered', 'in_progress'],
            start_date__lte=end_date,
            end_date__gte=start_date
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        # Check if we have enough units available
        available = self.available_units - rented_quantity
        return available >= requested_quantity
    
    @property
    def primary_image_url(self):
        """Get the primary image URL for product cards"""
        primary = self.images.filter(is_primary=True).first()
        return primary.image.url if primary else None
    
    @property
    def all_image_urls(self):
        """Get all image URLs in display order for product cards"""
        return [img.image.url for img in self.images.all()[:7]]  # Max 7 images
    
    @property
    def discounted_daily_rate(self):
        """Calculate discounted daily rate if on deal"""
        if self.is_todays_deal and self.deal_discount_percentage > 0:
            discount_amount = (self.daily_rate * self.deal_discount_percentage) / 100
            return self.daily_rate - discount_amount
        return self.daily_rate
    
    @property
    def savings_amount(self):
        """Calculate how much user saves with current deal"""
        if self.is_todays_deal and self.deal_discount_percentage > 0:
            return (self.daily_rate * self.deal_discount_percentage) / 100
        return 0
    
    @property
    def is_deal_active(self):
        """Check if deal is currently active"""
        if not self.is_todays_deal:
            return False
        if self.deal_expires_at:
            from django.utils import timezone
            return timezone.now() <= self.deal_expires_at
        return True
    
    @property
    def days_since_listed(self):
        """Calculate days since equipment was first listed"""
        from django.utils import timezone
        delta = timezone.now() - self.created_at
        return delta.days
    
    @property
    def is_actually_new(self):
        """Check if equipment is genuinely new (less than 30 days old)"""
        return self.is_new_listing and self.days_since_listed <= 30
    
    def get_image_gallery(self):
        """Get structured image data for frontend gallery"""
        images = self.images.all()[:7]  # Max 7 images
        return [
            {
                'id': img.id,
                'url': img.image.url,
                'is_primary': img.is_primary,
                'display_order': img.display_order,
                'caption': img.caption
            }
            for img in images
        ]

class EquipmentImage(models.Model):
    """Images for equipment listings - Max 7 images per equipment"""
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='equipment_images/')
    is_primary = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=1, help_text="Order for displaying in product card (1-7)")
    caption = models.CharField(max_length=255, blank=True)
    
    class Meta:
        ordering = ['display_order', 'id']
        unique_together = ['equipment', 'display_order']
    
    def __str__(self):
        return f"Image {self.display_order} for {self.equipment}"
    
    def save(self, *args, **kwargs):
        """Ensure only one primary image per equipment and max 7 images"""
        # Check image limit
        if not self.pk:  # Only for new images
            existing_count = EquipmentImage.objects.filter(equipment=self.equipment).count()
            if existing_count >= 7:
                raise ValueError("Maximum 7 images allowed per equipment")
        
        # Ensure only one primary image
        if self.is_primary:
            EquipmentImage.objects.filter(
                equipment=self.equipment, 
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        
        # Auto-assign display_order if not provided
        if not self.display_order or self.display_order < 1:
            max_order = EquipmentImage.objects.filter(
                equipment=self.equipment
            ).aggregate(models.Max('display_order'))['display_order__max'] or 0
            self.display_order = max_order + 1
        
        # Ensure display_order doesn't exceed 7
        if self.display_order > 7:
            self.display_order = 7
            
        super().save(*args, **kwargs)

class EquipmentSpecification(models.Model):
    """Additional specifications for equipment"""
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='specifications')
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=255)
    
    def __str__(self):
        return f"{self.name}: {self.value}"

class Banner(models.Model):
    """Homepage promotional banners for React/Next.js frontend"""
    
    BANNER_TYPE_CHOICES = (
        ('hero', 'Hero Banner'),
        ('featured_deals', 'Featured Deals Banner'),
        ('category_highlight', 'Category Highlight Banner'),
        ('brand_spotlight', 'Brand Spotlight Banner'),
        ('seasonal_promo', 'Seasonal Promotion Banner'),
    )
    
    POSITION_CHOICES = (
        ('top', 'Top of Homepage'),
        ('middle', 'Middle Section'),
        ('bottom', 'Bottom Section'),
        ('sidebar', 'Sidebar'),
    )
    
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    
    # Banner styling and content
    banner_type = models.CharField(max_length=20, choices=BANNER_TYPE_CHOICES)
    position = models.CharField(max_length=10, choices=POSITION_CHOICES, default='top')
    
    # Images
    desktop_image = models.ImageField(upload_to='banners/desktop/', help_text="Desktop banner image (1920x400px recommended)")
    mobile_image = models.ImageField(upload_to='banners/mobile/', blank=True, null=True, help_text="Mobile banner image (768x300px recommended)")
    
    # Call to action
    cta_text = models.CharField(max_length=50, default='Shop Now')
    cta_link = models.CharField(max_length=500, blank=True, help_text="Link to category, deals page, or external URL")
    
    # Targeting and display rules
    target_category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, help_text="Show banner for specific category")
    target_equipment = models.ForeignKey(Equipment, on_delete=models.SET_NULL, null=True, blank=True, help_text="Feature specific equipment")
    
    # Status and scheduling
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    display_order = models.PositiveIntegerField(default=1, help_text="Order for displaying multiple banners")
    
    # Tracking
    click_count = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['position', 'display_order']
    
    def __str__(self):
        return f"{self.get_banner_type_display()} - {self.title}"
    
    @property
    def is_currently_active(self):
        """Check if banner should be displayed now"""
        if not self.is_active:
            return False
        
        from django.utils import timezone
        now = timezone.now()
        
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        
        return True
    
    def increment_view_count(self):
        """Increment view count for analytics"""
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    def increment_click_count(self):
        """Increment click count for analytics"""
        self.click_count += 1
        self.save(update_fields=['click_count'])
