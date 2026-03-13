# XP Management API Documentation

The XP Management API allows administrators to configure levels (thresholds) and rewards for each skill section in the platform.

## 1. Get Current XP Configuration
Retrieve the current thresholds and reward settings.

**Endpoint**: `GET /api/xp-config/`
**Permission**: Authenticated (Student/Admin)

### Response Example
```json
{
  "listening_int_threshold": 200,
  "listening_pro_threshold": 1000,
  "listening_beginner_xp": 5,
  "listening_intermediate_xp": 10,
  "listening_professional_xp": 15,
  "reading_int_threshold": 200,
  "reading_pro_threshold": 1000,
  ...
  "updated_at": "2026-03-13T10:00:00Z"
}
```

---

## 2. Update XP Configuration
Modify thresholds or rewards. Only fields provided in the payload will be updated (Partial Update).

**Endpoint**: `PATCH /api/xp-config/` (or `POST`)
**Permission**: Admin Only

### Request Fields
| Field Pattern | Type | Description |
| :--- | :--- | :--- |
| `[section]_int_threshold` | integer | XP required to reach **Intermediate** status. |
| `[section]_pro_threshold` | integer | XP required to reach **Professional** status. |
| `[section]_beginner_xp` | integer | XP rewarded per activity for **Beginner** level. |
| `[section]_intermediate_xp`| integer | XP rewarded per activity for **Intermediate** level. |
| `[section]_professional_xp`| integer | XP rewarded per activity for **Professional** level. |

**Available Sections**: [listening](file:///c:/Users/aswin/OneDrive/Desktop/SKILL%20PARK/APPS/ENGLISH/english/core_api/models.py#190-192), [reading](file:///c:/Users/aswin/OneDrive/Desktop/SKILL%20PARK/APPS/ENGLISH/english/core_api/models.py#196-198), [writing](file:///c:/Users/aswin/OneDrive/Desktop/SKILL%20PARK/APPS/ENGLISH/english/core_api/models.py#199-201), [learning](file:///c:/Users/aswin/OneDrive/Desktop/SKILL%20PARK/APPS/ENGLISH/english/core_api/models.py#202-204)

> [!IMPORTANT]
> **Speaking Section**: Speaking XP fields are **deleted** and cannot be configured via the API. Speaking rewards are hardcoded to 0 XP.

### Example Request (Update Listening Rewards)
```json
{
  "listening_beginner_xp": 8,
  "listening_intermediate_xp": 12
}
```

---

## 3. UI Implementation Detail
In the admin panel, the [renderXPManagement()](file:///c:/Users/aswin/OneDrive/Desktop/SKILL%20PARK/APPS/ENGLISH/english/core_api/static/core_api/dashboard.js#1033-1118) function in [dashboard.js](file:///c:/Users/aswin/OneDrive/Desktop/SKILL%20PARK/APPS/ENGLISH/english/core_api/static/core_api/dashboard.js) fetches this data and generates cards for each active section. When "Save" is clicked, it sends a `PATCH` request to this endpoint.
