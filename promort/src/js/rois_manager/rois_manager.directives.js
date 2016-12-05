(function () {
    'use strict';

    angular
        .module('promort.rois_manager.directives')
        .directive('newSliceForm', newSliceForm)
        .directive('newSliceButtons', newSliceButtons)
        .directive('showSliceDetails', showSliceDetails)
        .directive('showSliceButtons', showSliceButtons)
        .directive('newCoreForm', newCoreForm)
        .directive('newCoreButtons', newCoreButtons)
        .directive('showCoreDetails', showCoreDetails)
        .directive('showCoreButtons', showCoreButtons)
        .directive('newFocusRegionForm', newFocusRegionForm)
        .directive('newFocusRegionButtons', newFocusRegionButtons)
        .directive('showFocusRegionDetails', showFocusRegionDetails)
        .directive('showFocusRegionButtons', showFocusRegionButtons);

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

    function showSliceDetails() {
        var directive = {
            replace: true,
            restricted: 'E',
            templateUrl: '/static/templates/rois_manager/slice.html',
            controller: 'ShowSliceController',
            controllerAs: 'rmCtrl'
        };
        return directive;
    }

    function showSliceButtons() {
        var directive = {
            replace: true,
            restrict: 'E',
            templateUrl: '/static/templates/rois_manager/buttons_ctrl_group.html',
            controller: 'ShowSliceController',
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
            controllerAs: 'rmCtrl',
            link: function(scope, element, attrs) {
                $(".selectpicker").selectpicker({
                    style: 'btn-default input-group-addon prm-selectpicker'
                });
            }
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

    function showCoreDetails() {
        var directive = {
            replace: true,
            restrict: 'E',
            templateUrl: '/static/templates/rois_manager/core.html',
            controller: 'ShowCoreController',
            controllerAs: 'rmCtrl',
            link: function(scope, element, attrs) {
                $(".selectpicker").selectpicker({
                    style: 'btn-default input-group-addon prm-selectpicker'
                });
            }
        };
        return directive;
    }

    function showCoreButtons() {
        var directive = {
            replace: true,
            restrict: 'E',
            templateUrl: '/static/templates/rois_manager/buttons_ctrl_group.html',
            controller: 'ShowCoreController',
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
            controllerAs: 'rmCtrl',
            link: function(scope, element, attrs) {
                $(".selectpicker").selectpicker({
                    style: 'btn-default input-group-addon prm-selectpicker'
                });
            }
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

    function showFocusRegionDetails() {
        var directive = {
            replace: true,
            restrict: 'E',
            templateUrl: '/static/templates/rois_manager/focus_region.html',
            controller: 'ShowFocusRegionController',
            controllerAs: 'rmCtrl',
            link: function(scope, element, attrs) {
                $(".selectpicker").selectpicker({
                    style: 'btn-default input-group-addon prm-selectpicker'
                });
            }
        };
        return directive;
    }

    function showFocusRegionButtons() {
        var directive = {
            replace: true,
            restrict: 'E',
            templateUrl: '/static/templates/rois_manager/buttons_ctrl_group.html',
            controller: 'ShowFocusRegionController',
            controllerAs: 'rmCtrl'
        };
        return directive;
    }
})();