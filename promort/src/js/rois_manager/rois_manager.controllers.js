(function () {
    'use strict';

    angular
        .module('promort.rois_manager.controllers')
        .controller('ROIsManagerController', ROIsManagerController);

    ROIsManagerController.$inject = ['$scope', '$routeParams'];

    function ROIsManagerController($scope, $routeParams) {
        var vm = this;
        vm.slide = undefined;
        vm.case_id = undefined;

        vm.ui_active_modes = {
            'new_slice': false,
            'new_core': false,
            'new_focus_region': false,
            'show_slice': false,
            'show_core': false,
            'show_focus_region': false
        };

        vm.allModesOff = allModesOff;
        vm.activateNewSliceMode = activateNewSliceMode;
        vm.newSliceModeActive = newSliceModeActive;
        vm.activateNewCoreMode = activateNewCoreMode;
        vm.newCoreModeActive = newCoreModeActive;
        vm.activateNewFocusRegionMode = activateNewFocusRegionMode;
        vm.newFocusRegionModeActive = newFocusRegionModeActive;

        activate();

        function activate() {
            vm.slide_id = $routeParams.slide;
            vm.case_id = $routeParams.case;

            // TODO: draw existing ROIs
        }

        function allModesOff() {
            console.log('Resetting UI modes');
            for (var mode in vm.ui_active_modes) {
                vm.ui_active_modes[mode] = false;
            }
        }

        function activateNewSliceMode() {
            vm.allModesOff();
            vm.ui_active_modes['new_slice'] = true;
            console.log('NEW SLICE MODE --- activated');
        }

        function newSliceModeActive() {
            return vm.ui_active_modes['new_slice'];
        }

        function activateNewCoreMode() {
            vm.allModesOff();
            vm.ui_active_modes['new_core'] = true;
            console.log('NEW CORE MODE --- activated');
        }

        function newCoreModeActive() {
            return vm.ui_active_modes['new_core'];
        }

        function activateNewFocusRegionMode() {
            vm.allModesOff();
            vm.ui_active_modes['new_focus_region'] = true;
            console.log('NEW FOCUS REGION MODE --- activated');
        }

        function newFocusRegionModeActive() {
            return vm.ui_active_modes['new_focus_region'];
        }
    }
})();