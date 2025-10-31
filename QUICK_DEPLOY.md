# 🚀 Quick Deployment Steps

## Ready in 5 Minutes!

### 1️⃣ Install Production Packages
```bash
pip install -r requirements.txt
```

### 2️⃣ Generate Secret Key
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
Save this key!

### 3️⃣ Push to GitHub
```bash
git init
git add .
git commit -m "Ready for deployment"
git remote add origin https://github.com/YOUR-USERNAME/tezrent-api.git
git push -u origin main
```

### 4️⃣ Deploy to Render (Recommended)

1. **Create Database**: 
   - Go to https://render.com
   - New → PostgreSQL (Free tier)
   - Save the Internal Database URL

2. **Create Web Service**:
   - New → Web Service
   - Connect your GitHub repo
   - Runtime: Python 3
   - Build: `pip install -r requirements.txt`
   - Start: `gunicorn config.wsgi:application`

3. **Add Environment Variables**:
   ```
   SECRET_KEY = your-generated-key
   DEBUG = False
   DATABASE_URL = [your-postgres-url]
   ALLOWED_HOSTS = your-service.onrender.com
   ```

4. **Deploy!**
   - Click "Create Web Service"
   - Wait 3-5 minutes
   - Done! ✅

### 5️⃣ Run Initial Setup
In Render Shell:
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6️⃣ Update Frontend
Update your Netlify environment variable:
```
REACT_APP_API_URL = https://your-service.onrender.com/api/v1
```

## 🎉 That's it! Your API is live!

---

## 📋 Checklist

- [ ] Installed production packages
- [ ] Generated new SECRET_KEY
- [ ] Pushed code to GitHub
- [ ] Created PostgreSQL database
- [ ] Created web service on Render
- [ ] Added environment variables
- [ ] Ran migrations
- [ ] Created superuser
- [ ] Updated frontend API URL
- [ ] Tested dashboard endpoint

---

## 🔗 Your API URLs

After deployment, your endpoints will be:

```
Base: https://your-service.onrender.com/api/v1/

Dashboard: https://your-service.onrender.com/api/v1/rentals/dashboard_summary/
Equipment: https://your-service.onrender.com/api/v1/equipment/
Rentals: https://your-service.onrender.com/api/v1/rentals/
```

---

## ⚠️ Common Issues

**502 Error?**
→ Check Procfile exists with: `web: gunicorn config.wsgi:application`

**Database Error?**
→ Verify DATABASE_URL in environment variables

**CORS Error?**
→ Already configured for https://sellerdashtezrent.netlify.app/

**Static Files Missing?**
→ Render automatically runs collectstatic

---

## 📚 Full Details

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for complete documentation.

---

**Need help? Check the logs in Render dashboard!**
