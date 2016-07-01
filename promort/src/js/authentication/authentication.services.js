(function() {
    'use strict';

    angular
        .module('promort.authentication.services')
        .factory('Authentication', Authentication);

    Authentication.$inject = ['$cookies', '$http'];

    function Authentication($cookies, $http) {
        var Authentication = {
            login: login,
            logout: logout,
            getAuthenticatedAccount: getAuthenticatedAccount,
            isAuthenticated: isAuthenticated,
            setAuthenticatedAccount: setAuthenticatedAccount,
            unauthenticate: unauthenticate
        };

        return Authentication;

        function login(username, password) {
            return $http.post('/api/auth/login/', {
                username: username, password: password
            }).then(loginSuccessFn, loginErrorFn);
            
            function loginSuccessFn(data, status, header, config) {
                Authentication.setAuthenticatedAccount(data.data);
                
                window.location = '/';
            }
            
            function loginErrorFn(data, status, headers, config) {
                console.error('Unable to complete login request');
            }
        }
        
        function logout() {
            console.log('Logout called');
            return $http.post('/api/auth/logout/')
                .then(logoutSuccessFn, logoutErrorFn);
            
            function logoutSuccessFn(data, status, headers, config) {
                Authentication.unauthenticate();
                
                window.location = '/login';
            }
            
            function logoutErrorFn(data, status, headers, config) {
                console.error('Error during logout operation');
            }
        }

        function getAuthenticatedAccount() {
            if (!$cookies.get('authenticatedAccount')) {
                return ;
            }
            return $cookies.get('authenticatedAccount');
        }

        function isAuthenticated() {
            return !!$cookies.get('authenticatedAccount');
        }

        function setAuthenticatedAccount(account) {
            $cookies.putObject('authenticatedAccount', account);
        }

        function unauthenticate() {
            $cookies.remove('authenticatedAccount');
        }
    }
})();