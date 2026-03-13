from django.contrib import admin
from .models import StudentProfile, ActivityLog, GlobalXPConfig

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'student_id', 'total_xp', 'overall_rank', 'is_approved')
    list_filter = ('is_approved',)
    search_fields = ('user__username', 'student_id')
    readonly_fields = ('overall_rank', 'listening_rank', 'reading_rank', 'writing_rank', 'learning_rank')

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('id','student', 'activity_type', 'duration_minutes', 'quiz_score', 'timestamp')
    list_filter = ('activity_type', 'timestamp')

@admin.register(GlobalXPConfig)
class GlobalXPConfigAdmin(admin.ModelAdmin):
    list_display = ('id', 'updated_at')
    fieldsets = (
        ('Section Level Thresholds', {
            'fields': (
                ('listening_int_threshold', 'listening_pro_threshold'),
                ('reading_int_threshold', 'reading_pro_threshold'),
                ('writing_int_threshold', 'writing_pro_threshold'),
                ('learning_int_threshold', 'learning_pro_threshold'),
            )
        }),
        ('Listening Rewards', {
            'fields': ('listening_beginner_xp', 'listening_intermediate_xp', 'listening_professional_xp')
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