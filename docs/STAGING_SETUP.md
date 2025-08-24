# Staging Environment Setup Guide

This guide explains how to properly configure the staging environment for the Galveston Reservation System.

## Overview

The staging environment provides a safe testing ground with:

- **Environment-based email routing**: Emails go only to `howard.shen@gmail.com` in staging
- **Separate database**: Isolated from production data
- **Real email testing**: Uses actual Gmail SMTP for testing email functionality
- **Security token validation**: Proper token generation and verification

## Key Configuration Changes Made

### 1. Email Variable Names (CRITICAL)

**Problem**: The original `.env.staging` used `SMTP_*` variables, but Flask-Mail expects `MAIL_*` variables.

**Solution**: Updated all email configuration variables:

```bash
# ❌ OLD (doesn't work with Flask-Mail)
SMTP_SERVER=smtp.gmail.com
SMTP_USERNAME=user@gmail.com
SMTP_PASSWORD=app-password

# ✅ NEW (correct Flask-Mail configuration)
MAIL_SERVER=smtp.gmail.com
MAIL_USERNAME=user@gmail.com
MAIL_PASSWORD=app-password
MAIL_DEFAULT_SENDER=user@gmail.com
```

### 2. Token Secret Consistency (CRITICAL)

**Problem**: The `APPROVAL_TOKEN_SECRET` was different between `.env.staging` and `compose.staging.yaml`, causing token validation failures.

**Solution**: Ensured both files use the same token secret value.

### 3. Gmail Authentication Setup

**Requirements**:

1. Gmail account with 2-Factor Authentication enabled
2. Generated App Password (not regular account password)
3. Proper SMTP configuration

## Setup Instructions

### Step 1: Configure Environment Variables

1. Copy `.env.staging` to your deployment location
2. Update the following variables with real values:

```bash
# Generate a secure 32+ character token secret
APPROVAL_TOKEN_SECRET=your-actual-32-char-secret-here

# Gmail SMTP Configuration
MAIL_USERNAME=your-gmail@gmail.com
MAIL_PASSWORD=your-gmail-app-password
MAIL_DEFAULT_SENDER=your-gmail@gmail.com

# Email routing (staging sends only to howard.shen@gmail.com)
BOOKING_APPROVAL_EMAIL=livingbayfront@gmail.com
BOOKING_NOTIFICATION_EMAILS=livingbayfront@gmail.com
```

### Step 2: Update Docker Compose

1. In `compose.staging.yaml`, update the `APPROVAL_TOKEN_SECRET` to match the one in `.env.staging`

### Step 3: Gmail App Password Setup

1. Go to your Gmail account settings
2. Enable 2-Factor Authentication
3. Generate an App Password:
   - Go to Security → 2-Step Verification → App passwords
   - Generate a new app password for "Mail"
   - Use this 16-character password (remove spaces) for `MAIL_PASSWORD`

### Step 4: Deploy and Test

```bash
# Deploy staging environment
docker compose -f compose.staging.yaml up -d

# Test email functionality
# 1. Submit a booking request at http://your-server:8081
# 2. Check that howard.shen@gmail.com receives the approval email
# 3. Click the approval link to verify token validation works
```

## Environment-Based Email Routing

The system automatically routes emails based on the `FLASK_ENV` variable:

- **Staging** (`FLASK_ENV=staging`): Emails go only to `howard.shen@gmail.com`
- **Production** (`FLASK_ENV=production`): Emails go to all stakeholders

This is implemented in `app/routes/api.py`:

```python
# Use different notification emails based on environment
if os.getenv('FLASK_ENV') == 'staging':
    notification_emails = ['howard.shen@gmail.com']
else:
    # Production environment - send to all stakeholders
    notification_emails = [
        'livingbayfront@gmail.com',
        'info@galvestonislandresortrentals.com', 
        'michelle.kleensweep@gmail.com',
        'alicia.kleensweep@gmail.com'
    ]
```

## Troubleshooting

### "Username and Password not accepted" Error

- Verify Gmail account has 2-Factor Authentication enabled
- Ensure you're using an App Password, not the regular account password
- Check that `MAIL_*` variables are used (not `SMTP_*`)

### "Invalid or expired approval token" Error

- Verify `APPROVAL_TOKEN_SECRET` is identical in both `.env.staging` and `compose.staging.yaml`
- Ensure the token secret is at least 32 characters long
- After changing the token secret, restart containers and submit a new booking request

### Email Not Sending

- Check container logs: `docker compose -f compose.staging.yaml logs app-staging`
- Verify all `MAIL_*` environment variables are set correctly
- Test SMTP connection manually if needed

## Security Notes

- **Never commit real credentials** to the repository
- Use separate App Passwords for staging and production
- Keep token secrets secure and unique per environment
- The staging environment uses HTTP (not HTTPS) for testing convenience
