(function () {
    'use strict';
    
    angular
        .module('promort.worklist.controllers')
        .controller('WorkListController', WorkListController)
        .controller('ReviewController', ReviewController);
    
    WorkListController.$inject = ['$scope', 'WorkListService'];
    
    function WorkListController($scope, WorkListService) {
        var vm = this;
        vm.pendingReviews = [];
        vm.reviewInProgress = reviewInProgress;
        vm.checkPendingReviews = checkPendingReviews;
        vm.getReviewLink = getReviewLink;
        vm.openReview = openReview;
        vm.closeReview = closeReview;
        
        activate();
        
        function activate() {
            WorkListService.get().then(workListSuccessFn, workListErrorFn);
            
            function workListSuccessFn(data, status, headers, config) {
                vm.pendingReviews = data.data;
            }
            
            function workListErrorFn(data, status, headers, config) {
                console.error(data.error);
            }
        }

        function reviewInProgress(review) {
            if (review.start_date && !review.completion_date ) {
                return true;
            }
            return false;
        }

        function checkPendingReviews() {
            for (var i in vm.pendingReviews) {
                var r = vm.pendingReviews[i];
                if (r.start_date && !r.completion_date) {
                    return true;
                }
            }
            return false;
        }
        
        function getReviewLink(review) {
            if (vm.checkPendingReviews()) {
                if (!vm.reviewInProgress(review)) {
                    return '';
                }
            }
            return 'worklist/' + review.case;
        }
        
        function openReview(review) {
            console.info('Starting review for case ' + review.case);
            WorkListService.startReview(review.case, review.type);
        }

        function closeReview(review) {
            WorkListService.closeReview(review.case, review.type);
        }
    }
    
    ReviewController.$inject = ['$scope', '$routeParams', 'ReviewStepsService'];

    function ReviewController($scope, $routeParams, ReviewStepsService) {
        var vm = this;
        vm.reviewSteps = [];
        vm.case_id = undefined;
        vm.reviewStepPending = reviewStepPending;
        vm.reviewStepInProgress = reviewStepInProgress;
        vm.reviewStepCompleted = reviewStepCompleted;
        vm.getReviewStepLink = getReviewStepLink;

        activate();

        function activate() {
            vm.case_id = $routeParams.case;
            ReviewStepsService.get(vm.case_id)
                .then(ReviewStepsSuccessFn, ReviewStepsErrorFn);

            function ReviewStepsSuccessFn(data, status, headers, config) {
                vm.reviewSteps = data.data;
            }

            function ReviewStepsErrorFn(data, status, headers, config) {
                console.error(data.error);
            }
        }

        function reviewStepPending(reviewStep) {
            return (!reviewStep.start_date && !reviewStep.completion_date);
        }

        function reviewStepInProgress(reviewStep) {
            return (reviewStep.start_date && !reviewStep.completion_date);
        }

        function reviewStepCompleted(reviewStep) {
            return (reviewStep.start_date && reviewStep.completion_date);
        }

        function getReviewStepLink(reviewStep) {
            if (reviewStep.review_type === 'REVIEW_1') {
                return 'worklist/' + vm.case_id + '/' + reviewStep.slide + '/quality_check';
            } else {
                return 'worklist/' + vm.case_id + '/' + reviewStep.slide + '/annotations';
            }
        }
    }
})();