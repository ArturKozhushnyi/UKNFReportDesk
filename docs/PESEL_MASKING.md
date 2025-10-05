# PESEL Masking Documentation

## Overview

PESEL (Powszechny Elektroniczny System Ewidencji Ludności) is a Polish national identification number consisting of 11 digits. Due to privacy regulations (GDPR/RODO), PESEL numbers must be protected when displayed in API responses.

## Implementation

### Masking Format

PESEL numbers are masked to show only the **last 4 digits**, with all preceding digits replaced by asterisks:

```
Original: 92050812345
Masked:   *******2345
```

### How It Works

1. **Database Storage**: PESEL is stored in full in the database (plain text)
   - ⚠️ **Note**: Consider encrypting PESEL in the database for enhanced security

2. **API Response**: PESEL is automatically masked when returned via API
   - Applied in the `UserOut` Pydantic model
   - Uses the `from_db_row()` class method

3. **Masking Logic**: Located in `administration-service/main.py`

```python
@staticmethod
def mask_pesel(pesel: Optional[str]) -> Optional[str]:
    """Mask PESEL to show only last 4 digits (format: *******5123)"""
    if not pesel or len(pesel) < 4:
        return pesel
    return '*' * (len(pesel) - 4) + pesel[-4:]
```

## API Endpoints Affected

### GET /users/{id}

**Response Example:**

```json
{
  "ID": 1,
  "USER_NAME": "Jan",
  "USER_LASTNAME": "Kowalski",
  "EMAIL": "jan.kowalski@example.com",
  "PESEL": "*******2345",
  "PHONE": "+48 123 456 789",
  "IS_USER_ACTIVE": true,
  "UKNF_ID": "UKNF001",
  "DATE_CREATE": "2025-10-04T12:30:45.123456Z",
  "DATE_ACTRUALIZATION": "2025-10-04T12:30:45.123456Z"
}
```

## Security Considerations

### Current State

✅ **Implemented**: PESEL masking in API responses  
✅ **Tested**: Comprehensive test coverage  
❌ **Missing**: Database encryption for PESEL

### Recommendations

1. **Encrypt PESEL in Database**
   - Use PostgreSQL `pgcrypto` extension
   - Or application-level encryption (Fernet, AES)

2. **Audit Logging**
   - Log all access to PESEL data
   - Track who accessed unmasked PESEL (if full access is needed)

3. **Role-Based Access**
   - Consider different masking levels:
     - Regular users: `*******2345`
     - Administrators: `920508*2345`
     - Auditors: Full PESEL with audit log

## Testing

Run the PESEL masking tests:

```bash
python test_pesel_masking.py
```

### Test Cases

| Input | Output | Description |
|-------|--------|-------------|
| `92050812345` | `*******2345` | Standard 11-digit PESEL |
| `12345678901` | `*******8901` | Another valid PESEL |
| `123` | `123` | Too short - no masking |
| `""` | `""` | Empty string |
| `None` | `None` | None value |
| `1234` | `1234` | Exactly 4 digits |
| `12345` | `*2345` | 5 digits |

## GDPR/RODO Compliance

### Article 32 - Security of Processing

PESEL masking helps comply with:
- **Data Minimization**: Only display necessary information
- **Confidentiality**: Protect personal identification numbers
- **Integrity**: Maintain data accuracy while protecting privacy

### Future Improvements

For full GDPR/RODO compliance:

1. ✅ Mask PESEL in API responses
2. ❌ Encrypt PESEL in database at rest
3. ❌ Implement data access logging
4. ❌ Add consent management
5. ❌ Implement right to erasure (GDPR Article 17)
6. ❌ Add data portability (GDPR Article 20)

## Code Examples

### Using in Controllers

```python
# Automatic masking via model
@app.get("/users/{id}", response_model=UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    stmt = select(users).where(users.c.ID == id)
    result = db.execute(stmt)
    row = result.fetchone()
    
    if row is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # PESEL is automatically masked here
    return UserOut.from_db_row(row)
```

### Manual Masking

```python
from administration_service.main import UserOut

# If you need to mask manually
pesel = "92050812345"
masked = UserOut.mask_pesel(pesel)
print(masked)  # Output: *******2345
```

## Related Files

- `administration-service/main.py` - Implementation
- `test_pesel_masking.py` - Unit tests
- `migrations/001_initial_schema.sql` - PESEL column definition

## Change Log

| Date | Version | Changes |
|------|---------|---------|
| 2025-10-04 | 1.0 | Initial PESEL masking implementation |

---

**⚠️ Important**: PESEL masking in API responses is just the first step. For production use, implement database-level encryption and comprehensive audit logging.

