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
        .module('promort.worklist.services')
        .factory('WorkListService', WorkListService)
        .factory('ROIsAnnotationStepService', ROIsAnnotationStepService)
        .factory('ClinicalAnnotationStepService', ClinicalAnnotationStepService);

    WorkListService.$inject = ['$http', '$log'];

    function WorkListService($http, $log) {
        var WorkListService = {
            get: get,
            startROIsAnnotation: startROIsAnnotation,
            closeROIsAnnotation: closeROIsAnnotation,
            startClinicalAnnotation: startClinicalAnnotation,
            closeClinicalAnnotation: closeClinicalAnnotation,
            startQuestionnaireRequest: startQuestionnaireRequest,
            closeQuestionnaireRequest: closeQuestionnaireRequest
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

        function _questionnaireRequestAction(label, action) {
            return $http.put(
                '/api/questionnaire_requests/' + label + '/',
                {action: action}
            )
        }

        function startQuestionnaireRequest(label) {
            return _questionnaireRequestAction(label, 'START');
        }

        function closeQuestionnaireRequest(label) {
            return _questionnaireRequestAction(label, 'FINISH');
        }
    }

    ROIsAnnotationStepService.$inject = ['$http', '$log'];

    function ROIsAnnotationStepService($http, $log) {
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

    ClinicalAnnotationStepService.$inject = ['$http', '$log'];

    function ClinicalAnnotationStepService($http, $log) {
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