# Tadrees — End-to-End Education Center Management System

A full-stack REST API backend for managing educational centers, covering students, teachers, scheduling, attendance, and finance in one unified platform.

---

## Overview

Tadrees is a Django REST Framework backend designed for private tutoring centers and educational institutes. It handles the complete operational lifecycle of a center — from registering students and teachers, building academic schedules, tracking session attendance, to processing payments. The system targets administrators and staff who need a centralized, role-protected API to run day-to-day center operations, backed by automated background tasks for session generation and cleanup.

---

## Features

- **Role-based authentication** — JWT login with distinct `ADMIN` and `STAFF` roles; admin-only routes enforced via custom permissions
- **Student & teacher management** — Full CRUD for students, teacher listing/creation, and teacher profile support with photo upload
- **Subject & room management** — Create subjects with pricing, manage physical rooms, and prevent scheduling conflicts via overlap detection
- **Recurring & special schedules** — Regular weekly schedules and one-off special sessions with individual pricing and notes
- **Automated session generation** — Celery Beat task runs nightly to create today's sessions from active schedules
- **Session attendance tracking** — Mark students as attended per session; view today's, upcoming, and historical attendance
- **Student enrollments** — Link students to subjects with payment status tracking
- **Finance & payments** — Record payments tied to enrollments, sessions, or products; support for generic product catalog
- **Center info & announcements** — Store branding/contact info; post announcements targeted at staff, students, teachers, or all
- **Automated maintenance tasks** — Scheduled cleanup of sessions older than 30 days and expired special schedules
- **Frontend UI** — Vanilla HTML/CSS/JS interface for admin dashboard, schedule management, students, teachers, subjects, and more
- **CORS support** — Configured for local frontend dev servers

---

## Tech Stack

| Layer | Technology | Version |
|---|---|---|
| Language | Python | 3.x |
| Web Framework | Django | 5.2 |
| REST API | Django REST Framework | 3.17 |
| Authentication | Simple JWT | 5.5 |
| Task Queue | Celery | 5.6 |
| Task Scheduler | Celery Beat + django-celery-beat | 2.9 |
| Message Broker | Redis | 8.0 |
| Database | PostgreSQL | — |
| ORM Driver | psycopg2-binary | 2.9 |
| Image Handling | Pillow | 12.2 |
| CORS | django-cors-headers | 4.9 |
| Environment Config | python-dotenv | 1.2 |
| Frontend | HTML / CSS / Vanilla JS | — |

---

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL (running locally or remote)
- Redis (running locally, default port `6379`)
- `pip` and `virtualenv` (or equivalent)

---

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/YousseffDawood/E2E-Education-system.git
cd E2E-Education-system

# 2. Create and activate a virtual environment
python -m venv env
# Windows
env\Scripts\activate
# macOS / Linux
source env/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Apply migrations
python manage.py migrate

# 5. (Optional) Seed the database with sample data
python seed.py
```

---

### Environment Variables

Create a `.env` file in the project root. The following variables are required:

```env
SECRET_KEY=your-django-secret-key
ALLOWED_HOSTS=127.0.0.1,localhost

DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
```

---

### Running

**Development server:**

```bash
python manage.py runserver
```

**Celery worker** (required for background tasks):

```bash
celery -A Tadrees worker --loglevel=info
```

**Celery Beat scheduler** (required for automated session generation & cleanup):

```bash
celery -A Tadrees beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

---

## API Overview

All endpoints are prefixed with `/api/`. JWT token must be sent as `Authorization: Bearer <token>` on protected routes.

### Auth — `/api/users/`

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/users/login/` | Obtain JWT access & refresh tokens |
| `POST` | `/api/users/token/refresh/` | Refresh an access token |

### Users — `/api/users/`

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/users/staff/` | Create a new staff account *(Admin only)* |
| `GET` | `/api/users/staff/list/` | List all staff members *(Admin only)* |
| `GET` | `/api/users/admin/dashboard/` | Dashboard: all staff & teachers *(Admin only)* |
| `GET/POST` | `/api/users/teachers/` | List or create teachers *(Staff/Admin)* |
| `DELETE` | `/api/users/teachers/<id>/` | Delete a teacher *(Admin only)* |
| `GET/POST/PATCH/DELETE` | `/api/users/students/` | Full CRUD for students *(Staff/Admin)* |

### Academics — `/api/academics/`

| Method | Endpoint | Description |
|---|---|---|
| `GET/POST/PATCH/DELETE` | `/api/academics/subjects/` | Manage subjects |
| `GET/POST/PATCH/DELETE` | `/api/academics/schedules/` | Manage recurring schedules |
| `GET/POST/PATCH/DELETE` | `/api/academics/special-schedules/` | Manage one-off special sessions |
| `GET/POST/PATCH/DELETE` | `/api/academics/rooms/` | Manage rooms |
| `GET/POST/PATCH/DELETE` | `/api/academics/enrollments/` | Manage student enrollments |
| `GET` | `/api/academics/teachers/<id>/subject/` | Subjects taught by a teacher |
| `GET` | `/api/academics/teachers/<id>/schedule/` | Schedule for a teacher |

### Attendance — `/api/attendance/`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/attendance/sessions/today/` | Sessions scheduled for today |
| `GET` | `/api/attendance/sessions/upcoming/` | Upcoming sessions |
| `GET` | `/api/attendance/sessions/history/` | Past attendance history |
| `POST` | `/api/attendance/sessions/<id>/attend/` | Mark a student as attended |

### Finance — `/api/finance/`

| Method | Endpoint | Description |
|---|---|---|
| `GET/POST/PATCH/DELETE` | `/api/finance/products/` | Manage product catalog |
| `GET/POST/PATCH/DELETE` | `/api/finance/payments/` | Record and view payments |

### Center — `/api/center/`

| Method | Endpoint | Description |
|---|---|---|
| `GET/POST/PATCH/DELETE` | `/api/center/center-info/` | Manage center branding & contact info |
| `GET/POST/PATCH/DELETE` | `/api/center/announcements/` | Manage targeted announcements |

---

## Project Structure

```
yarab/
├── Tadrees/                  # Django project config (settings, URLs, Celery, tasks)
│   ├── settings.py
│   ├── urls.py
│   ├── celery.py
│   └── tasks.py
│
├── users/                    # User management: Auth, Staff, Admin, Teachers, Students
├── academics/                # Subjects, Rooms, Schedules, Special Schedules, Enrollments
├── attendance/               # Sessions and attendance tracking
├── finance/                  # Products, Payments
├── center/                   # Center info and Announcements
│
├── frontend/                 # Vanilla HTML/CSS/JS admin interface
│   ├── index.html            # Main dashboard entry
│   ├── login.html
│   ├── students.html
│   ├── teachers.html
│   ├── subjects.html
│   ├── schedule.html
│   ├── special-schedule.html
│   ├── products.html
│   ├── center.html
│   └── ...
│
├── seed.py                   # Database seeding script for development
├── requirements.txt
└── .env                      # Environment variables (not committed)
```

| App | Role |
|---|---|
| `users` | Custom user model with roles, staff/admin/teacher/student profiles |
| `academics` | Subject catalog, rooms, recurring & special schedule management, enrollment |
| `attendance` | Session lifecycle, student attendance recording, history views |
| `finance` | Payment recording for enrollments, sessions, and products |
| `center` | Center branding, contact info, and role-targeted announcements |
| `frontend` | Static HTML/JS admin UI consuming the REST API |

---

## Preview

<!-- Add screenshots or demo video here -->
![Screenshot](./screenshots/screenshot1.png)
<img width="1918" height="946" alt="home page" src="https://github.com/user-attachments/assets/8a39a49a-baeb-4dac-93d1-8eaaeda76562" />
<img width="1917" height="946" alt="announcment" src="https://github.com/user-attachments/assets/06ea930e-b9b6-4764-a92b-7030db3be71c" />
<img width="1912" height="945" alt="Teacher_details" src="https://github.com/user-attachments/assets/600031ab-122d-4ed9-ab82-114f2f993213" />
<img width="1917" height="948" alt="student _add" src="https://github.com/user-attachments/assets/e7b82010-21a7-4739-a1cf-45720fa98e90" />
<img width="1919" height="948" alt="subject_details" src="https://github.com/user-attachments/assets/f9f80690-a25c-45df-8f9d-ee962dc1556a" />
<img width="1917" height="945" alt="teacher_subject" src="https://github.com/user-attachments/assets/4b94594a-2426-4767-a021-35fde9cdbb90" />
<img width="1919" height="946" alt="schedule" src="https://github.com/user-attachments/assets/76915bb6-ce7a-4bba-b798-d73bae1b46e4" />
<img width="1915" height="944" alt="special schedules" src="https://github.com/user-attachments/assets/a6779187-c872-428f-8ec8-89fcba3db430" />
<img width="1915" height="947" alt="payment" src="https://github.com/user-attachments/assets/f938ddbb-709c-44f8-a29e-34c54d9eb3f9" />
<img width="1916" height="948" alt="Login" src="https://github.com/user-attachments/assets/50caa8d7-4090-42cf-9b0d-c641649a8ffc" />


---

## License

This project is unlicensed. All rights reserved by the author.
