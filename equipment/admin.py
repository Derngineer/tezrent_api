from django.contrib import admin
from .models import Category, Equipment, EquipmentImage, EquipmentSpecification

class EquipmentSpecificationInline(admin.TabularInline):
    model = EquipmentSpecification
    extra = 1

class EquipmentImageInline(admin.TabularInline):
    model = EquipmentImage
    extra = 1

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'daily_rate', 'country', 'city', 'status', 'available_units', 'get_tags')
    list_filter = ('category', 'status', 'country', 'city', 'tags')
    search_fields = ('name', 'description', 'model_number', 'tags__name')
    filter_horizontal = ('tags',)  # Only needed for custom implementation
    
    def get_tags(self, obj):
        return ", ".join(o.name for o in obj.tags.all())
    get_tags.short_description = 'Tags'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

admin.site.register(EquipmentImage)
admin.site.register(EquipmentSpecification)
