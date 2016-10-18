(function () {
    'use strict';

    angular
        .module('promort.rois_manager.directives')
        .directive('sliceData', sliceData)
        .directive('sliceButtons', sliceButtons)
        .directive('coreData', coreData)
        .directive('coreButtons', coreButtons)
        .directive('focusRegionData', focusRegionData)
        .directive('focusRegionButtons', focusRegionButtons);

    function sliceData() {
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

    function sliceButtons() {
        var directive = {
            replace: true,
            restrict: 'E',
            templateUrl: '/static/templates/rois_manager/buttons_ctrl_group.html',
            controller: 'NewSliceController',
            controllerAs: 'rmCtrl'
        };
        return directive;
    }

    function coreData() {
        var directive = {
            replace: true,
            restrict: 'E',
            templateUrl: '/static/templates/rois_manager/core.html',
            controller: 'NewCoreController',
            controllerAs: 'rmCtrl'
        };
        return directive;
    }

    function coreButtons() {
        var directive = {
            replace: true,
            restrict: 'E',
            templateUrl: '/static/templates/rois_manager/buttons_ctrl_group.html',
            controller: 'NewCoreController',
            controllerAs: 'rmCtrl'
        };
        return directive;
    }

    function focusRegionData() {
        var directive = {
            replace: true,
            restrict: 'E',
            templateUrl: '/static/templates/rois_manager/focus_region.html',
            controller: 'NewFocusRegionController',
            controllerAs: 'rmCtrl'
        };
        return directive;
    }

    function focusRegionButtons() {
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