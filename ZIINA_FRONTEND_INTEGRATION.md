# Ziina Payment Integration - Frontend Guide

## Overview

This guide explains how to integrate Ziina payments in your mobile app (React Native/Flutter).

---

## Payment Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         PAYMENT FLOW                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. User taps "Pay Now" on rental                               │
│           │                                                      │
│           ▼                                                      │
│  2. App calls POST /api/payments/ziina/initiate/                │
│           │                                                      │
│           ▼                                                      │
│  3. Backend returns { redirect_url, payment_id }                │
│           │                                                      │
│           ▼                                                      │
│  4. App opens redirect_url in WebView or System Browser         │
│           │                                                      │
│           ▼                                                      │
│  5. User completes payment on Ziina page                        │
│           │                                                      │
│           ▼                                                      │
│  6. Ziina redirects to YOUR deep link:                          │
│     • Success: tezrent://payment/success?rental_id=X&payment_id=Y│
│     • Failed:  tezrent://payment/failed?rental_id=X              │
│           │                                                      │
│           ▼                                                      │
│  7. App catches deep link → extracts parameters                 │
│           │                                                      │
│           ▼                                                      │
│  8. App calls POST /api/payments/ziina/verify/                  │
│           │                                                      │
│           ▼                                                      │
│  9. Backend confirms → returns receipt data                     │
│           │                                                      │
│           ▼                                                      │
│  10. App shows Success/Failure screen with receipt              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## API Endpoints

### Base URL

```
Production: https://tezrent-api.onrender.com/api/payments/
```

---

### 1. Initiate Payment

**POST** `/ziina/initiate/`

Starts a new payment for a rental.

**Headers:**

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**

```json
{
  "rental_id": 123,
  "success_url": "tezrent://payment/success?rental_id=123",
  "cancel_url": "tezrent://payment/failed?rental_id=123"
}
```

**Response (Success - 200):**

```json
{
  "success": true,
  "payment_id": "pi_abc123xyz",
  "redirect_url": "https://pay.ziina.com/pi_abc123xyz",
  "rental_reference": "RNT12345678",
  "amount": 15000,
  "currency": "AED",
  "rental_payment_id": 45
}
```

**Response (Error - 400/403/502):**

```json
{
  "error": "Error message here"
}
```

---

### 2. Verify Payment

**POST** `/ziina/verify/`

Verify payment status after user returns from Ziina.

**Headers:**

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**

```json
{
  "payment_id": "pi_abc123xyz",
  "rental_id": 123
}
```

**Response (Payment Completed - 200):**

```json
{
  "success": true,
  "payment_status": "completed",
  "rental_status": "confirmed",
  "rental_reference": "RNT12345678",
  "message": "Payment successful! Your rental is confirmed.",
  "receipt": {
    "receipt_number": "RCP-000045",
    "payment_id": "pi_abc123xyz",
    "rental_reference": "RNT12345678",
    "payment_date": "2026-01-27T10:30:00Z",
    "payment_method": "Credit/Debit Card",
    "payment_status": "Completed",
    "customer": {
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+971501234567"
    },
    "equipment": {
      "name": "Professional Camera Kit",
      "category": "Photography",
      "seller": "Dubai Photo Rentals"
    },
    "rental_period": {
      "start_date": "2026-02-01",
      "end_date": "2026-02-03",
      "total_days": 3
    },
    "pricing": {
      "daily_rate": "50.00",
      "quantity": 1,
      "subtotal": "150.00",
      "delivery_fee": "0.00",
      "insurance_fee": "0.00",
      "security_deposit": "0.00",
      "total_amount": "150.00",
      "currency": "AED"
    },
    "amount_paid": "150.00"
  }
}
```

**Response (Payment Pending - 200):**

```json
{
  "success": false,
  "payment_status": "requires_payment",
  "rental_status": "payment_pending",
  "message": "Payment not completed. Please add a payment method."
}
```

**Response (Payment Failed - 200):**

```json
{
  "success": false,
  "payment_status": "failed",
  "rental_status": "payment_pending",
  "message": "Payment status: failed"
}
```

---

### 3. Get Payment Status

**GET** `/ziina/status/{rental_id}/`

Get all payments for a rental.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response (200):**

```json
{
  "rental_id": 123,
  "rental_reference": "RNT12345678",
  "rental_status": "confirmed",
  "rental_status_display": "Confirmed",
  "total_amount": "150.00",
  "total_paid": "150.00",
  "remaining_amount": "0.00",
  "payments": [
    {
      "id": 45,
      "payment_type": "rental_fee",
      "payment_type_display": "Rental Fee",
      "amount": "150.00",
      "status": "completed",
      "status_display": "Completed",
      "method": "card",
      "gateway_reference": "pi_abc123xyz",
      "created_at": "2026-01-27T10:25:00Z",
      "completed_at": "2026-01-27T10:30:00Z"
    }
  ],
  "is_fully_paid": true
}
```

---

### 4. Get Receipt

**GET** `/receipt/{payment_id}/`

Get receipt data for a completed payment.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response (200):**

```json
{
    "receipt_number": "RCP-000045",
    "payment_id": "pi_abc123xyz",
    "rental_reference": "RNT12345678",
    "payment_date": "2026-01-27T10:30:00Z",
    ... (same structure as receipt in verify response)
}
```

---

### 5. Resend Receipt Email

**POST** `/receipt/{payment_id}/resend/`

Resend receipt email to customer.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response (200):**

```json
{
  "success": true,
  "message": "Receipt email sent successfully"
}
```

---

## Deep Link Setup

### URL Scheme

Register the `tezrent://` scheme in your app.

### Deep Link Format

```
tezrent://payment/success?rental_id={rental_id}&payment_id={payment_id}
tezrent://payment/failed?rental_id={rental_id}
```

### React Native Setup

**1. Register scheme in `app.json` (Expo):**

```json
{
  "expo": {
    "scheme": "tezrent",
    "ios": {
      "bundleIdentifier": "com.tezrent.app"
    },
    "android": {
      "package": "com.tezrent.app",
      "intentFilters": [
        {
          "action": "VIEW",
          "data": [{ "scheme": "tezrent" }],
          "category": ["BROWSABLE", "DEFAULT"]
        }
      ]
    }
  }
}
```

**2. Handle deep links:**

```javascript
import * as Linking from "expo-linking";
import { useEffect } from "react";

function App() {
  useEffect(() => {
    // Handle deep link when app is already open
    const subscription = Linking.addEventListener("url", handleDeepLink);

    // Handle deep link when app opens from closed state
    Linking.getInitialURL().then((url) => {
      if (url) handleDeepLink({ url });
    });

    return () => subscription.remove();
  }, []);

  const handleDeepLink = ({ url }) => {
    const parsed = Linking.parse(url);
    // parsed.path = 'payment/success' or 'payment/failed'
    // parsed.queryParams = { rental_id: '123', payment_id: 'pi_xxx' }

    if (parsed.path === "payment/success") {
      verifyPayment(
        parsed.queryParams.payment_id,
        parsed.queryParams.rental_id,
      );
    } else if (parsed.path === "payment/failed") {
      navigateToFailureScreen(parsed.queryParams.rental_id);
    }
  };
}
```

---

## Frontend Implementation Example

### Payment Service (TypeScript)

```typescript
// services/paymentService.ts
import { api } from "./api";

interface InitiatePaymentParams {
  rentalId: number;
  successUrl?: string;
  cancelUrl?: string;
}

interface InitiatePaymentResponse {
  success: boolean;
  payment_id: string;
  redirect_url: string;
  rental_reference: string;
  amount: number;
  currency: string;
}

interface VerifyPaymentResponse {
  success: boolean;
  payment_status: string;
  rental_status: string;
  rental_reference: string;
  message: string;
  receipt?: ReceiptData;
}

interface ReceiptData {
  receipt_number: string;
  payment_id: string;
  rental_reference: string;
  payment_date: string;
  customer: { name: string; email: string; phone: string };
  equipment: { name: string; category: string; seller: string };
  rental_period: { start_date: string; end_date: string; total_days: number };
  pricing: {
    daily_rate: string;
    quantity: number;
    subtotal: string;
    delivery_fee: string;
    insurance_fee: string;
    total_amount: string;
    currency: string;
  };
  amount_paid: string;
}

export const paymentService = {
  // Initiate payment
  async initiatePayment(
    params: InitiatePaymentParams,
  ): Promise<InitiatePaymentResponse> {
    const response = await api.post("/payments/ziina/initiate/", {
      rental_id: params.rentalId,
      success_url:
        params.successUrl ||
        `tezrent://payment/success?rental_id=${params.rentalId}`,
      cancel_url:
        params.cancelUrl ||
        `tezrent://payment/failed?rental_id=${params.rentalId}`,
    });
    return response.data;
  },

  // Verify payment after redirect
  async verifyPayment(
    paymentId: string,
    rentalId: number,
  ): Promise<VerifyPaymentResponse> {
    const response = await api.post("/payments/ziina/verify/", {
      payment_id: paymentId,
      rental_id: rentalId,
    });
    return response.data;
  },

  // Get receipt
  async getReceipt(paymentId: string): Promise<ReceiptData> {
    const response = await api.get(`/payments/receipt/${paymentId}/`);
    return response.data;
  },

  // Resend receipt email
  async resendReceipt(
    paymentId: string,
  ): Promise<{ success: boolean; message: string }> {
    const response = await api.post(`/payments/receipt/${paymentId}/resend/`);
    return response.data;
  },
};
```

### Payment Screen Component

```tsx
// screens/PaymentScreen.tsx
import React, { useState } from "react";
import { View, Button, ActivityIndicator } from "react-native";
import * as WebBrowser from "expo-web-browser";
import { paymentService } from "../services/paymentService";

export function PaymentScreen({ route, navigation }) {
  const { rentalId } = route.params;
  const [loading, setLoading] = useState(false);

  const handlePayment = async () => {
    setLoading(true);
    try {
      // 1. Initiate payment
      const result = await paymentService.initiatePayment({
        rentalId,
        successUrl: `tezrent://payment/success?rental_id=${rentalId}`,
        cancelUrl: `tezrent://payment/failed?rental_id=${rentalId}`,
      });

      if (result.success) {
        // 2. Open Ziina payment page
        await WebBrowser.openBrowserAsync(result.redirect_url);
        // User will be redirected back via deep link
      } else {
        Alert.alert("Error", "Failed to initiate payment");
      }
    } catch (error) {
      Alert.alert("Error", error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View>
      <Button title="Pay Now" onPress={handlePayment} disabled={loading} />
      {loading && <ActivityIndicator />}
    </View>
  );
}
```

### Payment Success Screen

```tsx
// screens/PaymentSuccessScreen.tsx
import React, { useEffect, useState } from "react";
import { View, Text, Button, ScrollView } from "react-native";
import { paymentService } from "../services/paymentService";

export function PaymentSuccessScreen({ route, navigation }) {
  const { paymentId, rentalId } = route.params;
  const [receipt, setReceipt] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    verifyAndLoadReceipt();
  }, []);

  const verifyAndLoadReceipt = async () => {
    try {
      const result = await paymentService.verifyPayment(paymentId, rentalId);
      if (result.success && result.receipt) {
        setReceipt(result.receipt);
      }
    } catch (error) {
      console.error("Verification error:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleResendReceipt = async () => {
    try {
      await paymentService.resendReceipt(paymentId);
      Alert.alert("Success", "Receipt sent to your email");
    } catch (error) {
      Alert.alert("Error", "Failed to send receipt");
    }
  };

  if (loading) return <ActivityIndicator />;

  return (
    <ScrollView>
      <View style={styles.container}>
        <Text style={styles.title}>✅ Payment Successful!</Text>

        {receipt && (
          <>
            <View style={styles.receiptCard}>
              <Text style={styles.receiptTitle}>
                Receipt #{receipt.receipt_number}
              </Text>

              <Text>Equipment: {receipt.equipment.name}</Text>
              <Text>
                Rental Period: {receipt.rental_period.start_date} -{" "}
                {receipt.rental_period.end_date}
              </Text>
              <Text>Duration: {receipt.rental_period.total_days} days</Text>

              <View style={styles.divider} />

              <Text>Subtotal: AED {receipt.pricing.subtotal}</Text>
              <Text>Delivery: AED {receipt.pricing.delivery_fee}</Text>
              <Text style={styles.total}>
                Total Paid: AED {receipt.amount_paid}
              </Text>
            </View>

            <Button
              title="Resend Receipt Email"
              onPress={handleResendReceipt}
            />
          </>
        )}

        <Button
          title="View My Rentals"
          onPress={() => navigation.navigate("MyRentals")}
        />
      </View>
    </ScrollView>
  );
}
```

### Payment Failed Screen

```tsx
// screens/PaymentFailedScreen.tsx
import React from "react";
import { View, Text, Button } from "react-native";

export function PaymentFailedScreen({ route, navigation }) {
  const { rentalId } = route.params;

  return (
    <View style={styles.container}>
      <Text style={styles.title}>❌ Payment Failed</Text>
      <Text style={styles.message}>
        Your payment could not be completed. Please try again.
      </Text>

      <Button
        title="Try Again"
        onPress={() => navigation.navigate("Payment", { rentalId })}
      />

      <Button title="Go Back" onPress={() => navigation.goBack()} />
    </View>
  );
}
```

---

## Error Handling

| HTTP Code | Error                                   | Action                       |
| --------- | --------------------------------------- | ---------------------------- |
| 400       | `rental_id is required`                 | Check request body           |
| 403       | `You can only pay for your own rentals` | User doesn't own this rental |
| 404       | `Rental not found`                      | Invalid rental_id            |
| 502       | `Failed to create payment`              | Ziina API error, retry       |

---

## Testing

### Test Mode

The API is in test mode by default. Use Ziina test cards:

- **Success**: `4242 4242 4242 4242`
- **Failure**: `4000 0000 0000 0002`

### Test Deep Links

```bash
# iOS Simulator
xcrun simctl openurl booted "tezrent://payment/success?rental_id=1&payment_id=pi_test123"

# Android Emulator
adb shell am start -a android.intent.action.VIEW -d "tezrent://payment/success?rental_id=1&payment_id=pi_test123"
```

---

## Webhook (Backend Only)

The backend also receives Ziina webhooks at:

```
POST /api/payments/ziina/webhook/
```

This ensures payment confirmation even if the user closes the browser before redirect. **No frontend action needed** - this is handled server-side.

---

## Summary Checklist

### Frontend Tasks

- [ ] Register `tezrent://` deep link scheme
- [ ] Create payment initiation flow
- [ ] Handle deep link redirects (success/failed)
- [ ] Call verify endpoint after redirect
- [ ] Display success screen with receipt data
- [ ] Display failure screen with retry option
- [ ] Add "Resend Receipt" button

### API Endpoints Used

- `POST /api/payments/ziina/initiate/` - Start payment
- `POST /api/payments/ziina/verify/` - Confirm payment & get receipt
- `GET /api/payments/ziina/status/{rental_id}/` - Check payment status
- `GET /api/payments/receipt/{payment_id}/` - Get receipt
- `POST /api/payments/receipt/{payment_id}/resend/` - Resend email

---

## Questions?

Contact the backend team for any clarifications!
