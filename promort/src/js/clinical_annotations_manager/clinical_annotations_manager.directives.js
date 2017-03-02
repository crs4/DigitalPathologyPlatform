(function () {
    'use strict';

    angular
        .module('promort.clinical_annotations_manager.directives')
        .directive('newSliceAnnotationForm', newSliceAnnotationForm)
        .directive('newSliceAnnotationButtons', newSliceAnnotationButtons)
        .directive('showSliceAnnotationForm', showSliceAnnotationForm)
        .directive('showSliceAnnotationButtons', showSliceAnnotationButtons)
        .directive('newCoreAnnotationForm', newCoreAnnotationForm)
        .directive('newCoreAnnotationButtons', newCoreAnnotationButtons)
        .directive('showCoreAnnotationForm', showCoreAnnotationForm)
        .directive('showCoreAnnotationButtons', showCoreAnnotationButtons);

    function newSliceAnnotationForm() {
        var directive = {
            replace: true,
            restrict: 'E',
            templateUrl: '/static/templates/clinical_annotations_manager/slice_annotation.html',
            controller: 'NewSliceAnnotationController',
            controllerAs: 'cmCtrl'
        };
        return directive;
    }

    function newSliceAnnotationButtons() {
        var directive = {
            replace: true,
            restrict: 'E',
            templateUrl: '/static/templates/clinical_annotations_manager/buttons_ctrl_group.html',
            controller: 'NewSliceAnnotationController',
            controllerAs: 'cmCtrl'
        };
        return directive;
    }

    function showSliceAnnotationForm() {
        var directive = {
            replace: true,
            restricted: 'E',
            templateUrl: '/static/templates/clinical_annotations_manager/slice_annotation.html',
            controller: 'ShowSliceAnnotationController',
            controllerAs: 'cmCtrl'
        };
        return directive;
    }

    function showSliceAnnotationButtons() {
        var directive = {
            replace: true,
            restrict: 'E',
            templateUrl: '/static/templates/clinical_annotations_manager/buttons_ctrl_group.html',
            controller: 'ShowSliceAnnotationController',
            controllerAs: 'cmCtrl'
        };
        return directive;
    }

    function newCoreAnnotationForm() {
        var directive = {
            replace: true,
            restrict: 'E',
            templateUrl: '/static/templates/clinical_annotations_manager/core_annotation.html',
            controller: 'NewCoreAnnotationController',
            controllerAs: 'cmCtrl'
        };
        return directive;
    }

    function newCoreAnnotationButtons() {
        var directive = {
            replace: true,
            restrict: 'E',
            templateUrl: '/static/templates/clinical_annotations_manager/buttons_ctrl_group.html',
            controller: 'NewCoreAnnotationController',
            controllerAs: 'cmCtrl'
        };
        return directive;
    }

    function showCoreAnnotationForm() {
        var directive = {
            replace: true,
            restrict: 'E',
            templateUrl: '/static/templates/clinical_annotations_manager/core_annotation.html',
            controller: 'ShowCoreAnnotationController',
            controllerAs: 'cmCtrl'
        };
        return directive;
    }

    function showCoreAnnotationButtons() {
        var directive = {
            replace: true,
            restrict: 'E',
            templateUrl: '/static/templates/clinical_annotations_manager/buttons_ctrl_group.html',
            controller: 'ShowCoreAnnotationController',
            controllerAs: 'cmCtrl'
        };
        return directive;
    }
})();