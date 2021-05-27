/*
 * Copyright (c) 2019, CRS4
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of
 * this software and associated documentation files (the "Software"), to deal in
 * the Software without restriction, including without limitation the rights to
 * use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
 * the Software, and to permit persons to whom the Software is furnished to do so,
 * subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
 * FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
 * COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
 * IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
 * CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */

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
            // password change template
            .when('/change_password', {
                controller: 'ChangePasswordController',
                controllerAs: 'cpc',
                templateUrl: '/static/templates/authentication/change_password.html'
            })
            // shared datasets template
            .when('/datasets', {
                controller: 'SharedDatasetsController',
                controllerAs: 'sdc',
                templateUrl: '/static/templates/shared_datasets/datasets_index.html'
            })
            // shared dataset items template
            .when('/datasets/:dataset_id', {
                controller: 'SharedDatasetItemsController',
                controllerAs: 'sdic',
                templateUrl: '/static/templates/shared_datasets/dataset_details.html'
            })
            // user worklist template
            .when('/worklist', {
                controller: 'WorkListController',
                controllerAs: 'wlc',
                templateUrl: '/static/templates/worklist/pending_reviews.html'
            })
            // ROIs annotation steps template
            .when('/worklist/rois_annotations/:label', {
                controller: 'ROIsAnnotationController',
                controllerAs: 'rc',
                templateUrl: '/static/templates/worklist/rois_annotation_steps.html'
            })
            // clinical annotation steps template
            .when('/worklist/clinical_annotations/:label', {
                controller: 'ClinicalAnnotationController',
                controllerAs: 'cc',
                templateUrl: '/static/templates/worklist/clinical_annotation_steps.html'
            })
            // slide quality control
            .when('/worklist/:label/quality_control', {
                controller: 'QualityControlController',
                controllerAs: 'qcc',
                templateUrl: '/static/templates/slide_review/quality_control.html'
            })
            // ROIs manager
            .when('/worklist/:label/rois_manager', {
                controller: 'ROIsManagerController',
                controllerAs: 'rmc',
                templateUrl: '/static/templates/rois_manager/manager.html'
            })
            // clinical annotations manager
            .when('/worklist/:label/annotations_manager', {
                controller: 'ClinicalAnnotationsManagerController',
                controllerAs: 'cmc',
                templateUrl: '/static/templates/clinical_annotations_manager/manager.html'
            })
            // questionnaire manager
            .when('/worklist/questionnaire_requests/:label', {
                controller: 'QuestionnaireRequestsManagerController',
                controllerAs: 'qrmc',
                templateUrl: '/static/templates/questionnaire_requests_manager/manager.html'
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