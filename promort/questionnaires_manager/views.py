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
from questionnaires_manager.serializers import QuestionsSetSerializer, QuestionnaireSerializer, \
    QuestionnaireStepSerializer, QuestionnaireRequestSerializer, QuestionnaireRequestStatusSerializer, \
    QuestionnaireAnswersSerializer, QuestionnaireStepAnswersSerializer, QuestionnaireDetailsSerializer, \
    QuestionnaireStepDetailsSerializer, QuestionnaireRequestDetailsSerializer, QuestionnaireAnswersDetailsSerializer

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

    def get_object(self, quest_pk, step_index):
        logger.debug('Loading QuestionnaireStep object with index %s for Questionnaire %s' % (step_index, quest_pk))
        try:
            quest_obj = Questionnaire.objects.get(label__iexact=quest_pk)
            return quest_obj.steps.get(step_index=step_index)
        except Questionnaire.DoesNotExist:
            logger.debug('Questionnaire object not found!')
            raise NotFound('There is no Questionnare with label %s' % quest_pk)
        except QuestionnaireStep.DoesNotExist:
            logger.debug('QuestionnareStep object not found!')
            raise NotFound('There is no QuestionnaireStep with index %s for Questionnaire %s' % (step_index, quest_pk))

    def get(self, request, quest_pk, step_index, format=None):
        questionnaire_step = self.get_object(quest_pk, step_index)
        serializer = self.model_serializer(questionnaire_step)
        return Response(serializer.data, status=status.HTTP_200_OK)


class QuestionnaireRequestDetail(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def _find_questionnaire_request(self, label):
        try:
            return QuestionnaireRequest.objects.get(label=label)
        except QuestionnaireRequest.DoesNotExist:
            raise NotFound('No Questionnaire Request with label \'%s\'' % label)

    def _create_questionnaire_answers_obj(self, questionnaire_request, questionnaire, reviewer):
        return QuestionnaireAnswers(
            questionnaire_request=questionnaire_request,
            questionnaire=questionnaire,
            reviewer=reviewer
        )

    def _initialize_questionnaire_answers(self, questionnaire_request):
        try:
            q_answers_a = self._create_questionnaire_answers_obj(questionnaire_request,
                                                                 questionnaire_request.questionnaire_panel_a,
                                                                 questionnaire_request.reviewer)
            q_answers_a.save()
        except IntegrityError, ie:
            raise ie
        if questionnaire_request.questionnaire_panel_b is not None:
            q_answers_b = self._create_questionnaire_answers_obj(questionnaire_request,
                                                                 questionnaire_request.questionnaire_panel_b,
                                                                 questionnaire_request.reviewer)
            try:
                q_answers_b.save()
            except IntegrityError, ie:
                q_answers_a.delete()
                raise ie

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
                    try:
                        self._initialize_questionnaire_answers(questionnaire_request)
                    except IntegrityError:
                        return Response({
                            'status': 'ERROR',
                            'message': 'Integrity error while initializing QuestionnaireAnswers objects'
                        }, status=status.HTTP_409_CONFLICT)
                    questionnaire_request.start_date = datetime.now()
                else:
                    return Response({
                        'status': 'ERROR',
                        'message': 'Questionnaire request can\'t be started'
                    }, status=status.HTTP_409_CONFLICT)
            elif action == 'FINISH':
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


class QuestionnaireRequestStatus(APIView):
    permissions_classes = (permissions.IsAuthenticated,)

    def _find_questionnaire_request(self, label):
        try:
            return QuestionnaireRequest.objects.get(label=label)
        except QuestionnaireRequest.DoesNotExist:
            raise NotFound('No Questionnaire Request with label \'%s\'' % label)

    def get(self, request, label, format=None):
        questionnaire_request = self._find_questionnaire_request(label)
        serializer = QuestionnaireRequestStatusSerializer(questionnaire_request)
        return Response(serializer.data, status=status.HTTP_200_OK)


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


class QuestionnaireStepAnswersBaseView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def _get_request_panel_answers(self, label, panel):
        try:
            q_req = QuestionnaireRequest.objects.get(label=label)
            if panel == 'panel_a':
                q_req_panel = q_req.questionnaire_panel_a
            elif panel == 'panel_b':
                q_req_panel = q_req.questionnaire_panel_b
            else:
                q_req_panel = None
            if q_req_panel is None:
                raise NotFound('Questionnaire Request %s has no panel \'%s\'' % (label, panel))
            else:
                try:
                    return QuestionnaireAnswers.objects.get(questionnaire_request=q_req, questionnaire=q_req_panel)
                except QuestionnaireAnswers.DoesNotExist:
                    raise NotFound('No Questionnaires Answers for Request \'%s\' panel \'%s\'' % (label, panel))
        except QuestionnaireRequest.DoesNotExist:
            raise NotFound('No Questionnaire Request with label \'%s\'' % label)

    def _save_panel_answers(self, request_label, request_panel, questionnaire_step_index, answers_json):
        q_panel_answers = self._get_request_panel_answers(request_label, request_panel)
        q_step = q_panel_answers.get_questionnaire_step(questionnaire_step_index)
        if q_step:
            serializer = QuestionnaireStepAnswersSerializer(data={
                'questionnaire_answers': q_panel_answers.id,
                'questionnaire_step': q_step.id,
                'answers_json': answers_json
            })
            if serializer.is_valid():
                serializer.save()
                return serializer.data
        else:
            raise NotFound('No step with index %d found for questionnaire %s, can\'t save' %
                           (questionnaire_step_index, q_panel_answers.questionnaire.label))


class QuestionnaireRequestAnswers(QuestionnaireStepAnswersBaseView):

    def _delete_questionnaire_step_answer(self, questionnaire_answers_id, questionnaire_step):
        qsa_obj = QuestionnaireStepAnswers.objects.filter(
            questionnaire_answers__pk=questionnaire_answers_id,
            questionnaire_step=questionnaire_step
        )
        qsa_obj.delete()

    def _update_questionnaire_answers(self, panel_a_answers_id, panel_b_answers_id):
        pa_answers = QuestionnaireAnswers.objects.get(pk=panel_a_answers_id)
        if panel_b_answers_id is not None:
            pb_answers = QuestionnaireAnswers.objects.get(pk=panel_b_answers_id)
            if pa_answers.can_be_closed() and pb_answers.can_be_closed():
                completion_date = datetime.now()
                pa_answers.completion_date = completion_date
                pa_answers.save()
                pb_answers.completion_date = completion_date
                pb_answers.save()
            else:
                #TODO properly handle if one of the two steps can be closed and the other one not
                pass
        else:
            if pa_answers.can_be_closed():
                pa_answers.completion_date = datetime.now()
                pa_answers.save()

    def post(self, request, label, format=None):
        panel_a_answers = request.data['panel_a']
        qpa_step_index = panel_a_answers['questionnaire_step_index']
        try:
            # save panel a answers
            pa_response_data = self._save_panel_answers(label, 'panel_a', qpa_step_index,
                                                        panel_a_answers['answers_json'])
        except IntegrityError:
            return Response({
                'status': 'ERROR',
                'message': 'Duplicated answers for step %d, questionnaire request %s - panel %s' %
                           (qpa_step_index, label, 'panel_a')
            })
        panel_b_answers = request.data.get('panel_b')
        if panel_b_answers is not None:
            qpb_step_index = panel_b_answers['questionnaire_step_index']
            try:
                pb_response_data = self._save_panel_answers(label, 'panel_b', qpb_step_index,
                                                            panel_b_answers['answers_json'])
            except IntegrityError:
                # remove panel a answer
                self._delete_questionnaire_step_answer(pa_response_data['questionnaire_answers'],
                                                       qpa_step_index)
                return Response({
                    'status': 'ERROR',
                    'message': 'Duplicated answers for step %d, questionnaire request %s - panel %s' %
                               (qpb_step_index, label, 'panel_b')
                })
        else:
            pb_response_data = None
        self._update_questionnaire_answers(
            pa_response_data['questionnaire_answers'], pb_response_data.get('questionnaire_answers')
        )
        return Response({'panel_a': pa_response_data, 'panel_b': pb_response_data},
                        status=status.HTTP_201_CREATED)


class QuestionnairePanelAnswersDetail(QuestionnaireStepAnswersBaseView):

    def get(self, request, label, panel, format=None):
        panel_answers = self._get_request_panel_answers(label, panel)
        serializer = QuestionnaireAnswersDetailsSerializer(panel_answers)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, label, panel, format=None):
        questionnaire_step_index = int(request.data['questionnaire_step_index'])
        try:
            response_data = self._save_panel_answers(label, panel, questionnaire_step_index,
                                                     request.data['answers_json'])
            return Response(response_data, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response({
                'status': 'ERROR',
                'message': 'Duplicated answers for step %d, questionnaire request %s - panel %s' %
                           (questionnaire_step_index, label, panel)
            })

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
