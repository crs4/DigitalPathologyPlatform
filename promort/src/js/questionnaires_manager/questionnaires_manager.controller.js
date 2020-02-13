/*
 * Copyright (c) 2019, CRS4
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of
 * this software and associated documentation files (the "Software"), to deal in
 * the Software without restriction, including without limitation the rights to
 * use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
 * the Software, and to permit persons to whom the Software is furnished to do so,
 * subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
 * FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
 * COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
 * IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
 * CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */

(function () {
    'use strict';

    angular
        .module('promort.questionnaires_manager.controllers')
        .controller('QuestionnaireRequestsManagerController', QuestionnaireRequestsManagerController)
        .controller('QuestionnairePanelController', QuestionnairePanelController)
        .controller('QuestionsSetPanelController', QuestionsSetPanelController);

    QuestionnaireRequestsManagerController.$inject = ['$scope', '$routeParams', '$rootScope', '$log', '$location', '$route',
                                                      'QuestionnaireRequestService', 'SlidesSequenceViewerService',
                                                      'QuestionnaireAnswersService', 'WorkListService'];

    function QuestionnaireRequestsManagerController($scope, $routeParams, $rootScope, $log, $location, $route,
                                                    QuestionnaireRequestService, SlidesSequenceViewerService,
                                                    QuestionnaireAnswersService, WorkListService) {
        var vm = this;

        vm.panel_a_label = 'qm_panel_a';
        vm.panel_b_label = 'qm_panel_b';

        vm.request_label = undefined;
        vm.panel_a_questionnaire_label = undefined;
        vm.panel_b_questionnaire_label = undefined;
        vm.panel_a_last_completed_step = undefined;
        vm.panel_b_last_completed_step = undefined;
        vm.questionsPanelACtrl = undefined;
        vm.questionsPanelBCtrl = undefined;

        vm.getPanelAId = getPanelAId;
        vm.getPanelBId = getPanelBId;
        vm.getPanelALoadedTriggerLabel = getPanelALoadedTriggerLabel;
        vm.getPanelBLoadedTriggerLabel = getPanelBLoadedTriggerLabel;
        vm.isDualPanelQuestionnaire = isDualPanelQuestionnaire;
        vm.getPanelAQuestionnaireLabel = getPanelAQuestionnaireLabel;
        vm.getPanelAStepIndex = getPanelAStepIndex;
        vm.getPanelBQuestionnaireLabel = getPanelBQuestionnaireLabel;
        vm.getPanelBStepIndex = getPanelBStepIndex;
        vm.formValid = formValid;
        vm.submitAnswers = submitAnswers;

        activate();

        function activate() {
            vm.request_label = $routeParams.label;

            QuestionnaireRequestService.get(vm.request_label)
                .then(questionnaireRequestSuccessFn, questionnaireRequestErrorFn);

            function questionnaireRequestSuccessFn(response) {
                vm.panel_a_questionnaire_label = response.data.questionnaire_panel_a.label;
                vm.panel_a_last_completed_step = response.data.answers.questionnaire_panel_a.last_completed_step_index;
                if (response.data.questionnaire_panel_b !== null) {
                    vm.panel_b_questionnaire_label = response.data.questionnaire_panel_b.label;
                    vm.panel_b_last_completed_step = response.data.answers.questionnaire_panel_b.last_completed_step_index;
                }

                // initialize SlidesSequenceViewerService
                SlidesSequenceViewerService.initialize();

                // trigger data loaded events used by each panel to query for details
                $rootScope.$broadcast(
                    vm.getPanelALoadedTriggerLabel(),
                    {
                        'panel_id': vm.getPanelAId(),
                        'questionnaire_label': vm.getPanelAQuestionnaireLabel(),
                        'step_index': vm.getPanelAStepIndex()
                    }
                );
                if(vm.isDualPanelQuestionnaire()) {
                    $rootScope.$broadcast(
                        vm.getPanelBLoadedTriggerLabel(),
                        {
                            'panel_id': vm.getPanelBId(),
                            'questionnaire_label': vm.getPanelBQuestionnaireLabel(),
                            'step_index': vm.getPanelBStepIndex()
                        }
                    );
                }

                // register questions panel as soon as they are ready, this will enable form validation
                $scope.$on('questions_panel.' + vm.getPanelAId() + '.ready',
                    function(event, args) {
                        console.log('Registering questions panel A controller');
                        vm.questionsPanelACtrl = args.panelCtrl;
                    }
                );
                if(vm.isDualPanelQuestionnaire()) {
                    $scope.$on('questions_panel.' + vm.getPanelBId() + '.ready',
                        function(event, args) {
                            console.log('Registering questions panel B controller');
                            vm.questionsPanelBCtrl = args.panelCtrl;
                        }
                    );
                }
            }

            function questionnaireRequestErrorFn(response) {
                $log.error(response.error);
            }
        }

        function getPanelAId() {
            return vm.panel_a_label;
        }

        function getPanelBId() {
            return vm.panel_b_label;
        }

        function getPanelALoadedTriggerLabel() {
            return vm.panel_a_label + '.data.ready';
        }

        function getPanelBLoadedTriggerLabel() {
            return vm.panel_b_label + '.data.ready';
        }

        function isDualPanelQuestionnaire() {
            return vm.panel_b_questionnaire_label !== undefined;
        }

        function getPanelAQuestionnaireLabel() {
            return vm.panel_a_questionnaire_label;
        }

        function getPanelAStepIndex() {
            return vm.panel_a_last_completed_step + 1;
        }

        function getPanelBQuestionnaireLabel() {
            if(vm.isDualPanelQuestionnaire()) {
                return vm.panel_b_questionnaire_label;
            } else {
                return undefined;
            }
        }

        function getPanelBStepIndex() {
            if(vm.isDualPanelQuestionnaire()) {
                return vm.panel_b_last_completed_step + 1;
            } else {
                return undefined;
            }
        }

        function formValid() {
            if(vm.isDualPanelQuestionnaire()) {
                if(typeof vm.questionsPanelACtrl === 'undefined' || typeof vm.questionsPanelBCtrl === 'undefined') {
                    return false;
                } else {
                    return (vm.questionsPanelACtrl.formValid() && vm.questionsPanelBCtrl.formValid());
                }
            } else {
                if(typeof vm.questionsPanelACtrl === 'undefined') {
                    return false;
                } else {
                    return vm.questionsPanelACtrl.formValid();
                }
            }
        }

        function submitAnswers() {
            if(vm.isDualPanelQuestionnaire()) {
                var panel_a_details = {
                    questionnaire_step_index: vm.getPanelAStepIndex(),
                    answers_json: vm.questionsPanelACtrl.getAnswers()
                };
                var panel_b_details = {
                    questionnaire_step_index: vm.getPanelBStepIndex(),
                    answers_json: vm.questionsPanelBCtrl.getAnswers()
                };
                console.log({panel_a: panel_a_details, panel_b: panel_b_details});
                QuestionnaireAnswersService.saveRequestAnswers(vm.request_label, panel_a_details, panel_b_details)
                    .then(saveRequestAnswersSuccessFn, saveRequestAnswersErrorFn);

                function saveRequestAnswersSuccessFn(response) {
                    console.log('Answers saved');
                    console.log(response.data);
                    console.log('check request status');
                    QuestionnaireRequestService.get_status(vm.request_label)
                        .then(getStatusSuccessFn, getStatusErrorFn);

                    function getStatusSuccessFn(response) {
                        if(response.data.can_be_closed === true) {
                            console.log('Close questionnaire request');
                            WorkListService.closeQuestionnaireRequest(vm.request_label)
                                .then(closeQuestionnaireRequestSuccessFn, closeQuestionnaireRequestErrorFn);

                            function closeQuestionnaireRequestSuccessFn(response) {
                                console.log('Return to worklist page');
                                $location.url('worklist');
                            }

                            function closeQuestionnaireRequestErrorFn(response) {
                                $log.error(response.error);
                            }
                        } else {
                            console.log('Reload page and continue questionnaire');
                            $route.reload();
                        }
                    }

                    function getStatusErrorFn(response) {
                        $log.error(response.error);
                    }
                }

                function saveRequestAnswersErrorFn(response) {
                    $log.error(response.error);
                }
            } else {
                console.log('Single panel mode');
            }
        }
    }

    QuestionnairePanelController.$inject = ['$scope', '$routeParams', '$rootScope', '$log',
                                            'QuestionnaireStepService'];

    function QuestionnairePanelController($scope, $routeParams, $rootScope, $log, QuestionnaireStepService) {
        var vm = this;

        vm.panel_id = undefined;
        vm.questionnaire_label = undefined;
        vm.step_index = undefined;
        vm.slides_set_a_id = undefined;
        vm.slides_set_a_label = undefined;
        vm.slides_set_b_id = undefined;
        vm.slides_set_b_label = undefined;
        vm.questions_set_id = undefined;

        vm.getPanelId = getPanelId;
        vm.getSlidesSetADetails = getSlidesSetADetails;
        vm.getSlidesSetBDetails = getSlidesSetBDetails;
        vm.getQuestionsSetId = getQuestionsSetId;
        vm.getQuestionsLoadedTriggerLabel = getQuestionsLoadedTriggerLabel;
        vm.getQuestionsPanelIdentifier = getQuestionsPanelIdentifier;
        vm.getQuestionsDetails = getQuestionsDetails;
        vm.getSlidesSetPanelIdentifier = getSlidesSetPanelIdentifier;
        vm.getSlidesSetLoadedTriggerLabel = getSlidesSetLoadedTriggerLabel;
        vm.getViewerReadyTrigger = getViewerReadyTrigger;

        activate();

        function activate() {
            vm.panel_id = $scope.qpIdentifier;

            $scope.$on(
                $scope.qpWaitForIt,
                function(event, args) {
                    vm.questionnaire_label = args.questionnaire_label;
                    vm.step_index = args.step_index;

                    QuestionnaireStepService.get(vm.questionnaire_label, vm.step_index)
                        .then(questionnaireStepSuccessFn, questionnaireStepErrorFn);

                    function questionnaireStepSuccessFn(response) {
                        vm.slides_set_a_id = response.data.slides_set_a.id;
                        vm.slides_set_a_label = response.data.slides_set_a_label;

                        // trigger data loaded events for slides set panels and questions panel
                        $rootScope.$broadcast(
                            vm.getQuestionsLoadedTriggerLabel(),
                            vm.getQuestionsDetails(response.data.questions)
                        );
                        $rootScope.$broadcast(
                            vm.getSlidesSetLoadedTriggerLabel('set_a'),
                            vm.getSlidesSetADetails()
                        );
                        // TODO: handle set_b slides
                    }

                    function questionnaireStepErrorFn(response) {
                        $log.error(response.error);
                    }
                }
            )
        }

        function getPanelId() {
            return vm.panel_id;
        }

        function getSlidesSetADetails() {
            return {
                'slides_set_id': vm.slides_set_a_id,
                'slides_set_label': vm.slides_set_a_label
            }
        }

        function getSlidesSetBDetails() {
            return {
                'slides_set_id': vm.slides_set_b_id,
                'slides_set_label': vm.slides_set_b_label
            }
        }

        function getQuestionsSetId() {
            return vm.questions_set_id;
        }

        function getQuestionsLoadedTriggerLabel() {
            return vm.getPanelId() +  '.questions.ready';
        }

        function getQuestionsPanelIdentifier() {
            return vm.getPanelId();
        }

        function getQuestionsDetails(questions) {
            console.log(questions);
            return {
                'questions': $.parseJSON(questions.questions_json)
            }
        }

        function getSlidesSetPanelIdentifier(slides_set) {
            return vm.getPanelId() + '-' + slides_set;
        }

        function getSlidesSetLoadedTriggerLabel(slides_set) {
            return vm.getPanelId() + '.slides_' + slides_set + '.ready';
        }

        function getViewerReadyTrigger(slides_set) {
            return vm.getPanelId() + '.viewer_' + slides_set + '.ready';
        }
    }

    QuestionsSetPanelController.$inject = ['$scope', '$routeParams', '$rootScope', '$log'];

    function QuestionsSetPanelController($scope, $routeParams, $rootScope, $log) {
        var vm = this;

        vm.panel_id = undefined;
        vm.questions = undefined;
        vm.answers = undefined;
        vm.getPanelID = getPanelID;
        vm.getRadioGroupName = getRadioGroupName;
        vm.getAnswers = getAnswers;
        vm.formValid = formValid;

        activate();

        function activate() {
            vm.panel_id = $scope.qspIdentifier;

            $scope.$on(
                $scope.qspWaitForIt,
                function(event, args) {
                    console.log('Questions loaded!');
                    vm.questions = args.questions;

                    vm.answers = {};
                    for(var i=0; i<vm.questions.length; i++) {
                        if(vm.questions[i].type === "range") {
                            vm.answers[vm.questions[i].label] = vm.questions[i].default;
                        } else {
                            vm.answers[vm.questions[i].label] = undefined;
                        }
                    }

                    $rootScope.$broadcast(
                        'questions_panel.' + vm.getPanelID() + '.ready',
                        {'panelCtrl': vm}
                    );
                }
            )
        }

        function getPanelID() {
            return vm.panel_id;
        }

        function getRadioGroupName(question_label) {
            return vm.getPanelID() + '-' + question_label;
        }

        function getAnswers() {
            return JSON.stringify(vm.answers);
        }

        function formValid() {
            if(typeof vm.answers === 'undefined') {
                return false;
            } else {
                var form_valid = true;
                for(var a in vm.answers) {
                    if(typeof vm.answers[a] === 'undefined') {
                        form_valid = false;
                        break;
                    }
                }
                return form_valid;
            }
        }

    }
})();