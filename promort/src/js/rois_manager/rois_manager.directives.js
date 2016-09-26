(function () {
    'use strict';

    angular
        .module('promort.rois_manager.directives')
        .directive('newSliceCreation', newSliceCreation)
        .directive('newCoreCreation', newCoreCreation)
        .directive('newFocusRegionCreation', newFocusRegionCreation);

    function newSliceCreation() {
        var directive = {
            replace: true,
            restrict: 'E',
            templateUrl: '/static/templates/rois_manager/slice.html'
        };
        return directive;
    }

    function newCoreCreation() {
        var directive = {
            replace: true,
            restrict: 'E',
            templateUrl: '/static/templates/rois_manager/core.html'
        };
        return directive;
    }

    function newFocusRegionCreation() {
        var directive = {
            replace: true,
            restrict: 'E',
            templateUrl: '/static/templates/rois_manager/region.html'
        };
        return directive;
    }
})();