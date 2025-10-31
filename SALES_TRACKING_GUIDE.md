# Sales Tracking & Financial Processing Guide

## Overview

This guide explains **when rentals become sales** and how the system tracks revenue, commissions, and payouts for financial processing.

## 📊 The Key Question: When is a Rental Recorded as a Sale?

### Answer: When Status Changes to **'completed'**

A rental becomes a sale **automatically** when its status is updated to `completed`. This triggers the system to:

1. ✅ Create a `RentalSale` record
2. 💰 Calculate platform commission (default 10%)
3. 💵 Calculate seller payout
4. 📈 Make it available for financial analytics

### Rental Status Flow to Sale

```
pending → approved → payment_pending → confirmed → 
preparing → ready_for_pickup → out_for_delivery → delivered → 
in_progress → return_requested → returning → ✅ COMPLETED (SALE!)
```

**Only the 'completed' status triggers sale creation.**

---

## 🏗️ RentalSale Model Structure

### Database Fields

**Financial Details (copied from Rental at completion):**
- `total_revenue` - Total amount paid by customer
- `subtotal` - Base rental cost
- `delivery_fee` - Delivery charges
- `insurance_fee` - Insurance charges
- `late_fees` - Late return penalties
- `damage_fees` - Damage charges

**Platform Commission:**
- `platform_commission_percentage` - Commission rate (default 10%)
- `platform_commission_amount` - Calculated commission (auto)
- `seller_payout` - Amount seller receives (auto)

**References:**
- `rental` - OneToOne link to original Rental
- `seller` - Seller CompanyProfile
- `customer` - Customer Profile
- `equipment` - Equipment rented

**Rental Analytics:**
- `rental_days` - Total rental duration
- `rental_start_date` - Start date
- `rental_end_date` - End date
- `equipment_quantity` - Number of units

**Payout Tracking:**
- `payout_status` - pending, processing, completed, failed, on_hold
- `payout_date` - When seller was paid
- `payout_reference` - Payment reference number
- `payout_notes` - Admin notes

**Timestamps:**
- `sale_date` - When rental completed (auto)
- `created_at` - Record creation time
- `updated_at` - Last modified

---

## 🔄 Automatic Sale Creation (Signal)

### How It Works

The system uses a **Django signal** to automatically create sales:

```python
@receiver(post_save, sender=Rental)
def create_sale_on_completion(sender, instance, created, **kwargs):
    """
    Automatically create RentalSale when status becomes 'completed'
    """
    if instance.status == 'completed' and not hasattr(instance, 'sale'):
        RentalSale.objects.create(
            rental=instance,
            total_revenue=instance.total_amount,
            platform_commission_percentage=10.00,  # 10%
            seller=instance.equipment.owner,
            customer=instance.customer,
            # ... other fields
        )
```

### What Triggers It

1. **Status Update to 'completed':**
   - POST `/api/rentals/rentals/{id}/update_status/`
   - Body: `{"new_status": "completed"}`

2. **Automatic Actions:**
   - ✅ Creates RentalSale record
   - 💰 Calculates 10% commission
   - 📊 Available for analytics immediately
   - 🔔 Logs: "Sale created for rental {reference}"

3. **Prevents Duplicates:**
   - Only creates sale if one doesn't exist
   - Uses OneToOne relationship

---

## 💼 Commission Calculation

### Default: 10% Platform Fee

```
Total Revenue: AED 1,000
Platform Commission (10%): AED 100
Seller Payout: AED 900
```

### Breakdown:

```
total_revenue = subtotal + delivery_fee + insurance_fee + late_fees + damage_fees
platform_commission_amount = total_revenue × (platform_commission_percentage / 100)
seller_payout = total_revenue - platform_commission_amount
```

### Future: Custom Commission Rates

The system supports **per-seller commission rates**:
- Premium sellers: 5%
- Standard sellers: 10%
- New sellers: 15%

(Currently all use 10% default)

---

## 📈 Financial Analytics Endpoints

### 1. List All Sales

```http
GET /api/rentals/sales/
```

**Response:**
```json
{
  "count": 150,
  "results": [
    {
      "id": 1,
      "rental_reference": "RENT-2025-001",
      "seller_name": "Equipment Masters LLC",
      "customer_name": "John Doe",
      "equipment_name": "Hydraulic Excavator",
      "equipment_category": "Construction Equipment",
      
      "total_revenue": "5000.00",
      "platform_commission_percentage": "10.00",
      "platform_commission_amount": "500.00",
      "seller_payout": "4500.00",
      
      "formatted_revenue": "AED 5,000.00",
      "formatted_commission": "AED 500.00",
      "formatted_payout": "AED 4,500.00",
      
      "rental_days": 7,
      "rental_start_date": "2025-01-15",
      "rental_end_date": "2025-01-22",
      
      "payout_status": "pending",
      "payout_status_display": "Pending Payout",
      "sale_date": "2025-01-23T10:30:00Z"
    }
  ]
}
```

### 2. Sales Analytics Summary

```http
GET /api/rentals/sales_analytics/
```

**Response:**
```json
{
  "total_sales": 150,
  "total_revenue": "750000.00",
  "total_commission": "75000.00",
  "total_seller_payout": "675000.00",
  
  "average_sale_value": "5000.00",
  "average_rental_days": 5.2,
  
  "this_month_sales": 45,
  "this_month_revenue": "225000.00",
  "last_month_sales": 38,
  "last_month_revenue": "190000.00",
  
  "revenue_growth_percentage": 18.4,
  "sales_growth_percentage": 18.4,
  
  "top_equipment": [
    {
      "name": "Excavator CAT 320D",
      "total_revenue": "45000.00",
      "rental_count": 12
    }
  ],
  
  "top_sellers": [
    {
      "company_name": "Equipment Masters LLC",
      "total_revenue": "150000.00",
      "sales_count": 35
    }
  ],
  
  "pending_payouts_count": 12,
  "pending_payouts_amount": "54000.00"
}
```

### 3. Seller-Specific Sales

```http
GET /api/rentals/sales/?seller={seller_id}
```

Returns only sales for specific seller.

### 4. Date Range Filter

```http
GET /api/rentals/sales/?start_date=2025-01-01&end_date=2025-01-31
```

### 5. Payout Status Filter

```http
GET /api/rentals/sales/?payout_status=pending
GET /api/rentals/sales/?payout_status=completed
```

---

## 💸 Payout Management

### Payout Statuses

1. **pending** - Sale created, not yet processed
2. **processing** - Payment in progress
3. **completed** - Seller has been paid
4. **failed** - Payment failed, needs retry
5. **on_hold** - Payment held (dispute, review, etc.)

### Mark Payout as Completed

```http
PATCH /api/rentals/sales/{id}/
```

```json
{
  "payout_status": "completed",
  "payout_date": "2025-01-25T14:30:00Z",
  "payout_reference": "PAY-2025-12345",
  "payout_notes": "Wire transfer completed successfully"
}
```

### Bulk Payout Processing

```python
from rentals.models import RentalSale
from django.utils import timezone

# Get all pending payouts
pending_sales = RentalSale.objects.filter(payout_status='pending')

for sale in pending_sales:
    # Process payment via payment gateway
    payment_result = process_seller_payment(
        seller=sale.seller,
        amount=sale.seller_payout
    )
    
    if payment_result.success:
        sale.payout_status = 'completed'
        sale.payout_date = timezone.now()
        sale.payout_reference = payment_result.reference
        sale.save()
```

---

## 🎯 Seller Dashboard Integration

### Revenue Metrics

Add to seller dashboard endpoint:

```python
from django.db.models import Sum, Count, Avg
from rentals.models import RentalSale

# Get seller sales
sales = RentalSale.objects.filter(seller=seller_profile)

metrics = {
    'total_sales': sales.count(),
    'total_revenue': sales.aggregate(Sum('total_revenue'))['total_revenue__sum'] or 0,
    'total_payout': sales.aggregate(Sum('seller_payout'))['seller_payout__sum'] or 0,
    'average_sale': sales.aggregate(Avg('total_revenue'))['total_revenue__avg'] or 0,
    
    'pending_payout': sales.filter(payout_status='pending').aggregate(
        Sum('seller_payout')
    )['seller_payout__sum'] or 0,
    
    'this_month_revenue': sales.filter(
        sale_date__gte=this_month_start
    ).aggregate(Sum('seller_payout'))['seller_payout__sum'] or 0,
    
    'last_month_revenue': sales.filter(
        sale_date__gte=last_month_start,
        sale_date__lt=this_month_start
    ).aggregate(Sum('seller_payout'))['seller_payout__sum'] or 0,
}
```

---

## 📋 Admin Interface

### Django Admin Features

Access: `/admin/rentals/rentalsale/`

**List View:**
- Rental reference
- Seller name
- Equipment
- Total revenue
- Commission amount
- Seller payout
- Payout status
- Sale date

**Filters:**
- Payout status
- Sale date
- Seller
- Equipment category

**Search:**
- Rental reference
- Seller company name
- Equipment name
- Customer email

**Actions:**
- Mark as paid
- Export to CSV
- Generate payout reports

---

## 🧪 Testing Sale Creation

### 1. Create a Rental

```http
POST /api/rentals/rentals/
```

### 2. Update Status Through Workflow

```http
POST /api/rentals/rentals/{id}/update_status/
```

Progress through statuses:
- pending → approved
- approved → confirmed
- confirmed → delivered
- delivered → in_progress
- in_progress → returning
- returning → **completed** ✅

### 3. Check Sale Created

```http
GET /api/rentals/sales/?rental={rental_id}
```

Or check in Django admin.

### 4. Verify Console Log

```
📊 Rental RENT-2025-001 marked as COMPLETED - Sale will be recorded
✅ Sale created for rental RENT-2025-001
```

---

## 🔍 Querying Sales Data

### Get All Sales for a Seller

```python
from rentals.models import RentalSale

sales = RentalSale.objects.filter(seller__id=1)
total_revenue = sales.aggregate(Sum('seller_payout'))['seller_payout__sum']
```

### Get Sales for Specific Equipment

```python
sales = RentalSale.objects.filter(equipment__id=5)
```

### Get Pending Payouts

```python
pending = RentalSale.objects.filter(payout_status='pending')
total_pending = pending.aggregate(Sum('seller_payout'))['seller_payout__sum']
```

### Get This Month's Sales

```python
from django.utils import timezone
import datetime

start_of_month = timezone.now().replace(day=1, hour=0, minute=0, second=0)
this_month_sales = RentalSale.objects.filter(sale_date__gte=start_of_month)
```

### Get Top Performing Equipment

```python
from django.db.models import Sum, Count

top_equipment = RentalSale.objects.values(
    'equipment__name'
).annotate(
    total_revenue=Sum('total_revenue'),
    rental_count=Count('id')
).order_by('-total_revenue')[:10]
```

---

## 💡 Business Intelligence Use Cases

### 1. Revenue Forecasting
- Track monthly sales trends
- Predict future revenue based on active rentals
- Seasonal analysis

### 2. Commission Reports
- Total platform earnings
- Per-seller commission tracking
- Category-based commission analysis

### 3. Seller Performance
- Top revenue-generating sellers
- Average sale value per seller
- Payout history and reliability

### 4. Equipment ROI
- Most profitable equipment
- Average revenue per rental day
- Equipment utilization rates

### 5. Financial Dashboards
- Daily/weekly/monthly revenue
- Outstanding payouts
- Payment success rates
- Geographic revenue distribution

---

## 🚀 Future Enhancements

### 1. Variable Commission Rates
- Tier-based pricing (5%, 10%, 15%)
- Promotional rates for new sellers
- Volume-based discounts

### 2. Automated Payouts
- Schedule automatic payments
- Integration with payment gateways
- Multi-currency support

### 3. Tax Management
- VAT/GST calculation and tracking
- Tax reports per jurisdiction
- Withholding tax support

### 4. Advanced Analytics
- ML-based revenue predictions
- Fraud detection
- Customer lifetime value

### 5. Seller Insights
- Personalized dashboards
- Performance benchmarking
- Revenue optimization tips

---

## 📞 Support & Questions

**When does a rental become a sale?**
→ When status changes to 'completed'

**How is commission calculated?**
→ Platform takes 10% of total revenue, seller gets 90%

**When do sellers get paid?**
→ After payout_status changes to 'completed' (admin action)

**Can commission rates vary?**
→ Yes, but currently all use 10% default. System supports custom rates.

**What if rental is cancelled after sale creation?**
→ Sales are only created for 'completed' status. Cancelled rentals don't create sales.

**How to track pending payouts?**
→ Filter by `payout_status='pending'` in admin or API

---

## 📚 Related Documentation

- `MASTER_API_DOCUMENTATION.md` - Full API reference
- `RENTALS_FRONTEND_GUIDE.md` - Frontend integration
- `SELLER_DASHBOARD_SPEC.md` - Seller dashboard features
- `ARCHITECTURE_IMPROVEMENTS.md` - Technical specifications

---

**Last Updated:** October 31, 2025  
**Version:** 1.0
