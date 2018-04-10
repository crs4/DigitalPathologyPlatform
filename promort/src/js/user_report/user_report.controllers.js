(function() {
    'use strict';
    
    angular
        .module('promort.user_report.controllers')
        .controller('UserReportController', UserReportController);

    UserReportController.$inject = ['$scope', '$log', 'ngDialog', 'UserReportService'];

    function UserReportController($scope, $log, ngDialog, UserReportService) {
        var vm = this;
        vm.sendReport = sendReport;

        vm.report = {};


        function sendReport() {
            $scope.closeThisDialog();
            var dialog = ngDialog.open({
                template: '/static/templates/dialogs/report_sending.html',
                showClose: false,
                closeByEscape: false,
                closeByNavigation: false,
                closeByDocument: false
            });
            UserReportService.send(vm.report.subject, vm.report.message,
                window.location.href, navigator.userAgent)
                .then(sendUserReportSuccessFn, sendUserReportErrorFn);

            function sendUserReportSuccessFn(response) {
                vm.report = {};
                dialog.close();
            }

            function sendUserReportErrorFn(response) {
                $log.error('Error sending report!');
                dialog.close();
                ngDialog.open({
                    template: '/static/templates/dialogs/error_dialog.html'
                })
            }
        }
    }
})();