"""
Test dashboard_summary endpoint
"""

import django
import os
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from rentals.models import Rental, RentalSale
from equipment.models import Equipment
from django.utils import timezone
from datetime import timedelta

print("=" * 60)
print("DASHBOARD SUMMARY TEST")
print("=" * 60)

# Check current data
print("\n📊 Current System Status:")
print(f"   Total Equipment: {Equipment.objects.exclude(status='inactive').count()}")
print(f"   Total Rentals: {Rental.objects.count()}")

active_statuses = ['confirmed', 'preparing', 'ready_for_pickup', 
                  'out_for_delivery', 'delivered', 'in_progress']
active_rentals = Rental.objects.filter(status__in=active_statuses)
print(f"   Active Rentals: {active_rentals.count()}")
if active_rentals.exists():
    for rental in active_rentals:
        print(f"      - {rental.rental_reference}: {rental.status}")

pending_rentals = Rental.objects.filter(status='pending')
print(f"   Pending Approvals: {pending_rentals.count()}")
if pending_rentals.exists():
    for rental in pending_rentals:
        print(f"      - {rental.rental_reference}: waiting for approval")

completed_rentals = Rental.objects.filter(status='completed')
print(f"   Completed Rentals: {completed_rentals.count()}")

# Check sales
sales_count = RentalSale.objects.count()
print(f"   Sales Records: {sales_count}")

if sales_count > 0:
    print("\n💰 Sales Details:")
    for sale in RentalSale.objects.all():
        print(f"   - {sale.rental.rental_reference}")
        print(f"     Revenue: {sale.total_revenue}")
        print(f"     Commission: {sale.platform_commission_amount}")
        print(f"     Seller Payout: {sale.seller_payout}")
        print(f"     Status: {sale.payout_status}")
        print(f"     Date: {sale.sale_date}")

# Check monthly stats
now = timezone.now()
first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
this_month_sales = RentalSale.objects.filter(sale_date__gte=first_day_of_month)
print(f"\n📅 This Month ({now.strftime('%B %Y')}):")
print(f"   Sales: {this_month_sales.count()}")
if this_month_sales.exists():
    from django.db.models import Sum
    stats = this_month_sales.aggregate(
        total=Sum('total_revenue'),
        commission=Sum('platform_commission_amount')
    )
    print(f"   Revenue: {stats['total'] or 0}")
    print(f"   Commission: {stats['commission'] or 0}")

print("\n✅ Dashboard endpoint should return:")
print(f"   - total_equipment: {Equipment.objects.exclude(status='inactive').count()}")
print(f"   - active_rentals: {Rental.objects.filter(status__in=active_statuses).count()}")
print(f"   - pending_approvals: {Rental.objects.filter(status='pending').count()}")
print(f"   - monthly_revenue: {stats.get('total', 0) if 'stats' in locals() else 0}")

print("\n" + "=" * 60)
print("TEST ENDPOINT:")
print("GET /api/rentals/rentals/dashboard_summary/")
print("=" * 60)
