# Multi-Tenant Security Model Documentation

## 🎯 Overview

A comprehensive multi-tenant security architecture where every new user automatically becomes the administrator of their own isolated "subject" entity. This provides complete data isolation and automatic administrative rights.

---

## 🏗️ Architecture

### Core Concept

**Every user is the admin of their own subject** - When a user registers:
1. A unique subject (entity) is created for them
2. A dedicated resource representing subject admin rights is created
3. An admin group is created specifically for that subject
4. The user is automatically added to the admin group
5. Result: The user has full administrative control over their subject

### Security Model

```
USER
  ↓ (member of)
ADMIN_GROUP (admins_of_subject_<id>)
  ↓ (has permission to)
RESOURCE (subject:admin:<id>)
  ↓ (controls access to)
SUBJECT (entity)
```

---

## 📊 Database Schema Changes

### Migration: 013_add_subject_resource_link.sql

**Adds:**
- `RESOURCE_ID` column to `SUBJECTS` table (varchar(50), nullable)
- Foreign key constraint `SUBJECTS_RESOURCE_ID_FK` → `RESOURCES.ID`
- Index on `RESOURCE_ID` for performance

**Schema:**
```sql
ALTER TABLE "SUBJECTS" ADD COLUMN "RESOURCE_ID" VARCHAR(50);
ALTER TABLE "SUBJECTS" ADD CONSTRAINT "SUBJECTS_RESOURCE_ID_FK" 
    FOREIGN KEY ("RESOURCE_ID") REFERENCES "RESOURCES"("ID");
CREATE INDEX "IDX_SUBJECTS_RESOURCE_ID" ON "SUBJECTS"("RESOURCE_ID");
```

---

## 🔄 Registration Flow

### Atomic Transaction Steps

The `/register` endpoint performs **7 steps in a single transaction**:

#### 1. Create Empty Subject
```python
subject_dict = {
    "NAME_STRUCTURE": f"Subject for user {user_email}",
    "UKNF_ID": shared_uknf_id,
    "STATUS_S": "active",
    "VALIDATED": False,
    "DATE_CREATE": now,
    "DATE_ACTRUALIZATION": now
}
subject_id = db.execute(insert(subjects).values(**subject_dict).returning(subjects.c.ID))
```

#### 2. Create Admin Resource
```python
resource_id = f"subject:admin:{subject_id}"
db.execute(insert(resources).values(ID=resource_id))
```

#### 3. Link Resource to Subject
```python
db.execute(update(subjects).where(subjects.c.ID == subject_id)
          .values(RESOURCE_ID=resource_id))
```

#### 4. Create Admin Group
```python
group_name = f"admins_of_subject_{subject_id}"
group_id = db.execute(insert(groups).values(GROUP_NAME=group_name)
                     .returning(groups.c.ID))
```

#### 5. Grant Permission
```python
db.execute(insert(resources_allow_list).values(
    RESOURCE_ID=resource_id,
    GROUP_ID=group_id
))
```

#### 6. Create User
```python
user_id = db.execute(insert(users).values(**user_dict)
                    .returning(users.c.ID))
```

#### 7. Add User to Admin Group
```python
db.execute(insert(users_groups).values(
    USER_ID=user_id,
    GROUP_ID=group_id
))
```

---

## 📝 Naming Conventions

### Resources
**Pattern:** `subject:admin:<subject_id>`

**Examples:**
- `subject:admin:1` - Admin resource for subject ID 1
- `subject:admin:123` - Admin resource for subject ID 123

### Groups
**Pattern:** `admins_of_subject_<subject_id>`

**Examples:**
- `admins_of_subject_1` - Admin group for subject ID 1
- `admins_of_subject_123` - Admin group for subject ID 123

### Subjects
**Pattern:** `Subject for user <email>`

**Examples:**
- `Subject for user john@example.com`
- `Subject for user admin@company.com`

---

## 🚀 Usage

### Register a New User

**Request:**
```bash
curl -X POST http://localhost:8001/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "securepassword123",
    "user_name": "John",
    "user_lastname": "Doe"
  }'
```

**Response:**
```json
{
  "message": "User registered successfully with admin privileges",
  "user_id": 5,
  "subject_id": 3,
  "resource_id": "subject:admin:3",
  "admin_group": "admins_of_subject_3",
  "email": "newuser@example.com",
  "uknf_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "User is now administrator of their own subject"
}
```

### Check Admin Permissions

**Request:**
```bash
curl -X POST http://localhost:8001/authz \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "<user_session_id>",
    "resource_id": "subject:admin:3"
  }'
```

**Response (Authorized):**
```json
{
  "authorized": true,
  "message": "Access granted (group permission)"
}
```

---

## 🔍 Query Examples

### 1. Find All Subjects a User Can Administer

```sql
SELECT DISTINCT
    s."ID" as subject_id,
    s."NAME_STRUCTURE",
    s."UKNF_ID",
    s."RESOURCE_ID"
FROM "SUBJECTS" s
JOIN "RESOURCES_ALLOW_LIST" ral ON s."RESOURCE_ID" = ral."RESOURCE_ID"
JOIN "USERS_GROUPS" ug ON ral."GROUP_ID" = ug."GROUP_ID"
WHERE ug."USER_ID" = 5;  -- User ID
```

### 2. Find All Admins of a Subject

```sql
SELECT 
    u."ID" as user_id,
    u."EMAIL",
    u."USER_NAME",
    u."USER_LASTNAME",
    g."GROUP_NAME"
FROM "SUBJECTS" s
JOIN "RESOURCES_ALLOW_LIST" ral ON s."RESOURCE_ID" = ral."RESOURCE_ID"
JOIN "GROUPS" g ON ral."GROUP_ID" = g."ID"
JOIN "USERS_GROUPS" ug ON g."ID" = ug."GROUP_ID"
JOIN "USERS" u ON ug."USER_ID" = u."ID"
WHERE s."ID" = 3;  -- Subject ID
```

### 3. Check if User is Admin of Specific Subject

```sql
SELECT 
    CASE 
        WHEN COUNT(*) > 0 THEN 'Yes'
        ELSE 'No'
    END as is_admin
FROM "SUBJECTS" s
JOIN "RESOURCES_ALLOW_LIST" ral ON s."RESOURCE_ID" = ral."RESOURCE_ID"
JOIN "USERS_GROUPS" ug ON ral."GROUP_ID" = ug."GROUP_ID"
WHERE s."ID" = 3          -- Subject ID
  AND ug."USER_ID" = 5;   -- User ID
```

### 4. List All Subject-Admin Relationships

```sql
SELECT 
    s."ID" as subject_id,
    s."NAME_STRUCTURE" as subject_name,
    s."RESOURCE_ID",
    g."GROUP_NAME",
    COUNT(ug."USER_ID") as admin_count
FROM "SUBJECTS" s
LEFT JOIN "RESOURCES_ALLOW_LIST" ral ON s."RESOURCE_ID" = ral."RESOURCE_ID"
LEFT JOIN "GROUPS" g ON ral."GROUP_ID" = g."ID"
LEFT JOIN "USERS_GROUPS" ug ON g."ID" = ug."GROUP_ID"
WHERE s."RESOURCE_ID" IS NOT NULL
GROUP BY s."ID", s."NAME_STRUCTURE", s."RESOURCE_ID", g."GROUP_NAME"
ORDER BY s."ID";
```

### 5. Find Subjects Without Admin Groups (Legacy Data)

```sql
SELECT 
    s."ID",
    s."NAME_STRUCTURE",
    s."UKNF_ID"
FROM "SUBJECTS" s
WHERE s."RESOURCE_ID" IS NULL
ORDER BY s."ID";
```

---

## 🛡️ Security Features

### Data Isolation

**Each user's subject is isolated:**
- User A cannot access User B's subject data
- Access is controlled via resource permissions
- Group membership determines admin rights

### Automatic Admin Rights

**New users automatically get:**
- Their own subject entity
- Administrative control over that subject
- Ability to manage subject data
- Permission to perform subject-related operations

### Extensible Permissions

**Additional permissions can be granted:**
- Add more users to subject admin group
- Create additional resource types for granular control
- Implement role-based access within subject

---

## 📈 Advanced Use Cases

### 1. Add Additional Admin to a Subject

```python
# Add another user as admin of subject 3
db.execute(insert(users_groups).values(
    USER_ID=7,  # New admin user
    GROUP_ID=get_subject_admin_group_id(3)  # Subject 3's admin group
))
db.commit()
```

### 2. Remove Admin Rights

```python
# Remove user from subject admin group
db.execute(delete(users_groups).where(
    (users_groups.c.USER_ID == 7) &
    (users_groups.c.GROUP_ID == get_subject_admin_group_id(3))
))
db.commit()
```

### 3. Transfer Subject Ownership

```python
# Option 1: Add new owner, keep old owner
db.execute(insert(users_groups).values(
    USER_ID=new_owner_id,
    GROUP_ID=subject_admin_group_id
))

# Option 2: Replace owner
db.execute(delete(users_groups).where(
    (users_groups.c.USER_ID == old_owner_id) &
    (users_groups.c.GROUP_ID == subject_admin_group_id)
))
db.execute(insert(users_groups).values(
    USER_ID=new_owner_id,
    GROUP_ID=subject_admin_group_id
))
db.commit()
```

### 4. Create Subject-Specific Resources

```python
# Create additional resources for fine-grained control
resource_id = f"subject:{subject_id}:data:read"
db.execute(insert(resources).values(ID=resource_id))

# Grant permission to a specific group
db.execute(insert(resources_allow_list).values(
    RESOURCE_ID=resource_id,
    GROUP_ID=viewer_group_id
))
```

---

## 🧪 Testing

### Test Script

Create `test_multi_tenant_security.py`:

```python
import requests

BASE_URL = "http://localhost:8001"

def test_registration_creates_admin():
    """Test that new user becomes admin of their subject"""
    
    # Register user
    response = requests.post(f"{BASE_URL}/register", json={
        "email": "test@example.com",
        "password": "testpass123",
        "user_name": "Test",
        "user_lastname": "User"
    })
    
    assert response.status_code == 201
    data = response.json()
    
    # Verify response contains all expected fields
    assert "user_id" in data
    assert "subject_id" in data
    assert "resource_id" in data
    assert "admin_group" in data
    
    # Verify resource ID format
    assert data["resource_id"] == f"subject:admin:{data['subject_id']}"
    
    # Verify admin group format
    assert data["admin_group"] == f"admins_of_subject_{data['subject_id']}"
    
    print(f"✅ User {data['user_id']} is admin of subject {data['subject_id']}")
    
    # Login
    login_response = requests.post(f"{BASE_URL}/authn", json={
        "email": "test@example.com",
        "password": "testpass123"
    })
    
    assert login_response.status_code == 200
    session_id = login_response.json()["session_id"]
    
    # Check authorization for subject admin resource
    authz_response = requests.post(f"{BASE_URL}/authz", json={
        "session_id": session_id,
        "resource_id": data["resource_id"]
    })
    
    assert authz_response.status_code == 200
    authz_data = authz_response.json()
    assert authz_data["authorized"] == True
    
    print(f"✅ User authorized to manage their subject")
    print(f"✅ Multi-tenant security working correctly!")

if __name__ == "__main__":
    test_registration_creates_admin()
```

---

## 🔧 Troubleshooting

### Issue: Registration Fails

**Check migration applied:**
```sql
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'SUBJECTS' AND column_name = 'RESOURCE_ID';
```

**Check foreign key:**
```sql
SELECT conname FROM pg_constraint 
WHERE conname = 'SUBJECTS_RESOURCE_ID_FK';
```

### Issue: User Not Getting Admin Rights

**Verify group creation:**
```sql
SELECT * FROM "GROUPS" 
WHERE "GROUP_NAME" LIKE 'admins_of_subject_%';
```

**Verify user-group link:**
```sql
SELECT * FROM "USERS_GROUPS" 
WHERE "USER_ID" = <user_id>;
```

**Verify permission grant:**
```sql
SELECT * FROM "RESOURCES_ALLOW_LIST" 
WHERE "RESOURCE_ID" LIKE 'subject:admin:%';
```

### Issue: Authorization Fails

**Check resource exists:**
```sql
SELECT * FROM "RESOURCES" 
WHERE "ID" = 'subject:admin:3';
```

**Verify complete chain:**
```sql
-- Full authorization chain
SELECT 
    u."ID" as user_id,
    u."EMAIL",
    ug."GROUP_ID",
    g."GROUP_NAME",
    ral."RESOURCE_ID",
    s."ID" as subject_id,
    s."NAME_STRUCTURE"
FROM "USERS" u
JOIN "USERS_GROUPS" ug ON u."ID" = ug."USER_ID"
JOIN "GROUPS" g ON ug."GROUP_ID" = g."ID"
JOIN "RESOURCES_ALLOW_LIST" ral ON g."ID" = ral."GROUP_ID"
JOIN "SUBJECTS" s ON ral."RESOURCE_ID" = s."RESOURCE_ID"
WHERE u."ID" = <user_id>;
```

---

## 📋 Migration Checklist

- [ ] Apply migration `013_add_subject_resource_link.sql`
- [ ] Verify `RESOURCE_ID` column exists in `SUBJECTS`
- [ ] Verify foreign key constraint exists
- [ ] Deploy updated `auth-service/main.py`
- [ ] Test new user registration
- [ ] Verify admin permissions work
- [ ] Update API documentation
- [ ] Train team on multi-tenant model

---

## 🎓 Best Practices

### 1. Resource Naming
**Always follow the pattern:**
- Subject admin: `subject:admin:<id>`
- Subject read: `subject:read:<id>`
- Subject write: `subject:write:<id>`

### 2. Group Management
**Use descriptive group names:**
- Admins: `admins_of_subject_<id>`
- Editors: `editors_of_subject_<id>`
- Viewers: `viewers_of_subject_<id>`

### 3. Permission Grants
**Grant permissions to groups, not users:**
- Easier to manage
- More scalable
- Better audit trail

### 4. Transaction Safety
**Always use transactions for multi-step operations:**
```python
try:
    # Multiple operations
    db.commit()
except Exception as e:
    db.rollback()
    raise
```

---

## 📊 Performance Considerations

### Indexes
- ✅ Index on `SUBJECTS.RESOURCE_ID` (created by migration)
- ✅ Existing indexes on `USERS_GROUPS`, `RESOURCES_ALLOW_LIST`

### Query Optimization
```sql
-- Use EXISTS for permission checks (faster than JOIN)
SELECT EXISTS (
    SELECT 1
    FROM "USERS_GROUPS" ug
    JOIN "RESOURCES_ALLOW_LIST" ral ON ug."GROUP_ID" = ral."GROUP_ID"
    WHERE ug."USER_ID" = :user_id
      AND ral."RESOURCE_ID" = :resource_id
) as has_permission;
```

---

## 🔗 Related Documentation

- [Database Migrations](migrations/)
- [Authentication Service README](auth-service/README.md)
- [User-Subject Registration](USER_SUBJECT_REGISTRATION.md)
- [Authorization Integration](test_authorization_integration.py)

---

**Version:** 2.0.0  
**Date:** 2025-10-05  
**Status:** Production Ready ✅

