# Favorites API Guide

This guide details the API endpoints for managing user favorites (wishlist) in the TezRent application.

## Base URL

`/api/favorites/`

## Authentication

All endpoints require authentication (`Authorization: Bearer <token>`).
The user must have a `CustomerProfile` (automatically created for all users).

## 1. Toggle Favorite (Recommended)

The easiest way to add/remove items from favorites.

**Endpoint:** `POST /api/favorites/favorites/toggle/`

**Request Body:**

```json
{
  "equipment_id": 28
}
```

**Response (Added):**

```json
{
  "favorited": true,
  "favorite_id": 15,
  "message": "Added to favorites"
}
```

**Response (Removed):**

```json
{
  "favorited": false,
  "favorite_id": null,
  "message": "Removed from favorites"
}
```

## 2. List Favorites

Get all equipment favorited by the current user.

**Endpoint:** `GET /api/favorites/favorites/`

**Response:**

```json
[
  {
    "id": 15,
    "equipment": {
      "id": 28,
      "name": "Excavator 3000",
      "daily_rate": "500.00",
      "primary_image": "http://localhost:8000/media/..."
      // ... full equipment details
    },
    "notes": "",
    "is_available": true,
    "current_price": 500.0,
    "mobile_display_data": {
      "equipment_name": "Excavator 3000",
      "daily_rate": "500.00",
      "equipment_image": "/media/..."
    }
  }
]
```

## 3. Check Status

Check if a specific item is favorited (useful for setting the "heart" icon state on product load).

**Endpoint:** `GET /api/favorites/favorites/check/?equipment_id=123`

**Response:**

```json
{
  "is_favorited": true,
  "favorite_id": 15
}
```

## 4. Add Note to Favorite

Update a favorite with personal notes or rental preferences.

**Endpoint:** `PATCH /api/favorites/favorites/{id}/`

**Request Body:**

```json
{
  "notes": "Need this for the backyard project in July",
  "notify_on_price_drop": true
}
```

## Integration Tips for Frontend

### "Heart" Icon Logic

1. **On Component Load**:

   - If you have the list of favorites loaded, check if `equipment.id` is in it.
   - OR call `GET /api/favorites/favorites/check/{id}/`.

2. **On Click**:
   - Call `POST /api/favorites/favorites/toggle/` with `equipment_id`.
   - Update UI immediately (optimistic update) or wait for response.
   - If response is `favorited: true`, fill the heart.
   - If response is `favorited: false`, empty the heart.

### Mobile App

Use the `mobile_display_data` field in the list response for a lightweight view optimized for React Native lists.
