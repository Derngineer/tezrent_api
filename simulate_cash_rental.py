import os
import django
from datetime import timedelta
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from django.contrib.auth import get_user_model
from accounts.models import CustomerProfile, CompanyProfile
from equipment.models import Equipment, Category
from rentals.models import Rental, RentalPayment

User = get_user_model()

def run_simulation():
    print("🚀 Starting Cash Rental Simulation...")

    # 1. Get or Create a Customer
    customer_email = "test_customer@example.com"
    customer_user, created = User.objects.get_or_create(
        email=customer_email,
        defaults={
            'username': 'test_customer',
            'user_type': 'customer',
            'country': 'UAE'
        }
    )
    if created:
        customer_user.set_password('password123')
        customer_user.save()
        CustomerProfile.objects.create(user=customer_user, city='DXB')
        print(f"✅ Created new customer: {customer_email}")
    else:
        print(f"ℹ️ Using existing customer: {customer_email}")
    
    customer_profile = customer_user.customer_profile

    # 2. Get or Create a Seller Company
    seller_email = "seller_company@example.com"
    seller_user, created = User.objects.get_or_create(
        email=seller_email,
        defaults={
            'username': 'seller_company',
            'user_type': 'company',
            'country': 'UAE'
        }
    )
    if created:
        seller_user.set_password('password123')
        seller_user.save()
        CompanyProfile.objects.create(
            user=seller_user, 
            company_name="Best Rentals LLC",
            city='DXB',
            company_phone="+971500000000",
            company_address="Dubai Industrial City"
        )
        print(f"✅ Created new seller: {seller_email}")
    else:
        print(f"ℹ️ Using existing seller: {seller_email}")
    
    seller_profile = seller_user.company_profile

    # 3. Get or Create Equipment
    category, _ = Category.objects.get_or_create(name="Excavators")
    equipment, created = Equipment.objects.get_or_create(
        name="CAT 320 Excavator",
        seller_company=seller_profile,
        defaults={
            'description': 'Heavy duty excavator',
            'category': category,
            'manufacturer': 'Caterpillar',
            'model_number': '320',
            'year': 2022,
            'weight': 22000,
            'dimensions': '10x3x3m',
            'daily_rate': 1500.00,
            'weekly_rate': 9000.00,
            'monthly_rate': 35000.00,
            'country': 'UAE',
            'city': 'DXB',
            'status': 'available',
            'total_units': 5,
            'available_units': 5
        }
    )
    if created:
        print(f"✅ Created new equipment: {equipment.name}")
    else:
        print(f"ℹ️ Using existing equipment: {equipment.name}")

    # 4. Create a Rental Request
    start_date = timezone.now().date() + timedelta(days=1)
    end_date = start_date + timedelta(days=3) # 3 days rental
    
    print(f"\n📝 Creating Rental Request for {equipment.name}...")
    print(f"   Duration: {start_date} to {end_date} (3 days)")
    print(f"   Daily Rate: {equipment.daily_rate}")

    rental = Rental.objects.create(
        customer=customer_profile,
        equipment=equipment,
        seller=seller_profile,
        start_date=start_date,
        end_date=end_date,
        quantity=1,
        daily_rate=equipment.daily_rate,
        delivery_address="Project Site A, Dubai",
        delivery_city="DXB",
        delivery_country="UAE",
        customer_phone="+971555555555",
        customer_email=customer_email,
        status='pending' # Initial status
    )
    
    print(f"✅ Rental Created! Reference: {rental.rental_reference}")
    print(f"   Total Amount: {rental.total_amount}")
    print(f"   Status: {rental.status}")

    # 5. Simulate Seller Approval
    print("\n🔄 Simulating Seller Approval...")
    rental.status = 'approved'
    rental.approved_at = timezone.now()
    rental.save()
    print(f"✅ Rental Approved. Status: {rental.status}")

    # 6. Create Cash Payment
    print("\n💰 Processing Cash Payment...")
    payment = RentalPayment.objects.create(
        rental=rental,
        payment_type='rental_fee',
        amount=rental.total_amount,
        payment_method='cash',
        payment_status='completed', # Assuming cash was handed over
        notes="Cash received by driver upon delivery"
    )
    print(f"✅ Payment Recorded: {payment.amount} via {payment.get_payment_method_display()}")

    # 7. Update Rental Status to Confirmed
    print("\n🔄 Updating Rental Status to Confirmed...")
    rental.status = 'confirmed'
    rental.save()
    print(f"✅ Rental Confirmed! Status: {rental.status}")

    # 8. Verify Final State
    print("\n📊 Final Rental Summary:")
    print(f"   ID: {rental.id}")
    print(f"   Ref: {rental.rental_reference}")
    print(f"   Customer: {rental.customer.user.email}")
    print(f"   Equipment: {rental.equipment.name}")
    print(f"   Total Paid: {rental.total_amount}")
    print(f"   Payment Method: {payment.payment_method}")
    print(f"   Current Status: {rental.status}")

if __name__ == "__main__":
    run_simulation()
