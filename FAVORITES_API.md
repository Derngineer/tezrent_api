# Favorites/Liked Section - API Documentation

## ✅ IMPLEMENTED - Ready to Use!

The favorites system allows customers to save equipment they like, organize them into collections, and track recently viewed items.

---

## 📦 Features Included

### 1. **Favorites (Liked Equipment)**
- Save/like equipment for later
- Add personal notes to favorites
- Set rental preferences (dates, duration)
- Configure notifications (availability, price drops, deals)
- Track current price vs favorited price

### 2. **Collections/Wishlists**
- Organize favorites into custom collections
- Name collections (e.g., "Summer Projects", "Next Month")
- Add icons and colors for visual organization
- Make collections public/private
- Calculate total estimated cost for all items in collection

### 3. **Recently Viewed**
- Automatic tracking of equipment views
- View count tracking
- Track where users viewed from (search, category, featured, etc.)
- Limited to last 20 items

---

## 🔗 API Endpoints

### Favorites Endpoints

```
GET    /api/favorites/                    - List user's favorites
POST   /api/favorites/                    - Add to favorites
GET    /api/favorites/{id}/               - Get favorite detail
PUT    /api/favorites/{id}/               - Update favorite settings
DELETE /api/favorites/{id}/               - Remove from favorites

# Special Actions
POST   /api/favorites/toggle/             - Toggle favorite status
GET    /api/favorites/check/              - Check if equipment is favorited
GET    /api/favorites/available/          - Get only available favorites
GET    /api/favorites/on_deal/            - Get favorites currently on deal
```

### Collections Endpoints

```
GET    /api/favorites/collections/        - List user's collections
POST   /api/favorites/collections/        - Create new collection
GET    /api/favorites/collections/{id}/   - Get collection detail
PUT    /api/favorites/collections/{id}/   - Update collection
DELETE /api/favorites/collections/{id}/   - Delete collection

# Collection Actions
POST   /api/favorites/collections/{id}/add_equipment/     - Add equipment to collection
POST   /api/favorites/collections/{id}/remove_equipment/  - Remove from collection
```

### Recently Viewed Endpoints

```
GET    /api/favorites/recently-viewed/       - List recently viewed (last 20)
POST   /api/favorites/recently-viewed/track/ - Track equipment view
DELETE /api/favorites/recently-viewed/clear/ - Clear all history
```

---

## 💻 Usage Examples

### React Native - Toggle Favorite (Heart Button)

```javascript
// When user taps the heart icon
const toggleFavorite = async (equipmentId) => {
  try {
    const response = await fetch('/api/favorites/toggle/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ equipment_id: equipmentId })
    });
    
    const data = await response.json();
    // data.favorited = true/false
    // data.favorite_id = 123 or null
    // data.message = "Added to favorites" or "Removed from favorites"
    
    setIsFavorited(data.favorited);
  } catch (error) {
    console.error('Error toggling favorite:', error);
  }
};
```

### React Native - Check if Equipment is Favorited

```javascript
// When loading equipment detail page
const checkIfFavorited = async (equipmentId) => {
  try {
    const response = await fetch(
      `/api/favorites/check/?equipment_id=${equipmentId}`,
      {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
        }
      }
    );
    
    const data = await response.json();
    // data.is_favorited = true/false
    // data.favorite_id = 123 or null
    
    setIsFavorited(data.is_favorited);
  } catch (error) {
    console.error('Error checking favorite:', error);
  }
};
```

### React Native - Get User's Favorites

```javascript
// For "My Favorites" screen
const fetchFavorites = async () => {
  try {
    const response = await fetch('/api/favorites/', {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
      }
    });
    
    const data = await response.json();
    // data is array of favorites with full equipment details
    
    setFavorites(data);
  } catch (error) {
    console.error('Error fetching favorites:', error);
  }
};
```

### React Native - Add to Favorites with Notes

```javascript
const addToFavorites = async (equipmentId, notes = '') => {
  try {
    const response = await fetch('/api/favorites/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        equipment: equipmentId,
        notes: notes,
        notify_on_deals: true,
        notify_on_price_drop: true,
      })
    });
    
    const favorite = await response.json();
    return favorite;
  } catch (error) {
    console.error('Error adding to favorites:', error);
  }
};
```

### React Native - Create Collection

```javascript
const createCollection = async (name, description) => {
  try {
    const response = await fetch('/api/favorites/collections/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: name,
        description: description,
        icon: 'bookmark',
        color: '#FF6B35',
        is_public: false
      })
    });
    
    const collection = await response.json();
    return collection;
  } catch (error) {
    console.error('Error creating collection:', error);
  }
};
```

### React Native - Add Equipment to Collection

```javascript
const addToCollection = async (collectionId, equipmentId) => {
  try {
    const response = await fetch(
      `/api/favorites/collections/${collectionId}/add_equipment/`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ equipment_id: equipmentId })
      }
    );
    
    const data = await response.json();
    // data.message = "Added {equipment.name} to {collection.name}"
    // data.collection = updated collection object
    
    return data;
  } catch (error) {
    console.error('Error adding to collection:', error);
  }
};
```

### React Native - Track Equipment View

```javascript
// Call this when user views equipment detail
const trackView = async (equipmentId, viewedFrom = 'search') => {
  try {
    await fetch('/api/favorites/recently-viewed/track/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        equipment_id: equipmentId,
        viewed_from: viewedFrom // 'search', 'category', 'featured', 'deals', etc.
      })
    });
  } catch (error) {
    // Silent fail - tracking is not critical
    console.log('View tracking failed (non-critical)');
  }
};
```

### React Native - Get Favorites with Deals

```javascript
// Show favorites that are currently on sale
const getFavoritesOnDeal = async () => {
  try {
    const response = await fetch('/api/favorites/on_deal/', {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
      }
    });
    
    const data = await response.json();
    // data.count = number of deals
    // data.results = array of favorites with deals
    
    return data.results;
  } catch (error) {
    console.error('Error fetching deal favorites:', error);
  }
};
```

---

## 📱 React Native Component Examples

### Heart/Like Button Component

```jsx
import React, { useState, useEffect } from 'react';
import { TouchableOpacity } from 'react-native';
import Icon from 'react-native-vector-icons/Ionicons';

export const FavoriteButton = ({ equipmentId }) => {
  const [isFavorited, setIsFavorited] = useState(false);
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    checkFavoriteStatus();
  }, [equipmentId]);
  
  const checkFavoriteStatus = async () => {
    const response = await fetch(
      `/api/favorites/check/?equipment_id=${equipmentId}`,
      { headers: { 'Authorization': `Bearer ${accessToken}` } }
    );
    const data = await response.json();
    setIsFavorited(data.is_favorited);
  };
  
  const toggleFavorite = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/favorites/toggle/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ equipment_id: equipmentId })
      });
      
      const data = await response.json();
      setIsFavorited(data.favorited);
      
      // Show toast/notification
      showToast(data.message);
    } catch (error) {
      showToast('Failed to update favorite');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <TouchableOpacity onPress={toggleFavorite} disabled={loading}>
      <Icon
        name={isFavorited ? 'heart' : 'heart-outline'}
        size={24}
        color={isFavorited ? '#FF6B35' : '#666'}
      />
    </TouchableOpacity>
  );
};
```

### Favorites List Screen

```jsx
import React, { useState, useEffect } from 'react';
import { FlatList, View, Text, Image, TouchableOpacity } from 'react-native';

export const FavoritesScreen = ({ navigation }) => {
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetchFavorites();
  }, []);
  
  const fetchFavorites = async () => {
    try {
      const response = await fetch('/api/favorites/', {
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      const data = await response.json();
      setFavorites(data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };
  
  const renderFavorite = ({ item }) => {
    const display = item.mobile_display_data;
    
    return (
      <TouchableOpacity
        onPress={() => navigation.navigate('EquipmentDetail', {
          equipmentId: display.equipment_id
        })}
        style={styles.favoriteCard}
      >
        <Image
          source={{ uri: display.equipment_image }}
          style={styles.image}
        />
        <View style={styles.info}>
          <Text style={styles.name}>{display.equipment_name}</Text>
          <Text style={styles.company}>{display.company_name}</Text>
          <Text style={styles.location}>{display.location}</Text>
          <Text style={styles.price}>${display.daily_rate}/day</Text>
          
          {display.is_deal && (
            <View style={styles.dealBadge}>
              <Text style={styles.dealText}>
                {display.discount_percentage}% OFF
              </Text>
            </View>
          )}
          
          {!display.is_available && (
            <Text style={styles.unavailable}>Currently Unavailable</Text>
          )}
        </View>
      </TouchableOpacity>
    );
  };
  
  return (
    <FlatList
      data={favorites}
      renderItem={renderFavorite}
      keyExtractor={(item) => item.id.toString()}
      refreshing={loading}
      onRefresh={fetchFavorites}
    />
  );
};
```

---

## 🔔 Notification Integration

The favorites system includes notification preferences:

- **Availability Notifications**: Notify when favorited equipment becomes available
- **Price Drop Alerts**: Notify when price decreases
- **Deal Alerts**: Notify when equipment goes on sale

These can be integrated with the notification system we just created!

---

## 📊 Admin Interface

All favorites, collections, and recently viewed items are manageable in Django admin:

- `/admin/favorites/favorite/` - Manage all favorites
- `/admin/favorites/favoritecollection/` - Manage collections
- `/admin/favorites/recentlyviewed/` - View tracking data

---

## 🎯 Next Steps

1. **Test the API** - Try adding/removing favorites
2. **Implement in React Native** - Add heart buttons to equipment cards
3. **Create Favorites Screen** - Show user's saved equipment
4. **Add Collections UI** - Allow users to organize favorites
5. **Enable Notifications** - Alert users about price drops and deals

---

**The favorites system is fully functional and ready to integrate into your React Native apps!** 🎉
