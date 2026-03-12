# Refined Time Tracking via Video Durations

## Goal
Improve accuracy of student "spending time" metrics. For the Learning and Listening sections, time spent will be calculated based on the content's video duration rather than simple browser dwell time. This prevents students from artificially inflating their study time. We will also ensure that any section entry/exit calculates time accurately if the frontend supports it.

## User Review Required
> [!IMPORTANT]
> This change will strictly override the `duration_minutes` recorded in activity logs for the Learning and Listening sections based on the content's video duration.

> [!NOTE]
> The "Start/Pause" timer requested is a frontend implementation. Since the student dashboard is an external consumer (mobile/API-based), this plan focuses on the Backend/Admin support.

## Proposed Changes

### Core API
#### [MODIFY] [models.py](file:///c:/Users/aswin/OneDrive/Desktop/SKILL%20PARK/APPS/ENGLISH/english/core_api/models.py)
- Update `ActivityLog.save()`:
    - If `activity_type` is 'LEARNING' or 'LISTENING', look up the associated `item_id`.
    - Retrieve the `video_duration_minutes` from the [Chapter](file:///c:/Users/aswin/OneDrive/Desktop/SKILL%20PARK/APPS/ENGLISH/english/lessons_learning/models.py#3-16) or [ListeningLesson](file:///c:/Users/aswin/OneDrive/Desktop/SKILL%20PARK/APPS/ENGLISH/english/lessons_listening/models.py#3-13).
    - If a duration exists, set `self.duration_minutes = duration`.

### Lessons Learning
#### [MODIFY] [models.py](file:///c:/Users/aswin/OneDrive/Desktop/SKILL%20PARK/APPS/ENGLISH/english/lessons_learning/models.py)
- Add `video_url` (URLField) and `video_duration_minutes` (FloatField) to the [Chapter](file:///c:/Users/aswin/OneDrive/Desktop/SKILL%20PARK/APPS/ENGLISH/english/lessons_learning/models.py#3-16) model.

#### [MODIFY] [serializers.py](file:///c:/Users/aswin/OneDrive/Desktop/SKILL%20PARK/APPS/ENGLISH/english/lessons_learning/serializers.py)
- Include new video fields in [ChapterSerializer](file:///c:/Users/aswin/OneDrive/Desktop/SKILL%20PARK/APPS/ENGLISH/english/lessons_learning/serializers.py#18-122).

### Lessons Listening
#### [MODIFY] [models.py](file:///c:/Users/aswin/OneDrive/Desktop/SKILL%20PARK/APPS/ENGLISH/english/lessons_listening/models.py)
- Add `video_duration_minutes` (FloatField) to the [ListeningLesson](file:///c:/Users/aswin/OneDrive/Desktop/SKILL%20PARK/APPS/ENGLISH/english/lessons_listening/models.py#3-13) model.

#### [MODIFY] [serializers.py](file:///c:/Users/aswin/OneDrive/Desktop/SKILL%20PARK/APPS/ENGLISH/english/lessons_listening/serializers.py)
- Include `video_duration_minutes` in [ListeningLessonSerializer](file:///c:/Users/aswin/OneDrive/Desktop/SKILL%20PARK/APPS/ENGLISH/english/lessons_listening/serializers.py#9-40).

### Admin Dashboard
#### [MODIFY] [dashboard.js](file:///c:/Users/aswin/OneDrive/Desktop/SKILL%20PARK/APPS/ENGLISH/english/core_api/static/core_api/dashboard.js)
- Update [openEntityModal](file:///c:/Users/aswin/OneDrive/Desktop/SKILL%20PARK/APPS/ENGLISH/english/core_api/static/core_api/dashboard.js#516-628) to include inputs for the new video fields when editing Chapters or Listening Lessons.

---

## Verification Plan

### Automated Tests
- Create a [Chapter](file:///c:/Users/aswin/OneDrive/Desktop/SKILL%20PARK/APPS/ENGLISH/english/lessons_learning/models.py#3-16) with 10 minutes duration.
- Log an activity for that chapter with 60 minutes dwell time.
- Verify the [ActivityLog](file:///c:/Users/aswin/OneDrive/Desktop/SKILL%20PARK/APPS/ENGLISH/english/core_api/models.py#180-229) record shows exactly 10 minutes.
- Verify the Student Report sums the time correctly.

### Manual Verification
- Use the Admin Dashboard to add a video duration to a chapter.
- Save and verify the data persists.
- Check the "Detailed Report" for a student to see the updated "Spending Time" calculation.
