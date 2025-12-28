# Ziina Payment Integration - React Native

## Base URL

```
http://localhost:8000
```

> **Production:** Change to `https://tezrentapibackend-bsatbme3eqfkfnc3.canadacentral-01.azurewebsites.net`

---

## Quick Setup

### 1. Install Dependencies

```bash
npm install axios react-native-linking
```

### 2. Add Deep Link Config

**iOS** - `ios/YourApp/Info.plist`:

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

**Android** - `android/app/src/main/AndroidManifest.xml` (inside `<activity>`):

```xml
<intent-filter>
  <action android:name="android.intent.action.VIEW" />
  <category android:name="android.intent.category.DEFAULT" />
  <category android:name="android.intent.category.BROWSABLE" />
  <data android:scheme="tezrent" />
</intent-filter>
```

---

## API Reference

### Initiate Payment

```
POST /api/payments/ziina/initiate/
```

**Request:**

```json
{
  "rental_id": 123
}
```

**Response:**

```json
{
  "success": true,
  "payment_id": "pi_abc123",
  "redirect_url": "https://pay.ziina.com/checkout/abc123",
  "amount": 15000,
  "currency": "AED"
}
```

---

### Verify Payment

```
POST /api/payments/ziina/verify/
```

**Request:**

```json
{
  "payment_id": "pi_abc123",
  "rental_id": 123
}
```

**Response:**

```json
{
  "success": true,
  "payment_status": "completed",
  "rental_status": "confirmed",
  "message": "Payment successful!"
}
```

---

### Check Status

```
GET /api/payments/ziina/status/{rental_id}/
```

**Response:**

```json
{
  "rental_id": 123,
  "total_amount": "150.00",
  "is_fully_paid": true
}
```

---

## Complete Implementation

Copy this file to your React Native project:

### `services/paymentService.js`

```javascript
import { Linking } from "react-native";

const BASE_URL = "http://localhost:8000";

class PaymentService {
  constructor(accessToken) {
    this.accessToken = accessToken;
  }

  async initiatePayment(rentalId) {
    const response = await fetch(`${BASE_URL}/api/payments/ziina/initiate/`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${this.accessToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        rental_id: rentalId,
        success_url: `tezrent://payment/success?rental_id=${rentalId}`,
        cancel_url: `tezrent://payment/failed?rental_id=${rentalId}`,
      }),
    });
    return response.json();
  }

  async verifyPayment(paymentId, rentalId) {
    const response = await fetch(`${BASE_URL}/api/payments/ziina/verify/`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${this.accessToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        payment_id: paymentId,
        rental_id: rentalId,
      }),
    });
    return response.json();
  }

  async getPaymentStatus(rentalId) {
    const response = await fetch(
      `${BASE_URL}/api/payments/ziina/status/${rentalId}/`,
      {
        headers: {
          Authorization: `Bearer ${this.accessToken}`,
        },
      }
    );
    return response.json();
  }

  openCheckout(redirectUrl) {
    Linking.openURL(redirectUrl);
  }
}

export default PaymentService;
```

---

### `screens/PaymentScreen.js`

```javascript
import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
  Linking,
} from "react-native";
import PaymentService from "../services/paymentService";

const PaymentScreen = ({ route, navigation }) => {
  const { rental, accessToken } = route.params;

  const [loading, setLoading] = useState(false);
  const [paymentId, setPaymentId] = useState(null);

  const paymentService = new PaymentService(accessToken);

  // Listen for deep link when user returns from Ziina
  useEffect(() => {
    const handleDeepLink = (event) => {
      const url = event.url;

      if (url.includes("payment/success")) {
        handlePaymentReturn();
      } else if (url.includes("payment/failed")) {
        Alert.alert("Cancelled", "Payment was cancelled");
      }
    };

    const subscription = Linking.addEventListener("url", handleDeepLink);
    return () => subscription.remove();
  }, [paymentId]);

  // Step 1: Start payment
  const handlePay = async () => {
    setLoading(true);

    try {
      const result = await paymentService.initiatePayment(rental.id);

      if (result.success) {
        setPaymentId(result.payment_id);
        paymentService.openCheckout(result.redirect_url);
      } else {
        Alert.alert("Error", result.error);
      }
    } catch (error) {
      Alert.alert("Error", "Failed to start payment");
    }

    setLoading(false);
  };

  // Step 2: Verify when user returns
  const handlePaymentReturn = async () => {
    if (!paymentId) return;

    setLoading(true);

    try {
      const result = await paymentService.verifyPayment(paymentId, rental.id);

      if (result.success) {
        Alert.alert("Success! ✅", result.message, [
          { text: "OK", onPress: () => navigation.goBack() },
        ]);
      } else {
        Alert.alert("Payment Incomplete", result.message);
      }
    } catch (error) {
      Alert.alert("Error", "Could not verify payment");
    }

    setLoading(false);
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Payment</Text>

      <View style={styles.amountBox}>
        <Text style={styles.amountLabel}>Total Amount</Text>
        <Text style={styles.amount}>AED {rental.total_amount}</Text>
      </View>

      <TouchableOpacity
        style={[styles.payButton, loading && styles.disabled]}
        onPress={handlePay}
        disabled={loading}
      >
        <Text style={styles.payButtonText}>
          {loading ? "Processing..." : "Pay with Ziina"}
        </Text>
      </TouchableOpacity>

      <TouchableOpacity
        style={styles.verifyButton}
        onPress={handlePaymentReturn}
      >
        <Text style={styles.verifyText}>Already paid? Tap to verify</Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: "#fff",
  },
  title: {
    fontSize: 24,
    fontWeight: "bold",
    marginBottom: 30,
    textAlign: "center",
  },
  amountBox: {
    backgroundColor: "#f5f5f5",
    padding: 20,
    borderRadius: 10,
    marginBottom: 30,
    alignItems: "center",
  },
  amountLabel: {
    fontSize: 14,
    color: "#666",
  },
  amount: {
    fontSize: 36,
    fontWeight: "bold",
    color: "#2ecc71",
    marginTop: 5,
  },
  payButton: {
    backgroundColor: "#3498db",
    padding: 18,
    borderRadius: 10,
    alignItems: "center",
  },
  disabled: {
    opacity: 0.6,
  },
  payButtonText: {
    color: "#fff",
    fontSize: 18,
    fontWeight: "bold",
  },
  verifyButton: {
    marginTop: 20,
    padding: 15,
    alignItems: "center",
  },
  verifyText: {
    color: "#3498db",
    fontSize: 14,
  },
});

export default PaymentScreen;
```

---

### Usage

```javascript
// Navigate to payment screen
navigation.navigate("Payment", {
  rental: {
    id: 123,
    total_amount: "150.00",
  },
  accessToken: userToken,
});
```

---

## Test Cards

| Card                  | Result      |
| --------------------- | ----------- |
| `4242 4242 4242 4242` | ✅ Success  |
| `4000 0000 0000 0002` | ❌ Declined |

**Expiry:** Any future date  
**CVV:** Any 3 digits

---

## Flow Diagram

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Tap "Pay"  │ ──► │  Initiate   │ ──► │ Open Ziina  │
└─────────────┘     │   Payment   │     │  Checkout   │
                    └─────────────┘     └──────┬──────┘
                                               │
                                               ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Done! ✅   │ ◄── │   Verify    │ ◄── │  Deep Link  │
│  Confirmed  │     │   Payment   │     │   Return    │
└─────────────┘     └─────────────┘     └─────────────┘
```

---

## Checklist

- [ ] Add `tezrent://` deep link scheme (iOS + Android)
- [ ] Copy `paymentService.js` to services folder
- [ ] Copy `PaymentScreen.js` to screens folder
- [ ] Update `BASE_URL` for production
- [ ] Test with test card `4242 4242 4242 4242`

---

## Questions?

Contact backend team or check API docs at `/api/payments/`
