(function () {
    'use strict';

    angular
        .module('promort.clinical_annotations_manager.controllers')
        .controller('ClinicalAnnotationsManagerController', ClinicalAnnotationsManagerController);

    ClinicalAnnotationsManagerController.$inject = ['$scope', '$routeParams', '$compile', '$location',
        'ngDialog', 'Authentication', 'AnnotationsViewerService', 'ClinicalAnnotationStepService'];

    function ClinicalAnnotationsManagerController($scope, $routeParams, $compile, $location, ngDialog, Authentication,
                                                  AnnotationsViewerService, ClinicalannotationStepService) {
        var vm = this;
        vm.slide_id = undefined;
        vm.case_id = undefined;
        vm.rois_annotation_step_id = undefined;
        vm.clinical_annotation_step_id = undefined;

        vm.ui_active_mode = {
            'annotate_slice': false,
            'annotate_core': false,
            'annotate_focus_region': false,
            'show_slice': false,
            'show_core': false,
            'show_focus_region': false
        };
        vm.roisTreeLocked = false;

        activate();

        function activate() {
            vm.slide_id = $routeParams.slide;
            vm.case_id = $routeParams.case;
            vm.rois_annotation_step_id = $routeParams.annotation_step;
            vm.clinical_annotation_step_id = $routeParams.clinical_annotation_step;

            ClinicalannotationStepService.getDetails(vm.case_id, Authentication.getCurrentUser(),
                vm.rois_annotation_step_id, vm.slide_id)
                .then(getClinicalAnnotationStepSuccessFn, getClinicalAnnotationStepErrorFn);

            function getClinicalAnnotationStepSuccessFn(response) {
                if (response.data.completed === true || response.data.can_be_started === false) {
                    $location.url('worklist/' + vm.case_id);
                }
            }

            function getClinicalAnnotationStepErrorFn(response) {
                console.error('Cannon load slide info');
                console.error(response);
            }
        }
    }
})();