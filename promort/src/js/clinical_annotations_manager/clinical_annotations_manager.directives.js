(function () {
    'use strict';

    angular
        .module('promort.clinical_annotations_manager.directives')
        .directive('newSliceAnnotationForm', newSliceAnnotationForm)
        .directive('newSliceAnnotationButtons', newSliceAnnotationButtons)
        .directive('showSliceAnnotationForm', showSliceAnnotationForm)
        .directive('showSliceAnnotationButtons', showSliceAnnotationButtons);

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
        }
        return directive;
    }
})();