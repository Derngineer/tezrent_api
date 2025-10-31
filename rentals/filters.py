"""
Custom filters for rentals app
"""
import django_filters
from .models import Rental


class RentalFilter(django_filters.FilterSet):
    """
    Custom filter for Rental model
    Supports comma-separated status values
    """
    status = django_filters.CharFilter(method='filter_status')
    
    class Meta:
        model = Rental
        fields = {
            'equipment': ['exact'],
            'start_date': ['exact', 'gte', 'lte'],
            'end_date': ['exact', 'gte', 'lte'],
            'created_at': ['gte', 'lte'],
        }
    
    def filter_status(self, queryset, name, value):
        """
        Handle single or comma-separated status values
        Examples:
            ?status=pending
            ?status=completed,cancelled,disputed
        """
        if not value:
            return queryset
        
        # Split by comma and filter
        statuses = [s.strip() for s in value.split(',') if s.strip()]
        
        if statuses:
            return queryset.filter(status__in=statuses)
        
        return queryset
