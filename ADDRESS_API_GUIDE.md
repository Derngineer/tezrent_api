# Delivery Address API Guide

This guide details how to manage user delivery addresses and use them during the rental checkout process.

## Base URL

`/api/accounts/addresses/`

## 1. List All Addresses

Get all saved addresses for the logged-in user.

**Request:**

- Method: `GET`
- Endpoint: `/api/accounts/addresses/`
- Headers: `Authorization: Bearer <access_token>`

**Response:**

```json
[
  {
    "id": 1,
    "label": "Home",
    "apartment_room": "101",
    "building": "Sky Tower",
    "street_landmark": "Main Street, Downtown",
    "city": "Dubai",
    "contact_number": "+971501234567",
    "latitude": "25.204800",
    "longitude": "55.270800",
    "is_default": true,
    "created_at": "2025-12-10T10:00:00Z",
    "updated_at": "2025-12-10T10:00:00Z"
  },
  {
    "id": 2,
    "label": "Office",
    "apartment_room": "Office 404",
    "building": "Business Bay Tower",
    "street_landmark": "Business Bay",
    "city": "Dubai",
    "contact_number": "+971509876543",
    "latitude": "25.185700",
    "longitude": "55.270800",
    "is_default": false,
    "created_at": "2025-12-11T11:00:00Z",
    "updated_at": "2025-12-11T11:00:00Z"
  }
]
```

## 2. Create New Address

Add a new delivery location.

**Request:**

- Method: `POST`
- Endpoint: `/api/accounts/addresses/`
- Headers: `Authorization: Bearer <access_token>`
- Body:

```json
{
  "label": "Site Office",
  "apartment_room": "Container 3",
  "building": "Construction Site A",
  "street_landmark": "Al Asayel Street",
  "city": "Dubai",
  "contact_number": "+971501234567",
  "latitude": 25.1857,
  "longitude": 55.2708,
  "is_default": true
}
```

**Notes:**

- `latitude` and `longitude` are optional but recommended for accurate delivery.
- Setting `is_default: true` will automatically set `is_default: false` for all other addresses belonging to this user.

## 3. Update Address

Edit an existing address.

**Request:**

- Method: `PATCH` (Partial update) or `PUT` (Full update)
- Endpoint: `/api/accounts/addresses/{id}/`
- Headers: `Authorization: Bearer <access_token>`
- Body:

```json
{
  "contact_number": "+971555555555",
  "label": "Main Site Office"
}
```

## 4. Delete Address

Remove an address.

**Request:**

- Method: `DELETE`
- Endpoint: `/api/accounts/addresses/{id}/`
- Headers: `Authorization: Bearer <access_token>`

## 5. Using Address in Rental (Checkout)

When creating a rental request, pass the `delivery_address_id` to automatically populate delivery details.

**Request:**

- Method: `POST`
- Endpoint: `/api/rentals/rentals/`
- Body:

```json
{
  "equipment": 15,
  "start_date": "2025-12-15",
  "end_date": "2025-12-20",
  "quantity": 1,
  "pickup_required": false,
  "delivery_address_id": 1, // ID of the address to use
  "customer_notes": "Call upon arrival"
}
```

## Frontend Implementation Tips (Collecting Data)

1.  **Map Interface**: Use a map component (like Google Maps or Mapbox) to let users pin their location. Capture the `latitude` and `longitude` from the pin.
2.  **Reverse Geocoding**: Use the coordinates to auto-fill `street_landmark` and `city` if possible.
3.  **Form Fields**:
    - **Label**: Dropdown (Home, Office) or Text Input.
    - **Building/Villa**: Text Input.
    - **Apartment/Room**: Text Input.
    - **Contact Number**: Pre-fill with user's profile phone number but allow editing.
    - **Default Checkbox**: "Set as default delivery address".
