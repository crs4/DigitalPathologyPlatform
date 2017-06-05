(function () {
    'use strict';
    
    angular
        .module('promort.slides_manager.services')
        .factory('CurrentSlideDetailsService', CurrentSlideDetailsService)
        .factory('SlideService', SlideService)
        .factory('QualityControlService', QualityControlService);

    CurrentSlideDetailsService.$inject = ['$http'];

    function CurrentSlideDetailsService($http) {
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
            console.log('REGISTERING SLIDE ' + slide_id + ' FOR CASE ' + case_id);
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

    SlideService.$inject = ['$http'];

    function SlideService($http) {
        var SlideService = {
            get: get,
            fetchStainings: fetchStainings,
            updateSliceStaining: updateSliceStaining
        };

        return SlideService;

        function get(slide_id) {
            return $http.get('api/slides/' + slide_id + '/');
        }

        function fetchStainings() {
            return $http.get('api/utils/slide_stainings/');
        }

        function updateSliceStaining(slide_id, staining) {
            var params = {
                staining: staining
            };
            return $http.put('api/slides/' + slide_id + '/', params);
        }
    }

    QualityControlService.$inject = ['$http'];

    function QualityControlService($http) {
        var QualityControlService = {
            get: get,
            create: create,
            fetchNotAdequacyReasons: fetchNotAdequacyReasons
        };

        return QualityControlService;

        function get(annotation_step_label) {
            return $http.get('api/rois_annotations/steps/' + annotation_step_label + '/quality_control/');
        }
        
        function fetchNotAdequacyReasons() {
            return $http.get('api/utils/slide_not_adequacy_reasons/');
        }

        function create(annotation_step_label, adequacy, not_adequancy_reason, notes) {
            var params = {
                adequate_slide: adequacy
            };
            if (not_adequancy_reason) {
                params.not_adequacy_reason = not_adequancy_reason;
            }
            if (notes) {
                params.notes = notes;
            }
            console.log(params);
            return $http.post('api/rois_annotations/steps/' + annotation_step_label + '/quality_control/',
                params);
        }
    }
})();