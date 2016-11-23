(function () {
    'use strict';

    angular
        .module('promort.rois_manager.services')
        .factory('SlidesManagerService', SlidesManagerService)
        .factory('SlicesManagerService', SlicesManagerService)
        .factory('CoresManagerService', CoresManagerService)
        .factory('FocusRegionsManagerService', FocusRegionsManagerService);

    SlidesManagerService.$inject = ['$http'];

    function SlidesManagerService($http) {
        var SlidesManagerService = {
            getSlices: getSlices,
            createSlice: createSlice,
            getROIs: getROIs,
            clearROIs: clearROIs
        };

        return SlidesManagerService;

        function getSlices(slide_id) {
            return $http.get('/api/slides/' + slide_id + '/slices/');
        }

        function createSlice(slide_id, slice_label, roi_json, total_cores) {
            var params = {
                label: slice_label,
                roi_json: JSON.stringify(roi_json),
                total_cores: total_cores
            };
            return $http.post('/api/slides/' + slide_id + '/slices/', params);
        }

        function getROIs(slide_id) {
            return $http.get('/api/slides/' + slide_id + '/rois_list/');
        }

        function clearROIs(slide_id) {
            return $http.delete('/api/slides/' + slide_id + '/rois_list/');
        }
    }

    SlicesManagerService.$inject = ['$http'];

    function SlicesManagerService($http) {
        var SlicesManagerService = {
            get: get,
            cascadeDelete: cascadeDelete,
            getCores: getCores,
            createCore: createCore
        };

        return SlicesManagerService;

        function get(slice_id) {
            return $http.get('/api/slices/' + slice_id + '/');
        }

        function cascadeDelete(slice_id) {
            return $http.delete('/api/slices/' + slice_id + '/');
        }

        function getCores(slice_id) {
            return $http.get('/api/slices/' + slice_id + '/cores/');
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
            cascadeDelete: cascadeDelete,
            getFocusRegions: getFocusRegions,
            createFocusRegion: createFocusRegion
        };

        return CoresManagerService;

        function get(core_id) {
            return $http.get('/api/cores/' + core_id + '/');
        }

        function cascadeDelete(core_id) {
            return $http.delete('/api/cores/' + core_id + '/');
        }

        function getFocusRegions(core_id) {
            return $http.get('/api/cores/' + core_id + '/focus_regions/');
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
            cascadeDelete: cascadeDelete
        };

        return FocusRegionsManagerService;

        function get(focus_region_id) {
            return $http.get('/api/focus_regions/' + focus_region_id  + '/');
        }

        function cascadeDelete(focus_region_id) {
            return $http.delete('/api/focus_regions/' + focus_region_id + '/');
        }
    }
})();