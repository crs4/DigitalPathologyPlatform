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
        .controller('QuestionnairePanelController', QuestionnairePanelController);

    QuestionnaireRequestsManagerController.$inject = ['$scope', '$routeParams', '$rootScope', '$log',
                                                      'QuestionnaireRequestService'];

    function QuestionnaireRequestsManagerController($scope, $routeParams, $rootScope, $log,
                                                   QuestionnaireRequestService) {
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
            console.log('Request label is ' + vm.request_label);

            QuestionnaireRequestService.get(vm.request_label)
                .then(questionnaireRequestSuccessFn, questionnaireRequestErrorFn);

            function questionnaireRequestSuccessFn(response) {
                vm.panel_a_questionnaire_label = response.data.questionnaire_panel_a.label;
                vm.panel_a_last_completed_step = response.data.answers.questionnaire_panel_a.last_completed_step_index;
                $rootScope.$broadcast('questionnaire_panel_a.data.ready');
                if (response.data.questionnaire_panel_b !== null) {
                    vm.panel_b_questionnaire_label = response.data.questionnaire_panel_b.label;
                    vm.panel_b_last_completed_step = response.data.answers.questionnaire_panel_b.last_completed_step_index;
                }

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

        vm.getPanelId = getPanelId;

        activate();

        function activate() {
            console.log('Wait for trigger: ' + $scope.loadedDataTrigger);

            $rootScope.$on(
                $scope.loadedDataTrigger,
                function(event, args) {
                    console.log('Hello, I am panel ' + args.panel_id);
                    console.log('Questionnaire Label is: ' + args.questionnaire_label);
                    console.log('Step ID is: ' + args.step_index);
                    vm.panel_id = args.panel_id;
                    vm.questionnaire_label = args.questionnaire_label;
                    vm.step_index = args.step_index;

                    QuestionnaireStepService.get(vm.questionnaire_label, vm.step_index)
                        .then(questionnaireStepSuccessFn, questionnaireStepErrorFn);

                    function questionnaireStepSuccessFn(response) {
                        console.log('DETAILS FOR PANEL: ' + vm.panel_id);
                        console.log(response);
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
    }
})();