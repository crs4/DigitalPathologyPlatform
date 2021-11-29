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
        .module('promort.rois_manager.services')
        .factory('ROIsAnnotationStepManagerService', ROIsAnnotationStepManagerService)
        .factory('SlicesManagerService', SlicesManagerService)
        .factory('CoresManagerService', CoresManagerService)
        .factory('FocusRegionsManagerService', FocusRegionsManagerService);

    ROIsAnnotationStepManagerService.$inject = ['$http', '$log'];

    function ROIsAnnotationStepManagerService($http, $log) {
        var ROIsAnnotationStepManagerService = {
            createSlice: createSlice,
            getROIs: getROIs,
            clearROIs: clearROIs
        };

        return ROIsAnnotationStepManagerService;

        function createSlice(step_label, slide_id, slice_label, roi_json, total_cores, action_start_time) {
            var params = {
                label: slice_label,
                slide: slide_id,
                roi_json: JSON.stringify(roi_json),
                total_cores: total_cores,
                action_start_time: action_start_time
            };
            return $http.post('/api/rois_annotation_steps/' + step_label + '/slices/', params);
        }

        function getROIs(step_label, read_only, clinical_step_label) {
            if (!read_only) {
                return $http.get('/api/rois_annotation_steps/' + step_label + '/rois_list/');
            } else {
                return $http.get('/api/rois_annotation_steps/' + step_label + '/rois_list/' + clinical_step_label + '/');
            }
        }

        function clearROIs(step_label) {
            return $http.delete('/api/rois_annotation_steps/' + step_label + '/rois_list/');
        }
    }

    SlicesManagerService.$inject = ['$http', '$log'];

    function SlicesManagerService($http, $log) {
        var SlicesManagerService = {
            get: get,
            update: update,
            cascadeDelete: cascadeDelete,
            createCore: createCore
        };

        return SlicesManagerService;

        function get(slice_id) {
            return $http.get('/api/slices/' + slice_id + '/');
        }

        function update(slice_id, total_cores) {
            var params = {
                total_cores: total_cores
            };
            return $http.put('/api/slices/' + slice_id + '/', params);
        }

        function cascadeDelete(slice_id) {
            return $http.delete('/api/slices/' + slice_id + '/');
        }

        function createCore(slice_id, core_label, roi_json, length, area, tumor_length, action_start_time) {
            var params = {
                label: core_label,
                roi_json: JSON.stringify(roi_json),
                length: length,
                area: area,
                tumor_length: tumor_length,
                action_start_time: action_start_time
            };
            return $http.post('/api/slices/' + slice_id + '/cores/', params);
        }
    }

    CoresManagerService.$inject = ['$http', '$log'];

    function CoresManagerService($http, $log) {
        var CoresManagerService = {
            get: get,
            update: update,
            cascadeDelete: cascadeDelete,
            createFocusRegion: createFocusRegion
        };

        return CoresManagerService;

        function get(core_id) {
            return $http.get('/api/cores/' + core_id + '/');
        }

        function update(core_id, length, tumor_length) {
            var params = {
                length: length,
                tumor_length: tumor_length
            };
            return $http.put('/api/cores/' + core_id + '/', params);
        }

        function cascadeDelete(core_id) {
            return $http.delete('/api/cores/' + core_id + '/');
        }

        function createFocusRegion(core_id, focus_region_label, roi_json, length, area, tissue_status,
                                   action_start_time) {
            var params = {
                label: focus_region_label,
                roi_json: JSON.stringify(roi_json),
                length: length,
                area: area,
                tissue_status: tissue_status,
                action_start_time: action_start_time
            };
            return $http.post('/api/cores/' + core_id + '/focus_regions/', params);
        }
    }

    FocusRegionsManagerService.$inject = ['$http', '$log'];

    function FocusRegionsManagerService($http, $log) {
        var FocusRegionsManagerService = {
            get: get,
            update: update,
            cascadeDelete: cascadeDelete
        };

        return FocusRegionsManagerService;

        function get(focus_region_id) {
            return $http.get('/api/focus_regions/' + focus_region_id  + '/');
        }

        function update(focus_region_id, roi_json, length, tissue_status) {
            var params = {
                roi_json: JSON.stringify(roi_json),
                length: length,
                tissue_status: tissue_status
            };
            return $http.put('/api/focus_regions/' + focus_region_id + '/', params);
        }

        function cascadeDelete(focus_region_id) {
            return $http.delete('/api/focus_regions/' + focus_region_id + '/');
        }
    }
})();