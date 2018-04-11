(function() {
    'use strict';
    
    angular
        .module('promort.window_manager.controllers')
        .controller('WindowEventsController', WindowEventsController);
    
    WindowEventsController.$inject = ['$scope', '$log', 'Authentication'];
    
    function WindowEventsController($scope, $log, Authentication) {

        activate();
        
        function activate() {
            Authentication.checkUser();
        }
    }
})();