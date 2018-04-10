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