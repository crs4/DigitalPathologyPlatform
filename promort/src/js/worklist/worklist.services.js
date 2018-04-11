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
            startAndCloseClinicalAnnotationSteps: startAndCloseClinicalAnnotationSteps,
            resetAnnotationStep: resetAnnotationStep
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

        function resetAnnotationStep(label) {
            return $http.put('api/rois_annotations/steps/' + label + '/reset/');
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

        function get(annotation_label) {
            return $http.get('/api/worklist/clinical_annotations/' + annotation_label + '/');
        }

        function getDetails(annotation_step_label) {
            return $http.get('/api/clinical_annotations/steps/' + annotation_step_label + '/');
        }

        function _annotationStepAction(annotation_step_label, action, notes, rejected, rejection_reason) {
            var params = {action: action};
            if (typeof notes !== 'undefined') {
                params.notes = notes;
            }
            if (typeof rejected !== 'undefined') {
                params.rejected = rejected;
            }
            if (typeof rejection_reason !== 'undefined') {
                params.rejection_reason = rejection_reason
            }
            return $http.put(
                '/api/clinical_annotations/steps/' + annotation_step_label + '/',
                params
            );
        }

        function startAnnotationStep(annotation_step_label) {
            return _annotationStepAction(annotation_step_label, 'START');
        }

        function closeAnnotationStep(annotation_step_label, notes, rejected, rejection_reason) {
            return _annotationStepAction(annotation_step_label, 'FINISH', notes, rejected, rejection_reason);
        }

        function startAndCloseAnnotationStep(annotation_step_label, notes) {
            return _annotationStepAction(annotation_step_label, 'START_AND_FINISH', notes);
        }
    }
})();