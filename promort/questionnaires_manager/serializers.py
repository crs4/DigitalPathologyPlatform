#  Copyright (c) 2019, CRS4
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of
#  this software and associated documentation files (the "Software"), to deal in
#  the Software without restriction, including without limitation the rights to
#  use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
#  the Software, and to permit persons to whom the Software is furnished to do so,
#  subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
#  FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
#  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
#  IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
#  CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

try:
    import simplejson as json
except ImportError:
    import json

from django.contrib.auth.models import User

from rest_framework import serializers

from questionnaires_manager.models import QuestionsSet, Questionnaire, QuestionnaireStep,\
    QuestionnaireRequest, QuestionnaireAnswers, QuestionnaireStepAnswers
from slides_manager.serializers import SlidesSetSerializer


class QuestionsSetSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )

    class Meta:
        model = QuestionsSet

        fields = ('id', 'label', 'creation_date', 'questions_json', 'author')
        read_only_fields = ('id',)

    def validate_questions_json(self, value):
        try:
            json.loads(value)
            return value
        except ValueError:
            raise serializers.ValidationError('Not a valid JSON in \'questions_json\' field')


class QuestionnaireSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )

    class Meta:
        model = Questionnaire

        fields = ('id', 'label', 'creation_date', 'author', 'steps_count')
        read_only_fields = ('id', 'steps_count')


class QuestionnaireStepSerializer(serializers.ModelSerializer):

    class Meta:
        model = QuestionnaireStep

        fields = ('id', 'questions', 'slides_set_a', 'slides_set_a_label', 'slides_set_b', 'slides_set_b_label',
                  'questionnaire', 'answers', 'step_index', 'creation_date')
        read_only_fields = ('id', 'answers')


class QuestionnaireRequestSerializer(serializers.ModelSerializer):
    reviewer = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )
    annotation_type = serializers.SerializerMethodField()
    started = serializers.SerializerMethodField()
    completed = serializers.SerializerMethodField()

    class Meta:
        model = QuestionnaireRequest

        fields = ('id', 'label', 'annotation_type', 'questionnaire_panel_a', 'questionnaire_panel_b', 'reviewer',
                  'creation_date', 'start_date', 'completion_date', 'answers', 'started', 'completed')
        read_only_fields = ('id', 'answers', 'annotation_type')

    @staticmethod
    def get_annotation_type(obj):
        return 'QUESTIONNAIRE'

    @staticmethod
    def get_started(obj):
        return obj.is_started()

    @staticmethod
    def get_completed(obj):
        return obj.is_completed()


class QuestionnaireAnswersSerializer(serializers.ModelSerializer):
    reviewer = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )
    last_completed_step_index = serializers.SerializerMethodField()

    class Meta:
        model = QuestionnaireAnswers

        fields = ('id', 'questionnaire_request', 'questionnaire', 'reviewer', 'creation_date',
                  'completion_date', 'steps', 'steps_count', 'completed_steps_count',
                  'last_completed_step_index')
        read_only_fields = ('id', 'creation_date', 'steps', 'steps_count', 'completed_steps_count',
                            'last_completed_step_index')

    @staticmethod
    def get_last_completed_step_index(obj):
        return obj.get_last_completed_step_index()


class QuestionnaireStepAnswersSerializer(serializers.ModelSerializer):

    class Meta:
        model = QuestionnaireStepAnswers

        fields = ('id', 'questionnaire_answers', 'questionnaire_step', 'answers_json', 'creation_date',
                  'step_index')
        read_only_fields = ('id', 'step_index')

    def validate_answers_json(self, value):
        try:
            json.loads(value)
            return value
        except ValueError:
            raise serializers.ValidationError('Not a valid JSON in \'answers_json\' field')


class QuestionnaireDetailsSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )
    steps = QuestionnaireStepSerializer(many=True, read_only=True)

    class Meta:
        model = Questionnaire

        fields = ('id', 'label', 'creation_date', 'author', 'steps')
        read_only_fields = ('id', 'steps')


class QuestionnaireStepDetailsSerializer(QuestionnaireStepSerializer):
    questions = QuestionsSetSerializer(read_only=True)
    slides_set_a = SlidesSetSerializer(read_only=True, allow_null=True)
    slides_set_b = SlidesSetSerializer(read_only=True, allow_null=True)
    questionnaire = QuestionnaireSerializer(read_only=True)
    answers = QuestionnaireStepAnswersSerializer(many=True, read_only=True)


class QuestionnaireRequestDetailsSerializer(QuestionnaireRequestSerializer):
    questionnaire_panel_a = QuestionnaireSerializer(read_only=True)
    questionnaire_panel_b = QuestionnaireSerializer(read_only=True)
    answers = serializers.SerializerMethodField()

    @staticmethod
    def get_answers(obj):
        answers = dict()
        try:
            answers['questionnaire_panel_a'] = QuestionnaireAnswersSerializer(
                QuestionnaireAnswers.objects.get(questionnaire_request=obj, questionnaire=obj.questionnaire_panel_a)
            ).data
        except QuestionnaireAnswers.DoesNotExist:
            answers['questionnaire_panel_a'] = None
        if obj.questionnaire_panel_b:
            try:
                answers['questionnaire_panel_b'] = QuestionnaireAnswersSerializer(
                    QuestionnaireAnswers.objects.get(questionnaire_request=obj, questionnaire=obj.questionnaire_panel_b)
                ).data
            except QuestionnaireAnswers.DoesNotExist:
                answers['questionnaire_panel_b'] = None
        else:
            answers['questionnaire_panel_b'] = None
        return answers


class QuestionnaireAnswersDetailsSerializer(QuestionnaireAnswersSerializer):
    steps = QuestionnaireStepAnswersSerializer(many=True, read_only=True)
