# Subject Management Feature - Implementation Documentation

## Overview

This feature allows authorized users to edit subject details and view the complete history of changes. The implementation includes both backend API endpoints and a modern frontend interface with full audit trail support.

---

## Backend Implementation (administration-service)

### 1. Database Schema Updates

The SUBJECTS table already includes:
- All subject fields (NAME_STRUCTURE, NIP, KRS, ADDRESS fields, etc.)
- `VALIDATED` field for validation status
- `RESOURCE_ID` field for linking to permission resources

The SUBJECTS_HISTORY table (from migration 012) provides:
- Complete audit trail for all UPDATE and DELETE operations
- Automatic tracking of user_id who made the change
- Timestamp of each modification
- Full snapshot of data before the change

### 2. New API Endpoints

#### PUT /subjects/{subject_id}
**Purpose**: Update subject information with authorization and automatic audit logging.

**Authorization**: User must be an administrator of the specific subject.

**Request**:
```http
PUT /admin/subjects/1
Authorization: Bearer {session_id}
Content-Type: application/json

{
  "NAME_STRUCTURE": "Updated Bank Name",
  "PHONE": "+48 22 123 4567",
  "EMAIL": "contact@example.com"
}
```

**Response**:
```json
{
  "ID": 1,
  "NAME_STRUCTURE": "Updated Bank Name",
  "PHONE": "+48 22 123 4567",
  "EMAIL": "contact@example.com",
  "DATE_ACTRUALIZATION": "2025-10-05T10:30:00Z",
  ...
}
```

**Features**:
- ✅ Permission check using `subject:admin:{subject_id}` resource
- ✅ Partial updates (only send changed fields)
- ✅ Automatic DATE_ACTRUALIZATION update
- ✅ Audit trail via database trigger (sets `app.current_user_id`)
- ✅ Atomic transaction with rollback on error

#### GET /subjects/{subject_id}/history
**Purpose**: Retrieve complete change history for a subject.

**Authorization**: User must have `api:subjects:read` permission.

**Request**:
```http
GET /admin/subjects/1/history
Authorization: Bearer {session_id}
```

**Response**:
```json
[
  {
    "HISTORY_ID": 15,
    "OPERATION_TYPE": "UPDATE",
    "MODIFIED_AT": "2025-10-05T10:30:00Z",
    "MODIFIED_BY": 2,
    "ID": 1,
    "NAME_STRUCTURE": "Previous Bank Name",
    "PHONE": "+48 22 999 8888",
    ...
  },
  {
    "HISTORY_ID": 12,
    "OPERATION_TYPE": "UPDATE",
    "MODIFIED_AT": "2025-10-03T14:15:00Z",
    "MODIFIED_BY": 2,
    ...
  }
]
```

**Features**:
- ✅ Returns all history records for the subject
- ✅ Ordered by most recent first
- ✅ Includes user ID who made each change
- ✅ Full snapshot of data before each modification

### 3. Authorization Helper Functions

#### `check_subject_edit_permission(subject_id, authorization)`
**Purpose**: Verify user has permission to edit a specific subject.

**Logic**:
1. Extract session_id from Authorization header
2. Call auth-service to check `subject:admin:{subject_id}` permission
3. If authorized, return user_id
4. If not authorized, raise 403 Forbidden

**Usage**:
```python
@app.put("/subjects/{subject_id}", response_model=SubjectOut)
def update_subject(
    subject_id: int,
    subject_data: SubjectUpdate,
    db: Session = Depends(get_db),
    authorization: str = Header(None)
):
    user_id = check_subject_edit_permission(subject_id, authorization)
    # ... proceed with update
```

### 4. Pydantic Models

#### SubjectUpdate
```python
class SubjectUpdate(BaseModel):
    TYPE_STRUCTURE: Optional[str] = None
    NAME_STRUCTURE: Optional[str] = None
    NIP: Optional[str] = None
    KRS: Optional[str] = None
    STREET: Optional[str] = None
    TOWN: Optional[str] = None
    POST_CODE: Optional[str] = None
    PHONE: Optional[str] = None
    EMAIL: Optional[str] = None
    STATUS_S: Optional[str] = None
    # ... other optional fields
```

#### SubjectHistoryOut
```python
class SubjectHistoryOut(BaseModel):
    HISTORY_ID: int
    OPERATION_TYPE: str
    MODIFIED_AT: datetime
    MODIFIED_BY: Optional[int] = None
    ID: int
    # ... all subject fields
```

---

## Frontend Implementation

### 1. New API Client Methods

**File**: `frontend/src/services/api.ts`

```typescript
class AdministrationAPI extends ApiClient {
  constructor() {
    super('/admin');
  }

  async getSubject(id: number): Promise<Subject> {
    return this.get(`/subjects/${id}`);
  }

  async updateSubject(id: number, data: Partial<Subject>): Promise<Subject> {
    return this.put(`/subjects/${id}`, data);
  }

  async getSubjectHistory(id: number): Promise<HistoryRecord[]> {
    return this.get(`/subjects/${id}/history`);
  }
}

export const adminAPI = new AdministrationAPI();
```

### 2. Subject Management Page

**File**: `frontend/src/pages/SubjectManagementPage.tsx`

**Route**: `/subjects/:subjectId/manage`

**Features**:
- ✅ Form for editing subject details
- ✅ Real-time validation
- ✅ Change detection (only sends modified fields)
- ✅ Loading states and error handling
- ✅ Success notifications
- ✅ History sidebar with timeline view
- ✅ Responsive design (works on mobile/tablet/desktop)

**UI Components**:

#### Main Edit Form (Left Panel)
- Pre-populated form with current subject data
- Fields: Name, Type, NIP, KRS, Address, Contact info, Status
- "Save Changes" button (only visible to authorized users)
- Loading spinner during save operations
- Success/Error alerts

#### History Sidebar (Right Panel)
- Timeline view of all changes
- Shows operation type (UPDATE/DELETE)
- Displays date and time of each change
- Shows user ID who made the change
- Color-coded timeline (blue border for updates)
- Auto-refreshes after successful updates

### 3. Updated Type Definitions

**File**: `frontend/src/types/index.ts`

Extended the Subject interface to include all backend fields:

```typescript
export interface Subject {
  ID: number;
  TYPE_STRUCTURE?: string | null;
  CODE_UKNF?: string | null;
  NAME_STRUCTURE?: string | null;
  LEI?: string | null;
  NIP?: string | null;
  KRS?: string | null;
  STREET?: string | null;
  NR_STRET?: string | null;
  NR_HOUSE?: string | null;
  POST_CODE?: string | null;
  TOWN?: string | null;
  PHONE?: string | null;
  EMAIL?: string | null;
  UKNF_ID?: string | null;
  STATUS_S?: string | null;
  KATEGORY_S?: string | null;
  SELEKTOR_S?: string | null;
  SUBSELEKTOR_S?: string | null;
  TRANS_S?: boolean | null;
  DATE_CREATE?: string | null;
  DATE_ACTRUALIZATION?: string | null;
  VALIDATED?: boolean | null;
  RESOURCE_ID?: string | null;
}
```

### 4. Routing

**File**: `frontend/src/App.tsx`

Added new protected route:

```typescript
<Route path="/subjects/:subjectId/manage" element={<SubjectManagementPage />} />
```

---

## Security & Authorization

### 1. Permission Model

**Subject Administrator**:
- Resource ID: `subject:admin:{subject_id}`
- Can edit their own subject only
- Example: User with subject_id=2 can only edit subject 2

**UKNF Administrator** (future enhancement):
- Could have global `api:subjects:edit` permission
- Can edit any subject

### 2. Authorization Flow

```
┌─────────────┐
│   Frontend  │
│  (Browser)  │
└──────┬──────┘
       │ 1. PUT /subjects/1
       │    Authorization: Bearer {session_id}
       ▼
┌──────────────────┐
│ Administration   │
│   Service        │
└──────┬───────────┘
       │ 2. Check permission
       │    Resource: subject:admin:1
       ▼
┌──────────────────┐
│  Auth Service    │
│  (Authorization) │
└──────┬───────────┘
       │ 3. Query permissions
       ▼
┌──────────────────┐
│   PostgreSQL     │
│  (RESOURCES,     │
│   GROUPS, etc.)  │
└──────┬───────────┘
       │ 4. Permission granted
       ▼
┌──────────────────┐
│ Administration   │
│   Service        │
│ - Set user_id    │
│ - Update subject │
│ - Trigger logs   │
└──────┬───────────┘
       │ 5. Response
       ▼
┌──────────────────┐
│   Frontend       │
│ - Show success   │
│ - Reload history │
└──────────────────┘
```

### 3. Audit Trail

Every UPDATE operation:
1. **Before Update**: Trigger captures OLD row values
2. **During Update**: Session variable `app.current_user_id` is set
3. **Trigger Executes**: Inserts OLD values + metadata into SUBJECTS_HISTORY
4. **Result**: Complete audit trail with who, what, when

---

## Testing

### Test Scenario 1: UKNF Admin Edits Own Subject

```bash
# 1. Login as UKNF admin
SESSION_ID=$(curl -s -X POST http://localhost:3000/auth/authn \
  -H "Content-Type: application/json" \
  -d '{"email": "admin_uknf@example.com", "password": "password123"}' | jq -r '.session_id')

# 2. Get subject details
curl -H "Authorization: Bearer $SESSION_ID" \
  http://localhost:3000/admin/subjects/1 | jq .

# 3. Update subject
curl -X PUT -H "Authorization: Bearer $SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{"PHONE": "+48 22 NEW-NUMBER", "EMAIL": "newemail@uknf.gov.pl"}' \
  http://localhost:3000/admin/subjects/1 | jq .

# 4. View history
curl -H "Authorization: Bearer $SESSION_ID" \
  http://localhost:3000/admin/subjects/1/history | jq .
```

**Expected Result**:
- Update succeeds with 200 OK
- History shows new record with MODIFIED_BY=2 (UKNF admin user_id)

### Test Scenario 2: Bank Pekao Admin Tries to Edit UKNF Subject

```bash
# 1. Login as Bank Pekao admin
SESSION_ID=$(curl -s -X POST http://localhost:3000/auth/authn \
  -H "Content-Type: application/json" \
  -d '{"email": "admin_pekao@example.com", "password": "password456"}' | jq -r '.session_id')

# 2. Try to update UKNF subject (should fail)
curl -X PUT -H "Authorization: Bearer $SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{"PHONE": "Unauthorized change"}' \
  http://localhost:3000/admin/subjects/1 | jq .
```

**Expected Result**:
- 403 Forbidden
- Error: "Access denied: you must be an administrator of this subject to edit it"

### Test Scenario 3: Frontend UI Testing

1. **Navigate**: http://localhost:3000/subjects/1/manage
2. **Login**: Use `admin_uknf@example.com` / `password123`
3. **Edit**: Change phone number and email
4. **Save**: Click "Save Changes" button
5. **Verify**:
   - Success message appears
   - History sidebar shows new entry
   - Form updates with new values

---

## File Changes Summary

### Backend Files Modified:
- ✅ `administration-service/main.py` - Added PUT and GET endpoints, authorization helpers

### Frontend Files Modified:
- ✅ `frontend/src/services/api.ts` - Added AdminAPI class with new methods
- ✅ `frontend/src/types/index.ts` - Extended Subject interface
- ✅ `frontend/src/App.tsx` - Added new route

### Frontend Files Created:
- ✅ `frontend/src/pages/SubjectManagementPage.tsx` - New component

---

## Usage Examples

### For Administrators

**Access Subject Management**:
1. Login to the application
2. Navigate to: `/subjects/{id}/manage` (e.g., `/subjects/1/manage`)
3. Edit the subject fields
4. Click "Save Changes"
5. View the change history in the right sidebar

### For Developers

**Add Edit Button to Subject List**:
```tsx
<Link
  to={`/subjects/${subject.ID}/manage`}
  className="text-blue-600 hover:text-blue-800"
>
  <Edit size={18} />
  Edit Subject
</Link>
```

**Check if User Can Edit a Subject**:
```typescript
// Backend already handles this via check_subject_edit_permission
// Frontend displays edit form to all users, backend enforces permission
```

---

## Future Enhancements

### Phase 2:
- [ ] Add diff view showing what changed between versions
- [ ] Add rollback functionality (restore from history)
- [ ] Add bulk edit for multiple subjects
- [ ] Add export history to CSV/PDF

### Phase 3:
- [ ] Add field-level permissions (some users can only edit phone/email)
- [ ] Add approval workflow (changes require approval)
- [ ] Add comments/notes to history records
- [ ] Add email notifications on subject changes

---

## Troubleshooting

### Error: "Access denied: insufficient permissions"
**Cause**: User is not an administrator of the subject.
**Solution**: Ensure user is in the correct admin group for the subject.

### Error: "Subject not found"
**Cause**: Invalid subject_id in URL.
**Solution**: Verify the subject exists in the database.

### Error: "Failed to load subject"
**Cause**: Network issue or service unavailable.
**Solution**: Check that administration-service is running.

### History Not Updating
**Cause**: Database trigger not installed or disabled.
**Solution**: Run migration `012_add_subjects_history_trigger.sql`.

---

## Performance Considerations

### Database
- ✅ Indexes on SUBJECTS_HISTORY (ID, MODIFIED_AT, MODIFIED_BY)
- ✅ History table grows over time (monitor size)
- ✅ Consider archiving old history records after 2+ years

### Frontend
- ✅ History loaded separately (doesn't block form loading)
- ✅ Only changed fields sent in PUT request
- ✅ Auto-refresh history after updates

---

## Conclusion

The Subject Management Feature is fully implemented and ready for production use. It provides:
- ✅ Secure, authorized editing of subject details
- ✅ Complete audit trail of all changes
- ✅ Modern, user-friendly interface
- ✅ Comprehensive error handling
- ✅ Real-time feedback and validation

All functionality has been tested and documented. The feature integrates seamlessly with the existing authentication and authorization system.

