# Manage Subjects Feature Implementation

## Overview

The "Manage Subjects" feature allows users with appropriate permissions to view and manage subjects (banking entities) they have administrative access to. This feature provides a centralized interface for subject management operations.

## Implementation Details

### Backend Changes

#### New Endpoint: `/subjects/manageable`

**Location:** `administration-service/main.py`

**Method:** GET

**Authentication:** Required (Bearer token)

**Authorization Logic:**
1. **UKNF Administrators**: Can view and manage all subjects in the system
2. **Subject Administrators**: Can view and manage only subjects they are assigned to admin
3. **Regular Users**: Cannot access any subjects (returns empty array)

**Response:** Array of `SubjectOut` objects containing:
- Subject ID and name
- Contact information (email, phone, address)
- Validation status
- Entity identifiers (NIP, KRS, LEI)

### Frontend Changes

#### New Page: ManageSubjectsPage

**Location:** `frontend/src/pages/ManageSubjectsPage.tsx`

**Features:**
- Displays manageable subjects in a responsive table
- Shows subject details, contact info, and validation status
- Provides "Manage" buttons linking to detailed subject management
- Handles loading states and error conditions
- Shows appropriate message when no subjects are manageable

#### API Integration

**Location:** `frontend/src/services/api.ts`

**New Function:**
```typescript
async getManageableSubjects(): Promise<Subject[]>
```

#### Navigation Integration

**Location:** `frontend/src/layouts/MainLayout.tsx`

**Access Control:** Only visible to users with `internal_user` or `administrator` roles

**Location:** Added to "Administrative Module" submenu

#### Routing

**Location:** `frontend/src/App.tsx`

**New Route:** `/manage-subjects` → `ManageSubjectsPage`

## User Experience

### For UKNF Administrators
- Can see all subjects in the system
- Can manage any subject's details, users, and settings
- Full administrative control over the subject database

### For Subject Administrators
- Can see only subjects they have admin rights for
- Can manage their assigned subjects
- Limited scope based on their specific permissions

### For Regular Users
- Cannot access the Manage Subjects page
- Navigation link is hidden based on role permissions

## Security Considerations

1. **Authentication Required**: All requests require valid session tokens
2. **Authorization Enforced**: Backend validates user permissions before returning subjects
3. **Role-Based Access**: Frontend navigation respects user roles
4. **Subject Isolation**: Users can only manage subjects they have explicit permissions for

## Testing

A test script is provided at `test_manageable_subjects.py` that demonstrates:
- Health check verification
- Admin user authentication
- Manageable subjects endpoint testing
- Unauthenticated access rejection

## Usage Examples

### Backend API Call
```bash
curl -H "Authorization: Bearer <session_id>" \
     http://localhost:8000/subjects/manageable
```

### Frontend Navigation
1. Login as admin user
2. Navigate to "Administrative Module" → "Manage Subjects"
3. View list of manageable subjects
4. Click "Manage" to access detailed subject management

## Integration with Existing Features

This feature integrates seamlessly with:
- **Subject Management Page**: Direct navigation from manageable subjects list
- **Authentication System**: Uses existing session-based auth
- **Role-Based Access Control**: Respects existing RBAC implementation
- **Navigation System**: Follows established UI patterns

## Future Enhancements

Potential improvements could include:
- Bulk operations on multiple subjects
- Advanced filtering and search capabilities
- Subject creation from the manageable subjects page
- Export functionality for subject lists
- Real-time updates when subject permissions change
