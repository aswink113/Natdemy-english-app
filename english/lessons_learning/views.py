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
            # For students, we only allow updating is_completed.
            # We strip any other data from the serializer's validated_data just in case.
            allowed_fields = ['is_completed']
            keys_to_remove = [k for k in serializer.validated_data.keys() if k not in allowed_fields]
            for k in keys_to_remove:
                serializer.validated_data.pop(k)
            
            # Additional check: ensure they are only trying to set is_completed to True
            if serializer.validated_data.get('is_completed') is not True:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("Students can only mark chapters as completed.")

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
