(function () {
    'use strict';
    
    angular
        .module('promort.worklist.controllers')
        .controller('WorkListController', WorkListController);
    
    WorkListController.$inject = ['$scope', 'WorkListService'];
    
    function WorkListController($scope, WorkListService) {
        var vm = this;
        vm.pendingReviews = [];
        vm.dummyString  = 'Hey there, I am just a stupid string';
        vm.reviewInProgress = reviewInProgress;
        vm.checkPendingReviews = checkPendingReviews;
        vm.getReviewLink = getReviewLink;
        
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
    }
})();