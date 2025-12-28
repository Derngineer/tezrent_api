# Ziina Payment Gateway Integration Guide

## Overview

Tezrent uses **Ziina** as the payment gateway for processing rental payments. This guide explains how to integrate the payment flow in the mobile app.

---

## API Endpoints

| Endpoint                                  | Method | Description                     |
| ----------------------------------------- | ------ | ------------------------------- |
| `/api/payments/ziina/initiate/`           | POST   | Create a payment session        |
| `/api/payments/ziina/verify/`             | POST   | Verify payment after redirect   |
| `/api/payments/ziina/status/{rental_id}/` | GET    | Get payment status for a rental |

---

## Payment Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    PAYMENT FLOW                              │
└─────────────────────────────────────────────────────────────┘

1. User selects a rental to pay
2. Mobile app calls POST /api/payments/ziina/initiate/
3. Backend returns redirect_url
4. App opens Ziina checkout in browser/webview
5. User completes payment on Ziina
6. Ziina redirects to success_url or cancel_url
7. App catches the redirect (deep link)
8. App calls POST /api/payments/ziina/verify/
9. Backend confirms payment and updates rental status
```

---

## 1. Initiate Payment

### Request

```http
POST /api/payments/ziina/initiate/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "rental_id": 123,
    "success_url": "tezrent://payment/success?rental_id=123",
    "cancel_url": "tezrent://payment/failed?rental_id=123"
}
```

### Parameters

| Field         | Type    | Required | Description                                                  |
| ------------- | ------- | -------- | ------------------------------------------------------------ |
| `rental_id`   | integer | Yes      | The rental to pay for                                        |
| `success_url` | string  | No       | URL to redirect on success (default: https://tezrent.com/en) |
| `cancel_url`  | string  | No       | URL to redirect on failure (default: https://tezrent.com/uz) |

### Response (Success - 200)

```json
{
  "success": true,
  "payment_id": "pi_abc123xyz",
  "redirect_url": "https://pay.ziina.com/checkout/abc123xyz",
  "rental_reference": "RNT-2024-001",
  "amount": 15000,
  "currency": "AED",
  "rental_payment_id": 45
}
```

### Response (Error - 400)

```json
{
  "error": "Rental cannot be paid in 'pending' status. Must be 'approved' or 'payment_pending'."
}
```

### Response (Error - 403)

```json
{
  "error": "You can only pay for your own rentals"
}
```

---

## 2. After Payment - Verify

After the user completes (or cancels) the payment and is redirected back to your app, verify the payment status:

### Request

```http
POST /api/payments/ziina/verify/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "payment_id": "pi_abc123xyz",
    "rental_id": 123
}
```

### Response (Payment Completed - 200)

```json
{
  "success": true,
  "payment_status": "completed",
  "rental_status": "confirmed",
  "rental_reference": "RNT-2024-001",
  "message": "Payment successful! Your rental is confirmed."
}
```

### Response (Payment Not Completed - 200)

```json
{
  "success": false,
  "payment_status": "requires_payment",
  "rental_status": "payment_pending",
  "message": "Payment not completed. Please add a payment method."
}
```

### Response (Payment Failed - 200)

```json
{
  "success": false,
  "payment_status": "failed",
  "rental_status": "payment_pending",
  "message": "Payment status: failed"
}
```

---

## 3. Check Payment Status

Get the current payment status for any rental:

### Request

```http
GET /api/payments/ziina/status/123/
Authorization: Bearer <access_token>
```

### Response (200)

```json
{
  "rental_id": 123,
  "rental_reference": "RNT-2024-001",
  "rental_status": "payment_pending",
  "rental_status_display": "Payment Pending",
  "total_amount": "150.00",
  "total_paid": "0.00",
  "remaining_amount": "150.00",
  "payments": [
    {
      "id": 45,
      "payment_type": "rental_fee",
      "payment_type_display": "Rental Fee",
      "amount": "150.00",
      "status": "pending",
      "status_display": "Pending",
      "method": "card",
      "gateway_reference": "pi_abc123xyz",
      "created_at": "2024-12-28T10:30:00Z",
      "completed_at": null
    }
  ],
  "is_fully_paid": false
}
```

---

## Mobile App Integration

### Option 1: Deep Links (Recommended)

Register a custom URL scheme (e.g., `tezrent://`) in your mobile app.

**iOS (Info.plist):**

```xml
<key>CFBundleURLTypes</key>
<array>
    <dict>
        <key>CFBundleURLSchemes</key>
        <array>
            <string>tezrent</string>
        </array>
    </dict>
</array>
```

**Android (AndroidManifest.xml):**

```xml
<intent-filter>
    <action android:name="android.intent.action.VIEW" />
    <category android:name="android.intent.category.DEFAULT" />
    <category android:name="android.intent.category.BROWSABLE" />
    <data android:scheme="tezrent" />
</intent-filter>
```

**Usage:**

```javascript
// Initiate payment
const response = await api.post("/api/payments/ziina/initiate/", {
  rental_id: 123,
  success_url: "tezrent://payment/success?rental_id=123",
  cancel_url: "tezrent://payment/failed?rental_id=123",
});

// Open Ziina checkout
await Linking.openURL(response.data.redirect_url);

// Handle deep link in your app
Linking.addEventListener("url", async (event) => {
  if (event.url.startsWith("tezrent://payment/success")) {
    // Extract payment_id from your stored state
    const verifyResponse = await api.post("/api/payments/ziina/verify/", {
      payment_id: storedPaymentId,
      rental_id: 123,
    });

    if (verifyResponse.data.success) {
      // Payment successful! Navigate to confirmation screen
    }
  } else if (event.url.startsWith("tezrent://payment/failed")) {
    // Payment failed/cancelled
  }
});
```

### Option 2: WebView with Intercept

Open Ziina in a WebView and intercept the redirect URL:

```javascript
<WebView
  source={{ uri: ziinaRedirectUrl }}
  onNavigationStateChange={(navState) => {
    if (
      navState.url.startsWith("tezrent://") ||
      navState.url.includes("tezrent.com/en") ||
      navState.url.includes("tezrent.com/uz")
    ) {
      // Close WebView and verify payment
      closeWebView();
      verifyPayment();
    }
  }}
/>
```

---

## Complete React Native Example

```javascript
import React, { useState } from "react";
import { View, Button, Alert, Linking } from "react-native";
import axios from "axios";

const PaymentScreen = ({ rental, accessToken }) => {
  const [paymentId, setPaymentId] = useState(null);
  const [loading, setLoading] = useState(false);

  const API_BASE =
    "https://tezrentapibackend-bsatbme3eqfkfnc3.canadacentral-01.azurewebsites.net";

  const initiatePayment = async () => {
    setLoading(true);
    try {
      const response = await axios.post(
        `${API_BASE}/api/payments/ziina/initiate/`,
        {
          rental_id: rental.id,
          success_url: `tezrent://payment/success?rental_id=${rental.id}`,
          cancel_url: `tezrent://payment/failed?rental_id=${rental.id}`,
        },
        {
          headers: { Authorization: `Bearer ${accessToken}` },
        }
      );

      if (response.data.success) {
        setPaymentId(response.data.payment_id);
        // Open Ziina checkout
        await Linking.openURL(response.data.redirect_url);
      } else {
        Alert.alert("Error", response.data.error);
      }
    } catch (error) {
      Alert.alert(
        "Error",
        error.response?.data?.error || "Failed to initiate payment"
      );
    }
    setLoading(false);
  };

  const verifyPayment = async (pid) => {
    try {
      const response = await axios.post(
        `${API_BASE}/api/payments/ziina/verify/`,
        {
          payment_id: pid || paymentId,
          rental_id: rental.id,
        },
        {
          headers: { Authorization: `Bearer ${accessToken}` },
        }
      );

      if (response.data.success) {
        Alert.alert("Success", response.data.message);
        // Navigate to confirmation screen
      } else {
        Alert.alert("Payment Incomplete", response.data.message);
      }
    } catch (error) {
      Alert.alert("Error", "Could not verify payment");
    }
  };

  // Set up deep link listener
  React.useEffect(() => {
    const handleDeepLink = (event) => {
      const url = event.url;
      if (url.includes("payment/success")) {
        verifyPayment();
      } else if (url.includes("payment/failed")) {
        Alert.alert("Payment Cancelled", "Your payment was not completed.");
      }
    };

    Linking.addEventListener("url", handleDeepLink);
    return () => Linking.removeEventListener("url", handleDeepLink);
  }, [paymentId]);

  return (
    <View>
      <Button
        title={loading ? "Processing..." : `Pay AED ${rental.total_amount}`}
        onPress={initiatePayment}
        disabled={loading}
      />
    </View>
  );
};

export default PaymentScreen;
```

---

## Rental Status After Payment

| Before Payment    | After Payment |
| ----------------- | ------------- |
| `approved`        | `confirmed`   |
| `payment_pending` | `confirmed`   |

Once `status = confirmed`, the rental is fully booked and paid!

---

## Testing

The API is currently in **TEST MODE** (`ZIINA_TEST_MODE=True`).

Use Ziina's test cards:

- **Success:** 4242 4242 4242 4242
- **Decline:** 4000 0000 0000 0002

Test redirect URLs:

- Success: `https://tezrent.com/en`
- Failed: `https://tezrent.com/uz`

---

## Error Codes

| HTTP Status | Error                                   | Description                  |
| ----------- | --------------------------------------- | ---------------------------- |
| 400         | `rental_id is required`                 | Missing rental_id in request |
| 400         | `Rental cannot be paid...`              | Rental not in payable status |
| 403         | `You can only pay for your own rentals` | User doesn't own this rental |
| 404         | `Rental not found`                      | Invalid rental_id            |
| 404         | `Payment record not found`              | Invalid payment_id in verify |
| 502         | `Payment gateway unavailable`           | Ziina API error              |

---

## Environment Variables

For production, set these in Azure:

```env
ZIINA_API_KEY=your_production_api_key_here
ZIINA_TEST_MODE=False
```

Get your API key from: https://dashboard.ziina.com/developers

---

## Summary

1. **Initiate:** `POST /api/payments/ziina/initiate/` → Get `redirect_url`
2. **Pay:** Open `redirect_url` in browser/webview
3. **Redirect:** App catches deep link after payment
4. **Verify:** `POST /api/payments/ziina/verify/` → Confirm status
5. **Done:** Rental status becomes `confirmed`

For questions, check the Ziina API docs: https://docs.ziina.com
