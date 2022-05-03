/*
 * Copyright (c) 2019, CRS4
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of
 * this software and associated documentation files (the "Software"), to deal in
 * the Software without restriction, including without limitation the rights to
 * use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
 * the Software, and to permit persons to whom the Software is furnished to do so,
 * subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
 * FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
 * COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
 * IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
 * CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */

(function () {
    'use strict';

    angular
        .module('promort.rois_manager.controllers')
        .controller('ROIsManagerController', ROIsManagerController)
        .controller('NewScopeController', NewScopeController)
        .controller('NewSliceController', NewSliceController)
        .controller('EditSliceController', EditSliceController)
        .controller('ShowSliceController', ShowSliceController)
        .controller('NewCoreController', NewCoreController)
        .controller('EditCoreController', EditCoreController)
        .controller('ShowCoreController', ShowCoreController)
        .controller('NewFocusRegionController', NewFocusRegionController)
        .controller('EditFocusRegionController', EditFocusRegionController)
        .controller('ShowFocusRegionController', ShowFocusRegionController);

    ROIsManagerController.$inject = ['$scope', '$routeParams', '$rootScope', '$compile', '$location', '$log',
        'ngDialog', 'ROIsAnnotationStepService', 'ROIsAnnotationStepManagerService',
        'AnnotationsViewerService', 'CurrentSlideDetailsService', 'CurrentPredictionDetailsService',
        'HeatmapViewerService'];

    function ROIsManagerController($scope, $routeParams, $rootScope, $compile, $location, $log, ngDialog,
                                   ROIsAnnotationStepService, ROIsAnnotationStepManagerService,
                                   AnnotationsViewerService, CurrentSlideDetailsService,
                                   CurrentPredictionDetailsService, HeatmapViewerService) {
        var vm = this;
        vm.slide_id = undefined;
        vm.slide_index = undefined;
        vm.case_id = undefined;
        vm.annotation_label = undefined;
        vm.annotation_step_label = undefined;

        vm.prediction_id = undefined;
        vm.overlay_palette = undefined;
        vm.overlay_opacity = undefined;
        vm.overlay_threshold = undefined;
        vm.navmap_cluster_size = undefined;

        vm.oo_percentage = undefined;

        vm.slices_map = undefined;
        vm.cores_map = undefined;
        vm.focus_regions_map = undefined;

        vm.displayNavmap = undefined;

        vm.navmap_items = undefined;
        vm.navmap_items_label = undefined;

        vm.navmap_selected_item = undefined;

        vm.ui_active_modes = {
            'new_slice': false,
            'new_core': false,
            'new_focus_region': false,
            'show_slice': false,
            'show_core': false,
            'show_focus_region': false,
            'edit_slice': false,
            'edit_core': false,
            'edit_focus_region': false
        };
        vm.roisTreeLocked = false;

        vm._createListItem = _createListItem;
        vm._createNewSubtree = _createNewSubtree;
        vm._lockRoisTree = _lockRoisTree;
        vm._unlockRoisTree = _unlockRoisTree;
        vm._drawNavmapItem = _drawNavmapItem;
        vm._drawNavmap = _drawNavmap;
        vm._deleteNavmapItem = _deleteNavmapItem;
        vm._hideNavmap = _hideNavmap;
        vm._clearNavmap = _clearNavmap;
        vm._updateNavmap = _updateNavmap;
        vm.navmapDisplayEnabled = navmapDisplayEnabled;
        vm.switchNavmapDisplay = switchNavmapDisplay;
        vm.jumpToNextNavmapItem = jumpToNextNavmapItem;
        vm.jumpToPreviousNavmapItem = jumpToPreviousNavmapItem;
        vm.jumpToNavmapItem = jumpToNavmapItem;
        vm.jumpToSelectedNavmapItem = jumpToSelectedNavmapItem;
        vm.noNavmapItemSelected = noNavmapItemSelected;
        vm.showSelectedNavmapItem = showSelectedNavmapItem;
        vm.hideSelectedNavmapItem = hideSelectedNavmapItem;
        vm.selectNavmapItem = selectNavmapItem;
        vm.deselectNavmapItem = deselectNavmapItem;
        vm.isFirstItemSelected = isFirstItemSelected;
        vm.isLastItemSelected = isLastItemSelected;
        vm.allModesOff = allModesOff;
        vm.showROI = showROI;
        vm.editROI = editROI;
        vm.selectROI = selectROI;
        vm.deselectROI = deselectROI;
        vm.clearROIs = clearROIs;
        vm.closeROIsAnnotationStep = closeROIsAnnotationStep;
        vm.activateNewSliceMode = activateNewSliceMode;
        vm.newSliceModeActive = newSliceModeActive;
        vm.activateShowSliceMode = activateShowSliceMode;
        vm.showSliceModeActive = showSliceModeActive;
        vm.activateEditSliceMode = activateEditSliceMode;
        vm.editSliceModeActive = editSliceModeActive;
        vm.activateNewCoreMode = activateNewCoreMode;
        vm.newCoreModeActive = newCoreModeActive;
        vm.activateShowCoreMode = activateShowCoreMode;
        vm.showCoreModeActive = showCoreModeActive;
        vm.activateEditCoreMode = activateEditCoreMode;
        vm.editCoreModeActive = editCoreModeActive;
        vm.activateNewFocusRegionMode = activateNewFocusRegionMode;
        vm.newFocusRegionModeActive = newFocusRegionModeActive;
        vm.activateShowFocusRegionMode = activateShowFocusRegionMode;
        vm.showFocusRegionModeActive = showFocusRegionModeActive;
        vm.activateEditFocusRegionMode = activateEditFocusRegionMode;
        vm.editFocusRegionModeActive = editFocusRegionModeActive;
        vm.newItemCreationModeActive = newItemCreationModeActive;
        vm.editItemModeActive = editItemModeActive;
        vm._registerNavmapItem = _registerNavmapItem;
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

        vm.updateOverlayOpacity = updateOverlayOpacity;
        vm.updateOverlayThreshold = updateOverlayThreshold;
        vm.updateNavmapClusterSize = updateNavmapClusterSize;
        vm.updateOverlayPalette = updateOverlayPalette;

        activate();

        function activate() {
            console.log("Prediction ID: " + CurrentPredictionDetailsService.getPredictionId());

            vm.slide_id = CurrentSlideDetailsService.getSlideId();
            vm.case_id = CurrentSlideDetailsService.getCaseId();
            vm.annotation_step_label = $routeParams.label;
            vm.annotation_label = vm.annotation_step_label.split('-')[0];
            vm.slide_index = vm.annotation_step_label.split('-')[1];

            vm.prediction_id = CurrentPredictionDetailsService.getPredictionId();

            vm.overlay_palette = 'Greens_9';
            vm.overlay_opacity = 0.5;
            vm.overlay_threshold = "0.5";
            vm.navmap_cluster_size = "2";

            vm.oo_percentage = Math.floor(vm.overlay_opacity * 100);

            vm.slices_map = {};
            vm.cores_map = {};
            vm.focus_regions_map = {};

            vm.displayNavmap = false;
            vm.navmap_items = {};
            vm.navmap_items_label = [];

            $rootScope.slices = [];
            $rootScope.cores = [];
            $rootScope.focus_regions = [];

            ROIsAnnotationStepService.getDetails(vm.annotation_step_label)
                .then(getROIsAnnotationStepSuccessFn, getROIsAnnotationStepErrorFn);

            function getROIsAnnotationStepSuccessFn(response) {
                if (response.data.completed === true) {
                    $location.url('worklist/rois_annotations/' + vm.annotation_label);
                }

                if (response.data.slide_evaluation !== null &&
                    response.data.slide_evaluation.adequate_slide) {

                    $scope.$on('hm_viewerctrl.components.registered',
                        function() {
                            // load navigation map
                            $log.info('Building navigation map');
                            HeatmapViewerService.getShapesFromPrediction(vm.overlay_threshold, vm.navmap_cluster_size)
                                .then(getShapesSuccessFn, getShapesErrorFn);

                            function getShapesSuccessFn(response) {
                                for (var sh in response.data.shapes) {
                                    vm._registerNavmapItem(sh, response.data.shapes[sh]);
                                }
                            }

                            function getShapesErrorFn(response) {
                                $log.error('Error when loading shapes from prediction');
                                $log.error(response);
                            }
                        }
                    );

                    // shut down creation forms when specific events occur
                    $scope.$on('tool.destroyed',
                        function () {
                            vm.allModesOff();
                        }
                    );

                    $scope.$on('slice.new',
                        function (event, slice_info) {
                            vm._registerSlice(slice_info);
                            vm.allModesOff();
                            // add new item to ROIs tree
                            var $tree = $("#rois_tree");
                            var $new_slice_item = $(vm._createListItem(slice_info.label, true));
                            var $anchor = $new_slice_item.find('a');
                            $anchor.attr('ng-click', 'rmc.showROI("slice", ' + slice_info.id + ')')
                                .attr('ng-mouseenter', 'rmc.selectROI("slice", ' + slice_info.id + ')')
                                .attr('ng-mouseleave', 'rmc.deselectROI("slice", ' + slice_info.id + ')');
                            $compile($anchor)($scope);
                            var new_slice_subtree = vm._createNewSubtree(slice_info.label);
                            $new_slice_item.append(new_slice_subtree);
                            $tree.append($new_slice_item);
                        }
                    );

                    $scope.$on('slice.show',
                        function (event, slice_id) {
                            vm._unlockRoisTree();
                            vm.showROI('slice', slice_id);
                        }
                    );

                    $scope.$on('slice.deleted',
                        function (event, slice_id) {
                            $log.debug('SLICE ' + slice_id + ' DELETED');
                            var cores = _getSliceCores(slice_id);
                            cores.forEach(
                                function (item, index) {
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
                        function (event, core_info) {
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

                    $scope.$on('core.show',
                        function (event, core_id) {
                            vm._unlockRoisTree();
                            vm.showROI('core', core_id);
                        }
                    );

                    $scope.$on('core.deleted',
                        function (event, core_id) {
                            $log.debug('CORE ' + core_id + ' DELETED');
                            var focus_regions = _getCoreFocusRegions(core_id);
                            focus_regions.forEach(
                                function (item, index) {
                                    $log.debug('Broadcasting delete evento for focus region ' + item.id);
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
                        function (event, focus_region_info) {
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

                    $scope.$on('focus_region.show',
                        function (event, focus_region_id, parent_shape_id) {
                            vm._unlockRoisTree();
                            vm.showROI('focus_region', focus_region_id, parent_shape_id);
                        }
                    );

                    $scope.$on('focus_region.deleted',
                        function (event, focus_region_id) {
                            $log.debug('FOCUS REGION ' + focus_region_id + ' DELETED');
                            AnnotationsViewerService.deleteShape(vm._getFocusRegionLabel(focus_region_id));
                            $("#" + vm._getFocusRegionLabel(focus_region_id) + "_list").remove();
                            vm._unregisterFocusRegion(focus_region_id);
                            vm.allModesOff();
                        }
                    );

                    $scope.$on('edit.activate',
                        function (event, roi_info) {
                            vm.editROI(roi_info['roi_type'], roi_info['roi_id'], roi_info['parent_shape_id']);
                        }
                    );
                } else {
                    $location.url('worklist');
                }
            }

            function getROIsAnnotationStepErrorFn(response) {
                $log.error('Cannot load slide info');
                $log.error(response);
            }
        }

        function _registerNavmapItem(item_index, item_shape) {
            var item_label = 'cluster_' + (parseInt(item_index)+1);
            vm.navmap_items[item_label] = item_shape;
            vm.navmap_items_label.push(item_label);
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
            $log.debug($rootScope.focus_regions);
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

        function _drawNavmapItem(item_label, hidden) {
            if (hidden==true) {
                var stroke_alpha = 0;
            } else {
                var stroke_alpha = 1;
            }
            var item_shape = vm.navmap_items[item_label];
            var shape_json = {
                'shape_id': item_label,
                'fill_color': '#fff',
                'fill_alpha': 0.0,
                'stroke_color': '#0000ff',
                'stroke_alpha': stroke_alpha,
                'stroke_width': 50,
                'hidden': false,
                'segments': item_shape,
                'type': 'polygon'
            };
            AnnotationsViewerService.drawShape(shape_json);
        }

        function _deleteNavmapItem(item_label) {
            AnnotationsViewerService.deleteShape(item_label);
        }

        function _drawNavmap() {
            for (var ilabel in vm.navmap_items) {
                vm._drawNavmapItem(ilabel, false);
            }
        }

        function _hideNavmap() {
            for (var sh in vm.navmap_items) {
                vm._deleteNavmapItem(sh);
            }
        }

        function _clearNavmap() {
            for (var sh in vm.navmap_items) {
                vm._deleteNavmapItem(sh);
            }
            vm.navmap_items = {};
            vm.navmap_items_label = [];
            vm.navmap_selected_item = undefined;
        }

        function _updateNavmap(new_shapes) {
            vm._clearNavmap();
            $("#selected_navmap_item").text("-- Select an item --");
            for (var sh in new_shapes) {
                vm._registerNavmapItem(sh, new_shapes[sh]);
            }
            if (vm.navmapDisplayEnabled()) {
                vm._drawNavmap();
            }
        }

        function navmapDisplayEnabled() {
            return vm.displayNavmap;
        }

        function switchNavmapDisplay() {
            console.log('Switching navmap display');
            vm.displayNavmap = !vm.displayNavmap;
            if (vm.navmapDisplayEnabled()) {
                console.log('Draw navmap');
                vm._drawNavmap();
            } else {
                console.log('Hide navmap');
                vm._hideNavmap();
            }
        }

        function jumpToNextNavmapItem() {
            var next_item_label = vm.navmap_items_label[vm.navmap_items_label.indexOf(vm.navmap_selected_item)+1];
            if(!vm.navmapDisplayEnabled()) {
                vm._drawNavmapItem(next_item_label, true);
            }
            vm.jumpToNavmapItem(next_item_label);
            if(!vm.navmapDisplayEnabled()) {
                vm._deleteNavmapItem(next_item_label);
            }
        }

        function jumpToPreviousNavmapItem() {
            var prev_item_label = vm.navmap_items_label[vm.navmap_items_label.indexOf(vm.navmap_selected_item)-1];
            if(!vm.navmapDisplayEnabled()) {
                vm._drawNavmapItem(prev_item_label, true);
            }
            vm.jumpToNavmapItem(prev_item_label);
            if(!vm.navmapDisplayEnabled()) {
                vm._deleteNavmapItem(prev_item_label);
            }
        }

        function jumpToNavmapItem(label) {
            vm.navmap_selected_item = label;
            $("#selected_navmap_item").text(label);
            vm.jumpToSelectedNavmapItem();
        }

        function jumpToSelectedNavmapItem() {
            AnnotationsViewerService.focusOnShape(vm.navmap_selected_item);
        }

        function noNavmapItemSelected() {
            return vm.navmap_selected_item == undefined;
        }

        function showSelectedNavmapItem() {
            if(!vm.noNavmapItemSelected()) {
                vm.selectNavmapItem(vm.navmap_selected_item);
            }
        }

        function hideSelectedNavmapItem() {
            if(!vm.noNavmapItemSelected()) {
                vm.deselectNavmapItem(vm.navmap_selected_item);
            }
        }

        function selectNavmapItem(label) {
            if(!vm.navmapDisplayEnabled()) {
                vm._drawNavmapItem(label, true);
            }
            AnnotationsViewerService.selectShape(label);
        }

        function deselectNavmapItem(label) {
            AnnotationsViewerService.deselectShape(label);
            if(!vm.navmapDisplayEnabled()) {
                vm._deleteNavmapItem(label);
            }
        }

        function isFirstItemSelected() {
            return (vm.navmap_items_label.indexOf(vm.navmap_selected_item) == 0);
        }

        function isLastItemSelected() {
            return (vm.navmap_items_label.indexOf(vm.navmap_selected_item) == (vm.navmap_items_label.length - 1));
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

        function editROI(roi_type, roi_id, parent_roi_id) {
            if (!vm.roisTreeLocked) {
                switch (roi_type) {
                    case 'slice':
                        activateEditSliceMode(roi_id);
                        AnnotationsViewerService.focusOnShape(vm._getSliceLabel(roi_id));
                        break;
                    case 'core':
                        activateEditCoreMode(roi_id);
                        AnnotationsViewerService.focusOnShape(vm._getCoreLabel(roi_id));
                        break;
                    case 'focus_region':
                        activateEditFocusRegionMode(roi_id, parent_roi_id);
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

            function confirmFn(confirm_value) {
                if (confirm_value) {
                    var dialog = ngDialog.open({
                        template: '/static/templates/dialogs/deleting_data.html',
                        showClose: false,
                        closeByEscape: false,
                        closeByNavigation: false,
                        closeByDocument: false
                    });

                    ROIsAnnotationStepManagerService.clearROIs(vm.annotation_step_label)
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
                    $log.error('Clear ROIs failed');
                    $log.error(response);
                    dialog.close();
                }
            }
        }

        function closeROIsAnnotationStep() {
            ngDialog.openConfirm({
                template: '/static/templates/dialogs/accept_rois_confirm.html',
                showClose: false,
                closeByEscape: false,
                closeByNavigation: false,
                closeByDocument: false
            }).then(confirmFn);

            function confirmFn(confirm_value) {
                if (confirm_value) {
                    ROIsAnnotationStepService.closeAnnotationStep(vm.annotation_step_label)
                        .then(closeROIsAnnotationStepSuccessFn, closeROIsAnnotationStepErrorFn);
                }

                function closeROIsAnnotationStepSuccessFn(response) {
                    if (response.data.rois_annotation_closed === true) {
                        $location.url('worklist');
                    } else {
                        // review closed, go back to case worklist
                        $location.url('worklist/rois_annotations/' + vm.annotation_label);
                    }
                }

                function closeROIsAnnotationStepErrorFn(response) {
                    $log.error(response.error);
                }
            }
        }

        function activateNewSliceMode() {
            vm.allModesOff();
            vm._lockRoisTree();
            vm.ui_active_modes['new_slice'] = true;
            $rootScope.$broadcast('slice.creation_mode');
        }

        function newSliceModeActive() {
            return vm.ui_active_modes['new_slice'];
        }

        function activateShowSliceMode(slice_id) {
            vm.allModesOff();
            $rootScope.$broadcast('slice.load', slice_id);
            vm.ui_active_modes['show_slice'] = true;
        }

        function showSliceModeActive() {
            return vm.ui_active_modes['show_slice'];
        }

        function activateEditSliceMode(slice_id) {
            vm.allModesOff();
            vm._lockRoisTree();
            vm.ui_active_modes['edit_slice'] = true;
            $rootScope.$broadcast('slice.edit', slice_id);
        }

        function editSliceModeActive() {
            return vm.ui_active_modes['edit_slice'];
        }

        function activateNewCoreMode() {
            vm.allModesOff();
            vm._lockRoisTree();
            vm.ui_active_modes['new_core'] = true;
            $rootScope.$broadcast('core.creation_mode');
        }

        function newCoreModeActive() {
            return vm.ui_active_modes['new_core'];
        }

        function activateShowCoreMode(core_id) {
            vm.allModesOff();
            $rootScope.$broadcast('core.load', core_id);
            vm.ui_active_modes['show_core'] = true;
        }

        function showCoreModeActive() {
            return vm.ui_active_modes['show_core'];
        }

        function activateEditCoreMode(core_id) {
            vm.allModesOff();
            vm._lockRoisTree();
            vm.ui_active_modes['edit_core'] = true;
            $rootScope.$broadcast('core.edit', core_id);
        }

        function editCoreModeActive() {
            return vm.ui_active_modes['edit_core'];
        }

        function activateNewFocusRegionMode() {
            vm.allModesOff();
            vm._lockRoisTree();
            vm.ui_active_modes['new_focus_region'] = true;
            $rootScope.$broadcast('focus_region.creation_mode');
        }

        function newFocusRegionModeActive() {
            return vm.ui_active_modes['new_focus_region'];
        }

        function activateShowFocusRegionMode(focus_region_id, parent_core_id) {
            vm.allModesOff();
            $rootScope.$broadcast('focus_region.load', focus_region_id, parent_core_id);
            vm.ui_active_modes['show_focus_region'] = true;
        }

        function showFocusRegionModeActive() {
            return vm.ui_active_modes['show_focus_region'];
        }

        function activateEditFocusRegionMode(focus_region_id, parent_shape_id) {
            vm.allModesOff();
            vm._lockRoisTree();
            vm.ui_active_modes['edit_focus_region'] = true;
            $rootScope.$broadcast('focus_region.edit', focus_region_id, parent_shape_id);
        }

        function editFocusRegionModeActive() {
            return vm.ui_active_modes['edit_focus_region'];
        }

        function newItemCreationModeActive() {
            return (
                vm.ui_active_modes['new_slice']
                || vm.ui_active_modes['new_core']
                || vm.ui_active_modes['new_focus_region']
            );
        }

        function editItemModeActive() {
            return (
                vm.ui_active_modes['edit_slice']
                || vm.ui_active_modes['edit_core']
                || vm.ui_active_modes['edit_focus_region']
            );
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

        function updateOverlayOpacity() {
            HeatmapViewerService.setOverlayOpacity(vm.overlay_opacity);
            vm.oo_percentage = Math.floor(vm.overlay_opacity * 100);
        }

        function updateOverlayThreshold() {
            HeatmapViewerService.setOverlay(vm.overlay_palette, vm.overlay_threshold);

            HeatmapViewerService.getShapesFromPrediction(vm.overlay_threshold, vm.navmap_cluster_size)
                                .then(getShapesSuccessFn, getShapesErrorFn);

            function getShapesSuccessFn(response) {
                vm._updateNavmap(response.data.shapes);
            }

            function getShapesErrorFn(response) {
                $log.error('Error when loading shapes from prediction');
                $log.error(response);
            }
        }

        function updateNavmapClusterSize() {
            HeatmapViewerService.getShapesFromPrediction(vm.overlay_threshold, vm.navmap_cluster_size)
                                .then(getShapesSuccessFn, getShapesErrorFn);

            function getShapesSuccessFn(response) {
                vm._updateNavmap(response.data.shapes);
            }

            function getShapesErrorFn(response) {
                $log.error('Error when loading shapes from prediction');
                $log.error(response);
            }
        }

        function updateOverlayPalette() {
            console.log('Current overlay palette is: ' + vm.overlay_palette);
            HeatmapViewerService.setOverlay(vm.overlay_palette, vm.overlay_threshold);
        }
    }

    NewScopeController.$inject = ['$scope', '$log',];

    function NewScopeController($scope, $log) {
        var vm = this;
        vm.$scope = {};
    }

    NewSliceController.$inject = ['$scope', '$routeParams', '$rootScope', '$log', 'ngDialog',
        'AnnotationsViewerService', 'ROIsAnnotationStepManagerService', 'CurrentSlideDetailsService'];

    function NewSliceController($scope, $routeParams, $rootScope, $log, ngDialog, AnnotationsViewerService,
                                ROIsAnnotationStepManagerService, CurrentSlideDetailsService) {
        var vm = this;
        vm.slide_id = undefined;
        vm.case_id = undefined;
        vm.annotation_step_label = undefined;
        vm.default_shape_label = undefined;
        vm.shape_label = undefined;
        vm.shape = undefined;
        vm.totalCores = 0;

        vm.actionStartTime = undefined;

        vm.edit_shape_label = false;
        vm.previous_shape_label = undefined;

        vm.active_tool = undefined;
        vm.polygon_tool_paused = false;
        vm.freehand_tool_paused = false;

        vm.POLYGON_TOOL = 'polygon_drawing_tool';
        vm.FREEHAND_TOOL = 'freehand_drawing_tool';

        vm.shape_config = {
            'stroke_color': '#000000',
            'stroke_width': 40
        };

        vm.newPolygon = newPolygon;
        vm.newFreehand = newFreehand;
        vm.activateEditLabelMode = activateEditLabelMode;
        vm.labelValid = labelValid;
        vm.setNewLabel = setNewLabel;
        vm.deactivateEditLabelMode = deactivateEditLabelMode;
        vm.abortEditLabelMode = abortEditLabelMode;
        vm.resetLabel = resetLabel;
        vm.isEditLabelModeActive = isEditLabelModeActive;
        vm.save = save;
        vm.isReadOnly = isReadOnly;
        vm.isEditMode = isEditMode;
        vm.isPolygonToolActive = isPolygonToolActive;
        vm.isPolygonToolPaused = isPolygonToolPaused;
        vm.isFreehandToolActive = isFreehandToolActive;
        vm.isFreehandToolPaused =isFreehandToolPaused;
        vm.temporaryPolygonExists = temporaryPolygonExists;
        vm.temporaryPolygonValid = temporaryPolygonValid;
        vm.temporaryShapeExists = temporaryShapeExists;
        vm.temporaryShapeValid = temporaryShapeValid;
        vm.drawInProgress = drawInProgress;
        vm.shapeExists = shapeExists;
        vm.pausePolygonTool = pausePolygonTool;
        vm.unpausePolygonTool = unpausePolygonTool;
        vm.pauseFreehandTool = pauseFreehandTool;
        vm.unpauseFreehandTool = unpauseFreehandTool;
        vm.confirmPolygon = confirmPolygon;
        vm.confirmFreehandShape = confirmFreehandShape;
        vm.polygonRollbackPossible = polygonRollbackPossible;
        vm.polygonRestorePossible = polygonRestorePossible;
        vm.shapeRollbackPossible = shapeRollbackPossible;
        vm.shapeRestorePossible = shapeRestorePossible;
        vm.rollbackPolygon = rollbackPolygon;
        vm.restorePolygon = restorePolygon;
        vm.rollbackFreehandShape = rollbackFreehandShape;
        vm.restoreFreehandShape = restoreFreehandShape;
        vm.abortTool = abortTool;
        vm.clear = clear;
        vm.focusOnShape = focusOnShape;
        vm.deleteShape = deleteShape;
        vm.formValid = formValid;
        vm.destroy = destroy;

        activate();

        function activate() {
            vm.slide_id = CurrentSlideDetailsService.getSlideId();
            vm.case_id = CurrentSlideDetailsService.getCaseId();
            vm.annotation_step_label = $routeParams.label;
            $scope.$on('slice.creation_mode',
                function() {
                    vm.default_shape_label = AnnotationsViewerService.getFirstAvailableLabel('slice');
                    vm.shape_label = vm.default_shape_label;
                    vm.actionStartTime = new Date();
                }
            );
        }

        function newPolygon() {
            $log.debug('Start polygon drawing tool');
            AnnotationsViewerService.extendPolygonConfig(vm.shape_config);
            AnnotationsViewerService.startPolygonsTool();
            vm.active_tool = vm.POLYGON_TOOL;
            var canvas_label = AnnotationsViewerService.getCanvasLabel();
            var $canvas = $('#' + canvas_label);
            $canvas
                .on('polygon_created',
                    function() {
                        $canvas.unbind('polygon_created');
                        $scope.$apply();
                    }
                )
                .on('polygon_add_point',
                    function() {
                        $scope.$apply();
                    }
                );
        }

        function newFreehand() {
            $log.debug('Start freehand drawing tool');
            AnnotationsViewerService.setFreehandToolLabelPrefix('slice');
            AnnotationsViewerService.extendPathConfig(vm.shape_config);
            AnnotationsViewerService.startFreehandDrawingTool();
            var canvas_label = AnnotationsViewerService.getCanvasLabel();
            var $canvas = $('#' + canvas_label);
            $canvas.on('freehand_polygon_paused',
                function(event, polygon_label) {
                    AnnotationsViewerService.disableActiveTool();
                    vm.freehand_tool_paused = true;
                    $scope.$apply();
                }
            );
            vm.active_tool = vm.FREEHAND_TOOL;
        }

        function activateEditLabelMode() {
            vm.edit_shape_label = true;
            vm.previous_shape_label = vm.shape_label;
        }

        function labelValid() {
            return ((typeof vm.shape_label !== 'undefined') &&
                (vm.shape_label.length > 0 && vm.shape_label.length <= 25));
        }

        function setNewLabel() {
            if (typeof vm.shape !== 'undefined' && vm.shape_label === vm.shape.shape_id) {
                $log.debug('Shape label not changed');
                vm.deactivateEditLabelMode();
            } else {
                if (AnnotationsViewerService.shapeIdAvailable(vm.shape_label)) {
                    $log.debug('Label available, assigning to new shape');
                    vm.deactivateEditLabelMode();
                } else {
                    $log.debug('Label in use, restoring previous label');
                    vm.abortEditLabelMode();
                    ngDialog.open({
                        'template': '/static/templates/dialogs/invalid_label.html'
                    });
                }
            }
        }

        function deactivateEditLabelMode() {
            vm.previous_shape_label = undefined;
            vm.edit_shape_label = false;
            // if a shape already exists, change its name
            if (typeof vm.shape !== 'undefined' && vm.shape.shape_id !== vm.shape_label) {
                $log.debug('updating shape id');
                AnnotationsViewerService.changeShapeId(vm.shape.shape_id, vm.shape_label);
                vm.shape = AnnotationsViewerService.getShapeJSON(vm.shape_label);
                $log.debug('new shape id is: ' + vm.shape.shape_id);
            }
        }

        function abortEditLabelMode() {
            vm.shape_label = vm.previous_shape_label;
            vm.deactivateEditLabelMode();
        }

        function resetLabel() {
            vm.shape_label = vm.default_shape_label;
            vm.deactivateEditLabelMode();
        }

        function isEditLabelModeActive() {
            return vm.edit_shape_label;
        }

        function isReadOnly() {
            return false;
        }

        function isEditMode() {
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

        function isFreehandToolPaused() {
            return vm.freehand_tool_paused;
        }

        function temporaryPolygonExists() {
            return AnnotationsViewerService.temporaryPolygonExists();
        }

        function temporaryPolygonValid() {
            return AnnotationsViewerService.temporaryPolygonValid();
        }

        function temporaryShapeExists() {
            return AnnotationsViewerService.tmpFreehandPathExists();
        }

        function temporaryShapeValid() {
            return AnnotationsViewerService.tmpFreehandPathValid();
        }

        function drawInProgress() {
            return vm.isPolygonToolActive() || vm.isPolygonToolPaused() ||
                vm.isFreehandToolActive() || vm.isFreehandToolPaused();
        }

        function shapeExists() {
            return typeof vm.shape !==  'undefined';
        }

        function pausePolygonTool() {
            AnnotationsViewerService.disableActiveTool();
            vm.polygon_tool_paused = true;
        }

        function unpausePolygonTool() {
            AnnotationsViewerService.startPolygonsTool();
            vm.polygon_tool_paused = false;
        }

        function pauseFreehandTool() {
            AnnotationsViewerService.disableActiveTool();
            if (vm.temporaryShapeExists()) {
                AnnotationsViewerService.deactivatePreviewMode();
            }
            vm.freehand_tool_paused = true;
        }

        function unpauseFreehandTool() {
            AnnotationsViewerService.startFreehandDrawingTool();
            if (vm.temporaryShapeExists()) {
                AnnotationsViewerService.activatePreviewMode();
            }
            vm.freehand_tool_paused = false;
        }

        function confirmPolygon() {
            var canvas_label = AnnotationsViewerService.getCanvasLabel();
            var $canvas = $('#' + canvas_label);
            $canvas.on('polygon_saved',
                function(event, polygon_label) {
                    if (vm.shape_label !== polygon_label) {
                        AnnotationsViewerService.changeShapeId(polygon_label, vm.shape_label);
                        vm.shape = AnnotationsViewerService.getShapeJSON(vm.shape_label);
                    } else {
                        vm.shape = AnnotationsViewerService.getShapeJSON(polygon_label);
                    }
                    vm.abortTool();
                }
            );
            AnnotationsViewerService.saveTemporaryPolygon('slice');
        }

        function confirmFreehandShape() {
            var canvas_label = AnnotationsViewerService.getCanvasLabel();
            var $canvas = $('#' + canvas_label);
            $canvas.on('freehand_polygon_saved',
                function(event, polygon_label) {
                    if (vm.shape_label !== polygon_label) {
                        AnnotationsViewerService.changeShapeId(polygon_label, vm.shape_label);
                        vm.shape = AnnotationsViewerService.getShapeJSON(vm.shape_label);
                    } else {
                        vm.shape = AnnotationsViewerService.getShapeJSON(polygon_label);
                    }
                    vm.abortTool();
                }
             );
            AnnotationsViewerService.saveTemporaryFreehandShape();
        }

        function polygonRollbackPossible() {
            return AnnotationsViewerService.temporaryPolygonExists();
        }

        function polygonRestorePossible() {
            return AnnotationsViewerService.polygonRestoreHistoryExists();
        }

        function shapeRollbackPossible() {
            return (AnnotationsViewerService.tmpFreehandPathExists() ||
                AnnotationsViewerService.shapeUndoHistoryExists());
        }

        function shapeRestorePossible() {
            return AnnotationsViewerService.shapeRestoreHistoryExists();
        }

        function rollbackPolygon() {
            AnnotationsViewerService.rollbackPolygon();
        }

        function restorePolygon() {
            AnnotationsViewerService.restorePolygon();
        }

        function rollbackFreehandShape() {
            AnnotationsViewerService.rollbackTemporaryFreehandShape();
        }

        function restoreFreehandShape() {
            AnnotationsViewerService.restoreTemporaryFreehandShape();
        }

        function clear(destroy_shape) {
            vm.deleteShape(destroy_shape);
            vm.totalCores = 0;
            vm.shape_label = undefined;
            vm.default_shape_label = undefined;
            vm.actionStartTime = undefined;
        }

        function abortTool() {
            if (vm.active_tool === vm.POLYGON_TOOL) {
                AnnotationsViewerService.clearTemporaryPolygon();
                $("#" + AnnotationsViewerService.getCanvasLabel()).unbind('polygon_saved');
            }
            if (vm.active_tool === vm.FREEHAND_TOOL) {
                AnnotationsViewerService.clearTemporaryFreehandShape();
                $("#" + AnnotationsViewerService.getCanvasLabel())
                    .unbind('freehand_polygon_saved')
                    .unbind('freehand_polygon_paused');
            }
            AnnotationsViewerService.disableActiveTool();
            vm.active_tool = undefined;
            vm.polygon_tool_paused = false;
            vm.freehand_tool_paused = false;
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
            return (typeof vm.shape !== 'undefined') && !vm.isEditLabelModeActive();
        }

        function save() {
            var dialog = undefined;
            dialog = ngDialog.open({
                template: '/static/templates/dialogs/saving_data.html',
                showClose: false,
                closeByEscape: false,
                closeByNavigation: false,
                closeByDocument: false
            });
            ROIsAnnotationStepManagerService.createSlice(vm.annotation_step_label, vm.slide_id, vm.shape.shape_id,
                vm.shape, vm.totalCores, vm.actionStartTime, new Date())
                .then(createSliceSuccessFn, createSliceErrorFn);

            function createSliceSuccessFn(response) {
                var slice_info = {
                    'id': response.data.id,
                    'label': response.data.label,
                    'annotated': false
                };
                vm.clear(false);
                $rootScope.$broadcast('slice.new', slice_info);
                dialog.close();
            }

            function createSliceErrorFn(response) {
                $log.error('Unable to save slice!!!');
                $log.error(response.data);
                dialog.close();
            }
        }
    }

    EditSliceController.$inject = ['$scope', '$rootScope', '$log', 'ngDialog', 'SlicesManagerService',
        'AnnotationsViewerService'];

    function EditSliceController($scope, $rootScope, $log, ngDialog, SlicesManagerService, AnnotationsViewerService) {
        var vm = this;
        vm.slice_id = undefined;
        vm.label = undefined;
        vm.shape_id = undefined;
        vm.totalCores = undefined;

        vm.isReadOnly = isReadOnly;
        vm.isEditMode = isEditMode;
        vm.shapeExists = shapeExists;
        vm.focusOnShape = focusOnShape;
        vm.formValid = formValid;
        vm.abortEdit = abortEdit;
        vm.updateROI = updateROI;

        activate();

        function activate() {
            $scope.$on('slice.edit',
                function(event, slice_id) {
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
                $log.error('Unable to load slice data');
                $log.error(response);
            }
        }

        function isReadOnly() {
            return false;
        }

        function isEditMode() {
            return true;
        }

        function shapeExists() {
            return (typeof vm.shape_id !== 'undefined');
        }

        function focusOnShape() {
            AnnotationsViewerService.focusOnShape(vm.shape_id);
        }

        function formValid() {
            return true;
        }

        function abortEdit() {
            $rootScope.$broadcast('slice.show', vm.slice_id);
            vm.slice_id = undefined;
            vm.label = undefined;
            vm.shape_id = undefined;
            vm.totalCores = undefined;
        }

        function updateROI() {
            SlicesManagerService.update(vm.slice_id, vm.totalCores).
                then(updateSliceSuccessFn, updateSliceErrorFn);

            function updateSliceSuccessFn(response) {
                vm.abortEdit();
            }

            function updateSliceErrorFn(response) {
                $log.error('Unable to update slice data');
                $log.error(response);
            }
        }
    }

    ShowSliceController.$inject = ['$scope', '$rootScope', '$log', 'ngDialog', 'SlicesManagerService',
        'AnnotationsViewerService'];

    function ShowSliceController($scope, $rootScope, $log, ngDialog, SlicesManagerService, AnnotationsViewerService) {
        var vm = this;
        vm.slice_id = undefined;
        vm.label = undefined;
        vm.shape_id = undefined;
        vm.totalCores = undefined;

        vm.isReadOnly = isReadOnly;
        vm.isEditMode = isEditMode;
        vm.shapeExists = shapeExists;
        vm.focusOnShape = focusOnShape;
        vm.editROI = editROI;
        vm.deleteShape = deleteShape;

        activate();

        function activate() {
            $scope.$on('slice.load',
                function(event, slice_id) {
                    $log.debug('Show slice ' + slice_id);
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
                $log.error('Unable to load slice data');
                $log.error(response);
            }
        }

        function isReadOnly() {
            return true;
        }

        function isEditMode() {
            return false;
        }

        function shapeExists() {
            return (typeof vm.shape_id !== 'undefined');
        }

        function focusOnShape() {
            AnnotationsViewerService.focusOnShape(vm.shape_id);
        }

        function editROI() {
            $rootScope.$broadcast('edit.activate', {'roi_type': 'slice', 'roi_id': vm.slice_id});
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
                        template: '/static/templates/dialogs/deleting_data.html',
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
                $log.error('unable to delete slice');
                $log.error(response);
                dialog.close();
            }
        }
    }

    NewCoreController.$inject = ['$scope', '$routeParams', '$rootScope', '$log', 'ngDialog',
        'AnnotationsViewerService', 'SlicesManagerService', 'CurrentSlideDetailsService'];

    function NewCoreController($scope, $routeParams, $rootScope, $log, ngDialog, AnnotationsViewerService,
                               SlicesManagerService, CurrentSlideDetailsService) {
        var vm = this;
        vm.slide_id = undefined;
        vm.case_id = undefined;
        vm.parentSlice = undefined;
        vm.shape_label = undefined;
        vm.default_shape_label = undefined;
        vm.shape = undefined;
        vm.coreLength = undefined;
        vm.coreArea = undefined;
        vm.tumorLength = undefined;

        vm.actionStartTime = undefined;

        vm.scaledCoreLength = undefined;
        vm.coreLengthScaleFactor = undefined;
        vm.scaledTumorLength = undefined;
        vm.tumorLengthScaleFactor = undefined;
        vm.scaledCoreArea = undefined;
        vm.coreAreaScaleFactor = undefined;

        vm.lengthUOM = [
            { id: 1, unit_of_measure: 'μm' },
            { id: Math.pow(10, -3), unit_of_measure: 'mm' }
        ];

        vm.areaUOM = [
            { id: 1, unit_of_measure: 'μm²'},
            { id: Math.pow(10, -6), unit_of_measure: 'mm²'}
        ];

        vm.ruler_on_id = 'new_core_ruler_on';
        vm.ruler_off_id = 'new_core_ruler_off';
        vm.ruler_output_id = 'new_core_ruler_output';
        vm.tumor_ruler_on_id = 'new_core_tumor_ruler_on';
        vm.tumor_ruler_off_id = 'new_core_tumor_ruler_off';
        vm.tumor_ruler_output_id = 'new_core_tumor_ruler_output';

        vm.tmp_ruler_exists  =false;

        vm.active_tool = undefined;
        vm.polygon_tool_paused = false;
        vm.freehand_tool_paused = false;
        vm.ruler_tool_paused = false;
        vm.tumor_ruler_tool_paused = false;

        vm.POLYGON_TOOL = 'polygon_drawing_tool';
        vm.FREEHAND_TOOL = 'freehand_drawing_tool';
        vm.RULER_TOOL = 'ruler_tool';
        vm.TUMOR_RULER_TOOL = 'tumor_ruler_tool';

        vm.shape_config = {
            'stroke_color': '#0000ff',
            'stroke_width': 30
        };

        vm.newPolygon = newPolygon;
        vm.newFreehand = newFreehand;
        vm.activateEditLabelMode = activateEditLabelMode;
        vm.labelValid = labelValid;
        vm.setNewLabel = setNewLabel;
        vm.deactivateEditLabelMode = deactivateEditLabelMode;
        vm.abortEditLabelMode = abortEditLabelMode;
        vm.resetLabel = resetLabel;
        vm.isEditLabelModeActive = isEditLabelModeActive;
        vm._updateCoreData = _updateCoreData;
        vm.getRulerOnId = getRulerOnId;
        vm.getRulerOffId = getRulerOffId;
        vm.getRulerOutputId = getRulerOutputId;
        vm.getTumorRulerOnId = getTumorRulerOnId;
        vm.getTumorRulerOffId = getTumorRulerOffId;
        vm.getTumorRulerOutputId = getTumorRulerOutputId;
        vm.initializeRuler = initializeRuler;
        vm.initializeTumorRuler = initializeTumorRuler;
        vm.startRuler = startRuler;
        vm.pauseRulerTool = pauseRulerTool;
        vm.resumeRulerTool = resumeRulerTool;
        vm.isRulerToolPaused = isRulerToolPaused;
        vm.startTumorRuler = startTumorRuler;
        vm.pauseTumorRulerTool = pauseTumorRulerTool;
        vm.resumeTumorRulerTool = resumeTumorRulerTool;
        vm.isTumorRulerToolPaused = isTumorRulerToolPaused;
        vm.save = save;
        vm.isReadOnly = isReadOnly;
        vm.isEditMode = isEditMode;
        vm.isPolygonToolActive = isPolygonToolActive;
        vm.isPolygonToolPaused = isPolygonToolPaused;
        vm.isFreehandToolActive = isFreehandToolActive;
        vm.isFreehandToolPaused =isFreehandToolPaused;
        vm.isRulerToolActive = isRulerToolActive;
        vm.isTumorRulerToolActive = isTumorRulerToolActive;
        vm.temporaryPolygonExists = temporaryPolygonExists;
        vm.temporaryPolygonValid = temporaryPolygonValid;
        vm.temporaryShapeExists = temporaryShapeExists;
        vm.temporaryShapeValid = temporaryShapeValid;
        vm.drawInProgress = drawInProgress;
        vm.shapeExists = shapeExists;
        vm.temporaryRulerExists = temporaryRulerExists;
        vm.coreLengthExists = coreLengthExists;
        vm.tumorLengthExists = tumorLengthExists;
        vm.pausePolygonTool = pausePolygonTool;
        vm.unpausePolygonTool = unpausePolygonTool;
        vm.pauseFreehandTool = pauseFreehandTool;
        vm.unpauseFreehandTool = unpauseFreehandTool;
        vm.confirmPolygon = confirmPolygon;
        vm.confirmFreehandShape = confirmFreehandShape;
        vm.polygonRollbackPossible = polygonRollbackPossible;
        vm.polygonRestorePossible = polygonRestorePossible;
        vm.shapeRollbackPossible = shapeRollbackPossible;
        vm.shapeRestorePossible = shapeRestorePossible;
        vm.rollbackPolygon = rollbackPolygon;
        vm.restorePolygon = restorePolygon;
        vm.rollbackFreehandShape = rollbackFreehandShape;
        vm.restoreFreehandShape = restoreFreehandShape;
        vm.stopRuler = stopRuler;
        vm.stopTumorRuler = stopTumorRuler;
        vm.abortTool = abortTool;
        vm.clear = clear;
        vm.focusOnShape = focusOnShape;
        vm.deleteShape = deleteShape;
        vm._unbindRulers = _unbindRulers;
        vm.deleteRuler = deleteRuler;
        vm.deleteTumorRuler = deleteTumorRuler;
        vm.formValid = formValid;
        vm.destroy = destroy;
        vm.updateTumorLength = updateTumorLength;
        vm.updateCoreLength = updateCoreLength;
        vm.updateCoreArea = updateCoreArea;

        activate();

        function activate() {
            vm.slide_id = CurrentSlideDetailsService.getSlideId();
            vm.case_id = CurrentSlideDetailsService.getCaseId();

            vm.coreLengthScaleFactor = vm.lengthUOM[0];
            vm.tumorLengthScaleFactor = vm.lengthUOM[0];
            vm.coreAreaScaleFactor = vm.areaUOM[0];

            $scope.$on('rois_viewerctrl.components.registered',
                function() {
                    vm.initializeRuler();
                    vm.initializeTumorRuler();
                }
            );

            $scope.$on('core.creation_mode',
                function() {
                    vm.default_shape_label = AnnotationsViewerService.getFirstAvailableLabel('core');
                    vm.shape_label = vm.default_shape_label;
                    vm.actionStartTime = new Date();
                }
            );
        }

        function newPolygon() {
            AnnotationsViewerService.extendPolygonConfig(vm.shape_config);
            AnnotationsViewerService.startPolygonsTool();
            vm.active_tool = vm.POLYGON_TOOL;
            var canvas_label = AnnotationsViewerService.getCanvasLabel();
            var $canvas = $("#" + canvas_label);
            $canvas.on('polygon_created',
                function() {
                    $canvas.unbind('polygon_created');
                    $scope.$apply();
                }
            )
            .on('polygon_add_point',
                function() {
                    $scope.$apply();
                }
            );
        }

        function newFreehand() {
            AnnotationsViewerService.setFreehandToolLabelPrefix('core');
            AnnotationsViewerService.extendPathConfig(vm.shape_config);
            AnnotationsViewerService.startFreehandDrawingTool();
            var canvas_label = AnnotationsViewerService.getCanvasLabel();
            var $canvas = $("#" + canvas_label);
            $canvas.on('freehand_polygon_paused',
                function(event, polygon_label) {
                    AnnotationsViewerService.disableActiveTool();
                    vm.freehand_tool_paused = true;
                    $scope.$apply();
                }
            );
            vm.active_tool = vm.FREEHAND_TOOL;
        }

        function _updateCoreData(polygon_label, parent_slice) {
            vm.parentSlice = parent_slice;
            vm.coreArea = AnnotationsViewerService.getShapeArea(polygon_label);
            vm.updateCoreArea();
        }

        function getRulerOnId() {
            return vm.ruler_on_id;
        }

        function getRulerOffId() {
            return vm.ruler_off_id;
        }

        function getRulerOutputId() {
            return vm.ruler_output_id;
        }

        function getTumorRulerOnId() {
            return vm.tumor_ruler_on_id;
        }

        function getTumorRulerOffId() {
            return vm.tumor_ruler_off_id;
        }

        function getTumorRulerOutputId() {
            return vm.tumor_ruler_output_id;
        }

        function initializeRuler() {
            AnnotationsViewerService.createRulerBindings(vm.getRulerOnId(), vm.getRulerOffId(),
                vm.getRulerOutputId());
        }

        function initializeTumorRuler() {
            AnnotationsViewerService.createRulerBindings(vm.getTumorRulerOnId(), vm.getTumorRulerOffId(),
                vm.getTumorRulerOutputId());
        }

        function startRuler() {
            var $ruler_out = $('#' + vm.getRulerOutputId());
            AnnotationsViewerService.extendRulerConfig(vm.shape_config);
            $ruler_out.on('ruler_created',
                function() {
                    if (vm.isRulerToolActive()) {
                        vm.tmp_ruler_exists = true;
                        $ruler_out.unbind('ruler_created');
                        $scope.$apply();
                    }
                }
            );
            $ruler_out.on('ruler_updated',
                function() {
                    vm.coreLength = $ruler_out.data('measure');
                    vm.updateCoreLength();
                    $scope.$apply();
                }
            );
            $ruler_out.on('ruler_cleared',
                function(event, ruler_saved) {
                    if (ruler_saved) {
                        $ruler_out.unbind('ruler_cleared');
                        $ruler_out.unbind('ruler_updated');
                    }
                }
            );
            vm.active_tool = vm.RULER_TOOL;
        }

        function pauseRulerTool() {
            AnnotationsViewerService.disableActiveTool();
            vm.ruler_tool_paused = true;
        }

        function resumeRulerTool() {
            AnnotationsViewerService.startRuler();
            vm.ruler_tool_paused = false;
        }

        function isRulerToolPaused() {
            return vm.ruler_tool_paused;
        }

        function startTumorRuler() {
            var $tumor_ruler_out = $('#' + vm.getTumorRulerOutputId());
            AnnotationsViewerService.extendRulerConfig(vm.shape_config);
            $tumor_ruler_out.on('ruler_created',
                function() {
                    if (vm.isTumorRulerToolActive()) {
                        vm.tmp_ruler_exists = true;
                        $tumor_ruler_out.unbind('ruler_created');
                        $scope.$apply();
                    }
                }
            );
            $tumor_ruler_out.on('ruler_updated',
                function() {
                    vm.tumorLength = $tumor_ruler_out.data('measure');
                    vm.updateTumorLength();
                    $scope.$apply();
                }
            );
            $tumor_ruler_out.on('ruler_cleared',
                function(event, ruler_saved){
                    if (ruler_saved) {
                        $tumor_ruler_out.unbind('ruler_cleared');
                        $tumor_ruler_out.unbind('ruler_updated');
                    }
                }
            );
            vm.active_tool = vm.TUMOR_RULER_TOOL;
        }

        function pauseTumorRulerTool() {
            AnnotationsViewerService.disableActiveTool();
            vm.tumor_ruler_tool_paused = true;
        }

        function resumeTumorRulerTool() {
            AnnotationsViewerService.startRuler();
            vm.tumor_ruler_tool_paused = false;
        }

        function isTumorRulerToolPaused() {
            return vm.tumor_ruler_tool_paused;
        }

        function activateEditLabelMode() {
            vm.edit_shape_label = true;
            vm.previuos_shape_label = vm.shape_label;
        }

        function labelValid() {
            return ((typeof vm.shape_label !== 'undefined') &&
                (vm.shape_label.length > 0 && vm.shape_label.length <= 25));
        }

        function setNewLabel() {
            if (typeof vm.shape !== 'undefined' && vm.shape_label === vm.shape.shape_id){
                $log.debug('Shape label not changed');
                vm.deactivateEditLabelMode();
            } else {
                if (AnnotationsViewerService.shapeIdAvailable(vm.shape_label)) {
                    $log.debug('Label available, assigning to new shape');
                    vm.deactivateEditLabelMode();
                } else {
                    $log.debug('Label in use, restoring previous label');
                    vm.abortEditLabelMode();
                    ngDialog.open({
                        'template': '/static/templates/dialogs/invalid_label.html'
                    });
                }
            }
        }

        function deactivateEditLabelMode() {
            vm.previuos_shape_label = undefined;
            vm.edit_shape_label = false;
            // if a shape already exists, change its name
            if (typeof vm.shape !== 'undefined' && vm.shape.shape_id !== vm.shape_label) {
                $log.debug('updating shape id');
                AnnotationsViewerService.changeShapeId(vm.shape.shape_id, vm.shape_label);
                vm.shape = AnnotationsViewerService.getShapeJSON(vm.shape_label);
                $log.debug('new shape id is: ' + vm.shape.shape_id);
            }
        }

        function abortEditLabelMode() {
            vm.shape_label = vm.previuos_shape_label;
            vm.deactivateEditLabelMode();
        }

        function resetLabel() {
            vm.shape_label = vm.default_shape_label;
            vm.deactivateEditLabelMode();
        }

        function isEditLabelModeActive() {
            return vm.edit_shape_label;
        }

        function isReadOnly() {
            return false;
        }

        function isEditMode() {
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

        function isTumorRulerToolActive() {
            return vm.active_tool === vm.TUMOR_RULER_TOOL;
        }

        function isPolygonToolPaused() {
            return vm.polygon_tool_paused;
        }

        function isFreehandToolPaused() {
            return vm.freehand_tool_paused;
        }

        function temporaryPolygonExists() {
            return AnnotationsViewerService.temporaryPolygonExists();
        }

        function temporaryPolygonValid() {
            return AnnotationsViewerService.temporaryPolygonValid();
        }

        function temporaryShapeExists() {
            return AnnotationsViewerService.tmpFreehandPathExists();
        }

        function temporaryShapeValid() {
            return AnnotationsViewerService.tmpFreehandPathValid();
        }

        function drawInProgress() {
            return vm.isPolygonToolActive() || vm.isPolygonToolPaused() || vm.isFreehandToolActive() ||
                vm.isFreehandToolPaused() || vm.isRulerToolActive() || vm.isTumorRulerToolActive();
        }

        function shapeExists() {
            return vm.shape !== undefined;
        }

        function temporaryRulerExists() {
            if (vm.active_tool === vm.RULER_TOOL) {
                return vm.tmp_ruler_exists && vm.coreLength > 0;
            } else if (vm.active_tool === vm.TUMOR_RULER_TOOL) {
                return vm.tmp_ruler_exists && vm.tumorLength > 0;
            } else {
                return false;
            }
        }

        function coreLengthExists() {
            return vm.coreLength !== undefined;
        }

        function tumorLengthExists() {
            return vm.tumorLength !== undefined;
        }

        function pausePolygonTool() {
            AnnotationsViewerService.disableActiveTool();
            vm.polygon_tool_paused = true;
        }

        function unpausePolygonTool() {
            AnnotationsViewerService.startPolygonsTool();
            vm.polygon_tool_paused = false;
        }

        function pauseFreehandTool() {
            AnnotationsViewerService.disableActiveTool();
            if (vm.temporaryShapeExists()) {
                AnnotationsViewerService.deactivatePreviewMode();
            }
            vm.freehand_tool_paused = true;
        }

        function unpauseFreehandTool() {
            AnnotationsViewerService.startFreehandDrawingTool();
            if (vm.temporaryShapeExists()) {
                AnnotationsViewerService.activatePreviewMode();
            }
            vm.freehand_tool_paused = false;
        }

        function confirmPolygon() {
            ngDialog.open({
                template: '/static/templates/dialogs/rois_check.html',
                showClose: false,
                closeByEscape: false,
                closeByNavigation: false,
                closeByDocument: false,
                name: 'checkCore',
                onOpenCallback: function () {
                    var canvas_label = AnnotationsViewerService.getCanvasLabel();
                    var $canvas = $("#" + canvas_label);
                    $canvas.on('polygon_saved',
                        function (event, polygon_label) {
                            var slices = $rootScope.slices;
                            for (var s in slices) {
                                if (AnnotationsViewerService.checkContainment(slices[s].label, polygon_label) ||
                                    AnnotationsViewerService.checkContainment(polygon_label, slices[s].label)) {
                                    AnnotationsViewerService.adaptToContainer(slices[s].label, polygon_label);
                                    if (vm.shape_label !== polygon_label) {
                                        AnnotationsViewerService.changeShapeId(polygon_label, vm.shape_label);
                                        vm.shape = AnnotationsViewerService.getShapeJSON(vm.shape_label);
                                    } else {
                                        vm.shape = AnnotationsViewerService.getShapeJSON(polygon_label);
                                    }
                                    vm._updateCoreData(vm.shape.shape_id, slices[s]);
                                    break;
                                }
                            }
                            ngDialog.close('checkCore');
                            if (typeof vm.shape === 'undefined') {
                                AnnotationsViewerService.deleteShape(polygon_label);
                                ngDialog.open({
                                    'template': '/static/templates/dialogs/invalid_core.html'
                                });
                            }
                            vm.abortTool();
                            $scope.$apply();
                        }
                    );
                    setTimeout(function () {
                        AnnotationsViewerService.saveTemporaryPolygon('core');
                    }, 1);
                }
            });
        }

        function confirmFreehandShape() {
            ngDialog.open({
                template: '/static/templates/dialogs/rois_check.html',
                showClose: false,
                closeByEscape: false,
                closeByNavigation: false,
                closeByDocument: false,
                name: 'checkCore',
                onOpenCallback: function () {
                    var canvas_label = AnnotationsViewerService.getCanvasLabel();
                    var $canvas = $('#' + canvas_label);
                    $canvas.on('freehand_polygon_saved',
                        function (event, polygon_label) {
                            var slices = $rootScope.slices;
                            for (var s in slices) {
                                if (AnnotationsViewerService.checkContainment(slices[s].label, polygon_label) ||
                                    AnnotationsViewerService.checkContainment(polygon_label, slices[s].label)) {
                                    AnnotationsViewerService.adaptToContainer(slices[s].label, polygon_label);
                                    if (vm.shape_label !== polygon_label) {
                                        AnnotationsViewerService.changeShapeId(polygon_label, vm.shape_label);
                                        vm.shape = AnnotationsViewerService.getShapeJSON(polygon_label);
                                    } else {
                                        vm.shape = AnnotationsViewerService.getShapeJSON(polygon_label);
                                    }
                                    vm._updateCoreData(vm.shape.shape_id, slices[s]);
                                    break;
                                }
                            }
                            ngDialog.close('checkCore');
                            if (typeof vm.shape === 'undefined') {
                                AnnotationsViewerService.deleteShape(polygon_label);
                                ngDialog.open({
                                    template: '/static/templates/dialogs/invalid_core.html'
                                });
                            }
                            vm.abortTool();
                            $scope.$apply();
                        }
                    );
                    setTimeout(function () {
                        AnnotationsViewerService.saveTemporaryFreehandShape();
                    }, 1);
                }
            });
        }

        function polygonRollbackPossible() {
            return AnnotationsViewerService.temporaryPolygonExists();
        }

        function polygonRestorePossible() {
            return AnnotationsViewerService.polygonRestoreHistoryExists();
        }

        function shapeRollbackPossible() {
            return (AnnotationsViewerService.tmpFreehandPathExists() ||
                AnnotationsViewerService.shapeUndoHistoryExists());
        }

        function shapeRestorePossible() {
            return AnnotationsViewerService.shapeRestoreHistoryExists();
        }

        function rollbackPolygon() {
            AnnotationsViewerService.rollbackPolygon();
        }

        function restorePolygon() {
            AnnotationsViewerService.restorePolygon();
        }

        function rollbackFreehandShape() {
            AnnotationsViewerService.rollbackTemporaryFreehandShape();
        }

        function restoreFreehandShape() {
            AnnotationsViewerService.restoreTemporaryFreehandShape();
        }

        function stopRuler() {
            AnnotationsViewerService.disableActiveTool();
            vm.active_tool = undefined;
            vm.tmp_ruler_exists = false;
            vm.ruler_tool_paused = false;
        }

        function stopTumorRuler() {
            AnnotationsViewerService.disableActiveTool();
            vm.active_tool = undefined;
            vm.tmp_ruler_exists = false;
            vm.tumor_ruler_tool_paused = false;
        }

        function clear(destroy_shape) {
            vm.deleteShape(destroy_shape);
            vm.deleteRuler();
            vm.deleteTumorRuler();
            vm.shape_label = undefined;
            vm.default_shape_label = undefined;
            vm.actionStartTime = undefined;
        }

        function abortTool() {
            if (vm.active_tool === vm.POLYGON_TOOL) {
                AnnotationsViewerService.clearTemporaryPolygon();
                $("#" + AnnotationsViewerService.getCanvasLabel()).unbind('polygon_saved');
            }
            if (vm.active_tool === vm.FREEHAND_TOOL) {
                AnnotationsViewerService.clearTemporaryFreehandShape();
                $("#" + AnnotationsViewerService.getCanvasLabel())
                    .unbind('freehand_polygon_saved')
                    .unbind('freehand_polygon_paused');
            }
            if (vm.active_tool === vm.RULER_TOOL) {
                vm.deleteRuler();
            }
            if (vm.active_tool === vm.TUMOR_RULER_TOOL) {
                vm.deleteTumorRuler();
            }
            AnnotationsViewerService.disableActiveTool();
            vm.active_tool = undefined;
            vm.polygon_tool_paused = false;
            vm.tmp_ruler_exists = false;
            vm.freehand_tool_paused = false;
            vm.ruler_tool_paused = false;
            vm.tumor_ruler_tool_paused = false;
        }

        function destroy() {
            vm._unbindRulers();
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
                vm.scaledCoreArea = undefined;
                vm.coreLength = undefined;
                vm.scaledCoreLength = undefined;
                vm.tumorLength = undefined;
                vm.scaledTumorLength = undefined;
                vm.parentSlice = undefined;
            }
        }

        function _unbindRulers() {
            $("#core_ruler_output")
                .unbind('ruler_cleared')
                .unbind('ruler_updated');
            $("#tumor_ruler_output")
                .unbind('ruler_cleared')
                .unbind('ruler_updated');
        }

        function deleteRuler() {
            var $ruler_out = $('#core_ruler_output');
            $ruler_out.unbind('ruler_updated');
            $ruler_out.unbind('ruler_cleared');
            AnnotationsViewerService.clearRuler();
            if (typeof vm.coreLength !== 'undefined') {
                $ruler_out.removeData('ruler_json')
                    .removeData('measure');
                vm.coreLength = undefined;
                vm.scaledCoreLength = undefined;
            }
            vm.tmp_ruler_exists = false;
        }

        function deleteTumorRuler() {
            var $tumor_ruler_out = $("#tumor_ruler_output");
            $tumor_ruler_out.unbind('ruler_updated');
            $tumor_ruler_out.unbind('ruler_cleared');
            AnnotationsViewerService.clearRuler();
            if (typeof vm.tumorLength !== 'undefined') {
                $tumor_ruler_out.removeData('ruler_json')
                    .removeData('measure');
                vm.tumorLength = undefined;
                vm.scaledTumorLength = undefined;
            }
            vm.tmp_ruler_exists = false;
        }

        function focusOnShape() {
            AnnotationsViewerService.focusOnShape(vm.shape.shape_id);
        }

        function formValid() {
            // if tumor ruler tool is active, "Save" button should be disabled
            if (vm.isTumorRulerToolActive() || vm.isRulerToolActive()) {
                return false;
            }
            // if shape exists, we also have the parent slice and the shape area, we only need to check
            // for coreLength to decide if the form is valid
            return (typeof vm.shape !== 'undefined') && (typeof vm.coreLength !== 'undefined') &&
                !vm.isEditLabelModeActive();
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
                vm.coreLength, vm.coreArea, vm.tumorLength, vm.actionStartTime, new Date())
                .then(createCoreSuccessFn, createCoreErrorFn);

            function createCoreSuccessFn(response) {
                var core_info = {
                    'id': response.data.id,
                    'label': response.data.label,
                    'slice': response.data.slice,
                    'annotated': false
                };
                vm.clear(false);
                $rootScope.$broadcast('core.new', core_info);
                dialog.close();
            }

            function createCoreErrorFn(response) {
                $log.error('Unable to save core!!!');
                $log.error(response.data);
                dialog.close();
            }
        }

        function updateCoreLength() {
            vm.scaledCoreLength = formatDecimalNumber(
                (vm.coreLength * vm.coreLengthScaleFactor.id), 3
            );
        }

        function updateTumorLength() {
            vm.scaledTumorLength = formatDecimalNumber(
                (vm.tumorLength * vm.tumorLengthScaleFactor.id), 3
            );
        }

        function updateCoreArea() {
            vm.scaledCoreArea = formatDecimalNumber(
                (vm.coreArea * vm.coreAreaScaleFactor.id), 3
            );
        }
    }

    EditCoreController.$inject = ['$scope', '$rootScope', '$log', 'ngDialog', 'CoresManagerService',
        'AnnotationsViewerService'];

    function EditCoreController($scope, $rootScope, $log, ngDialog, CoresManagerService, AnnotationsViewerService) {
        var vm = this;
        vm.core_id = undefined;
        vm.label = undefined;
        vm.shape_id = undefined;
        vm.coreArea = undefined;
        vm.coreLength = undefined;
        vm.tumorLength = undefined;

        vm.scaledCoreLength = undefined;
        vm.coreLengthScaleFactor = undefined;
        vm.scaledTumorLength = undefined;
        vm.tumorLengthScaleFactor = undefined;
        vm.scaledCoreArea = undefined;
        vm.coreAreaScaleFactor = undefined;

        vm.lengthUOM = [
            { id: 1, unit_of_measure: 'μm' },
            { id: Math.pow(10, -3), unit_of_measure: 'mm' }
        ];

        vm.areaUOM = [
            { id: 1, unit_of_measure: 'μm²'},
            { id: Math.pow(10, -6), unit_of_measure: 'mm²'}
        ];

        vm.ruler_on_id = 'edit_core_ruler_on';
        vm.ruler_off_id = 'edit_core_ruler_off';
        vm.ruler_output_id = 'edit_core_ruler_output';
        vm.tumor_ruler_on_id = 'edit_core_tumor_ruler_on';
        vm.tumor_ruler_off_id = 'edit_core_tumor_ruler_off';
        vm.tumor_ruler_output_id = 'edit_core_tumor_ruler_output';

        vm.tmp_ruler_exists  =false;

        vm.active_tool = undefined;
        vm.ruler_tool_paused = false;
        vm.tumor_ruler_tool_paused = false;

        vm.RULER_TOOL = 'ruler_tool';
        vm.TUMOR_RULER_TOOL = 'tumor_ruler_tool';

        vm.shape_config = {
            'stroke_color': '#0000ff',
            'stroke_width': 30
        };

        vm.isReadOnly = isReadOnly;
        vm.isEditMode = isEditMode;
        vm.shapeExists = shapeExists;
        vm.focusOnShape = focusOnShape;
        vm.updateTumorLength = updateTumorLength;
        vm.updateCoreLength = updateCoreLength;
        vm.updateCoreArea = updateCoreArea;
        vm.getRulerOnId = getRulerOnId;
        vm.getRulerOffId = getRulerOffId;
        vm.getRulerOutputId = getRulerOutputId;
        vm.getTumorRulerOnId = getTumorRulerOnId;
        vm.getTumorRulerOffId = getTumorRulerOffId;
        vm.getTumorRulerOutputId = getTumorRulerOutputId;
        vm.initializeRuler = initializeRuler;
        vm.initializeTumorRuler = initializeTumorRuler;
        vm.startRuler = startRuler;
        vm.pauseRulerTool = pauseRulerTool;
        vm.resumeRulerTool = resumeRulerTool;
        vm.isRulerToolPaused = isRulerToolPaused;
        vm.startTumorRuler = startTumorRuler;
        vm.pauseTumorRulerTool = pauseTumorRulerTool;
        vm.resumeTumorRulerTool = resumeTumorRulerTool;
        vm.isTumorRulerToolPaused = isTumorRulerToolPaused;
        vm.isRulerToolActive = isRulerToolActive;
        vm.isTumorRulerToolActive = isTumorRulerToolActive;
        vm.coreLengthExists = coreLengthExists;
        vm.tumorLengthExists = tumorLengthExists;
        vm.temporaryRulerExists = temporaryRulerExists;
        vm.stopRuler = stopRuler;
        vm.stopTumorRuler = stopTumorRuler;
        vm.abortTool = abortTool;
        vm._unbindRulers = _unbindRulers;
        vm.deleteRuler = deleteRuler;
        vm.deleteTumorRuler = deleteTumorRuler;
        vm.formValid = formValid;
        vm.abortEdit = abortEdit;
        vm.updateROI = updateROI;

        activate();

        function activate() {
            $scope.$on('rois_viewerctrl.components.registered',
                function() {
                    vm.initializeRuler();
                    vm.initializeTumorRuler();
                }
            );

            $scope.$on('core.edit',
                function(event, core_id) {
                    vm.coreLengthScaleFactor = vm.lengthUOM[0];
                    vm.tumorLengthScaleFactor = vm.lengthUOM[0];
                    vm.coreAreaScaleFactor = vm.areaUOM[0];

                    vm.core_id = core_id;
                    CoresManagerService.get(core_id)
                        .then(getCoreSuccessFn, getCoreErrorFn);
                }
            );

            function getCoreSuccessFn(response) {
                vm.label = response.data.label;
                vm.shape_id = $.parseJSON(response.data.roi_json).shape_id;
                vm.coreArea = response.data.area;
                vm.updateCoreArea();
                vm.coreLength = response.data.length;
                vm.updateCoreLength();
                vm.tumorLength = response.data.tumor_length;
                if (!(typeof vm.tumorLength === 'undefined') && !(vm.tumorLength === null)) {
                    vm.updateTumorLength();
                }
            }

            function getCoreErrorFn(response) {
                $log.error('Unable to load core data');
                $log.error(response);
            }
        }

        function isReadOnly() {
            return false;
        }

        function isEditMode() {
            return true;
        }

        function shapeExists() {
            return (typeof vm.shape_id !== 'undefined');
        }

        function focusOnShape() {
            AnnotationsViewerService.focusOnShape(vm.shape_id);
        }

        function updateCoreLength() {
            vm.scaledCoreLength = formatDecimalNumber(
                (vm.coreLength * vm.coreLengthScaleFactor.id), 3
            );
        }

        function updateTumorLength() {
            vm.scaledTumorLength = formatDecimalNumber(
                (vm.tumorLength * vm.tumorLengthScaleFactor.id), 3
            );
        }

        function updateCoreArea() {
            vm.scaledCoreArea = formatDecimalNumber(
                (vm.coreArea * vm.coreAreaScaleFactor.id), 3
            );
        }

        function getRulerOnId() {
            return vm.ruler_on_id;
        }

        function getRulerOffId() {
            return vm.ruler_off_id;
        }

        function getRulerOutputId() {
            return vm.ruler_output_id;
        }

        function getTumorRulerOnId() {
            return vm.tumor_ruler_on_id;
        }

        function getTumorRulerOffId() {
            return vm.tumor_ruler_off_id;
        }

        function getTumorRulerOutputId() {
            return vm.tumor_ruler_output_id;
        }

        function initializeRuler() {
            AnnotationsViewerService.createRulerBindings(vm.getRulerOnId(), vm.getRulerOffId(),
                vm.getRulerOutputId());
        }

        function initializeTumorRuler() {
            AnnotationsViewerService.createRulerBindings(vm.getTumorRulerOnId(), vm.getTumorRulerOffId(),
                vm.getTumorRulerOutputId());
        }

        function startRuler() {
            var $ruler_out = $('#' + vm.getRulerOutputId());
            AnnotationsViewerService.extendRulerConfig(vm.shape_config);
            $ruler_out.on('ruler_created',
                function() {
                    if (vm.isRulerToolActive()) {
                        vm.tmp_ruler_exists = true;
                        $ruler_out.unbind('ruler_created');
                        $scope.$apply();
                    }
                }
            );
            $ruler_out.on('ruler_updated',
                function() {
                    vm.coreLength = $ruler_out.data('measure');
                    vm.updateCoreLength();
                    $scope.$apply();
                }
            );
            $ruler_out.on('ruler_cleared',
                function(event, ruler_saved) {
                    if (ruler_saved) {
                        $ruler_out.unbind('ruler_cleared');
                        $ruler_out.unbind('ruler_updated');
                    }
                }
            );
            vm.active_tool = vm.RULER_TOOL;
        }

        function pauseRulerTool() {
            AnnotationsViewerService.disableActiveTool();
            vm.ruler_tool_paused = true;
        }

        function resumeRulerTool() {
            AnnotationsViewerService.startRuler();
            vm.ruler_tool_paused = false;
        }

        function isRulerToolPaused() {
            return vm.ruler_tool_paused;
        }

        function startTumorRuler() {
            var $tumor_ruler_out = $('#' + vm.getTumorRulerOutputId());
            AnnotationsViewerService.extendRulerConfig(vm.shape_config);
            $tumor_ruler_out.on('ruler_created',
                function() {
                    if (vm.isTumorRulerToolActive()) {
                        vm.tmp_ruler_exists = true;
                        $tumor_ruler_out.unbind('ruler_created');
                        $scope.$apply();
                    }
                }
            );
            $tumor_ruler_out.on('ruler_updated',
                function() {
                    vm.tumorLength = $tumor_ruler_out.data('measure');
                    vm.updateTumorLength();
                    $scope.$apply();
                }
            );
            $tumor_ruler_out.on('ruler_cleared',
                function(event, ruler_saved){
                    if (ruler_saved) {
                        $tumor_ruler_out.unbind('ruler_cleared');
                        $tumor_ruler_out.unbind('ruler_updated');
                    }
                }
            );
            vm.active_tool = vm.TUMOR_RULER_TOOL;
        }

        function pauseTumorRulerTool() {
            AnnotationsViewerService.disableActiveTool();
            vm.tumor_ruler_tool_paused = true;
        }

        function resumeTumorRulerTool() {
            AnnotationsViewerService.startRuler();
            vm.tumor_ruler_tool_paused = false;
        }

        function isTumorRulerToolPaused() {
            return vm.tumor_ruler_tool_paused;
        }

        function isRulerToolActive() {
            return vm.active_tool === vm.RULER_TOOL;
        }

        function isTumorRulerToolActive() {
            return vm.active_tool === vm.TUMOR_RULER_TOOL;
        }

        function coreLengthExists() {
            return (vm.coreLength !== undefined && vm.coreLength !== null);
        }

        function tumorLengthExists() {
            return (vm.tumorLength !== undefined && vm.tumorLength !== null);
        }

        function temporaryRulerExists() {
            if (vm.active_tool === vm.RULER_TOOL) {
                return vm.tmp_ruler_exists && vm.coreLength > 0;
            } else if (vm.active_tool === vm.TUMOR_RULER_TOOL) {
                return vm.tmp_ruler_exists && vm.tumorLength > 0;
            } else {
                return false;
            }
        }

        function stopRuler() {
            AnnotationsViewerService.disableActiveTool();
            vm.active_tool = undefined;
            vm.tmp_ruler_exists = false;
            vm.ruler_tool_paused = false;
        }

        function stopTumorRuler() {
            AnnotationsViewerService.disableActiveTool();
            vm.active_tool = undefined;
            vm.tmp_ruler_exists = false;
            vm.tumor_ruler_tool_paused = false;
        }

        function abortTool() {
            if (vm.isRulerToolActive()) {
                vm.deleteRuler();
            }
            if (vm.isTumorRulerToolActive()) {
                vm.deleteTumorRuler();
            }
            AnnotationsViewerService.disableActiveTool();
            vm.active_tool = undefined;
            vm.tmp_ruler_exists = false;
            vm.ruler_tool_paused = false;
            vm.tumor_ruler_tool_paused = false;
        }

        function _unbindRulers() {
            $("#" + vm.getRulerOutputId())
                .unbind('ruler_cleared')
                .unbind('ruler_updated');
            $("#" + vm.getTumorRulerOutputId())
                .unbind('ruler_cleared')
                .unbind('ruler_updated');
        }

        function deleteRuler() {
            var $ruler_out = $('#' + vm.getRulerOutputId());
            $ruler_out.unbind('ruler_updated');
            $ruler_out.unbind('ruler_cleared');
            AnnotationsViewerService.clearRuler();
            if (typeof vm.coreLength !== 'undefined') {
                $ruler_out.removeData('ruler_json')
                    .removeData('measure');
                vm.coreLength = undefined;
                vm.scaledCoreLength = undefined;
            }
            vm.tmp_ruler_exists = false;
        }

        function deleteTumorRuler() {
            var $tumor_ruler_out = $("#tumor_ruler_output");
            $tumor_ruler_out.unbind('ruler_updated');
            $tumor_ruler_out.unbind('ruler_cleared');
            AnnotationsViewerService.clearRuler();
            if (typeof vm.tumorLength !== 'undefined') {
                $tumor_ruler_out.removeData('ruler_json')
                    .removeData('measure');
                vm.tumorLength = undefined;
                vm.scaledTumorLength = undefined;
            }
            vm.tmp_ruler_exists = false;
        }

        function formValid() {
            // if tumor ruler tool is active, "Save" button should be disabled
            if (vm.isTumorRulerToolActive() || vm.isRulerToolActive()) {
                return false;
            }
            return typeof vm.coreLength !== 'undefined';
        }

        function abortEdit() {
            vm.abortTool();
            vm._unbindRulers();
            $rootScope.$broadcast('core.show', vm.core_id);
            vm.core_id = undefined;
            vm.label = undefined;
            vm.shape_id = undefined;
            vm.coreArea = undefined;
            vm.coreLength = undefined;
            vm.scaledCoreLength = undefined;
            vm.tumorLength = undefined;
            vm.scaledTumorLength = undefined;
        }

        function updateROI() {
            var tumor_length = typeof vm.tumorLength !== 'undefined' ? vm.tumorLength : null;
            CoresManagerService.update(vm.core_id, vm.coreLength, tumor_length)
                .then(updateCoreSuccessFn, updateCoreErrorFn);

            function updateCoreSuccessFn(response) {
                vm.abortEdit();
            }

            function updateCoreErrorFn(response) {
                $log.error('unable to update core data');
                $log.error(response);
            }
        }
    }


    ShowCoreController.$inject = ['$scope', '$rootScope', '$log', 'ngDialog', 'CoresManagerService',
        'AnnotationsViewerService'];

    function ShowCoreController($scope, $rootScope, $log, ngDialog, CoresManagerService, AnnotationsViewerService) {
        var vm = this;
        vm.core_id = undefined;
        vm.label = undefined;
        vm.shape_id = undefined;
        vm.coreArea = undefined;
        vm.coreLength = undefined;
        vm.tumorLength = undefined;

        vm.scaledCoreLength = undefined;
        vm.coreLengthScaleFactor = undefined;
        vm.scaledTumorLength = undefined;
        vm.tumorLengthScaleFactor = undefined;
        vm.scaledCoreArea = undefined;
        vm.coreAreaScaleFactor = undefined;

        vm.lengthUOM = [
            { id: 1, unit_of_measure: 'μm' },
            { id: Math.pow(10, -3), unit_of_measure: 'mm' }
        ];

        vm.areaUOM = [
            { id: 1, unit_of_measure: 'μm²'},
            { id: Math.pow(10, -6), unit_of_measure: 'mm²'}
        ];

        vm.isReadOnly = isReadOnly;
        vm.isEditMode = isEditMode;
        vm.shapeExists = shapeExists;
        vm.focusOnShape = focusOnShape;
        vm.editROI = editROI;
        vm.deleteShape = deleteShape;
        vm.updateTumorLength = updateTumorLength;
        vm.updateCoreLength = updateCoreLength;
        vm.updateCoreArea = updateCoreArea;

        activate();

        function activate() {
            vm.coreLengthScaleFactor = vm.lengthUOM[0];
            vm.tumorLengthScaleFactor = vm.lengthUOM[0];
            vm.coreAreaScaleFactor = vm.areaUOM[0];

            $scope.$on('core.load',
                function(event, core_id) {
                    $log.debug('Show core ' + core_id);
                    vm.core_id = core_id;
                    CoresManagerService.get(core_id)
                        .then(getCoreSuccessFn, getCoreErrorFn);
                }
            );

            function getCoreSuccessFn(response) {
                vm.label = response.data.label;
                vm.shape_id = $.parseJSON(response.data.roi_json).shape_id;
                vm.coreArea = response.data.area;
                vm.updateCoreArea();
                vm.coreLength = response.data.length;
                vm.updateCoreLength();
                vm.tumorLength = response.data.tumor_length;
                vm.updateTumorLength();
            }

            function getCoreErrorFn(response) {
                $log.error('Unable to load core data');
                $log.error(response);
            }
        }

        function isReadOnly() {
            return true;
        }

        function isEditMode() {
            return false;
        }

        function shapeExists() {
            return (typeof vm.shape_id !== 'undefined');
        }

        function focusOnShape() {
            AnnotationsViewerService.focusOnShape(vm.shape_id);
        }

        function editROI() {
            $rootScope.$broadcast('edit.activate', {'roi_type': 'core', 'roi_id': vm.core_id});
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
                vm.scaledCoreArea = undefined;
                vm.coreLength = undefined;
                vm.scaledCoreLength = undefined;
                vm.tumorLength = undefined;
                vm.scaledTumorLength = undefined;
                dialog.close();
            }

            function deleteCoreErrorFn(response) {
                $log.error('Unable to delete core');
                $log.error(response);
                dialog.close();
            }
        }

        function updateCoreLength() {
            vm.scaledCoreLength = formatDecimalNumber(
                (vm.coreLength * vm.coreLengthScaleFactor.id), 3
            );
        }

        function updateTumorLength() {
            vm.scaledTumorLength = formatDecimalNumber(
                (vm.tumorLength * vm.tumorLengthScaleFactor.id), 3
            );
        }

        function updateCoreArea() {
            vm.scaledCoreArea = formatDecimalNumber(
                (vm.coreArea * vm.coreAreaScaleFactor.id), 3
            );
        }
    }

    NewFocusRegionController.$inject = ['$scope', '$rootScope', '$routeParams', '$log', 'ngDialog',
        'AnnotationsViewerService', 'CoresManagerService', 'CurrentSlideDetailsService'];

    function NewFocusRegionController($scope, $rootScope, $routeParams, $log, ngDialog, AnnotationsViewerService,
                                      CoresManagerService, CurrentSlideDetailsService) {
        var vm = this;
        vm.slide_id = undefined;
        vm.case_id = undefined;
        vm.parentCore = undefined;
        vm.shape_label = undefined;
        vm.default_shape_label = undefined;
        vm.shape = undefined;
        vm.regionLength = undefined;
        vm.regionArea = undefined;
        vm.coreCoverage = undefined;
        vm.tissueStatus = undefined;

        vm.actionStartTime = undefined;

        vm.scaledRegionLength = undefined;
        vm.regionLengthScaleFactor = undefined;
        vm.scaledRegionArea = undefined;
        vm.regionAreaScaleFactor = undefined;

        vm.lengthUOM = [
            { id: 1, unit_of_measure: 'μm' },
            { id: Math.pow(10, -3), unit_of_measure: 'mm' }
        ];

        vm.areaUOM = [
            { id: 1, unit_of_measure: 'μm²'},
            { id: Math.pow(10, -6), unit_of_measure: 'mm²'}
        ];

        vm.ruler_on_id = 'new_focus_region_ruler_on';
        vm.ruler_off_id = 'new_focus_region_ruler_off';
        vm.ruler_output_id = 'new_focus_region_ruler_output';

        vm.active_tool = undefined;
        vm.polygon_tool_paused = false;
        vm.freehand_tool_paused = false;
        vm.ruler_tool_paused = false;

        vm.tmp_ruler_exists = false;

        vm.POLYGON_TOOL = 'polygon_drawing_tool';
        vm.FREEHAND_TOOL = 'freehand_drawing_tool';
        vm.RULER_TOOL = 'ruler_tool';

        vm.shape_config = {
            'stroke_color': '#00ff00',
            'stroke_width': 20
        };

        vm._updateShapeConfig = _updateShapeConfig;
        vm.switchShapeColor = switchShapeColor;
        vm.newPolygon = newPolygon;
        vm.newFreehand = newFreehand;
        vm.activateEditLabelMode = activateEditLabelMode;
        vm.labelValid = labelValid;
        vm.setNewLabel = setNewLabel;
        vm.deactivateEditLabelMode = deactivateEditLabelMode;
        vm.abortEditLabelMode = abortEditLabelMode;
        vm.resetLabel = resetLabel;
        vm.isEditLabelModeActive = isEditLabelModeActive;
        vm._updateFocusRegionData = _updateFocusRegionData;
        vm.getRulerOnId = getRulerOnId;
        vm.getRulerOffId = getRulerOffId;
        vm.getRulerOutputId = getRulerOutputId;
        vm.initializeRuler = initializeRuler;
        vm.startRuler = startRuler;
        vm.pauseRulerTool = pauseRulerTool;
        vm.resumeRulerTool = resumeRulerTool;
        vm.isRulerToolPaused = isRulerToolPaused;
        vm.save = save;
        vm.isReadOnly = isReadOnly;
        vm.isPolygonToolActive = isPolygonToolActive;
        vm.isPolygonToolPaused = isPolygonToolPaused;
        vm.isFreehandToolActive = isFreehandToolActive;
        vm.isFreehandToolPaused = isFreehandToolPaused;
        vm.isRulerToolActive = isRulerToolActive;
        vm.temporaryPolygonExists = temporaryPolygonExists;
        vm.temporaryPolygonValid = temporaryPolygonValid;
        vm.temporaryShapeExists = temporaryShapeExists;
        vm.temporaryShapeValid = temporaryShapeValid;
        vm.drawInProgress = drawInProgress;
        vm.shapeExists = shapeExists;
        vm.temporaryRulerExists = temporaryRulerExists;
        vm.regionLengthExists = regionLengthExists;
        vm.pausePolygonTool = pausePolygonTool;
        vm.unpausePolygonTool = unpausePolygonTool;
        vm.pauseFreehandTool = pauseFreehandTool;
        vm.unpauseFreehandTool = unpauseFreehandTool;
        vm.confirmPolygon = confirmPolygon;
        vm.confirmFreehandShape = confirmFreehandShape;
        vm.polygonRollbackPossible = polygonRollbackPossible;
        vm.polygonRestorePossible = polygonRestorePossible;
        vm.shapeRollbackPossible = shapeRollbackPossible;
        vm.shapeRestorePossible = shapeRestorePossible;
        vm.rollbackPolygon = rollbackPolygon;
        vm.restorePolygon = restorePolygon;
        vm.rollbackFreehandShape = rollbackFreehandShape;
        vm.restoreFreehandShape = restoreFreehandShape;
        vm.stopRuler = stopRuler;
        vm.abortTool = abortTool;
        vm.clear = clear;
        vm.focusOnShape = focusOnShape;
        vm.deleteShape = deleteShape;
        vm.deleteRuler = deleteRuler;
        vm.formValid = formValid;
        vm.destroy = destroy;
        vm.updateRegionLength = updateRegionLength;
        vm.updateRegionArea = updateRegionArea;

        activate();

        function activate() {
            vm.slide_id = CurrentSlideDetailsService.getSlideId();
            vm.case_id = CurrentSlideDetailsService.getCaseId();

            // by default, mark region as NORMAL
            vm.tissueStatus = 'NORMAL';

            vm.regionLengthScaleFactor = vm.lengthUOM[0];
            vm.regionAreaScaleFactor = vm.areaUOM[0];

            $scope.$on('rois_viewerctrl.components.registered',
                function() {
                    vm.initializeRuler();
                }
            );

            $scope.$on('focus_region.creation_mode',
                function() {
                    vm.default_shape_label = AnnotationsViewerService.getFirstAvailableLabel('focus_region');
                    vm.shape_label = vm.default_shape_label;
                    vm.actionStartTime = new Date();
                }
            );
        }

        function _updateShapeConfig() {
            switch(vm.tissueStatus) {
                case 'NORMAL':
                    vm.shape_config.stroke_color = '#32fc46';
                    break;
                case 'STRESSED':
                    vm.shape_config.stroke_color = '#fd6402';
                    break;
                case 'TUMOR':
                    vm.shape_config.stroke_color = '#ff0000';
                    break;
            }
        }

        function switchShapeColor() {
            if (typeof vm.shape !== 'undefined') {
                vm._updateShapeConfig();
                AnnotationsViewerService.setShapeStrokeColor(vm.shape.shape_id, vm.shape_config.stroke_color);
                vm.shape = AnnotationsViewerService.getShapeJSON(vm.shape.shape_id);
            }
        }

        function newPolygon() {
            vm._updateShapeConfig();
            AnnotationsViewerService.extendPolygonConfig(vm.shape_config);
            AnnotationsViewerService.startPolygonsTool();
            vm.active_tool = vm.POLYGON_TOOL;
            var canvas_label = AnnotationsViewerService.getCanvasLabel();
            var $canvas = $("#" + canvas_label);
            $canvas
                .on('polygon_created',
                    function() {
                        $canvas.unbind('polygon_created');
                        $scope.$apply();
                    }
                )
                .on('polygon_add_point',
                    function() {
                        $scope.$apply();
                    }
                );
        }

        function newFreehand() {
            AnnotationsViewerService.setFreehandToolLabelPrefix('focus_region');
            vm._updateShapeConfig();
            AnnotationsViewerService.extendPathConfig(vm.shape_config);
            AnnotationsViewerService.startFreehandDrawingTool();
            var canvas_label = AnnotationsViewerService.getCanvasLabel();
            var $canvas = $("#" + canvas_label);
            $canvas.on('freehand_polygon_paused',
                function(event, polygon_label) {
                    AnnotationsViewerService.disableActiveTool();
                    vm.freehand_tool_paused = true;
                    $scope.$apply();
                }
            );
            vm.active_tool = vm.FREEHAND_TOOL;
        }

        function _updateFocusRegionData(polygon_label, parent_core) {
            vm.parentCore = parent_core;
            vm.regionArea = AnnotationsViewerService.getShapeArea(polygon_label);
            vm.updateRegionArea();
            vm.coreCoverage = AnnotationsViewerService.getAreaCoverage(vm.parentCore.label, polygon_label);
        }

        function getRulerOnId() {
            return vm.ruler_on_id;
        }

        function getRulerOffId() {
            return vm.ruler_off_id;
        }

        function getRulerOutputId() {
            return vm.ruler_output_id;
        }

        function initializeRuler() {
            AnnotationsViewerService.createRulerBindings(vm.getRulerOnId(), vm.getRulerOffId(), vm.getRulerOutputId());
        }

        function startRuler() {
            var $ruler_out = $('#' + vm.getRulerOutputId());
            vm._updateShapeConfig();
            AnnotationsViewerService.extendRulerConfig(vm.shape_config);
            $ruler_out.on('ruler_created',
                function() {
                    vm.tmp_ruler_exists = true;
                    $ruler_out.unbind('ruler_created');
                    $scope.$apply();
                }
            );
            $ruler_out.on('ruler_updated',
                function() {
                    vm.regionLength = $ruler_out.data('measure');
                    vm.updateRegionLength();
                    $scope.$apply();
                }
            );
            $ruler_out.on('ruler_cleared',
                function(event, ruler_saved) {
                    if (ruler_saved) {
                        $ruler_out.unbind('ruler_updated');
                        $ruler_out.unbind('ruler_cleared');
                    }
                }
            );
            vm.active_tool = vm.RULER_TOOL;
        }

        function pauseRulerTool() {
            AnnotationsViewerService.disableActiveTool();
            vm.ruler_tool_paused = true;
        }

        function resumeRulerTool() {
            AnnotationsViewerService.startRuler();
            vm.ruler_tool_paused = false;
        }

        function isRulerToolPaused() {
            return vm.ruler_tool_paused;
        }

        function activateEditLabelMode() {
            vm.edit_shape_label = true;
            vm.previuos_shape_label = vm.shape_label;
        }

        function labelValid() {
            return ((typeof vm.shape_label !== 'undefined') &&
                (vm.shape_label.length > 0 && vm.shape_label.length <= 40));
        }

        function setNewLabel() {
            if (typeof vm.shape !== 'undefined' && vm.shape_label === vm.shape.shape_id) {
                $log.debug('Shape label not changed');
                vm.deactivateEditLabelMode();
            } else {
                if (AnnotationsViewerService.shapeIdAvailable(vm.shape_label)) {
                    $log.debug('Label available, assigning to new shape');
                    vm.deactivateEditLabelMode();
                } else {
                    $log.debug('Label in use, restoring previous label');
                    vm.abortEditLabelMode();
                    ngDialog.open({
                        'template': '/static/templates/dialogs/invalid_label.html'
                    });
                }
            }
        }

        function deactivateEditLabelMode() {
            vm.previuos_shape_label = undefined;
            vm.edit_shape_label = false;
            // if a shape already exists, change its name
            if (typeof vm.shape !== 'undefined' && vm.shape.shape_id !== vm.shape_label) {
                $log.debug('updating shape id');
                AnnotationsViewerService.changeShapeId(vm.shape.shape_id, vm.shape_label);
                vm.shape = AnnotationsViewerService.getShapeJSON(vm.shape_label);
                $log.debug('new shape id is: ' + vm.shape.shape_id);
            }
        }

        function abortEditLabelMode() {
            vm.shape_label = vm.previuos_shape_label;
            vm.deactivateEditLabelMode();
        }

        function resetLabel() {
            vm.shape_label = vm.default_shape_label;
            vm.deactivateEditLabelMode();
        }

        function isEditLabelModeActive() {
            return vm.edit_shape_label;
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

        function isFreehandToolPaused() {
            return vm.freehand_tool_paused;
        }

        function temporaryPolygonExists() {
            return AnnotationsViewerService.temporaryPolygonExists();
        }

        function temporaryPolygonValid() {
            return AnnotationsViewerService.temporaryPolygonValid();
        }

        function temporaryShapeExists() {
            return AnnotationsViewerService.tmpFreehandPathExists();
        }

        function temporaryShapeValid() {
            return AnnotationsViewerService.tmpFreehandPathValid();
        }

        function shapeExists() {
            return vm.shape !== undefined;
        }

        function drawInProgress() {
            return vm.isPolygonToolActive() || vm.isPolygonToolPaused() || vm.isFreehandToolActive() ||
                vm.isFreehandToolPaused() || vm.isRulerToolActive();
        }

        function temporaryRulerExists() {
            return vm.tmp_ruler_exists && vm.regionLength > 0;
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

        function pauseFreehandTool() {
            AnnotationsViewerService.disableActiveTool();
            if (vm.temporaryShapeExists()) {
                AnnotationsViewerService.deactivatePreviewMode();
            }
            vm.freehand_tool_paused = true;
        }

        function unpauseFreehandTool() {
            AnnotationsViewerService.startFreehandDrawingTool();
            if (vm.temporaryShapeExists()) {
                AnnotationsViewerService.activatePreviewMode();
            }
            vm.freehand_tool_paused = false;
        }

        function confirmPolygon() {
            ngDialog.open({
                template: '/static/templates/dialogs/rois_check.html',
                showClose: false,
                closeByEscape: false,
                closeByNavigation: false,
                closeByDocument: false,
                name: 'checkFocusRegion',
                onOpenCallback: function() {
                    var canvas_label = AnnotationsViewerService.getCanvasLabel();
                    var $canvas = $("#" + canvas_label);
                    $canvas.on('polygon_saved',
                        function (event, polygon_label) {
                            var cores = $rootScope.cores;
                            for (var c in cores) {
                                if (AnnotationsViewerService.checkContainment(cores[c].label, polygon_label) ||
                                    AnnotationsViewerService.checkContainment(polygon_label, cores[c].label)) {
                                    AnnotationsViewerService.adaptToContainer(cores[c].label, polygon_label);
                                    if (vm.shape_label !== polygon_label) {
                                        AnnotationsViewerService.changeShapeId(polygon_label, vm.shape_label);
                                        vm.shape = AnnotationsViewerService.getShapeJSON(vm.shape_label);
                                    } else {
                                        vm.shape = AnnotationsViewerService.getShapeJSON(polygon_label);
                                    }
                                    vm._updateFocusRegionData(polygon_label, cores[c]);
                                    break;
                                }
                            }
                            ngDialog.close('checkFocusRegion');
                            if (typeof vm.shape === 'undefined') {
                                AnnotationsViewerService.deleteShape(polygon_label);
                                ngDialog.open({
                                    'template': '/static/templates/dialogs/invalid_focus_region.html'
                                });
                            }
                            vm.abortTool();
                            $scope.$apply();
                        }
                    );
                    setTimeout(function() {
                        AnnotationsViewerService.saveTemporaryPolygon('focus_region');
                    }, 10);
                }
            });
        }

        function confirmFreehandShape() {
            ngDialog.open({
                template: '/static/templates/dialogs/rois_check.html',
                showClose: false,
                closeByEscape: false,
                closeByNavigation: false,
                closeByDocument: false,
                name: 'checkFocusRegion',
                onOpenCallback: function() {
                    var canvas_label = AnnotationsViewerService.getCanvasLabel();
                    var $canvas = $('#' + canvas_label);
                    $canvas.on('freehand_polygon_saved',
                        function(event, polygon_label){
                            var cores = $rootScope.cores;
                            for (var c in cores) {
                                if (AnnotationsViewerService.checkContainment(cores[c].label, polygon_label) ||
                                    AnnotationsViewerService.checkContainment(polygon_label, cores[c].label)) {
                                    AnnotationsViewerService.adaptToContainer(cores[c].label, polygon_label);
                                    if (vm.shape_label !== polygon_label) {
                                        AnnotationsViewerService.changeShapeId(polygon_label, vm.shape_label);
                                        vm.shape = AnnotationsViewerService.getShapeJSON(vm.shape_label);
                                    } else {
                                        vm.shape = AnnotationsViewerService.getShapeJSON(polygon_label);
                                    }
                                    vm._updateFocusRegionData(polygon_label, cores[c]);
                                    break;
                                }
                            }
                            ngDialog.close('checkFocusRegion');
                            if (typeof vm.shape === 'undefined') {
                                AnnotationsViewerService.deleteShape(polygon_label);
                                ngDialog.open({
                                    template: '/static/templates/dialogs/invalid_focus_region.html'
                                });
                            }
                            vm.abortTool();
                            $scope.$apply();
                        }
                    );
                    setTimeout(function() {
                        AnnotationsViewerService.saveTemporaryFreehandShape();
                    }, 10);
                }
            });
        }

        function polygonRollbackPossible() {
            return AnnotationsViewerService.temporaryPolygonExists();
        }

        function polygonRestorePossible() {
            return AnnotationsViewerService.polygonRestoreHistoryExists();
        }

        function shapeRollbackPossible() {
            return (AnnotationsViewerService.tmpFreehandPathExists() ||
                AnnotationsViewerService.shapeUndoHistoryExists());
        }

        function shapeRestorePossible() {
            return AnnotationsViewerService.shapeRestoreHistoryExists();
        }

        function rollbackPolygon() {
            AnnotationsViewerService.rollbackPolygon();
        }

        function restorePolygon() {
            AnnotationsViewerService.restorePolygon();
        }

        function rollbackFreehandShape() {
            AnnotationsViewerService.rollbackTemporaryFreehandShape();
        }

        function restoreFreehandShape() {
            AnnotationsViewerService.restoreTemporaryFreehandShape();
        }

        function stopRuler() {
            AnnotationsViewerService.disableActiveTool();
            vm.active_tool = undefined;
            vm.tmp_ruler_exists = false;
            vm.ruler_tool_paused = false;
        }

        function clear(destroy_shape) {
            vm.deleteShape(destroy_shape);
            vm.deleteRuler();
            vm.isTumor = false;
            vm.shape_label = undefined;
            vm.default_shape_label = undefined;
            vm.actionStartTime = undefined;
        }

        function abortTool() {
            if (vm.active_tool === vm.POLYGON_TOOL) {
                AnnotationsViewerService.clearTemporaryPolygon();
                $("#" + AnnotationsViewerService.getCanvasLabel()).unbind('polygon_saved');
            }
            if (vm.active_tool === vm.FREEHAND_TOOL) {
                AnnotationsViewerService.clearTemporaryFreehandShape();
                $("#" + AnnotationsViewerService.getCanvasLabel())
                    .unbind('freehand_polygon_saved')
                    .unbind('freehand_polygon_paused');
            }
            if (vm.active_tool === vm.RULER_TOOL) {
                vm.deleteRuler();
            }
            AnnotationsViewerService.disableActiveTool();
            vm.active_tool = undefined;
            vm.polygon_tool_paused = false;
            vm.tmp_ruler_exists = false;
            vm.freehand_tool_paused = false;
            vm.ruler_tool_paused = false;
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
                vm.scaledRegionArea = undefined;
                vm.regionLength = undefined;
                vm.scaledRegionLength = undefined;
                vm.parentCore = undefined;
                vm.coreCoverage = undefined;
                vm.tissueStatus = 'NORMAL';
            }
        }

        function deleteRuler() {
            var $ruler_out = $('#focus_region_ruler_output');
            $ruler_out.unbind('ruler_updated');
            $ruler_out.unbind('ruler_cleared');
            AnnotationsViewerService.clearRuler();
            if (typeof vm.regionLength !== 'undefined') {
                $ruler_out.removeData('ruler_json')
                    .removeData('measure');
                vm.regionLength = undefined;
                vm.scaledRegionLength = undefined;
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
                vm.regionLength, vm.regionArea, vm.tissueStatus, vm.actionStartTime, new Date())
                .then(createFocusRegionSuccessFn, createFocusRegionErrorFn);

            function createFocusRegionSuccessFn(response) {
                var focus_region_info = {
                    'id': response.data.id,
                    'label': response.data.label,
                    'core': response.data.core,
                    'annotated': false
                };
                vm.clear(false);
                $rootScope.$broadcast('focus_region.new', focus_region_info);
                dialog.close();
            }

            function createFocusRegionErrorFn(response) {
                $log.error('Unable to save focus region!!!');
                $log.error(response.data);
                dialog.close();
            }
        }

        function formValid() {
            if (vm.isRulerToolActive()) {
                return false;
            }
            return ((typeof vm.shape !== 'undefined') && (typeof vm.regionLength !== 'undefined')) &&
                !vm.isEditLabelModeActive();
        }

        function updateRegionArea() {
            vm.scaledRegionArea = formatDecimalNumber(
                (vm.regionArea * vm.regionAreaScaleFactor.id), 3
            );
        }

        function updateRegionLength() {
            vm.scaledRegionLength = formatDecimalNumber(
                (vm.regionLength * vm.regionLengthScaleFactor.id), 3
            );
        }
    }

    EditFocusRegionController.$inject = ['$scope', '$rootScope', '$routeParams', '$log', 'ngDialog',
        'AnnotationsViewerService', 'FocusRegionsManagerService'];

    function EditFocusRegionController($scope, $rootScope, $routeParams, $log, ngDialog, AnnotationsViewerService,
                                      FocusRegionsManagerService) {
        var vm = this;
        vm.focus_region_id = undefined;
        vm.label = undefined;
        vm.shape_id = undefined;
        vm.shape = undefined;
        vm.parent_shape_id = undefined;
        vm.regionLength = undefined;
        vm.regionArea = undefined;
        vm.coreCoverage = undefined;
        vm.tissueStatus = undefined;

        vm.scaledRegionLength = undefined;
        vm.regionLengthScaleFactor = undefined;
        vm.scaledRegionArea = undefined;
        vm.regionAreaScaleFactor = undefined;

        vm.lengthUOM = [
            { id: 1, unit_of_measure: 'μm' },
            { id: Math.pow(10, -3), unit_of_measure: 'mm' }
        ];

        vm.areaUOM = [
            { id: 1, unit_of_measure: 'μm²'},
            { id: Math.pow(10, -6), unit_of_measure: 'mm²'}
        ];

        vm.ruler_on_id = 'edit_focus_region_ruler_on';
        vm.ruler_off_id = 'edit_focus_region_ruler_off';
        vm.ruler_output_id = 'edit_focus_region_output';

        vm.active_tool = undefined;
        vm.polygon_tool_paused = false;
        vm.freehand_tool_paused = false;
        vm.ruler_tool_paused = false;

        vm.tmp_ruler_exists = false;

        vm.RULER_TOOL = 'ruler_tool';

        vm.shape_config = {
            'stroke_color': '#00ff00',
            'stroke_width': 20
        };

        vm._updateShapeConfig = _updateShapeConfig;
        vm.switchShapeColor = switchShapeColor;
        vm._updateFocusRegionData = _updateFocusRegionData;
        vm.getRulerOnId = getRulerOnId;
        vm.getRulerOffId = getRulerOffId;
        vm.getRulerOutputId = getRulerOutputId;
        vm.initializeRuler = initializeRuler;
        vm.startRuler = startRuler;
        vm.pauseRulerTool = pauseRulerTool;
        vm.resumeRulerTool = resumeRulerTool;
        vm.isReadOnly = isReadOnly;
        vm.isEditMode = isEditMode;
        vm.isRulerToolActive = isRulerToolActive;
        vm.isRulerToolPaused = isRulerToolPaused;
        vm.shapeExists = shapeExists;
        vm.temporaryRulerExists = temporaryRulerExists;
        vm.regionLengthExists = regionLengthExists;
        vm.stopRuler = stopRuler;
        vm.abortTool = abortTool;
        vm.clear = clear;
        vm.focusOnShape = focusOnShape;
        vm.deleteRuler = deleteRuler;
        vm._unbindRuler = _unbindRuler;
        vm.formValid = formValid;
        vm.updateRegionLength = updateRegionLength;
        vm.updateRegionArea = updateRegionArea;
        vm.abortEdit = abortEdit;
        vm.updateROI = updateROI;

        activate();

        function activate() {
            $scope.$on('rois_viewerctrl.components.registered',
                function() {
                    vm.initializeRuler();
                }
            );

            $scope.$on('focus_region.edit',
                function (event, focus_region_id, parent_shape_id) {
                    vm.regionAreaScaleFactor = vm.areaUOM[0];
                    vm.regionLengthScaleFactor = vm.lengthUOM[0];

                    vm.focus_region_id = focus_region_id;
                    vm.parent_shape_id = parent_shape_id;
                    FocusRegionsManagerService.get(focus_region_id)
                        .then(getFocusRegionSuccessFn, getFocusRegionErrorFn);
                }
            );

            function getFocusRegionSuccessFn(response) {
                vm.label = response.data.label;
                vm.shape_id = $.parseJSON(response.data.roi_json).shape_id;
                vm.shape = AnnotationsViewerService.getShapeJSON(vm.shape_id);
                vm.regionArea = response.data.area;
                vm.updateRegionArea();
                vm.regionLength = response.data.length;
                vm.updateRegionLength();
                vm.tissueStatus = response.data.tissue_status;
                vm.coreCoverage = AnnotationsViewerService.getAreaCoverage(vm.parent_shape_id, vm.shape_id);
                vm._updateShapeConfig();
            }

            function getFocusRegionErrorFn(response) {
                $log.error('Unable to load focus region data');
                $log.error(response);
            }
        }

        function _updateShapeConfig() {
            switch(vm.tissueStatus) {
                case 'NORMAL':
                    vm.shape_config.stroke_color = '#32fc46';
                    break;
                case 'STRESSED':
                    vm.shape_config.stroke_color = '#fd6402';
                    break;
                case 'TUMOR':
                    vm.shape_config.stroke_color = '#ff0000';
                    break;
            }
        }

        function switchShapeColor() {
            if (typeof vm.shape_id !== 'undefined') {
                vm._updateShapeConfig();
                AnnotationsViewerService.setShapeStrokeColor(vm.shape_id, vm.shape_config.stroke_color);
                vm.shape = AnnotationsViewerService.getShapeJSON(vm.shape_id);
            }
        }

        function _updateFocusRegionData(polygon_label, parent_core) {
            vm.parentCore = parent_core;
            vm.regionArea = AnnotationsViewerService.getShapeArea(polygon_label);
            vm.updateRegionArea();
            vm.coreCoverage = AnnotationsViewerService.getAreaCoverage(vm.parentCore.label, polygon_label);
        }

        function getRulerOnId() {
            return vm.ruler_on_id;
        }

        function getRulerOffId() {
            return vm.ruler_off_id;
        }

        function getRulerOutputId() {
            return vm.ruler_output_id;
        }

        function initializeRuler() {
            AnnotationsViewerService.createRulerBindings(vm.getRulerOnId(), vm.getRulerOffId(), vm.getRulerOutputId());
        }

        function startRuler() {
            var $ruler_out = $('#' + vm.getRulerOutputId());
            vm._updateShapeConfig();
            AnnotationsViewerService.extendRulerConfig(vm.shape_config);
            $ruler_out.on('ruler_created',
                function() {
                    vm.tmp_ruler_exists = true;
                    $ruler_out.unbind('ruler_created');
                    $scope.$apply();
                }
            );
            $ruler_out.on('ruler_updated',
                function() {
                    vm.regionLength = $ruler_out.data('measure');
                    vm.updateRegionLength();
                    $scope.$apply();
                }
            );
            $ruler_out.on('ruler_cleared',
                function(event, ruler_saved) {
                    if (ruler_saved) {
                        $ruler_out.unbind('ruler_updated');
                        $ruler_out.unbind('ruler_cleared');
                    }
                }
            );
            vm.active_tool = vm.RULER_TOOL;
        }

        function pauseRulerTool() {
            AnnotationsViewerService.disableActiveTool();
            vm.ruler_tool_paused = true;
        }

        function resumeRulerTool() {
            AnnotationsViewerService.startRuler();
            vm.ruler_tool_paused = false;
        }

        function isRulerToolPaused() {
            return vm.ruler_tool_paused;
        }

        function isReadOnly() {
            return false;
        }

        function isEditMode() {
            return true;
        }

        function isRulerToolActive() {
            return vm.active_tool === vm.RULER_TOOL;
        }

        function shapeExists() {
            return vm.shape_id !== undefined;
        }

        function temporaryRulerExists() {
            return vm.tmp_ruler_exists && vm.regionLength > 0;
        }

        function regionLengthExists() {
            return vm.regionLength !== undefined;
        }

        function stopRuler() {
            AnnotationsViewerService.disableActiveTool();
            vm.active_tool = undefined;
            vm.tmp_ruler_exists = false;
            vm.ruler_tool_paused = false;
        }

        function clear(destroy_shape) {
            vm.deleteShape(destroy_shape);
            vm.deleteRuler();
            vm.isTumor = false;
            vm.shape_label = undefined;
            vm.default_shape_label = undefined;
        }

        function abortTool() {
            if (vm.isRulerToolActive()) {
                vm.deleteRuler();
            }
            AnnotationsViewerService.disableActiveTool();
            vm.active_tool = undefined;
            vm.polygon_tool_paused = false;
            vm.tmp_ruler_exists = false;
            vm.freehand_tool_paused = false;
            vm.ruler_tool_paused = false;
        }

        function deleteRuler() {
            var $ruler_out = $('#' + vm.getRulerOutputId());
            $ruler_out.unbind('ruler_updated');
            $ruler_out.unbind('ruler_cleared');
            AnnotationsViewerService.clearRuler();
            if (typeof vm.regionLength !== 'undefined') {
                $ruler_out.removeData('ruler_json')
                    .removeData('measure');
                vm.regionLength = undefined;
                vm.scaledRegionLength = undefined;
            }
        }

        function _unbindRuler() {
            $("#" + vm.getRulerOutputId())
                .unbind('ruler_updated')
                .unbind('ruler_cleared');
        }

        function focusOnShape() {
            AnnotationsViewerService.focusOnShape(vm.shape_id);
        }

        function formValid() {
            if (vm.isRulerToolActive()) {
                return false;
            }
            return typeof vm.regionLength !== 'undefined';
        }

        function updateRegionArea() {
            vm.scaledRegionArea = formatDecimalNumber(
                (vm.regionArea * vm.regionAreaScaleFactor.id), 3
            );
        }

        function updateRegionLength() {
            vm.scaledRegionLength = formatDecimalNumber(
                (vm.regionLength * vm.regionLengthScaleFactor.id), 3
            );
        }

        function abortEdit() {
            vm.abortTool();
            vm._unbindRuler();
            $rootScope.$broadcast('focus_region.show', vm.focus_region_id, vm.parent_shape_id);
            vm.focus_region_id = undefined;
            vm.parent_shape_id = undefined;
            vm.label = undefined;
            vm.shape_id = undefined;
            vm.shape = undefined;
            vm.regionLength = undefined;
            vm.scaledRegionLength = undefined;
            vm.regionArea = undefined;
            vm.coreCoverage = undefined;
            vm.tissueStatus = undefined;
        }

        function updateROI() {
            FocusRegionsManagerService.update(vm.focus_region_id, vm.shape, vm.regionLength, vm.tissueStatus)
                .then(updateFocusRegionSuccessFn, updateFocusRegionErrorFn);

            function updateFocusRegionSuccessFn(response) {
                vm.abortEdit();
            }

            function updateFocusRegionErrorFn(response) {
                $log.error('unable to update focus region');
                $log.error(response);
            }
        }
    }

    ShowFocusRegionController.$inject = ['$scope', '$rootScope', '$log', 'ngDialog', 'FocusRegionsManagerService',
        'AnnotationsViewerService'];

    function ShowFocusRegionController($scope, $rootScope, $log, ngDialog, FocusRegionsManagerService,
                                       AnnotationsViewerService) {
        var vm = this;
        vm.focus_region_id = undefined;
        vm.parent_shape_id = undefined;
        vm.label = undefined;
        vm.shape_id = undefined;
        vm.regionArea = undefined;
        vm.regionLength = undefined;
        vm.coreCoverage = undefined;
        vm.tissueStatus = undefined;

        vm.scaledRegionLength = undefined;
        vm.regionLengthScaleFactor = undefined;
        vm.scaledRegionArea = undefined;
        vm.regionAreaScaleFactor = undefined;

        vm.lengthUOM = [
            { id: 1, unit_of_measure: 'μm' },
            { id: Math.pow(10, -3), unit_of_measure: 'mm' }
        ];

        vm.areaUOM = [
            { id: 1, unit_of_measure: 'μm²'},
            { id: Math.pow(10, -6), unit_of_measure: 'mm²'}
        ];

        vm.shape_config = {
            'stroke_color': '#00ff00',
            'stroke_width': 20
        };

        vm._updateShapeConfig = _updateShapeConfig;
        vm.switchShapeColor = switchShapeColor;
        vm.isReadOnly = isReadOnly;
        vm.shapeExists = shapeExists;
        vm.focusOnShape = focusOnShape;
        vm.deleteShape = deleteShape;
        vm.updateRegionArea = updateRegionArea;
        vm.updateRegionLength = updateRegionLength;
        vm.editROI = editROI;

        activate();

        function activate() {
            vm.regionAreaScaleFactor = vm.areaUOM[0];
            vm.regionLengthScaleFactor = vm.lengthUOM[0];

            $scope.$on('focus_region.load',
                function (event, focus_region_id, parent_shape_id) {
                    $log.debug('Show focus region ' + focus_region_id);
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
                vm.updateRegionArea();
                vm.regionLength = response.data.length;
                vm.updateRegionLength();
                vm.tissueStatus = response.data.tissue_status;
                vm.coreCoverage = AnnotationsViewerService.getAreaCoverage(vm.parent_shape_id, vm.shape_id);
                vm.switchShapeColor();
            }

            function getFocusRegionErrorFn(response) {
                $log.error('Unable to load focus region data');
                $log.error(response);
            }
        }

        function _updateShapeConfig() {
            switch(vm.tissueStatus) {
                case 'NORMAL':
                    vm.shape_config.stroke_color = '#32fc46';
                    break;
                case 'STRESSED':
                    vm.shape_config.stroke_color = '#fd6402';
                    break;
                case 'TUMOR':
                    vm.shape_config.stroke_color = '#ff0000';
                    break;
            }
        }

        function switchShapeColor() {
            if (typeof vm.shape_id !== 'undefined') {
                vm._updateShapeConfig();
                AnnotationsViewerService.setShapeStrokeColor(vm.shape_id, vm.shape_config.stroke_color);
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

        function editROI() {
            $rootScope.$broadcast('edit.activate', {'roi_type': 'focus_region', 'roi_id': vm.focus_region_id,
                                                    'parent_shape_id': vm.parent_shape_id});
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
                vm.scaledRegionArea = undefined;
                vm.regionLength = undefined;
                vm.scaledRegionLength = undefined;
                vm.coreCoverage = undefined;
                vm.tissueStatus = undefined;
                dialog.close();
            }

            function deleteFocusRegionErrorFn(response) {
                $log.error('Unable to delete focus region');
                $log.error(response);
                dialog.close();
            }
        }

        function updateRegionArea() {
            vm.scaledRegionArea = formatDecimalNumber(
                (vm.regionArea * vm.regionAreaScaleFactor.id), 3
            );
        }

        function updateRegionLength() {
            vm.scaledRegionLength = formatDecimalNumber(
                (vm.regionLength * vm.regionLengthScaleFactor.id), 3
            );
        }
    }
})();