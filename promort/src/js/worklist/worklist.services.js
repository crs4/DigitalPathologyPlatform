(function () {
    'use strict';

    angular
        .module('promort.worklist.services')
        .factory('WorkListService', WorkListService)
        .factory('ROIsAnnotationStepService', ROIsAnnotationStepService)
        .factory('ClinicalAnnotationStepService', ClinicalAnnotationStepService);

    WorkListService.$inject = ['$http'];

    function WorkListService($http) {
        var WorkListService = {
            get: get,
            startROIsAnnotation: startROIsAnnotation,
            closeROIsAnnotation: closeROIsAnnotation,
            startClinicalAnnotation: startClinicalAnnotation,
            closeClinicalAnnotation: closeClinicalAnnotation
        };

        return WorkListService;

        function get() {
            return $http.get('/api/worklist/');
        }

        function _ROIsAnnotationAction(case_id, reviewer, action) {
            return $http.put(
                '/api/rois_annotations/' + case_id + '/' + reviewer + '/',
                {action: action}
            );
        }

        function startROIsAnnotation(case_id, reviewer) {
            return _ROIsAnnotationAction(case_id, reviewer, 'START');
        }

        function closeROIsAnnotation(case_id, reviewer) {
            return _ROIsAnnotationAction(case_id, reviewer, 'FINISH');
        }

        function _clinicalAnnotationAction(case_id, reviewer, rois_review_id, action) {
            return $http.put(
                '/api/clinical_annotation/' + case_id + '/' + reviewer + '/' + rois_review_id + '/',
                {action: action}
            )
        }

        function startClinicalAnnotation(case_id, reviewer, rois_review_id) {
            return _clinicalAnnotationAction(case_id, reviewer, rois_review_id, 'START');
        }

        function closeClinicalAnnotation(case_id, reviewer, rois_review_id) {
            return _clinicalAnnotationAction(case_id, reviewer, rois_review_id, 'FINISH');
        }
    }

    ROIsAnnotationStepService.$inject = ['$http'];

    function ROIsAnnotationStepService($http) {
        var ROIsAnnotationStepService = {
            get: get,
            getDetails: getDetails,
            startAnnotationStep: startAnnotationStep,
            closeAnnotationStep: closeAnnotationStep
        };

        return ROIsAnnotationStepService;

        function get(case_id) {
            return $http.get('/api/worklist/' + case_id + '/');
        }

        function getDetails(case_id, reviewer, slide_id) {
            return $http.get('/api/rois_annotations/' + case_id + '/' + reviewer + '/' + slide_id +'/');
        }

        function _annotationStepAction(case_id, reviewer, slide_id, action) {
            var params = {action: action};
            return $http.put(
                '/api/rois_annotations/' + case_id + '/' + reviewer + '/' + slide_id + '/',
                params
            );
        }

        function startAnnotationStep(case_id, reviewer, slide_id) {
            return _annotationStepAction(case_id, reviewer, slide_id, 'START');
        }

        function closeAnnotationStep(case_id, reviewer, slide_id) {
            return _annotationStepAction(case_id, reviewer, slide_id, 'FINISH');
        }
    }

    ClinicalAnnotationStepService.$inject = ['$http'];

    function ClinicalAnnotationStepService($http) {
        var ClinicalAnnotationStepService = {
            get: get,
            getDetails: getDetails,
            startAnnotationStep: startAnnotationStep,
            closeAnnotationStep: closeAnnotationStep
        };

        return ClinicalAnnotationStepService;

        function get(case_id, rois_annotation_id) {
            return $http.get('/api/worklist/' + case_id + '/' + rois_annotation_id + '/');
        }

        function getDetails(case_id, reviewer, rois_annotation_id, slide_id) {
            return $http.get('/api/clinical_annotations/' + case_id + '/' + reviewer + '/' +
                rois_annotation_id + '/' + slide_id + '/');
        }

        function _annotationStepAction(case_id, reviewer, rois_annotation_id, slide_id, action, notes) {
            var params = {action: action};
            if (typeof notes !== 'undefined') {
                params.notes = notes;
            }
            return $http.put(
                '/api/clinical_annotations/' + case_id + '/' + reviewer + '/' +
                rois_annotation_id + '/' + slide_id + '/',
                params
            );
        }

        function startAnnotationStep(case_id, reviewer, rois_annotation_id, slide_id) {
            return _annotationStepAction(case_id, reviewer, rois_annotation_id, slide_id, 'START');
        }

        function closeAnnotationStep(case_id, reviewer, rois_annotation_id, slide_id) {
            return _annotationStepAction(case_id, reviewer, rois_annotation_id, slide_id, 'FINISH');
        }
    }
})();