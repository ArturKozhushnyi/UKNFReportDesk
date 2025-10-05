# Mock Subject Admin Users Documentation

## 🎯 Overview

Pre-configured administrative users for the existing UKNF and Bank Pekao subjects, complete with groups, resources, and permissions.

---

## 👥 Created Admin Users

### 1. UKNF Administrator

**Email:** `admin_uknf@example.com`  
**Password:** `password123`  
**Subject ID:** 1 (UKNF)  
**Admin Group:** `admins_of_UKNF`  
**Resource:** `subject:admin:1`

**Permissions:**
- Full administrative control over UKNF subject
- Can manage UKNF subject data
- Can access all UKNF-related resources

### 2. Bank Pekao Administrator

**Email:** `admin_pekao@example.com`  
**Password:** `password456`  
**Subject ID:** 2 (Bank Polska Kasa Opieki S.A.)  
**Admin Group:** `admins_of_Bank_Polska_Kasa_Opieki_Spółka_Akcyjna`  
**Resource:** `subject:admin:2`

**Permissions:**
- Full administrative control over Bank Pekao subject
- Can manage Bank Pekao subject data
- Can access all Bank Pekao-related resources

---

## 📦 What Gets Created

### For Each Subject:

1. **Admin Group** - Dedicated group for subject administrators
2. **Admin Resource** - Resource representing admin access (`subject:admin:<id>`)
3. **Resource Link** - Links subject to its admin resource
4. **Permission Grant** - Grants group access to resource
5. **Admin User** - User account with proper password hash
6. **Group Membership** - Links user to admin group

### Complete Setup Chain:

```
ADMIN USER
    ↓ (member of)
ADMIN GROUP (admins_of_<subject>)
    ↓ (has permission to)
ADMIN RESOURCE (subject:admin:<id>)
    ↓ (controls)
SUBJECT (entity)
```

---

## 🚀 Usage

### Login as UKNF Admin

**cURL:**
```bash
curl -X POST http://localhost:8001/authn \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin_uknf@example.com",
    "password": "password123"
  }'
```

**Python:**
```python
import requests

response = requests.post(
    "http://localhost:8001/authn",
    json={
        "email": "admin_uknf@example.com",
        "password": "password123"
    }
)

session_id = response.json()["session_id"]
print(f"Logged in with session: {session_id}")
```

### Login as Bank Pekao Admin

**cURL:**
```bash
curl -X POST http://localhost:8001/authn \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin_pekao@example.com",
    "password": "password456"
  }'
```

### Check Authorization

**Test UKNF admin can access UKNF subject:**
```bash
# First, login to get session_id
SESSION_ID="<session_id_from_login>"

curl -X POST http://localhost:8001/authz \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"resource_id\": \"subject:admin:1\"
  }"
```

**Expected Response:**
```json
{
  "authorized": true,
  "message": "Access granted (group permission)"
}
```

**Test cross-subject access (should fail):**
```bash
# UKNF admin trying to access Bank Pekao subject
curl -X POST http://localhost:8001/authz \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"resource_id\": \"subject:admin:2\"
  }"
```

**Expected Response:**
```json
{
  "authorized": false,
  "message": "Access denied"
}
```

---

## 🔍 Database Verification

### Verify UKNF Admin Setup

```sql
-- Check complete permission chain
SELECT 
    u."ID" as user_id,
    u."EMAIL",
    u."SUBJECT_ID",
    g."ID" as group_id,
    g."GROUP_NAME",
    ral."RESOURCE_ID",
    s."ID" as subject_id,
    s."NAME_STRUCTURE"
FROM "USERS" u
JOIN "USERS_GROUPS" ug ON u."ID" = ug."USER_ID"
JOIN "GROUPS" g ON ug."GROUP_ID" = g."ID"
JOIN "RESOURCES_ALLOW_LIST" ral ON g."ID" = ral."GROUP_ID"
JOIN "SUBJECTS" s ON ral."RESOURCE_ID" = s."RESOURCE_ID"
WHERE u."EMAIL" = 'admin_uknf@example.com';
```

### Verify Bank Pekao Admin Setup

```sql
SELECT 
    u."ID" as user_id,
    u."EMAIL",
    u."SUBJECT_ID",
    g."ID" as group_id,
    g."GROUP_NAME",
    ral."RESOURCE_ID",
    s."ID" as subject_id,
    s."NAME_STRUCTURE"
FROM "USERS" u
JOIN "USERS_GROUPS" ug ON u."ID" = ug."USER_ID"
JOIN "GROUPS" g ON ug."GROUP_ID" = g."ID"
JOIN "RESOURCES_ALLOW_LIST" ral ON g."ID" = ral."GROUP_ID"
JOIN "SUBJECTS" s ON ral."RESOURCE_ID" = s."RESOURCE_ID"
WHERE u."EMAIL" = 'admin_pekao@example.com';
```

### List All Subject Admin Groups

```sql
SELECT 
    g."ID",
    g."GROUP_NAME",
    ral."RESOURCE_ID",
    s."NAME_STRUCTURE" as subject_name,
    COUNT(ug."USER_ID") as member_count
FROM "GROUPS" g
JOIN "RESOURCES_ALLOW_LIST" ral ON g."ID" = ral."GROUP_ID"
LEFT JOIN "SUBJECTS" s ON ral."RESOURCE_ID" = s."RESOURCE_ID"
LEFT JOIN "USERS_GROUPS" ug ON g."ID" = ug."GROUP_ID"
WHERE g."GROUP_NAME" LIKE 'admins_of_%'
GROUP BY g."ID", g."GROUP_NAME", ral."RESOURCE_ID", s."NAME_STRUCTURE"
ORDER BY g."ID";
```

### Check Subject-Resource Links

```sql
SELECT 
    s."ID",
    s."NAME_STRUCTURE",
    s."RESOURCE_ID",
    r."ID" as resource_exists
FROM "SUBJECTS" s
LEFT JOIN "RESOURCES" r ON s."RESOURCE_ID" = r."ID"
WHERE s."ID" IN (1, 2)
ORDER BY s."ID";
```

---

## 🔧 Installation

### Apply Migration

**Using Docker Compose:**
```bash
docker-compose down
docker-compose up -d
# Migration runs automatically
```

**Manual Application:**
```bash
psql -U myuser -d mydatabase -f migrations/014_add_mock_subject_admins.sql
```

### Verify Installation

```bash
# Run the test script
python test_mock_admin_users.py
```

---

## 🧪 Testing

### Quick Test Script

```python
import requests

AUTH_URL = "http://localhost:8001"

def test_admin_login(email, password, expected_subject_resource):
    """Test admin login and authorization"""
    
    # Login
    response = requests.post(f"{AUTH_URL}/authn", json={
        "email": email,
        "password": password
    })
    
    if response.status_code != 200:
        print(f"❌ Login failed for {email}")
        return False
    
    session_id = response.json()["session_id"]
    print(f"✅ Logged in: {email}")
    
    # Check authorization for their own subject
    response = requests.post(f"{AUTH_URL}/authz", json={
        "session_id": session_id,
        "resource_id": expected_subject_resource
    })
    
    if response.json().get("authorized"):
        print(f"✅ Authorized for {expected_subject_resource}")
        return True
    else:
        print(f"❌ Not authorized for {expected_subject_resource}")
        return False

# Test UKNF admin
print("Testing UKNF Administrator...")
test_admin_login("admin_uknf@example.com", "password123", "subject:admin:1")

print("\nTesting Bank Pekao Administrator...")
test_admin_login("admin_pekao@example.com", "password456", "subject:admin:2")
```

---

## 🔐 Security Considerations

### ⚠️ IMPORTANT: Development Only

These are **mock/test credentials** for development:
- ❌ **DO NOT** use in production
- ❌ **DO NOT** commit passwords to repository
- ❌ **DO NOT** share these credentials

### Production Recommendations

1. **Change Passwords Immediately**
   ```python
   from passlib.context import CryptContext
   pwd_context = CryptContext(schemes=["sha256_crypt"])
   new_hash = pwd_context.hash("your_strong_password_here")
   ```

2. **Use Strong Passwords**
   - Minimum 12 characters
   - Mix of uppercase, lowercase, numbers, symbols
   - Not dictionary words
   - Unique per account

3. **Enable Additional Security**
   - Implement MFA/2FA
   - Use temporary passwords with forced reset
   - Enable account lockout after failed attempts
   - Monitor admin activity

4. **Password Rotation**
   - Rotate admin passwords every 90 days
   - Keep password history to prevent reuse
   - Use password managers

### Password Hashing

**Current Setup:**
- Algorithm: `sha256_crypt`
- Rounds: 535,000
- Library: `passlib` (Python)

**Generate New Hash:**
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
new_hash = pwd_context.hash("your_new_password")
print(new_hash)
```

**Update Password in Database:**
```sql
UPDATE "USERS"
SET "PASSWORD_HASH" = '<new_hash_here>'
WHERE "EMAIL" = 'admin_uknf@example.com';
```

---

## 📋 Troubleshooting

### Issue: Login Fails

**Check user exists:**
```sql
SELECT "ID", "EMAIL", "IS_USER_ACTIVE"
FROM "USERS"
WHERE "EMAIL" IN ('admin_uknf@example.com', 'admin_pekao@example.com');
```

**Check password hash:**
```sql
SELECT "EMAIL", LENGTH("PASSWORD_HASH") as hash_length
FROM "USERS"
WHERE "EMAIL" IN ('admin_uknf@example.com', 'admin_pekao@example.com');
-- Hash length should be around 90-100 characters for sha256_crypt
```

### Issue: Authorization Fails

**Check group membership:**
```sql
SELECT u."EMAIL", g."GROUP_NAME"
FROM "USERS" u
JOIN "USERS_GROUPS" ug ON u."ID" = ug."USER_ID"
JOIN "GROUPS" g ON ug."GROUP_ID" = g."ID"
WHERE u."EMAIL" IN ('admin_uknf@example.com', 'admin_pekao@example.com');
```

**Check resource permissions:**
```sql
SELECT g."GROUP_NAME", ral."RESOURCE_ID"
FROM "GROUPS" g
JOIN "RESOURCES_ALLOW_LIST" ral ON g."ID" = ral."GROUP_ID"
WHERE g."GROUP_NAME" LIKE 'admins_of_%';
```

**Check subject-resource links:**
```sql
SELECT "ID", "NAME_STRUCTURE", "RESOURCE_ID"
FROM "SUBJECTS"
WHERE "ID" IN (1, 2);
```

### Issue: Migration Fails

**Check if already applied:**
```sql
-- Check if groups exist
SELECT "GROUP_NAME" FROM "GROUPS"
WHERE "GROUP_NAME" IN ('admins_of_UKNF', 'admins_of_Bank_Polska_Kasa_Opieki_Spółka_Akcyjna');

-- Check if users exist
SELECT "EMAIL" FROM "USERS"
WHERE "EMAIL" IN ('admin_uknf@example.com', 'admin_pekao@example.com');
```

**Rollback if needed:**
```sql
-- Remove users
DELETE FROM "USERS"
WHERE "EMAIL" IN ('admin_uknf@example.com', 'admin_pekao@example.com');

-- Remove groups
DELETE FROM "GROUPS"
WHERE "GROUP_NAME" IN ('admins_of_UKNF', 'admins_of_Bank_Polska_Kasa_Opieki_Spółka_Akcyjna');

-- Remove resources
DELETE FROM "RESOURCES"
WHERE "ID" IN ('subject:admin:1', 'subject:admin:2');

-- Clear subject resource links
UPDATE "SUBJECTS"
SET "RESOURCE_ID" = NULL
WHERE "ID" IN (1, 2);
```

---

## 📊 Summary

### Created Objects

| Object Type | UKNF | Bank Pekao |
|-------------|------|------------|
| **Group** | `admins_of_UKNF` | `admins_of_Bank_Polska_Kasa_Opieki_Spółka_Akcyjna` |
| **Resource** | `subject:admin:1` | `subject:admin:2` |
| **User** | `admin_uknf@example.com` | `admin_pekao@example.com` |
| **Password** | `password123` | `password456` |
| **Subject ID** | 1 | 2 |

### Permissions Flow

```
admin_uknf@example.com
    → admins_of_UKNF
        → subject:admin:1
            → UKNF Subject (ID: 1)

admin_pekao@example.com
    → admins_of_Bank_Polska_Kasa_Opieki_Spółka_Akcyjna
        → subject:admin:2
            → Bank Pekao Subject (ID: 2)
```

---

## 🔗 Related Documentation

- [Multi-Tenant Security](MULTI_TENANT_SECURITY.md)
- [User-Subject Registration](USER_SUBJECT_REGISTRATION.md)
- [Authentication Service README](auth-service/README.md)
- [Database Migrations](migrations/)

---

**Migration File:** `migrations/014_add_mock_subject_admins.sql`  
**Version:** 1.0.0  
**Date:** 2025-10-05  
**Status:** Development/Testing Only ⚠️

**⚠️ Remember: Change passwords before production use!**

