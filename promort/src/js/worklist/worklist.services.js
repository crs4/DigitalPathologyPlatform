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

        function _ROIsAnnotationAction(label, action) {
            return $http.put(
                '/api/rois_annotations/annotations/' + label + '/',
                {action: action}
            );
        }

        function startROIsAnnotation(label) {
            return _ROIsAnnotationAction(label, 'START');
        }

        function closeROIsAnnotation(label) {
            return _ROIsAnnotationAction(label, 'FINISH');
        }

        function _clinicalAnnotationAction(label, action) {
            return $http.put(
                '/api/clinical_annotations/annotations/' + label + '/',
                {action: action}
            )
        }

        function startClinicalAnnotation(label) {
            return _clinicalAnnotationAction(label, 'START');
        }

        function closeClinicalAnnotation(label) {
            return _clinicalAnnotationAction(label, 'FINISH');
        }
    }

    ROIsAnnotationStepService.$inject = ['$http'];

    function ROIsAnnotationStepService($http) {
        var ROIsAnnotationStepService = {
            get: get,
            getDetails: getDetails,
            startAnnotationStep: startAnnotationStep,
            closeAnnotationStep: closeAnnotationStep,
            startAndCloseAnnotationStep: startAndCloseAnnotationStep,
            startAndCloseClinicalAnnotationSteps: startAndCloseClinicalAnnotationSteps
        };

        return ROIsAnnotationStepService;

        function get(annotation_label) {
            return $http.get('/api/worklist/rois_annotations/' + annotation_label + '/');
        }

        function getDetails(label) {
            return $http.get('/api/rois_annotations/steps/' + label +'/');
        }

        function _annotationStepAction(label, action) {
            var params = {action: action};
            return $http.put(
                '/api/rois_annotations/steps/' + label + '/',
                params
            );
        }

        function startAnnotationStep(label) {
            return _annotationStepAction(label, 'START');
        }

        function closeAnnotationStep(label) {
            return _annotationStepAction(label, 'FINISH');
        }

        function startAndCloseAnnotationStep(label) {
            return _annotationStepAction(label, 'START_AND_FINISH')
        }

        function _relatedClinicalAnnotationStepsAction(annotation_step_label, action, notes) {
            var params = {
                action: action,
                notes: notes
            };
            return $http.put(
                'api/rois_annotation_steps/' + annotation_step_label + '/clinical_annotation_steps/',
                params
            );
        }

        function startAndCloseClinicalAnnotationSteps(annotation_step_label, notes) {
            return _relatedClinicalAnnotationStepsAction(annotation_step_label,
                'START_AND_FINISH', notes);
        }
    }

    ClinicalAnnotationStepService.$inject = ['$http'];

    function ClinicalAnnotationStepService($http) {
        var ClinicalAnnotationStepService = {
            get: get,
            getDetails: getDetails,
            startAnnotationStep: startAnnotationStep,
            closeAnnotationStep: closeAnnotationStep,
            startAndCloseAnnotationStep: startAndCloseAnnotationStep
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

        function closeAnnotationStep(case_id, reviewer, rois_annotation_id, slide_id, notes) {
            return _annotationStepAction(case_id, reviewer, rois_annotation_id, slide_id,
                'FINISH', notes);
        }

        function startAndCloseAnnotationStep(case_id, reviewer, rois_annotation_id, slide_id, notes) {
            return _annotationStepAction(case_id, reviewer, rois_annotation_id, slide_id,
                'START_AND_FINISH', notes);
        }
    }
})();