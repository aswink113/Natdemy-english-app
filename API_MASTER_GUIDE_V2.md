# API Master Guide - Natdemy English Academy

This guide provides a comprehensive overview of the Natdemy English Academy API.

## 1. Authentication
Endpoints for user login and token management.

- **Login**: `POST /api/login/`
  - Body: `{"username": "...", "password": "..."}`
  - Returns: `access` and `refresh` JWT tokens.
- **Refresh Token**: `POST /api/token/refresh/`
  - Body: `{"refresh": "..."}`
- **Logout**: `POST /api/logout/`
  - Body: `{"refresh": "..."}`

---

## 2. Student Activity & Time Tracking [NEW UPDATES]
Endpoints for logging study sessions and monitoring "Spending Time" accurately.

### Log Activity
- **Endpoint**: `POST /api/students/log-activity/`
- **Body**:
  ```json
  {
    "activity_type": "LEARNING",
    "duration_minutes": 15.0,
    "item_id": 4,
    "quiz_score": 90,
    "xp_earned": 10
  }
  ```
- **Validation Rules**:
  - **Learning (Grammar) & Listening**: The `duration_minutes` is automatically calculated by the backend based on the **Video Duration** set by the admin for that specific `item_id`.
  - **Reading, Writing, Speaking**: The client-provided `duration_minutes` is saved as-is.

### Student State (Real-time tracking)
- **Endpoint**: `PATCH /api/students/state/`
- **Purpose**: Track active sessions before completion (Pause/Resume).

---

## 3. Section Endpoints (Curriculum)

### Listening
- **List Lessons**: `GET /api/listening/`
- **Detailed Lesson**: `GET /api/listening/<id>/` (Includes questions and video duration)

### Learning (Grammar Topics)
- **Current Learning**: `GET /api/learning/chapters/current_learning/`
- **List Chapters**: `GET /api/learning/chapters/`
- **Update Chapter Progress**: `PATCH /api/learning/chapters/<id>/` (Mark `is_completed: true` requires quiz score >= 50%)

### Reading
- **List Stories**: `GET /api/reading/`
- **Story Details**: `GET /api/reading/<id>/`

### Writing
- **List Tasks**: `GET /api/writing/`

---

## 4. XP & Profile Management

### Student Profile
- **Get Profile**: `GET /api/students/<id>/`
- **Detailed Dashboard**: `GET /api/students/dashboard/`
- **Update Photo**: `POST /api/students/update-photo/`

### Global XP Config (Admin Only)
- **Current Config**: `GET /api/xp-config/current/`
- **Update Config**: `PATCH /api/xp-config/update_config/`

---

## 5. Admin & Analytics

### Admin Stats
- **Dashboard Stats**: `GET /api/students/admin_stats/`
- **Student Detailed Report**: `GET /api/students/<id>/student_report/` (Shows breakdown of accurate time spent in each section)

### Bulk Import
- **CSV Student Import**: `POST /api/students/bulk-import/` (File upload)
