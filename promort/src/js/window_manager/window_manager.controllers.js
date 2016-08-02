(function() {
    'use strict';
    
    angular
        .module('promort.window_manager.controllers')
        .controller('WindowEventsController', WindowEventsController);
    
    WindowEventsController.$inject = ['$scope', 'Authentication'];
    
    function WindowEventsController($scope, Authentication) {

        activate();
        
        function activate() {
            Authentication.checkUser();
        }
    }
})();