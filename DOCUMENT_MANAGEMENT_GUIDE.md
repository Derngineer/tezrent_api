# 📄 Document & Payment Receipt Management Guide

## 🎯 Overview

Your rental system now supports comprehensive document management including:
- **Rental agreements** (contracts between parties)
- **Operating manuals** (equipment instructions, available after payment)
- **Payment receipts** (for cash on delivery and manual payments)
- **Delivery/return receipts** (proof of transfer with signatures)
- **Insurance documents**
- **Damage reports**
- **Invoices**

---

## 📁 Document Types Explained

### 1. **Rental Agreement** 🤝
- **Who uploads**: Seller (auto-generated or template-based)
- **When**: After booking confirmation
- **Requires payment**: No (customer must see to agree)
- **Purpose**: Legal contract terms and conditions
- **Can be signed**: Yes (digital signature)

### 2. **Operating Manual** 📖
- **Who uploads**: Seller (when creating equipment listing)
- **When**: Available in equipment listing
- **Requires payment**: YES ✅ (Only visible after booking confirmation/payment)
- **Purpose**: Equipment operation instructions, safety guidelines, troubleshooting
- **Location**: Equipment.operating_manual field

### 3. **Payment Receipt** 💵
- **Who uploads**: Seller
- **When**: After cash on delivery or manual payment verification
- **Purpose**: Proof of payment for bookkeeping
- **Attached to**: RentalPayment model
- **Fields**: receipt_file, receipt_number, notes

### 4. **Delivery Receipt** 📦
- **Who uploads**: Seller/Delivery person
- **When**: When equipment is delivered to customer
- **Purpose**: Proof customer received equipment in good condition
- **Can be signed**: Yes (customer signs upon receipt)

### 5. **Return Receipt** ↩️
- **Who uploads**: Seller/Pickup person
- **When**: When equipment is returned by customer
- **Purpose**: Document condition of equipment upon return
- **Can be signed**: Yes (both parties sign)

### 6. **Damage Report** ⚠️
- **Who uploads**: Seller or Customer
- **When**: If equipment is damaged during rental
- **Purpose**: Document damages for insurance/billing
- **Photos**: Can attach to RentalImage model

### 7. **Invoice** 📄
- **Who uploads**: System (auto-generated) or Seller
- **When**: After booking confirmation
- **Purpose**: Formal invoice for payment

---

## 🗄️ Database Models

### Equipment Model (has operating manual)
```python
class Equipment(models.Model):
    # ... other fields ...
    
    # Operating Manual (uploaded by seller)
    operating_manual = FileField(
        upload_to='equipment_manuals/',
        blank=True, null=True,
        help_text="Operating manual/user guide (PDF)"
    )
    manual_description = TextField(
        blank=True,
        help_text="Description of what's included in the manual"
    )
```

### RentalPayment Model (has receipt)
```python
class RentalPayment(models.Model):
    rental = ForeignKey(Rental)
    payment_type = CharField(...)  # rental_fee, security_deposit, etc.
    amount = DecimalField(...)
    payment_method = CharField(...)  # card, cash, bank_transfer
    payment_status = CharField(...)  # pending, completed, failed
    
    # Payment receipt fields
    receipt_file = FileField(
        upload_to='payment_receipts/',
        blank=True, null=True,
        help_text="Payment receipt (for cash or manual payments)"
    )
    receipt_number = CharField(
        max_length=50,
        blank=True,
        help_text="Receipt/invoice number"
    )
    notes = TextField(
        blank=True,
        help_text="Additional notes (e.g., 'Cash collected by John')"
    )
    
    # Gateway info (for online payments)
    transaction_id = CharField(...)
    gateway_reference = CharField(...)
    
    # Timestamps
    created_at = DateTimeField(...)
    completed_at = DateTimeField(...)
```

### RentalDocument Model (all other documents)
```python
class RentalDocument(models.Model):
    rental = ForeignKey(Rental)
    document_type = CharField(...)  # rental_agreement, delivery_receipt, etc.
    title = CharField(max_length=200)
    file = FileField(upload_to='rental_documents/')
    uploaded_by = ForeignKey(User)
    
    # Visibility control
    visible_to_customer = BooleanField(default=True)
    requires_payment = BooleanField(
        default=False,
        help_text="Only visible after payment (e.g., operating manual)"
    )
    
    # Digital signature
    is_signed = BooleanField(default=False)
    signed_at = DateTimeField(null=True)
    signature_data = JSONField(default=dict)
    
    created_at = DateTimeField(...)
```

---

## 📋 Document Workflow

### Seller Workflow:

```
1. Create Equipment Listing
   └─ Upload operating_manual PDF (optional)
      └─ Add manual_description
      
2. Customer Books Equipment
   ↓
3. Seller Approves Booking
   └─ System creates rental_agreement document
   └─ Customer can view and sign
   
4. Customer Makes Payment (or Cash on Delivery)
   ↓
5. Seller Records Payment
   └─ If cash: Upload receipt_file
   └─ Add receipt_number
   └─ Add notes ("Cash collected by delivery driver")
   
6. Operating Manual Becomes Visible
   └─ System automatically makes it available
   └─ Customer can download from app
   
7. Delivery
   └─ Upload delivery_receipt document
   └─ Customer signs digitally
   
8. Rental Period
   └─ If damaged: Upload damage_report
   
9. Return
   └─ Upload return_receipt document
   └─ Both parties sign
   └─ Note condition of equipment
```

---

## 🔐 Visibility & Access Control

### Document Visibility Rules:

| Document Type | Visible Before Payment | Visible After Payment | Who Can Upload |
|--------------|----------------------|---------------------|----------------|
| Rental Agreement | ✅ Yes | ✅ Yes | Seller/System |
| Operating Manual | ❌ No | ✅ Yes | Seller |
| Payment Receipt | ❌ No | ✅ Yes | Seller |
| Delivery Receipt | ❌ No | ✅ Yes | Seller/Driver |
| Return Receipt | ❌ No | ✅ Yes | Seller/Driver |
| Damage Report | ❌ No | ✅ Yes | Both |
| Invoice | ✅ Yes | ✅ Yes | System/Seller |

### Implementation:

```python
# In RentalDetailSerializer
def get_documents(self, obj):
    documents = obj.documents.filter(visible_to_customer=True)
    
    # Check if payment completed
    payment_completed = obj.payments.filter(
        payment_status='completed'
    ).exists()
    
    # Filter out payment-required docs if not paid
    if not payment_completed:
        documents = documents.filter(requires_payment=False)
    
    return RentalDocumentSerializer(documents, many=True).data
```

---

## 📱 API Endpoints

### 1. Upload Operating Manual (Equipment)
```
POST /api/equipment/equipment/{id}/upload_manual/
Content-Type: multipart/form-data

Fields:
- operating_manual: File (PDF)
- manual_description: Text
```

**Response:**
```json
{
  "message": "Operating manual uploaded successfully",
  "equipment": {
    "id": 1,
    "name": "Caterpillar Excavator",
    "operating_manual": "http://.../media/equipment_manuals/excavator_manual.pdf",
    "manual_description": "Complete operation guide including safety procedures..."
  }
}
```

### 2. Upload Payment Receipt
```
POST /api/rentals/payments/{payment_id}/upload_receipt/
Content-Type: multipart/form-data

Fields:
- receipt_file: File (PDF/Image)
- receipt_number: String
- notes: Text
```

**Response:**
```json
{
  "id": 1,
  "rental": 1,
  "payment_type": "rental_fee",
  "amount": "1825.00",
  "payment_method": "cash",
  "payment_status": "completed",
  "receipt_file": "http://.../media/payment_receipts/REC001.pdf",
  "receipt_number": "REC-2025-001",
  "notes": "Cash collected on delivery by John Smith",
  "completed_at": "2025-10-28T10:30:00Z"
}
```

### 3. Upload Rental Document
```
POST /api/rentals/rentals/{rental_id}/upload_document/
Content-Type: multipart/form-data

Fields:
- document_type: String (rental_agreement, delivery_receipt, etc.)
- title: String
- file: File (PDF)
- visible_to_customer: Boolean (default: true)
- requires_payment: Boolean (default: false)
```

**Response:**
```json
{
  "id": 1,
  "rental": 1,
  "document_type": "delivery_receipt",
  "title": "Delivery Receipt - RNTF7EC27D3",
  "file": "http://.../media/rental_documents/delivery_001.pdf",
  "uploaded_by": "Ustasells",
  "visible_to_customer": true,
  "requires_payment": false,
  "is_signed": false,
  "created_at": "2025-10-28T11:00:00Z"
}
```

### 4. Sign Document (Digital Signature)
```
POST /api/rentals/documents/{document_id}/sign/
Content-Type: application/json

{
  "signature_data": {
    "signature_image": "data:image/png;base64,...",
    "signed_by": "customer",
    "ip_address": "192.168.1.1",
    "device": "iPhone 14 Pro"
  }
}
```

### 5. Get Rental Documents
```
GET /api/rentals/rentals/{rental_id}/documents/
```

**Response:**
```json
{
  "documents": [
    {
      "id": 1,
      "document_type": "rental_agreement",
      "title": "Rental Agreement - RNTF7EC27D3",
      "file": "http://.../rental_agreement_001.pdf",
      "visible_to_customer": true,
      "requires_payment": false,
      "is_signed": true,
      "signed_at": "2025-10-28T09:30:00Z",
      "created_at": "2025-10-28T09:00:00Z"
    },
    {
      "id": 2,
      "document_type": "operating_manual",
      "title": "Excavator Operating Manual",
      "file": "http://.../equipment_manuals/excavator_manual.pdf",
      "visible_to_customer": true,
      "requires_payment": true,  // ← Only visible after payment
      "is_signed": false,
      "created_at": "2025-10-28T09:00:00Z"
    }
  ]
}
```

---

## 💰 Payment Receipt Workflow

### Scenario: Cash on Delivery

```
1. Customer books equipment
   Status: pending
   
2. Seller approves
   Status: approved
   
3. Equipment delivered + cash collected
   ↓
4. Seller creates payment record:
   POST /api/rentals/rentals/{rental_id}/make_payment/
   {
     "payment_type": "rental_fee",
     "amount": 1825.00,
     "payment_method": "cash",
     "notes": "Cash collected on delivery by John Smith"
   }
   
5. Seller uploads receipt:
   POST /api/rentals/payments/{payment_id}/upload_receipt/
   Form Data:
   - receipt_file: [receipt.pdf]
   - receipt_number: "REC-2025-001"
   - notes: "Driver signature on receipt"
   
6. Payment marked as completed
   ↓
7. Operating manual becomes visible to customer
```

---

## 🎨 React Seller Dashboard - Implementation

### Payment Receipt Upload Component:

```tsx
const UploadPaymentReceipt = ({ payment }: { payment: Payment }) => {
  const [receiptFile, setReceiptFile] = useState<File | null>(null);
  const [receiptNumber, setReceiptNumber] = useState('');
  const [notes, setNotes] = useState('');
  const [uploading, setUploading] = useState(false);
  
  const handleUpload = async () => {
    if (!receiptFile) {
      alert('Please select a receipt file');
      return;
    }
    
    setUploading(true);
    const formData = new FormData();
    formData.append('receipt_file', receiptFile);
    formData.append('receipt_number', receiptNumber);
    formData.append('notes', notes);
    
    try {
      const response = await fetch(
        `http://localhost:8000/api/rentals/payments/${payment.id}/upload_receipt/`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${accessToken}`,
          },
          body: formData
        }
      );
      
      if (response.ok) {
        alert('Receipt uploaded successfully!');
        // Refresh payment data
      } else {
        alert('Failed to upload receipt');
      }
    } catch (error) {
      console.error('Upload error:', error);
    } finally {
      setUploading(false);
    }
  };
  
  return (
    <div className="receipt-upload-form">
      <h3>Upload Payment Receipt</h3>
      
      <div className="form-group">
        <label>Receipt File (PDF/Image)</label>
        <input
          type="file"
          accept=".pdf,.jpg,.jpeg,.png"
          onChange={(e) => setReceiptFile(e.target.files?.[0] || null)}
        />
      </div>
      
      <div className="form-group">
        <label>Receipt Number</label>
        <input
          type="text"
          value={receiptNumber}
          onChange={(e) => setReceiptNumber(e.target.value)}
          placeholder="REC-2025-001"
        />
      </div>
      
      <div className="form-group">
        <label>Notes</label>
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Cash collected by delivery driver John Smith"
          rows={3}
        />
      </div>
      
      <button onClick={handleUpload} disabled={uploading}>
        {uploading ? 'Uploading...' : 'Upload Receipt'}
      </button>
    </div>
  );
};
```

### Operating Manual Upload (Equipment Form):

```tsx
const EquipmentForm = () => {
  const [operatingManual, setOperatingManual] = useState<File | null>(null);
  const [manualDescription, setManualDescription] = useState('');
  
  // ... other form fields ...
  
  return (
    <form onSubmit={handleSubmit}>
      {/* ... other fields ... */}
      
      <div className="form-section">
        <h3>Operating Manual (Optional)</h3>
        <p className="help-text">
          Upload equipment operating manual. Will be available to customers after booking.
        </p>
        
        <div className="form-group">
          <label>Manual File (PDF)</label>
          <input
            type="file"
            accept=".pdf"
            onChange={(e) => setOperatingManual(e.target.files?.[0] || null)}
          />
        </div>
        
        <div className="form-group">
          <label>Manual Description</label>
          <textarea
            value={manualDescription}
            onChange={(e) => setManualDescription(e.target.value)}
            placeholder="Comprehensive operating guide including safety procedures, maintenance tips, and troubleshooting..."
            rows={3}
          />
        </div>
      </div>
      
      <button type="submit">Create Equipment</button>
    </form>
  );
};
```

---

## 📱 React Native Customer App - View Documents

```tsx
const RentalDocuments = ({ rental }: { rental: Rental }) => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetchDocuments();
  }, [rental.id]);
  
  const fetchDocuments = async () => {
    try {
      const response = await fetch(
        `${API_URL}/api/rentals/rentals/${rental.id}/documents/`,
        {
          headers: {
            'Authorization': `Bearer ${accessToken}`,
          }
        }
      );
      const data = await response.json();
      setDocuments(data.documents);
    } catch (error) {
      console.error('Error fetching documents:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const openDocument = async (doc) => {
    // Open PDF in browser or download
    Linking.openURL(doc.file);
  };
  
  if (loading) {
    return <ActivityIndicator size="large" />;
  }
  
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Rental Documents</Text>
      
      {documents.length === 0 ? (
        <Text style={styles.emptyText}>No documents available yet</Text>
      ) : (
        documents.map((doc) => (
          <TouchableOpacity
            key={doc.id}
            style={styles.documentCard}
            onPress={() => openDocument(doc)}
          >
            <View style={styles.documentIcon}>
              📄
            </View>
            <View style={styles.documentInfo}>
              <Text style={styles.documentTitle}>{doc.title}</Text>
              <Text style={styles.documentType}>
                {doc.document_type.replace('_', ' ')}
              </Text>
              {doc.is_signed && (
                <Text style={styles.signedBadge}>✓ Signed</Text>
              )}
            </View>
            <Text style={styles.downloadIcon}>⬇️</Text>
          </TouchableOpacity>
        ))
      )}
      
      {rental.status === 'confirmed' && (
        <View style={styles.infoBox}>
          <Text style={styles.infoText}>
            💡 Operating manual is now available for download!
          </Text>
        </View>
      )}
    </View>
  );
};
```

---

## ✅ Best Practices

### For Sellers:

1. **Upload operating manuals** when creating equipment listings
2. **Always upload receipts** for cash on delivery payments
3. **Use delivery/return receipts** with customer signatures
4. **Document damages** immediately with photos and reports
5. **Keep internal notes** in document notes field

### For System:

1. **Auto-generate** rental agreements from templates
2. **Control visibility** based on payment status
3. **Store signatures** securely with timestamp and IP
4. **Validate file types** (PDF for documents, PDF/images for receipts)
5. **Set file size limits** (e.g., 10MB max)

### Security:

1. Only allow authenticated users to upload
2. Verify uploader is seller or admin
3. Scan uploaded files for malware
4. Use signed URLs for file downloads
5. Log all document uploads and accesses

---

## 🎯 Summary

You now have a complete document management system:

✅ **Equipment operating manuals** - Uploaded by sellers, visible after payment
✅ **Payment receipts** - For cash on delivery and manual verification
✅ **Rental agreements** - Legal contracts with digital signatures
✅ **Delivery/return receipts** - Proof of transfer
✅ **Damage reports** - Document issues
✅ **Visibility control** - Show documents based on payment status
✅ **Digital signatures** - Legally binding electronic signatures

All ready for implementation in your frontends! 🚀
