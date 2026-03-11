import os
import django
import sys

# Setup Django environment
sys.path.append('c:/Users/aswin/OneDrive/Desktop/SKILL PARK/APPS/ENGLISH/english')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'natdemy_english.settings')
django.setup()

from django.contrib.auth.models import User
from core_api.models import StudentProfile, ActivityLog

def verify_new_logic():
    # 1. Setup - get or create test user
    username = 'verify_test_user'
    user, created = User.objects.get_or_create(username=username, defaults={'email': 'test@example.com'})
    if created:
        user.set_password('password123')
        user.save()
        print(f"Created new test user: {username}")
    
    profile = user.profile
    profile.total_xp = 0
    profile.learning_xp = 0
    profile.unlocked_chapter = 1
    profile.save()
    
    print(f"\n--- Starting Logic Verification ---")
    print(f"Initial State: Chapter={profile.unlocked_chapter}, XP={profile.total_xp}")

    # TEST 1: "1 Right, 2 Wrong" (33%)
    # Total 3 questions. 1 right = ~33%. Should FAIL.
    print("\n[TEST 1] Simulating 1 Right, 2 Wrong (Score: 33%)...")
    ActivityLog.objects.create(
        student=user, 
        activity_type='LEARNING', 
        quiz_score=33, 
        xp_earned=5,
        item_id=1
    )
    profile.refresh_from_db()
    print(f"Result -> Chapter: {profile.unlocked_chapter} (Expected: 1), XP: {profile.total_xp} (Expected: 0)")
    
    if profile.unlocked_chapter == 1 and profile.total_xp == 0:
        print("✅ TEST 1 PASSED: Low score blocked progress and XP.")
    else:
        print("❌ TEST 1 FAILED!")

    # TEST 2: "2 Right, 1 Wrong" (66%)
    # Total 3 questions. 2 right = ~66%. Should PASS.
    print("\n[TEST 2] Simulating 2 Right, 1 Wrong (Score: 66%)...")
    ActivityLog.objects.create(
        student=user, 
        activity_type='LEARNING', 
        quiz_score=66, 
        xp_earned=10,
        item_id=1
    )
    profile.refresh_from_db()
    print(f"Result -> Chapter: {profile.unlocked_chapter} (Expected: 2), XP: {profile.total_xp} (Expected: 10)")
    
    if profile.unlocked_chapter == 2 and profile.total_xp == 10:
        print("✅ TEST 2 PASSED: Passing score unlocked next chapter and awarded XP.")
    else:
        print("❌ TEST 2 FAILED!")

    # TEST 3: Verifying explicit XP reward
    # Non-learning activity with 100% score but 0 xp_earned in request
    print("\n[TEST 3] Simulating Reading activity with 100% score but 0 xp_earned...")
    ActivityLog.objects.create(
        student=user, 
        activity_type='READING', 
        quiz_score=100, 
        xp_earned=0,
        item_id=10
    )
    profile.refresh_from_db()
    print(f"Result -> XP: {profile.total_xp} (Expected: 10 - no new XP gain)")
    
    if profile.total_xp == 10:
        print("✅ TEST 3 PASSED: No XP awarded when xp_earned is 0.")
    else:
        print("❌ TEST 3 FAILED!")

if __name__ == "__main__":
    verify_new_logic()
