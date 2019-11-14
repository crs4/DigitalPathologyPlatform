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

from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import MethodNotAllowed, NotFound

from view_templates.views import GenericListView, GenericReadOnlyDetailView, GenericDetailView

from questionnaires_manager.models import QuestionsSet, Questionnaire, QuestionnaireStep, \
    QuestionnaireRequest, QuestionnaireAnswers, QuestionnaireStepAnswers
from questionnaires_manager.serializers import QuestionsSetSerializer, QuestionnaireSerializer,\
    QuestionnaireStepSerializer, QuestionnaireRequestSerializer, QuestionnaireAnswersSerializer,\
    QuestionnaireStepAnswersSerializer, QuestionnaireDetailsSerializer, QuestionnaireStepDetailsSerializer, \
    QuestionnaireRequestDetailsSerializer, QuestionnaireAnswersDetailsSerializer

import logging
logger = logging.getLogger('promort')


class QuestionsSetList(GenericListView):
    model = QuestionsSet
    model_serializer = QuestionsSetSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, requestion, format=None):
        raise MethodNotAllowed


class QuestionsSetDetail(GenericReadOnlyDetailView):
    model = QuestionsSet
    model_serializer = QuestionsSetSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, pk):
        logger.debug('Loading QuestionsSetDetail with label %r', pk)
        try:
            return self.model.objects.get(label__iexact=pk)
        except self.model.DoesNotExist:
            logger.debug('Object not found!')
            raise NotFound('There is no QuestionsSetDetail with label %s' % pk)


class QuestionnaireList(GenericListView):
    model = Questionnaire
    model_serializer = QuestionnaireSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, requestion, format=None):
        raise MethodNotAllowed


class QuestionnaireDetail(GenericReadOnlyDetailView):
    model = Questionnaire
    model_serializer = QuestionnaireDetailsSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, pk):
        logger.debug('Loading Questionnaire with label %s', pk)
        try:
            return self.model.objects.get(label__iexact=pk)
        except self.model.DoesNotExist:
            logger.debug('Object not found!')
            raise NotFound('There is no Questionnaire with label %s' % pk)


class QuestionnaireStepDetail(APIView):
    model_serializer = QuestionnaireStepDetailsSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, quest_pk, step_pk):
        logger.debug('Loading QuestionnaireStep object with ID %s for Questionnaire %s' % (step_pk, quest_pk))
        try:
            quest_obj = Questionnaire.objects.get(label__iexact=quest_pk)
            return quest_obj.steps.get(id=step_pk)
        except Questionnaire.DoesNotExist:
            logger.debug('Questionnaire object not found!')
            raise NotFound('There is no Questionnare with label %s' % quest_pk)
        except QuestionnaireStep.DoesNotExist:
            logger.debug('QuestionnareStep object not found!')
            raise NotFound('There is no QuestionnaireStep with ID %s for Questionnaire %s' % (step_pk, quest_pk))

    def get(self, request, quest_pk, step_pk, format=None):
        questionnaire_step = self.get_object(quest_pk, step_pk)
        serializer = self.model_serializer(questionnaire_step)
        return Response(serializer.data, status=status.HTTP_200_OK)
