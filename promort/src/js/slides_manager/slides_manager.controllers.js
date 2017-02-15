(function () {
    'use strict';
    
    angular
        .module('promort.slides_manager.controllers')
        .controller('QualityControlController', QualityControlController);

    QualityControlController.$inject = ['$scope', '$routeParams', '$location', 'Authentication',
        'QualityControlService', 'ROIsAnnotationStepService', 'SlideService'];

    function QualityControlController($scope, $routeParams, $location, Authentication, QualityControlService,
                                      ROIsAnnotationStepService, SlideService) {
        var vm = this;
        vm.slide_id = undefined;
        vm.case_id = undefined;
        vm.annotation_step_id = undefined;
        vm.stainings = undefined;
        vm.not_adequacy_reasons = undefined;
        vm.checkStainingFormSubmission = checkStainingFormSubmission;
        vm.checkQCFormSubmission = checkQCFormSubmission;
        vm.submitStaining = submitStaining;
        vm.submitQualityControl = submitQualityControl;

        vm.slideStainingSubmitted = false;
        vm.slideStaining = undefined;
        vm.slideQualityControl = {};
        vm.reviewNotes = '';

        activate();

        function activate() {
            vm.slide_id = $routeParams.slide;
            vm.case_id = $routeParams.case;
            vm.annotation_step_id = $routeParams.annotation_step;

            ROIsAnnotationStepService.getDetails(vm.case_id, Authentication.getCurrentUser(), vm.slide_id)
                .then(getROIsAnnotationStepSuccessFn, getROIsAnnotationStepErrorFn);

            function getROIsAnnotationStepSuccessFn(response) {
                if (response.data.slide_quality_control === null) {
                    // initialize not_adequacy_reason
                    QualityControlService.fetchNotAdequacyReasons()
                        .then(fetchNotAdequacyReasonSuccessFn);
                    //noinspection JSAnnotator
                    function fetchNotAdequacyReasonSuccessFn(response) {
                        vm.not_adequacy_reasons = response.data;
                    }
                    //initialize staining
                    SlideService.fetchStainings()
                        .then(fetchStainingSuccessFn);
                    //noinspection JSAnnotator
                    function fetchStainingSuccessFn(response) {
                        vm.stainings = response.data;
                    }
                    if (response.data.slide.staining !== null) {
                        vm.slideStaining = response.data.slide.staining;
                        vm.slideStainingSubmitted = true;
                    }
                } else {
                    if (response.data.slide_quality_control.adequate_slide) {
                        $location.url('worklist/' + vm.case_id + '/' + vm.slide_id + '/' +
                            vm.annotation_step_id + '/rois_manager');
                    } else {
                        $location.url('worklist/' + vm.case_id);
                    }
                }
            }

            function getROIsAnnotationStepErrorFn(response) {
                console.error('Cannot load slide info');
                console.error(response);
            }
        }

        function checkStainingFormSubmission() {
            return !(typeof vm.slideStaining === 'undefined');
        }

        function checkQCFormSubmission() {
            if (!vm.slideStainingSubmitted) {
                return false;
            }
            if (vm.slideQualityControl.goodImageQuality &&
                vm.slideQualityControl.goodImageQuality === 'true') {
                return true;
            }
            if (vm.slideQualityControl.goodImageQuality &&
                vm.slideQualityControl.goodImageQuality === 'false' &&
                vm.slideQualityControl.notAdequacyReason) {
                return true;
            }
            return false;
        }

        function submitStaining() {
            SlideService.updateSliceStaining(
                vm.slide_id,
                vm.slideStaining
            ).then(slideStainingUpdateSuccessFn, slideStainingUpdateErrorFn);

            function slideStainingUpdateSuccessFn(response) {
                vm.slideStainingSubmitted = true;
            }

            function slideStainingUpdateErrorFn(response) {
                console.error('Unable to update slide staining');
                console.error(response);
            }
        }

        function submitQualityControl() {
            QualityControlService.create(
                vm.case_id,
                Authentication.getCurrentUser(),
                vm.slide_id,
                $.parseJSON(vm.slideQualityControl.goodImageQuality),
                vm.slideQualityControl.notAdequacyReason,
                vm.slideQualityControl.notes
            ).then(qualityControlCreationSuccessFn, qualityControlCreationErrorFn);

            function qualityControlCreationSuccessFn(response) {
                if(vm.slideQualityControl.goodImageQuality === 'true') {
                    ROIsAnnotationStepService.startAnnotationStep(vm.case_id, Authentication.getCurrentUser(),
                        vm.slide_id).then(startAnnotationSuccessFn, startAnnotationErrorFn);

                    //noinspection JSAnnotator
                    function startAnnotationSuccessFn(response) {
                        $location.url('worklist/' + vm.case_id + '/' + vm.slide_id + '/' +
                            vm.annotation_step_id + '/rois_manager');
                    }

                    //noinspection JSAnnotator
                    function startAnnotationErrorFn(response) {
                        console.error(response.error);
                    }

                } else {
                    // close the review because image quality is bad
                    ROIsAnnotationStepService.closeAnnotationStep(vm.case_id, Authentication.getCurrentUser(),
                        vm.slide_id).then(closeReviewSuccessFn, closeReviewErrorFn);

                    //noinspection JSAnnotator
                    function closeReviewSuccessFn(response) {
                        // TODO: close clinical annotation steps related to this object
                        if (response.data.rois_annotation_closed === true) {
                            $location.url('worklist');
                        } else {
                            // review closed, go back to case worklist
                            $location.url('worklist/' + vm.case_id);
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