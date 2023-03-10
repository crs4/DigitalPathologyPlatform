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
        .module('promort.clinical_annotations_manager.services')
        .factory('ClinicalAnnotationStepManagerService', ClinicalAnnotationStepManagerService)
        .factory('SliceAnnotationsManagerService', SliceAnnotationsManagerService)
        .factory('CoreAnnotationsManagerService', CoreAnnotationsManagerService)
        .factory('FocusRegionAnnotationsManagerService', FocusRegionAnnotationsManagerService)
        .factory('GleasonPatternAnnotationsManagerService', GleasonPatternAnnotationsManagerService);

    ClinicalAnnotationStepManagerService.$inject = ['$http', '$log'];

    function ClinicalAnnotationStepManagerService($http, $log) {
        var ClinicalAnnotationStepManagerService = {
            clearAnnotations: clearAnnotations,
            fetchRejectionReasons: fetchRejectionReasons,
            fetchGleasonElementTypes: fetchGleasonElementTypes
        };

        return ClinicalAnnotationStepManagerService;

        function clearAnnotations(annotation_step_label) {
            return $http.delete('/api/clinical_annotation_steps/' + annotation_step_label + '/annotations_list/');
        }

        function fetchRejectionReasons() {
            return $http.get('api/utils/clinical_step_rejection_reasons/');
        }

        function fetchGleasonElementTypes() {
            console.log('Fetch Gleason types from server');
            return $http.get('api/utils/gleason_element_types/');
        }
    }

    SliceAnnotationsManagerService.$inject = ['$http', '$log'];

    function SliceAnnotationsManagerService($http, $log) {
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

    CoreAnnotationsManagerService.$inject = ['$http', '$log'];

    function CoreAnnotationsManagerService($http, $log) {
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

    FocusRegionAnnotationsManagerService.$inject = ['$http', '$log'];

    function FocusRegionAnnotationsManagerService($http, $log) {
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

    GleasonPatternAnnotationsManagerService.$inject = ['$http', '$log'];

    function GleasonPatternAnnotationsManagerService($http, $log) {
        var GleasonPatternAnnotationsManagerService = {
            getAnnotation: getAnnotation,
            createAnnotation: createAnnotation,
            deleteAnnotation: deleteAnnotation
        };

        return GleasonPatternAnnotationsManagerService;

        function getAnnotation() {

        }

        function createAnnotation(focus_region_id, annotation_step_label, gleason_pattern_config) {
            return $http.post('/api/focus_regions/' + focus_region_id + '/clinical_annotations/' +
                annotation_step_label + '/gleason_patterns/',
                gleason_pattern_config);
        }

        function deleteAnnotation() {

        }
    }
})();