(function() {
    'use strict';
    
    angular
        .module('promort.user_report.controllers')
        .controller('UserReportController', UserReportController);

    UserReportController.$inject = ['$scope', 'UserReportService'];

    function UserReportController($scope, UserReportService) {
        var vm = this;
        vm.sendReport = sendReport;

        vm.report = {};


        function sendReport() {
            UserReportService.send(vm.report.subject, vm.report.message,
                window.location.href, navigator.userAgent)
                .then(sendUserReportSuccessFn, sendUserReportErrorFn);

            function sendUserReportSuccessFn(response) {
                vm.report = {};
                $scope.closeThisDialog();
            }

            function sendUserReportErrorFn(response) {
                console.error('Error sending report!');
                $scope.closeThisDialog();
            }
        }
    }
})();