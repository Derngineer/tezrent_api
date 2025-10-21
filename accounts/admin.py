from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, CustomerProfile, CompanyProfile, StaffProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User Admin with enhanced display"""
    list_display = [
        'email', 'username', 'user_type', 'country', 
        'phone_number', 'is_active', 'is_staff', 'date_joined'
    ]
    list_filter = ['user_type', 'country', 'is_active', 'is_staff', 'is_superuser', 'date_joined']
    search_fields = ['email', 'username', 'phone_number', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {
            'fields': ('email', 'username', 'password')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'phone_number')
        }),
        ('Location', {
            'fields': ('country',)
        }),
        ('User Type', {
            'fields': ('user_type',)
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'user_type', 'country', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ['date_joined', 'last_login']


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    """Customer Profile Admin"""
    list_display = [
        'user_email', 'user_name', 'city_display', 'rental_history_count', 
        'total_spent', 'date_of_birth'
    ]
    list_filter = ['city', 'user__country']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'address']
    readonly_fields = ['rental_history_count', 'total_spent']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Profile Details', {
            'fields': ('address', 'city', 'date_of_birth')
        }),
        ('Statistics', {
            'fields': ('rental_history_count', 'total_spent'),
            'classes': ('collapse',)
        }),
    )
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'
    user_email.admin_order_field = 'user__email'
    
    def user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or "N/A"
    user_name.short_description = 'Name'
    
    def city_display(self, obj):
        return obj.city_name or obj.city or "N/A"
    city_display.short_description = 'City'


@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    """Company Profile Admin"""
    list_display = [
        'company_name', 'user_email', 'business_type', 
        'city_display', 'company_phone', 'tax_number'
    ]
    list_filter = ['business_type', 'city', 'user__country']
    search_fields = [
        'company_name', 'user__email', 'business_type', 
        'tax_number', 'company_phone', 'company_address'
    ]
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Company Details', {
            'fields': ('company_name', 'business_type', 'company_phone')
        }),
        ('Location', {
            'fields': ('company_address', 'city')
        }),
        ('Tax Information', {
            'fields': ('tax_number',),
            'classes': ('collapse',)
        }),
    )
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'
    
    def city_display(self, obj):
        return obj.city_name or obj.city or "N/A"
    city_display.short_description = 'City'


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    """Staff Profile Admin"""
    list_display = [
        'user_email', 'user_name', 'position', 
        'department', 'employee_id'
    ]
    list_filter = ['department', 'position']
    search_fields = [
        'user__email', 'user__first_name', 'user__last_name', 
        'position', 'department', 'employee_id'
    ]
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Staff Details', {
            'fields': ('employee_id', 'position', 'department')
        }),
    )
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'
    user_email.admin_order_field = 'user__email'
    
    def user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or "N/A"
    user_name.short_description = 'Name'
