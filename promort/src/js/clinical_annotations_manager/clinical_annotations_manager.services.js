(function () {
    'use strict';

    angular
        .module('promort.clinical_annotations_manager.services')
        .factory('ClinicalAnnotationStepManagerService', ClinicalAnnotationStepManagerService)
        .factory('SliceAnnotationsManagerService', SliceAnnotationsManagerService)
        .factory('CoreAnnotationsManagerService', CoreAnnotationsManagerService)
        .factory('FocusRegionAnnotationsManagerService', FocusRegionAnnotationsManagerService);

    ClinicalAnnotationStepManagerService.$inject = ['$http'];

    function ClinicalAnnotationStepManagerService($http) {
        var ClinicalAnnotationStepManagerService = {
            clearAnnotations: clearAnnotations,
            fetchRejectionReasons: fetchRejectionReasons
        };

        return ClinicalAnnotationStepManagerService;

        function clearAnnotations(annotation_step_label) {
            return $http.delete('/api/clinical_annotation_steps/' + annotation_step_label + '/annotations_list/');
        }

        function fetchRejectionReasons() {
            return $http.get('api/utils/clinical_step_rejection_reasons/');
        }
    }

    SliceAnnotationsManagerService.$inject = ['$http'];

    function SliceAnnotationsManagerService($http) {
        var SliceAnnotationsManagerService = {
            getAnnotation: getAnnotation,
            createAnnotation: createAnnotation,
            deleteAnnotation: deleteAnnotation
        };

        return SliceAnnotationsManagerService;

        function getAnnotation(slice_id, annotation_step_label) {
            return $http.get('/api/slices/' + slice_id + '/clinical_annotations/' + annotation_step_label + '/');
        }

        function createAnnotation(slice_id, annotation_step_label, annotation_config) {
            return $http.post('/api/slices/' + slice_id + '/clinical_annotations/' + annotation_step_label + '/',
                annotation_config);
        }

        function deleteAnnotation(slice_id, annotation_step_label) {
            return $http.delete('/api/slices/' + slice_id + '/clinical_annotations/' + annotation_step_label + '/');
        }
    }

    CoreAnnotationsManagerService.$inject = ['$http'];

    function CoreAnnotationsManagerService($http) {
        var CoreAnnotationsManagerService = {
            getAnnotation: getAnnotation,
            createAnnotation: createAnnotation,
            deleteAnnotation: deleteAnnotation
        };

        return CoreAnnotationsManagerService;

        function getAnnotation(core_id, annotation_step_label) {
            return $http.get('/api/cores/' + core_id + '/clinical_annotations/' + annotation_step_label +'/');
        }

        function createAnnotation(core_id, annotation_step_label, annotation_config) {
            return $http.post('/api/cores/' + core_id + '/clinical_annotations/' + annotation_step_label +'/',
                annotation_config);
        }

        function deleteAnnotation(core_id, annotation_step_label) {
            return $http.delete('/api/cores/' + core_id + '/clinical_annotations/' + annotation_step_label +'/');
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

        function getAnnotation(focus_region_id, annotation_step_label) {
            return $http.get('/api/focus_regions/' + focus_region_id + '/clinical_annotations/' +
                annotation_step_label + '/');
        }

        function createAnnotation(focus_region_id, annotation_step_label, annotation_config) {
            return $http.post('/api/focus_regions/' + focus_region_id + '/clinical_annotations/' +
                annotation_step_label + '/',
                annotation_config);
        }

        function deleteAnnotation(focus_region_id, annotation_step_label) {
            return $http.delete('/api/focus_regions/' + focus_region_id + '/clinical_annotations/' +
                annotation_step_label + '/');
        }
    }
})();