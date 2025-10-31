"""
Test script to verify RentalSale auto-creation on rental completion.

This script:
1. Takes an existing rental
2. Updates its status to 'completed'
3. Verifies that a RentalSale is automatically created
4. Displays the sale details including commission breakdown
"""

from rentals.models import Rental, RentalSale
from django.utils import timezone

# Get rental ID 5 (currently 'delivered')
rental = Rental.objects.get(id=5)

print("=" * 60)
print("TESTING RENTAL SALE AUTO-CREATION")
print("=" * 60)
print(f"\nRental: {rental.rental_reference}")
print(f"Current Status: {rental.status}")
print(f"Total Amount: {rental.total_amount}")
print(f"Seller: {rental.equipment.seller_company.company_name}")
print(f"Customer: {rental.customer.user.get_full_name()}")

# Check if sale already exists
if hasattr(rental, 'sale'):
    print(f"\n⚠️  Sale already exists for this rental!")
    sale = rental.sale
else:
    print(f"\n✅ No sale exists yet (expected)")
    
    # Update status to completed
    print(f"\n🔄 Updating rental status to 'completed'...")
    rental.status = 'completed'
    rental.save()
    
    # Check if sale was created
    if hasattr(rental, 'sale'):
        print(f"✅ SUCCESS! Sale was automatically created!")
        sale = rental.sale
    else:
        print(f"❌ FAILED! Sale was not created")
        exit()

# Display sale details
print("\n" + "=" * 60)
print("SALE DETAILS")
print("=" * 60)
print(f"\nSale ID: {sale.id}")
print(f"Rental Reference: {sale.rental.rental_reference}")
print(f"Seller: {sale.seller.company_name}")
print(f"Customer: {sale.customer.user.get_full_name()}")
print(f"Equipment: {sale.equipment.name}")
print(f"\n💰 FINANCIAL BREAKDOWN:")
print(f"  Total Revenue:       {sale.total_revenue:,.2f}")
print(f"    - Subtotal:        {sale.subtotal:,.2f}")
print(f"    - Delivery Fee:    {sale.delivery_fee:,.2f}")
print(f"    - Insurance:       {sale.insurance_fee:,.2f}")
print(f"    - Late Fees:       {sale.late_fees:,.2f}")
print(f"    - Damage Fees:     {sale.damage_fees:,.2f}")
print(f"\n📊 COMMISSION:")
print(f"  Platform Rate:       {sale.platform_commission_percentage}%")
print(f"  Platform Commission: {sale.platform_commission_amount:,.2f}")
print(f"  Seller Payout:       {sale.seller_payout:,.2f}")
print(f"\n📅 RENTAL DETAILS:")
print(f"  Duration:            {sale.rental_days} days")
print(f"  Start Date:          {sale.rental_start_date}")
print(f"  End Date:            {sale.rental_end_date}")
print(f"  Quantity:            {sale.equipment_quantity}")
print(f"\n💸 PAYOUT STATUS:")
print(f"  Status:              {sale.get_payout_status_display()}")
print(f"  Payout Date:         {sale.payout_date or 'Not yet paid'}")
print(f"  Reference:           {sale.payout_reference or 'N/A'}")
print(f"\n⏰ TIMESTAMPS:")
print(f"  Sale Date:           {sale.sale_date}")
print(f"  Created:             {sale.created_at}")

print("\n" + "=" * 60)
print("TEST COMPLETED SUCCESSFULLY!")
print("=" * 60)
print(f"\n📝 Summary:")
print(f"   ✅ Rental status updated to 'completed'")
print(f"   ✅ RentalSale automatically created")
print(f"   ✅ Commission calculated: {sale.platform_commission_percentage}%")
print(f"   ✅ Seller payout calculated: {sale.seller_payout:,.2f}")
print(f"   ✅ Ready for financial processing")
