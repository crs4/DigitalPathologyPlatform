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

from datetime import datetime

from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import MethodNotAllowed, NotFound

from django.db import IntegrityError

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


class QuestionnaireRequestDetail(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def _find_questionnaire_request(self, label):
        try:
            return QuestionnaireRequest.objects.get(label=label)
        except QuestionnaireRequest.DoesNotExist:
            raise NotFound('No Questionnaire Request with label \'%s\'', label)

    def get(self, request, label, format=None):
        questionnaire_request = self._find_questionnaire_request(label)
        serializer = QuestionnaireRequestDetailsSerializer(questionnaire_request)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, label, format=None):
        questionnaire_request = self._find_questionnaire_request(label)
        action = request.data.get('action')
        if action is not None:
            action = action.upper()
            if action == 'START':
                if not questionnaire_request.is_started():
                    questionnaire_request.start_date = datetime.now()
                else:
                    return Response({
                        'status': 'ERROR',
                        'message': 'Questionnaire request can\'t be started'
                    }, status=status.HTTP_409_CONFLICT)
            if action == 'FINISH':
                if questionnaire_request.can_be_closed() and not questionnaire_request.is_completed():
                    questionnaire_request.completion_date = datetime.now()
                else:
                    return Response({
                        'status': 'ERROR',
                        'message': 'Questionnaire request can\'t be closed'
                    }, status=status.HTTP_409_CONFLICT)
            else:
                return Response({
                    'status': 'ERROR',
                    'message': '\'%s\' is not a valid action' % action
                }, status=status.HTTP_400_BAD_REQUEST)
            questionnaire_request.save()
            serializer = QuestionnaireRequestSerializer(questionnaire_request)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'ERROR',
                'message': 'Missing \'action\' field in request data'
            }, status=status.HTTP_400_BAD_REQUEST)


class QuestionnaireRequestPanelDetail(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def _find_questionnaire_request_panel(self, label, panel):
        try:
            q_req = QuestionnaireRequest.objects.get(label=label)
            if panel == 'panel_a':
                return q_req.questionnaire_panel_a
            elif panel == 'panel_b':
                return q_req.questionnaire_panel_b
        except QuestionnaireRequest.DoesNotExist:
            raise NotFound('No Questionnaire Request with label \'%s\'', label)

    def get(self, request, label, panel, format=None):
        request_panel = self._find_questionnaire_request_panel(label, panel)
        if request_panel:
            serializer = QuestionnaireDetailsSerializer(request_panel)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)


class QuestionnairePanelAnswersDetail(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def _get_request_panel_answers(self, label, panel):
        try:
            q_req = QuestionnaireRequest.objects.get(label=label)
            if panel == 'panel_a':
                q_req_panel = q_req.questionnaire_panel_a
            elif panel == 'panel_b':
                q_req_panel = q_req.questionnaire_panel_b
            if q_req_panel is None:
                raise NotFound('Questionnaire Request %s has no panel \'%s\'' % (label, panel))
            else:
                try:
                    return QuestionnaireAnswers.objects.get(questionnaire_request=q_req, questionnaire=q_req_panel)
                except QuestionnaireAnswers.DoesNotExist:
                    raise NotFound('No Questionnaires Answers for Request \'%s\' panel \'%s\'' % (label, panel))
        except QuestionnaireRequest.DoesNotExist:
            raise NotFound('No Questionnaire Request with label \'%s\'' % label)

    def get(self, request, label, panel, format=None):
        panel_answers = self._get_request_panel_answers(label, panel)
        serializer = QuestionnaireAnswersDetailsSerializer(panel_answers)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, label, panel, format=None):
        panel_answers = self._get_request_panel_answers(label, panel)
        step_answers = request.data
        step_answers['questionnaire_answers'] = panel_answers.id
        q_step = panel_answers.get_questionnaire_step(step_answers['questionnaire_step'])
        if q_step:
            step_answers['questionnaire_step'] = q_step.id

            serializer = QuestionnaireStepAnswersSerializer(step_answers)
            if serializer.is_valid():
                try:
                    serializer.save()
                except IntegrityError:
                    return Response({
                        'status': 'ERROR',
                        'message': 'duplicated answers for step %s of Questionnaire answers %s' %
                                   (step_answers['questionnaire_step'], step_answers['questionnaire_answers'])
                    })
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'status': 'ERROR',
                'message': 'No step with ID %s found for questionnaire, can\'t save' %
                           step_answers['questionnaire_answers']
            }, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, label, panel, format=None):
        panel_answer = self._get_request_panel_answers(label, panel)
        action = request.data.get('action')
        if action is not None:
            action = action.upper()
            if action == 'FINISH':
                if panel_answer.can_be_closed() and not panel_answer.is_completed():
                    panel_answer.completion_date = datetime.now()
                else:
                    return Response({
                        'status': 'ERROR',
                        'message': 'Questionnaire answers can\'t\' be closed'
                    })
            panel_answer.save()
            serializer = QuestionnaireAnswersSerializer(panel_answer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'ERROR',
                'message': 'Missing \'action\' field in request data'
            }, status=status.HTTP_400_BAD_REQUEST)
