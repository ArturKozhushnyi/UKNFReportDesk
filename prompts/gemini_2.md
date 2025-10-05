Read files with understading, analyze what it is
Files and prompt exceed Gemini’s context window. For better results upload smaller files. Learn more

This project, UKNF Report Desk, is a comprehensive, microservices-based platform designed for managing financial reports submitted to the Polish Financial Supervision Authority (Urząd Komisji Nadzoru Finansowego - UKNF). It facilitates report submission, validation, communication between entities and UKNF staff, and user management with a robust role-based access control (RBAC) system.

Architecture

The system employs a microservices architecture consisting of three backend services and a frontend application, all containerized with Docker.

The services are:

    Frontend (Port 3000): A React/TypeScript application that serves as the user interface.

    Administration Service (Port 8000): A FastAPI service for managing banking entities (Subjects) and users.

    Authentication Service (Port 8001): A FastAPI service handling user registration, login, and authorization, using Redis for session management.

    Communication Service (Port 8002): A FastAPI service for the chat and reporting system.

All backend services connect to a shared PostgreSQL database, and the entire system is orchestrated using docker-compose.yaml.

Key Features

    Multi-Tenant Security: Each new user is automatically made an administrator of their own isolated "subject" entity. This provides data isolation with automatic administrative rights from the moment of registration.

    Comprehensive Chat System: A full-featured messaging system with 32 endpoints, supporting multi-party conversations, threaded messages, file attachments, read receipts, emoji reactions, and assignment management.

    Automated Audit Trail: A database-level audit trail system automatically tracks all UPDATE and DELETE operations on the SUBJECTS table, capturing a complete history of changes for compliance and security.

    Reporting System: A sophisticated reporting module with a detailed database schema to manage report types, templates, validation, and deadlines.

    Security: The platform includes PESEL masking for privacy, password hashing using sha256_crypt, and a role-based access control (RBAC) system.

Frontend

The frontend is a modern React application built with TypeScript and Vite. It uses:

    TanStack Query for data fetching and caching.

    Zustand for state management.

    Tailwind CSS for styling.

    React Router for navigation.

    A centralized API client (api.ts) with Axios interceptors for handling authentication tokens and errors.

The main dashboard provides an overview of reports, messages, cases, and notifications, with role-based access control determining what each user can see and do.

Database

The PostgreSQL database schema is managed through a series of SQL migration files. Key tables include SUBJECTS, USERS, GROUPS, RESOURCES, CONVERSATIONS, MESSAGES, and REPORTS, all linked to provide the application's functionality. The project also includes extensive documentation and test scripts to verify the functionality of its various components.

Create a prompt that will create registration page on frontend

Based on the analysis of the provided files for the UKNF Report Desk application, here is a prompt to generate the frontend registration page:

Prompt:

"Create a new registration page for the UKNF Report Desk frontend application. The frontend is a React/TypeScript application built with Vite, using TanStack Query for data fetching, Zustand for state management, and Tailwind CSS for styling.

Instructions:

    Create a new component file named RegistrationPage.tsx inside the src/pages directory.

    Design the registration form to be visually consistent with the existing LoginPage.tsx. The form should include the following input fields:

        Username

        Password

        Email

        First Name

        Last Name

        PESEL

    Implement form submission logic:

        Use the api.ts client to send a POST request to the /register endpoint of the authentication service.

        The payload should be a JSON object containing the values from the form fields.

    Handle API responses:

        On a successful registration, display a success message and redirect the user to the /login page.

        If the registration fails, display an appropriate error message to the user.

    Update the application's routing:

        In the src/App.tsx file, add a new route for /register that renders the newly created RegistrationPage component.

Reference Files:

    frontend/src/pages/LoginPage.tsx

    frontend/src/services/api.ts

    frontend/src/App.tsx

    auth-service/main.py (for the /register endpoint details)

    USER_SUBJECT_REGISTRATION_REFACTOR.md (for understanding the registration process)"

create prompt that will add mutliple features

I need to somehow get user_id by session id, this will be in auth-service

and I need to show on frontend real user name and surname and subject name

Of course! Here is a prompt that will add multiple features to your UKNF Report Desk application.

Prompt:

"I need to add several new features to the UKNF Report Desk application. This will involve changes to both the auth-service backend and the frontend.

1. Backend Changes (auth-service):

    Create a new endpoint to get user_id by session_id:

        In auth-service/main.py, create a new GET endpoint: /get-user-id-by-session/{session_id}.

        This endpoint should take a session_id as a path parameter.

        It needs to connect to the Redis session store, retrieve the user_id associated with the provided session_id, and return it in a JSON response.

    Enhance the /me endpoint to return user and subject details:

        Modify the existing /me endpoint in auth-service/main.py.

        In addition to the current information, the endpoint should now also return the logged-in user's first_name, last_name, and the name of the subject they belong to.

        To do this, you will need to:

            Get the user_id from the session.

            Query the PostgreSQL database to get the user's details from the users table.

            Use the subject_id from the user's record to query the subjects table and get the subject_name.

            Include firstName, lastName, and subjectName in the JSON response.

2. Frontend Changes:

    Update the Zustand store to hold user details:

        In frontend/src/stores/authStore.ts, add firstName, lastName, and subjectName to the AuthState interface and the initial state.

    Fetch and store user details on login:

        In frontend/src/stores/authStore.ts, modify the login function.

        After a successful login, it should make a call to the enhanced /me endpoint.

        The firstName, lastName, and subjectName from the response should be stored in the Zustand store.

    Display user's full name and subject name in the UI:

        In frontend/src/layouts/MainLayout.tsx, access the firstName, lastName, and subjectName from the useAuthStore.

        In the header or user profile section of the layout, display the user's full name (e.g., "John Doe") and their subject name.

Reference Files:

    auth-service/main.py

    frontend/src/stores/authStore.ts

    frontend/src/layouts/MainLayout.tsx

    frontend/src/services/api.ts

    migrations/001_initial_schema.sql (for database schema reference)

    migrations/010_add_subject_id_to_users.sql"

I need to change the subjects endpoint in administration-service, create prompt that prepares everything that it need to have for this, take into the account subject change history also

create prompt that will implement all of that, subject can be changed by only UKNF admins & subjects admins

Of course! Here is a comprehensive prompt that outlines all the necessary changes to modify the subjects endpoint in the administration-service, including the implementation of authorization and the subject change history feature.

Prompt:

"I need to implement a feature that allows authorized users to edit subject details and view the history of those changes. This will involve modifications to the administration-service and the frontend.

High-Level Requirements:

    Backend (administration-service):

        Create a new, protected endpoint to update subject information.

        Create a new endpoint to retrieve the audit history for a specific subject.

        The update functionality must be restricted to users with either "UKNF Admin" or "Subject Admin" roles.

    Frontend:

        Create a new page or modal where authorized users can edit subject details.

        Display the subject's change history on that page.

        The editing functionality in the UI should only be visible to authorized users.

Part 1: Backend Changes (administration-service)

Task 1.1: Create the Subject Update Endpoint

    In administration-service/main.py, create a new PUT endpoint: /subjects/{subject_id}.

    Request Body: The endpoint should accept a Pydantic schema with the fields that can be modified (e.g., name, address, krs, etc.).

    Logic:

        Implement the authorization check (see Task 1.2).

        If authorized, update the corresponding record in the subjects table in the PostgreSQL database.

        The existing database trigger on the subjects table will automatically record this change in the subjects_history table.

    Response: On success, return the updated subject data.

Task 1.2: Implement Authorization

    Create a new dependency or function to handle the authorization logic for the PUT /subjects/{subject_id} endpoint.

    This function must verify that the user making the request has one of the following roles:

        UKNF Admin: A user who is part of the global "UKNF Admin" group.

        Subject Admin: A user who is a member of the "Admin" group specifically for the subject_id being modified.

    If the user does not have the required permissions, the endpoint must return a 403 Forbidden HTTP status code.

Task 1.3: Create the Subject History Endpoint

    In administration-service/main.py, create a new GET endpoint: /subjects/{subject_id}/history.

    Logic:

        This endpoint should query the subjects_history table.

        It should retrieve all historical records where the id matches the requested subject_id.

        The results should be ordered by the changed_at timestamp in descending order to show the most recent changes first.

    Response: Return a JSON array of the historical records for the subject.

Part 2: Frontend Changes

Task 2.1: Create a Subject Management Page

    Create a new page component, for example, SubjectManagementPage.tsx, in the frontend/src/pages directory.

    This page should be accessible via a new route like /subjects/:subjectId/manage.

    Add this new route to the router in frontend/src/App.tsx.

Task 2.2: Implement the Edit Subject Form

    On the SubjectManagementPage.tsx, create a form that is pre-populated with the details of the subject.

    Conditional Rendering:

        Use the user's role information from the authStore to determine if they are a "UKNF Admin" or a "Subject Admin" for the current subject.

        The form fields and the "Save Changes" button should only be enabled if the user has the necessary permissions. Otherwise, they should be disabled or hidden.

    Form Submission:

        When the form is submitted, make a PUT request to the /subjects/{subject_id} endpoint using the api.ts service.

        Handle both success and error responses from the API, providing feedback to the user (e.g., a success notification or an error message).

Task 2.3: Display the Subject Change History

    On the SubjectManagementPage.tsx, create a new component to display the change history.

    When the page loads, make a GET request to the /subjects/{subject_id}/history endpoint.

    Display the retrieved history in a table or a list, showing the changes made, who made them, and when they occurred.

Reference Files:

    administration-service/main.py

    migrations/001_initial_schema.sql (for subjects table structure)

    migrations/012_add_subjects_history_trigger.sql (for the audit trigger logic)

    SUBJECTS_AUDIT_TRAIL.md (for an overview of the audit trail)

    frontend/src/services/api.ts

    frontend/src/stores/authStore.ts

    frontend/src/App.tsx"