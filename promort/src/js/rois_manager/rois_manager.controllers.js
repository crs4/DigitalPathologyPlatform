(function () {
    'use strict';

    angular
        .module('promort.rois_manager.controllers')
        .controller('ROIsManagerController', ROIsManagerController)
        .controller('NewScopeController', NewScopeController)
        .controller('NewSliceController', NewSliceController)
        .controller('ShowSliceController', ShowSliceController)
        .controller('NewCoreController', NewCoreController)
        .controller('ShowCoreController', ShowCoreController)
        .controller('NewFocusRegionController', NewFocusRegionController)
        .controller('ShowFocusRegionController', ShowFocusRegionController);

    ROIsManagerController.$inject = ['$scope', '$routeParams', '$rootScope', '$compile',
        'ngDialog', 'SlidesManagerService', 'AnnotationsViewerService'];

    function ROIsManagerController($scope, $routeParams, $rootScope, $compile, ngDialog,
                                   SlidesManagerService, AnnotationsViewerService) {
        var vm = this;
        vm.slide_id = undefined;
        vm.case_id = undefined;

        vm.slices_map = undefined;
        vm.cores_map = undefined;
        vm.focus_regions_map = undefined;

        vm.ui_active_modes = {
            'new_slice': false,
            'new_core': false,
            'new_focus_region': false,
            'show_slice': false,
            'show_core': false,
            'show_focus_region': false
        };
        vm.roisTreeLocked = false;

        vm._createListItem = _createListItem;
        vm._createNewSubtree = _createNewSubtree;
        vm._lockRoisTree = _lockRoisTree;
        vm._unlockRoisTree = _unlockRoisTree;
        vm.allModesOff = allModesOff;
        vm.showROI = showROI;
        vm.selectROI = selectROI;
        vm.deselectROI = deselectROI;
        vm.clearROIs = clearROIs;
        vm.activateNewSliceMode = activateNewSliceMode;
        vm.newSliceModeActive = newSliceModeActive;
        vm.activateShowSliceMode = activateShowSliceMode;
        vm.showSliceModeActive = showSliceModeActive;
        vm.activateNewCoreMode = activateNewCoreMode;
        vm.newCoreModeActive = newCoreModeActive;
        vm.activateShowCoreMode = activateShowCoreMode;
        vm.showCoreModeActive = showCoreModeActive;
        vm.activateNewFocusRegionMode = activateNewFocusRegionMode;
        vm.newFocusRegionModeActive = newFocusRegionModeActive;
        vm.activateShowFocusRegionMode = activateShowFocusRegionMode;
        vm.showFocusRegionModeActive = showFocusRegionModeActive;
        vm._registerSlice = _registerSlice;
        vm._unregisterSlice = _unregisterSlice;
        vm._registerCore = _registerCore;
        vm._unregisterCore = _unregisterCore;
        vm._registerFocusRegion = _registerFocusRegion;
        vm._unregisterFocusRegion = _unregisterFocusRegion;
        vm._getSliceLabel = _getSliceLabel;
        vm._getCoreLabel = _getCoreLabel;
        vm._getFocusRegionLabel = _getFocusRegionLabel;
        vm._getSliceCores = _getSliceCores;
        vm._getCoreFocusRegions = _getCoreFocusRegions;
        vm.getSlicesCount = getSlicesCount;
        vm.getCoresCount = getCoresCount;
        vm.getFocusRegionsCount = getFocusRegionsCount;

        activate();

        function activate() {
            vm.slide_id = $routeParams.slide;
            vm.case_id = $routeParams.case;

            vm.slices_map = {};
            vm.cores_map = {};
            vm.focus_regions_map = {};

            $rootScope.slices = [];
            $rootScope.cores = [];
            $rootScope.focus_regions = [];

            // shut down creation forms when specific events occur
            $scope.$on('tool.destroyed',
                function() {
                    vm.allModesOff();
                }
            );

            $scope.$on('slice.new',
                function(event, slice_info) {
                    vm._registerSlice(slice_info);
                    vm.allModesOff();
                    // add new item to ROIs tree
                    var $tree = $("#rois_tree");
                    var $new_slice_item = $(vm._createListItem(slice_info.label, true));
                    var $anchor = $new_slice_item.find('a');
                    $anchor.attr('ng-click', 'rmc.showROI("slice", ' + slice_info.id + ')')
                        .attr('ng-mouseenter', 'rmc.selectROI("slice", ' + slice_info.id +')')
                        .attr('ng-mouseleave', 'rmc.deselectROI("slice", ' + slice_info.id +')');
                    $compile($anchor)($scope);
                    var new_slice_subtree = vm._createNewSubtree(slice_info.label);
                    $new_slice_item.append(new_slice_subtree);
                    $tree.append($new_slice_item);
                }
            );

            $scope.$on('slice.deleted',
                function(event, slice_id) {
                    console.log('SLICE ' + slice_id + ' DELETED');
                    var cores = _getSliceCores(slice_id);
                    cores.forEach(
                        function(item, index) {
                            $rootScope.$broadcast('core.deleted', item.id);
                        }
                    );
                    AnnotationsViewerService.deleteShape(vm._getSliceLabel(slice_id));
                    $("#" + vm._getSliceLabel(slice_id) + "_list").remove();
                    vm._unregisterSlice(slice_id);
                    vm.allModesOff();
                }
            );

            $scope.$on('core.new',
                function(event, core_info) {
                    vm._registerCore(core_info);
                    vm.allModesOff();
                    // add new item to ROIs tree
                    var $tree = $("#" + vm._getSliceLabel(core_info.slice) + "_tree");
                    var $new_core_item = $(vm._createListItem(core_info.label, true));
                    var $anchor = $new_core_item.find('a');
                    $anchor.attr('ng-click', 'rmc.showROI("core", ' + core_info.id + ')')
                        .attr('ng-mouseenter', 'rmc.selectROI("core", ' + core_info.id + ')')
                        .attr('ng-mouseleave', 'rmc.deselectROI("core", ' + core_info.id + ')');
                    $compile($anchor)($scope);
                    var new_core_subtree = vm._createNewSubtree(core_info.label);
                    $new_core_item.append(new_core_subtree);
                    $tree.append($new_core_item);
                }
            );

            $scope.$on('core.deleted',
                function(event, core_id) {
                    console.log('CORE ' + core_id + ' DELETED');
                    var focus_regions = _getCoreFocusRegions(core_id);
                    focus_regions.forEach(
                        function(item, index) {
                            console.log('Broadcasting delete evento for focus region ' + item.id);
                            $rootScope.$broadcast('focus_region.deleted', item.id);
                        }
                    );
                    AnnotationsViewerService.deleteShape(vm._getCoreLabel(core_id));
                    $("#" + vm._getCoreLabel(core_id) + "_list").remove();
                    vm._unregisterCore(core_id);
                    vm.allModesOff();
                }
            );

            $scope.$on('focus_region.new',
                function(event, focus_region_info) {
                    vm._registerFocusRegion(focus_region_info);
                    vm.allModesOff();
                    // add new item to ROIs tree
                    var $tree = $("#" + vm._getCoreLabel(focus_region_info.core) + "_tree");
                    var $new_focus_region_item = $(vm._createListItem(focus_region_info.label, false));
                    var $anchor = $new_focus_region_item.find('a');
                    $anchor.attr('ng-click', 'rmc.showROI("focus_region", ' + focus_region_info.id + ', "' +
                        vm._getCoreLabel(focus_region_info.core) + '")')
                        .attr('ng-mouseenter', 'rmc.selectROI("focus_region", ' + focus_region_info.id + ')')
                        .attr('ng-mouseleave', 'rmc.deselectROI("focus_region", ' + focus_region_info.id + ')');
                    $compile($anchor)($scope);
                    $tree.append($new_focus_region_item);
                }
            );

            $scope.$on('focus_region.deleted',
                function(event, focus_region_id) {
                    console.log('FOCUS REGION ' + focus_region_id + ' DELETED');
                    AnnotationsViewerService.deleteShape(vm._getFocusRegionLabel(focus_region_id));
                    $("#" + vm._getFocusRegionLabel(focus_region_id) + "_list").remove();
                    vm._unregisterFocusRegion(focus_region_id);
                    vm.allModesOff();
                }
            )
        }

        function _registerSlice(slice_info) {
            $rootScope.slices.push(slice_info);
            vm.slices_map[slice_info.id] = slice_info.label;
        }

        function _unregisterSlice(slice_id) {
            delete vm.slices_map[slice_id];
            $rootScope.slices = $.grep($rootScope.slices,
                function(value) {
                    return value.id !== slice_id;
                }
            );
        }

        function _getSliceLabel(slice_id) {
            return vm.slices_map[slice_id];
        }

        function _registerCore(core_info) {
            $rootScope.cores.push(core_info);
            vm.cores_map[core_info.id] = core_info.label;
        }

        function _unregisterCore(core_id) {
            delete vm.cores_map[core_id];
            $rootScope.cores = $.grep($rootScope.cores,
                function(value) {
                    return value.id !== core_id;
                }
            );
        }

        function _getCoreLabel(core_id) {
            return vm.cores_map[core_id];
        }

        function _registerFocusRegion(focus_region_info) {
            $rootScope.focus_regions.push(focus_region_info);
            vm.focus_regions_map[focus_region_info.id] = focus_region_info.label;
        }

        function _unregisterFocusRegion(focus_region_id) {
            delete vm.focus_regions_map[focus_region_id];
            $rootScope.focus_regions = $.grep($rootScope.focus_regions,
                function(value) {
                    return value.id !== focus_region_id;
                }
            );
        }

        function _getFocusRegionLabel(focus_region_id) {
            return vm.focus_regions_map[focus_region_id];
        }

        function _createListItem(label, set_neg_margin_cls) {
            var html = '<li id="';
            html += label;
            html += '_list" class="list-group-item prm-tree-item';
            if (set_neg_margin_cls) {
                html += ' prm-tree-item-neg-margin';
            }
            html += '"><a class="prm-tree-el" href="#"><i class="icon-isight"></i> ';
            html += label;
            html += '</a></li>';
            return html;
        }

        function _getSliceCores(slice_id) {
            return $.grep($rootScope.cores,
                function(value) {
                    return value.slice === slice_id;
                }
            )
        }

        function _getCoreFocusRegions(core_id) {
            console.log($rootScope.focus_regions);
            return $.grep($rootScope.focus_regions,
                function(value) {
                    return value.core === core_id;
                }
            )
        }

        function _createNewSubtree(roi_label) {
            var html = '<ul id="' + roi_label +'_tree" class="list-group"></ul>';
            return html;
        }

        function _lockRoisTree() {
            vm.roisTreeLocked = true;
            $(".prm-tree-el").addClass("prm-tree-el-disabled");
        }

        function _unlockRoisTree() {
            vm.roisTreeLocked = false;
            $(".prm-tree-el").removeClass("prm-tree-el-disabled");
        }

        function allModesOff() {
            for (var mode in vm.ui_active_modes) {
                vm.ui_active_modes[mode] = false;
            }
            vm._unlockRoisTree();
        }

        function showROI(roi_type, roi_id, parent_roi) {
            if (!vm.roisTreeLocked) {
                switch (roi_type) {
                    case 'slice':
                        activateShowSliceMode(roi_id);
                        AnnotationsViewerService.focusOnShape(vm._getSliceLabel(roi_id));
                        break;
                    case 'core':
                        activateShowCoreMode(roi_id);
                        AnnotationsViewerService.focusOnShape(vm._getCoreLabel(roi_id));
                        break;
                    case 'focus_region':
                        activateShowFocusRegionMode(roi_id, parent_roi);
                        AnnotationsViewerService.focusOnShape(vm._getFocusRegionLabel(roi_id));
                        break;
                }
            }
        }

        function selectROI(roi_type, roi_id) {
            if (!vm.roisTreeLocked) {
                switch (roi_type) {
                    case 'slice':
                        AnnotationsViewerService.selectShape(vm._getSliceLabel(roi_id));
                        break;
                    case 'core':
                        AnnotationsViewerService.selectShape(vm._getCoreLabel(roi_id));
                        break;
                    case 'focus_region':
                        AnnotationsViewerService.selectShape(vm._getFocusRegionLabel(roi_id));
                        break;
                }
            }
        }

        function deselectROI(roi_type, roi_id) {
            if (!vm.roisTreeLocked) {
                switch (roi_type) {
                    case 'slice':
                        AnnotationsViewerService.deselectShape(vm._getSliceLabel(roi_id));
                        break;
                    case 'core':
                        AnnotationsViewerService.deselectShape(vm._getCoreLabel(roi_id));
                        break;
                    case 'focus_region':
                        AnnotationsViewerService.deselectShape(vm._getFocusRegionLabel(roi_id));
                        break;
                }
            }
        }

        function clearROIs() {
            ngDialog.openConfirm({
                template: '/static/templates/dialogs/clear_rois_confirm.html',
                closeByEscape: false,
                showClose: false,
                closeByNavigation: false,
                closeByDocument: false
            }).then(confirmFn);

            var dialog = undefined;
            function confirmFn(confirm_value) {
                dialog = ngDialog.open({
                        'template': '/static/templates/dialogs/deleting_data.html',
                        showClose: false,
                        closeByEscape: false,
                        closeByNavigation: false,
                        closeByDocument: false
                    });
                if (confirm_value) {
                    SlidesManagerService.clearROIs(vm.slide_id)
                        .then(clearROIsSuccessFn, clearROIsErrorFn);
                }

                function clearROIsSuccessFn(response) {
                    AnnotationsViewerService.clear();

                    vm.slices_map = {};
                    vm.cores_map = {};
                    vm.focus_regions_map = {};

                    $rootScope.slices = [];
                    $rootScope.cores = [];
                    $rootScope.focus_regions = [];

                    $("#rois_tree").children().remove();

                    vm.allModesOff();

                    dialog.close();
                }

                function clearROIsErrorFn(response) {
                    console.error('Clear ROIs failed');
                    console.error(response);
                    $scope.closeThisDialog();
                }
            }
        }

        function activateNewSliceMode() {
            vm.allModesOff();
            vm._lockRoisTree();
            vm.ui_active_modes['new_slice'] = true;
        }

        function newSliceModeActive() {
            return vm.ui_active_modes['new_slice'];
        }

        function activateShowSliceMode(slice_id) {
            console.log('Show slice ' + slice_id);
            vm.allModesOff();
            $rootScope.$broadcast('slice.show', slice_id);
            vm.ui_active_modes['show_slice'] = true;
        }

        function showSliceModeActive() {
            return vm.ui_active_modes['show_slice'];
        }

        function activateNewCoreMode() {
            vm.allModesOff();
            vm._lockRoisTree();
            vm.ui_active_modes['new_core'] = true;
        }

        function newCoreModeActive() {
            return vm.ui_active_modes['new_core'];
        }

        function activateShowCoreMode(core_id) {
            vm.allModesOff();
            $rootScope.$broadcast('core.show', core_id);
            vm.ui_active_modes['show_core'] = true;
        }

        function showCoreModeActive() {
            return vm.ui_active_modes['show_core'];
        }

        function activateNewFocusRegionMode() {
            vm.allModesOff();
            vm._lockRoisTree();
            vm.ui_active_modes['new_focus_region'] = true;
        }

        function newFocusRegionModeActive() {
            return vm.ui_active_modes['new_focus_region'];
        }

        function activateShowFocusRegionMode(focus_region_id, parent_core_id) {
            vm.allModesOff();
            $rootScope.$broadcast('focus_region.show', focus_region_id, parent_core_id);
            vm.ui_active_modes['show_focus_region'] = true;
        }

        function showFocusRegionModeActive() {
            return vm.ui_active_modes['show_focus_region'];
        }

        function getSlicesCount() {
            return $rootScope.slices.length;
        }

        function getCoresCount() {
            return $rootScope.cores.length;
        }

        function getFocusRegionsCount() {
            return $rootScope.focus_regions.length;
        }
    }

    NewScopeController.$inject = ['$scope'];

    function NewScopeController($scope) {
        var vm = this;
        vm.$scope = {};
    }

    NewSliceController.$inject = ['$scope', '$routeParams', '$rootScope', 'ngDialog',
        'AnnotationsViewerService', 'SlidesManagerService'];

    function NewSliceController($scope, $routeParams, $rootScope, ngDialog,
                                AnnotationsViewerService, SlidesManagerService) {
        var vm = this;
        vm.slide_id = undefined;
        vm.case_id = undefined;
        vm.shape = undefined;
        vm.totalCores = 0;

        vm.active_tool = undefined;
        vm.polygon_tool_paused = false;

        vm.POLYGON_TOOL = 'polygon_drawing_tool';
        vm.FREEHAND_TOOL = 'freehand_drawing_tool';

        vm.shape_config = {
            'stroke_color': '#000000',
            'stroke_width': 40
        };

        vm.newPolygon = newPolygon;
        vm.newFreehand = newFreehand;
        vm.save = save;
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
            AnnotationsViewerService.extendPolygonConfig(vm.shape_config);
            AnnotationsViewerService.startPolygonsTool();
            vm.active_tool = vm.POLYGON_TOOL
        }

        function newFreehand() {
            console.log('Start freehabd drawing tool');
            AnnotationsViewerService.setFreehandToolLabelPrefix('slice');
            AnnotationsViewerService.extendPathConfig(vm.shape_config);
            AnnotationsViewerService.startFreehandDrawingTool();
            var canvas_label = AnnotationsViewerService.getCanvasLabel();
            var $canvas = $('#' + canvas_label);
            $canvas.on('freehand_polygon_saved',
                function(event, polygon_label) {
                    console.log('Freehand drawing saved');
                    vm.shape = AnnotationsViewerService.getShapeJSON(polygon_label);
                    // calling the click event of the button will also refresh page and apply
                    // proper angular.js controller rules
                    vm.abortTool();
                    $canvas.unbind('freehand_polygon_saved');
                    $scope.$apply();
                }
            );
            vm.active_tool = vm.FREEHAND_TOOL;
        }

        function isReadOnly() {
            return false;
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
            AnnotationsViewerService.disableActiveTool();
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

        function clear(destroy_shape) {
            vm.deleteShape(destroy_shape);
            vm.totalCores = 0;
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
            vm.clear(true);
            vm.abortTool();
            $rootScope.$broadcast('tool.destroyed');
        }

        function deleteShape(destroy_shape) {
            if (typeof vm.shape !== 'undefined') {
                if (destroy_shape === true) {
                    AnnotationsViewerService.deleteShape(vm.shape.shape_id);
                }
                vm.shape = undefined;
            }
        }

        function focusOnShape() {
            AnnotationsViewerService.focusOnShape(vm.shape.shape_id);
        }

        function formValid() {
            return (typeof vm.shape !== 'undefined');
        }

        function save() {
            var dialog = ngDialog.open({
                template: '/static/templates/dialogs/saving_data.html',
                showClose: false,
                closeByEscape: false,
                closeByNavigation: false,
                closeByDocument: false
            });
            SlidesManagerService.createSlice(vm.slide_id, vm.shape.shape_id, vm.shape, vm.totalCores)
                .then(createSliceSuccessFn, createSliceErrorFn);

            function createSliceSuccessFn(response) {
                var slice_info = {
                    'id': response.data.id,
                    'label': response.data.label
                };
                vm.clear(false);
                $rootScope.$broadcast('slice.new', slice_info);
                dialog.close();
            }

            function createSliceErrorFn(response) {
                console.error('Unable to save slice!!!');
                console.error(response.data);
                $scope.closeThisDialog();
            }
        }
    }

    ShowSliceController.$inject = ['$scope', '$rootScope', 'ngDialog',
        'SlicesManagerService', 'AnnotationsViewerService'];

    function ShowSliceController($scope, $rootScope, ngDialog,
                                 SlicesManagerService, AnnotationsViewerService) {
        var vm = this;
        vm.slice_id = undefined;
        vm.label = undefined;
        vm.shape_id = undefined;
        vm.totalCores = undefined;

        vm.isReadOnly = isReadOnly;
        vm.shapeExists = shapeExists;
        vm.focusOnShape = focusOnShape;
        vm.deleteShape = deleteShape;

        activate();

        function activate() {
            $scope.$on('slice.show',
                function(event, slice_id) {
                    console.log('Show slice ' + slice_id);
                    vm.slice_id = slice_id;
                    SlicesManagerService.get(slice_id)
                        .then(getSliceSuccessFn, getSliceErrorFn);
                }
            );

            function getSliceSuccessFn(response) {
                vm.label = response.data.label;
                vm.shape_id = $.parseJSON(response.data.roi_json).shape_id;
                vm.totalCores = response.data.total_cores;
            }

            function getSliceErrorFn(response) {
                console.error('Unable to load slice data');
                console.error(response);
            }
        }

        function isReadOnly() {
            return true;
        }

        function shapeExists() {
            return (typeof vm.shape_id !== 'undefined');
        }

        function focusOnShape() {
            AnnotationsViewerService.focusOnShape(vm.shape_id);
        }

        function deleteShape() {
            ngDialog.openConfirm({
                template: '/static/templates/dialogs/delete_roi_confirm.html',
                closeByEscape: false,
                showClose: false,
                closeByNavigation: false,
                closeByDocument: false
            }).then(confirmFn);

            var dialog = undefined;
            function confirmFn(confirm_value) {
                if (confirm_value) {
                    dialog = ngDialog.open({
                        'template': '/static/templates/dialogs/deleting_data.html',
                        showClose: false,
                        closeByEscape: false,
                        closeByNavigation: false,
                        closeByDocument: false
                    });
                    SlicesManagerService.cascadeDelete(vm.slice_id)
                        .then(deleteSliceSuccessFn, deleteSliceErrorFn);
                }
            }

            function deleteSliceSuccessFn(response) {
                $rootScope.$broadcast('slice.deleted', vm.slice_id);
                vm.slice_id = undefined;
                vm.label = undefined;
                vm.shape_id = undefined;
                vm.totalCores = undefined;
                dialog.close();
            }

            function deleteSliceErrorFn(response) {
                console.error('unable to delete slice');
                console.error(response);
                $scope.closeThisDialog();
            }
        }
    }

    NewCoreController.$inject = ['$scope', '$routeParams', '$rootScope', 'ngDialog',
        'AnnotationsViewerService', 'SlicesManagerService'];

    function NewCoreController($scope, $routeParams, $rootScope, ngDialog,
                               AnnotationsViewerService, SlicesManagerService) {
        var vm = this;
        vm.slide_id = undefined;
        vm.case_id = undefined;
        vm.parentSlice = undefined;
        vm.shape = undefined;
        vm.coreLength = undefined;
        vm.coreArea = undefined;

        vm.active_tool = undefined;
        vm.polygon_tool_paused = false;

        vm.POLYGON_TOOL = 'polygon_drawing_tool';
        vm.FREEHAND_TOOL = 'freehand_drawing_tool';
        vm.RULER_TOOL = 'ruler_tool';

        vm.shape_config = {
            'stroke_color': '#0000ff',
            'stroke_width': 30
        };

        vm.newPolygon = newPolygon;
        vm.newFreehand = newFreehand;
        vm._updateCoreData = _updateCoreData;
        vm.initializeRuler = initializeRuler;
        vm.startRuler = startRuler;
        vm.save = save;
        vm.isReadOnly = isReadOnly;
        vm.isPolygonToolActive = isPolygonToolActive;
        vm.isPolygonToolPaused = isPolygonToolPaused;
        vm.isFreehandToolActive = isFreehandToolActive;
        vm.isRulerToolActive = isRulerToolActive;
        vm.shapeExists = shapeExists;
        vm.coreLengthExists = coreLengthExists;
        vm.pausePolygonTool = pausePolygonTool;
        vm.unpausePolygonTool = unpausePolygonTool;
        vm.confirmPolygon = confirmPolygon;
        vm.stopRuler = stopRuler;
        vm.abortTool = abortTool;
        vm.clear = clear;
        vm.focusOnShape = focusOnShape;
        vm.deleteShape = deleteShape;
        vm.deleteRuler = deleteRuler;
        vm.formValid = formValid;
        vm.destroy = destroy;

        activate();

        function activate() {
            vm.slide_id = $routeParams.slide;
            vm.case_id = $routeParams.case;
            $scope.$on('viewerctrl.components.registered',
                function() {
                    vm.initializeRuler();
                }
            );
        }

        function newPolygon() {
            AnnotationsViewerService.extendPolygonConfig(vm.shape_config);
            AnnotationsViewerService.startPolygonsTool();
            vm.active_tool = vm.POLYGON_TOOL;
        }

        function newFreehand() {
            AnnotationsViewerService.setFreehandToolLabelPrefix('core');
            AnnotationsViewerService.extendPathConfig(vm.shape_config);
            AnnotationsViewerService.startFreehandDrawingTool();
            var canvas_label = AnnotationsViewerService.getCanvasLabel();
            var $canvas = $("#" + canvas_label);
            $canvas.on('freehand_polygon_saved',
                function(event, polygon_label) {
                    // check if new core is contained inside an existing slide
                    var slices = $rootScope.slices;
                    for (var s in slices) {
                        if (AnnotationsViewerService.checkContainment(slices[s].label, polygon_label)) {
                            vm.shape = AnnotationsViewerService.getShapeJSON(polygon_label);
                            console.log('FREEHAND SAVED ' + vm.shape);
                            vm._updateCoreData(polygon_label, slices[s]);
                            break;
                        }
                    }
                    if (typeof vm.shape === 'undefined') {
                        console.error('CORE IS NOT INSIDE A SLIDE');
                        AnnotationsViewerService.deleteShape(polygon_label);
                    }
                    vm.abortTool();
                    $canvas.unbind('freehand_polygon_saved');
                    $scope.$apply();
                }
            );
            vm.active_tool = vm.FREEHAND_TOOL;
        }

        function _updateCoreData(polygon_label, parent_slice) {
            vm.parentSlice = parent_slice;
            vm.coreArea = getAreaInSquareMillimiters(AnnotationsViewerService.getShapeArea(polygon_label), 3);
        }

        function initializeRuler() {
            AnnotationsViewerService.createRulerBindings('core_ruler_on', 'core_ruler_off',
                'core_ruler_output');
        }

        function startRuler() {
            var $ruler_out = $('#core_ruler_output');
            AnnotationsViewerService.extendRulerConfig(vm.shape_config);
            $ruler_out.on('ruler_cleared',
                function(event, ruler_saved) {
                    console.log('ruler_cleared trigger, ruler_saved value is ' + ruler_saved);
                    if (ruler_saved) {
                        console.log($ruler_out.data());
                        vm.coreLength = getLengthInMillimiters($ruler_out.data('measure'), 3);
                        console.log(vm.coreLength);
                        $ruler_out.unbind('ruler_clered');
                    }
                    $scope.$apply();
                }
            );
            vm.active_tool = vm.RULER_TOOL;
        }

        function isReadOnly() {
            return false;
        }

        function isPolygonToolActive() {
            return vm.active_tool === vm.POLYGON_TOOL;
        }

        function isFreehandToolActive() {
            return vm.active_tool === vm.FREEHAND_TOOL;
        }

        function isRulerToolActive() {
            return vm.active_tool === vm.RULER_TOOL;
        }

        function isPolygonToolPaused() {
            return vm.polygon_tool_paused;
        }

        function shapeExists() {
            return vm.shape !== undefined;
        }

        function coreLengthExists() {
            return vm.coreLength !== undefined;
        }

        function pausePolygonTool() {
            AnnotationsViewerService.disableActiveTool();
            vm.polygon_tool_paused = true;
        }

        function unpausePolygonTool() {
            AnnotationsViewerService.startPolygonsTool();
            vm.polygon_tool_paused = false;
        }

        function confirmPolygon() {
            var canvas_label = AnnotationsViewerService.getCanvasLabel();
            var $canvas = $("#" + canvas_label);
            $canvas.on('polygon_saved',
                function(event, polygon_label) {
                    var slices = $rootScope.slices;
                    for (var s in slices) {
                        if (AnnotationsViewerService.checkContainment(slices[s].label, polygon_label)) {
                            vm.shape = AnnotationsViewerService.getShapeJSON(polygon_label);
                            vm._updateCoreData(polygon_label, slices[s]);
                            break;
                        }
                    }
                    if (typeof vm.shape === 'undefined') {
                        console.error('CORE IS NOT INSIDE A SLIDE');
                        AnnotationsViewerService.deleteShape(polygon_label);
                    }
                    vm.abortTool();
                    $canvas.unbind('polygon_saved');
                }
            );
            AnnotationsViewerService.saveTemporaryPolygon('core');
        }

        function stopRuler() {
            AnnotationsViewerService.disableActiveTool();
            vm.active_tool = undefined;
        }

        function clear(destroy_shape) {
            vm.deleteShape(destroy_shape);
            vm.deleteRuler();
        }

        function abortTool() {
            if (vm.active_tool === vm.POLYGON_TOOL) {
                AnnotationsViewerService.clearTemporaryPolygon();
            }
            if (vm.active_tool === vm.RULER_TOOL) {
                vm.deleteRuler();
            }
            AnnotationsViewerService.disableActiveTool();
            vm.active_tool = undefined;
        }

        function destroy() {
            vm.clear(true);
            vm.abortTool();
            $rootScope.$broadcast('tool.destroyed');
        }

        function deleteShape(destroy_shape) {
            if (typeof vm.shape !== 'undefined') {
                if (destroy_shape === true) {
                    AnnotationsViewerService.deleteShape(vm.shape.shape_id);
                }
                vm.shape = undefined;
                vm.coreArea = undefined;
                vm.coreLength = undefined;
                vm.parentSlice = undefined;
            }
        }

        function deleteRuler() {
            if (typeof vm.coreLength !== 'undefined') {
                var $ruler_out = $('#core_ruler_output');
                $ruler_out.unbind('ruler_cleared');
                AnnotationsViewerService.clearRuler();
                $ruler_out.removeData('ruler_json')
                    .removeData('measure');
                vm.coreLength = undefined;
            }
        }

        function focusOnShape() {
            AnnotationsViewerService.focusOnShape(vm.shape.shape_id);
        }

        function formValid() {
            // if shape exists, we also have the parent slice and the shape area, we only need to check
            // for coreLength to decide if the form is valid
            return ((typeof vm.shape !== 'undefined') && (typeof vm.coreLength !== 'undefined'));
        }

        function save() {
            var dialog = ngDialog.open({
                template: '/static/templates/dialogs/saving_data.html',
                showClose: false,
                closeByEscape: false,
                closeByNavigation: false,
                closeByDocument: false
            });
            SlicesManagerService.createCore(vm.parentSlice.id, vm.shape.shape_id, vm.shape,
                vm.coreLength, vm.coreArea)
                .then(createCoreSuccessFn, createCoreErrorFn);

            function createCoreSuccessFn(response) {
                var core_info = {
                    'id': response.data.id,
                    'label': response.data.label,
                    'slice': response.data.slice
                };
                vm.clear(false);
                $rootScope.$broadcast('core.new', core_info);
                dialog.close();
            }

            function createCoreErrorFn(response) {
                console.error('Unable to save core!!!');
                console.error(response.data);
                $scope.closeThisDialog();
            }
        }
    }

    ShowCoreController.$inject = ['$scope', '$rootScope', 'ngDialog',
        'CoresManagerService', 'AnnotationsViewerService'];

    function ShowCoreController($scope, $rootScope, ngDialog,
                                CoresManagerService, AnnotationsViewerService) {
        var vm = this;
        vm.core_id = undefined;
        vm.label = undefined;
        vm.shape_id = undefined;
        vm.coreArea = undefined;
        vm.coreLength = undefined;

        vm.isReadOnly = isReadOnly;
        vm.shapeExists = shapeExists;
        vm.focusOnShape = focusOnShape;
        vm.deleteShape = deleteShape;

        activate();

        function activate() {
            $scope.$on('core.show',
                function(event, core_id) {
                    console.log('Show core ' + core_id);
                    vm.core_id = core_id;
                    CoresManagerService.get(core_id)
                        .then(getCoreSuccessFn, getCoreErrorFn);
                }
            );

            function getCoreSuccessFn(response) {
                vm.label = response.data.label;
                vm.shape_id = $.parseJSON(response.data.roi_json).shape_id;
                vm.coreArea = response.data.area;
                vm.coreLength = response.data.length;
            }

            function getCoreErrorFn(response) {
                console.error('Unable to load core data');
                console.error(response);
            }
        }

        function isReadOnly() {
            return true;
        }

        function shapeExists() {
            return (typeof vm.shape_id !== 'undefined');
        }

        function focusOnShape() {
            AnnotationsViewerService.focusOnShape(vm.shape_id);
        }

        function deleteShape() {
            ngDialog.openConfirm({
                template: '/static/templates/dialogs/delete_roi_confirm.html',
                closeByEscape: false,
                showClose: false,
                closeByNavigation: false,
                closeByDocument: false
            }).then(confirmFn);

            var dialog = undefined;
            function confirmFn(confirm_value) {
                if (confirm_value) {
                    dialog = ngDialog.open({
                        'template': '/static/templates/dialogs/deleting_data.html',
                        showClose: false,
                        closeByEscape: false,
                        closeByNavigation: false,
                        closeByDocument: false
                    });
                    CoresManagerService.cascadeDelete(vm.core_id)
                        .then(deleteCoreSuccessFn, deleteCoreErrorFn)
                }
            }

            function deleteCoreSuccessFn(response) {
                $rootScope.$broadcast('core.deleted', vm.core_id);
                vm.core_id = undefined;
                vm.label = undefined;
                vm.shape_id = undefined;
                vm.coreArea = undefined;
                vm.coreLength = undefined;
                dialog.close();
            }

            function deleteCoreErrorFn(response) {
                console.error('Unable to delete core');
                console.error(response);
                $scope.closeThisDialog();
            }
        }
    }

    NewFocusRegionController.$inject = ['$scope', '$rootScope', '$routeParams', 'ngDialog',
        'AnnotationsViewerService', 'CoresManagerService'];

    function NewFocusRegionController($scope, $rootScope, $routeParams, ngDialog,
                                      AnnotationsViewerService, CoresManagerService) {
        var vm = this;
        vm.slide_id = undefined;
        vm.case_id = undefined;
        vm.parentCore = undefined;
        vm.shape = undefined;
        vm.regionLength = undefined;
        vm.regionArea = undefined;
        vm.coreCoverage = undefined;
        vm.isTumor = false;

        vm.active_tool = undefined;
        vm.polygon_tool_paused = false;

        vm.POLYGON_TOOL = 'polygon_drawing_tool';
        vm.FREEHAND_TOOL = 'freehand_drawing_tool';
        vm.RULER_TOOL = 'ruler_tool';

        vm.shape_config = {
            'stroke_color': '#00ff00',
            'stroke_width': 20
        };

        vm._updateShapeConfig = _updateShapeConfig;
        vm.newPolygon = newPolygon;
        vm.newFreehand = newFreehand;
        vm._updateFocusRegionData = _updateFocusRegionData;
        vm.initializeRuler = initializeRuler;
        vm.startRuler = startRuler;
        vm.save = save;
        vm.isReadOnly = isReadOnly;
        vm.isPolygonToolActive = isPolygonToolActive;
        vm.isPolygonToolPaused = isPolygonToolPaused;
        vm.isFreehandToolActive = isFreehandToolActive;
        vm.isRulerToolActive = isRulerToolActive;
        vm.shapeExists = shapeExists;
        vm.regionLengthExists = regionLengthExists;
        vm.pausePolygonTool = pausePolygonTool;
        vm.unpausePolygonTool = unpausePolygonTool;
        vm.confirmPolygon = confirmPolygon;
        vm.stopRuler = stopRuler;
        vm.abortTool = abortTool;
        vm.clear = clear;
        vm.focusOnShape = focusOnShape;
        vm.deleteShape = deleteShape;
        vm.deleteRuler = deleteRuler;
        vm.formValid = formValid;
        vm.destroy = destroy;

        activate();

        function activate() {
            vm.slide_id = $routeParams.slide;
            vm.case_id = $routeParams.case;
            $scope.$on('viewerctrl.components.registered',
                function() {
                    vm.initializeRuler();
                }
            );
        }

        function _updateShapeConfig() {
            if (vm.isTumor) {
                vm.shape_config.stroke_color = '#ff0000';
            } else {
                vm.shape_config.stroke_color = '#32fc46';
            }
        }

        function newPolygon() {
            vm._updateShapeConfig();
            AnnotationsViewerService.extendPolygonConfig(vm.shape_config);
            AnnotationsViewerService.startPolygonsTool();
            vm.active_tool = vm.POLYGON_TOOL;
        }

        function newFreehand() {
            AnnotationsViewerService.setFreehandToolLabelPrefix('focus_region');
            vm._updateShapeConfig();
            AnnotationsViewerService.extendPathConfig(vm.shape_config);
            AnnotationsViewerService.startFreehandDrawingTool();
            var canvas_label = AnnotationsViewerService.getCanvasLabel();
            var $canvas = $("#" + canvas_label);
            $canvas.on('freehand_polygon_saved',
                function(event, polygon_label){
                    var cores = $rootScope.cores;
                    for (var c in cores) {
                        if (AnnotationsViewerService.checkContainment(cores[c].label, polygon_label)) {
                            vm.shape = AnnotationsViewerService.getShapeJSON(polygon_label);
                            vm._updateFocusRegionData(polygon_label, cores[c]);
                            break;
                        }
                    }
                    if (typeof vm.shape === 'undefined') {
                        console.error('FOCUS REGION IS NOT INSIDE A CORE');
                        AnnotationsViewerService.deleteShape(polygon_label);
                    }
                    vm.abortTool();
                    $canvas.unbind('freehand_polygon_saved');
                    $scope.$apply();
                }
            );
            vm.active_tool = vm.FREEHAND_TOOL;
        }

        function _updateFocusRegionData(polygon_label, parent_core) {
            vm.parentCore = parent_core;
            vm.regionArea = getAreaInSquareMillimiters(AnnotationsViewerService.getShapeArea(polygon_label), 3);
            vm.coreCoverage = AnnotationsViewerService.getAreaCoverage(vm.parentCore.label, polygon_label);
        }

        function initializeRuler() {
            AnnotationsViewerService.createRulerBindings('focus_region_ruler_on', 'focus_region_ruler_off',
                'focus_region_ruler_output');
        }

        function startRuler() {
            var $ruler_out = $('#focus_region_ruler_output');
            vm._updateShapeConfig();
            AnnotationsViewerService.extendRulerConfig(vm.shape_config);
            $ruler_out.on('ruler_cleared',
                function(event, ruler_saved) {
                    if (ruler_saved) {
                        vm.regionLength = getLengthInMillimiters($ruler_out.data('measure'), 3);
                        $ruler_out.unbind('ruler_cleared');
                    }
                    $scope.$apply();
                }
            );
            vm.active_tool = vm.RULER_TOOL;
        }

        function isReadOnly() {
            return false;
        }

        function isPolygonToolActive() {
            return vm.active_tool === vm.POLYGON_TOOL;
        }

        function isFreehandToolActive() {
            return vm.active_tool === vm.FREEHAND_TOOL;
        }

        function isRulerToolActive() {
            return vm.active_tool === vm.RULER_TOOL;
        }

        function isPolygonToolPaused() {
            return vm.polygon_tool_paused;
        }

        function shapeExists() {
            return vm.shape !== undefined;
        }

        function regionLengthExists() {
            return vm.regionLength !== undefined;
        }

        function pausePolygonTool() {
            AnnotationsViewerService.disableActiveTool();
            vm.polygon_tool_paused = true;
        }

        function unpausePolygonTool() {
            AnnotationsViewerService.startPolygonsTool();
            vm.polygon_tool_paused = false;
        }

        function confirmPolygon() {
            var canvas_label = AnnotationsViewerService.getCanvasLabel();
            var $canvas = $("#" + canvas_label);
            $canvas.on('polygon_saved',
                function(event, polygon_label) {
                    var cores = $rootScope.cores;
                    for (var c in cores) {
                        if (AnnotationsViewerService.checkContainment(cores[c].label, polygon_label)) {
                            vm.shape = AnnotationsViewerService.getShapeJSON(polygon_label);
                            vm._updateFocusRegionData(polygon_label, cores[c]);
                            break;
                        }
                    }
                    if (typeof vm.shape === 'undefined') {
                        console.error('FOCUS REGION IS NOT INSIDE A CORE');
                        AnnotationsViewerService.deleteShape(polygon_label);
                    }
                    vm.abortTool();
                    $canvas.unbind('polygon_saved');
                }
            );
            AnnotationsViewerService.saveTemporaryPolygon('focus_region');
        }

        function stopRuler() {
            AnnotationsViewerService.disableActiveTool();
            vm.active_tool = undefined;
        }

        function clear(destroy_shape) {
            vm.deleteShape(destroy_shape);
            vm.deleteRuler();
            vm.isTumor = false;
        }

        function abortTool() {
            if (vm.active_tool === vm.POLYGON_TOOL) {
                AnnotationsViewerService.clearTemporaryPolygon();
            }
            if (vm.active_tool === vm.RULER_TOOL) {
                vm.deleteRuler();
            }
            AnnotationsViewerService.disableActiveTool();
            vm.active_tool = undefined;
        }

        function destroy() {
            vm.clear(true);
            vm.abortTool();
            vm.isTumor = false;
            $rootScope.$broadcast('tool.destroyed');
        }

        function deleteShape(destroy_shape) {
            if (typeof vm.shape !== 'undefined') {
                if (destroy_shape === true) {
                    AnnotationsViewerService.deleteShape(vm.shape.shape_id);
                }
                vm.shape = undefined;
                vm.regionArea = undefined;
                vm.regionLength = undefined;
                vm.parentCore = undefined;
                vm.coreCoverage = undefined;
            }
        }

        function deleteRuler() {
            if (typeof vm.regionLength !== 'undefined') {
                var $ruler_out = $('#focus_region_ruler_output');
                $ruler_out.unbind('ruler_cleared');
                AnnotationsViewerService.clearRuler();
                $ruler_out.removeData('ruler_json')
                    .removeData('measure');
                vm.regionLength = undefined;
            }
        }

        function focusOnShape() {
            AnnotationsViewerService.focusOnShape(vm.shape.shape_id);
        }

        function save() {
            var dialog = ngDialog.open({
                template: '/static/templates/dialogs/saving_data.html',
                showClose: false,
                closeByEscape: false,
                closeByNavigation: false,
                closeByDocument: false
            });
            CoresManagerService.createFocusRegion(vm.parentCore.id, vm.shape.shape_id, vm.shape,
                vm.regionLength, vm.regionArea, vm.isTumor)
                .then(createFocusRegionSuccessFn, createFocusRegionErrorFn);

            function createFocusRegionSuccessFn(response) {
                var focus_region_info = {
                    'id': response.data.id,
                    'label': response.data.label,
                    'core': response.data.core
                };
                vm.clear(false);
                $rootScope.$broadcast('focus_region.new', focus_region_info);
                dialog.close();
            }

            function createFocusRegionErrorFn(response) {
                console.error('Unable to save focus region!!!');
                console.error(response.data);
                $scope.closeThisDialog();
            }
        }

        function formValid() {
            return ((typeof vm.shape !== 'undefined') && (typeof vm.regionLength !== 'undefined'));
        }
    }

    ShowFocusRegionController.$inject = ['$scope', '$rootScope', 'ngDialog',
        'FocusRegionsManagerService', 'AnnotationsViewerService'];

    function ShowFocusRegionController($scope, $rootScope, ngDialog,
                                       FocusRegionsManagerService, AnnotationsViewerService) {
        var vm = this;
        vm.focus_region_id = undefined;
        vm.parent_shape_id = undefined;
        vm.label = undefined;
        vm.shape_id = undefined;
        vm.regionArea = undefined;
        vm.regionLength = undefined;
        vm.coreCoverage = undefined;
        vm.isTumor = undefined;

        vm.isReadOnly = isReadOnly;
        vm.shapeExists = shapeExists;
        vm.focusOnShape = focusOnShape;
        vm.deleteShape = deleteShape;

        activate();

        function activate() {
            $scope.$on('focus_region.show',
                function (event, focus_region_id, parent_shape_id) {
                    console.log('Show focus region ' + focus_region_id);
                    vm.focus_region_id = focus_region_id;
                    vm.parent_shape_id = parent_shape_id;
                    FocusRegionsManagerService.get(focus_region_id)
                        .then(getFocusRegionSuccessFn, getFocusRegionErrorFn);
                }
            );

            function getFocusRegionSuccessFn(response) {
                vm.label = response.data.label;
                vm.shape_id = $.parseJSON(response.data.roi_json).shape_id;
                vm.regionArea = response.data.area;
                vm.regionLength = response.data.length;
                vm.isTumor = response.data.cancerous_region;
                vm.coreCoverage = AnnotationsViewerService.getAreaCoverage(vm.parent_shape_id, vm.shape_id);
            }

            function getFocusRegionErrorFn(response) {
                console.error('Unable to load focus region data');
                console.error(response);
            }
        }

        function isReadOnly() {
            return true;
        }

        function shapeExists() {
            return (typeof vm.shape_id !== 'undefined');
        }

        function focusOnShape() {
            AnnotationsViewerService.focusOnShape(vm.shape_id);
        }

        function deleteShape() {
            ngDialog.openConfirm({
                template: '/static/templates/dialogs/delete_roi_confirm.html',
                closeByEscape: false,
                showClose: false,
                closeByNavigation: false,
                closeByDocument: false
            }).then(confirmFn);

            var dialog = undefined;
            function confirmFn(confirm_value) {
                if (confirm_value) {
                    dialog = ngDialog.open({
                        'template': '/static/templates/dialogs/deleting_data.html',
                        showClose: false,
                        closeByEscape: false,
                        closeByNavigation: false,
                        closeByDocument: false
                    });
                    FocusRegionsManagerService.cascadeDelete(vm.focus_region_id)
                        .then(deleteFocusRegionSuccessFn, deleteFocusRegionErrorFn);
                }
            }

            function deleteFocusRegionSuccessFn(response) {
                $rootScope.$broadcast('focus_region.deleted', vm.focus_region_id);
                vm.focus_region_id = undefined;
                vm.parent_shape_id = undefined;
                vm.label = undefined;
                vm.shape_id = undefined;
                vm.regionArea = undefined;
                vm.regionLength = undefined;
                vm.coreCoverage = undefined;
                vm.isTumor = false;
                dialog.close();
            }

            function deleteFocusRegionErrorFn(response) {
                console.error('Unable to delete focus region');
                console.error(response);
                $scope.closeThisDialog();
            }
        }
    }
})();