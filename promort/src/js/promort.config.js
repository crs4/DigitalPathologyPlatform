(function() {
    'use strict';

    angular
        .module('promort.config')
        .config(config);

    config.$inject = ['$locationProvider'];

    function config($locationProvider) {
        $locationProvider.html5Mode(true);
        $locationProvider.hashPrefix('!');
    }
})();