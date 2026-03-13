from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
from datetime import timedelta
import re

# --- GLOBAL XP CONFIG ---

class GlobalXPConfig(models.Model):
    """
    Singleton-style config for XP thresholds and rewards.
    """
    # Section Specific Thresholds
    listening_int_threshold = models.IntegerField(default=200)
    listening_pro_threshold = models.IntegerField(default=1000)
    
    reading_int_threshold = models.IntegerField(default=200)
    reading_pro_threshold = models.IntegerField(default=1000)
    
    writing_int_threshold = models.IntegerField(default=200)
    writing_pro_threshold = models.IntegerField(default=1000)
    
    learning_int_threshold = models.IntegerField(default=200)
    learning_pro_threshold = models.IntegerField(default=1000)
    
    # Granular Defaults reward XP (Points earned per activity)
    listening_beginner_xp = models.IntegerField(default=5)
    listening_intermediate_xp = models.IntegerField(default=10)
    listening_professional_xp = models.IntegerField(default=15)
    
    reading_beginner_xp = models.IntegerField(default=5)
    reading_intermediate_xp = models.IntegerField(default=10)
    reading_professional_xp = models.IntegerField(default=15)
    
    writing_beginner_xp = models.IntegerField(default=5)
    writing_intermediate_xp = models.IntegerField(default=10)
    writing_professional_xp = models.IntegerField(default=15)
    
    learning_beginner_xp = models.IntegerField(default=5)
    learning_intermediate_xp = models.IntegerField(default=10)
    learning_professional_xp = models.IntegerField(default=15)
    
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def get_config(cls):
        obj, _ = cls.objects.get_or_create(id=1)
        return obj

    def __str__(self):
        return f"XP Config (Last updated: {self.updated_at.strftime('%Y-%m-%d %H:%M')})"

# --- STUDENT PROFILE ---

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    student_id = models.CharField(max_length=20, unique=True)
    is_approved = models.BooleanField(default=False) 
    
    # Progress Data
    total_xp = models.IntegerField(default=0)
    listening_xp = models.IntegerField(default=0)
    speaking_xp = models.IntegerField(default=0)
    reading_xp = models.IntegerField(default=0)
    writing_xp = models.IntegerField(default=0)
    learning_xp = models.IntegerField(default=0)
    
    current_streak = models.IntegerField(default=0)
    last_streak_date = models.DateField(null=True, blank=True)
    daily_goal_minutes = models.IntegerField(default=20)
    unlocked_chapter = models.IntegerField(default=1)
    rank_percentage = models.FloatField(default=100.0)
    
    # Global Ranking Fields (Rank in the whole student population)
    overall_rank = models.IntegerField(default=0)
    listening_rank = models.IntegerField(default=0)
    reading_rank = models.IntegerField(default=0)
    writing_rank = models.IntegerField(default=0)
    learning_rank = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    
    profile_photo = models.ImageField(
        upload_to='profile_photos/', 
        null=True, 
        blank=True,
        default='profile_photos/default_user.png'
    )

    # Social & Availability
    is_online = models.BooleanField(default=False)
    is_dnd = models.BooleanField(default=False)
    friends = models.ManyToManyField(User, blank=True, related_name='friends_set')

    def check_completion_for_level(self, level_name):
        """
        Checks if the student has completed all content for a specific level 
        across Listening, Reading, Writing, and Grammar.
        """
        from lessons_listening.models import ListeningLesson
        from lessons_reading.models import ReadingStory
        from lessons_writing.models import WritingTask
        from lessons_learning.models import Chapter
        from .models import ActivityLog

        # 1. Get total counts for each section at this level
        total_listening = ListeningLesson.objects.filter(level=level_name).count()
        total_reading = ReadingStory.objects.filter(level=level_name).count()
        total_writing = WritingTask.objects.filter(level=level_name).count()
        total_learning = Chapter.objects.filter(level=level_name).count()

        # If no content exists for this level, consider it "completed" to avoid getting stuck
        if total_listening == 0 and total_reading == 0 and total_writing == 0 and total_learning == 0:
            return True

        # 2. Get completed counts for this student
        # We use unique item_id to ensure they can't game it by doing the same lesson twice
        completed_listening = ActivityLog.objects.filter(
            student=self.user, activity_type='LISTENING', quiz_score__gte=80  # Assuming 80% is passing
        ).values('item_id').distinct().count()

        completed_reading = ActivityLog.objects.filter(
            student=self.user, activity_type='READING', quiz_score__gte=80
        ).values('item_id').distinct().count()

        completed_writing = ActivityLog.objects.filter(
            student=self.user, activity_type='WRITING', quiz_score__gte=80
        ).values('item_id').distinct().count()

        completed_learning = ActivityLog.objects.filter(
            student=self.user, activity_type='LEARNING', quiz_score__gte=80
        ).values('item_id').distinct().count()

        # 3. Final Check
        return (
            completed_listening >= total_listening and
            completed_reading >= total_reading and
            completed_writing >= total_writing and
            completed_learning >= total_learning
        )

    def validate_streak(self):
        """
        Validates and updates the current streak based on the last streak date.
        Call this method whenever the student completes a significant activity.
        """
        today = timezone.localdate()
        
        # If no previous date, start the streak
        if self.last_streak_date is None:
            self.current_streak = 1
            self.last_streak_date = today
            self.save(update_fields=['current_streak', 'last_streak_date'])
            return self.current_streak
            
        # If already updated today, no changes
        if self.last_streak_date == today:
            return self.current_streak
            
        # If the last streak was exactly yesterday, increment
        if self.last_streak_date == today - timedelta(days=1):
            self.current_streak += 1
        else:
            # Otherwise, the streak was broken, reset to 1
            self.current_streak = 1
            
        self.last_streak_date = today
        self.save(update_fields=['current_streak', 'last_streak_date'])
        return self.current_streak

    def get_section_level(self, section_type, xp):
        """
        Returns the level for a specific section based on its own thresholds.
        """
        config = GlobalXPConfig.get_config()
        
        # Determine which thresholds to use
        int_thresh = getattr(config, f"{section_type.lower()}_int_threshold", 200)
        pro_thresh = getattr(config, f"{section_type.lower()}_pro_threshold", 1000)

        if xp >= pro_thresh:
            return 'PROFESSIONAL'
        if xp >= int_thresh:
            return 'INTERMEDIATE'
        return 'BEGINNER'

    @property
    def listening_level(self): return self.get_section_level('listening', self.listening_xp)

    @property
    def speaking_level(self): return "N/A"

    @property
    def reading_level(self): return self.get_section_level('reading', self.reading_xp)

    @property
    def writing_level(self): return self.get_section_level('writing', self.writing_xp)

    @property
    def learning_level(self): return self.get_section_level('learning', self.learning_xp)

    @classmethod
    def update_global_ranks(cls):
        """
        Expensive operation to recalculate ranks for everyone.
        Ideally run in background or periodically.
        """
        from django.db.models import Window, F
        from django.db.models.functions import Rank

        # 1. Overall Rank
        profiles = cls.objects.annotate(
            new_overall_rank=Window(expression=Rank(), order_by=F('total_xp').desc())
        )
        for p in profiles:
            cls.objects.filter(id=p.id).update(overall_rank=p.new_overall_rank)

        # 2. Section Ranks
        sections = ['listening', 'reading', 'writing', 'learning']
        for section in sections:
            field = f"{section}_xp"
            rank_field = f"{section}_rank"
            profiles = cls.objects.annotate(
                new_rank=Window(expression=Rank(), order_by=F(field).desc())
            )
            for p in profiles:
                cls.objects.filter(id=p.id).update(**{rank_field: p.new_rank})

    def __str__(self):
        status = "✅" if self.is_approved else "⏳ Pending"
        return f"{self.user.username} - {status}"

class ActivityLog(models.Model):
    ACTIVITY_CHOICES = [
        ('LISTENING', 'Listening'), ('SPEAKING', 'Speaking'), 
        ('LEARNING', 'Learning'), ('READING', 'Reading'), ('WRITING', 'Writing'),
    ]
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_CHOICES)
    duration_minutes = models.FloatField(default=0.0)
    quiz_score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], null=True, blank=True)
    xp_earned = models.IntegerField(default=0, help_text="Specific XP earned for this activity")
    item_id = models.IntegerField(null=True, blank=True, help_text="ID of the lesson/chapter/story")
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            xp_to_add = getattr(self, 'xp_earned', 0)

            # Rule: If a quiz is present, it must be passed (>= 50%) to earn XP or unlock content
            is_quiz_passed = True
            if self.quiz_score is not None and self.quiz_score < 50:
                is_quiz_passed = False
                xp_to_add = 0
            
            # Enforce video-duration-based time tracking for specific sections
            try:
                if self.activity_type == 'LEARNING' and self.item_id:
                    from lessons_learning.models import Chapter
                    chapter = Chapter.objects.filter(id=self.item_id).first()
                    if chapter and chapter.video_duration_minutes > 0:
                        self.duration_minutes = chapter.video_duration_minutes
                elif self.activity_type == 'LISTENING' and self.item_id:
                    from lessons_listening.models import ListeningLesson
                    lesson = ListeningLesson.objects.filter(id=self.item_id).first()
                    if lesson and lesson.video_duration_minutes > 0:
                        self.duration_minutes = lesson.video_duration_minutes
            except Exception:
                pass

            try:
                if hasattr(self.student, 'profile'):
                    profile = self.student.profile
                    
                    if is_quiz_passed:
                        # Use GlobalXPConfig for rewards instead of frontend trust
                        config = GlobalXPConfig.get_config()
                        
                        if self.activity_type == 'LISTENING':
                            lvl = profile.listening_level
                            if lvl == 'PROFESSIONAL': xp_to_add = config.listening_professional_xp
                            elif lvl == 'INTERMEDIATE': xp_to_add = config.listening_intermediate_xp
                            else: xp_to_add = config.listening_beginner_xp
                        elif self.activity_type == 'READING':
                            lvl = profile.reading_level
                            if lvl == 'PROFESSIONAL': xp_to_add = config.reading_professional_xp
                            elif lvl == 'INTERMEDIATE': xp_to_add = config.reading_intermediate_xp
                            else: xp_to_add = config.reading_beginner_xp
                        elif self.activity_type == 'WRITING':
                            lvl = profile.writing_level
                            if lvl == 'PROFESSIONAL': xp_to_add = config.writing_professional_xp
                            elif lvl == 'INTERMEDIATE': xp_to_add = config.writing_intermediate_xp
                            else: xp_to_add = config.writing_beginner_xp
                        elif self.activity_type == 'LEARNING':
                            lvl = profile.learning_level
                            if lvl == 'PROFESSIONAL': xp_to_add = config.learning_professional_xp
                            elif lvl == 'INTERMEDIATE': xp_to_add = config.learning_intermediate_xp
                            else: xp_to_add = config.learning_beginner_xp
                        else:
                            xp_to_add = 0

                        self.xp_earned = xp_to_add
                        profile.total_xp += xp_to_add
                        if self.activity_type == 'LISTENING': profile.listening_xp += xp_to_add
                        elif self.activity_type == 'READING': profile.reading_xp += xp_to_add
                        elif self.activity_type == 'WRITING': profile.writing_xp += xp_to_add
                        elif self.activity_type == 'LEARNING': profile.learning_xp += xp_to_add
                        
                        if self.activity_type == 'LEARNING' and self.quiz_score and self.quiz_score >= 50:
                            profile.unlocked_chapter += 1
                            # Update state to point to next chapter
                            from .models import StudentState
                            state, _ = StudentState.objects.get_or_create(student=self.student)
                            state.last_activity_type = 'LEARNING'
                            state.last_item_id = profile.unlocked_chapter
                            state.save()
                        
                        profile.validate_streak()
                        profile.save()
            except Exception:
                pass 
        super().save(*args, **kwargs)

def generate_next_student_id():
    """Finds the highest NAT-XXXX ID and increments it."""
    # Try to find the highest existing ID formatted as NAT-XXXX
    # This queries all profiles and finds the one with the highest string value
    # which works well for zero-padded strings like NAT-0001
    last_profile = StudentProfile.objects.filter(student_id__startswith='NAT-').order_by('-student_id').first()
    
    if last_profile:
        match = re.search(r'NAT-(\d+)', last_profile.student_id)
        if match:
            try:
                last_num = int(match.group(1))
                return f"NAT-{(last_num + 1):04d}"
            except ValueError:
                pass
    
    return "NAT-0001"

@receiver(post_save, sender=User)
def manage_user_profile(sender, instance, created, **kwargs):
    """Creates a profile for new users or ensures one exists for old users."""
    if created:
        StudentProfile.objects.create(
            user=instance, 
            student_id=generate_next_student_id()
        )
    else:
        if not hasattr(instance, 'profile'):
            StudentProfile.objects.get_or_create(
                user=instance, 
                defaults={'student_id': generate_next_student_id()}
            )
        else:
            instance.profile.save()


@receiver(post_save, sender=StudentProfile)
def sync_user_permissions(sender, instance, **kwargs):
    """
    Syncs StudentProfile.is_approved with User.is_active.
    Ensures students stay students, but PROTECTS superusers/staff.
    """
    user = instance.user
    # If the user is a superuser or staff, we should NOT strip their permissions
    if user.is_superuser or user.is_staff:
        # We also ensure superusers are always "approved" in their profile
        if not instance.is_approved:
            StudentProfile.objects.filter(id=instance.id).update(is_approved=True)
        return
    # We use .update() to avoid triggering the User.post_save signal recursively
    User.objects.filter(id=instance.user.id).update(
        is_active=instance.is_approved,
        is_staff=False,
        is_superuser=False
    )
# --- STUDENT STATE (Persistent App State) ---

class StudentState(models.Model):
    """
    Stores 'live' app state, draft content, and last accessed items 
    to allow resuming from the last point.
    """
    student = models.OneToOneField(User, on_delete=models.CASCADE, related_name='state')
    last_activity_type = models.CharField(max_length=20, blank=True, null=True)
    last_item_id = models.IntegerField(blank=True, null=True)
    live_data = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"State for {self.student.username}"

@receiver(post_save, sender=User)
def manage_student_state(sender, instance, created, **kwargs):
    """Ensures every user has a StudentState object."""
    if created:
        StudentState.objects.get_or_create(student=instance)
    else:
        if not hasattr(instance, 'state'):
            StudentState.objects.get_or_create(student=instance)
