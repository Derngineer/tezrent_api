"""
Create revenue data across multiple dates for trend chart testing.
This populates RentalSale records with varying dates to show trends.
"""
import os
import django
from decimal import Decimal
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tezrent_api.settings')
django.setup()

from django.utils import timezone
from rentals.models import Rental, RentalSale
from accounts.models import CustomerProfile, CompanyProfile
from equipment.models import Equipment

def create_trending_sales():
    """Create sales across last 30 days with varying amounts"""
    
    print("📈 Creating Revenue Trend Data")
    print("=" * 70)
    
    # Get or create test users
    try:
        customer = CustomerProfile.objects.first()
        seller = CompanyProfile.objects.first()
        equipment = Equipment.objects.first()
        
        if not all([customer, seller, equipment]):
            print("❌ Missing required data. Run other scripts first:")
            print("   python create_categories.py")
            print("   python create_4_listings.py")
            return
        
        print(f"✓ Using customer: {customer.user.email}")
        print(f"✓ Using seller: {seller.company_name}")
        print(f"✓ Using equipment: {equipment.name}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Create sales for last 30 days with varying patterns
    today = timezone.now()
    sales_data = [
        # Week 4 (most recent) - High sales
        {'days_ago': 1, 'amount': 3200, 'days': 5},
        {'days_ago': 2, 'amount': 1800, 'days': 3},
        {'days_ago': 3, 'amount': 4500, 'days': 10},
        {'days_ago': 5, 'amount': 2100, 'days': 4},
        {'days_ago': 6, 'amount': 1500, 'days': 2},
        
        # Week 3 - Medium sales
        {'days_ago': 8, 'amount': 2800, 'days': 6},
        {'days_ago': 10, 'amount': 1900, 'days': 4},
        {'days_ago': 12, 'amount': 3400, 'days': 8},
        {'days_ago': 13, 'amount': 1200, 'days': 2},
        
        # Week 2 - Lower sales
        {'days_ago': 15, 'amount': 2200, 'days': 5},
        {'days_ago': 17, 'amount': 1600, 'days': 3},
        {'days_ago': 19, 'amount': 2900, 'days': 7},
        
        # Week 1 (oldest) - Starting low
        {'days_ago': 22, 'amount': 1400, 'days': 3},
        {'days_ago': 24, 'amount': 1800, 'days': 4},
        {'days_ago': 27, 'amount': 2500, 'days': 6},
        {'days_ago': 29, 'amount': 1100, 'days': 2},
    ]
    
    created_count = 0
    
    for data in sales_data:
        sale_date = today - timedelta(days=data['days_ago'])
        rental_start = sale_date - timedelta(days=data['days'] + 2)
        rental_end = sale_date - timedelta(days=2)
        
        # Create rental first
        rental = Rental.objects.create(
            customer=customer,
            equipment=equipment,
            seller=seller,
            start_date=rental_start.date(),
            end_date=rental_end.date(),
            quantity=1,
            daily_rate=Decimal(str(data['amount'] / data['days'])),
            subtotal=Decimal(str(data['amount'])),
            delivery_fee=Decimal('150.00'),
            insurance_fee=Decimal('0.00'),
            late_fees=Decimal('0.00'),
            damage_fees=Decimal('0.00'),
            total_amount=Decimal(str(data['amount'])),
            status='completed',
            delivery_address="Test Address",
            delivery_city="Dubai",
            delivery_country="UAE"
        )
        
        # Calculate commission (10%)
        total_revenue = Decimal(str(data['amount']))
        commission = total_revenue * Decimal('0.10')
        payout = total_revenue - commission
        
        # Create sale record
        sale = RentalSale.objects.create(
            rental=rental,
            total_revenue=total_revenue,
            subtotal=rental.subtotal,
            delivery_fee=rental.delivery_fee,
            insurance_fee=rental.insurance_fee,
            late_fees=rental.late_fees,
            damage_fees=rental.damage_fees,
            platform_commission_percentage=Decimal('10.00'),
            platform_commission_amount=commission,
            seller_payout=payout,
            seller=seller,
            customer=customer,
            equipment=equipment,
            rental_days=data['days'],
            rental_start_date=rental.start_date,
            rental_end_date=rental.end_date,
            equipment_quantity=1,
            payout_status='pending'
        )
        
        # Backdate the sale_date
        RentalSale.objects.filter(id=sale.id).update(
            sale_date=sale_date,
            created_at=sale_date
        )
        
        created_count += 1
        date_str = sale_date.strftime('%b %d')
        print(f"✓ {date_str}: AED {data['amount']:>5} ({data['days']}d rental) → Payout: AED {float(payout):>6,.2f}")
    
    print("\n" + "=" * 70)
    print(f"✅ Created {created_count} sales records across 30 days")
    print(f"✅ Total revenue trend data ready for line chart")
    
    # Show summary
    from django.db.models import Sum, Count
    summary = RentalSale.objects.aggregate(
        total_sales=Count('id'),
        total_revenue=Sum('total_revenue'),
        total_payout=Sum('seller_payout')
    )
    
    print(f"\n📊 Total Database Stats:")
    print(f"   Sales: {summary['total_sales']}")
    print(f"   Revenue: AED {float(summary['total_revenue']):,.2f}")
    print(f"   Seller Payout: AED {float(summary['total_payout']):,.2f}")
    
    print("\n🌐 Test the API:")
    print("   GET /api/rentals/rentals/revenue_trends/")
    print("   GET /api/rentals/rentals/revenue_trends/?period=daily&days=30")
    print("   GET /api/rentals/rentals/revenue_trends/?period=weekly&days=84")
    print("   GET /api/rentals/rentals/revenue_trends/?period=monthly&days=365")

if __name__ == '__main__':
    create_trending_sales()
