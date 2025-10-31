# 🚀 Deployment Guide - TezRent API

Complete guide to deploy your Django API to production using GitHub and a cloud platform.

---

## 📋 Prerequisites

1. ✅ GitHub account
2. ✅ Git installed locally
3. ✅ Choose a deployment platform:
   - **Render** (Recommended - Free tier available)
   - **Railway** (Free tier available)
   - **Heroku** (Paid plans)

---

## 🔧 Pre-Deployment Setup

### 1. Install Production Packages

```bash
pip install -r requirements.txt
```

This installs:
- `dj-database-url` - PostgreSQL connection
- `psycopg2-binary` - PostgreSQL adapter
- `whitenoise` - Static file serving
- `gunicorn` - Production WSGI server

### 2. Generate a New SECRET_KEY

```python
# Run in Python shell
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

Save this key - you'll need it for environment variables.

### 3. Test Production Settings Locally

```bash
# Set environment variables temporarily
export SECRET_KEY="your-generated-secret-key"
export DEBUG="False"
export DATABASE_URL="sqlite:///db.sqlite3"

# Collect static files
python manage.py collectstatic --noinput

# Test that it runs
python manage.py runserver
```

---

## 📦 GitHub Setup

### 1. Initialize Git Repository

```bash
# If not already initialized
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Ready for deployment"
```

### 2. Create GitHub Repository

1. Go to https://github.com/new
2. Name: `tezrent-api` (or your choice)
3. Don't initialize with README (you already have one)
4. Create repository

### 3. Push to GitHub

```bash
# Add remote
git remote add origin https://github.com/YOUR-USERNAME/tezrent-api.git

# Push to GitHub
git branch -M main
git push -u origin main
```

---

## 🌐 Deployment Options

Choose one platform below:

---

## Option A: Deploy to Render (Recommended)

### Step 1: Create Render Account
1. Go to https://render.com
2. Sign up with GitHub
3. Authorize Render to access your repositories

### Step 2: Create PostgreSQL Database
1. Click "New +" → "PostgreSQL"
2. Name: `tezrent-db`
3. Select Free tier
4. Click "Create Database"
5. **Save the Internal Database URL** (you'll need this)

### Step 3: Create Web Service
1. Click "New +" → "Web Service"
2. Connect your `tezrent-api` repository
3. Configure:
   - **Name**: `tezrent-api`
   - **Region**: Choose closest to your users
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn config.wsgi:application`

### Step 4: Add Environment Variables
In the "Environment" section, add:

```
SECRET_KEY = your-generated-secret-key
DEBUG = False
DATABASE_URL = [paste your PostgreSQL Internal Database URL]
ALLOWED_HOSTS = your-service-name.onrender.com
```

### Step 5: Deploy
1. Click "Create Web Service"
2. Wait 3-5 minutes for deployment
3. Your API will be live at: `https://your-service-name.onrender.com`

### Step 6: Run Migrations
1. Go to your Web Service dashboard
2. Click "Shell" tab
3. Run:
```bash
python manage.py migrate
python manage.py createsuperuser
```

---

## Option B: Deploy to Railway

### Step 1: Create Railway Account
1. Go to https://railway.app
2. Sign up with GitHub

### Step 2: Create New Project
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your `tezrent-api` repository

### Step 3: Add PostgreSQL
1. Click "New" → "Database" → "Add PostgreSQL"
2. Railway automatically creates `DATABASE_URL` variable

### Step 4: Configure Environment Variables
1. Go to your service
2. Click "Variables" tab
3. Add:
```
SECRET_KEY = your-generated-secret-key
DEBUG = False
ALLOWED_HOSTS = your-project.up.railway.app
```

### Step 5: Deploy
1. Railway automatically deploys
2. Click "Settings" → "Generate Domain"
3. Your API will be live at: `https://your-project.up.railway.app`

### Step 6: Run Migrations
1. Click "Settings" → "Deploy" → "Run Command"
2. Run:
```bash
python manage.py migrate
python manage.py createsuperuser
```

---

## 🔐 Update Frontend CORS Settings

After deployment, update your frontend to use the production API:

### Update Frontend Code
```javascript
// Replace localhost with your production URL
const API_BASE_URL = 'https://your-service-name.onrender.com/api/v1';

// Or use environment variables
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';
```

### Update Netlify Environment Variables
1. Go to Netlify dashboard
2. Site settings → Environment variables
3. Add:
```
REACT_APP_API_URL = https://your-service-name.onrender.com/api/v1
```

### Redeploy Frontend
```bash
# Trigger a new build on Netlify
git commit --allow-empty -m "Update API URL"
git push
```

---

## ✅ Post-Deployment Checklist

### 1. Test API Endpoints
```bash
# Test health check (if you have one)
curl https://your-api-url.com/api/v1/

# Test dashboard endpoint
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://your-api-url.com/api/v1/rentals/dashboard_summary/
```

### 2. Create Sample Data
```bash
# SSH into your deployment
# Then run your data creation scripts
python create_categories.py
python create_sample_listing.py
python create_sample_rentals.py
```

### 3. Monitor Logs
- **Render**: Dashboard → Logs tab
- **Railway**: Dashboard → Logs tab

### 4. Set Up Monitoring
- Check error logs daily
- Monitor database usage
- Watch for CORS issues

---

## 🐛 Common Issues & Solutions

### Issue 1: Static Files Not Loading
**Solution**: Make sure you ran `collectstatic`
```bash
python manage.py collectstatic --noinput
```

### Issue 2: Database Connection Error
**Solution**: Check `DATABASE_URL` format:
```
postgresql://user:password@host:port/database
```

### Issue 3: CORS Errors
**Solution**: Add your frontend URL to `settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    'https://sellerdashtezrent.netlify.app',
    'https://your-production-url.com',
]
```

### Issue 4: 502 Bad Gateway
**Solution**: Check that `Procfile` exists with:
```
web: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
```

### Issue 5: Media Files Not Accessible
**Solution**: For user uploads, consider using:
- AWS S3 (django-storages)
- Cloudinary
- Render Persistent Disks (paid)

---

## 🔄 Continuous Deployment

### Auto-Deploy on Push
Both Render and Railway automatically deploy when you push to GitHub:

```bash
# Make changes
git add .
git commit -m "Add new feature"
git push

# Deployment happens automatically!
```

### Manual Deploy
- **Render**: Dashboard → "Manual Deploy" → "Deploy latest commit"
- **Railway**: Dashboard → "Deploy" → "Redeploy"

---

## 📊 Database Management

### Backup Database (Render)
```bash
# Download backup
pg_dump $DATABASE_URL > backup.sql

# Restore backup
psql $DATABASE_URL < backup.sql
```

### Access Database Shell
- **Render**: Dashboard → "Shell" → `python manage.py dbshell`
- **Railway**: Dashboard → PostgreSQL → "Connect"

---

## 🔒 Security Best Practices

1. ✅ Never commit `.env` file
2. ✅ Use strong `SECRET_KEY` (50+ characters)
3. ✅ Set `DEBUG=False` in production
4. ✅ Keep `ALLOWED_HOSTS` specific
5. ✅ Use HTTPS only (platforms provide this automatically)
6. ✅ Regularly update dependencies:
   ```bash
   pip list --outdated
   pip install --upgrade package-name
   ```

---

## 📈 Scaling Tips

### Performance Optimization
1. **Enable Database Connection Pooling** (already configured in settings.py)
2. **Use Redis for Caching** (optional, for high traffic)
3. **Add CDN for Media Files** (Cloudflare, AWS CloudFront)

### Monitoring
- Set up error tracking: **Sentry**
- Monitor uptime: **UptimeRobot** (free)
- Performance monitoring: **New Relic** or **Datadog**

---

## 🆘 Need Help?

### Platform Documentation
- **Render**: https://render.com/docs
- **Railway**: https://docs.railway.app
- **Django Deployment**: https://docs.djangoproject.com/en/5.0/howto/deployment/

### Troubleshooting Steps
1. Check deployment logs
2. Verify environment variables
3. Test database connection
4. Check CORS settings
5. Verify static files collected

---

## ✨ Your API is Live!

Once deployed, your endpoints will be available at:

```
Base URL: https://your-service-name.onrender.com/api/v1/

Dashboard: https://your-service-name.onrender.com/api/v1/rentals/dashboard_summary/

Equipment: https://your-service-name.onrender.com/api/v1/equipment/

Rentals: https://your-service-name.onrender.com/api/v1/rentals/
```

Update your frontend to use this base URL and you're ready to go! 🎉

---

## 📝 Quick Reference

### Environment Variables Template
```bash
SECRET_KEY=your-50-char-secret-key
DEBUG=False
DATABASE_URL=postgresql://user:pass@host:port/db
ALLOWED_HOSTS=your-domain.com
```

### Useful Commands
```bash
# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Check deployment settings
python manage.py check --deploy
```

---

**Happy Deploying! 🚀**
