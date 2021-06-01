/*
 * Copyright (c) 2021, CRS4
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
        .module('promort.shared_datasets_manager.controllers')
        .controller('SharedDatasetsController', SharedDatasetsController)
        .controller('SharedDatasetItemsController', SharedDatasetItemsController)
        .controller('SharedDatasetItemViewController', SharedDatasetItemViewController);

    SharedDatasetsController.$inject = ['$scope', '$log', 'SharedDatasetsService'];

    function SharedDatasetsController($scope, $log, SharedDatasetsService) {
        var vm = this;

        vm.datasets = [];

        vm.getDatasetLink = getDatasetLink;

        activate();

        function activate() {
            SharedDatasetsService.list_datasets().then(listDatasetsSuccessFn, listDatasetsErrorFn);

            function listDatasetsSuccessFn(response) {
                vm.datasets = response.data;
            }

            function listDatasetsErrorFn(response) {
                $log.error(response.error);
            }
        }

        function getDatasetLink(dataset) {
            return 'datasets/' + dataset.id;
        }
    }

    SharedDatasetItemsController.$inject = ['$scope', '$routeParams', '$log', 'SharedDatasetsService'];

    function SharedDatasetItemsController($scope, $routeParams,  $log, SharedDatasetsService) {
        var vm = this;

        vm.dataset_id = undefined;
        vm.dataset_label = undefined;
        vm.items = [];

        vm.getDatasetItemLink = getDatasetItemLink;

        activate();

        function activate() {
            vm.dataset_id = $routeParams.dataset_id;
            SharedDatasetsService.get_dataset_details(vm.dataset_id)
                .then(getDatasetDetailsSuccessFn, getDatasetDetailsErrorFn);

            function getDatasetDetailsSuccessFn(response) {
                vm.dataset_label = response.data.label;
                vm.items = response.data.items;
            }

            function getDatasetDetailsErrorFn(response) {
                $log.error(response.error);
            }
        }

        function getDatasetItemLink(dataset_item) {
            return 'datasets/' + vm.dataset_id + '/' + dataset_item.dataset_index;
        }
    }

    SharedDatasetItemViewController.$inject = ['$scope', '$rootScope', '$routeParams', '$log', 'SharedDatasetsService',
                                               'SlidesSequenceViewerService'];

    function SharedDatasetItemViewController($scope, $rootScope, $routeParams, $log, SharedDatasetsService,
                                             SlidesSequenceViewerService) {
        var vm = this;

        vm.dataset_id = undefined;
        vm.dataset_label = undefined;
        vm.dataset_item_index = undefined;
        vm.slides_sync_enabled = false;
        vm.slides_set_a = undefined;
        vm.slides_set_a_label = undefined;
        vm.slides_set_b = undefined;
        vm.slides_set_b_label = undefined;
        vm.viewer_panels_details = undefined;
        vm.slides_set_a_panel = 'slides_panel_a';
        vm.slides_set_b_panel = 'slides_panel_b';

        vm.slidesSyncRequired = slidesSyncRequired;
        vm.slidesSyncEnabled = slidesSyncEnabled;
        vm.switchSlidesSync = switchSlidesSync;
        vm.enableDoubleViewer = enableDoubleViewer;
        vm.getSlidesSetADetails = getSlidesSetADetails;
        vm.getSlidesSetBDetails = getSlidesSetBDetails;
        vm.getSlidesSetLoadedTriggerLabel = getSlidesSetLoadedTriggerLabel;
        vm.getViewerReadyTrigger = getViewerReadyTrigger;

        activate();

        function activate() {
            vm.dataset_id = $routeParams.dataset_id;
            vm.dataset_item_index = $routeParams.dataset_item_index;
            vm.viewer_panels_details = {
                'set_a': undefined,
                'set_b': undefined
            };

            SharedDatasetsService.get_dataset_item(vm.dataset_id, vm.dataset_item_index)
                .then(getDatasetItemSuccessFn, getDatasetItemErrorFn);

            function getDatasetItemSuccessFn(response) {
                vm.dataset_label = response.data.dataset.label;
                vm.slides_set_a_label = response.data.slides_set_a_label;
                vm.slides_set_a = response.data.slides_set_a.id;
                if (response.data.slides_set_b !== null) {
                    vm.slides_set_b = response.data.slides_set_b.id;
                    vm.slides_set_b_label = response.data.slides_set_b_label;
                }

                SlidesSequenceViewerService.initialize();

                $rootScope.$broadcast(
                    vm.getSlidesSetLoadedTriggerLabel(vm.slides_set_a_panel),
                    vm.getSlidesSetADetails()
                );
                $scope.$on(vm.getViewerReadyTrigger(vm.slides_set_a_panel),
                    function(event, args) {
                        vm.viewer_panels_details.set_a = {
                            'label': args.viewer_label,
                            'slides_count': args.slides_count
                        }
                    }
                );
                if(vm.slides_set_b !== undefined) {
                    $rootScope.$broadcast(
                        vm.getSlidesSetLoadedTriggerLabel(vm.slides_set_b_panel),
                        vm.getSlidesSetBDetails()
                    );
                    $scope.$on(vm.getViewerReadyTrigger(vm.slides_set_b_panel),
                        function(event, args) {
                            vm.viewer_panels_details.set_b = {
                                'label': args.viewer_label,
                                'slides_count': args.slides_count
                            }
                        }
                    );
                }
            }

            function getDatasetItemErrorFn(response) {
                $log.error(response.error);
            }
        }

        function slidesSyncRequired() {
            if (vm.slides_set_b === undefined) {
                return false;
            } else {

            }
        }

        function slidesSyncEnabled() {
            vm.slides_sync_enabled = !vm.slides_sync_enabled;
        }

        function switchSlidesSync() {
            return vm.slides_sync_enabled;
        }

        function enableDoubleViewer() {
            return vm.slides_set_b !== undefined;
        }

        function getSlidesSetADetails() {
            return {
                'slides_set_id': vm.slides_set_a,
                'slides_set_label': vm.slides_set_a_label
            }
        }

        function getSlidesSetBDetails() {
            return {
                'slides_set_id': vm.slides_set_b,
                'slides_set_label': vm.slides_set_b_label
            }
        }

        function getSlidesSetLoadedTriggerLabel(slides_set) {
            return slides_set + '.slides.ready';
        }

        function getViewerReadyTrigger(slides_set) {
            return slides_set + '.viewer.ready';
        }
    }
})();