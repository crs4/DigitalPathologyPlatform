(function () {
    'use strict';
    
    angular
        .module('promort.slides_manager.controllers')
        .controller('QualityControlController', QualityControlController);

    QualityControlController.$inject = ['$scope', '$routeParams', '$location', 'Authentication',
        'SlideEvaluationService', 'ROIsAnnotationStepService', 'SlideService', 'CurrentSlideDetailsService'];

    function QualityControlController($scope, $routeParams, $location, Authentication, SlideEvaluationService,
                                      ROIsAnnotationStepService, SlideService, CurrentSlideDetailsService) {
        var vm = this;
        vm.annotation_label = undefined;
        vm.annotation_step_label = undefined;
        vm.slide_id = undefined;
        vm.case_id = undefined;
        vm.annotation_step_id = undefined;
        vm.stainings = undefined;
        vm.not_adequacy_reasons = undefined;
        vm.checkEvaluationFormSubmission = checkEvaluationFormSubmission;
        vm.submitSlideEvaluation = submitSlideEvaluation;

        vm.slideStaining = undefined;
        vm.slideQualityControl = {};
        vm.reviewNotes = '';

        activate();

        function activate() {
            vm.annotation_step_label = $routeParams.label;
            vm.annotation_label = vm.annotation_step_label.split('-')[0];
            vm.slide_id = CurrentSlideDetailsService.getSlideId();
            vm.case_id = CurrentSlideDetailsService.getCaseId();

            ROIsAnnotationStepService.getDetails(vm.annotation_step_label)
                .then(getROIsAnnotationStepSuccessFn, getROIsAnnotationStepErrorFn);

            function getROIsAnnotationStepSuccessFn(response) {
                if (response.data.slide_evaluation === null) {
                    // initialize not_adequacy_reason
                    SlideEvaluationService.fetchNotAdequacyReasons()
                        .then(fetchNotAdequacyReasonSuccessFn);
                    //noinspection JSAnnotator
                    function fetchNotAdequacyReasonSuccessFn(response) {
                        vm.not_adequacy_reasons = response.data;
                    }
                    //initialize staining
                    SlideEvaluationService.fetchStainings()
                        .then(fetchStainingSuccessFn);
                    //noinspection JSAnnotator
                    function fetchStainingSuccessFn(response) {
                        vm.stainings = response.data;
                    }
                } else {
                    if (response.data.slide_evaluation.adequate_slide) {
                        $location.url('worklist/' + vm.annotation_step_label + '/rois_manager');
                    } else {
                        $location.url('worklist/' + vm.annotation_label);
                    }
                }
            }

            function getROIsAnnotationStepErrorFn(response) {
                console.error('Cannot load slide info');
                console.error(response);
            }
        }

        function checkEvaluationFormSubmission() {
            if (typeof vm.slideStaining === 'undefined') {
                return false;
            } else {
                if (
                    (
                        vm.slideQualityControl.goodImageQuality &&
                        vm.slideQualityControl.goodImageQuality === 'true'
                    )
                    ||
                    (
                        vm.slideQualityControl.goodImageQuality &&
                        vm.slideQualityControl.goodImageQuality === 'false' &&
                        vm.slideQualityControl.notAdequacyReason
                    )
                ) {
                    return true;
                }
                return false;
            }
        }

        function submitSlideEvaluation() {
            SlideEvaluationService.create(
                vm.annotation_step_label,
                vm.slideStaining,
                $.parseJSON(vm.slideQualityControl.goodImageQuality),
                vm.slideQualityControl.notAdequacyReason,
                vm.slideQualityControl.notes
            ).then(qualityControlCreationSuccessFn, qualityControlCreationErrorFn);

            function qualityControlCreationSuccessFn(response) {
                if(vm.slideQualityControl.goodImageQuality === 'true') {
                    ROIsAnnotationStepService.startAnnotationStep(vm.annotation_step_label)
                        .then(startAnnotationSuccessFn, startAnnotationErrorFn);

                    //noinspection JSAnnotator
                    function startAnnotationSuccessFn(response) {
                        $location.url('worklist/' + vm.annotation_step_label + '/rois_manager');
                    }

                    //noinspection JSAnnotator
                    function startAnnotationErrorFn(response) {
                        console.error(response.error);
                    }

                } else {
                    // close the review because image quality is bad
                    ROIsAnnotationStepService.startAndCloseAnnotationStep(vm.annotation_step_label)
                        .then(closeReviewSuccessFn, closeReviewErrorFn);

                    //noinspection JSAnnotator
                    function closeReviewSuccessFn(response) {
                        var rois_annotation_closed = response.data.rois_annotation_closed;
                        // TODO: close clinical annotation steps related to this object
                        var clinical_steps_notes = 'Automatically closed due to bad quality image';
                        ROIsAnnotationStepService.startAndCloseClinicalAnnotationSteps(
                            vm.annotation_step_label, clinical_steps_notes)
                            .then(closeClinicalStepsSuccessFn, closeClinicalStepsErrorFn);

                        function closeClinicalStepsSuccessFn(response) {
                            if (rois_annotation_closed === true) {
                                $location.url('worklist');
                            } else {
                                // review closed, go back to case worklist
                                $location.url('worklist/rois_annotations/' + vm.annotation_label);
                            }
                        }

                        function closeClinicalStepsErrorFn(response) {
                            console.error(response.error);
                        }
                    }

                    //noinspection JSAnnotator
                    function closeReviewErrorFn(response) {
                        console.error(response.error);
                    }
                }
            }

            function qualityControlCreationErrorFn(response) {
                console.error(response);
            }
        }
    }
})();