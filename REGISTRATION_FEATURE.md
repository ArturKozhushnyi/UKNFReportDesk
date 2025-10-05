# 📝 User Registration Feature Documentation

## Overview

The UKNF Report Desk now includes a comprehensive user registration system with automatic subject creation and multi-tenant security setup. Every new user automatically becomes an administrator of their own dedicated subject entity.

---

## 🎯 Features

### User-Facing Features
- ✅ **Clean, intuitive registration form** matching the existing login page design
- ✅ **Real-time form validation** with helpful error messages
- ✅ **Password confirmation** to prevent typos
- ✅ **Optional fields** for phone and PESEL
- ✅ **Success message** with automatic redirect to login
- ✅ **Pre-filled email** on login page after registration
- ✅ **Loading states** and visual feedback during submission

### Backend Features
- ✅ **Automatic subject creation** for each new user
- ✅ **Multi-tenant security** - each user gets their own admin group and resource
- ✅ **Atomic transaction** - all operations succeed or fail together
- ✅ **Unique UUID generation** for user-subject relationship
- ✅ **PESEL privacy** - automatic masking when displayed
- ✅ **Password hashing** using sha256_crypt with 535,000 rounds

---

## 📋 Form Fields

| Field | Required | Validation | Description |
|-------|----------|------------|-------------|
| **Email** | ✅ Yes | Valid email format | User's email address (also username) |
| **Password** | ✅ Yes | Min 8 characters | Account password |
| **Confirm Password** | ✅ Yes | Must match password | Password confirmation |
| **First Name** | ❌ No | - | User's first name |
| **Last Name** | ❌ No | - | User's last name |
| **Phone** | ❌ No | Min 9 chars if provided | Contact phone number |
| **PESEL** | ❌ No | Exactly 11 digits if provided | Polish national ID |

---

## 🌐 Access Points

### Frontend Routes

**Registration Page:**
```
URL: http://localhost:3000/register
Direct access or via "Register here" link on login page
```

**Login Page:**
```
URL: http://localhost:3000/login
Contains "Don't have an account? Register here" link
```

### API Endpoints

**Direct Registration:**
```bash
curl -X POST http://localhost:8001/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "user_name": "John",
    "user_lastname": "Doe",
    "phone": "+48 123 456 789",
    "pesel": "92050812345"
  }'
```

**Through Frontend Proxy:**
```bash
curl -X POST http://localhost:3000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "user_name": "John",
    "user_lastname": "Doe"
  }'
```

---

## 🔄 Registration Flow

### User Experience

```
1. User visits /register
   ↓
2. Fills out registration form
   ↓
3. Clicks "Register" button
   ↓
4. System validates input
   ↓
5. Success message appears
   ↓
6. Auto-redirect to /login after 2 seconds
   ↓
7. Email pre-filled, success message shown
   ↓
8. User logs in with new credentials
```

### Backend Process

```
1. Receive registration request
   ↓
2. Validate email is unique
   ↓
3. Generate shared UUID
   ↓
4. BEGIN TRANSACTION
   ├─ Create empty subject
   ├─ Create admin resource (subject:admin:<id>)
   ├─ Link subject to resource
   ├─ Create admin group (admins_of_subject_<id>)
   ├─ Grant group permission to resource
   ├─ Create user account
   └─ Add user to admin group
   ↓
5. COMMIT TRANSACTION
   ↓
6. Return success response
```

---

## 📤 API Response Format

### Successful Registration

```json
{
  "message": "User registered successfully with admin privileges",
  "user_id": 4,
  "subject_id": 3,
  "resource_id": "subject:admin:3",
  "admin_group": "admins_of_subject_3",
  "email": "test@example.com",
  "uknf_id": "4029cd25-f354-4569-b54f-b9589eca3999",
  "status": "User is now administrator of their own subject"
}
```

### Error Response

```json
{
  "detail": "User with this email already exists"
}
```

---

## 🎨 UI/UX Features

### Visual Design
- **Consistent styling** with LoginPage
- **Blue gradient background** (matching brand colors)
- **Centered white card** with shadow
- **Icon-based header** with UserPlus icon
- **Two-column layout** for related fields (responsive)
- **Tailwind CSS** for modern, responsive design

### User Feedback
- **Info box** explaining subject creation
- **Success message** with checkmark icon
- **Error messages** with alert icon
- **Loading spinner** during submission
- **Button state changes** (loading, success, default)
- **Input validation** with helpful hints

### Accessibility
- **Proper labels** for all form fields
- **Required field indicators** (red asterisk)
- **Placeholder text** for guidance
- **Disabled state** when submitting
- **Keyboard navigation** support

---

## 🔐 Security Features

### Password Security
- **Minimum 8 characters** enforced
- **Client-side validation** before submission
- **Server-side hashing** using sha256_crypt
- **535,000 rounds** for brute-force resistance
- **Password confirmation** prevents typos

### PESEL Privacy
- **Optional field** - users can skip
- **Format validation** - must be 11 digits
- **Automatic masking** when displayed (`*******2345`)
- **Never exposed** in API responses

### Multi-Tenant Isolation
- **Automatic subject creation** for each user
- **Dedicated admin group** per subject
- **Unique resource ID** per subject
- **Permission isolation** - can only access own subject
- **Atomic transaction** - all-or-nothing creation

---

## 🧪 Testing

### Manual Testing

**Test 1: Successful Registration**
```bash
# Navigate to http://localhost:3000/register
# Fill in all fields with valid data
# Click "Register"
# Expected: Success message, redirect to login
```

**Test 2: Duplicate Email**
```bash
# Try to register with existing email
# Expected: Error message "User with this email already exists"
```

**Test 3: Password Mismatch**
```bash
# Enter different passwords in password fields
# Expected: Error "Passwords do not match"
```

**Test 4: Invalid PESEL**
```bash
# Enter PESEL with less than 11 digits
# Expected: Error "PESEL must be exactly 11 digits"
```

### Automated Testing

```bash
# Test registration via API
curl -X POST http://localhost:3000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "securepass123",
    "user_name": "New",
    "user_lastname": "User"
  }' | jq .

# Expected output includes:
# - user_id
# - subject_id
# - resource_id
# - admin_group
# - uknf_id
```

### Test Login After Registration

```bash
# After registration, test login
curl -X POST http://localhost:3000/auth/authn \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "securepass123"
  }' | jq .

# Expected: session_id returned
```

---

## 📁 Files Created/Modified

### New Files

**`frontend/src/pages/RegistrationPage.tsx`**
- Complete registration form component
- Form validation logic
- API integration
- Success/error handling
- 330+ lines of TypeScript/React code

### Modified Files

**`frontend/src/App.tsx`**
- Added import for `RegistrationPage`
- Added route: `/register`

**`frontend/src/pages/LoginPage.tsx`**
- Added registration success message display
- Added "Register here" link
- Pre-fill email from registration
- Display success message from registration redirect

---

## 🎯 Use Cases

### For New Organizations

**Scenario:** A new bank wants to access the UKNF Report Desk

1. Navigate to registration page
2. Fill in organization details
3. Register account
4. Automatic subject entity created
5. Login with new credentials
6. Start submitting reports

### For Additional Users (Future)

Currently, each registration creates a new subject. For adding users to existing subjects:

1. **Admin invites user** (future feature)
2. User receives invitation link
3. Registers with special token
4. Gets added to existing subject
5. Inherits appropriate permissions

---

## 🔍 Validation Rules

### Email Validation
```typescript
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
```
- Must contain `@` symbol
- Must have domain part
- No whitespace allowed

### Password Validation
```typescript
password.length >= 8
```
- Minimum 8 characters
- No complexity requirements (can be enhanced)

### PESEL Validation
```typescript
/^\d{11}$/.test(pesel)
```
- Must be exactly 11 digits
- Only digits allowed
- Optional field

### Phone Validation
```typescript
phone.length >= 9
```
- Minimum 9 characters
- No specific format enforced
- Optional field

---

## 🚀 Future Enhancements

### Planned Features

1. **Email Verification**
   - Send confirmation email
   - Verify email before activation
   - Resend verification link

2. **Password Strength Meter**
   - Visual indicator of password strength
   - Suggest improvements
   - Enforce complexity rules

3. **Organization Details**
   - Add organization name during registration
   - Add organization type (bank, insurance, etc.)
   - Pre-populate subject data

4. **Invitation System**
   - Invite users to existing subjects
   - Role selection during invite
   - Token-based registration

5. **CAPTCHA Integration**
   - Prevent automated registrations
   - Google reCAPTCHA v3
   - Invisible to most users

6. **Terms & Conditions**
   - Accept terms checkbox
   - Privacy policy link
   - GDPR compliance

---

## 🐛 Troubleshooting

### "User with this email already exists"
- **Cause:** Email is already registered
- **Solution:** Use different email or login with existing account

### Registration hangs/doesn't complete
- **Check:** Auth service is running
- **Check:** Database is accessible
- **Check:** Network connectivity
- **Check:** Browser console for errors

### Validation errors not showing
- **Check:** Client-side validation is enabled
- **Check:** Form fields have correct `name` attributes
- **Check:** State updates are working

### Not redirected to login after success
- **Check:** Navigation state is being passed
- **Check:** Timeout is completing (2 seconds)
- **Check:** React Router is configured correctly

---

## 📊 Database Impact

### Tables Affected

**New Data Created:**

1. **SUBJECTS table**
   - One new row per registration
   - Links to USERS via SUBJECT_ID
   - Links to RESOURCES via RESOURCE_ID

2. **USERS table**
   - One new row per registration
   - Password hashed with sha256_crypt
   - PESEL stored (will be masked on display)

3. **GROUPS table**
   - One new admin group per registration
   - Named: `admins_of_subject_<id>`

4. **RESOURCES table**
   - One new resource per registration
   - ID format: `subject:admin:<subject_id>`

5. **RESOURCES_ALLOW_LIST table**
   - One permission entry per registration
   - Links group to resource

6. **USERS_GROUPS table**
   - One membership entry per registration
   - Links user to their admin group

### Sample Data After Registration

```sql
-- USERS table
ID | EMAIL                  | SUBJECT_ID | UKNF_ID
4  | test@example.com      | 3          | 4029cd25-...

-- SUBJECTS table
ID | NAME_STRUCTURE         | RESOURCE_ID       | UKNF_ID
3  | Subject for user...   | subject:admin:3   | 4029cd25-...

-- GROUPS table
ID | GROUP_NAME
4  | admins_of_subject_3

-- RESOURCES table
ID
subject:admin:3

-- RESOURCES_ALLOW_LIST table
RESOURCE_ID        | GROUP_ID
subject:admin:3    | 4

-- USERS_GROUPS table
USER_ID | GROUP_ID
4       | 4
```

---

## 🔗 Related Documentation

- **[MULTI_TENANT_SECURITY.md](MULTI_TENANT_SECURITY.md)** - Multi-tenant architecture details
- **[USER_SUBJECT_REGISTRATION_REFACTOR.md](USER_SUBJECT_REGISTRATION_REFACTOR.md)** - Backend registration logic
- **[LOGIN_CREDENTIALS.md](LOGIN_CREDENTIALS.md)** - Available test accounts
- **[BUGFIX_SUMMARY.md](BUGFIX_SUMMARY.md)** - Recent bug fixes (nginx proxy)

---

## ✅ Summary

The registration feature is now **fully operational** with:

- ✅ Beautiful, responsive UI matching the existing design
- ✅ Comprehensive form validation
- ✅ Automatic subject and permission setup
- ✅ Multi-tenant security out of the box
- ✅ Seamless user experience with success messages
- ✅ Full integration with existing login system
- ✅ Production-ready error handling
- ✅ TypeScript type safety
- ✅ No linter errors

**Ready for production use! 🎉**

---

**Created:** October 5, 2025  
**Version:** 1.0.0  
**Status:** ✅ Production Ready

