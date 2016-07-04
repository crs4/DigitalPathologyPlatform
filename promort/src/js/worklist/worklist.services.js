(function () {
    'use strict';

    angular
        .module('promort.worklist.services')
        .factory('WorkListService', WorkListService);

    WorkListService.$inject = ['$http'];

    function WorkListService($http) {
        var WorkListService = {
            get: get,
            startReview: startReview,
            closeReview: closeReview
        };

        return WorkListService;

        function get() {
            return $http.get('/api/worklist/');
        }

        function _reviewAction(case_id, review_type, action) {
            return $http.put(
                '/api/reviews/' + case_id + '/' + review_type.toLowerCase() + '/',
                {action: action}
            );
        }

        function startReview(case_id, review_type) {
            return _reviewAction(case_id, review_type, 'START');
        }

        function closeReview(case_id, review_type) {
            return _reviewAction(case_id, review_type, 'FINISH');
        }
    }

    }
})();