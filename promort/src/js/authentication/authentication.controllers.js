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
        .module('promort.authentication.controllers')
        .controller('LoginController', LoginController)
        .controller('AuthenticationController', AuthenticationController)
        .controller('ChangePasswordController', ChangePasswordController);
    
    LoginController.$inject = ['$location', '$scope', '$log', 'Authentication'];
    
    function LoginController($location, $scope, $log, Authentication) {
        var vm = this;
        
        vm.login = login;
        
        activate();
        
        function activate() {
            if (Authentication.isAuthenticated()) {
                $location.url('/worklist');
            }
        }
        
        function login() {
            Authentication.login(vm.username, vm.password);
        }
    }

    AuthenticationController.$inject = ['$scope', '$log', 'Authentication'];

    function AuthenticationController($scope, $log, Authentication) {
        var vm = this;

        vm.isAuthenticated = isAuthenticated;

        function isAuthenticated() {
            return Authentication.isAuthenticated();
        }
    }

    ChangePasswordController.$inject = ['$scope', '$log', 'Authentication', 'ngDialog'];

    function ChangePasswordController($location, $log, Authentication, ngDialog) {
        var vm = this;

        vm.old_password = undefined;
        vm.new_password = undefined;
        vm.new_password_check = undefined;

        vm.newPasswordMatch = newPasswordMatch;
        vm.newPasswordMismatch = newPasswordMismatch;
        vm.checkPasswordLength = checkPasswordLength;
        vm.checkAgainstOldPassword = checkAgainstOldPassword;
        vm.passwordValid = passwordValid;
        vm.formValid = formValid;
        vm.formEmpty = formEmpty;
        vm.clearForm = clearForm;
        vm.changePassword = changePassword;

        function newPasswordMatch() {
            if(typeof vm.new_password !== 'undefined' && typeof vm.new_password_check !== 'undefined') {
                return vm.new_password === vm.new_password_check;
            } else {
                return false;
            }
        }

        function newPasswordMismatch() {
            if(typeof vm.new_password !== 'undefined' && typeof vm.new_password_check !== 'undefined') {
                return vm.new_password !== vm.new_password_check;
            } else {
                return false;
            }
        }

        function checkPasswordLength() {
            return (typeof vm.new_password !== 'undefined' && vm.new_password.length >= 8);
        }

        function checkAgainstOldPassword() {
            return (
                typeof vm.old_password !== 'undefined' &&
                typeof vm.new_password !== 'undefined' &&
                vm.old_password !== vm.new_password
            );
        }

        function passwordValid() {
            return (vm.checkPasswordLength() && vm.checkAgainstOldPassword());
        }

        function formValid() {
            return (typeof vm.old_password !== 'undefined' && vm.newPasswordMatch());
        }

        function formEmpty() {
            return (
                typeof vm.old_password === 'undefined' &&
                typeof vm.new_password === 'undefined' &&
                typeof vm.new_password_check === 'undefined'
            )
        }

        function clearForm() {
            vm.old_password = undefined;
            vm.new_password = undefined;
            vm.new_password_check = undefined;
        }

        function changePassword() {
            var dialog = undefined;
            dialog = ngDialog.open({
                template: '/static/templates/dialogs/updating_password.html',
                showClose: false,
                closeByEscape: false,
                closeByNavigation: false,
                closeByDocument: false
            });

            Authentication.changePassword(
                vm.old_password, vm.new_password
            ).then(changePasswordSuccessFn, changePasswordErrorFn);

            function changePasswordSuccessFn(response) {
                console.log('Password changed successfully! You need to login again');
                dialog.close();

                ngDialog.openConfirm({
                    template: '/static/templates/dialogs/password_update_success.html',
                    showClose: false,
                    closeByEscape: false,
                    closeByNavigation: false,
                    closeByDocument: false
                }).then(confirmFn);

                function confirmFn() {
                    Authentication.unauthenticate();
                    window.location = '/login';
                }
            }

            function changePasswordErrorFn(response) {
                dialog.close();
                if(response.data.status === 'password_check_failed') {
                    ngDialog.open({
                        template: '/static/templates/dialogs/old_password_check_error.html'
                    });
                    clearForm();
                } else {
                    ngDialog.open({
                        template: '/static/templates/dialogs/error_dialog.html'
                    });
                    console.log(response.data.status, response.data.message);
                }
            }
        }
    }
})();