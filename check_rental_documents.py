"""
Check Rental Documents
Shows all rentals and their associated documents
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from rentals.models import Rental, RentalDocument

print("\n" + "=" * 70)
print("📋 RENTAL DOCUMENTS REPORT")
print("=" * 70)

rentals = Rental.objects.all().order_by('-created_at')

if rentals.count() == 0:
    print("\n❌ No rentals found. Run create_sample_rentals.py first.")
else:
    print(f"\n✅ Found {rentals.count()} rental(s)\n")
    
    for rental in rentals:
        print(f"{'=' * 70}")
        print(f"📦 Rental: {rental.rental_reference}")
        print(f"   Equipment: {rental.equipment.name}")
        print(f"   Customer: {rental.customer.user.get_full_name()}")
        print(f"   Status: {rental.get_status_display()}")
        print(f"   Total: ${rental.total_amount} ({rental.total_days} days)")
        print(f"   Period: {rental.start_date} to {rental.end_date}")
        
        # Check for documents
        documents = rental.documents.all()
        print(f"\n   📄 Documents: {documents.count()}")
        
        if documents.count() == 0:
            print(f"      ⚠️  No documents attached")
        else:
            for doc in documents:
                lock_icon = "🔒" if doc.requires_payment else "🔓"
                visible_icon = "👁️" if doc.visible_to_customer else "🚫"
                signed_icon = "✓" if doc.is_signed else "✗"
                
                print(f"\n      {lock_icon} {visible_icon} {doc.get_document_type_display()}")
                print(f"         Title: {doc.title}")
                print(f"         File: {doc.file.name if doc.file else 'No file'}")
                print(f"         Uploaded by: {doc.uploaded_by.get_full_name()}")
                print(f"         Requires payment: {'Yes' if doc.requires_payment else 'No'}")
                print(f"         Visible to customer: {'Yes' if doc.visible_to_customer else 'No'}")
                print(f"         Signed: {signed_icon}")
                print(f"         Created: {doc.created_at.strftime('%Y-%m-%d %H:%M')}")
        
        # Check if equipment has operating manual
        print(f"\n   📖 Equipment Operating Manual:")
        if rental.equipment.operating_manual:
            print(f"      ✅ Available: {rental.equipment.operating_manual.name}")
            print(f"      Description: {rental.equipment.manual_description or 'No description'}")
        else:
            print(f"      ❌ No operating manual uploaded for this equipment")
        
        print()

print("=" * 70)
print("\n✨ Document Summary:")
print(f"   Total Documents: {RentalDocument.objects.count()}")
print(f"   Rental Agreements: {RentalDocument.objects.filter(document_type='rental_agreement').count()}")
print(f"   Operating Manuals: {RentalDocument.objects.filter(document_type='operating_manual').count()}")
print(f"   Payment Required: {RentalDocument.objects.filter(requires_payment=True).count()}")
print(f"   Publicly Visible: {RentalDocument.objects.filter(requires_payment=False, visible_to_customer=True).count()}")

print("\n💡 To test document visibility:")
print("   1. Customer can see rental agreements immediately (requires_payment=False)")
print("   2. Operating manuals are locked (requires_payment=True)")
print("   3. After payment, operating manual becomes visible")

print("\n=" * 70)
