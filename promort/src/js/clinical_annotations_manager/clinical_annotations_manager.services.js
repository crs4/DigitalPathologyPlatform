(function () {
    'use strict';

    angular
        .module('promort.clinical_annotations_manager.services')
        .factory('SliceAnnotationsManagerService', SliceAnnotationsManagerService)
        .factory('CoreAnnotationsManagerService', CoreAnnotationsManagerService)
        .factory('FocusRegionAnnotationsManagerService', FocusRegionAnnotationsManagerService);

    SliceAnnotationsManagerService.$inject = ['$http'];

    function SliceAnnotationsManagerService($http) {
        var SliceAnnotationsManagerService = {
            getAnnotation: getAnnotation,
            createAnnotation: createAnnotation,
            deleteAnnotation: deleteAnnotation
        };

        return SliceAnnotationsManagerService;

        function getAnnotation(slice_id, annotation_step_id) {
            return $http.get('/api/slices/' + slice_id + '/clinical_annotations/' + annotation_step_id + '/');
        }

        function createAnnotation(slice_id, annotation_step_id, annotation_config) {
            return $http.post('/api/slices/' + slice_id + '/clinical_annotations/' + annotation_step_id + '/',
                annotation_config);
        }

        function deleteAnnotation(slice_id, annotation_step_id) {
            return $http.delete('/api/slices/' + slice_id + '/clinical_annotations/' + annotation_step_id + '/');
        }
    }

    CoreAnnotationsManagerService.$inject = ['$http'];

    function CoreAnnotationsManagerService($http) {
        var CoreAnnotationsManagerService = {
            getAnnotation: getAnnotation,
            createAnnoation: createAnnotation,
            deleteAnnotation: deleteAnnotation
        };

        return CoreAnnotationsManagerService;

        function getAnnotation(core_id, annotation_step_id) {
            return $http.get('/api/cores/' + core_id + '/clinical_annotations/' + annotation_step_id +'/');
        }

        function createAnnotation(core_id, annotation_step_id, annotation_config) {
            return $http.post('/api/cores/' + core_id + '/clinical_annotations/' + annotation_step_id +'/',
                annotation_config);
        }

        function deleteAnnotation(core_id, annotation_step_id) {
            return $http.delete('/api/cores/' + core_id + '/clinical_annotations/' + annotation_step_id +'/');
        }
    }

    FocusRegionAnnotationsManagerService.$inject = ['$http'];

    function FocusRegionAnnotationsManagerService($http) {
        var FocusRegionAnnotationsManagerService = {
            getAnnotation: getAnnotation,
            createAnnotation: createAnnotation,
            deleteAnnotation: deleteAnnotation
        };

        return FocusRegionAnnotationsManagerService;

        function getAnnotation(focus_region_id, annotation_step_id) {
            return $http.get('/api/focus_regions/' + focus_region_id + '/clinical_annotations/' +
                annotation_step_id + '/');
        }

        function createAnnotation(focus_region_id, annotation_step_id, annotation_config) {
            return $http.post('/api/focus_regions/' + focus_region_id + '/clinical_annotations/' +
                annotation_step_id + '/',
                annotation_config);
        }

        function deleteAnnotation(focus_region_id, annotation_step_id) {
            return $http.delete('/api/focus_regions/' + focus_region_id + '/clinical_annotations/' +
                annotation_step_id + '/');
        }
    }
})();