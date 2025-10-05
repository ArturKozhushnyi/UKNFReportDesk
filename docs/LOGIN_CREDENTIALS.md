# 🔐 Login Credentials - Quick Reference

## Available Admin Accounts

### 1. Default Administrator
```
Email:    admin@example.com
Password: admin
Subject:  N/A (legacy admin)
Status:   ✅ Active
```

**Use for:** General system administration and testing

---

### 2. UKNF Administrator
```
Email:    admin_uknf@example.com
Password: password123
Subject:  UKNF (ID: 1)
Group:    admins_of_UKNF
Resource: subject:admin:1
Status:   ✅ Active
```

**Use for:** UKNF subject management and testing multi-tenant security

---

### 3. Bank Pekao Administrator
```
Email:    admin_pekao@example.com
Password: password456
Subject:  Bank Polska Kasa Opieki S.A. (ID: 2)
Group:    admins_of_Bank_Polska_Kasa_Opieki_Spółka_Akcyjna
Resource: subject:admin:2
Status:   ✅ Active
```

**Use for:** Bank Pekao subject management and testing multi-tenant security

---

## 🌐 Access Points

### Frontend
```
URL:      http://localhost:3000
Login:    Use any credentials above
```

### API Endpoints (Direct)

**Auth Service:**
```bash
# Login
curl -X POST http://localhost:8001/authn \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin"}'

# Response
{"session_id": "...", "expires_in": 86400}
```

**Through Frontend Proxy:**
```bash
# Login (same result, through nginx)
curl -X POST http://localhost:3000/auth/authn \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin"}'
```

---

## 🧪 Quick Test

**Test all credentials:**
```bash
# Test 1: Default admin
curl -s -X POST http://localhost:3000/auth/authn \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin"}' | jq .

# Test 2: UKNF admin
curl -s -X POST http://localhost:3000/auth/authn \
  -H "Content-Type: application/json" \
  -d '{"email": "admin_uknf@example.com", "password": "password123"}' | jq .

# Test 3: Bank Pekao admin
curl -s -X POST http://localhost:3000/auth/authn \
  -H "Content-Type: application/json" \
  -d '{"email": "admin_pekao@example.com", "password": "password456"}' | jq .
```

**Expected output for each:** `{"session_id": "...", "expires_in": 86400}`

---

## 🔒 Security Notes

⚠️ **These are DEVELOPMENT/TESTING credentials only!**

**For Production:**
1. Change all passwords immediately
2. Use strong passwords (min 12 chars, mixed case, numbers, symbols)
3. Enable MFA/2FA
4. Implement password rotation policy
5. Monitor admin account activity
6. Use password managers

**Password Requirements:**
- Hashing: sha256_crypt with 535,000 rounds
- Storage: `USERS.PASSWORD_HASH` column
- Validation: Passlib library in Python

**Generate New Password Hash:**
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['sha256_crypt'])
new_hash = pwd_context.hash("your_secure_password")
print(new_hash)
```

---

## 📊 User Permissions

### Default Admin (`admin@example.com`)
- Member of: `administrator` group
- Has access to: Legacy admin resources
- Can: Manage all system resources

### UKNF Admin (`admin_uknf@example.com`)
- Member of: `admins_of_UKNF` group
- Has access to: `subject:admin:1` resource only
- Can: Manage UKNF subject and its data
- Cannot: Access Bank Pekao subject

### Bank Pekao Admin (`admin_pekao@example.com`)
- Member of: `admins_of_Bank_Polska_Kasa_Opieki_Spółka_Akcyjna` group
- Has access to: `subject:admin:2` resource only
- Can: Manage Bank Pekao subject and its data
- Cannot: Access UKNF subject

---

## 🎯 Multi-Tenant Security

Each subject admin can ONLY access their own subject:

```
✅ UKNF admin → subject:admin:1 → ALLOWED
❌ UKNF admin → subject:admin:2 → DENIED

✅ Pekao admin → subject:admin:2 → ALLOWED
❌ Pekao admin → subject:admin:1 → DENIED
```

**Test Isolation:**
```bash
# Login as UKNF admin
SESSION_ID=$(curl -s -X POST http://localhost:8001/authn \
  -H "Content-Type: application/json" \
  -d '{"email": "admin_uknf@example.com", "password": "password123"}' \
  | jq -r '.session_id')

# Try to access UKNF subject (should succeed)
curl -s -X POST http://localhost:8001/authz \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"$SESSION_ID\", \"resource_id\": \"subject:admin:1\"}" \
  | jq .
# Output: {"authorized": true, ...}

# Try to access Pekao subject (should fail)
curl -s -X POST http://localhost:8001/authz \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"$SESSION_ID\", \"resource_id\": \"subject:admin:2\"}" \
  | jq .
# Output: {"authorized": false, ...}
```

---

## 📝 Database Queries

**Find all admin users:**
```sql
SELECT 
    u."ID",
    u."EMAIL",
    u."SUBJECT_ID",
    u."IS_USER_ACTIVE",
    s."NAME_STRUCTURE" as subject_name
FROM "USERS" u
LEFT JOIN "SUBJECTS" s ON u."SUBJECT_ID" = s."ID"
WHERE u."EMAIL" LIKE '%admin%'
ORDER BY u."ID";
```

**Check user permissions:**
```sql
SELECT 
    u."EMAIL",
    g."GROUP_NAME",
    ral."RESOURCE_ID"
FROM "USERS" u
JOIN "USERS_GROUPS" ug ON u."ID" = ug."USER_ID"
JOIN "GROUPS" g ON ug."GROUP_ID" = g."ID"
JOIN "RESOURCES_ALLOW_LIST" ral ON g."ID" = ral."GROUP_ID"
WHERE u."EMAIL" = 'admin_uknf@example.com';
```

---

## 🆘 Troubleshooting

### Login fails with "Invalid email or password"
- Check email is exactly correct (case-sensitive)
- Verify password matches
- Check user is active: `SELECT "IS_USER_ACTIVE" FROM "USERS" WHERE "EMAIL" = '...'`

### Login fails with 502 Bad Gateway
- Check auth-service is running: `docker compose ps auth-service`
- Check nginx proxy config in `frontend/nginx.conf`
- Rebuild frontend if nginx config changed

### Session expires immediately
- Check Redis is running: `docker compose ps redis`
- Verify Redis connection in auth-service logs

---

**Last Updated:** October 5, 2025  
**Status:** ✅ All credentials verified and working  
**Documentation:** See BUGFIX_SUMMARY.md for recent fixes

