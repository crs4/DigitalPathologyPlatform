(function () {
    'use strict';
    
    angular
        .module('promort.slides_manager.services')
        .factory('SlideService', SlideService)
        .factory('QualityControlService', QualityControlService);

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

        function get(slide_id) {
            return $http.get('api/slides/' + slide_id + '/quality_control/');
        }
        
        function fetchNotAdequacyReasons() {
            return $http.get('api/utils/slide_not_adequacy_reasons/');
        }

        function create(slide_id, adequacy, not_adequancy_reason, notes) {
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
            return $http.post('api/slides/' + slide_id + '/quality_control/', params);
        }
    }
})();