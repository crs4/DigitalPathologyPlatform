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
        .module('promort.viewer.controllers')
        .controller('MiniViewerNavigationController', MiniViewerNavigationController)
        .controller('SimpleViewerController', SimpleViewerController)
        .controller('SimpleHeatmapViewerController', SimpleHeatmapViewerController)
        .controller('AnnotationsViewerController', AnnotationsViewerController)
        .controller('SlidesSequenceViewerController', SlidesSequenceViewerController);

    MiniViewerNavigationController.$inject = ['$scope', '$log', 'SlidesSequenceViewerService'];

    function MiniViewerNavigationController($scope, $log, SlidesSequenceViewerService) {
        var vm = this;
        vm.viewer_panel_id = undefined;
        vm.getNaviItemID = getNaviItemID;

        activate();

        function activate() {
            vm.viewer_panel_id = $scope.viewerPanelId;
        }

        function getNaviItemID(item_label) {
            return SlidesSequenceViewerService.getNaviItemID(vm.viewer_panel_id, item_label);
        }
    }

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
                        vm.dzi_url = base_url + 'deepzoom/get/' + vm.slide_details.omero_id + '.dzi';
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

    SimpleHeatmapViewerController.$inject = ['$scope', '$routeParams', '$rootScope', '$location', '$log',
        'ViewerService', 'HeatmapViewerService', 'CurrentPredictionDetailsService'];
    
    function SimpleHeatmapViewerController($scope, $routeParams, $rootScope, $location, $log, ViewerService,
                                           HeatmapViewerService, CurrentPredictionDetailsService) {
        var vm = this;
        vm.slide_id = undefined;
        vm.prediction_id = undefined;
        vm.slide_details = undefined;
        vm.prediction_details = undefined;
        vm.dzi_url = undefined;
        vm.dataset_dzi_url = undefined;
        vm.static_files_url = undefined;
        vm.current_opacity = undefined;
        vm.getDZIURL = getDZIURL;
        vm.getDatasetDZIURL = getDatasetDZIURL;
        vm.getStaticFilesURL = getStaticFilesURL;
        vm.getSlideMicronsPerPixel = getSlideMicronsPerPixel;
        vm.registerComponents = registerComponents;
        vm.setOverlayOpacity = setOverlayOpacity;
        vm.updateOverlayOpacity = updateOverlayOpacity;

        activate();

        function activate() {
            vm.slide_id = CurrentPredictionDetailsService.getSlideId();
            vm.prediction_id = CurrentPredictionDetailsService.getPredictionId();

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
                        vm.dzi_url = base_url + 'deepzoom/get/' + vm.slide_details.omero_id + '.dzi';
                    }

                    HeatmapViewerService.getPredictionInfo(vm.prediction_id)
                        .then(PredictionInfoSuccessFn, PredictionInfoErrorFn);

                    function PredictionInfoSuccessFn(response) {
                        vm.prediction_details = response.data;
                        vm.dataset_dzi_url = base_url + 'arrays/deepzoom/get/' + vm.prediction_details.omero_id + '.dzi';

                        $rootScope.$broadcast('viewer.controller_initialized');
                    }

                    function PredictionInfoErrorFn(response) {
                        $log.error(response.error);
                        $location.url('404');
                    }
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
            return vm.dzi_url + '?limit_bounds=false';
        }

        function getDatasetDZIURL(color_palette) {
            return vm.dataset_dzi_url + '?palette=' + color_palette;
        }

        function getStaticFilesURL() {
            return vm.static_files_url;
        }

        function getSlideMicronsPerPixel() {
            return vm.slide_details.image_microns_per_pixel;
        }

        function registerComponents(viewer_manager, dataset_base_url) {
            HeatmapViewerService.registerComponents(viewer_manager, dataset_base_url);
        }

        function setOverlayOpacity(opacity, update) {
            this.current_opacity = opacity;
            if (typeof(update) !== 'undefined' && update === true) {
                this.updateOverlayOpacity();
            }
        }

        function updateOverlayOpacity() {
            HeatmapViewerService.setOverlayOpacity(this.current_opacity);
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
                        vm.dzi_url = base_url + 'deepzoom/get/' + vm.slide_details.omero_id + '.dzi';
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
                                        'tumor': focus_region.tissue_status === 'TUMOR',
                                        'stressed': focus_region.tissue_status === 'STRESSED'
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

    SlidesSequenceViewerController.$inject = ['$scope', '$routeParams', '$rootScope', '$location', '$log',
        'ViewerService', 'SlidesSetService', 'SlidesSequenceViewerService'];

    function SlidesSequenceViewerController($scope, $routeParams, $rootScope, $location, $log, ViewerService,
                                            SlidesSetService, SlidesSequenceViewerService) {
        var vm = this;
        vm.slides_set_id = undefined;
        vm.slides_set_label = undefined;
        vm.dzi_urls = undefined;
        vm.pages = [];
        vm.static_files_url = undefined;
        vm.viewer_identifier = undefined;
        vm.current_page = undefined;
        vm.compact_viewer = undefined;

        vm.addSetItem = addSetItem;
        vm.isMultiSlidesSet = isMultiSlidesSet;
        vm.getDZIURLs = getDZIURLs;
        vm.getStaticFilesURL = getStaticFilesURL;
        vm.getPages = getPages;
        vm.isPageActive = isPageActive;
        vm.getPagesMap = getPagesMap;
        vm.checkPage = checkPage;
        vm.getViewerID = getViewerID;
        vm.registerViewer = registerViewer;
        vm.goToPage = goToPage;
        vm.getNaviItemID = getNaviItemID;
        vm.getSlidesSetLabel = getSlidesSetLabel;
        vm.enableCompactViewer = enableCompactViewer;

        activate();

        function activate() {
            vm.viewer_identifier = $scope.viewerIdentifier;
            vm.compact_viewer = $.parseJSON($scope.compactViewer);

            $scope.$on(
                $scope.svWaitForIt,
                function(event, args){
                    vm.dzi_urls = [];
                    vm.pages = [];
                    vm.slides_set_id = args.slides_set_id;
                    vm.slides_set_label = args.slides_set_label;

                    ViewerService.getOMEBaseURLs()
                        .then(OMEBaseUrlSuccessFn, OMEBaseUrlErrorFn);

                    function OMEBaseUrlSuccessFn(response) {
                        var base_url = response.data.base_url;
                        vm.static_files_url = response.data.static_files_url + '/ome_seadragon/img/openseadragon/';

                        SlidesSetService.get(vm.slides_set_id)
                            .then(SlidesSetSuccessFn, SlidesSetErrorFn);

                        function SlidesSetSuccessFn(response) {
                            for (var i=0; i<response.data.items.length; i++) {
                                vm.addSetItem(response.data.items[i], base_url);
                            }
                            vm.current_page = vm.pages[0]['label'];

                            $rootScope.$broadcast($scope.viewerReady,
                                {'viewer_label': vm.getViewerID(), 'slides_count': vm.pages.length});
                        }

                        function SlidesSetErrorFn(response) {
                            $log.error(response.error);
                            // $location.url('404');
                        }
                    }

                    function OMEBaseUrlErrorFn(response) {
                        $log.error(response.error);
                        // $location.url('404');
                    }
                }
            )

            $scope.$on('slides_sequence.page.change', function(event, args) {
                if (args.viewer_id === vm.getViewerID()) {
                    console.log('Ignore change page trigger, it was me');
                } else {
                    console.log('Received order to change to page ' + args.page);
                    if (vm.checkPage(args.page)) {
                        console.log('Changing to page ' + args.page);
                        vm.goToPage(args.page, false);
                    } else {
                        console.log('SlidesSet has no page ' + args.page);
                    }
                }
            });
        }

        function addSetItem(slides_set_item, ome_base_url) {
            if (slides_set_item.image_type === 'MIRAX') {
                var dzi_url = ome_base_url + 'mirax/deepzoom/get/' + slides_set_item.slide + '.dzi';
            } else {
                var dzi_url = ome_base_url + 'deepzoom/get/' + slides_set_item.omero_id + '.dzi';
            }
            vm.dzi_urls.push(dzi_url);
            vm.pages.push({
                'label': slides_set_item.set_label,
                'index': slides_set_item.set_index
            });
        }

        function isMultiSlidesSet() {
            return vm.pages.length > 1;
        }

        function getDZIURLs() {
            return vm.dzi_urls;
        }

        function getStaticFilesURL() {
            return vm.static_files_url;
        }

        function getPages() {
            return vm.pages;
        }

        function isPageActive(page_label) {
            return vm.current_page === page_label;
        }

        function getPagesMap() {
            var pages = {}
            for (var i=0; i < vm.pages.length; i++) {
                pages[vm.pages[i].label] = vm.pages[i].index;
            }
            return pages;
        }

        function checkPage(page_label) {
            var pages_map = vm.getPagesMap();
            return pages_map.hasOwnProperty(page_label);
        }

        function getViewerID() {
            return vm.viewer_identifier;
        }

        function registerViewer(viewer) {
            SlidesSequenceViewerService.registerViewer(vm.getViewerID(), viewer);
        }

        function goToPage(page_label, trigger_event) {
            var trigger_event =  typeof trigger_event !== 'undefined' ? trigger_event : true;
            var pages_map = vm.getPagesMap();
            SlidesSequenceViewerService.goToPage(vm.getViewerID(), pages_map[page_label]);
            vm.current_page = page_label;
            if (trigger_event) {
                console.log('Trigger page changed event');
                $rootScope.$broadcast('slides_sequence.page.changed',
                    {'page': page_label, 'viewer_id': vm.getViewerID()});
            }
        }

        function getNaviItemID(item_label) {
            return SlidesSequenceViewerService.getNaviItemID(vm.getViewerID(), item_label);
        }

        function getSlidesSetLabel() {
            return vm.slides_set_label;
        }

        function enableCompactViewer() {
            return vm.compact_viewer;
        }
    }
})();