# NATDEMY API SPECIFICATION

This document provides a complete list of all API endpoints for the Natdemy English Academy backend.

## 1. Authentication
Access control and token management.

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/login/` | `POST` | Login with username/password. Returns JWT Access/Refresh tokens. |
| `/api/token/refresh/` | `POST` | Get a new Access token using a Refresh token. |
| `/api/logout/` | `POST` | Blacklist a refresh token and log out. |

---

## 2. Student Profile & State
Managing personal data and real-time session status.

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/students/id/` | `GET` | Get profile details (XP, Level, Streak). |
| `/api/students/dashboard/`| `GET` | Get personalized dashboard stats (Student view). |
| `/api/students/update-photo/`| `POST` | Upload/Update profile photo. |
| `/api/students/state/` | `GET`/`POST` | Get or update current active session status (for start/pause timers). |
| `/api/students/digital_wellbeing/`| `GET` | Get screen time and usage analytics. |

---

## 3. Activity & Time Tracking
Submitting progress and XP.

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/students/log-activity/` | `POST` | **Critical**: Submit lesson completion. <br> - Handles `LEARNING`, `LISTENING`, `READING`, `WRITING`, `SPEAKING`. <br> - **Learning/Listening**: Auto-calculates time based on video duration. |
| `/api/students/reports/` | `GET` | Get average scores and total time spent per section. |

---

## 4. Curriculum Sections
Content retrieval for specific sections.

### Listening
- `GET /api/listening/` - List all listening lessons.
- `GET /api/listening/<id>/` - Get lesson details (audio URL, questions).

### Reading
- `GET /api/reading/` - List all reading stories.
- `GET /api/reading/<id>/` - Get story content and quiz questions.

### Writing
- `GET /api/writing/` - List all writing tasks.

### Learning (Grammar)
- `GET /api/learning/chapters/` - List grammar chapters.
- `GET /api/learning/chapters/current_learning/` - Get next chapter to study.
- `PATCH /api/learning/chapters/<id>/` - Update chapter status (requires quiz score >= 50%).

---

## 5. Social & Speaking
Connecting with others and discovery.

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/social/discover_students/` | `GET` | **NEW**: List students for friend requests (excludes existing friends). |
| `/api/social/list-friends/` | `GET` | List your friends with their Online/DND status. |
| `/api/social/send-request/` | `POST` | Send a request by username. |
| `/api/social/respond-request/<id>/`| `POST` | Accept (`status: ACCEPT`) or Reject a request. |
| `/api/social/toggle-status/`| `POST` | Toggle your profile between `ONLINE` and `DND`. |
| `/api/speaking/save/` | `POST` | Save a recording and log for a call session. |
| `/api/speaking/history/` | `GET` | List all past calls with recording URLs. |

---

## 6. Admin & Global Config
Higher-level management (Superuser only).

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/admin/register-student/` | `POST` | Create a new student account. |
| `/api/students/admin_stats/` | `GET` | Overall academy stats (Total students, XP, etc.). |
| `/api/students/bulk-import/` | `POST` | Bulk register students via CSV upload. |
| `/api/students/<id>/student_report/`| `GET` | Detailed engagement report for a specific student. |
| `/api/xp-config/` | `GET`/`PATCH`| Manage global XP thresholds and rewards. |
