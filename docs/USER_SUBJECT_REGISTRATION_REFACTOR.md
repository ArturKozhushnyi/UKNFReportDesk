# User Registration Refactor - Automatic Subject Creation

## Overview

The user registration process in the `auth-service` has been refactored to automatically create and associate an empty `SUBJECT` record for each new user. This ensures every new user is linked to a unique, newly created subject entity from the moment of registration through a single, atomic database transaction.

## Changes Made

### 1. Database Schema Changes

#### Migration: `010_add_subject_id_to_users.sql`
- **Added `SUBJECT_ID` column** to the `USERS` table as a foreign key to `SUBJECTS.ID`
- **Added foreign key constraint** with `ON DELETE SET NULL` behavior
- **Added index** for performance optimization
- **Column is nullable** to maintain backward compatibility

```sql
ALTER TABLE "USERS" 
ADD COLUMN "SUBJECT_ID" BIGINT;

ALTER TABLE "USERS" 
ADD CONSTRAINT "USERS_SUBJECT_ID_FK" 
FOREIGN KEY ("SUBJECT_ID") 
REFERENCES "SUBJECTS"("ID") 
ON DELETE SET NULL;

CREATE INDEX "IDX_USERS_SUBJECT_ID" 
ON "USERS"("SUBJECT_ID") 
WHERE "SUBJECT_ID" IS NOT NULL;
```

### 2. Auth Service Updates

#### Updated `auth-service/main.py`

**New Table Definitions:**
- **Added `subjects` table definition** (copied from administration-service)
- **Updated `users` table definition** to include `SUBJECT_ID` column
- **Added `VALIDATED` column** to subjects table definition

**New Pydantic Models:**
- **Added `UserOut` model** with PESEL masking functionality
- **Updated `UserRegister` model** with optional `subject_id` field

**Refactored Registration Logic:**
```python
@app.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user with automatic subject creation"""
    try:
        # Check for existing user
        # Generate shared UUID for both user and subject
        shared_uknf_id = str(uuid.uuid4())
        
        # Step 1: Create empty subject
        subject_dict = {
            "UKNF_ID": shared_uknf_id,
            "DATE_CREATE": now,
            "DATE_ACTRUALIZATION": now,
            "VALIDATED": False,
            "STATUS_S": "inactive"
        }
        stmt = insert(subjects).values(**subject_dict).returning(subjects.c.ID)
        result = db.execute(stmt)
        subject_id = result.fetchone().ID
        
        # Step 2: Create user with subject reference
        user_dict = {
            "EMAIL": user_data.email,
            "PASSWORD_HASH": hashed_password,
            "UKNF_ID": shared_uknf_id,
            "SUBJECT_ID": subject_id,
            # ... other fields
        }
        stmt = insert(users).values(**user_dict).returning(users.c.ID)
        result = db.execute(stmt)
        user_id = result.fetchone().ID
        
        db.commit()
        
        return {
            "message": "User registered successfully",
            "user_id": user_id,
            "subject_id": subject_id,
            "email": user_data.email,
            "uknf_id": shared_uknf_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(...)
```

## Key Features

### 1. Atomic Transaction
- **Single database transaction** ensures both user and subject are created together
- **Rollback on failure** prevents partial data creation
- **ACID compliance** maintains data integrity

### 2. Shared Unique Identifier
- **UUID v4 generation** creates a unique identifier for each user-subject pair
- **Same `UKNF_ID`** used in both `USERS` and `SUBJECTS` tables
- **Durable relationship** that survives database operations

### 3. Minimal Subject Data
- **Empty subject creation** with only essential fields populated:
  - `UKNF_ID`: Shared UUID
  - `DATE_CREATE`: Current timestamp
  - `DATE_ACTRUALIZATION`: Current timestamp
  - `VALIDATED`: `false`
  - `STATUS_S`: `'inactive'`

### 4. Enhanced Response
- **Updated response format** includes:
  - `user_id`: ID of created user
  - `subject_id`: ID of created subject
  - `uknf_id`: Shared UUID
  - `email`: User email
  - `message`: Success message

## Database Relationships

### Before Refactor
```
USERS (no SUBJECT_ID)
SUBJECTS (independent)
```

### After Refactor
```
USERS ──SUBJECT_ID──> SUBJECTS
  │                    │
  └── UKNF_ID ─────────┘
```

## API Changes

### Registration Endpoint: `POST /register`

**Request Format (unchanged):**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "user_name": "John",
  "user_lastname": "Doe",
  "phone": "+48 123 456 789",
  "pesel": "92050812345",
  "uknf_id": "custom_id"  // Optional, will be ignored
}
```

**Response Format (enhanced):**
```json
{
  "message": "User registered successfully",
  "user_id": 123,
  "subject_id": 456,
  "email": "user@example.com",
  "uknf_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

## Testing

### Test Script: `test_user_subject_registration.py`
- **Comprehensive testing** of the new registration flow
- **Verification** of user-subject relationship
- **Duplicate email testing**
- **Custom UKNF_ID handling**
- **Database consistency checks**

### Test Coverage
- ✅ User registration with automatic subject creation
- ✅ Shared UKNF_ID between user and subject
- ✅ SUBJECT_ID foreign key relationship
- ✅ Atomic transaction behavior
- ✅ PESEL masking still works
- ✅ Duplicate email prevention
- ✅ Error handling and rollback

## Migration Instructions

### 1. Apply Database Migration
```bash
# Apply the new migration
psql -U myuser -d mydatabase -f migrations/010_add_subject_id_to_users.sql
```

### 2. Restart Services
```bash
# Restart with updated code
docker-compose down
docker-compose up -d
```

### 3. Verify Installation
```bash
# Run the test script
python test_user_subject_registration.py
```

## Backward Compatibility

### Existing Users
- **Existing users** without `SUBJECT_ID` will have `NULL` values
- **No data loss** or breaking changes
- **Gradual migration** possible for existing users

### API Compatibility
- **Request format unchanged** - existing clients continue to work
- **Response format enhanced** - new fields added, existing fields preserved
- **Optional fields** maintain backward compatibility

## Security Considerations

### Data Integrity
- **Foreign key constraints** ensure referential integrity
- **Atomic transactions** prevent partial data creation
- **UUID generation** prevents predictable identifiers

### Privacy
- **PESEL masking** still works correctly
- **No additional sensitive data** exposed
- **Same authentication flow** maintained

## Performance Impact

### Database Operations
- **Additional INSERT** for subject creation
- **Single transaction** minimizes overhead
- **Indexed foreign key** for efficient lookups

### Memory Usage
- **Minimal increase** due to additional table definition
- **No significant impact** on service performance

## Future Enhancements

### Potential Improvements
- **Bulk user import** with subject creation
- **Subject data enrichment** after registration
- **User-subject relationship management** endpoints
- **Audit logging** for user-subject creation

### Monitoring
- **Transaction success rates** monitoring
- **User-subject relationship** health checks
- **Performance metrics** for registration endpoint

## Conclusion

The refactored user registration process successfully implements automatic subject creation while maintaining backward compatibility and data integrity. The atomic transaction ensures reliable user-subject relationship creation, and the shared UUID provides a durable link between the entities.

**Key Benefits:**
- ✅ **Automatic subject creation** for every new user
- ✅ **Atomic transaction** ensures data consistency
- ✅ **Shared UUID** provides durable relationship
- ✅ **Backward compatibility** maintained
- ✅ **Enhanced API response** with additional information
- ✅ **Comprehensive testing** included
- ✅ **Production-ready** implementation
