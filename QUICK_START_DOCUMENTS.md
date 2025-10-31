# Quick Start: Document & Auto-Approval Features

## 🎯 What's New

### 1. **Operating Manual Upload (Seller)**
- Sellers can now upload operating manuals when creating equipment listings
- Customers can access manuals **AFTER payment**

### 2. **Payment Receipt Upload (Seller)**  
- Sellers upload payment receipts after cash on delivery
- Includes receipt number and notes

### 3. **Auto-Approval for Small Orders**
- Rentals with quantity < 5 automatically approved ✅
- Rentals with quantity >= 5 need seller approval ⏳

### 4. **Auto-Document Generation**
- Rental agreements created automatically ✅
- Operating manuals auto-attached (locked until payment) 🔒

---

## 📋 Frontend Form Updates Needed

### Seller Dashboard - Equipment Creation Form

**Add these fields to your equipment creation form:**

```javascript
// Existing fields
name: string
description: string
category_id: number
daily_rate: number
total_units: number

// 🆕 NEW FIELDS - Add these
operating_manual: File  // PDF, DOC, DOCX (optional)
manual_description: string  // "Complete safety and operating guide"
```

**Form Submission Example:**
```javascript
const formData = new FormData();
formData.append('name', 'Excavator XL');
formData.append('description', 'Heavy duty excavator');
formData.append('category_id', categoryId);
formData.append('daily_rate', 500);
formData.append('total_units', 3);

// Add operating manual if seller uploads one
if (manualFile) {
  formData.append('operating_manual', manualFile);
  formData.append('manual_description', 'Complete operating and safety manual');
}

await fetch('/api/equipment/equipment/', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` },
  body: formData
});
```

---

### Seller Dashboard - Upload Payment Receipt

**Add this feature after seller collects cash payment:**

**Endpoint:** `POST /api/rentals/rentals/{rental_id}/upload_payment_receipt/`

```javascript
const uploadReceipt = async (rentalId, receiptFile, receiptNumber, notes) => {
  const formData = new FormData();
  formData.append('receipt_file', receiptFile);  // Photo or PDF
  formData.append('receipt_number', receiptNumber);  // "RCT-001"
  formData.append('notes', notes);  // "Cash collected by driver John"
  
  const response = await fetch(
    `/api/rentals/rentals/${rentalId}/upload_payment_receipt/`,
    {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${sellerToken}` },
      body: formData
    }
  );
  
  const result = await response.json();
  // { message: "Payment receipt uploaded successfully", payment: {...} }
  
  return result;
};
```

**UI Elements:**
- File upload button (accept images and PDFs)
- Receipt number text input
- Notes textarea
- Submit button

---

## 📱 Customer App Updates

### View Rental Documents

**Endpoint:** `GET /api/rentals/rentals/{rental_id}/documents/`

```javascript
const getRentalDocuments = async (rentalId) => {
  const response = await fetch(
    `/api/rentals/rentals/${rentalId}/documents/`,
    { headers: { 'Authorization': `Bearer ${customerToken}` } }
  );
  
  const data = await response.json();
  // {
  //   count: 2,
  //   documents: [
  //     {
  //       id: 1,
  //       document_type: "rental_agreement",
  //       title: "Rental Agreement - RNT123",
  //       file_url: "http://.../agreement.txt",
  //       is_locked: false,  // ✅ Can download
  //       requires_payment: false
  //     },
  //     {
  //       id: 2,
  //       document_type: "operating_manual",
  //       title: "Operating Manual - Excavator",
  //       file_url: "http://.../manual.pdf",
  //       is_locked: true,  // 🔒 Locked until payment
  //       requires_payment: true
  //     }
  //   ]
  // }
  
  return data;
};
```

**Display Logic:**
```javascript
{documents.map(doc => (
  <DocumentCard key={doc.id}>
    <Icon name={doc.is_locked ? 'lock' : 'file-document'} />
    <h4>{doc.title}</h4>
    <p>{doc.document_type_display}</p>
    
    {doc.is_locked ? (
      <Badge>🔒 Unlocks after payment</Badge>
    ) : (
      <Button onClick={() => downloadDocument(doc.file_url)}>
        Download
      </Button>
    )}
  </DocumentCard>
))}
```

---

## 🔄 Workflow Summary

### Complete Flow:

1. **Seller creates equipment listing**
   - Fills basic info (name, price, etc.)
   - **🆕 Uploads operating manual (optional)**
   - Clicks "Create Equipment"

2. **Customer books equipment**
   - Selects dates and quantity
   - Clicks "Book Now"
   - **Auto-approved if quantity < 5 ✅**
   - **Pending if quantity >= 5 ⏳**

3. **Documents auto-generated:**
   - ✅ Rental agreement created (unlocked)
   - 🔒 Operating manual attached (locked)

4. **Customer views documents:**
   - Can view/sign rental agreement immediately
   - Operating manual shows "🔒 Locked until payment"

5. **Seller collects payment (cash on delivery)**
   - Meets customer, collects cash
   - **🆕 Uploads payment receipt** via seller dashboard
   - Enters receipt number and notes

6. **Operating manual unlocks:**
   - System detects completed payment
   - Operating manual automatically unlocks 🔓
   - Customer can now download manual

---

## ✅ Testing Checklist

### Test 1: Equipment Creation with Manual
```
✓ Create equipment without manual (should work)
✓ Create equipment with manual PDF (should upload and save)
✓ Verify manual_description field saves correctly
```

### Test 2: Rental Auto-Approval
```
✓ Create rental with quantity=1 → Status = "approved" ✅
✓ Create rental with quantity=4 → Status = "approved" ✅
✓ Create rental with quantity=5 → Status = "pending" ⏳
✓ Create rental with quantity=10 → Status = "pending" ⏳
```

### Test 3: Document Generation
```
✓ Create rental → Rental agreement auto-created
✓ Rental agreement visible to customer immediately
✓ If equipment has manual → Operating manual attached
✓ Operating manual is locked (is_locked = true)
```

### Test 4: Receipt Upload
```
✓ Seller can upload receipt file
✓ Receipt number saves correctly
✓ Notes field saves correctly
✓ Payment status changes to "completed"
```

### Test 5: Manual Unlock
```
✓ Before payment → Operating manual locked 🔒
✓ After payment → Operating manual unlocked 🔓
✓ Customer can download manual after payment
```

---

## 🐛 Troubleshooting

### Issue: Operating manual field not showing
**Fix:** Clear browser cache, verify serializers updated

### Issue: Rentals not auto-approving
**Check:** 
- Quantity < 5?
- Check rental status in database
- Verify RentalCreateSerializer logic

### Issue: Manual not unlocking after payment
**Check:**
- Payment status = "completed"?
- Verify payment exists in database
- Check is_locked calculation in serializer

### Issue: Receipt upload fails
**Check:**
- User is seller?
- Rental belongs to this seller?
- File size < limit?

---

## 📊 Database Fields Reference

### Equipment Model
```python
operating_manual = FileField(upload_to='equipment_manuals/', null=True, blank=True)
manual_description = TextField(blank=True)
```

### RentalPayment Model
```python
receipt_file = FileField(upload_to='payment_receipts/', null=True, blank=True)
receipt_number = CharField(max_length=50, blank=True)
notes = TextField(blank=True)
```

### RentalDocument Model
```python
visible_to_customer = BooleanField(default=True)
requires_payment = BooleanField(default=False)
is_locked = SerializerMethodField()  # Calculated dynamically
```

---

## 🚀 Ready for Implementation!

**All backend code is complete:**
- ✅ Models updated with new fields
- ✅ Serializers include all fields
- ✅ Auto-approval logic implemented
- ✅ Document generation works
- ✅ Receipt upload endpoint ready
- ✅ Document viewing endpoint ready

**Frontend needs to:**
1. Add operating manual upload to equipment form
2. Add receipt upload UI to seller dashboard
3. Add document viewing page to customer app
4. Show lock/unlock indicators on documents

---

**Implementation Date:** October 28, 2025  
**Status:** ✅ Backend Complete - Ready for Frontend Integration  
**Django Version:** 5.2.7

For detailed examples, see `IMPLEMENTATION_COMPLETE_GUIDE.md`
