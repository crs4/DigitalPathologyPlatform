(function () {
    'use strict';

    angular
        .module('promort.worklist.services')
        .factory('WorkListService', WorkListService);

    WorkListService.$inject = ['$http'];

    function WorkListService($http) {
        var WorkListService = {
            get: get
        };

        return WorkListService;

        function get() {
            return $http.get('/api/worklist/');
        }
    }
})();