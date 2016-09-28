(function () {
    'use strict';

    angular
        .module('promort.rois_manager.controllers')
        .controller('ROIsManagerController', ROIsManagerController)
        .controller('NewScopeController', NewScopeController)
        .controller('NewSliceController', NewSliceController)
        .controller('NewCoreController', NewCoreController)
        .controller('NewFocusRegionController', NewFocusRegionController);

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

    NewScopeController.$inject = ['$scope'];

    function NewScopeController($scope) {
        var vm = this;
        vm.$scope = {};

        activate();

        function activate() {
            console.log('Activated NewScopeController');
        }
    }

    NewSliceController.$inject = ['AnnotationsViewerService'];

    function NewSliceController(AnnotationsViewerService) {
        var vm = this;
        vm.read_only_mode = false;
        vm.active_tool = undefined;
        vm.polygon_tool_paused = false;
        vm.shape = undefined;

        vm.POLYGON_TOOL = 'polygon_drawing_tool';
        vm.FREEHAND_TOOL = 'freehand_drawing_tool';

        vm.newPolygon = newPolygon;
        vm.newFreehand = newFreehand;
        vm.click = click;
        vm.setReadOnlyMode = setReadOnlyMode;
        vm.isReadOnly = isReadOnly;
        vm.isPolygonToolActive = isPolygonToolActive;
        vm.isPolygonToolPaused = isPolygonToolPaused;
        vm.isFreehandToolActive = isFreehandToolActive;
        vm.shapeExists = shapeExists;
        vm.pausePolygonTool = pausePolygonTool;
        vm.unpausePolygonTool = unpausePolygonTool;
        vm.confirmPolygon = confirmPolygon;
        vm.abortTool = abortTool;
        vm.deleteShape = deleteShape;

        function newPolygon() {
            AnnotationsViewerService.startPolygonsTool();
            vm.active_tool = vm.POLYGON_TOOL
        }

        function newFreehand() {
            vm.active_tool = vm.FREEHAND_TOOL;
        }

        function setReadOnlyMode() {
            vm.read_only_mode = true;
        }

        function isReadOnly() {
            return vm.read_only_mode;
        }

        function isPolygonToolActive() {
            return vm.active_tool === vm.POLYGON_TOOL;
        }

        function isPolygonToolPaused() {
            return vm.polygon_tool_paused;
        }

        function isFreehandToolActive() {
            return vm.active_tool === vm.FREEHAND_TOOL;
        }

        function shapeExists() {
            return vm.shape != undefined;
        }

        function pausePolygonTool() {
            vm.polygon_tool_paused = true;
        }

        function unpausePolygonTool() {
            vm.polygon_tool_paused = false;
        }

        function confirmPolygon() {
            // TODO: get shape's JSON from ome_seadragon viewer
            vm.shape = '';
            vm.active_tool = undefined;
        }

        function abortTool() {
            vm.active_tool = undefined;
        }

        function deleteShape() {
            vm.shape = undefined;
        }

        // TODO: change into a proper save function for the whole slide object
        function click() {
            console.log('Clicked on NEW SLICE CONTROLLER button');
        }
    }

    function NewCoreController() {
        var vm = this;
        vm.click = click;

        function click() {
            console.log('Clicked on NEW CORE CONTROLLER button');
        }
    }

    function NewFocusRegionController() {
        var vm = this;
        vm.click = click;

        function click() {
            console.log('Cliecked on NEW FOCUS REGION CONTROLLER button');
        }
    }
})();