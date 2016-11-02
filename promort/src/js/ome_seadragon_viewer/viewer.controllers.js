(function () {
    'use strict';

    angular
        .module('promort.viewer.controllers')
        .controller('SimpleViewerController', SimpleViewerController)
        .controller('AnnotationsViewerController', AnnotationsViewerController);

    SimpleViewerController.$inject = ['$scope', '$routeParams', '$rootScope', 'ViewerService'];

    function SimpleViewerController($scope, $routeParams, $rootScope, ViewerService) {
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

    AnnotationsViewerController.$inject = ['$scope', '$routeParams', '$rootScope', 'ngDialog',
        'ViewerService', 'AnnotationsViewerService', 'SlidesManagerService'];

    function AnnotationsViewerController($scope, $routeParams, $rootScope, ngDialog, ViewerService,
                                         AnnotationsViewerService, SlidesManagerService) {
        var vm = this;
        vm.slide_id = undefined;
        vm.slide_details = undefined;
        vm.dzi_url = undefined;
        vm.static_files_url = undefined;
        vm.getDZIURL = getDZIURL;
        vm.getStaticFilesURL = getStaticFilesURL;
        vm.getSlideMicronsPerPixel = getSlideMicronsPerPixel;
        vm.registerComponents = registerComponents;

        activate();

        function activate() {
            vm.slide_id = $routeParams.slide;
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
                    console.error(response.error);
                }
            }

            function OMEBaseURLErrorFn(response) {
                console.error(response.error);
            }

            $scope.$on('viewerctrl.components.registered',
                function() {
                    var dialog = ngDialog.open({
                        template: '/static/templates/dialogs/rois_loading.html',
                        showClose: false,
                        closeByEscape: false,
                        closeByNavigation: false,
                        closeByDocument: false
                    });

                    SlidesManagerService.getROIs(vm.slide_id).then(getROIsSuccessFn, getROIsErrorFn);

                    function getROIsSuccessFn(response) {
                        for (var sl in response.data.slices) {
                            var slice = response.data.slices[sl];
                            AnnotationsViewerService.drawShape($.parseJSON(slice.roi_json));
                            var slice_info = {
                                'id': slice.id,
                                'label': slice.label
                            };
                            $rootScope.$broadcast('slice.new', slice_info);
                            for (var cr in slice.cores) {
                                var core = slice.cores[cr];
                                AnnotationsViewerService.drawShape($.parseJSON(core.roi_json));
                                var core_info = {
                                    'id': core.id,
                                    'label': core.label,
                                    'slice': core.slice
                                };
                                $rootScope.$broadcast('core.new', core_info);
                                for (var fr in core.focus_regions) {
                                    var focus_region = core.focus_regions[fr];
                                    AnnotationsViewerService.drawShape($.parseJSON(focus_region.roi_json));
                                    var focus_region_info = {
                                        'id': focus_region.id,
                                        'label': focus_region.label,
                                        'core': focus_region.core
                                    };
                                    $rootScope.$broadcast('focus_region.new', focus_region_info);
                                }
                            }
                        }
                        dialog.close();
                    }

                    function getROIsErrorFn(response) {
                        console.error('Unable to load ROIs for slide ' + vm.slide_id);
                        console.error(response);
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

        function registerComponents(viewer_manager, annotations_manager, tools_manager) {
            AnnotationsViewerService.registerComponents(viewer_manager,
                annotations_manager, tools_manager);
            console.log('--- VERIFY ---');
            AnnotationsViewerService.checkComponents();
            $rootScope.$broadcast('viewerctrl.components.registered');
        }
    }
})();