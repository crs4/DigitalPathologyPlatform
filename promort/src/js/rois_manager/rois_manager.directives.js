(function () {
    'use strict';

    angular
        .module('promort.rois_manager.directives')
        .directive('newSliceForm', newSliceForm)
        .directive('newSliceButtons', newSliceButtons)
        .directive('newCoreForm', newCoreForm)
        .directive('newCoreButtons', newCoreButtons)
        .directive('newFocusRegionForm', newFocusRegionForm)
        .directive('newFocusRegionButtons', newFocusRegionButtons);

    function newSliceForm() {
        var directive = {
            replace: true,
            restrict: 'E',
            templateUrl: '/static/templates/rois_manager/slice.html',
            controller: 'NewSliceController',
            controllerAs: 'rmCtrl',
            link: function(scope, element, attrs) {
                $("#spinner").TouchSpin({
                    min: 0,
                    step: 1,
                    booster: false,
                    mousewheel: false
                });
            }
        };
        return directive;
    }

    function newSliceButtons() {
        var directive = {
            replace: true,
            restrict: 'E',
            templateUrl: '/static/templates/rois_manager/buttons_ctrl_group.html',
            controller: 'NewSliceController',
            controllerAs: 'rmCtrl'
        };
        return directive;
    }

    function newCoreForm() {
        var directive = {
            replace: true,
            restrict: 'E',
            templateUrl: '/static/templates/rois_manager/core.html',
            controller: 'NewCoreController',
            controllerAs: 'rmCtrl'
        };
        return directive;
    }

    function newCoreButtons() {
        var directive = {
            replace: true,
            restrict: 'E',
            templateUrl: '/static/templates/rois_manager/buttons_ctrl_group.html',
            controller: 'NewCoreController',
            controllerAs: 'rmCtrl'
        };
        return directive;
    }

    function newFocusRegionForm() {
        var directive = {
            replace: true,
            restrict: 'E',
            templateUrl: '/static/templates/rois_manager/focus_region.html',
            controller: 'NewFocusRegionController',
            controllerAs: 'rmCtrl'
        };
        return directive;
    }

    function newFocusRegionButtons() {
        var directive = {
            replace: true,
            restrict: 'E',
            templateUrl: '/static/templates/rois_manager/buttons_ctrl_group.html',
            controller: 'NewFocusRegionController',
            controllerAs: 'rmCtrl'
        };
        return directive;
    }
})();