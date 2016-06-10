(function() {
    'use strict';

    angular
        .module('promort.authentication', [
            'promort.authentication.services',
            'promort.authentication.controllers'
        ]);

    angular
        .module('promort.authentication.services', ['ngCookies']);

    angular
        .module('promort.authentication.controllers', []);
})();