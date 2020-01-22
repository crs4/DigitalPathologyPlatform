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

    QuestionnaireRequestsManagerController.$inject = ['$scope', '$routeParams', '$rootScope', '$log',
                                                      'QuestionnaireRequestService', 'SlidesSequenceViewerService'];

    function QuestionnaireRequestsManagerController($scope, $routeParams, $rootScope, $log,
                                                   QuestionnaireRequestService, SlidesSequenceViewerService) {
        var vm = this;

        vm.panel_a_label = 'qm_panel_a';
        vm.panel_b_label = 'qm_panel_b';

        vm.request_label = undefined;
        vm.panel_a_questionnaire_label = undefined;
        vm.panel_b_questionnaire_label = undefined;
        vm.panel_a_last_completed_step = undefined;
        vm.panel_b_last_completed_step = undefined;

        vm.getPanelAId = getPanelAId;
        vm.getPanelBId = getPanelBId;
        vm.getPanelALoadedTriggerLabel = getPanelALoadedTriggerLabel;
        vm.getPanelBLoadedTriggerLabel = getPanelBLoadedTriggerLabel;
        vm.isDualPanelQuestionnaire = isDualPanelQuestionnaire;
        vm.getPanelAQuestionnaireLabel = getPanelAQuestionnaireLabel;
        vm.getPanelANextStep = getPanelANextStep;
        vm.getPanelBQuestionnaireLabel = getPanelBQuestionnaireLabel;
        vm.getPanelBNextStep = getPanelBNextStep;

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
                        'step_index': vm.getPanelANextStep()
                    }
                );
                if(vm.isDualPanelQuestionnaire()) {
                    $rootScope.$broadcast(
                        vm.getPanelBLoadedTriggerLabel(),
                        {
                            'panel_id': vm.getPanelBId(),
                            'questionnaire_label': vm.getPanelBQuestionnaireLabel(),
                            'step_index': vm.getPanelBNextStep()
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

        function getPanelANextStep() {
            return vm.panel_a_last_completed_step + 1;
        }

        function getPanelBQuestionnaireLabel() {
            if(vm.isDualPanelQuestionnaire()) {
                return vm.panel_b_questionnaire_label;
            } else {
                return undefined;
            }
        }

        function getPanelBNextStep() {
            if(vm.isDualPanelQuestionnaire()) {
                return vm.panel_b_last_completed_step + 1;
            } else {
                return undefined;
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
                            vm.getQuestionsLoadedTriggerLabel()
                        );
                        $rootScope.$broadcast(
                            vm.getSlidesSetLoadedTriggerLabel('set_a'),
                            vm.getSlidesSetADetails()
                        );
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

        activate();

        function activate() {
            $scope.$on(
                $scope.qspWaitForIt,
                function(event, arg) {
                    console.log('Questions loaded!');
                }
            )
        }

    }
})();