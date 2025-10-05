# SUBJECTS Audit Trail - Quick Start Guide

## 🚀 Installation (5 minutes)

### Step 1: Apply the Migration

**Option A: Using Docker Compose (Automatic)**
```bash
cd /Users/kan/Projects/hackyeah/UKNFReportDesk
docker-compose down
docker-compose up -d
```
✅ Migration runs automatically on container startup

**Option B: Manual Application**
```bash
psql -U myuser -d mydatabase -f migrations/012_add_subjects_history_trigger.sql
```

### Step 2: Verify Installation

```bash
# Run the test suite
python test_subjects_audit_trail.py
```

Expected output:
```
✅ SUBJECTS_HISTORY table exists
✅ subjects_history_trigger exists  
✅ log_subjects_changes() function exists
✅ All Tests Completed Successfully!
```

---

## 💻 Using in Your Code

### Python/FastAPI Example

```python
from sqlalchemy import text, update

def update_subject_with_audit(db: Session, subject_id: int, user_id: int, updates: dict):
    """Update a subject with automatic audit trail"""
    
    # Set user context for audit
    db.execute(text("SET LOCAL app.current_user_id = :user_id"), {"user_id": user_id})
    
    # Perform update
    stmt = update(subjects).where(subjects.c.ID == subject_id).values(**updates)
    db.execute(stmt)
    db.commit()

# Usage
update_subject_with_audit(
    db=db,
    subject_id=123,
    user_id=5,
    updates={"NAME_STRUCTURE": "New Name", "STATUS_S": "active"}
)
```

### Direct SQL Example

```sql
BEGIN;
    -- Set user context
    SET LOCAL app.current_user_id = 5;
    
    -- Make changes (automatically logged)
    UPDATE "SUBJECTS" 
    SET "NAME_STRUCTURE" = 'Updated Name',
        "STATUS_S" = 'active'
    WHERE "ID" = 123;
COMMIT;
```

---

## 🔍 Querying History

### View All Changes for a Subject

```sql
SELECT 
    "MODIFIED_AT",
    "OPERATION_TYPE",
    "NAME_STRUCTURE",
    "STATUS_S"
FROM "SUBJECTS_HISTORY"
WHERE "ID" = 123
ORDER BY "MODIFIED_AT" DESC;
```

### Find Who Made Changes

```sql
SELECT 
    sh."MODIFIED_AT",
    sh."OPERATION_TYPE",
    sh."ID" as subject_id,
    u."EMAIL" as modified_by
FROM "SUBJECTS_HISTORY" sh
LEFT JOIN "USERS" u ON sh."MODIFIED_BY" = u."ID"
WHERE sh."ID" = 123
ORDER BY sh."MODIFIED_AT" DESC;
```

### Audit Report - Last 30 Days

```sql
SELECT 
    DATE(sh."MODIFIED_AT") as date,
    COUNT(*) as changes,
    COUNT(DISTINCT sh."ID") as subjects_affected,
    COUNT(DISTINCT sh."MODIFIED_BY") as users_involved
FROM "SUBJECTS_HISTORY" sh
WHERE sh."MODIFIED_AT" >= NOW() - INTERVAL '30 days'
GROUP BY DATE(sh."MODIFIED_AT")
ORDER BY date DESC;
```

---

## 🛠️ Integration with Administration Service

### Update the PUT/PATCH Endpoint

Add user context to your update endpoint:

```python
# administration-service/main.py

@app.put("/subjects/{id}")
def update_subject(
    id: int,
    subject_data: SubjectUpdate,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    # Extract user ID from session (your existing logic)
    user_id = get_user_from_session(authorization)
    
    # SET user context for audit trail
    db.execute(text("SET LOCAL app.current_user_id = :user_id"), {"user_id": user_id})
    
    # Perform update
    stmt = update(subjects).where(subjects.c.ID == id).values(**subject_data.dict())
    result = db.execute(stmt)
    db.commit()
    
    return {"message": "Subject updated"}
```

### Update the DELETE Endpoint

```python
@app.delete("/subjects/{id}")
def delete_subject(
    id: int,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    # Extract user ID
    user_id = get_user_from_session(authorization)
    
    # SET user context
    db.execute(text("SET LOCAL app.current_user_id = :user_id"), {"user_id": user_id})
    
    # Perform delete (history automatically saved)
    stmt = delete(subjects).where(subjects.c.ID == id)
    db.execute(stmt)
    db.commit()
    
    return {"message": "Subject deleted"}
```

---

## 📊 Dashboard Queries

### Recent Activity Widget

```sql
SELECT 
    COUNT(*) as changes_today,
    COUNT(DISTINCT "ID") as subjects_modified,
    COUNT(DISTINCT "MODIFIED_BY") as active_users
FROM "SUBJECTS_HISTORY"
WHERE DATE("MODIFIED_AT") = CURRENT_DATE;
```

### Most Active Users

```sql
SELECT 
    u."EMAIL",
    u."USER_NAME" || ' ' || u."USER_LASTNAME" as name,
    COUNT(*) as modifications,
    MAX(sh."MODIFIED_AT") as last_activity
FROM "SUBJECTS_HISTORY" sh
JOIN "USERS" u ON sh."MODIFIED_BY" = u."ID"
WHERE sh."MODIFIED_AT" >= NOW() - INTERVAL '7 days'
GROUP BY u."ID", u."EMAIL", u."USER_NAME", u."USER_LASTNAME"
ORDER BY modifications DESC
LIMIT 10;
```

### Deletion Log

```sql
SELECT 
    sh."MODIFIED_AT" as deleted_at,
    sh."NAME_STRUCTURE" as subject_name,
    sh."UKNF_ID",
    u."EMAIL" as deleted_by
FROM "SUBJECTS_HISTORY" sh
LEFT JOIN "USERS" u ON sh."MODIFIED_BY" = u."ID"
WHERE sh."OPERATION_TYPE" = 'DELETE'
  AND sh."MODIFIED_AT" >= NOW() - INTERVAL '30 days'
ORDER BY sh."MODIFIED_AT" DESC;
```

---

## 🔧 Maintenance

### Monthly Cleanup (Optional)

```sql
-- Archive records older than 7 years
DELETE FROM "SUBJECTS_HISTORY"
WHERE "MODIFIED_AT" < NOW() - INTERVAL '7 years';

-- Vacuum to reclaim space
VACUUM ANALYZE "SUBJECTS_HISTORY";
```

### Monitor Table Size

```sql
SELECT 
    pg_size_pretty(pg_total_relation_size('SUBJECTS_HISTORY')) as size,
    COUNT(*) as records
FROM "SUBJECTS_HISTORY";
```

---

## 🚨 Troubleshooting

### Problem: MODIFIED_BY is always NULL

**Solution:** Make sure you're setting the session variable:
```python
db.execute(text("SET LOCAL app.current_user_id = :user_id"), {"user_id": user_id})
```

### Problem: No history records created

**Check trigger is active:**
```sql
SELECT * FROM pg_trigger WHERE tgname = 'subjects_history_trigger';
```

### Problem: Permission denied

**Grant permissions:**
```sql
GRANT SELECT ON "SUBJECTS_HISTORY" TO your_app_user;
```

---

## 📝 What Gets Logged?

✅ **Logged:**
- Every UPDATE to SUBJECTS
- Every DELETE from SUBJECTS  
- Timestamp of change
- User who made change (if set)
- Complete snapshot of data BEFORE change

❌ **Not Logged:**
- INSERT operations
- SELECT queries
- Changes to other tables

---

## 🎯 Next Steps

1. **Deploy to Production**
   ```bash
   # Run migration
   docker-compose up -d
   
   # Verify
   python test_subjects_audit_trail.py
   ```

2. **Update Your Code**
   - Add `SET LOCAL app.current_user_id` to update/delete operations
   - Test with your existing API

3. **Create Dashboards**
   - Use the provided queries
   - Set up monitoring alerts
   - Schedule regular audit reports

4. **Train Your Team**
   - Share this documentation
   - Demonstrate audit queries
   - Establish review procedures

---

## 📚 Full Documentation

- **Complete Guide**: [SUBJECTS_AUDIT_TRAIL.md](SUBJECTS_AUDIT_TRAIL.md)
- **Migration File**: [migrations/012_add_subjects_history_trigger.sql](migrations/012_add_subjects_history_trigger.sql)
- **Test Suite**: [test_subjects_audit_trail.py](test_subjects_audit_trail.py)

---

## ✅ Checklist

- [ ] Migration applied
- [ ] Tests pass
- [ ] Code updated to set user context
- [ ] Team trained on querying history
- [ ] Monitoring dashboards created
- [ ] Backup strategy updated
- [ ] Retention policy documented

---

**Ready to Go!** 🎉

Your audit trail system is production-ready and will automatically track all changes to SUBJECTS from now on.

