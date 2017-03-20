(function () {
    'use strict';

    angular
        .module('promort.routes')
        .config(config);

    config.$inject = ['$routeProvider'];

    function config($routeProvider) {
        $routeProvider
            // login template
            .when('/login', {
                controller: 'LoginController',
                controllerAs: 'vm',
                templateUrl: '/static/templates/authentication/login.html'
            })
            // user worklist template
            .when('/worklist', {
                controller: 'WorkListController',
                controllerAs: 'wlc',
                templateUrl: '/static/templates/worklist/pending_reviews.html'
            })
            // ROIs annotation steps template
            .when('/worklist/:case', {
                controller: 'ROIsAnnotationController',
                controllerAs: 'rc',
                templateUrl: '/static/templates/worklist/rois_annotation_steps.html'
            })
            // clinical annotation steps template
            .when('/worklist/:case/:rois_annotation_step', {
                controller: 'ClinicalAnnotationController',
                controllerAs: 'cc',
                templateUrl: '/static/templates/worklist/clinical_annotation_steps.html'
            })
            // slide quality control
            .when('/worklist/:case/:slide/:annotation_step/quality_control', {
                controller: 'QualityControlController',
                controllerAs: 'qcc',
                templateUrl: '/static/templates/slide_review/quality_control.html'
            })
            // ROIs manager
            .when('/worklist/:case/:slide/:annotation_step/rois_manager', {
                controller: 'ROIsManagerController',
                controllerAs: 'rmc',
                templateUrl: '/static/templates/rois_manager/manager.html'
            })
            // clinical annotations manager
            .when('/worklist/:case/:slide/:annotation_step/:clinical_annotation_step/annotations_manager', {
                controller: 'ClinicalAnnotationsManagerController',
                controllerAs: 'cmc',
                templateUrl: '/static/templates/clinical_annotations_manager/manager.html'
            })
            // homepage
            .when('/', {
                controller: 'AuthenticationController',
                controllerAs: 'ac',
                templateUrl: '/static/templates/index/index.html'
            })
            // page not found
            .when('/404', {
                controller: 'AuthenticationController',
                controllerAs: 'ac',
                templateUrl: '/static/templates/404/not_found.html'
            })
            // no match
            .otherwise('/404');
    }
})();