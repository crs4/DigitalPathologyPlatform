(function () {
    'use strict';

    angular
        .module('promort.routes')
        .config(config);

    config.$inject = ['$routeProvider'];

    function config($routeProvider) {
        $routeProvider
            .when('/login', {
                controller: 'LoginController',
                controllerAs: 'vm',
                templateUrl: '/static/templates/authentication/login.html'
            })
            .when('/worklist', {
                controller: 'WorkListController',
                controllerAs: 'wlc',
                templateUrl: '/static/templates/worklist/pending_reviews.html'
            })
            .otherwise('/');
    }
})();