from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Chapter, GrammarExample, GrammarQuiz
from .serializers import ChapterSerializer, GrammarExampleSerializer, GrammarQuizSerializer

try:
    from core_api.permissions import IsApprovedStudent, IsSuperUser
except ImportError:
    from rest_framework.permissions import IsApprovedStudent
    from rest_framework.permissions import IsAdminUser as IsSuperUser

class LearningMixin:
    @action(detail=False, methods=['get'])
    def current_learning(self, request):
        """Learning: Gets current Chapter with Primary and Backup examples."""
        profile = request.user.profile
        try:
            chapter = Chapter.objects.get(order=profile.unlocked_chapter)
        except Chapter.DoesNotExist:
            return Response({"message": "You have completed all available chapters!"}, status=status.HTTP_404_NOT_FOUND)
        
        examples = chapter.examples.filter(is_backup=False)[:5]
        backups = chapter.examples.filter(is_backup=True)[:5]
        quiz = chapter.quizzes.all()[:3]
        
        return Response({
            "chapter_title": chapter.title,
            "grammar_logic": getattr(chapter, 'grammar_rule_malayalam', ""),
            "primary_examples": [{"en": e.english_text, "ml": e.malayalam_explanation} for e in examples],
            "backup_examples": [{"en": b.english_text, "ml": b.malayalam_explanation} for b in backups],
            "quiz": [
                {
                    "id": q.id,
                    "question": q.question_text,
                    "options": [q.option_a, q.option_b, q.option_c, q.option_d],
                    "correct": q.correct_option
                } for q in quiz
            ]
        })

from rest_framework.pagination import PageNumberPagination

class ChapterViewSet(viewsets.ModelViewSet, LearningMixin):
    serializer_class = ChapterSerializer
    pagination_class = PageNumberPagination
    search_fields = ['title', 'grammar_rule_malayalam']

    def get_queryset(self):
        # We now return all chapters, and the 'is_locked' field in the serializer
        # tells the frontend which ones are playable.
        return Chapter.objects.all().order_by('order')
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'current_learning']:
            return [IsApprovedStudent()]
        if self.action in ['update', 'partial_update']:
            return [IsApprovedStudent()]
        return [IsSuperUser()]

    def perform_update(self, serializer):
        if self.request.user.is_superuser:
            serializer.save()
        else:
            from rest_framework.exceptions import PermissionDenied, ValidationError
            
            # For students, we only allow updating is_completed.
            is_completed = serializer.validated_data.get('is_completed')
            quiz_score = serializer.validated_data.get('quiz_score')

            # 1. Strip all other fields
            allowed_fields = ['is_completed', 'quiz_score']
            keys_to_remove = [k for k in serializer.validated_data.keys() if k not in allowed_fields]
            for k in keys_to_remove:
                serializer.validated_data.pop(k)
            
            # 2. Validation: If marking as completed, must have a passing quiz score
            if is_completed is True:
                if quiz_score is None:
                    raise ValidationError({"quiz_score": "Quiz score is required to complete this chapter."})
                
                if quiz_score < 70:
                    raise PermissionDenied(f"Quiz score {quiz_score}% is too low. You need 70% or higher to complete this chapter.")
                
                # Advance student progress
                profile = getattr(self.request.user, 'profile', None)
                if profile and serializer.instance.order >= profile.unlocked_chapter:
                    profile.unlocked_chapter = serializer.instance.order + 1
                    profile.save()
            elif is_completed is False:
                # Students shouldn't be "un-completing" chapters through this endpoint
                raise PermissionDenied("Chapters cannot be marked as incomplete once finished.")
            elif 'is_completed' not in serializer.validated_data:
                # If they hit the endpoint but didn't provide is_completed
                raise ValidationError("You can only update the 'is_completed' status.")

            serializer.save()

class GrammarExampleViewSet(viewsets.ModelViewSet):
    queryset = GrammarExample.objects.all()
    serializer_class = GrammarExampleSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsApprovedStudent()]
        return [IsSuperUser()]

class GrammarQuizViewSet(viewsets.ModelViewSet):
    queryset = GrammarQuiz.objects.all()
    serializer_class = GrammarQuizSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsApprovedStudent()]
        return [IsSuperUser()]
