# Django Admin Guide - TezRent

## ✅ All Models Registered in Admin

All models across all apps are now fully registered in the Django admin interface with comprehensive management features.

---

## 🔐 Access the Admin

**URL:** `http://localhost:8000/admin/`

**To create a superuser:**
```bash
python manage.py createsuperuser
```

---

## 📦 Registered Apps & Models

### 1. **Accounts App** (`accounts/admin.py`)

#### User
- **Model:** Custom User model with email authentication
- **Features:**
  - List display: email, username, user_type, country, phone, status
  - Filters: user_type, country, is_active, is_staff, date_joined
  - Search: email, username, phone, name
  - Fieldsets: Personal info, location, permissions, dates
- **Actions:** Activate/deactivate users, manage permissions

#### CustomerProfile
- **Model:** Customer account profiles
- **Features:**
  - List display: email, name, city, rental count, total spent
  - Filters: city, country
  - Search: email, name, address
  - Readonly: rental_history_count, total_spent
- **Info shown:** Customer rental statistics, location details

#### CompanyProfile
- **Model:** Seller company profiles
- **Features:**
  - List display: company name, email, business type, city, phone, tax number
  - Filters: business_type, city, country
  - Search: company name, email, tax number, phone, address
  - Fieldsets: Company details, location, tax information

#### StaffProfile
- **Model:** Internal staff profiles
- **Features:**
  - List display: email, name, position, department, employee_id
  - Filters: department, position
  - Search: email, name, position, department, employee_id

---

### 2. **Equipment App** (`equipment/admin.py`)

#### Category
- **Model:** Equipment categories
- **Features:**
  - List display: name, slug, is_featured, display_order, equipment_count
  - Filters: is_featured
  - Search: name, description, slug
  - Prepopulated slug field
  - Inline image preview

#### Tag
- **Model:** Equipment tags for filtering
- **Features:**
  - List display: name, equipment_count
  - Search: name
  - Shows count of tagged equipment

#### Equipment
- **Model:** Main equipment listings
- **Features:**
  - List display: name, category, seller, daily_rate, location, status, units, promotional flags
  - Filters: category, status, country, city, featured, deals, tags
  - Search: name, description, model_number, seller name
  - Readonly: created_at, updated_at, discounted_rate, savings, deal_active
  - **Inlines:** EquipmentImage (max 7), EquipmentSpecification
  - Fieldsets: Basic info, seller, details, pricing, location, promotions, availability

#### EquipmentImage
- **Model:** Equipment photos (max 7 per equipment)
- **Features:**
  - List display: equipment, is_primary, display_order, caption, preview
  - Filters: is_primary
  - Editable: is_primary, display_order
  - Image preview in list

#### EquipmentSpecification
- **Model:** Technical specifications
- **Features:**
  - List display: equipment, name, value
  - Filters: name
  - Search: equipment, name, value

#### Banner
- **Model:** Homepage promotional banners
- **Features:**
  - List display: title, type, position, active status, order, click_count, view_count, preview
  - Filters: banner_type, position, is_active, dates
  - Editable: is_active, display_order
  - Readonly: click_count, view_count, created_at, updated_at, is_currently_active
  - Fieldsets: Basic info, images, CTA, targeting, display settings, statistics

---

### 3. **Rentals App** (`rentals/admin.py`)

#### Rental
- **Model:** Main rental orders
- **Features:**
  - List display: reference, equipment, customer, seller, status, dates, amount
  - Filters: status, created_at, start_date, end_date, pickup_required
  - Search: reference, equipment name, customer email, seller name
  - Readonly: reference, dates, calculated totals
  - **Inlines:** RentalStatusUpdate, RentalImage, RentalPayment
  - Fieldsets: Rental info, dates, delivery, contact, financial, notes, timestamps

#### RentalStatusUpdate
- **Model:** Status change history
- **Features:**
  - List display: rental, old_status, new_status, updated_by, created_at
  - Filters: new_status, created_at, is_visible_to_customer
  - Search: rental reference, notes
  - Track who changed status and when

#### RentalImage
- **Model:** Rental-related images (before/after, damage, etc.)
- **Features:**
  - List display: rental, image_type, uploaded_by, created_at
  - Filters: image_type, created_at
  - Search: rental reference, description

#### RentalReview
- **Model:** Customer reviews and ratings
- **Features:**
  - List display: rental, customer, overall_rating, would_recommend, created_at
  - Filters: overall_rating, would_recommend, created_at
  - Search: rental reference, customer email, review text
  - Fieldsets: Review info, ratings (equipment, service, delivery), content

#### RentalPayment
- **Model:** Payment transactions
- **Features:**
  - List display: transaction_id, rental, payment_type, amount, status, created_at
  - Filters: payment_type, payment_status, payment_method, created_at
  - Search: transaction_id, rental reference, gateway_reference
  - Readonly: created_at, completed_at, transaction_id

#### RentalDocument
- **Model:** Rental contracts and documents
- **Features:**
  - List display: rental, document_type, title, uploaded_by, is_signed, created_at
  - Filters: document_type, is_signed, created_at
  - Search: rental reference, title
  - Readonly: created_at, signed_at

---

### 4. **Notifications App** (`notifications/admin.py`)

#### Notification
- **Model:** User notifications
- **Features:**
  - List display: user email, notification_type, title, is_read, sent_via, created_at
  - Filters: notification_type, is_read, sent_via_push, sent_via_email, created_at
  - Search: user email, title, message
  - Readonly: created_at, read_at
  - Fieldsets: Recipient, notification details, status, references, metadata

#### PushNotificationToken
- **Model:** Device push notification tokens
- **Features:**
  - List display: user email, device_name, platform, is_active, created_at
  - Filters: platform, is_active, created_at
  - Search: user email, device_name, token
  - Actions: Activate/deactivate tokens

#### NotificationPreference
- **Model:** User notification settings
- **Features:**
  - List display: user email, push_enabled, email_enabled, SMS_enabled
  - Filters: All notification type preferences
  - Search: user email
  - Organized fieldsets by notification category

---

### 5. **Favorites App** (`favorites/admin.py`)

#### Favorite
- **Model:** User favorite equipment
- **Features:**
  - List display: customer email, equipment name, favorited_at, notify preferences
  - Filters: notify_on_availability, notify_on_price_drop, notify_on_deals, favorited_at
  - Search: customer email, equipment name, notes
  - Readonly: favorited_at
  - Fieldsets: Customer & equipment, preferences, notes, rental preferences

#### FavoriteCollection
- **Model:** Custom wishlists
- **Features:**
  - List display: customer email, collection name, item_count, is_public, created_at
  - Filters: is_public, created_at
  - Search: customer email, name, description
  - Filter_horizontal: equipment (many-to-many)
  - Fieldsets: Customer, collection details, display settings, equipment

#### RecentlyViewed
- **Model:** User viewing history
- **Features:**
  - List display: customer email, equipment name, view_count, last_viewed, viewed_from
  - Filters: viewed_from, first_viewed, last_viewed
  - Search: customer email, equipment name
  - Readonly: first_viewed, last_viewed, view_count

---

### 6. **Payments App** (`payments/admin.py`)
**Status:** Placeholder - No models created yet
- Expected: Payment, PaymentMethod, Transaction, Refund, Invoice

### 7. **CRM App** (`crm/admin.py`)
**Status:** Placeholder - No models created yet
- Expected: Lead, CustomerInteraction, SalesOpportunity, SupportTicket, CustomerNote

---

## 🎨 Admin Customization

### Site Branding
- **Site Header:** "TezRent Administration"
- **Site Title:** "TezRent Admin Portal"
- **Index Title:** "Welcome to TezRent Equipment Rental Management"

### Features Across All Admins
- ✅ Search functionality
- ✅ Filters by key fields
- ✅ Date-based filtering
- ✅ Readonly fields for calculated/automated values
- ✅ Organized fieldsets with collapsible sections
- ✅ Related object selection with select_related for performance
- ✅ Custom display methods with sorting
- ✅ Inline editing for related models
- ✅ Image previews where applicable
- ✅ Bulk actions support

---

## 📊 Admin Dashboard Sections

When you log in to `/admin/`, you'll see:

1. **ACCOUNTS**
   - Users
   - Customer Profiles
   - Company Profiles
   - Staff Profiles

2. **EQUIPMENT**
   - Categories
   - Tags
   - Equipment
   - Equipment Images
   - Equipment Specifications
   - Banners

3. **RENTALS**
   - Rentals
   - Rental Status Updates
   - Rental Images
   - Rental Reviews
   - Rental Payments
   - Rental Documents

4. **NOTIFICATIONS**
   - Notifications
   - Push Notification Tokens
   - Notification Preferences

5. **FAVORITES**
   - Favorites
   - Favorite Collections
   - Recently Viewed

6. **AUTHENTICATION AND AUTHORIZATION** (Django built-in)
   - Groups
   - Permissions

---

## 🔍 Common Admin Tasks

### Manage Users
1. Go to **Accounts > Users**
2. Click "Add User" or select existing user
3. Edit user type, permissions, and profile

### Manage Equipment
1. Go to **Equipment > Equipment**
2. Add new equipment with up to 7 images
3. Set promotional flags (featured, new listing, today's deal)
4. Add specifications inline

### Monitor Rentals
1. Go to **Rentals > Rentals**
2. Filter by status, date range, customer
3. View inline status updates and payments
4. Track rental lifecycle

### Send Notifications
1. Go to **Notifications > Notifications**
2. Create notification for specific user
3. Choose notification type and channels
4. Add navigation params for React Native deep linking

### Manage Favorites
1. Go to **Favorites > Favorites**
2. View what equipment users are liking
3. See notification preferences for deals/availability

### Manage Banners
1. Go to **Equipment > Banners**
2. Add desktop and mobile images
3. Set position, type, and scheduling
4. Track clicks and views

---

## 🚀 Quick Actions

### Create Superuser
```bash
python manage.py createsuperuser
```

### Access Admin
```
http://localhost:8000/admin/
```

### Reset Admin Password
```bash
python manage.py changepassword <username>
```

---

## 📝 Notes

- All models have proper `__str__()` methods for readable display
- Related objects use select_related/prefetch_related for performance
- Image fields show previews in list view
- Calculated fields are readonly
- Timestamps are readonly and auto-managed
- Inline editing available for related models (images, specifications, status updates, payments)
- Search fields are optimized for common queries
- List filters match the most useful query patterns

---

**Everything is ready to manage through the Django admin! 🎉**
