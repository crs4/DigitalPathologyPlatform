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