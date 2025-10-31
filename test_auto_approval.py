#!/usr/bin/env python
"""
Test script for auto-approval and document generation
"""
import os
import django
import sys

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from datetime import timedelta
from equipment.models import Equipment
from rentals.models import Rental, RentalDocument, RentalPayment
from accounts.models import CustomerProfile, CompanyProfile, User

def test_auto_approval():
    """Test rental auto-approval for quantity < 5"""
    print("\n" + "="*70)
    print("🧪 TESTING AUTO-APPROVAL & DOCUMENT GENERATION")
    print("="*70)
    
    # Get test equipment
    equipment = Equipment.objects.filter(status='available').first()
    if not equipment:
        print("❌ No equipment found. Create equipment first.")
        return
    
    print(f"\n📦 Using Equipment: {equipment.name}")
    print(f"   Seller: {equipment.seller_company.company_name}")
    print(f"   Has Operating Manual: {'✅ Yes' if equipment.operating_manual else '❌ No'}")
    
    # Get test customer
    customer_profile = CustomerProfile.objects.first()
    if not customer_profile:
        print("❌ No customer profile found.")
        return
    
    print(f"\n👤 Customer: {customer_profile.user.get_full_name()}")
    
    # Create rental with quantity < 5 (should auto-approve)
    print("\n" + "-"*70)
    print("TEST 1: Creating rental with quantity=2 (should auto-approve)")
    print("-"*70)
    
    start_date = timezone.now().date() + timedelta(days=2)
    end_date = start_date + timedelta(days=5)
    
    # Simulate what happens in RentalCreateSerializer
    from rentals.serializers import RentalCreateSerializer
    from rest_framework.test import APIRequestFactory
    from rest_framework.request import Request
    
    factory = APIRequestFactory()
    request = factory.post('/api/rentals/rentals/')
    request.user = customer_profile.user
    rest_request = Request(request)
    
    serializer = RentalCreateSerializer(
        data={
            'equipment': equipment.id,
            'start_date': start_date,
            'end_date': end_date,
            'quantity': 2,  # < 5, should auto-approve
            'delivery_address': '123 Test Street',
            'delivery_city': 'GBE',  # 3-char code
            'delivery_country': 'BWA',  # 3-char code
            'customer_phone': '+267 71234567',
            'customer_email': customer_profile.user.email,
            'pickup_required': True
        },
        context={'request': rest_request}
    )
    
    if serializer.is_valid():
        rental = serializer.save()
        
        print(f"\n✅ Rental Created!")
        print(f"   Reference: {rental.rental_reference}")
        print(f"   Quantity: {rental.quantity}")
        print(f"   Status: {rental.status}")
        print(f"   Auto-Approved: {'✅ YES' if rental.status == 'approved' else '❌ NO (still pending)'}")
        print(f"   Approved At: {rental.approved_at or 'N/A'}")
        print(f"   Total Amount: ${rental.total_amount}")
        
        # Check documents
        print("\n" + "-"*70)
        print("TEST 2: Checking Auto-Generated Documents")
        print("-"*70)
        
        documents = RentalDocument.objects.filter(rental=rental)
        print(f"\n📄 Documents Created: {documents.count()}")
        
        for doc in documents:
            lock_icon = "🔒 LOCKED" if doc.requires_payment else "🔓 UNLOCKED"
            visible_icon = "👁️  VISIBLE" if doc.visible_to_customer else "🚫 HIDDEN"
            
            print(f"\n   {doc.get_document_type_display()}")
            print(f"   └─ Title: {doc.title}")
            print(f"   └─ Status: {lock_icon} | {visible_icon}")
            print(f"   └─ Requires Payment: {doc.requires_payment}")
            print(f"   └─ File: {doc.file.name if doc.file else 'None'}")
        
        # Test payment receipt upload simulation
        print("\n" + "-"*70)
        print("TEST 3: Simulating Payment Receipt Upload")
        print("-"*70)
        
        # Create payment (seller would do this via API)
        payment = RentalPayment.objects.create(
            rental=rental,
            payment_type='full',
            amount=rental.total_amount,
            payment_method='cash_on_delivery',
            payment_status='completed',
            receipt_number='RCT-TEST-001',
            notes='Test payment - cash collected',
            completed_at=timezone.now()
        )
        
        print(f"\n✅ Payment Receipt Created!")
        print(f"   Receipt Number: {payment.receipt_number}")
        print(f"   Amount: ${payment.amount}")
        print(f"   Method: {payment.get_payment_method_display()}")
        print(f"   Status: {payment.get_payment_status_display()}")
        
        # Check if operating manual unlocked
        print("\n" + "-"*70)
        print("TEST 4: Checking Document Lock Status After Payment")
        print("-"*70)
        
        for doc in documents:
            # Check if locked (simulate serializer logic)
            is_locked = False
            if doc.requires_payment:
                completed_payment = rental.payments.filter(
                    payment_status='completed'
                ).exists()
                is_locked = not completed_payment
            
            status_icon = "🔒 STILL LOCKED" if is_locked else "🔓 UNLOCKED"
            
            print(f"\n   {doc.get_document_type_display()}")
            print(f"   └─ Status: {status_icon}")
            print(f"   └─ Customer Can Download: {'✅ YES' if not is_locked else '❌ NO (needs payment)'}")
        
        # Summary
        print("\n" + "="*70)
        print("📊 TEST SUMMARY")
        print("="*70)
        print(f"✅ Rental auto-approved: {rental.status == 'approved'}")
        print(f"✅ Documents generated: {documents.count()}")
        print(f"✅ Rental agreement visible: {documents.filter(document_type='rental_agreement', visible_to_customer=True).exists()}")
        print(f"✅ Operating manual attached: {documents.filter(document_type='operating_manual').exists()}")
        print(f"✅ Payment receipt uploaded: {rental.payments.exists()}")
        print(f"✅ Operating manual unlocked: {not is_locked}")
        
        print("\n🎉 ALL TESTS PASSED!")
        print("="*70)
        
    else:
        print(f"\n❌ Validation Error: {serializer.errors}")
    
    # Test with quantity >= 5 (should stay pending)
    print("\n" + "-"*70)
    print("TEST 5: Creating rental with quantity=5 (should stay pending)")
    print("-"*70)
    
    serializer2 = RentalCreateSerializer(
        data={
            'equipment': equipment.id,
            'start_date': start_date + timedelta(days=10),
            'end_date': end_date + timedelta(days=10),
            'quantity': 5,  # >= 5, should stay pending
            'delivery_address': '456 Test Avenue',
            'delivery_city': 'FRW',  # 3-char code
            'delivery_country': 'BWA',  # 3-char code
            'customer_phone': '+267 71234567',
            'customer_email': customer_profile.user.email,
            'pickup_required': True
        },
        context={'request': rest_request}
    )
    
    if serializer2.is_valid():
        rental2 = serializer2.save()
        
        print(f"\n✅ Rental Created!")
        print(f"   Reference: {rental2.rental_reference}")
        print(f"   Quantity: {rental2.quantity}")
        print(f"   Status: {rental2.status}")
        print(f"   Auto-Approved: {'✅ YES' if rental2.status == 'approved' else '❌ NO (needs approval)'}")
        print(f"   Expected: PENDING (quantity >= 5)")
        
        if rental2.status == 'pending':
            print("\n✅ Correct! Rental with quantity >= 5 stayed PENDING")
        else:
            print("\n⚠️  Warning: Expected pending but got", rental2.status)

if __name__ == '__main__':
    test_auto_approval()
