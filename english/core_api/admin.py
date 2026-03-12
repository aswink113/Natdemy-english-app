from django.contrib import admin
from .models import StudentProfile, ActivityLog, GlobalXPConfig

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'student_id', 'total_xp', 'current_level', 'is_approved')
    list_filter = ('is_approved',)
    search_fields = ('user__username', 'student_id')

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('id','student', 'activity_type', 'duration_minutes', 'quiz_score', 'timestamp')
    list_filter = ('activity_type', 'timestamp')

@admin.register(GlobalXPConfig)
class GlobalXPConfigAdmin(admin.ModelAdmin):
    list_display = ('id', 'overall_intermediate', 'overall_professional', 'section_intermediate', 'section_professional', 'updated_at')
    fieldsets = (
        ('Overall Level Thresholds', {
            'fields': ('overall_intermediate', 'overall_professional')
        }),
        ('Section Level Thresholds', {
            'fields': ('section_intermediate', 'section_professional')
        }),
        ('Legacy & Base Rewards', {
            'fields': ('points_per_activity',)
        }),
        ('Listening Rewards', {
            'fields': ('listening_beginner_xp', 'listening_intermediate_xp', 'listening_professional_xp')
        }),
        ('Speaking Rewards', {
            'fields': ('speaking_beginner_xp', 'speaking_intermediate_xp', 'speaking_professional_xp')
        }),
        ('Reading Rewards', {
            'fields': ('reading_beginner_xp', 'reading_intermediate_xp', 'reading_professional_xp')
        }),
        ('Writing Rewards', {
            'fields': ('writing_beginner_xp', 'writing_intermediate_xp', 'writing_professional_xp')
        }),
        ('Grammar (Learning) Rewards', {
            'fields': ('learning_beginner_xp', 'learning_intermediate_xp', 'learning_professional_xp')
        }),
    )