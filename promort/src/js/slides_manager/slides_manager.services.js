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
        .module('promort.slides_manager.services')
        .factory('CurrentSlideDetailsService', CurrentSlideDetailsService)
        .factory('SlideService', SlideService)
        .factory('SlidesSetService', SlidesSetService)
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

    SlidesSetService.$inject = ['$http', '$log'];

    function SlidesSetService($http, $log) {
        var SlidesSetService = {
            get: get
        };

        return SlidesSetService;

        function get(slides_set_id) {
            return $http.get('api/slides_set/' + slides_set_id + '/');
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