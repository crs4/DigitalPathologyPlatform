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

    AnnotationsViewerController.$inject = ['$scope', '$routeParams', '$rootScope',
        'ViewerService', 'AnnotationsViewerService', 'SlidesManagerService',
        'SlicesManagerService', 'CoresManagerService'];

    function AnnotationsViewerController($scope, $routeParams, $rootScope, ViewerService,
                                         AnnotationsViewerService, SlidesManagerService,
                                         SlicesManagerService, CoresManagerService) {
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
                    console.log('AnnotationsViewerController');
                    console.log('Retrieving existing slices');
                    SlidesManagerService.getSlices(vm.slide_id).then(getSlicesSuccessFn, getSlicesErrorFn);

                    function getSlicesSuccessFn(response) {
                        function drawSlice(slice_data) {
                            AnnotationsViewerService.drawShape($.parseJSON(slice_data.roi_json));
                            var slice_info = {
                                'id': slice_data.id,
                                'label': slice_data.label
                            };
                            $rootScope.$broadcast('slice.new', slice_info);
                            // load cores
                            SlicesManagerService.getCores(slice_data.id)
                                .then(getCoresSuccessFn, getCoresErrorFn);
                        }
                        response.data.slices.forEach(drawSlice);
                    }

                    function getSlicesErrorFn(response) {
                        console.error('Unable to load slices for slide ' + vm.slide_id);
                        console.error(response.data);
                    }

                    function getCoresSuccessFn(response) {
                        function drawCore(core_data) {
                            console.log('Drawing core ' + core_data.label);
                            AnnotationsViewerService.drawShape($.parseJSON(core_data.roi_json));
                            var core_info = {
                                'id': core_data.id,
                                'label': core_data.label,
                                'slice': core_data.slice
                            };
                            $rootScope.$broadcast('core.new', core_info);
                            // load focus regions
                            CoresManagerService.getFocusRegions(core_data.id)
                                .then(getFocusRegionsSuccessFn, getFocusRegionsErrorFn)
                        }
                        response.data.cores.forEach(drawCore);
                    }

                    function getCoresErrorFn(response) {
                        console.error('Unable to load cores');
                        console.error(response.data);
                    }

                    function getFocusRegionsSuccessFn(response) {
                        function drawFocusRegion(focus_region_data) {
                            console.log('Drawing focus regions ' + focus_region_data.label);
                            AnnotationsViewerService.drawShape($.parseJSON(focus_region_data.roi_json));
                            var focus_region_info = {
                                'id': focus_region_data.id,
                                'label': focus_region_data.label,
                                'core': focus_region_data.core
                            };
                            $rootScope.$broadcast('focus_region.new', focus_region_info);
                        }
                        response.data.focus_regions.forEach(drawFocusRegion);
                    }

                    function getFocusRegionsErrorFn(response) {
                        console.error('Unable to load focus regions');
                        console.error(response.data);
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