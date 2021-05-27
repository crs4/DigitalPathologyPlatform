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
        .controller('SharedDatasetItemsController', SharedDatasetItemsController);

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
})();