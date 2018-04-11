(function () {
    'use strict';
    
    angular
        .module('promort.slides_manager.services')
        .factory('CurrentSlideDetailsService', CurrentSlideDetailsService)
        .factory('SlideService', SlideService)
        .factory('SlideEvaluationService', SlideEvaluationService);

    CurrentSlideDetailsService.$inject = ['$http', '$log'];

    function CurrentSlideDetailsService($http, $log) {
        var slideID = undefined;
        var caseID = undefined;

        var CurrentSlideDetailsService = {
            getSlideByAnnotationStep: getSlideByAnnotationStep,
            registerCurrentSlide: registerCurrentSlide,
            getSlideId: getSlideId,
            getCaseId: getCaseId
        };

        return CurrentSlideDetailsService;

        function getSlideByAnnotationStep(annotation_step_label, annotation_type) {
            slideID = undefined;
            caseID = undefined;

            switch (annotation_type) {
                case 'ROIS_ANNOTATION':
                    return $http.get('api/rois_annotations/steps/' + annotation_step_label + '/');
                case 'CLINICAL_ANNOTATION':
                    return $http.get('api/clinical_annotations/steps/' + annotation_step_label + '/');
            }
        }

        function registerCurrentSlide(slide_id, case_id) {
            $log.debug('REGISTERING SLIDE ' + slide_id + ' FOR CASE ' + case_id);
            slideID = slide_id;
            caseID = case_id;
        }

        function getSlideId() {
            return slideID;
        }

        function getCaseId() {
            return caseID;
        }
    }

    SlideService.$inject = ['$http', '$log'];

    function SlideService($http, $log) {
        var SlideService = {
            get: get
        };

        return SlideService;

        function get(slide_id) {
            return $http.get('api/slides/' + slide_id + '/');
        }
    }

    SlideEvaluationService.$inject = ['$http', '$log'];

    function SlideEvaluationService($http, $log) {
        var SlideEvaluationService = {
            get: get,
            create: create,
            fetchStainings: fetchStainings,
            fetchNotAdequacyReasons: fetchNotAdequacyReasons
        };

        return SlideEvaluationService;

        function get(annotation_step_label) {
            return $http.get('api/rois_annotations/steps/' + annotation_step_label + '/slide_evaluation/');
        }

        function fetchStainings() {
            return $http.get('api/utils/slide_stainings/');
        }
        
        function fetchNotAdequacyReasons() {
            return $http.get('api/utils/slide_not_adequacy_reasons/');
        }

        function create(annotation_step_label, staining, adequacy, not_adequancy_reason, notes) {
            var params = {
                adequate_slide: adequacy,
                staining: staining
            };
            if (not_adequancy_reason) {
                params.not_adequacy_reason = not_adequancy_reason;
            }
            if (notes) {
                params.notes = notes;
            }
            $log.debug(params);
            return $http.post('api/rois_annotations/steps/' + annotation_step_label + '/slide_evaluation/',
                params);
        }
    }
})();