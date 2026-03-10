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

class ChapterSerializer(serializers.ModelSerializer):
    examples = GrammarExampleSerializer(many=True, required=False)
    quizzes = GrammarQuizSerializer(many=True, required=False)
    is_locked = serializers.SerializerMethodField()
    is_completed = serializers.BooleanField(required=False)

    class Meta:
        model = Chapter
        fields = '__all__'

    def get_is_locked(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_superuser:
            return False
        
        profile = getattr(request.user, 'profile', None)
        if profile:
            # Chapter is locked if its order is greater than unlocked_chapter
            return obj.order > profile.unlocked_chapter
        return True

    def to_representation(self, instance):
        """Handle reading is_completed based on profile status."""
        data = super().to_representation(instance)
        request = self.context.get('request')
        
        if request and request.user.is_authenticated:
            if request.user.is_superuser:
                data['is_completed'] = False
            else:
                profile = getattr(request.user, 'profile', None)
                if profile:
                    data['is_completed'] = instance.order < profile.unlocked_chapter
                else:
                    data['is_completed'] = False
        else:
            data['is_completed'] = False
            
        return data

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
        is_completed_data = validated_data.pop('is_completed', None)

        request = self.context.get('request')
        
        # Handle progress advancement if is_completed is set to True
        if is_completed_data is True and request and not request.user.is_superuser:
            profile = getattr(request.user, 'profile', None)
            if profile and instance.order >= profile.unlocked_chapter:
                # Advance unlocked_chapter only if completing the current or future chapter
                profile.unlocked_chapter = instance.order + 1
                profile.save()

        # Update Chapter fields (only if superuser or if fields are explicitly provided)
        # Students shouldn't be able to change these, but views.py will secondary-enforce this.
        instance.order = validated_data.get('order', instance.order)
        instance.title = validated_data.get('title', instance.title)
        instance.grammar_rule_malayalam = validated_data.get('grammar_rule_malayalam', instance.grammar_rule_malayalam)
        instance.xp_reward = validated_data.get('xp_reward', instance.xp_reward)
        instance.save()

        # Handle Examples
        keep_examples = []
        for example_data in examples_data:
            if 'id' in example_data:
                example_instance = GrammarExample.objects.get(id=example_data['id'], chapter=instance)
                for attr, value in example_data.items():
                    setattr(example_instance, attr, value)
                example_instance.save()
                keep_examples.append(example_instance.id)
            else:
                new_example = GrammarExample.objects.create(chapter=instance, **example_data)
                keep_examples.append(new_example.id)
        
        # Optional: Delete examples not in the request
        # instance.examples.exclude(id__in=keep_examples).delete()

        # Handle Quizzes
        keep_quizzes = []
        for quiz_data in quizzes_data:
            if 'id' in quiz_data:
                quiz_instance = GrammarQuiz.objects.get(id=quiz_data['id'], chapter=instance)
                for attr, value in quiz_data.items():
                    setattr(quiz_instance, attr, value)
                quiz_instance.save()
                keep_quizzes.append(quiz_instance.id)
            else:
                new_quiz = GrammarQuiz.objects.create(chapter=instance, **quiz_data)
                keep_quizzes.append(new_quiz.id)
        
        # Optional: Delete quizzes not in the request
        # instance.quizzes.exclude(id__in=keep_quizzes).delete()

        return instance
