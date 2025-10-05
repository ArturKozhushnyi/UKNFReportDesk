# 🚀 Registration Feature - Quick Start

## Access the Registration Page

**URL:** `http://localhost:3000/register`

Or click **"Register here"** link on the login page.

---

## 📝 Quick Test

### Register a New User (Frontend)

1. Open browser: `http://localhost:3000/register`
2. Fill in the form:
   - Email: `myuser@example.com`
   - Password: `mypassword123`
   - Confirm Password: `mypassword123`
   - (Optional) Fill First Name, Last Name, Phone, PESEL
3. Click **Register**
4. Wait for success message
5. Auto-redirect to login page
6. Login with your new credentials

### Register via API (cURL)

```bash
curl -X POST http://localhost:3000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "password123",
    "user_name": "Test",
    "user_lastname": "User"
  }' | jq .
```

**Expected Response:**
```json
{
  "message": "User registered successfully with admin privileges",
  "user_id": 5,
  "subject_id": 4,
  "resource_id": "subject:admin:4",
  "admin_group": "admins_of_subject_4",
  "email": "testuser@example.com",
  "uknf_id": "...",
  "status": "User is now administrator of their own subject"
}
```

### Login with New User

```bash
curl -X POST http://localhost:3000/auth/authn \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "password123"
  }' | jq .
```

**Expected Response:**
```json
{
  "session_id": "...",
  "expires_in": 86400
}
```

---

## 🔐 What You Get Automatically

When you register, the system automatically creates:

1. ✅ **User Account** - Your login credentials
2. ✅ **Subject Entity** - Your organization's record
3. ✅ **Admin Group** - `admins_of_subject_<id>`
4. ✅ **Admin Resource** - `subject:admin:<id>`
5. ✅ **Permissions** - Full access to your subject
6. ✅ **Group Membership** - You're automatically an admin

**Result:** You're immediately an administrator of your own isolated subject!

---

## 📋 Required vs Optional Fields

| Field | Required | Example |
|-------|----------|---------|
| Email | ✅ Required | `user@bank.com` |
| Password | ✅ Required | `securepass123` |
| Confirm Password | ✅ Required | `securepass123` |
| First Name | ❌ Optional | `Jan` |
| Last Name | ❌ Optional | `Kowalski` |
| Phone | ❌ Optional | `+48 123 456 789` |
| PESEL | ❌ Optional | `92050812345` |

---

## ✅ Validation Rules

- **Email:** Must be valid format (`user@domain.com`)
- **Password:** Minimum 8 characters
- **Confirm Password:** Must match password
- **PESEL:** If provided, must be exactly 11 digits
- **Phone:** If provided, minimum 9 characters

---

## 🐛 Common Issues

### "User with this email already exists"
→ Use a different email or login with existing account

### "Passwords do not match"
→ Retype both password fields carefully

### "PESEL must be exactly 11 digits"
→ Enter full 11-digit PESEL or leave blank

---

## 📚 Full Documentation

- **Complete Guide:** `REGISTRATION_FEATURE.md`
- **Implementation:** `REGISTRATION_IMPLEMENTATION_SUMMARY.md`
- **Multi-Tenant Info:** `MULTI_TENANT_SECURITY.md`

---

**Status:** ✅ Fully Operational  
**Last Updated:** October 5, 2025

