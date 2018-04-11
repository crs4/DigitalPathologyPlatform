(function() {
    'use strict';
    
    angular
        .module('promort.layout.controllers')
        .controller('NavbarController', NavbarController);
    
    NavbarController.$inject = ['$scope', '$log', 'Authentication'];
    
    function NavbarController($scope, $log, Authentication) {
        var vm = this;

        vm.logout = logout;
        
        function logout() {
            Authentication.logout();
        }
    }
})();