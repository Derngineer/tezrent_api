"""
Create 2 Sample Rental Requests with Documents
Creates realistic rental orders for testing the seller dashboard and document system

Usage:
    python create_sample_rentals.py --clear  (to delete existing rentals first)
    python create_sample_rentals.py          (to add 2 new rentals)

Features:
- Creates 2 customer profiles
- Creates 2 rental requests in 'pending' status
- Auto-attaches operating manual if equipment has one
- Creates rental agreement document
- Demonstrates document workflow
"""

import os
import sys
import django
from datetime import date, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User, CustomerProfile, CompanyProfile
from equipment.models import Equipment
from rentals.models import Rental, RentalDocument, RentalPayment
from django.core.files.base import ContentFile

def clear_existing_rentals():
    """Clear existing test rentals"""
    print("\n🗑️  Clearing Existing Test Rentals...")
    deleted_count = Rental.objects.all().count()
    Rental.objects.all().delete()
    print(f"   ✅ Deleted {deleted_count} existing rental(s)")


def create_sample_agreement_document(rental):
    """Create a sample rental agreement document"""
    agreement_content = f"""
RENTAL AGREEMENT
----------------
Rental Reference: {rental.rental_reference}
Equipment: {rental.equipment.name}
Daily Rate: ${rental.daily_rate}
Rental Period: {rental.start_date} to {rental.end_date}

Terms and Conditions:
1. Equipment must be returned in good condition
2. Customer is responsible for any damages
3. Late returns will incur additional fees
4. Payment must be completed before delivery

Signed: {rental.created_at}
    """.strip()
    
    doc = RentalDocument.objects.create(
        rental=rental,
        document_type='rental_agreement',
        title=f'Rental Agreement - {rental.rental_reference}',
        uploaded_by=rental.seller.user,
        visible_to_customer=True,
        requires_payment=False  # Must be visible for customer to agree
    )
    
    # Save text file as PDF placeholder
    doc.file.save(
        f'rental_agreement_{rental.rental_reference}.txt',
        ContentFile(agreement_content.encode('utf-8')),
        save=True
    )
    
    return doc


def attach_operating_manual(rental):
    """Attach equipment operating manual to rental (if exists)"""
    if rental.equipment.operating_manual:
        doc = RentalDocument.objects.create(
            rental=rental,
            document_type='operating_manual',
            title=f'Operating Manual - {rental.equipment.name}',
            file=rental.equipment.operating_manual,  # Reference the same file
            uploaded_by=rental.seller.user,
            visible_to_customer=True,
            requires_payment=True  # Only visible after payment
        )
        return doc
    return None


def create_sample_rentals():
    """Create 2 sample rental requests"""
    
    # Check for --clear flag
    if '--clear' in sys.argv:
        clear_existing_rentals()
    
    print("\n🏗️  Creating Sample Rental Requests...")
    print("=" * 70)
    
    # Get seller company
    print("\n1️⃣  Finding Seller Company...")
    seller = CompanyProfile.objects.first()
    if not seller:
        print("   ❌ No company profile found. Please create one first.")
        return
    print(f"   ✅ Using seller: {seller.company_name}")
    
    # Get equipment
    print("\n2️⃣  Finding Equipment...")
    equipment_list = Equipment.objects.filter(seller_company=seller)[:2]
    if equipment_list.count() < 2:
        print(f"   ⚠️  Only {equipment_list.count()} equipment found. Need at least 2.")
        equipment_list = Equipment.objects.all()[:2]
    
    if equipment_list.count() == 0:
        print("   ❌ No equipment found. Please create equipment first.")
        return
    
    print(f"   ✅ Found {equipment_list.count()} equipment items")
    
    # Create or get customer profiles
    print("\n3️⃣  Creating/Finding Customer Profiles...")
    customers = []
    
    # Customer 1
    customer1_user = User.objects.filter(user_type='customer').first()
    if not customer1_user:
        customer1_user = User.objects.create_user(
            username='customer1',
            email='customer1@example.com',
            password='TestPassword123!',
            user_type='customer',
            first_name='John',
            last_name='Smith',
            phone_number='+1234567890',
            country='UAE',
        )
        print(f"   ✅ Created customer user: {customer1_user.email}")
    
    customer1, created = CustomerProfile.objects.get_or_create(
        user=customer1_user,
        defaults={
            'date_of_birth': date(1990, 5, 15),
            'address': '123 Main Street, Apartment 4B',
            'city': 'DXB'
        }
    )
    customers.append(customer1)
    print(f"   ✅ Customer 1: {customer1_user.get_full_name()}")
    
    # Customer 2
    customer2_user = User.objects.filter(user_type='customer').exclude(id=customer1_user.id).first()
    if not customer2_user:
        customer2_user = User.objects.create_user(
            username='customer2',
            email='customer2@example.com',
            password='TestPassword123!',
            user_type='customer',
            first_name='Sarah',
            last_name='Johnson',
            phone_number='+1234567892',
            country='UAE',
        )
        print(f"   ✅ Created customer user: {customer2_user.email}")
    
    customer2, created = CustomerProfile.objects.get_or_create(
        user=customer2_user,
        defaults={
            'date_of_birth': date(1988, 8, 22),
            'address': '456 Oak Avenue, Suite 12',
            'city': 'AUH'
        }
    )
    customers.append(customer2)
    print(f"   ✅ Customer 2: {customer2_user.get_full_name()}")
    
    # Create rentals
    print("\n4️⃣  Creating Rental Requests...")
    
    rental_data = [
        {
            'customer': customers[0],
            'equipment': equipment_list[0],
            'start_date': date.today() + timedelta(days=3),
            'end_date': date.today() + timedelta(days=10),
            'quantity': 1,
            'delivery_address': '123 Main Street, Apartment 4B, New York, NY 10001',
            'delivery_city': 'NYC',
            'delivery_country': 'USA',
            'customer_phone': '+1234567890',
            'customer_email': 'customer1@example.com',
            'customer_notes': 'Need equipment for construction project. Please deliver between 8AM-12PM.',
            'pickup_required': True,
            'delivery_fee': 150.00,
            'insurance_fee': 75.00,
            'security_deposit': 1000.00,
            'status': 'pending'
        },
        {
            'customer': customers[1],
            'equipment': equipment_list[1] if equipment_list.count() > 1 else equipment_list[0],
            'start_date': date.today() + timedelta(days=1),
            'end_date': date.today() + timedelta(days=5),
            'quantity': 2,
            'delivery_address': '456 Oak Avenue, Suite 12, Brooklyn, NY 11201',
            'delivery_city': 'NYC',
            'delivery_country': 'USA',
            'customer_phone': '+1234567892',
            'customer_email': 'customer2@example.com',
            'customer_notes': 'Urgent rental needed for landscaping project. Will pick up if delivery not available.',
            'delivery_instructions': 'Call 30 minutes before delivery. Use service entrance.',
            'pickup_required': False,
            'delivery_fee': 0.00,
            'insurance_fee': 50.00,
            'security_deposit': 800.00,
            'status': 'pending'
        }
    ]
    
    created_rentals = []
    
    for idx, data in enumerate(rental_data, 1):
        print(f"\n   📦 Creating Rental {idx}/2...")
        
        # Check if similar rental exists
        existing = Rental.objects.filter(
            customer=data['customer'],
            equipment=data['equipment'],
            start_date=data['start_date']
        ).first()
        
        if existing:
            print(f"      ⚠️  Similar rental exists: {existing.rental_reference}")
            created_rentals.append(existing)
            continue
        
        # Calculate pricing
        equipment = data['equipment']
        start_date = data['start_date']
        end_date = data['end_date']
        quantity = data['quantity']
        
        total_days = (end_date - start_date).days + 1
        daily_rate = float(equipment.daily_rate)
        subtotal = daily_rate * total_days * quantity
        total_amount = subtotal + data['delivery_fee'] + data['insurance_fee']
        
        # Create rental
        rental = Rental.objects.create(
            customer=data['customer'],
            equipment=equipment,
            seller=seller,
            start_date=start_date,
            end_date=end_date,
            quantity=quantity,
            daily_rate=daily_rate,
            total_days=total_days,
            subtotal=subtotal,
            delivery_fee=data['delivery_fee'],
            insurance_fee=data['insurance_fee'],
            security_deposit=data['security_deposit'],
            total_amount=total_amount,
            status=data['status'],
            delivery_address=data['delivery_address'],
            delivery_city=data['delivery_city'],
            delivery_country=data['delivery_country'],
            delivery_instructions=data.get('delivery_instructions', ''),
            pickup_required=data['pickup_required'],
            customer_phone=data['customer_phone'],
            customer_email=data['customer_email'],
            customer_notes=data['customer_notes']
        )
        
        created_rentals.append(rental)
        
        print(f"      ✅ Created: {rental.rental_reference}")
        print(f"         Equipment: {rental.equipment.name}")
        print(f"         Customer: {rental.customer.user.get_full_name()}")
        print(f"         Period: {rental.start_date} to {rental.end_date} ({total_days} days)")
        print(f"         Quantity: {quantity} unit(s)")
        print(f"         Daily Rate: ${daily_rate}")
        print(f"         Subtotal: ${subtotal}")
        print(f"         Delivery Fee: ${data['delivery_fee']}")
        print(f"         Insurance: ${data['insurance_fee']}")
        print(f"         Total: ${total_amount}")
        print(f"         Status: {rental.get_status_display()}")
        
        # Create rental agreement document
        print(f"      📄 Creating rental agreement...")
        agreement = create_sample_agreement_document(rental)
        print(f"         ✅ Agreement created: {agreement.title}")
        
        # Attach operating manual if equipment has one
        print(f"      📖 Checking for operating manual...")
        manual = attach_operating_manual(rental)
        if manual:
            print(f"         ✅ Operating manual attached (locked until payment)")
        else:
            print(f"         ⚠️  No operating manual on this equipment")
    
    # Summary
    print("\n" + "=" * 70)
    print("✨ SUMMARY")
    print("=" * 70)
    print(f"✅ Created {len(created_rentals)} rental request(s)")
    print(f"📊 Total rentals in database: {Rental.objects.count()}")
    print(f"👥 Customers: {CustomerProfile.objects.count()}")
    print(f"🏢 Seller: {seller.company_name}")
    
    print("\n📋 Rental Details:")
    for rental in created_rentals:
        print(f"\n   • {rental.rental_reference}")
        print(f"     Equipment: {rental.equipment.name}")
        print(f"     Customer: {rental.customer.user.get_full_name()}")
        print(f"     Total: ${rental.total_amount} ({rental.total_days} days)")
        print(f"     Status: {rental.get_status_display()}")
        
        # Show documents
        docs = rental.documents.all()
        print(f"     Documents: {docs.count()}")
        for doc in docs:
            lock_icon = "🔒" if doc.requires_payment else "🔓"
            print(f"       {lock_icon} {doc.get_document_type_display()}: {doc.title}")
    
    print("\n🎯 Test Endpoints:")
    print(f"   GET /api/rentals/rentals/")
    print(f"   GET /api/rentals/rentals/?status=pending")
    if created_rentals:
        print(f"   GET /api/rentals/rentals/{created_rentals[0].id}/")
        print(f"   GET /api/rentals/rentals/{created_rentals[0].id}/documents/")
    
    print("\n📝 Document Workflow:")
    print(f"   1. Rental Agreement: ✅ Visible to customer (must agree)")
    print(f"   2. Operating Manual: 🔒 Locked until payment confirmed")
    print(f"   3. After payment: Manual becomes visible to customer")
    
    print("\n🎉 Done! Check your seller dashboard to manage these rental requests.")
    print("=" * 70)

if __name__ == '__main__':
    try:
        create_sample_rentals()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
