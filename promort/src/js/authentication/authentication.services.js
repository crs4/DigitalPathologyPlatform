(function() {
    'use strict';

    angular
        .module('promort.authentication.services')
        .factory('Authentication', Authentication);

    Authentication.$inject = ['$cookies', '$http', 'ngDialog'];

    function Authentication($cookies, $http, ngDialog) {
        var Authentication = {
            login: login,
            logout: logout,
            checkUser: checkUser,
            isAuthenticated: isAuthenticated,
            setAuthenticationCookie: setAuthenticationCookie,
            unauthenticate: unauthenticate
        };

        return Authentication;

        function login(username, password) {
            return $http.post('/api/auth/login/', {
                username: username, password: password
            }).then(loginSuccessFn, loginErrorFn);
            
            function loginSuccessFn(data, status, header, config) {
                Authentication.setAuthenticationCookie();
                
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
            console.log('Logout called');
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
                console.log('Active session found on backed');
                Authentication.setAuthenticationCookie();
            }

            function checkErrorFn(data) {
                console.log('No active session found on backend');
            }
        }

        function isAuthenticated() {
            return !!$cookies.get('promortUserAuthenticated');
        }

        function setAuthenticationCookie() {
            $cookies.putObject('promortUserAuthenticated', true);
        }

        function unauthenticate() {
            $cookies.remove('promortUserAuthenticated');
        }
    }
})();