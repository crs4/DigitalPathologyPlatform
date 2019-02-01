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
        .module('promort.authentication.services')
        .factory('Authentication', Authentication);

    Authentication.$inject = ['$cookies', '$http', '$log', 'ngDialog'];

    function Authentication($cookies, $http, $log, ngDialog) {

        var Authentication = {
            login: login,
            logout: logout,
            checkUser: checkUser,
            isAuthenticated: isAuthenticated,
            setAuthenticationCookie: setAuthenticationCookie,
            unauthenticate: unauthenticate,
            getCurrentUser: getCurrentUser
        };

        return Authentication;

        function login(username, password) {
            return $http.post('/api/auth/login/', {
                username: username, password: password
            }).then(loginSuccessFn, loginErrorFn);
            
            function loginSuccessFn(data, status, header, config) {
                Authentication.setAuthenticationCookie(username);

                window.location = '/worklist';
            }
            
            function loginErrorFn(data, status, headers, config) {
                console.error('Unable to complete login request');

                ngDialog.open({
                    template: '/static/templates/authentication/authentication_error.html'
                });
            }
        }
        
        function logout() {
            $log.debug('Logout called');
            return $http.post('/api/auth/logout/')
                .then(logoutSuccessFn, logoutErrorFn);
            
            function logoutSuccessFn(data, status, headers, config) {
                Authentication.unauthenticate();

                window.location = '/';
            }
            
            function logoutErrorFn(data, status, headers, config) {
                console.error('Error during logout operation');
            }
        }

        function checkUser() {
            return $http.get('api/auth/check/')
                .then(checkSuccessFn, checkErrorFn);

            function checkSuccessFn(data) {
                Authentication.setAuthenticationCookie(data.data.username);
            }

            function checkErrorFn(data) {
                $log.debug('No active session found on backend');
            }
        }

        function isAuthenticated() {
            return !!$cookies.get('promortUserAuthenticated');
        }

        function setAuthenticationCookie(username) {
            $cookies.putObject('promortUserAuthenticated', true);
            $cookies.putObject('currentUser', username);
        }

        function unauthenticate() {
            $cookies.remove('promortUserAuthenticated');
            $cookies.remove('currentUser');
        }

        function getCurrentUser() {
            return $cookies.getObject('currentUser');
        }
    }
})();