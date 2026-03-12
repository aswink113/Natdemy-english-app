from rest_framework import serializers
from .models import Chapter, GrammarExample, GrammarQuiz

class GrammarExampleSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    class Meta:
        model = GrammarExample
        fields = ['id', 'english_text', 'malayalam_explanation', 'is_backup']

class GrammarQuizSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    class Meta:
        model = GrammarQuiz
        fields = ['id', 'question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option']

class ChapterSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    order = serializers.IntegerField(required=False)
    title = serializers.CharField(required=False)
    grammar_rule_malayalam = serializers.CharField(required=False)
    level = serializers.CharField(required=False)
    video_url = serializers.URLField(required=False, allow_null=True, allow_blank=True)
    video_duration_minutes = serializers.FloatField(required=False)
    xp_reward = serializers.IntegerField(required=False)
    
    # Relationships
    examples = GrammarExampleSerializer(many=True, required=False)
    quizzes = GrammarQuizSerializer(many=True, required=False)
    
    # Custom fields
    is_locked = serializers.SerializerMethodField()
    is_completed = serializers.SerializerMethodField()
    quiz_score = serializers.IntegerField(required=False, write_only=True)

    def get_is_locked(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_superuser:
            return False
        profile = getattr(request.user, 'profile', None)
        return obj.order > profile.unlocked_chapter if profile else True

    def get_is_completed(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return False
        profile = getattr(request.user, 'profile', None)
        return obj.order < profile.unlocked_chapter if profile else False

    def create(self, validated_data):
        examples_data = validated_data.pop('examples', [])
        quizzes_data = validated_data.pop('quizzes', [])
        chapter = Chapter.objects.create(**validated_data)
        for example_data in examples_data:
            GrammarExample.objects.create(chapter=chapter, **example_data)
        for quiz_data in quizzes_data:
            GrammarQuiz.objects.create(chapter=chapter, **quiz_data)
        return chapter

    def update(self, instance, validated_data):
        examples_data = validated_data.pop('examples', [])
        quizzes_data = validated_data.pop('quizzes', [])
        validated_data.pop('quiz_score', None)
        
        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update Examples
        if examples_data:
            keep_examples = []
            for example_data in examples_data:
                item_id = example_data.pop('id', None)
                if item_id:
                    try:
                        example_instance = GrammarExample.objects.get(id=item_id, chapter=instance)
                        for attr, value in example_data.items():
                            setattr(example_instance, attr, value)
                        example_instance.save()
                        keep_examples.append(example_instance.id)
                    except GrammarExample.DoesNotExist:
                        new_example = GrammarExample.objects.create(chapter=instance, **example_data)
                        keep_examples.append(new_example.id)
                else:
                    new_example = GrammarExample.objects.create(chapter=instance, **example_data)
                    keep_examples.append(new_example.id)

        # Update Quizzes
        if quizzes_data:
            keep_quizzes = []
            for quiz_data in quizzes_data:
                item_id = quiz_data.pop('id', None)
                if item_id:
                    try:
                        quiz_instance = GrammarQuiz.objects.get(id=item_id, chapter=instance)
                        for attr, value in quiz_data.items():
                            setattr(quiz_instance, attr, value)
                        quiz_instance.save()
                        keep_quizzes.append(quiz_instance.id)
                    except GrammarQuiz.DoesNotExist:
                        new_quiz = GrammarQuiz.objects.create(chapter=instance, **quiz_data)
                        keep_quizzes.append(new_quiz.id)
                else:
                    new_quiz = GrammarQuiz.objects.create(chapter=instance, **quiz_data)
                    keep_quizzes.append(new_quiz.id)
        
        return instance
