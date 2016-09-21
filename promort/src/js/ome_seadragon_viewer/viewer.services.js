(function () {
    'use strict';

    angular
        .module('promort.viewer.services')
        .factory('ViewerService', ViewerService);

    ViewerService.$inject = ['$http'];

    function ViewerService($http) {
        var ViewerService = {
            getOMEBaseURLs: getOMEBaseURLs,
            getSlideInfo: getSlideInfo
        };

        return ViewerService;

        function getOMEBaseURLs() {
            return $http.get('api/utils/omeseadragon_base_urls/');
        }

        function getSlideInfo(slide_id) {
            return $http.get('api/slides/' + slide_id + '/');
        }
    }
})();