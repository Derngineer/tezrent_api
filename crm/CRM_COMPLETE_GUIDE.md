# TezRent CRM System - Complete Documentation

## 📋 Table of Contents
1. [Overview](#overview)
2. [Who Uses the CRM](#who-uses-the-crm)
3. [User Flows](#user-flows)
4. [API Endpoints](#api-endpoints)
5. [Models & Database](#models--database)
6. [Permissions & Access Control](#permissions--access-control)
7. [Automation & Signals](#automation--signals)
8. [Mobile App Integration](#mobile-app-integration)
9. [Admin Interface](#admin-interface)
10. [Setup & Configuration](#setup--configuration)

---

## 🎯 Overview

The TezRent CRM (Customer Relationship Management) system is a comprehensive solution for managing:
- **Leads**: Potential customers who show interest
- **Sales Opportunities**: Qualified leads in the sales pipeline
- **Customer Interactions**: Log of all communications
- **Support Tickets**: Customer service and issue tracking
- **Customer Notes**: Internal notes about customer preferences
- **Customer Segments**: Group customers for targeted campaigns

### Key Features
✅ Multi-user access (Staff, Sellers, Customers)
✅ Role-based permissions
✅ Automated lead/opportunity creation
✅ Support ticket system with comments
✅ Sales pipeline tracking
✅ Activity logging
✅ Mobile-optimized APIs
✅ Real-time notifications

---

## 👥 Who Uses the CRM

### 1. **Staff Users (Internal Sales/Support Team)**
- **Access**: Django Admin + Mobile/Web Staff App
- **Permissions**: Full access to all CRM data
- **Use Cases**:
  - Manage all leads and opportunities
  - Assign work to team members
  - Handle support tickets
  - View analytics and reports
  - Add customer notes
  - Segment customers

### 2. **Seller Users (Company Staff)**
- **Access**: Seller Portal (Web/Mobile App)
- **Permissions**: View/edit only their company's data
- **Use Cases**:
  - View leads assigned to their company
  - Manage opportunities for their equipment
  - Respond to support tickets for their rentals
  - Add notes about customers who rented from them
  - Track sales performance

### 3. **Customer Users**
- **Access**: Customer App (React Native)
- **Permissions**: View only their own data
- **Use Cases**:
  - Create support tickets
  - View ticket status and comments
  - Respond to support queries
  - Submit contact forms (creates leads)

---

## 🔄 User Flows

### **STAFF: Managing Leads**

```
1. Staff opens CRM → Leads section (Django Admin or Mobile App)
2. Views all leads or filters by status/source/assigned person
3. Clicks "Add Lead" to create new lead OR lead is auto-created
4. Fills form:
   - Title: "Interested in excavator rental"
   - Contact: Name, email, phone
   - Source: Web form / Phone / Referral / Automation
   - Status: New → Contacted → Qualified
   - Company: (optional) Link to seller if relevant
   - Customer: (optional) Link if customer already exists
   - Assigned to: Select staff member
   - Notes: "Customer needs equipment for 3-month project"
   - Estimated Value: 50,000 AED
5. Saves lead
6. Adds interactions:
   - "Phone call - discussed requirements - 15 mins"
   - "Email - sent pricing proposal"
7. Qualifies lead → Converts to Opportunity
```

**API Endpoints Used:**
```
POST   /api/crm/leads/                    # Create lead
GET    /api/crm/leads/                    # List all leads
GET    /api/crm/leads/{id}/               # View lead details
PUT    /api/crm/leads/{id}/               # Update lead
POST   /api/crm/leads/{id}/mark_contacted/         # Mark as contacted
POST   /api/crm/leads/{id}/convert_to_opportunity/ # Convert to opportunity
POST   /api/crm/interactions/             # Add interaction/note
```

---

### **SELLER: Viewing Company Leads**

```
1. Seller logs into portal → "My Leads" tab
2. Sees only leads where company = their CompanyProfile
3. Filters by status: "New", "Contacted", "Qualified"
4. Clicks on a lead to view details
5. Adds a note: "Customer called asking about delivery options"
6. Updates status to "Contacted"
7. Cannot see leads from other companies (permission denied)
```

**API Endpoints Used:**
```
GET    /api/crm/leads/?company={seller_company_id}   # Filtered leads
GET    /api/crm/leads/my_leads/                      # Assigned to current user
POST   /api/crm/interactions/                        # Add interaction
PUT    /api/crm/leads/{id}/                          # Update lead
```

---

### **STAFF: Managing Sales Opportunities**

```
1. Staff opens Opportunities section
2. Views sales pipeline:
   - Prospecting: 5 opportunities, $150,000 value
   - Proposal: 3 opportunities, $80,000 value
   - Negotiation: 2 opportunities, $120,000 value
   - Closed Won: 1 opportunity, $50,000 value
3. Clicks on opportunity to view details
4. Updates stage: Proposal → Negotiation
5. Updates probability: 50% → 75%
6. Adds interaction: "Meeting - negotiated pricing - customer agreed"
7. Marks opportunity as WON with actual amount: $45,000
```

**API Endpoints Used:**
```
GET    /api/crm/opportunities/            # List opportunities
GET    /api/crm/opportunities/pipeline/   # Pipeline summary
POST   /api/crm/opportunities/            # Create opportunity
PUT    /api/crm/opportunities/{id}/       # Update opportunity
POST   /api/crm/opportunities/{id}/mark_won/   # Mark as won
POST   /api/crm/opportunities/{id}/mark_lost/  # Mark as lost
```

---

### **CUSTOMER: Creating Support Ticket**

```
1. Customer has issue → opens "Help" in mobile app
2. Clicks "Create Ticket"
3. Fills form:
   - Related Rental: Select from dropdown (rentals they have)
   - Title: "Equipment not working properly"
   - Description: "The excavator engine stops after 30 minutes"
   - Category: Equipment Problem
   - Priority: High
   - Attachments: Upload photos of issue
4. Submits ticket
5. Ticket is created with auto-generated number: TKT-20251021-0001
6. Notification sent to seller and support staff
7. Customer can:
   - View ticket status
   - Add comments (public)
   - Upload more photos
   - Get notifications on updates
```

**API Endpoints Used:**
```
POST   /api/crm/tickets/                  # Create ticket
GET    /api/crm/tickets/my_tickets/       # View own tickets
POST   /api/crm/tickets/{id}/add_comment/ # Add comment
GET    /api/crm/tickets/{id}/             # View ticket details
```

---

### **STAFF/SELLER: Responding to Support Ticket**

```
1. Staff/Seller gets notification: "New ticket TKT-20251021-0001"
2. Opens ticket in admin/portal
3. Views:
   - Customer details
   - Related rental
   - Equipment involved
   - Customer's description and photos
4. Adds INTERNAL note (only staff/seller can see):
   "Equipment has known issue with fuel filter. Need to send technician."
5. Adds PUBLIC comment (customer can see):
   "We've identified the issue. Our technician will visit you tomorrow at 10 AM."
6. Updates status: Open → In Progress
7. Customer gets notification about the update
8. After technician visit, adds another comment:
   "Issue resolved. Fuel filter replaced. Equipment working normally."
9. Marks ticket as Resolved
10. Customer confirms and ticket is Closed
```

**API Endpoints Used:**
```
GET    /api/crm/tickets/?assigned_to_me=true    # My assigned tickets
GET    /api/crm/tickets/{id}/                   # View ticket
POST   /api/crm/tickets/{id}/add_comment/       # Add comment
       Body: { "comment": "text", "is_internal": true/false, "attachment": file }
POST   /api/crm/tickets/{id}/mark_resolved/     # Resolve ticket
       Body: { "resolution": "Fuel filter replaced" }
POST   /api/crm/tickets/{id}/mark_closed/       # Close ticket
```

---

### **SELLER: Adding Customer Notes**

```
1. Seller views customer profile who rented from them
2. Clicks "Add Note"
3. Fills:
   - Title: "VIP Customer"
   - Note: "Customer rents frequently. Prefers excavators. Always pays on time. Good relationship."
   - Important: ✓ (flag as important)
   - Tags: "VIP, repeat customer, excavator preference"
4. Saves note
5. Note is visible to:
   - All staff
   - Seller who created it
   - Other sellers (if allowed by permissions)
6. NOT visible to customer
```

**API Endpoints Used:**
```
POST   /api/crm/customer-notes/           # Create note
GET    /api/crm/customer-notes/?customer_id={id}  # View customer notes
GET    /api/crm/customer-notes/?important=true    # Important notes only
```

---

## 🔗 API Endpoints

### **Leads**
```
GET    /api/crm/leads/                    # List leads
POST   /api/crm/leads/                    # Create lead
GET    /api/crm/leads/{id}/               # Lead detail
PUT    /api/crm/leads/{id}/               # Update lead
DELETE /api/crm/leads/{id}/               # Delete lead
POST   /api/crm/leads/{id}/mark_contacted/         # Mark contacted
POST   /api/crm/leads/{id}/convert_to_opportunity/ # Convert to opportunity
GET    /api/crm/leads/my_leads/                    # Assigned to me

Query Parameters:
- ?status=new|contacted|qualified|converted|disqualified|lost
- ?source=web_form|phone|email|referral|automation|seller_input
- ?assigned_to_me=true
- ?mobile=true (returns lightweight mobile serializer)
```

### **Sales Opportunities**
```
GET    /api/crm/opportunities/            # List opportunities
POST   /api/crm/opportunities/            # Create opportunity
GET    /api/crm/opportunities/{id}/       # Opportunity detail
PUT    /api/crm/opportunities/{id}/       # Update opportunity
DELETE /api/crm/opportunities/{id}/       # Delete opportunity
POST   /api/crm/opportunities/{id}/mark_won/   # Mark as won
       Body: { "actual_amount": 45000 }
POST   /api/crm/opportunities/{id}/mark_lost/  # Mark as lost
       Body: { "reason": "Customer chose competitor" }
GET    /api/crm/opportunities/pipeline/   # Pipeline summary

Query Parameters:
- ?stage=prospecting|qualification|proposal|negotiation|closed_won|closed_lost
- ?assigned_to_me=true
```

### **Customer Interactions**
```
GET    /api/crm/interactions/             # List interactions
POST   /api/crm/interactions/             # Create interaction
GET    /api/crm/interactions/{id}/        # Interaction detail
PUT    /api/crm/interactions/{id}/        # Update interaction
DELETE /api/crm/interactions/{id}/        # Delete interaction

Query Parameters:
- ?lead_id={id}
- ?opportunity_id={id}
- ?customer_id={id}
```

### **Support Tickets**
```
GET    /api/crm/tickets/                  # List tickets
POST   /api/crm/tickets/                  # Create ticket
GET    /api/crm/tickets/{id}/             # Ticket detail
PUT    /api/crm/tickets/{id}/             # Update ticket
DELETE /api/crm/tickets/{id}/             # Delete ticket
POST   /api/crm/tickets/{id}/add_comment/ # Add comment
       Body: { "comment": "text", "is_internal": false, "attachment": file }
POST   /api/crm/tickets/{id}/mark_resolved/     # Resolve
       Body: { "resolution": "text" }
POST   /api/crm/tickets/{id}/mark_closed/       # Close
GET    /api/crm/tickets/my_tickets/             # Customer's tickets

Query Parameters:
- ?status=open|in_progress|waiting_customer|waiting_seller|resolved|closed
- ?priority=low|medium|high|urgent
- ?category=general|technical|billing|equipment|delivery|damage|complaint|refund
- ?assigned_to_me=true
- ?mobile=true
```

### **Ticket Comments**
```
GET    /api/crm/ticket-comments/          # List comments
POST   /api/crm/ticket-comments/          # Create comment
GET    /api/crm/ticket-comments/{id}/     # Comment detail
PUT    /api/crm/ticket-comments/{id}/     # Update comment
DELETE /api/crm/ticket-comments/{id}/     # Delete comment

Query Parameters:
- ?ticket_id={id}
```

### **Customer Notes**
```
GET    /api/crm/customer-notes/           # List notes
POST   /api/crm/customer-notes/           # Create note
GET    /api/crm/customer-notes/{id}/      # Note detail
PUT    /api/crm/customer-notes/{id}/      # Update note
DELETE /api/crm/customer-notes/{id}/      # Delete note

Query Parameters:
- ?customer_id={id}
- ?important=true
```

### **Customer Segments** (Staff Only)
```
GET    /api/crm/customer-segments/        # List segments
POST   /api/crm/customer-segments/        # Create segment
GET    /api/crm/customer-segments/{id}/   # Segment detail
PUT    /api/crm/customer-segments/{id}/   # Update segment
DELETE /api/crm/customer-segments/{id}/   # Delete segment
```

---

## 🗄️ Models & Database

### **Lead**
Purpose: Track potential customers

Fields:
- `title`: Brief description
- `contact_name`, `contact_email`, `contact_phone`: Contact info
- `company_name`: If lead is from a business
- `source`: Where lead came from (web_form, phone, referral, automation, etc.)
- `status`: New → Contacted → Qualified → Converted/Disqualified/Lost
- `company`: FK to CompanyProfile (seller) - optional
- `customer`: FK to CustomerProfile - optional
- `assigned_to`: FK to User (staff) - optional
- `notes`: Internal notes
- `estimated_value`: Potential revenue
- `expected_close_date`: When we expect to close
- `metadata`: JSON field for extra data (UTM params, form fields, etc.)
- `created_by`, `created_at`, `updated_at`, `last_contacted_at`, `converted_at`

Methods:
- `mark_contacted()`: Update status and timestamp
- `convert_to_opportunity()`: Create opportunity from qualified lead

### **SalesOpportunity**
Purpose: Track qualified leads through sales pipeline

Fields:
- `title`, `description`: What is this opportunity
- `lead`: FK to Lead (if converted) - optional
- `contact_name`, `contact_email`, `contact_phone`: Contact info
- `company`: FK to CompanyProfile - optional
- `customer`: FK to CustomerProfile - optional
- `equipment`: FK to Equipment (specific equipment being sold) - optional
- `assigned_to`: FK to User (staff) - optional
- `stage`: Prospecting → Qualification → Proposal → Negotiation → Closed Won/Lost
- `probability`: 0-100% chance of winning
- `estimated_amount`: Expected revenue
- `actual_amount`: Actual revenue if won
- `expected_close_date`, `actual_close_date`
- `notes`, `loss_reason`
- `created_by`, `created_at`, `updated_at`

Methods:
- `weighted_value`: estimated_amount × probability
- `mark_won(actual_amount)`: Close as won
- `mark_lost(reason)`: Close as lost

### **CustomerInteraction**
Purpose: Log all activities and communications

Fields:
- `interaction_type`: Call, Email, Meeting, Note, Task, SMS, WhatsApp, Demo, Other
- `related_to_lead`: FK to Lead - optional
- `related_to_opportunity`: FK to Opportunity - optional
- `related_to_customer`: FK to CustomerProfile - optional
- `related_to_rental`: FK to Rental - optional
- `subject`: Brief description
- `description`: Full details
- `outcome`: Result of interaction
- `duration_minutes`: For calls/meetings
- `next_action`: Follow-up needed
- `performed_by`: FK to User
- `performed_at`: When it happened
- `created_at`

### **SupportTicket**
Purpose: Handle customer support requests

Fields:
- `ticket_number`: Auto-generated (TKT-YYYYMMDD-XXXX)
- `title`, `description`: What's the issue
- `category`: General, Technical, Billing, Equipment, Delivery, Damage, Complaint, Refund, Other
- `priority`: Low, Medium, High, Urgent
- `status`: Open → In Progress → Waiting Customer/Seller → Resolved → Closed
- `customer`: FK to CustomerProfile (required)
- `company`: FK to CompanyProfile (seller involved) - optional
- `related_rental`: FK to Rental - optional
- `related_equipment`: FK to Equipment - optional
- `assigned_to`: FK to User (staff) - optional
- `internal_notes`: Staff-only notes
- `resolution`: How it was resolved
- `created_by`, `created_at`, `updated_at`, `resolved_at`, `closed_at`

Methods:
- `save()`: Auto-generate ticket number
- `mark_resolved(resolution_text)`: Resolve ticket
- `mark_closed()`: Close ticket

### **TicketComment**
Purpose: Thread of messages on tickets

Fields:
- `ticket`: FK to SupportTicket
- `comment`: Message text
- `is_internal`: Boolean (if True, only staff/seller can see)
- `attachment`: File upload (photos, documents)
- `created_by`: FK to User
- `created_at`

### **CustomerNote**
Purpose: Internal notes about customers

Fields:
- `customer`: FK to CustomerProfile
- `title`, `note`: Note content
- `is_important`: Flag important notes
- `tags`: Comma-separated tags (VIP, repeat customer, etc.)
- `created_by`: FK to User
- `company`: FK to CompanyProfile (seller who added) - optional
- `created_at`, `updated_at`

### **CustomerSegment**
Purpose: Group customers for marketing

Fields:
- `name`, `description`: Segment info
- `criteria`: JSON field with segmentation rules
- `customers`: ManyToMany to CustomerProfile
- `created_at`, `updated_at`

---

## 🔐 Permissions & Access Control

### Permission Classes

**IsStaffUser**
- Only authenticated staff users
- Used for: Full CRM admin access

**IsSellerOwner**
- Authenticated users with CompanyProfile
- Can only access records where `company = their_company`
- Used for: Seller portal access

**IsCustomerOwner**
- Authenticated users with CustomerProfile
- Can only access their own records
- Used for: Customer ticket access

**IsStaffOrSellerOwner**
- Staff OR sellers (for their own company)
- Used for: Leads, Opportunities, Customer Notes

**IsStaffOrCustomerOwner**
- Staff OR customers (for their own data)
- Used for: Support Tickets

### Access Matrix

| Resource | Staff | Seller (Own Company) | Customer (Own Data) | Anonymous |
|----------|-------|----------------------|---------------------|-----------|
| **Leads** |
| List all | ✅ | ✅ (filtered) | ❌ | ❌ |
| Create | ✅ | ✅ | Via contact form | ❌ |
| View detail | ✅ | ✅ (own company) | ❌ | ❌ |
| Update | ✅ | ✅ (own company) | ❌ | ❌ |
| Delete | ✅ | ❌ | ❌ | ❌ |
| **Opportunities** |
| List all | ✅ | ✅ (filtered) | ❌ | ❌ |
| Create | ✅ | ✅ | ❌ | ❌ |
| View detail | ✅ | ✅ (own company) | ❌ | ❌ |
| Update | ✅ | ✅ (own company) | ❌ | ❌ |
| Delete | ✅ | ❌ | ❌ | ❌ |
| Mark won/lost | ✅ | ✅ (own company) | ❌ | ❌ |
| **Interactions** |
| List all | ✅ | ❌ | ❌ | ❌ |
| Create | ✅ | ❌ | ❌ | ❌ |
| View detail | ✅ | ❌ | ❌ | ❌ |
| **Support Tickets** |
| List all | ✅ | ✅ (filtered) | ✅ (own only) | ❌ |
| Create | ✅ | ✅ | ✅ | ❌ |
| View detail | ✅ | ✅ (own company) | ✅ (own only) | ❌ |
| Update | ✅ | ✅ (own company) | ❌ | ❌ |
| Add public comment | ✅ | ✅ | ✅ | ❌ |
| Add internal comment | ✅ | ✅ | ❌ | ❌ |
| Resolve/close | ✅ | ✅ (own company) | ❌ | ❌ |
| View internal notes | ✅ | ✅ (own company) | ❌ | ❌ |
| **Customer Notes** |
| List all | ✅ | ✅ (filtered) | ❌ | ❌ |
| Create | ✅ | ✅ | ❌ | ❌ |
| View detail | ✅ | ✅ (own company) | ❌ | ❌ |
| Update | ✅ | ✅ (own) | ❌ | ❌ |
| Delete | ✅ | ❌ | ❌ | ❌ |
| **Customer Segments** |
| Full CRUD | ✅ | ❌ | ❌ | ❌ |

---

## ⚙️ Automation & Signals

The CRM system includes several automated triggers:

### **1. Large Rental → Opportunity**
**Trigger**: Rental created with total_amount >= 10,000 OR duration >= 30 days
**Action**: Automatically creates SalesOpportunity (marked as won)
```python
# High-value rental completed
# Auto-create opportunity to track revenue
stage='closed_won', probability=100
```

### **2. Rental Dispute → Support Ticket**
**Trigger**: Rental status changes to 'dispute'
**Action**: Auto-creates high-priority SupportTicket
```python
# Rental enters dispute
# Ticket created with category='complaint', priority='high'
# Staff gets notification
```

### **3. Repeated Favorites → Lead**
**Trigger**: Customer favorites 5+ items in 7 days
**Action**: Creates lead with source='automation', status='qualified'
```python
# High-intent customer signal
# Auto-create lead to follow up
```

### **4. Ticket Comment → Notification**
**Trigger**: TicketComment created (public comment)
**Action**: Sends notification to customer or assigned staff
```python
# Customer commented → notify assigned staff
# Staff commented → notify customer
```

### **5. Ticket Status Change → Notification**
**Trigger**: SupportTicket status updated
**Action**: Notifies customer of status change

To disable automation signals, comment them out in `crm/signals.py`.

---

## 📱 Mobile App Integration

### React Native - Lead Form Example
```javascript
import React, { useState } from 'react';
import { View, TextInput, Button, Picker } from 'react-native';

const LeadForm = () => {
  const [formData, setFormData] = useState({
    title: '',
    contact_name: '',
    contact_email: '',
    contact_phone: '',
    source: 'web_form',
    notes: ''
  });
  
  const submitLead = async () => {
    const response = await fetch('/api/crm/leads/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(formData)
    });
    
    const lead = await response.json();
    console.log('Lead created:', lead.id);
  };
  
  return (
    <View>
      <TextInput
        placeholder="Title"
        value={formData.title}
        onChangeText={(text) => setFormData({...formData, title: text})}
      />
      {/* More fields... */}
      <Button title="Create Lead" onPress={submitLead} />
    </View>
  );
};
```

### React Native - Support Ticket Screen
```javascript
const CreateTicketScreen = ({ navigation }) => {
  const [ticket, setTicket] = useState({
    title: '',
    description: '',
    category: 'general',
    priority: 'medium',
    related_rental: null
  });
  
  const submitTicket = async () => {
    const response = await fetch('/api/crm/tickets/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(ticket)
    });
    
    const created = await response.json();
    
    // Navigate to ticket detail
    navigation.navigate('TicketDetail', { ticketId: created.id });
  };
  
  return (
    <View>
      <Picker
        selectedValue={ticket.related_rental}
        onValueChange={(value) => setTicket({...ticket, related_rental: value})}
      >
        <Picker.Item label="Select Rental (Optional)" value={null} />
        {userRentals.map(rental => (
          <Picker.Item 
            key={rental.id} 
            label={rental.rental_reference} 
            value={rental.id} 
          />
        ))}
      </Picker>
      
      <TextInput
        placeholder="Subject"
        value={ticket.title}
        onChangeText={(text) => setTicket({...ticket, title: text})}
      />
      
      <TextInput
        placeholder="Description"
        multiline
        numberOfLines={5}
        value={ticket.description}
        onChangeText={(text) => setTicket({...ticket, description: text})}
      />
      
      <Button title="Submit Ticket" onPress={submitTicket} />
    </View>
  );
};
```

### React Native - Ticket Comments (Chat Interface)
```javascript
const TicketDetailScreen = ({ route }) => {
  const { ticketId } = route.params;
  const [ticket, setTicket] = useState(null);
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');
  
  useEffect(() => {
    fetchTicket();
  }, []);
  
  const fetchTicket = async () => {
    const response = await fetch(`/api/crm/tickets/${ticketId}/`, {
      headers: { 'Authorization': `Bearer ${accessToken}` }
    });
    const data = await response.json();
    setTicket(data);
    setComments(data.public_comments || []);
  };
  
  const addComment = async () => {
    const response = await fetch(`/api/crm/tickets/${ticketId}/add_comment/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ comment: newComment, is_internal: false })
    });
    
    const comment = await response.json();
    setComments([...comments, comment]);
    setNewComment('');
  };
  
  return (
    <View>
      <Text>Ticket: {ticket?.ticket_number}</Text>
      <Text>Status: {ticket?.status}</Text>
      
      <FlatList
        data={comments}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => (
          <View style={styles.comment}>
            <Text style={styles.author}>{item.created_by_name}</Text>
            <Text>{item.comment}</Text>
            <Text style={styles.time}>{item.created_at}</Text>
          </View>
        )}
      />
      
      <TextInput
        placeholder="Add a comment..."
        value={newComment}
        onChangeText={setNewComment}
      />
      <Button title="Send" onPress={addComment} />
    </View>
  );
};
```

---

## 🖥️ Admin Interface

All CRM models are registered in Django Admin with:
- List display with key fields
- Search functionality
- Filters (status, priority, date, assigned to)
- Inline editing (interactions within leads, comments within tickets)
- Bulk actions (mark as contacted, assign to me, etc.)
- Readonly fields for calculated values

Access: `http://localhost:8000/admin/crm/`

Admin sections:
- Leads
- Sales Opportunities
- Customer Interactions
- Support Tickets
- Ticket Comments
- Customer Notes
- Customer Segments

---

## 🚀 Setup & Configuration

### 1. Install Dependencies
Already included in project requirements.

### 2. Run Migrations
```bash
python manage.py makemigrations crm
python manage.py migrate crm
```

### 3. Create Test Data (Optional)
```bash
python manage.py shell
```

```python
from crm.models import Lead
from accounts.models import User

# Create a lead
staff_user = User.objects.filter(is_staff=True).first()
Lead.objects.create(
    title="Test Lead",
    contact_name="John Doe",
    contact_email="john@example.com",
    source='web_form',
    created_by=staff_user
)
```

### 4. Test API
```bash
# Get JWT token
curl -X POST http://localhost:8000/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"your@email.com","password":"yourpassword"}'

# List leads (staff only)
curl -X GET http://localhost:8000/api/crm/leads/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Create ticket (customer)
curl -X POST http://localhost:8000/api/crm/tickets/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Ticket",
    "description": "This is a test",
    "category": "general",
    "priority": "medium"
  }'
```

### 5. Configure Signals (Optional)
Signals are auto-loaded via `crm/apps.py ready()` method.
To disable specific signals, edit `crm/signals.py`.

---

## 📊 Usage Examples

### Staff Dashboard View
```python
# Get pipeline summary
GET /api/crm/opportunities/pipeline/

Response:
{
  "prospecting": {"count": 5, "total_value": 150000, "weighted_value": 15000},
  "qualification": {"count": 3, "total_value": 80000, "weighted_value": 20000},
  "proposal": {"count": 2, "total_value": 120000, "weighted_value": 60000},
  "negotiation": {"count": 1, "total_value": 50000, "weighted_value": 45000},
  "closed_won": {"count": 10, "total_value": 500000, "weighted_value": 500000},
  "closed_lost": {"count": 5, "total_value": 200000, "weighted_value": 0}
}
```

### Seller Portal View
```python
# Get my company's leads
GET /api/crm/leads/?company={company_id}

# Get my assigned opportunities
GET /api/crm/opportunities/?assigned_to_me=true
```

### Customer App View
```python
# Get my tickets
GET /api/crm/tickets/my_tickets/

# Create ticket
POST /api/crm/tickets/
Body: {
  "title": "Equipment issue",
  "description": "...",
  "category": "equipment",
  "priority": "high",
  "related_rental": 123
}
```

---

## 🎯 Best Practices

1. **Always assign leads**: Unassigned leads get lost
2. **Update lead status regularly**: Keep pipeline accurate
3. **Add interactions**: Document all customer communications
4. **Use internal notes**: Keep sensitive info private
5. **Respond to tickets quickly**: Customer satisfaction
6. **Tag customer notes**: Makes searching easier
7. **Segment customers**: Better targeted campaigns

---

## 🔧 Troubleshooting

**Issue**: Can't see all leads as seller
- **Cause**: Permissions filter by company
- **Solution**: Sellers only see their company's leads (by design)

**Issue**: Customer can see internal notes
- **Cause**: Using wrong serializer
- **Solution**: Customer endpoints use SupportTicketCustomerSerializer (hides internal notes)

**Issue**: Signals not firing
- **Cause**: Signals not loaded
- **Solution**: Check crm/apps.py has ready() method importing signals

**Issue**: Can't create lead
- **Cause**: Missing required fields
- **Solution**: At minimum provide: title, contact_name, contact_email

---

## 📄 Files Reference

- `crm/models.py` - Database models
- `crm/admin.py` - Django admin registration
- `crm/serializers.py` - REST API serializers
- `crm/views.py` - API viewsets
- `crm/permissions.py` - Access control
- `crm/signals.py` - Automation triggers
- `crm/urls.py` - API routing
- `crm/apps.py` - App configuration

---

**Documentation complete! The TezRent CRM system is fully operational.** 🎉
