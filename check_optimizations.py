#!/usr/bin/env python
"""
Check all query optimizations for correctfield references
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from equipment.models import Equipment, Category
from rentals.models import Rental
from crm.models import Lead, SalesOpportunity, CustomerInteraction, SupportTicket
from favorites.models import Favorite

def check_equipment_optimizations():
    """Test Equipment query optimizations"""
    print("Testing Equipment optimizations...")
    try:
        # Test the exact queryset from views.py line 200-220
        queryset = Equipment.objects.select_related(
            'category',
            'seller_company',
            'seller_company__user',
        ).prefetch_related(
            'tags',
            'images',
        ).only(
            'id', 'name', 'daily_rate', 'status',
            'is_active', 'available_units', 'created_at',
            'category__id', 'category__name',
            'seller_company__id', 'seller_company__company_name'
        )
        list(queryset)  # Force query execution
        print("✅ Equipment optimizations OK")
        return True
    except Exception as e:
        print(f"❌ Equipment error: {e}")
        return False

def check_rental_optimizations():
    """Test Rental query optimizations"""
    print("\nTesting Rental optimizations...")
    try:
        queryset = Rental.objects.select_related(
            'equipment', 'customer', 'seller', 'customer__user', 'seller__user'
        ).prefetch_related(
            'status_updates', 'images', 'payments', 'documents'
        )
        list(queryset)
        print("✅ Rental optimizations OK")
        return True
    except Exception as e:
        print(f"❌ Rental error: {e}")
        return False

def check_crm_optimizations():
    """Test CRM query optimizations"""
    print("\nTesting CRM optimizations...")
    errors = []
    
    # Lead
    try:
        queryset = Lead.objects.select_related(
            'assigned_to', 'interested_category', 'converted_to_customer'
        )
        list(queryset)
        print("✅ Lead optimizations OK")
    except Exception as e:
        print(f"❌ Lead error: {e}")
        errors.append(str(e))
    
    # SalesOpportunity
    try:
        queryset = SalesOpportunity.objects.select_related(
            'lead', 'company', 'customer', 'assigned_to', 'won_rental'
        ).prefetch_related('equipment_items')
        list(queryset)
        print("✅ SalesOpportunity optimizations OK")
    except Exception as e:
        print(f"❌ SalesOpportunity error: {e}")
        errors.append(str(e))
    
    # CustomerInteraction
    try:
        queryset = CustomerInteraction.objects.select_related(
            'lead', 'customer', 'company', 'handled_by', 'related_rental'
        )
        list(queryset)
        print("✅ CustomerInteraction optimizations OK")
    except Exception as e:
        print(f"❌ CustomerInteraction error: {e}")
        errors.append(str(e))
    
    # SupportTicket
    try:
        queryset = SupportTicket.objects.select_related(
            'customer__user', 'company', 'related_rental',
            'related_equipment', 'assigned_to', 'resolved_by'
        ).prefetch_related('comments')
        list(queryset)
        print("✅ SupportTicket optimizations OK")
    except Exception as e:
        print(f"❌ SupportTicket error: {e}")
        errors.append(str(e))
    
    return len(errors) == 0

def check_favorites_optimizations():
    """Test Favorites query optimizations"""
    print("\nTesting Favorites optimizations...")
    try:
        queryset = Favorite.objects.select_related(
            'equipment', 'equipment__seller_company', 'customer__user'
        )
        list(queryset)
        print("✅ Favorites optimizations OK")
        return True
    except Exception as e:
        print(f"❌ Favorites error: {e}")
        return False

def main():
    print("=" * 60)
    print("CHECKING ALL QUERY OPTIMIZATIONS")
    print("=" * 60)
    
    results = []
    results.append(check_equipment_optimizations())
    results.append(check_rental_optimizations())
    results.append(check_crm_optimizations())
    results.append(check_favorites_optimizations())
    
    print("\n" + "=" * 60)
    if all(results):
        print("✅ ALL OPTIMIZATIONS PASSED!")
    else:
        print(f"❌ {len([r for r in results if not r])} OPTIMIZATION(S) FAILED")
    print("=" * 60)

if __name__ == '__main__':
    main()
