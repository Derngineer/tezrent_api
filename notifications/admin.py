from django.contrib import admin
from .models import Notification, PushNotificationToken, NotificationPreference


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'notification_type', 'title', 'is_read', 
        'push_sent', 'email_sent', 'created_at'
    ]
    list_filter = [
        'notification_type', 'is_read', 'push_sent', 
        'email_sent', 'created_at'
    ]
    search_fields = ['user__email', 'title', 'message']
    readonly_fields = ['created_at', 'read_at', 'push_sent_at', 'email_sent_at']
    
    fieldsets = (
        ('Notification Info', {
            'fields': ('user', 'notification_type', 'title', 'message')
        }),
        ('References', {
            'fields': ('related_rental', 'related_equipment')
        }),
        ('Navigation', {
            'fields': ('action_url', 'navigation_params')
        }),
        ('Status', {
            'fields': (
                'is_read', 'read_at', 
                'push_sent', 'push_sent_at',
                'email_sent', 'email_sent_at',
                'created_at'
            )
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(PushNotificationToken)
class PushNotificationTokenAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'device_type', 'device_name', 
        'is_active', 'created_at', 'last_used_at'
    ]
    list_filter = ['device_type', 'is_active', 'created_at']
    search_fields = ['user__email', 'device_name', 'device_id']
    readonly_fields = ['created_at', 'updated_at', 'last_used_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'push_rental_updates', 'push_messages', 
        'email_rental_updates', 'email_messages', 'updated_at'
    ]
    search_fields = ['user__email']
    readonly_fields = ['updated_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Push Notifications', {
            'fields': (
                'push_rental_updates', 'push_messages',
                'push_payment_updates', 'push_deals_alerts',
                'push_marketing'
            )
        }),
        ('Email Notifications', {
            'fields': (
                'email_rental_updates', 'email_messages',
                'email_payment_updates', 'email_deals_alerts',
                'email_marketing'
            )
        }),
        ('SMS Notifications', {
            'fields': ('sms_rental_updates', 'sms_payment_updates'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('updated_at',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

