# Sales Recording - Quick Answer

## When is a Rental Recorded as a Sale?

### ✅ Answer: When Status Changes to `completed`

A rental becomes a sale **automatically** when its status is updated to `completed`. This is the final status in the rental lifecycle when:
- Equipment has been returned
- No disputes exist
- Rental is successfully finished

## What Happens When Status → completed?

1. **Automatic Sale Creation**
   - `RentalSale` record is created via Django signal
   - No manual intervention needed

2. **Financial Calculations**
   - Platform Commission: **10%** of total revenue
   - Seller Payout: **90%** of total revenue
   - All fees included (subtotal + delivery + insurance + late fees + damage fees)

3. **Ready for Processing**
   - Sale appears in admin dashboard
   - Available via `/api/rentals/sales/` endpoint
   - Ready for payout processing

## Example

```
Rental: RENT-2025-001
Total Amount: AED 5,000

Status Changed: returning → completed ✅

Automatic Result:
- RentalSale created
- Platform Commission: AED 500 (10%)
- Seller Payout: AED 4,500 (90%)
- Payout Status: pending
```

## Financial Processing Flow

```
1. Rental completed
   ↓
2. Sale auto-created
   ↓
3. Admin reviews sale
   ↓
4. Process payout to seller
   ↓
5. Mark payout_status = 'completed'
   ↓
6. Financial records updated
```

## Quick Facts

- **Trigger Status:** `completed`
- **Commission Rate:** 10% (default)
- **Auto-Created:** Yes (via signal)
- **Prevents Duplicates:** Yes (OneToOne relationship)
- **Payout Tracking:** 5 statuses (pending, processing, completed, failed, on_hold)

## API Endpoints for Sales

```http
# List all sales
GET /api/rentals/sales/

# Get sales analytics
GET /api/rentals/sales_analytics/

# Filter by seller
GET /api/rentals/sales/?seller={id}

# Filter by payout status
GET /api/rentals/sales/?payout_status=pending

# Update payout status
PATCH /api/rentals/sales/{id}/
```

## Console Logs to Watch

```
📊 Rental RENT-2025-001 marked as COMPLETED - Sale will be recorded
✅ Sale created for rental RENT-2025-001
```

## For Full Details

See: `SALES_TRACKING_GUIDE.md` for complete documentation including:
- Detailed commission calculations
- Payout management workflows
- Seller dashboard integration
- Analytics endpoints
- Admin interface features
- Testing procedures

---

**Summary:** Rentals become sales automatically when status reaches `completed`. The system handles all calculations and record creation. You can then process payouts and generate financial reports using the admin interface or API endpoints.
