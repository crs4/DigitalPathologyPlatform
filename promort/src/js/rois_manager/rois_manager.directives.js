(function () {
    'use strict';

    angular
        .module('promort.rois_manager.directives')
        .directive('newSliceForm', newSliceForm)
        .directive('newSliceButtons', newSliceButtons)
        .directive('showSliceDetails', showSliceDetails)
        .directive('showSliceButtons', showSliceButtons)
        .directive('editSliceForm', editSliceForm)
        .directive('editSliceButtons', editSliceButtons)
        .directive('newCoreForm', newCoreForm)
        .directive('newCoreButtons', newCoreButtons)
        .directive('showCoreDetails', showCoreDetails)
        .directive('showCoreButtons', showCoreButtons)
        .directive('editCoreForm', editCoreForm)
        .directive('editCoreButtons', editCoreButtons)
        .directive('newFocusRegionForm', newFocusRegionForm)
        .directive('newFocusRegionButtons', newFocusRegionButtons)
        .directive('showFocusRegionDetails', showFocusRegionDetails)
        .directive('showFocusRegionButtons', showFocusRegionButtons)
        .directive('editFocusRegionForm', editFocusRegionForm)
        .directive('editFocusRegionButtons', editFocusRegionButtons);

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

    function editSliceForm() {
        var directive = {
            replace: true,
            restrict: 'E',
            templateUrl: '/static/templates/rois_manager/slice.html',
            controller: 'EditSliceController',
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

    function editSliceButtons() {
        var directive = {
            replace: true,
            restrict: 'E',
            templateUrl: '/static/templates/rois_manager/buttons_ctrl_group.html',
            controller: 'EditSliceController',
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

    function editCoreForm() {
        var directive = {
            replace: true,
            restrict: 'E',
            templateUrl: '/static/templates/rois_manager/core.html',
            controller: 'EditCoreController',
            controllerAs: 'rmCtrl',
            link: function(scope, element, attrs) {
                $(".selectpicker").selectpicker({
                    style: 'btn-default input-group-addon prm-selectpicker'
                });
            }
        };
        return directive;
    }

    function editCoreButtons() {
        var directive = {
            replace: true,
            restrict: 'E',
            templateUrl: '/static/templates/rois_manager/buttons_ctrl_group.html',
            controller: 'EditCoreController',
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

    function editFocusRegionForm() {
        var directive = {
            replace: true,
            restrict: 'E',
            templateUrl: '/static/templates/rois_manager/focus_region.html',
            controller: 'EditFocusRegionController',
            controllerAs: 'rmCtrl',
            link: function(scope, element, attrs) {
                $(".selectpicker").selectpicker({
                    style: 'btn-default input-group-addon prm-selectpicker'
                });
            }
        };
        return directive;
    }

    function editFocusRegionButtons() {
        var directive = {
            replace: true,
            restrict: 'E',
            templateUrl: '/static/templates/rois_manager/buttons_ctrl_group.html',
            controller: 'EditFocusRegionController',
            controllerAs: 'rmCtrl'
        };
        return directive;
    }
})();