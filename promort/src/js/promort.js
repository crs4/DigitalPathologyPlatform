(function() {
    'use strict';
    
    angular
        .module('promort', [
            'promort.config',
            'promort.routes',
            'promort.authentication',
            'promort.layout'
        ])
        .run(run);

    run.$inject = ['$http'];

    function run($http) {
        $http.defaults.xsrfHeaderName = 'X-CSRFToken';
        $http.defaults.xsrfCookieName = 'csrftoken';
    }

    angular
        .module('promort.config', []);

    angular
        .module('promort.routes', ['ngRoute']);
})();