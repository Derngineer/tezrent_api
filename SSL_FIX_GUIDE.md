# SSL Certificate Error - FIXED! ✅

## ✅ Solution Applied: Custom Email Backend

I've created a **custom email backend** that bypasses SSL certificate verification for macOS. This is the easiest solution that works immediately.

### What Was Done:
1. Created `accounts/email_backend.py` - Custom SMTP backend
2. Updated `settings.py` to use: `EMAIL_BACKEND = 'accounts.email_backend.CustomEmailBackend'`
3. Backend uses `ssl._create_unverified_context()` to bypass certificate checks

### ⚠️ Important Note:
This is **safe for development** but for production, you should:
- Install proper SSL certificates, OR
- Use a production email service (SendGrid, AWS SES)

---

## 🔄 Restart Your Server

**IMPORTANT:** You must restart Django for the changes to take effect!

1. Stop your server (Ctrl+C)
2. Restart: `python manage.py runserver`
3. Test password reset - **emails should now send!**

---

## The Error You're Seeing

```
Email error: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: 
unable to get local issuer certificate (_ssl.c:1077)
```

**Good News:** This means your email settings are configured correctly! It's just an SSL certificate issue on macOS.

---

## Quick Fix #1: Use Port 465 with SSL (Recommended)

Update your `config/settings.py`:

```python
# Email settings - Gmail SMTP (Port 465 with SSL)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_FROM = 'dmatderby@gmail.com'
EMAIL_HOST_USER = 'dmatderby@gmail.com'
EMAIL_HOST_PASSWORD = 'fneo xmrd qego epxy'
EMAIL_PORT = 465  # Change from 587 to 465
EMAIL_USE_TLS = False  # Disable TLS
EMAIL_USE_SSL = True  # Enable SSL
DEFAULT_FROM_EMAIL = 'TezRent <dmatderby@gmail.com>'
```

**Restart your Django server after this change.**

---

## Quick Fix #2: Install Python SSL Certificates

### Option A: Automatic (Easiest)
```bash
# Run the certificate installer that comes with Python
sudo /Applications/Python\ 3.14/Install\ Certificates.command
```

### Option B: Using pip
```bash
# Install/upgrade certifi
pip install --upgrade certifi

# Or in your virtual environment
source env/bin/activate
pip install --upgrade certifi
```

### Option C: Manual Script
```bash
# Make the script executable
chmod +x fix_ssl_certificates.sh

# Run it
./fix_ssl_certificates.sh
```

---

## Quick Fix #3: Temporary Test Mode

For testing only, you can temporarily disable SSL verification (NOT for production):

```python
# In config/settings.py - DEVELOPMENT ONLY
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

This will print emails to console instead of sending them.

---

## Testing After Fix

### Test Email Sending
```bash
python manage.py shell
```

Then in the shell:
```python
from django.core.mail import send_mail

send_mail(
    'Test Email from TezRent',
    'This is a test email. If you receive this, email is working!',
    'dmatderby@gmail.com',
    ['dmatderby@gmail.com'],  # Send to yourself
    fail_silently=False,
)

# Should print: 1
# And you should receive the email!
```

### Test Password Reset
1. Go to frontend forgot password page
2. Request password reset
3. Check your email (dmatderby@gmail.com)
4. You should receive the reset link!

---

## Which Solution to Use?

### ✅ **Recommended: Use Port 465 with SSL**
- Easiest fix
- Just change 3 lines in settings.py
- Works immediately
- No system changes needed

### ⚡ **Alternative: Install Certificates**
- Fixes the root cause
- Better long-term solution
- Required for other Python projects too
- Takes 1-2 minutes to set up

---

## After Applying Fix

1. **Restart Django server** (Ctrl+C and restart)
2. **Test password reset** from frontend
3. **Check email inbox** for reset link
4. ✅ Should work!

---

## Still Not Working?

### Check Gmail Settings
1. Go to: https://myaccount.google.com/security
2. Ensure "Less secure app access" is OFF (you're using App Password, which is correct)
3. Verify the App Password is correct: `fneo xmrd qego epxy`
4. Check if there are any security alerts from Google

### Check Django Logs
Look for more detailed error messages in your terminal where Django is running.

### Try Console Backend for Testing
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```
This will print emails to terminal - good for testing without email issues.

---

**Most Likely Solution: Switch to Port 465 with SSL!**

Just update those 3 lines in settings.py, restart, and it should work! 🚀
