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
        .module('promort.shared_datasets_manager.services')
        .factory('SharedDatasetsService', SharedDatasetsService);

    SharedDatasetsService.$inject = ['$http', '$log'];

    function SharedDatasetsService($http, $log) {
        var SharedDatasetsService = {
            list_datasets: list_datasets,
            get_dataset_details: get_dataset_details,
            get_dataset_item: get_dataset_item
        };

        return SharedDatasetsService;

        function list_datasets() {
            return $http.get('/api/shared_datasets/');
        }

        function get_dataset_details(dataset_id) {
            return $http.get('/api/shared_datasets/' + dataset_id + '/');
        }

        function get_dataset_item(dataset_id, item_index) {
            return $http.get('/api/shared_datasets/' + dataset_id + '/' + item_index +'/');
        }
    }
})();