# 💵 Cash on Delivery (COD) - Standard Operating Procedure

## Overview
Cash on Delivery allows customers to pay with cash when equipment is delivered, instead of paying online through a payment gateway.

---

## 🔄 Cash on Delivery Workflow

### **Step 1: Customer Books Rental**
```
Customer selects equipment and dates
├─→ Payment method: "Cash on Delivery"
├─→ Rental status: 'pending'
└─→ RentalPayment created (status: 'pending', method: 'cash')
```

### **Step 2: Seller Approves**
```
Seller reviews and approves rental
├─→ Rental status: 'approved'
└─→ Prepares equipment for delivery
```

### **Step 3: Delivery & Cash Collection**
```
Seller/driver delivers equipment to customer
├─→ Customer pays cash: AED 2,350
├─→ Seller issues receipt
├─→ Seller uploads receipt to system
└─→ Rental status: 'confirmed'

RentalPayment updated:
├─→ payment_status: 'completed'
├─→ completed_at: 2025-11-04 14:30:00
├─→ receipt_number: "REC-20251104-001"
├─→ receipt_file: "payment_receipts/receipt_001.pdf"
└─→ notes: "Cash collected by John Doe on delivery"
```

### **Step 4: Seller Keeps 90%, Owes Platform 10%**
```
✅ Seller collected: AED 2,350 (full amount)

Seller's obligation:
├─→ Keeps: AED 2,115 (90%)
└─→ Owes platform: AED 235 (10% commission)
```

### **Step 5: Rental Completes**
```
After rental period ends:
├─→ Equipment returned
├─→ Rental status: 'completed'
└─→ RentalSale created:
    ├─→ total_revenue: AED 2,350
    ├─→ platform_commission_amount: AED 235
    ├─→ seller_payout: AED 2,115
    └─→ payout_status: 'completed' (already paid via COD)
```

### **Step 6: Commission Settlement**
```
Platform invoices seller for commission:
├─→ Seller owes: AED 235
├─→ Settlement options:
    ├─ Deducted from next payout
    ├─ Monthly invoice (bank transfer)
    └─ Wallet/credit system
```

---

## 💰 Money Flow Comparison

### **Online Payment (Gateway):**
```
Customer Card → Gateway → Platform Bank → Platform pays Seller
AED 2,350 → Stripe → Platform (keeps 235) → Seller (gets 2,115)
```

### **Cash on Delivery:**
```
Customer Cash → Seller → Seller remits Commission → Platform
AED 2,350 → Seller (keeps 2,115) → Platform (receives 235)
```

---

## 📋 Standard COD Procedures

### **For Sellers:**

#### ✅ **Required Actions:**
1. **Collect Full Amount**
   - Collect AED 2,350 from customer
   - Count money in customer's presence
   - Verify no counterfeit bills

2. **Issue Receipt**
   - Date and time
   - Amount received
   - Rental reference number
   - Seller signature
   - Customer signature (optional)

3. **Upload Proof**
   - Photo of receipt
   - Upload to platform within 24 hours
   - Add notes about collection

4. **Remit Commission**
   - Platform commission: 10%
   - Due within 7-30 days (configurable)
   - Payment via bank transfer or deduction

#### ⚠️ **Prohibited Actions:**
- ❌ Collecting less than full amount
- ❌ Delaying receipt upload
- ❌ Not issuing customer receipt
- ❌ Altering payment amounts

---

### **For Platform/Admin:**

#### ✅ **Verification Process:**
1. **Receipt Review**
   - Check receipt uploaded
   - Verify amount matches booking
   - Confirm signatures present

2. **Payment Confirmation**
   - Mark RentalPayment as 'completed'
   - Update completed_at timestamp
   - Change rental status to 'confirmed'

3. **Commission Tracking**
   - Track commission owed by seller
   - Issue invoice (weekly/monthly)
   - Monitor payment status

4. **Reconciliation**
   - Monthly commission settlement
   - Generate seller statements
   - Track outstanding commissions

---

## 🔐 Security & Fraud Prevention

### **Risk Mitigation:**

#### 1. **Seller Verification**
```python
# Only verified sellers can use COD
if seller.verification_status != 'verified':
    cod_payment_disabled = True
```

#### 2. **COD Limits**
```python
# Limit COD to certain amounts
MAX_COD_AMOUNT = 10000  # AED
if rental.total_amount > MAX_COD_AMOUNT:
    cod_option_disabled = True
```

#### 3. **Track Record**
```python
# Disable COD for sellers with issues
if seller.unpaid_commissions > threshold:
    cod_suspended = True
```

#### 4. **Receipt Validation**
- Required within 24 hours of delivery
- Must include photo evidence
- System sends reminders
- Late uploads trigger warnings

---

## 📊 Commission Settlement Methods

### **Option 1: Monthly Invoice**
```
Platform invoices seller monthly:
├─→ Invoice generated on 1st of month
├─→ Lists all COD transactions
├─→ Total commission owed
├─→ Due date: 15th of month
└─→ Payment via bank transfer
```

### **Option 2: Deduct from Next Payout**
```
When seller has online payment rentals:
├─→ Platform holds commission from payout
├─→ Automatically deducted
└─→ Settles COD commission debt

Example:
Next online rental payout: AED 1,500
COD commission owed: AED 235
Seller receives: AED 1,265 (1,500 - 235)
```

### **Option 3: Prepaid Wallet**
```
Seller maintains wallet balance:
├─→ Deposits money in advance
├─→ COD commissions deducted automatically
└─→ Refill when low

Seller deposits: AED 1,000
COD commission: AED 235
New balance: AED 765
```

---

## 📱 Implementation in Code

### **RentalPayment Model (Already Supports COD):**
```python
class RentalPayment(models.Model):
    payment_method = models.CharField(
        max_length=20,
        choices=[
            ('card', 'Credit/Debit Card'),
            ('cash', 'Cash'),  # ← COD uses this
            ('bank_transfer', 'Bank Transfer'),
            # ...
        ]
    )
    
    # For COD receipt upload
    receipt_file = models.FileField(
        upload_to='payment_receipts/',
        blank=True,
        help_text="Payment receipt for COD"
    )
    
    receipt_number = models.CharField(
        max_length=50,
        blank=True
    )
    
    notes = models.TextField(
        blank=True,
        help_text="E.g., 'Cash collected by John on delivery'"
    )
```

### **COD Flow Example:**
```python
# When seller delivers and collects cash
rental = Rental.objects.get(id=rental_id)
payment = rental.payments.get(payment_type='rental_fee')

# Seller uploads receipt
payment.payment_method = 'cash'
payment.receipt_number = 'REC-20251104-001'
payment.receipt_file = receipt_file
payment.notes = 'Cash collected on delivery by John Doe'
payment.payment_status = 'completed'
payment.completed_at = timezone.now()
payment.save()

# Update rental status
rental.status = 'confirmed'
rental.save()

# Track commission owed
commission_owed = rental.total_amount * Decimal('0.10')
# Add to seller's commission balance (to be paid later)
```

---

## 📈 Dashboard Display

### **Seller Dashboard:**
```
╔════════════════════════════════════════════════════════╗
║                  COMMISSION BALANCE                    ║
║                                                        ║
║   COD Collections:     AED 2,350.00                   ║
║   Your Earnings:       AED 2,115.00 (kept)            ║
║   Commission Owed:     AED 235.00 (due Nov 15)        ║
╚════════════════════════════════════════════════════════╝

Recent COD Transactions:
┌────────────┬──────────┬───────────┬─────────────┐
│ Date       │ Rental   │ Collected │ Commission  │
├────────────┼──────────┼───────────┼─────────────┤
│ Nov 4      │ RNT12345 │ AED 2,350 │ AED 235     │
│ Nov 1      │ RNT12340 │ AED 1,200 │ AED 120     │
└────────────┴──────────┴───────────┴─────────────┘

Total Commission Due: AED 355 (Due: Nov 15, 2025)
```

### **Admin Dashboard:**
```
╔════════════════════════════════════════════════════════╗
║              COD COMMISSION TRACKING                   ║
║                                                        ║
║   This Month COD:      AED 45,000                     ║
║   Commission Due:      AED 4,500                      ║
║   Received:            AED 3,200 (71%)                ║
║   Outstanding:         AED 1,300 (29%)                ║
╚════════════════════════════════════════════════════════╝

Sellers with Outstanding Commission:
┌──────────────┬───────────┬─────────┬────────────┐
│ Seller       │ Amount    │ Days    │ Status     │
├──────────────┼───────────┼─────────┼────────────┤
│ Heavy Eq Co  │ AED 235   │ 4 days  │ On time    │
│ UAE Rentals  │ AED 1,065 │ 18 days │ ⚠️ Due    │
└──────────────┴───────────┴─────────┴────────────┘
```

---

## ⚖️ Legal & Tax Considerations

### **VAT/Tax:**
- Platform commission subject to VAT
- Seller responsible for sales tax on full amount
- Receipt must show VAT breakdown

### **Accounting:**
- COD treated as seller revenue
- Commission = liability to platform
- Must track for financial reporting

### **Contracts:**
- Terms & Conditions must specify COD terms
- Commission payment obligations
- Late payment penalties

---

## 🎯 Best Practices

### ✅ **DO:**
- Issue receipts immediately
- Upload proof within 24 hours
- Keep cash secure during transport
- Verify bills authenticity
- Track all COD transactions
- Pay commissions on time

### ❌ **DON'T:**
- Collect partial payments
- Delay receipt uploads
- Skip customer receipts
- Ignore platform invoices
- Mix personal and business funds

---

## 📞 Support & Disputes

### **Customer Disputes:**
- Receipt is proof of payment
- Photos/timestamps critical
- Platform mediates disputes

### **Seller Support:**
- Help with receipt templates
- Commission payment reminders
- Statement generation
- Dispute resolution

---

**Last Updated:** November 4, 2025  
**Version:** 1.0
