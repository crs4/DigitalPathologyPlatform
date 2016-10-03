(function () {
    'use strict';
    
    angular
        .module('promort.slides_manager.controllers')
        .controller('QualityControlController', QualityControlController);

    QualityControlController.$inject = ['$scope', '$routeParams', '$location',
        'QualityControlService', 'ReviewStepsService'];

    function QualityControlController($scope, $routeParams, $location,
                                      QualityControlService, ReviewStepsService) {
        var vm = this;
        vm.slide_id = undefined;
        vm.case_id = undefined;
        vm.not_adequacy_reasons = undefined;
        vm.checkFormSubmission = checkFormSubmission;
        vm.submit = submit;

        vm.slideQualityControl = {};
        vm.reviewNotes = '';

        activate();

        function activate() {
            vm.slide_id = $routeParams.slide;
            vm.case_id = $routeParams.case;
            QualityControlService.get(vm.slide_id)
                .then(qualityControlSuccessFn, qualityControlErrorFn);

            function qualityControlSuccessFn(response) {
                // move to the ROIs review page
                $location.url('worklist/' + vm.case_id + '/' + vm.slide_id + '/rois_manager');
            }

            function qualityControlErrorFn(response) {
                if (response.status === 404) {
                    // initialize not_adequacy_reason
                    QualityControlService.fetchNotAdequacyReasons()
                        .then(fetchNotAdequacyReasonSuccessFn);

                    //noinspection JSAnnotator
                    function fetchNotAdequacyReasonSuccessFn(response) {
                        vm.not_adequacy_reasons = response.data;
                    }
                } else {
                    console.error(response.error);
                }
            }
        }

        function checkFormSubmission() {
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

        function submit() {
            QualityControlService.create(
                vm.slide_id,
                $.parseJSON(vm.slideQualityControl.goodImageQuality),
                vm.slideQualityControl.notAdequacyReason
            ).then(qualityControlCreationSuccessFn, qualityControlCreationErrorFn);

            function qualityControlCreationSuccessFn(response) {
                if(vm.slideQualityControl.goodImageQuality === 'true') {
                    $location.url('worklist/' + vm.case_id + '/' + vm.slide_id + '/rois');
                } else {
                    // close the review because image quality is bad
                    ReviewStepsService.closeReviewStep(vm.case_id, 'REVIEW_1',
                        vm.slide_id, vm.reviewNotes)
                        .then(closeReviewSuccessFn, closeReviewErrorFn);

                    //noinspection JSAnnotator
                    function closeReviewSuccessFn(response) {
                        // review closed, go back to case worklist
                        $location.url('worklist/' + vm.case_id);
                    }

                    //noinspection JSAnnotator
                    function closeReviewErrorFn(response) {
                        console.error(response.error);
                    }
                }
            }

            function qualityControlCreationErrorFn(response) {
                console.error(response.error);
            }
        }
    }
})();