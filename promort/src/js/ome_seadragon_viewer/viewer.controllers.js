(function () {
    'use strict';

    angular
        .module('promort.viewer.controllers')
        .controller('SimpleViewerController', SimpleViewerController)
        .controller('AnnotationsViewerController', AnnotationsViewerController);

    SimpleViewerController.$inject = ['$scope', '$routeParams', '$rootScope', '$location', '$log', 'ViewerService',
        'CurrentSlideDetailsService'];

    function SimpleViewerController($scope, $routeParams, $rootScope, $location, $log, ViewerService, 
                                    CurrentSlideDetailsService) {
        var vm = this;
        vm.slide_id = undefined;
        vm.annotation_step_label = undefined;
        vm.slide_details = undefined;
        vm.dzi_url = undefined;
        vm.static_files_url = undefined;
        vm.getDZIURL = getDZIURL;
        vm.getStaticFilesURL = getStaticFilesURL;
        vm.getSlideMicronsPerPixel = getSlideMicronsPerPixel;

        activate();

        function activate() {
            vm.annotation_step_label = $routeParams.label;
            vm.slide_id = CurrentSlideDetailsService.getSlideId();
            ViewerService.getOMEBaseURLs()
                .then(OMEBaseURLSuccessFn, OMEBaseURLErrorFn);

            function OMEBaseURLSuccessFn(response) {
                var base_url = response.data.base_url;
                vm.static_files_url = response.data.static_files_url + '/ome_seadragon/img/openseadragon/';

                ViewerService.getSlideInfo(vm.slide_id)
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
                    $log.error(response.error);
                    $location.url('404');
                }
            }

            function OMEBaseURLErrorFn(response) {
                $log.error(response.error);
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

    AnnotationsViewerController.$inject = ['$scope', '$rootScope', '$location', '$log', 'ngDialog',
        'ViewerService', 'AnnotationsViewerService', 'ROIsAnnotationStepManagerService',
        'CurrentSlideDetailsService', 'CurrentAnnotationStepsDetailsService'];

    function AnnotationsViewerController($scope, $rootScope, $location, $log, ngDialog, ViewerService,
                                         AnnotationsViewerService, ROIsAnnotationStepManagerService,
                                         CurrentSlideDetailsService, CurrentAnnotationStepsDetailsService) {
        var vm = this;
        vm.slide_id = undefined;
        vm.annotation_step_label = undefined;
        vm.slide_details = undefined;
        vm.dzi_url = undefined;
        vm.static_files_url = undefined;
        vm.getDZIURL = getDZIURL;
        vm.getStaticFilesURL = getStaticFilesURL;
        vm.getSlideMicronsPerPixel = getSlideMicronsPerPixel;
        vm.registerComponents = registerComponents;

        activate();

        function activate() {
            vm.slide_id = CurrentSlideDetailsService.getSlideId();
            vm.annotation_step_label = CurrentAnnotationStepsDetailsService.getROIsAnnotationStepLabel();
            ViewerService.getOMEBaseURLs()
                .then(OMEBaseURLSuccessFn, OMEBaseURLErrorFn);

            function OMEBaseURLSuccessFn(response) {
                var base_url = response.data.base_url;
                vm.static_files_url = response.data.static_files_url + '/ome_seadragon/img/openseadragon/';

                ViewerService.getSlideInfo(vm.slide_id)
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
                    $log.error(response.error);
                    $location.url('404');
                }
            }

            function OMEBaseURLErrorFn(response) {
                $log.error(response.error);
            }

            $scope.$on('viewerctrl.components.registered',
                function(event, rois_read_only, clinical_annotation_step_label) {
                    var dialog = ngDialog.open({
                        template: '/static/templates/dialogs/rois_loading.html',
                        showClose: false,
                        closeByEscape: false,
                        closeByNavigation: false,
                        closeByDocument: false
                    });
                    ROIsAnnotationStepManagerService.getROIs(vm.annotation_step_label, rois_read_only,
                        clinical_annotation_step_label)
                        .then(getROIsSuccessFn, getROIsErrorFn);

                    function getROIsSuccessFn(response) {
                        for (var sl in response.data.slices) {
                            var slice = response.data.slices[sl];
                            AnnotationsViewerService.drawShape($.parseJSON(slice.roi_json));
                            var annotated = false;
                            if (slice.hasOwnProperty('annotated')) {
                                annotated = slice.annotated;
                            }
                            var slice_info = {
                                'id': slice.id,
                                'label': slice.label,
                                'annotated': annotated
                            };
                            $rootScope.$broadcast('slice.new', slice_info);
                            for (var cr in slice.cores) {
                                var core = slice.cores[cr];
                                AnnotationsViewerService.drawShape($.parseJSON(core.roi_json));
                                annotated = false;
                                if (core.hasOwnProperty('annotated')) {
                                    annotated = core.annotated;
                                }
                                var core_info = {
                                    'id': core.id,
                                    'label': core.label,
                                    'slice': core.slice,
                                    'annotated': annotated,
                                    'tumor': core.positive
                                };
                                $rootScope.$broadcast('core.new', core_info);
                                for (var fr in core.focus_regions) {
                                    var focus_region = core.focus_regions[fr];
                                    AnnotationsViewerService.drawShape($.parseJSON(focus_region.roi_json));
                                    annotated = false;
                                    if (core.hasOwnProperty('annotated')) {
                                        annotated = focus_region.annotated;
                                    }
                                    var focus_region_info = {
                                        'id': focus_region.id,
                                        'label': focus_region.label,
                                        'core': focus_region.core,
                                        'annotated': annotated,
                                        'tumor': focus_region.cancerous_region
                                    };
                                    $rootScope.$broadcast('focus_region.new', focus_region_info);
                                }
                            }
                        }
                        dialog.close();
                    }

                    function getROIsErrorFn(response) {
                        $log.error('Unable to load ROIs for slide ' + vm.slide_id);
                        $log.error(response);
                        dialog.close();
                    }
                }
            );
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

        function registerComponents(viewer_manager, annotations_manager, tools_manager, rois_read_only) {
            AnnotationsViewerService.registerComponents(viewer_manager,
                annotations_manager, tools_manager);
            $log.debug('--- VERIFY ---');
            AnnotationsViewerService.checkComponents();
            var clinical_annotation_step_label = undefined;
            if (rois_read_only) {
                clinical_annotation_step_label =
                    CurrentAnnotationStepsDetailsService.getClinicalAnnotationStepLabel();
            }
            $rootScope.$broadcast('viewerctrl.components.registered', rois_read_only,
                clinical_annotation_step_label);
        }
    }
})();