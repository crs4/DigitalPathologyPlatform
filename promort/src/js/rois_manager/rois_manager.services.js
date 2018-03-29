(function () {
    'use strict';

    angular
        .module('promort.rois_manager.services')
        .factory('ROIsAnnotationStepManagerService', ROIsAnnotationStepManagerService)
        .factory('SlicesManagerService', SlicesManagerService)
        .factory('CoresManagerService', CoresManagerService)
        .factory('FocusRegionsManagerService', FocusRegionsManagerService);

    ROIsAnnotationStepManagerService.$inject = ['$http'];

    function ROIsAnnotationStepManagerService($http) {
        var ROIsAnnotationStepManagerService = {
            createSlice: createSlice,
            getROIs: getROIs,
            clearROIs: clearROIs
        };

        return ROIsAnnotationStepManagerService;

        function createSlice(step_label, slide_id, slice_label, roi_json, total_cores) {
            var params = {
                label: slice_label,
                slide: slide_id,
                roi_json: JSON.stringify(roi_json),
                total_cores: total_cores
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

    SlicesManagerService.$inject = ['$http'];

    function SlicesManagerService($http) {
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

        function createCore(slice_id, core_label, roi_json, length, area, tumor_length) {
            var params = {
                label: core_label,
                roi_json: JSON.stringify(roi_json),
                length: length,
                area: area,
                tumor_length: tumor_length
            };
            return $http.post('/api/slices/' + slice_id + '/cores/', params);
        }
    }

    CoresManagerService.$inject = ['$http'];

    function CoresManagerService($http) {
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

        function createFocusRegion(core_id, focus_region_label, roi_json, length, area, cancerous_region) {
            var params = {
                label: focus_region_label,
                roi_json: JSON.stringify(roi_json),
                length: length,
                area: area,
                cancerous_region: cancerous_region
            };
            return $http.post('/api/cores/' + core_id + '/focus_regions/', params);
        }
    }

    FocusRegionsManagerService.$inject = ['$http'];

    function FocusRegionsManagerService($http) {
        var FocusRegionsManagerService = {
            get: get,
            update: update,
            cascadeDelete: cascadeDelete
        };

        return FocusRegionsManagerService;

        function get(focus_region_id) {
            return $http.get('/api/focus_regions/' + focus_region_id  + '/');
        }

        function update(focus_region_id, length, cancerous_region) {
            var params = {
                length: length,
                cancerous_region: cancerous_region
            };
            return $http.put('/api/focus_regions/' + focus_region_id + '/', params);
        }

        function cascadeDelete(focus_region_id) {
            return $http.delete('/api/focus_regions/' + focus_region_id + '/');
        }
    }
})();