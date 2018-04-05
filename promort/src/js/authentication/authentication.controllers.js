(function() {
    'use strict';
    
    angular
        .module('promort.authentication.controllers')
        .controller('LoginController', LoginController)
        .controller('AuthenticationController', AuthenticationController);
    
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
})();