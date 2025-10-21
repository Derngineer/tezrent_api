from django.contrib import admin
from .models import Favorite, FavoriteCollection, RecentlyViewed


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = [
        'customer', 'equipment', 'is_available', 'current_price',
        'notify_on_deals', 'created_at'
    ]
    list_filter = [
        'notify_on_availability', 'notify_on_price_drop',
        'notify_on_deals', 'created_at'
    ]
    search_fields = [
        'customer__user__email', 'equipment__name', 'notes'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Favorite Info', {
            'fields': ('customer', 'equipment', 'notes')
        }),
        ('Rental Preferences', {
            'fields': (
                'preferred_rental_start', 'preferred_rental_duration'
            )
        }),
        ('Notifications', {
            'fields': (
                'notify_on_availability', 'notify_on_price_drop',
                'notify_on_deals'
            )
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'customer__user', 'equipment'
        )


@admin.register(FavoriteCollection)
class FavoriteCollectionAdmin(admin.ModelAdmin):
    list_display = [
        'customer', 'name', 'item_count', 'is_public',
        'created_at'
    ]
    list_filter = ['is_public', 'created_at']
    search_fields = ['customer__user__email', 'name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'item_count', 'total_estimated_cost']
    filter_horizontal = ['equipment']
    
    fieldsets = (
        ('Collection Info', {
            'fields': ('customer', 'name', 'description', 'is_public')
        }),
        ('Display Settings', {
            'fields': ('icon', 'color')
        }),
        ('Equipment', {
            'fields': ('equipment',)
        }),
        ('Stats', {
            'fields': ('item_count', 'total_estimated_cost'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'customer__user'
        ).prefetch_related('equipment')


@admin.register(RecentlyViewed)
class RecentlyViewedAdmin(admin.ModelAdmin):
    list_display = [
        'customer', 'equipment', 'view_count',
        'last_viewed_at', 'viewed_from'
    ]
    list_filter = ['viewed_from', 'last_viewed_at']
    search_fields = ['customer__user__email', 'equipment__name']
    readonly_fields = ['first_viewed_at', 'last_viewed_at', 'view_count']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'customer__user', 'equipment'
        )
