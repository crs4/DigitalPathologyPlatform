(function () {
    'use strict';

    angular
        .module('promort.rois_manager.controllers')
        .controller('ROIsManagerController', ROIsManagerController)
        .controller('NewScopeController', NewScopeController)
        .controller('NewSliceController', NewSliceController)
        .controller('NewCoreController', NewCoreController)
        .controller('NewFocusRegionController', NewFocusRegionController);

    ROIsManagerController.$inject = ['$scope', '$routeParams', '$rootScope',
        'SlidesManagerService', 'AnnotationsViewerService'];

    function ROIsManagerController($scope, $routeParams, $rootScope,
                                   SlidesManagerService, AnnotationsViewerService) {
        var vm = this;
        vm.slide_id = undefined;
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

            // draw existing ROIs as soon as viewer's components are registered
            $rootScope.$on('viewerctrl.components.registered',
                function() {
                    console.log('Retrieving existing slices');
                    SlidesManagerService.getSlices(vm.slide_id).then(getSlicesSuccessFn, getSlicesErrorFn);

                    function getSlicesSuccessFn(response) {
                        function drawSlice(slice_data) {
                            console.log(slice_data);
                            AnnotationsViewerService.drawShape($.parseJSON(slice_data.roi_json));
                            // TODO: add a $rootScope.$broadcast to declare the slice
                            var slice_info = {
                                'id': slice_data.id,
                                'label': slice_data.label
                            };
                            $rootScope.$broadcast('slice.new', slice_info);
                        }

                        response.data.slices.forEach(drawSlice);
                    }

                    function getSlicesErrorFn(response) {
                        console.error('Unable to load slices for slide ' + vm.slide_id);
                        console.error(response.data);
                    }
                }
            );

            // shut down creation forms when specific events occur
            $rootScope.$on('tool.destroyed',
                function() {
                    vm.allModesOff();
                }
            );
            $rootScope.$on('slice.saved',
                function(){
                    vm.allModesOff();
                }
            );
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

    NewSliceController.$inject = ['$routeParams', '$rootScope',
        'AnnotationsViewerService', 'SlidesManagerService'];

    function NewSliceController($routeParams, $rootScope,
                                AnnotationsViewerService, SlidesManagerService) {
        var vm = this;
        vm.slide_id = undefined;
        vm.case_id = undefined;
        vm.shape = undefined;
        vm.totalCores = 0;

        vm.read_only_mode = false;
        vm.active_tool = undefined;
        vm.polygon_tool_paused = false;

        vm.POLYGON_TOOL = 'polygon_drawing_tool';
        vm.FREEHAND_TOOL = 'freehand_drawing_tool';

        vm.newPolygon = newPolygon;
        vm.newFreehand = newFreehand;
        vm.save = save;
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
        vm.clear = clear;
        vm.focusOnShape = focusOnShape;
        vm.deleteShape = deleteShape;
        vm.formValid = formValid;
        vm.destroy = destroy;

        activate();

        function activate() {
            vm.slide_id = $routeParams.slide;
            vm.case_id = $routeParams.case;
        }

        function newPolygon() {
            console.log('Start polygon drawing tool');
            AnnotationsViewerService.startPolygonsTool();
            vm.active_tool = vm.POLYGON_TOOL
        }

        function newFreehand() {
            console.log('Start freehabd drawing tool');
            AnnotationsViewerService.setFreehandToolLabelPrefix('slice');
            AnnotationsViewerService.startFreehandDrawingTool();
            var canvas_label = AnnotationsViewerService.getCanvasLabel();
            var $canvas = $('#' + canvas_label);
            $canvas.on('freehand_polygon_saved',
                function(event, polygon_label) {
                    console.log('Freehand drawing saved');
                    vm.shape = AnnotationsViewerService.getShapeJSON(polygon_label);
                    // calling the click event of the button will also refresh page and apply
                    // proper angular.js controller rules
                    $("#freehand_abort").click();
                    $canvas.unbind('freehand_polygon_saved');
                }
            );
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
            AnnotationsViewerService.pausePolygonTool();
            vm.polygon_tool_paused = true;
        }

        function unpausePolygonTool() {
            AnnotationsViewerService.startPolygonsTool();
            vm.polygon_tool_paused = false;
        }

        function confirmPolygon() {
            var canvas_label = AnnotationsViewerService.getCanvasLabel();
            var $canvas = $('#' + canvas_label);
            $canvas.on('polygon_saved',
                function(event, polygon_label) {
                    console.log('Polygon saved!');
                    vm.shape = AnnotationsViewerService.getShapeJSON(polygon_label);
                    vm.abortTool();
                    $canvas.unbind('polygon_saved');
                }
            );
            AnnotationsViewerService.saveTemporaryPolygon('slice');
        }

        function clear() {
            if (typeof this.shape !== 'undefined') {
                AnnotationsViewerService.deleteShape(vm.shape.shape_id);
                this.shape = undefined;
            }
            this.totalCores = 0;
        }

        function abortTool() {
            console.log('Aborting tool');
            if (vm.active_tool === vm.POLYGON_TOOL) {
                AnnotationsViewerService.clearTemporaryPolygon();
            }
            AnnotationsViewerService.disableActiveTool();
            vm.active_tool = undefined;
        }

        function destroy() {
            vm.clear();
            vm.abortTool();
            $rootScope.$broadcast('tool.destroyed');
        }

        function deleteShape() {
            AnnotationsViewerService.deleteShape(vm.shape.shape_id);
            vm.shape = undefined;
        }

        function focusOnShape() {
            AnnotationsViewerService.focusOnShape(vm.shape.shape_id);
        }

        function formValid() {
            if (typeof(vm.shape) !== 'undefined') {
                return true;
            } else {
                return false;
            }
        }

        function save() {
            console.log(vm.slide_id, vm.shape.shape_id,
                vm.shape, vm.totalCores);
            SlidesManagerService.createSlice(vm.slide_id, vm.shape.shape_id, vm.shape, vm.totalCores)
                .then(createSliceSuccessFn, createSliceErrorFn);

            function createSliceSuccessFn(response) {
                var slice_info = {
                    'id': response.data.id,
                    'label': response.data.label
                };
                $rootScope.$broadcast('slice.new', slice_info);
            }

            function createSliceErrorFn(response) {
                console.error('Unable to save slice!!!');
                console.error(response.data);
            }
        }
    }

    NewCoreController.$inject = ['$rootScope'];

    function NewCoreController($rootScope) {
        var vm = this;
        vm.save = save;
        vm.formValid = formValid;
        vm.destroy = destroy;

        function save() {
            console.log('Clicked on NEW CORE CONTROLLER button');
        }

        function formValid() {
            return false;
        }

        function destroy() {
            $rootScope.$broadcast('tool.destroyed');
        }
    }

    NewFocusRegionController.$inject = ['$rootScope'];

    function NewFocusRegionController($rootScope) {
        var vm = this;
        vm.save = save;
        vm.formValid = formValid;
        vm.destroy = destroy;

        function save() {
            console.log('Cliecked on NEW FOCUS REGION CONTROLLER button');
        }

        function formValid() {
            return false;
        }

        function destroy() {
            $rootScope.$broadcast('tool.destroyed');
        }
    }
})();