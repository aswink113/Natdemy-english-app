# Leaderboard API Documentation

The leaderboard is powered by the `/students/` endpoint, utilizing Django REST Framework's `OrderingFilter`.

## 1. Fetching Rankings
To get the top students, use a `GET` request with the `ordering` parameter.

**Endpoint**: `GET /api/students/`

### Query Parameters
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `ordering` | string | Optional | Field to sort by. Use `-` prefix for descending order. |
| `page` | integer | Optional | Page number for pagination. |
| `page_size` | integer | Optional | Number of results per page (Default: 10, Max: 50). |

### Available Sorting Fields
| Field | Description |
| :--- | :--- |
| `-total_xp` | Rank by Overall XP (Default Leaderboard) |
| `-listening_xp` | Rank by Listening Skill |
| `-reading_xp` | Rank by Reading Skill |
| `-writing_xp` | Rank by Writing Skill |
| `-learning_xp` | Rank by Learning Skill |
| `-overall_rank` | Rank by Global position |

---

## 2. Request Examples

### Get Top 10 Overall Students
```http
GET /api/students/?ordering=-total_xp&page_size=10
```

### Get Writing Specialists (Top 20)
```http
GET /api/students/?ordering=-writing_xp&page_size=20
```

---

## 3. Response Structure
The response follows a standard paginated format.

```json
{
  "count": 150,
  "next": "http://example.com/api/students/?ordering=-total_xp&page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "username": "johndoe",
      "student_id": "NAT-0001",
      "total_xp": 1250,
      "overall_rank": 1,
      "listening_xp": 400,
      "listening_rank": 2,
      "listening_level": "INTERMEDIATE",
      "learning_xp": 200,
      "learning_level": "BEGINNER",
      ...
    }
  ]
}
```

## 4. Permissions
- **Authenticated Users**: Can view the list.
- **Filtering**: Rankings are calculated in real-time on the server and cached in the database fields for performance.
