from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Tag, Equipment, EquipmentImage, EquipmentSpecification, Banner


class EquipmentSpecificationInline(admin.TabularInline):
    model = EquipmentSpecification
    extra = 1
    fields = ['name', 'value']


class EquipmentImageInline(admin.TabularInline):
    model = EquipmentImage
    extra = 1
    fields = ['image', 'is_primary', 'display_order', 'caption']
    readonly_fields = ['image_preview']
    max_num = 7
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Preview'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_featured', 'display_order', 'equipment_count']
    list_filter = ['is_featured']
    search_fields = ['name', 'description', 'slug']
    ordering = ['display_order', 'name']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'slug')
        }),
        ('Display Settings', {
            'fields': ('icon', 'promotional_image', 'display_order', 'is_featured', 'color_code')
        }),
    )
    
    def equipment_count(self, obj):
        return obj.equipment.filter(status='available').count()
    equipment_count.short_description = 'Available Equipment'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'equipment_count']
    search_fields = ['name']
    
    def equipment_count(self, obj):
        return obj.equipment.count()
    equipment_count.short_description = 'Equipment Count'


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category', 'seller_company_name', 'daily_rate', 
        'country', 'city', 'status', 'available_units', 'featured',
        'is_new_listing', 'is_todays_deal'
    ]
    list_filter = [
        'category', 'status', 'country', 'city',
        'featured', 'is_new_listing', 'is_todays_deal', 'tags'
    ]
    search_fields = ['name', 'description', 'model_number', 'seller_company__company_name']
    filter_horizontal = ['tags']
    inlines = [EquipmentImageInline, EquipmentSpecificationInline]
    readonly_fields = ['created_at', 'updated_at', 'discounted_daily_rate', 'savings_amount', 'is_deal_active']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'category', 'tags')
        }),
        ('Seller Information', {
            'fields': ('seller_company',)
        }),
        ('Equipment Details', {
            'fields': (
                'model_number', 'manufacturer', 'year',
                'weight', 'dimensions', 'fuel_type'
            )
        }),
        ('Pricing', {
            'fields': ('daily_rate', 'weekly_rate', 'monthly_rate')
        }),
        ('Location', {
            'fields': ('country', 'city')
        }),
        ('Promotional Features', {
            'fields': (
                'featured', 'is_new_listing', 'is_todays_deal',
                'original_daily_rate', 'deal_discount_percentage', 'deal_expires_at',
                'promotion_badge', 'promotion_description'
            ),
            'classes': ('collapse',)
        }),
        ('Status & Availability', {
            'fields': ('status', 'total_units', 'available_units')
        }),
        ('Computed Values', {
            'fields': ('discounted_daily_rate', 'savings_amount', 'is_deal_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def seller_company_name(self, obj):
        return obj.seller_company.company_name if obj.seller_company else "N/A"
    seller_company_name.short_description = 'Seller'
    seller_company_name.admin_order_field = 'seller_company__company_name'


@admin.register(EquipmentImage)
class EquipmentImageAdmin(admin.ModelAdmin):
    list_display = ['equipment', 'is_primary', 'display_order', 'caption', 'image_preview']
    list_filter = ['is_primary']
    search_fields = ['equipment__name', 'caption']
    list_editable = ['is_primary', 'display_order']
    
    fieldsets = (
        ('Equipment', {
            'fields': ('equipment',)
        }),
        ('Image Details', {
            'fields': ('image', 'caption')
        }),
        ('Display Settings', {
            'fields': ('is_primary', 'display_order')
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Preview'


@admin.register(EquipmentSpecification)
class EquipmentSpecificationAdmin(admin.ModelAdmin):
    list_display = ['equipment', 'name', 'value']
    list_filter = ['name']
    search_fields = ['equipment__name', 'name', 'value']


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'banner_type', 'position', 'is_active', 
        'display_order', 'click_count', 'view_count', 'image_preview'
    ]
    list_filter = ['banner_type', 'position', 'is_active', 'start_date', 'end_date']
    search_fields = ['title', 'subtitle', 'description', 'cta_text']
    list_editable = ['is_active', 'display_order']
    readonly_fields = ['click_count', 'view_count', 'created_at', 'updated_at', 'is_currently_active']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'subtitle', 'description', 'banner_type', 'position')
        }),
        ('Images', {
            'fields': ('desktop_image', 'mobile_image')
        }),
        ('Call to Action', {
            'fields': ('cta_text', 'cta_link')
        }),
        ('Targeting', {
            'fields': ('target_category', 'target_equipment'),
            'classes': ('collapse',)
        }),
        ('Display Settings', {
            'fields': ('is_active', 'display_order', 'start_date', 'end_date')
        }),
        ('Statistics', {
            'fields': ('click_count', 'view_count', 'is_currently_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def image_preview(self, obj):
        if obj.desktop_image:
            return format_html('<img src="{}" width="150" height="75" />', obj.desktop_image.url)
        return "No Image"
    image_preview.short_description = 'Preview'
