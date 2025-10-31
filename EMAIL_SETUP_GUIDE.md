# Email Configuration Guide for TezRent API

## Current Status

**Development Mode:** ✅ Configured  
**Production Mode:** ⚠️ Needs Configuration

---

## Development Setup (Current)

Currently, the API uses **Console Email Backend**, which means:
- Emails are **printed to the terminal/console**
- No actual emails are sent
- Perfect for testing without SMTP setup
- Check your Django server terminal to see password reset links

### Testing Password Reset in Development

1. User requests password reset at frontend
2. API generates reset token
3. **Check your terminal** where Django is running
4. You'll see something like:
```
Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Subject: Password Reset for TezRent
From: TezRent <noreply@tezrent.com>
To: user@example.com

Click the link below to reset your password:
http://localhost:3000/reset-password?token=eyJ0eXAiOiJKV1Qi...

This link expires in 1 hour.
```
5. Copy the token from terminal and test in frontend

---

## Production Setup

### Option 1: Gmail SMTP (Recommended for Small/Medium Traffic)

#### Step 1: Enable 2-Factor Authentication
1. Go to your Google Account: https://myaccount.google.com/
2. Navigate to **Security**
3. Enable **2-Step Verification**

#### Step 2: Generate App Password
1. Go to: https://myaccount.google.com/apppasswords
2. Select **Mail** and **Other (Custom name)**
3. Enter "TezRent API" as the name
4. Click **Generate**
5. Copy the 16-character password (e.g., `abcd efgh ijkl mnop`)

#### Step 3: Update settings.py

```python
# In config/settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-actual-email@gmail.com'  # Your Gmail address
EMAIL_HOST_PASSWORD = 'abcdefghijklmnop'  # The 16-char app password (no spaces)
DEFAULT_FROM_EMAIL = 'TezRent <noreply@tezrent.com>'
```

**Important:** 
- Use your actual Gmail address for `EMAIL_HOST_USER`
- Use the app password (not your regular Gmail password)
- Remove spaces from app password

#### Step 4: Test

```bash
# In Django shell
python manage.py shell

from django.core.mail import send_mail
send_mail(
    'Test Email',
    'This is a test email from TezRent API.',
    'your-actual-email@gmail.com',
    ['recipient@example.com'],
    fail_silently=False,
)
```

---

### Option 2: SendGrid (Recommended for Production/High Volume)

SendGrid offers **100 emails/day for FREE**, perfect for production.

#### Step 1: Create SendGrid Account
1. Sign up at: https://signup.sendgrid.com/
2. Verify your email
3. Complete setup wizard

#### Step 2: Create API Key
1. Go to: https://app.sendgrid.com/settings/api_keys
2. Click **Create API Key**
3. Name it "TezRent API"
4. Select **Full Access** or **Mail Send** only
5. Copy the API key (starts with `SG.`)

#### Step 3: Install SendGrid Package

```bash
pip install sendgrid
```

#### Step 4: Update settings.py

```python
# In config/settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'  # This is literally the string 'apikey'
EMAIL_HOST_PASSWORD = 'SG.your-actual-sendgrid-api-key'  # Your SendGrid API key
DEFAULT_FROM_EMAIL = 'TezRent <noreply@tezrent.com>'

# Optional: Verify sender email in SendGrid dashboard
# Go to Settings > Sender Authentication
```

#### Step 5: Verify Sender Email
1. In SendGrid dashboard, go to **Settings** > **Sender Authentication**
2. Verify your domain OR single sender email
3. For single sender: Use an email you control (e.g., `noreply@yourdomain.com`)

---

### Option 3: AWS SES (For High Volume + Low Cost)

AWS Simple Email Service is extremely cost-effective for high volumes.

#### Pricing
- $0.10 per 1,000 emails
- First 62,000 emails/month FREE if hosted on AWS EC2

#### Setup Steps

1. **Create AWS Account**: https://aws.amazon.com/
2. **Verify Email/Domain** in SES Console
3. **Create SMTP Credentials** in SES Console
4. **Request Production Access** (initially in sandbox mode)

#### Configuration

```python
# In config/settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'email-smtp.us-east-1.amazonaws.com'  # Your SES region
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'AKIAIOSFODNN7EXAMPLE'  # Your SES SMTP username
EMAIL_HOST_PASSWORD = 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'  # Your SES SMTP password
DEFAULT_FROM_EMAIL = 'TezRent <noreply@tezrent.com>'
```

---

### Option 4: Mailgun

Another popular option with 5,000 free emails/month.

#### Setup
1. Sign up at: https://www.mailgun.com/
2. Verify your domain or use sandbox domain
3. Get SMTP credentials

#### Configuration

```python
# In config/settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'postmaster@yourdomain.mailgun.org'
EMAIL_HOST_PASSWORD = 'your-mailgun-password'
DEFAULT_FROM_EMAIL = 'TezRent <noreply@tezrent.com>'
```

---

## Environment Variables (Recommended for Production)

**Never commit credentials to Git!** Use environment variables:

### Step 1: Create .env file

```bash
# In project root, create .env file
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Step 2: Install python-decouple

```bash
pip install python-decouple
```

### Step 3: Update settings.py

```python
from decouple import config

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='TezRent <noreply@tezrent.com>')
```

### Step 4: Add .env to .gitignore

```bash
echo ".env" >> .gitignore
```

---

## Custom Email Templates

### Create Email Templates Directory

```bash
mkdir -p templates/emails
```

### Password Reset Email Template

Create `templates/emails/password_reset.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background-color: #2563EB; color: white; padding: 20px; text-align: center; }
        .content { padding: 30px; background-color: #f9f9f9; }
        .button { display: inline-block; padding: 12px 30px; background-color: #2563EB; 
                  color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }
        .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>TezRent</h1>
        </div>
        <div class="content">
            <h2>Password Reset Request</h2>
            <p>Hello,</p>
            <p>You requested to reset your password for your TezRent account.</p>
            <p>Click the button below to reset your password:</p>
            <a href="{{ reset_link }}" class="button">Reset Password</a>
            <p>Or copy and paste this link into your browser:</p>
            <p style="word-break: break-all; color: #2563EB;">{{ reset_link }}</p>
            <p><strong>This link will expire in 1 hour.</strong></p>
            <p>If you didn't request this password reset, please ignore this email.</p>
        </div>
        <div class="footer">
            <p>&copy; 2025 TezRent. All rights reserved.</p>
            <p>This is an automated email. Please do not reply.</p>
        </div>
    </div>
</body>
</html>
```

### Update Views to Use Template

```python
# In accounts/views.py
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        
        try:
            user = User.objects.get(email=email)
            
            # Generate token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Create reset link
            frontend_url = "http://localhost:3000"  # Change for production
            reset_link = f"{frontend_url}/reset-password?token={token}&uid={uid}"
            
            # Render HTML email
            html_content = render_to_string('emails/password_reset.html', {
                'reset_link': reset_link,
                'user': user
            })
            
            # Plain text fallback
            text_content = f"Click the link to reset your password: {reset_link}\n\nThis link expires in 1 hour."
            
            # Send email with both HTML and text
            email_message = EmailMultiAlternatives(
                subject='Password Reset for TezRent',
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email]
            )
            email_message.attach_alternative(html_content, "text/html")
            email_message.send()
            
            return Response({
                'message': 'Password reset email sent.'
            })
            
        except User.DoesNotExist:
            # Return success anyway for security
            return Response({
                'message': 'Password reset email sent.'
            })
```

---

## Testing Email Configuration

### Test Script

Create `test_email.py`:

```python
from django.core.mail import send_mail
from django.conf import settings

def test_email():
    try:
        send_mail(
            subject='TezRent API - Test Email',
            message='This is a test email. If you receive this, your email configuration is working!',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['your-test-email@example.com'],
            fail_silently=False,
        )
        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Email failed: {str(e)}")

if __name__ == "__main__":
    import django
    django.setup()
    test_email()
```

Run test:
```bash
python test_email.py
```

---

## Troubleshooting

### Gmail: "Username and Password not accepted"
**Solution:** 
- Ensure 2FA is enabled
- Use App Password, not regular password
- Check for typos in credentials

### "SMTPAuthenticationError"
**Solution:**
- Verify credentials are correct
- Check if account has SMTP access enabled
- Try regenerating app password

### Emails going to spam
**Solution:**
- Verify sender email/domain
- Add SPF and DKIM records to DNS
- Use a verified sending domain
- Avoid spam trigger words in subject/body

### "Connection refused"
**Solution:**
- Check firewall settings
- Verify port (587 or 465) is open
- Try alternative ports (Gmail: 465 for SSL)

### Rate Limits
**Solution:**
- Gmail: Max 500 emails/day
- Use SendGrid or AWS SES for higher volumes
- Implement email queuing with Celery

---

## Recommended Email Service by Use Case

| Use Case | Recommended Service | Reason |
|----------|-------------------|---------|
| Development/Testing | Console Backend | Free, instant, no setup |
| Small Business (<100 emails/day) | Gmail SMTP | Free, reliable, easy setup |
| Medium Business (100-10k emails/day) | SendGrid Free | 100/day free, professional |
| High Volume (10k+ emails/day) | AWS SES | Cheapest, most scalable |
| Transactional Emails | SendGrid/Mailgun | Best deliverability |
| Marketing Emails | SendGrid/Mailchimp | Built-in analytics |

---

## Security Best Practices

1. **Never commit credentials** - Use environment variables
2. **Use App Passwords** - Not your main account password
3. **Enable 2FA** - On your email service account
4. **Rotate credentials** - Change passwords periodically
5. **Monitor usage** - Check for suspicious activity
6. **Rate limiting** - Prevent abuse of password reset
7. **HTTPS only** - Never send emails over HTTP
8. **Verify recipients** - Prevent email injection attacks

---

## Next Steps

1. ✅ **Development:** Already configured (console backend)
2. ⏳ **Choose email service** for production (Gmail, SendGrid, AWS SES)
3. ⏳ **Set up account** with chosen service
4. ⏳ **Update settings.py** with credentials
5. ⏳ **Test email sending** with test script
6. ⏳ **Create HTML templates** for better-looking emails
7. ⏳ **Deploy to production** with environment variables

---

**For now, your password reset works in development mode!** Check the Django terminal to see the reset links when testing.

**Last Updated:** October 23, 2025
