# NOTIFICATIONS APP - Complete API Documentation

## 📋 Overview

The Notifications app manages system notifications sent to users for various events like rental status updates, new messages, payment confirmations, etc.

### Key Features
- Multi-channel notifications (in-app, email, push)
- Event-driven notifications
- Mark as read/unread
- Notification preferences
- Badge counts
- Real-time updates

---

## 🗄️ Model

### **Notification**

**Fields:**
- `recipient` (FK to User) - Who receives this
- `sender` (FK to User) - Who triggered it (optional)
- `notification_type` - Type of notification
- `title` - Notification title
- `message` - Notification text
- `related_object_type` - ContentType (optional)
- `related_object_id` - Object ID (optional)
- `is_read` - Read status
- `read_at` - When marked as read
- `created_at` - When created

**Notification Types:**
- `rental_request` - New rental request
- `rental_approved` - Rental approved
- `rental_cancelled` - Rental cancelled
- `rental_delivered` - Equipment delivered
- `rental_completed` - Rental completed
- `payment_received` - Payment confirmed
- `review_received` - New review
- `message` - New message
- `system` - System announcement

---

## 🔗 API Endpoints

### 1. List Notifications
```
GET /api/notifications/
Authorization: Bearer <token>
```

**Query Parameters:**
- `is_read=false` - Only unread
- `notification_type=rental_approved` - Filter by type

**Response (200 OK):**
```json
{
  "count": 15,
  "unread_count": 5,
  "results": [
    {
      "id": 1001,
      "title": "Rental Approved",
      "message": "Your rental request for CAT 320D Excavator has been approved",
      "notification_type": "rental_approved",
      "is_read": false,
      "created_at": "2025-10-21T11:15:00Z",
      "related_object": {
        "type": "rental",
        "id": 501
      }
    }
  ]
}
```

---

### 2. Mark as Read
```
POST /api/notifications/{id}/mark_read/
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "message": "Notification marked as read"
}
```

---

### 3. Mark All as Read
```
POST /api/notifications/mark_all_read/
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "message": "All notifications marked as read",
  "count": 5
}
```

---

### 4. Get Unread Count
```
GET /api/notifications/unread_count/
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "count": 5
}
```

---

## 📱 React Native Example

```javascript
const NotificationsScreen = () => {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  
  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 60000); // Poll every minute
    return () => clearInterval(interval);
  }, []);
  
  const fetchNotifications = async () => {
    const token = await AsyncStorage.getItem('access_token');
    
    const response = await fetch(
      'https://api.tezrent.com/api/notifications/',
      {
        headers: { 'Authorization': `Bearer ${token}` }
      }
    );
    
    const data = await response.json();
    setNotifications(data.results);
    setUnreadCount(data.unread_count);
  };
  
  const markAsRead = async (id) => {
    const token = await AsyncStorage.getItem('access_token');
    
    await fetch(
      `https://api.tezrent.com/api/notifications/${id}/mark_read/`,
      {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      }
    );
    
    fetchNotifications();
  };
  
  const handleNotificationPress = (notification) => {
    markAsRead(notification.id);
    
    // Navigate based on type
    if (notification.related_object?.type === 'rental') {
      navigation.navigate('RentalDetail', { 
        id: notification.related_object.id 
      });
    }
  };
  
  return (
    <View>
      <Text>Notifications ({unreadCount} unread)</Text>
      
      <FlatList
        data={notifications}
        renderItem={({ item }) => (
          <TouchableOpacity onPress={() => handleNotificationPress(item)}>
            <View style={{ 
              backgroundColor: item.is_read ? '#FFF' : '#E3F2FD' 
            }}>
              <Text style={{ fontWeight: item.is_read ? 'normal' : 'bold' }}>
                {item.title}
              </Text>
              <Text>{item.message}</Text>
              <Text>{formatDate(item.created_at)}</Text>
            </View>
          </TouchableOpacity>
        )}
      />
    </View>
  );
};
```

---

## 🔔 NotificationService

Used by other apps to send notifications:

```python
from notifications.services import NotificationService

# Send rental approved notification
NotificationService.send_notification(
    recipient=customer_user,
    notification_type='rental_approved',
    title='Rental Approved',
    message=f'Your rental request for {equipment.name} has been approved',
    related_object=rental
)
```

---

**End of Notifications API Documentation** 📚
