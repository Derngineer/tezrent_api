#!/usr/bin/env python
"""
Create sample rentals in different statuses: pending, approved, confirmed, active, completed
All amounts in AED (not USD)
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from datetime import timedelta, datetime
from decimal import Decimal
from equipment.models import Equipment
from rentals.models import Rental, RentalStatusUpdate, RentalDocument, RentalPayment
from accounts.models import CustomerProfile, CompanyProfile, User

print("\n" + "="*70)
print("🏗️  CREATING SAMPLE RENTALS (ALL STATUSES) - AED CURRENCY")
print("="*70)

# Get equipment and profiles
equipment_list = list(Equipment.objects.filter(status='available')[:5])
if len(equipment_list) < 3:
    print("❌ Not enough equipment. Need at least 3 equipment items.")
    exit(1)

customers = list(CustomerProfile.objects.all()[:3])
if len(customers) < 2:
    print("❌ Need at least 2 customers. Creating missing customers...")
    # Create additional customer
    user = User.objects.create_user(
        email='rental.test@example.com',
        username='rental.test',
        password='testpass123',
        first_name='Rental',
        last_name='Tester'
    )
    CustomerProfile.objects.create(user=user)
    customers = list(CustomerProfile.objects.all()[:3])

print(f"✅ Found {len(equipment_list)} equipment items")
print(f"✅ Found {len(customers)} customers\n")

# Helper function to create rental
def create_rental_with_status(
    equipment, customer, status, days_offset_start, days_offset_end,
    quantity=1, description=""
):
    """Create rental with specific status and dates"""
    start_date = timezone.now().date() + timedelta(days=days_offset_start)
    end_date = timezone.now().date() + timedelta(days=days_offset_end)
    total_days = (end_date - start_date).days + 1
    
    daily_rate = equipment.daily_rate
    subtotal = daily_rate * total_days * quantity
    delivery_fee = Decimal('150.00') if True else Decimal('0')  # AED 150 delivery
    insurance_fee = daily_rate * Decimal('0.10') * total_days
    
    rental = Rental.objects.create(
        customer=customer,
        equipment=equipment,
        seller=equipment.seller_company,
        start_date=start_date,
        end_date=end_date,
        quantity=quantity,
        daily_rate=daily_rate,
        total_days=total_days,
        subtotal=subtotal,
        delivery_fee=delivery_fee,
        insurance_fee=insurance_fee,
        security_deposit=daily_rate * 2,
        total_amount=subtotal + delivery_fee + insurance_fee,
        status=status,
        customer_phone='+971 50 123 4567',
        customer_email=customer.user.email,
        delivery_address='Business Bay, Dubai',
        delivery_city='DXB',
        delivery_country='UAE',
        pickup_required=True,
        customer_notes=description
    )
    
    # Set approved_at for approved statuses
    if status in ['approved', 'confirmed', 'preparing', 'ready_for_pickup', 
                  'out_for_delivery', 'delivered', 'in_progress', 'completed']:
        rental.approved_at = timezone.now() - timedelta(hours=2)
        rental.save()
    
    # Create status update
    RentalStatusUpdate.objects.create(
        rental=rental,
        new_status=status,
        updated_by=customer.user,
        notes=f'Sample rental created in {status} status',
        is_visible_to_customer=True
    )
    
    # Create rental agreement (no file for now, just placeholder)
    # Note: In production, this would have an actual PDF file
    # RentalDocument.objects.create(
    #     rental=rental,
    #     document_type='rental_agreement',
    #     title=f'Rental Agreement - {rental.rental_reference}',
    #     file='rental_documents/sample_agreement.pdf',  # Would be actual file
    #     uploaded_by=equipment.seller_company.user,
    #     visible_to_customer=True,
    #     requires_payment=False
    # )
    
    return rental

# Create sample rentals
rentals_created = []

print("📦 Creating Sample Rentals...")
print("-" * 70)

# 1. PENDING - Awaiting seller approval (quantity >= 5)
print("\n1️⃣  PENDING - Awaiting Seller Approval (Qty=5)")
rental = create_rental_with_status(
    equipment=equipment_list[0],
    customer=customers[0],
    status='pending',
    days_offset_start=3,
    days_offset_end=10,
    quantity=5,  # >= 5 requires approval
    description='Large order needs seller approval before payment'
)
print(f"   ✅ {rental.rental_reference}")
print(f"      Equipment: {rental.equipment.name}")
print(f"      Quantity: {rental.quantity} units")
print(f"      Period: {rental.start_date} to {rental.end_date} ({rental.total_days} days)")
print(f"      Total: AED {rental.total_amount:,.2f}")
print(f"      Status: {rental.get_status_display()}")
rentals_created.append(rental)

# 2. APPROVED - Seller approved, waiting for payment
print("\n2️⃣  APPROVED - Ready for Customer Payment (Qty=2)")
rental = create_rental_with_status(
    equipment=equipment_list[1],
    customer=customers[1],
    status='approved',
    days_offset_start=2,
    days_offset_end=6,
    quantity=2,  # < 5, auto-approved
    description='Auto-approved, customer needs to pay'
)
print(f"   ✅ {rental.rental_reference}")
print(f"      Equipment: {rental.equipment.name}")
print(f"      Quantity: {rental.quantity} units")
print(f"      Period: {rental.start_date} to {rental.end_date} ({rental.total_days} days)")
print(f"      Total: AED {rental.total_amount:,.2f}")
print(f"      Status: {rental.get_status_display()}")
rentals_created.append(rental)

# 3. CONFIRMED - Payment completed, preparing equipment
print("\n3️⃣  CONFIRMED - Payment Received, Preparing Equipment")
rental = create_rental_with_status(
    equipment=equipment_list[2],
    customer=customers[0],
    status='confirmed',
    days_offset_start=1,
    days_offset_end=4,
    quantity=1,
    description='Payment confirmed, seller preparing equipment'
)
# Add payment record
RentalPayment.objects.create(
    rental=rental,
    payment_type='rental_fee',
    amount=rental.total_amount,
    payment_method='card',
    payment_status='completed',
    transaction_id=f'PAY_{rental.rental_reference}',
    completed_at=timezone.now(),
    gateway_response={'currency': 'AED', 'payment_gateway': 'Stripe'}
)
print(f"   ✅ {rental.rental_reference}")
print(f"      Equipment: {rental.equipment.name}")
print(f"      Period: {rental.start_date} to {rental.end_date} ({rental.total_days} days)")
print(f"      Total: AED {rental.total_amount:,.2f}")
print(f"      Payment: ✅ Completed (AED {rental.total_amount:,.2f})")
print(f"      Status: {rental.get_status_display()}")
rentals_created.append(rental)

# 4. IN_PROGRESS - Currently active rental
print("\n4️⃣  IN_PROGRESS - Active Rental (Customer Has Equipment)")
rental = create_rental_with_status(
    equipment=equipment_list[3] if len(equipment_list) > 3 else equipment_list[0],
    customer=customers[1],
    status='in_progress',
    days_offset_start=-2,  # Started 2 days ago
    days_offset_end=5,      # Ends in 5 days
    quantity=1,
    description='Equipment currently with customer'
)
rental.actual_start_date = timezone.now() - timedelta(days=2)
rental.save()
# Add payment
RentalPayment.objects.create(
    rental=rental,
    payment_type='rental_fee',
    amount=rental.total_amount,
    payment_method='card',
    payment_status='completed',
    transaction_id=f'PAY_{rental.rental_reference}',
    completed_at=timezone.now() - timedelta(days=3),
    gateway_response={'currency': 'AED'}
)
print(f"   ✅ {rental.rental_reference}")
print(f"      Equipment: {rental.equipment.name}")
print(f"      Period: {rental.start_date} to {rental.end_date}")
print(f"      Started: {rental.actual_start_date.date()}")
print(f"      Days Remaining: {rental.days_remaining}")
print(f"      Total: AED {rental.total_amount:,.2f}")
print(f"      Status: {rental.get_status_display()}")
rentals_created.append(rental)

# 5. COMPLETED - Successfully finished rental
print("\n5️⃣  COMPLETED - Rental Finished Successfully")
rental = create_rental_with_status(
    equipment=equipment_list[4] if len(equipment_list) > 4 else equipment_list[1],
    customer=customers[0],
    status='completed',
    days_offset_start=-10,  # Started 10 days ago
    days_offset_end=-3,     # Ended 3 days ago
    quantity=1,
    description='Equipment returned, rental completed'
)
rental.actual_start_date = timezone.now() - timedelta(days=10)
rental.actual_end_date = timezone.now() - timedelta(days=3)
rental.save()
# Add payment
RentalPayment.objects.create(
    rental=rental,
    payment_type='rental_fee',
    amount=rental.total_amount,
    payment_method='bank_transfer',
    payment_status='completed',
    transaction_id=f'PAY_{rental.rental_reference}',
    completed_at=timezone.now() - timedelta(days=11),
    gateway_response={'currency': 'AED', 'reference': 'BT12345'}
)
print(f"   ✅ {rental.rental_reference}")
print(f"      Equipment: {rental.equipment.name}")
print(f"      Period: {rental.start_date} to {rental.end_date}")
print(f"      Completed: {rental.actual_end_date.date()}")
print(f"      Duration: {rental.total_days} days")
print(f"      Total: AED {rental.total_amount:,.2f}")
print(f"      Status: {rental.get_status_display()}")
rentals_created.append(rental)

print("\n" + "="*70)
print("✨ SUMMARY")
print("="*70)
print(f"✅ Created {len(rentals_created)} sample rentals")
print(f"📊 Total rentals in database: {Rental.objects.count()}")
print(f"\n💰 All amounts in AED (not USD)")
print(f"\n📋 Status Distribution:")
print(f"   - Pending: {Rental.objects.filter(status='pending').count()}")
print(f"   - Approved: {Rental.objects.filter(status='approved').count()}")
print(f"   - Confirmed: {Rental.objects.filter(status='confirmed').count()}")
print(f"   - In Progress: {Rental.objects.filter(status='in_progress').count()}")
print(f"   - Completed: {Rental.objects.filter(status='completed').count()}")

print(f"\n🔗 API Endpoints to Test:")
print(f"   GET /api/rentals/rentals/")
print(f"   GET /api/rentals/rentals/?status=pending")
print(f"   GET /api/rentals/rentals/?status=approved")
print(f"   GET /api/rentals/rentals/?status=in_progress")
print(f"   GET /api/rentals/rentals/{rentals_created[0].id}/")
print("="*70)
