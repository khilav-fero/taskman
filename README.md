# Task Management Application

This full-stack application provides a platform for teams to manage tasks, track changes, and receive relevant notifications. It features a Django REST Framework API backend and a Vue.js (JavaScript) frontend.

## Current Features

*   **Authentication:** Secure registration and token-based login.
*   **Role System:** Users assigned roles (Admin, Manager, Team Member) controlling permissions.
*   **Task Management:**
    *   API for CRUD (Create, Read, Update, Delete) operations on tasks.
    *   API for assigning tasks and managing collaborators (restricted).
    *   Frontend displays tasks in a sortable Vuetify data table (`v-data-table`).
    *   Frontend allows task creation and editing via a modal form for authorized roles.
    *   Assignee selection implemented in the task form.
*   **Task History:**
    *   Automatic logging of task modifications (status, assignee, collaborators, etc.) via Django Signals.
    *   Read-only API endpoint to retrieve history for a specific task (permission-restricted).
*   **Notifications:**
    *   Automatic generation of notifications for task assignments and collaborator changes via Django Signals.
    *   API endpoints for users to fetch their own notifications and mark them as read.
*   **User Management List:**
    *   Frontend page (`/users`) displaying all users and their roles (accessible by Admin/Manager only).
    *   Placeholder actions for role editing and user deletion (Admin only).
*   **Frontend:**
    *   Role-based display of UI elements (buttons, links).
    *   Client-side routing handled by Vue Router.
    *   Global state managed by Pinia (auth status, user info, task list, etc.).
    *   UI built with the Vuetify 3 component library.
    *   Client-side form validation using Vuetify rules.
    *   API communication handled by Axios with automatic token injection.

## Technology Stack

**Backend:**

*   Python 3.x
*   Django
*   Django REST Framework (DRF)
*   `django-cors-headers`
*   `django-filter`
*   SQLite (Development)

**Frontend:**

*   Vue 3 (Composition API, JavaScript)
*   Vite
*   Vuetify 3
*   Pinia
*   Vue Router 4
*   Axios
*   `@vuepic/vue-datepicker`
*   SCSS


## Prerequisites

*   Python 3.9+ & Pip
*   Node.js (LTS) & npm

## Setup

1.  **Clone:** `git clone <repository-url>` & `cd <repository-name>`
2.  **Backend:**
    *   `cd backend`
    *   `python -m venv venv`
    *   Activate environment (`source venv/bin/activate` or `venv\Scripts\activate`)
    *   `pip install -r requirements.txt`
    *   `python manage.py migrate`
    *   `python manage.py createsuperuser`
    *   Run server, log into `/admin/`, edit superuser profile, set Role to `ADMIN`, Save.
3.  **Frontend:**
    *   `cd ../frontend` (or `cd frontend` from root)
    *   `npm install`

## Running

1.  **Terminal 1 (Backend):**
    *   `cd backend`
    *   Activate venv
    *   `python manage.py runserver` (Runs on `http://localhost:8000`)
2.  **Terminal 2 (Frontend):**
    *   `cd frontend`
    *   `npm run dev` (Runs on `http://localhost:5173` or similar)
3.  **Access:** Open the frontend URL (e.g., `http://localhost:5173`) in your browser. Ensure backend `CORS_ALLOWED_ORIGINS` in `settings.py` includes the frontend origin.

