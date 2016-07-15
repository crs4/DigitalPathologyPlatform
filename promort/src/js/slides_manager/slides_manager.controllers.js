(function () {
    'use strict';
    
    angular
        .module('promort.slides_manager.controllers')
        .controller('QualityControlController', QualityControlController)
        .controller('SimpleViewerController', SimpleViewerController);

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

        $scope.slideQualityControl = {};
        $scope.reviewNotes = '';

        activate();

        function activate() {
            vm.slide_id = $routeParams.slide;
            vm.case_id = $routeParams.case;
            QualityControlService.get(vm.slide_id)
                .then(qualityControlSuccessFn, qualityControlErrorFn);

            function qualityControlSuccessFn(response) {
                // move to the ROIs review page
                console.log('$location.url(worklist/' + vm.case_id + '/' + vm.slide_id + '/rois');
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
            if ($scope.slideQualityControl.goodImageQuality &&
                $scope.slideQualityControl.goodImageQuality === 'true') {
                return true;
            }
            if ($scope.slideQualityControl.goodImageQuality &&
                $scope.slideQualityControl.goodImageQuality === 'false' &&
                $scope.slideQualityControl.notAdequacyReason) {
                return true;
            }
            return false;
        }

        function submit() {
            QualityControlService.create(
                vm.slide_id,
                $.parseJSON($scope.slideQualityControl.goodImageQuality),
                $scope.slideQualityControl.notAdequacyReason
            ).then(qualityControlCreationSuccessFn, qualityControlCreationErrorFn);

            function qualityControlCreationSuccessFn(response) {
                if($scope.slideQualityControl.goodImageQuality === 'true') {
                    console.log('redirect to ROIs review page');
                } else {
                    // close the review because image quality is bad
                    ReviewStepsService.closeReviewStep(vm.case_id, 'REVIEW_1',
                        vm.slide_id, $scope.reviewNotes)
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

    SimpleViewerController.$inject = ['$scope', '$routeParams',
        '$rootScope', 'SimpleViewerService', 'Authentication'];

    function SimpleViewerController($scope, $routeParams, $rootScope, 
                                    SimpleViewerService) {
        var vm = this;
        vm.slide_id = undefined;
        vm.slide_details = undefined;
        vm.dzi_url = undefined;
        vm.static_files_url = undefined;
        vm.getDZIURL = getDZIURL;
        vm.getStaticFilesURL = getStaticFilesURL;
        vm.getSlideMicronsPerPixel = getSlideMicronsPerPixel;

        activate();

        function activate() {
            vm.slide_id = $routeParams.slide;
            SimpleViewerService.getOMEBaseURLs()
                .then(OMEBaseURLSuccessFn, OMEBaseURLErrorFn);

            function OMEBaseURLSuccessFn(response) {
                var base_url = response.data.base_url;
                vm.static_files_url = response.data.static_files_url + '/ome_seadragon/img/openseadragon/';

                SimpleViewerService.getSlideInfo(vm.slide_id)
                    .then(SlideInfoSuccessFn, SlideInfoErrorFn);

                function SlideInfoSuccessFn(response) {
                    vm.slide_details = response.data;
                    if (vm.slide_details.image_type === 'MIRAX') {
                        vm.dzi_url = base_url + 'mirax/deepzoom/get/' + vm.slide_details.id + '.dzi';
                    } else {
                        vm.dzi_url = base_url + 'deepzoom/get/' + vm.slide_details.id + '.dzi';
                    }
                    $rootScope.$broadcast('viewer.controller_initialized');
                }

                function SlideInfoErrorFn(response) {
                    console.error(response.error);
                }
            }

            function OMEBaseURLErrorFn(response) {
                console.error(response.error);
            }
        }

        function getDZIURL() {
            return vm.dzi_url;
        }
        
        function getStaticFilesURL() {
            return vm.static_files_url;
        }

        function getSlideMicronsPerPixel() {
            return vm.slide_details.image_microns_per_pixel;
        }
    }
})();