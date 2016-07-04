(function () {
    'use strict';

    angular
        .module('promort.worklist.services')
        .factory('WorkListService', WorkListService)
        .factory('ReviewStepsService', ReviewStepsService);

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

    ReviewStepsService.$inject = ['$http'];

    function ReviewStepsService($http) {
        var ReviewStepsService = {
            get: get,
            startReviewStep: startReviewStep,
            closeReviewStep: closeReviewStep
        };

        return ReviewStepsService;

        function get(case_id) {
            return $http.get('/api/worklist/' + case_id + '/');
        }

        function _reviewStepAction(case_id, review_type, slide_id, action) {
            return $http.put(
                '/api/reviews/' + case_id + '/' + review_type.toLowerCase() + '/' + slide_id + '/',
                {action: action}
            );
        }

        function startReviewStep(case_id, review_type, slide_id) {
            return _reviewStepAction(case_id, review_type, slide_id, 'START');
        }

        function closeReviewStep(case_id, review_type, slide_id) {
            return _reviewStepAction(case_id, review_type, slide_id, 'FINISH');
        }
    }
})();