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
        .module('promort.clinical_annotations_manager.controllers')
        .controller('ClinicalAnnotationsManagerController', ClinicalAnnotationsManagerController)
        .controller('RejectClinicalAnnotationStepController', RejectClinicalAnnotationStepController)
        .controller('NewSliceAnnotationController', NewSliceAnnotationController)
        .controller('ShowSliceAnnotationController', ShowSliceAnnotationController)
        .controller('NewCoreAnnotationController', NewCoreAnnotationController)
        .controller('ShowCoreAnnotationController', ShowCoreAnnotationController)
        .controller('NewFocusRegionAnnotationController', NewFocusRegionAnnotationController)
        .controller('ShowFocusRegionAnnotationController', ShowFocusRegionAnnotationController)
        .controller('NewGleasonPatternAnnotationController', NewGleasonPatternAnnotationController)
        .controller('ShowGleasonPatternAnnotationController', ShowGleasonPatternAnnotationController);

    ClinicalAnnotationsManagerController.$inject = ['$scope', '$rootScope', '$routeParams', '$compile', '$location',
        '$log', 'ngDialog', 'AnnotationsViewerService', 'ClinicalAnnotationStepService',
        'ClinicalAnnotationStepManagerService', 'CurrentSlideDetailsService'];

    function ClinicalAnnotationsManagerController($scope, $rootScope, $routeParams, $compile, $location, $log, ngDialog,
        AnnotationsViewerService, ClinicalAnnotationStepService,
        ClinicalAnnotationStepManagerService, CurrentSlideDetailsService) {
        var vm = this;
        vm.slide_id = undefined;
        vm.slide_index = undefined;
        vm.case_id = undefined;
        vm.clinical_annotation_label = undefined;
        vm.clinical_annotation_step_label = undefined;

        vm.slices_map = undefined;
        vm.cores_map = undefined;
        vm.focus_regions_map = undefined;

        vm.positive_fr_count = undefined;


        vm.ui_active_modes = {
            'annotate_slice': false,
            'annotate_core': false,
            'annotate_focus_region': false,
            'annotate_gleason_pattern': false,
            'show_slice': false,
            'show_core': false,
            'show_focus_region': false,
            'show_gleason_pattern': false
        };
        vm.roisTreeLocked = false;

        vm._registerSlice = _registerSlice;
        vm._registerCore = _registerCore;
        vm._registerFocusRegion = _registerFocusRegion;
        vm._registerGleasonPattern = _registerGleasonPattern;
        vm._getSliceLabel = _getSliceLabel;
        vm._getCoreLabel = _getCoreLabel;
        vm._getFocusRegionLabel = _getFocusRegionLabel;
        vm._getGleasonPatternLabel = _getGleasonPatternLabel;
        vm._createListItem = _createListItem;
        vm._createNewSubtree = _createNewSubtree;
        vm._focusOnShape = _focusOnShape;
        vm.showROIPanel = showROIPanel;
        vm.selectROI = selectROI;
        vm.deselectROI = deselectROI;
        vm._lockRoisTree = _lockRoisTree;
        vm._unlockRoisTree = _unlockRoisTree;
        vm.canCloseAnnotation = canCloseAnnotation;
        vm.closeAnnotation = closeAnnotation;
        vm.canClearAnnotations = canClearAnnotations;
        vm.clearAnnotations = clearAnnotations;
        vm.rejectAnnotation = rejectAnnotation;
        vm.allModesOff = allModesOff;
        vm.newClinicalAnnotationModeActive = newClinicalAnnotationModeActive;
        vm.activateNewSliceAnnotationMode = activateNewSliceAnnotationMode;
        vm.newSliceAnnotationModeActive = newSliceAnnotationModeActive;
        vm.activateShowSliceAnnotationMode = activateShowSliceAnnotationMode;
        vm.showSliceAnnotationModeActive = showSliceAnnotationModeActive;
        vm.activateNewCoreAnnotationMode = activateNewCoreAnnotationMode;
        vm.newCoreAnnotationModeActive = newCoreAnnotationModeActive;
        vm.activateShowCoreAnnotationMode = activateShowCoreAnnotationMode;
        vm.showCoreAnnotationModeActive = showCoreAnnotationModeActive;
        vm.activateNewFocusRegionAnnotationMode = activateNewFocusRegionAnnotationMode;
        vm.newFocusRegionAnnotationModeActive = newFocusRegionAnnotationModeActive;
        vm.activateShowFocusRegionAnnotationMode = activateShowFocusRegionAnnotationMode;
        vm.showFocusRegionAnnotationModeActive = showFocusRegionAnnotationModeActive;
        vm.getPositiveFocusRegionsCount = getPositiveFocusRegionsCount;
        vm.activateNewGleasonPatternAnnotationMode = activateNewGleasonPatternAnnotationMode;
        vm.newGleasonPatternAnnotationModeActive = newGleasonPatternAnnotationModeActive;
        vm.activateShowGleasonPatternAnnotationMode = activateShowGleasonPatternAnnotationMode;
        vm.showGleasonPatternAnnotationModeActive = showGleasonPatternAnnotationModeActive;
        vm.annotationModeActive = annotationModeActive;

        activate();

        function activate() {
            vm.slide_id = CurrentSlideDetailsService.getSlideId();
            vm.case_id = CurrentSlideDetailsService.getCaseId();
            vm.clinical_annotation_step_label = $routeParams.label;
            vm.clinical_annotation_label = vm.clinical_annotation_step_label.split('-')[0];
            vm.slide_index = vm.clinical_annotation_step_label.split('-')[1];

            vm.slices_map = {};
            vm.cores_map = {};
            vm.focus_regions_map = {};
            vm.gleason_patterns_map = {};

            vm.positive_fr_count = 0;

            vm.slices_edit_mode = [];
            vm.cores_edit_mode = [];
            vm.focus_regions_edit_mode = [];

            $rootScope.slices = [];
            $rootScope.cores = [];
            $rootScope.focus_regions = [];
            $rootScope.gleason_patterns = [];

            ClinicalAnnotationStepService.getDetails(vm.clinical_annotation_step_label)
                .then(getClinicalAnnotationStepSuccessFn, getClinicalAnnotationStepErrorFn);

            function getClinicalAnnotationStepSuccessFn(response) {
                if (response.data.completed === true || response.data.can_be_started === false) {
                    $location.url('worklist/clinical_annotations/' + vm.clinical_annotation_label);
                }

                $scope.$on('annotation_panel.closed',
                    function () {
                        vm.allModesOff();
                    }
                );

                $scope.$on('tool.destroyed',
                    function () {
                        vm.allModesOff();
                    }
                );

                $scope.$on('slice.new',
                    function (event, slice_info) {
                        vm._registerSlice(slice_info);
                        vm.allModesOff();
                        var $tree = $("#rois_tree");
                        var $new_slice_item = $(vm._createListItem(slice_info.label,
                            vm.slices_edit_mode[slice_info.id], true));
                        var $anchor = $new_slice_item.find('a');
                        $anchor.attr('ng-click', 'cmc.showROIPanel("slice", ' + slice_info.id + ')')
                            .attr('ng-mouseenter', 'cmc.selectROI("slice", ' + slice_info.id + ')')
                            .attr('ng-mouseleave', 'cmc.deselectROI("slice", ' + slice_info.id + ')');
                        $compile($anchor)($scope);
                        var new_slice_subtree = vm._createNewSubtree(slice_info.label);
                        $new_slice_item.append(new_slice_subtree);
                        $tree.append($new_slice_item);
                    }
                );

                $scope.$on('core.new',
                    function (event, core_info) {
                        vm._registerCore(core_info);
                        vm.allModesOff();
                        var $tree = $("#" + vm._getSliceLabel(core_info.slice) + "_tree");
                        var $new_core_item = $(vm._createListItem(core_info.label,
                            vm.cores_edit_mode[core_info.id], true));
                        var $anchor = $new_core_item.find('a');
                        $anchor.attr('ng-click', 'cmc.showROIPanel("core", ' + core_info.id + ')')
                            .attr('ng-mouseenter', 'cmc.selectROI("core", ' + core_info.id + ')')
                            .attr('ng-mouseleave', 'cmc.deselectROI("core", ' + core_info.id + ')');
                        $compile($anchor)($scope);
                        var new_core_subtree = vm._createNewSubtree(core_info.label);
                        $new_core_item.append(new_core_subtree);
                        $tree.append($new_core_item);
                    }
                );

                $scope.$on('focus_region.new',
                    function (event, focus_region_info) {
                        if (focus_region_info.tumor == true) {
                            vm.positive_fr_count += 1;
                        }
                        vm._registerFocusRegion(focus_region_info);
                        vm.allModesOff();
                        var $tree = $("#" + vm._getCoreLabel(focus_region_info.core) + "_tree");
                        var $new_focus_region_item = $(vm._createListItem(focus_region_info.label,
                            vm.focus_regions_edit_mode[focus_region_info.id], true));
                        var $anchor = $new_focus_region_item.find('a');
                        $anchor.attr('ng-click', 'cmc.showROIPanel("focus_region", ' + focus_region_info.id + ')')
                            .attr('ng-mouseenter', 'cmc.selectROI("focus_region", ' + focus_region_info.id + ')')
                            .attr('ng-mouseleave', 'cmc.deselectROI("focus_region", ' + focus_region_info.id + ')');
                        $compile($anchor)($scope);
                        var new_focus_region_subtree = vm._createNewSubtree(focus_region_info.label);
                        $new_focus_region_item.append(new_focus_region_subtree);
                        $tree.append($new_focus_region_item);
                    }
                );

                $scope.$on('gleason_pattern.new',
                    function (event, gleason_pattern_info) {
                        vm._registerGleasonPattern(gleason_pattern_info);
                        vm.allModesOff();
                        var $tree = $("#" + vm._getFocusRegionLabel(gleason_pattern_info.focus_region) + "_tree");
                        var $new_gleason_pattern_item = $(vm._createListItem(gleason_pattern_info.label,
                            false, false));
                        var $anchor = $new_gleason_pattern_item.find('a');
                        $anchor.attr('ng-click', '')
                            .attr('ng-mouseenter', 'cmc.selectROI("gleason_pattern", ' + gleason_pattern_info.id + ')')
                            .attr('ng-mouseleave', 'cmc.deselectROI("gleason_pattern", ' + gleason_pattern_info.id + ')');
                        $compile($anchor)($scope);
                        $tree.append($new_gleason_pattern_item);
                    }
                );

                $scope.$on('slice_annotation.saved',
                    function (event, slice_label, slice_id) {
                        var $icon = $("#" + slice_label).find('i');
                        $icon.removeClass("icon-black_question");
                        $icon.addClass("icon-check_circle");
                        vm.allModesOff();
                        vm.slices_edit_mode[slice_id] = false;
                    }
                );

                $scope.$on('slice_annotation.deleted',
                    function (event, slice_label, slice_id) {
                        if (slice_id in vm.slices_edit_mode) {
                            var $icon = $("#" + slice_label).find('i');
                            $icon.removeClass("icon-check_circle");
                            $icon.addClass("icon-black_question");
                            vm.allModesOff();
                            vm.slices_edit_mode[slice_id] = true;
                        }
                    }
                );

                $scope.$on('core_annotation.saved',
                    function (event, core_label, core_id) {
                        var $icon = $("#" + core_label).find('i');
                        $icon.removeClass("icon-black_question");
                        $icon.addClass("icon-check_circle");
                        vm.allModesOff();
                        vm.cores_edit_mode[core_id] = false;
                    }
                );

                $scope.$on('core_annotation.deleted',
                    function (event, core_label, core_id) {
                        if (core_id in vm.cores_edit_mode) {
                            var $icon = $("#" + core_label).find('i');
                            $icon.removeClass("icon-check_circle");
                            $icon.addClass("icon-black_question");
                            vm.allModesOff();
                            vm.cores_edit_mode[core_id] = true;
                        }
                    }
                );

                $scope.$on('focus_region_annotation.saved',
                    function (event, focus_region_label, focus_region_id) {
                        var $icon = $("#" + focus_region_label).find('i');
                        $icon.removeClass("icon-black_question");
                        $icon.addClass("icon-check_circle");
                        vm.allModesOff();
                        vm.focus_regions_edit_mode[focus_region_id] = false;
                    }
                );

                $scope.$on('focus_region_annotation.deleted',
                    function (event, focus_region_label, focus_region_id) {
                        if (focus_region_id in vm.focus_regions_edit_mode) {
                            var $icon = $("#" + focus_region_label).find('i');
                            $icon.removeClass('icon-check_circle');
                            $icon.addClass('icon-black_question');
                            vm.allModesOff();
                            vm.focus_regions_edit_mode[focus_region_id] = true;
                        }
                    }
                );
            }

            function getClinicalAnnotationStepErrorFn(response) {
                $log.error('Cannot load slide info');
                $log.error(response);
            }
        }

        function _registerSlice(slice_info) {
            $rootScope.slices.push(slice_info);
            vm.slices_map[slice_info.id] = slice_info.label;
            vm.slices_edit_mode[slice_info.id] = !slice_info.annotated;
        }

        function _getSliceLabel(slice_id) {
            return vm.slices_map[slice_id];
        }

        function _registerCore(core_info) {
            $rootScope.cores.push(core_info);
            vm.cores_map[core_info.id] = core_info.label;
            if (core_info.tumor === true) {
                vm.cores_edit_mode[core_info.id] = !core_info.annotated;
            }
        }

        function _getCoreLabel(core_id) {
            return vm.cores_map[core_id];
        }

        function _registerFocusRegion(focus_region_info) {
            $rootScope.focus_regions.push(focus_region_info);
            vm.focus_regions_map[focus_region_info.id] = focus_region_info.label;
            if (focus_region_info.tumor === true || focus_region_info.stressed === true) {
                vm.focus_regions_edit_mode[focus_region_info.id] = !focus_region_info.annotated;
            }
        }

        function _getFocusRegionLabel(focus_region_id) {
            return vm.focus_regions_map[focus_region_id];
        }

        function _registerGleasonPattern(gleason_pattern_info) {
            $rootScope.gleason_patterns.push(gleason_pattern_info);
            vm.gleason_patterns_map[gleason_pattern_info.id] = gleason_pattern_info.label;
        }

        function _getGleasonPatternLabel(gleason_pattern_id) {
            return vm.gleason_patterns_map[gleason_pattern_id];
        }

        function _createListItem(label, edit_mode, set_neg_margin_cls) {
            var html = '<li id="';
            html += label;
            html += '_list" class="list-group-item prm-tree-item';
            if (set_neg_margin_cls) {
                html += ' prm-tree-item-neg-margin';
            }
            html += '"><a id="';
            html += label;
            if (edit_mode === true) {
                html += '" class="prm-tree-el" href="#"><i class="icon-black_question"></i> ';
            } else {
                html += '" class="prm-tree-el" href="#"><i class="icon-check_circle"></i> ';
            }
            html += label;
            html += '</a></li>';
            return html;
        }

        function _createNewSubtree(roi_label) {
            var html = '<ul id="' + roi_label + '_tree" class="list-group"></ul>';
            return html;
        }

        function _focusOnShape(shape_type, roi_id) {
            var shape_id = undefined;
            switch (shape_type) {
                case 'slice':
                    shape_id = vm.slices_map[roi_id];
                    break;
                case 'core':
                    shape_id = vm.cores_map[roi_id];
                    break;
                case 'focus_region':
                    shape_id = vm.focus_regions_map[roi_id];
                    break;
                case 'gleason_pattern':
                    shape_id = vm.gleason_patterns_map[roi_id];
                    break;
            }
            AnnotationsViewerService.focusOnShape(shape_id);
        }

        function canCloseAnnotation() {
            // only cores annotation is mandatory
            for (var x in vm.cores_edit_mode) {
                if (vm.cores_edit_mode[x] === true) {
                    return false;
                }
            }
            return true;
        }

        function canClearAnnotations() {
            for (var x in vm.slices_edit_mode) {
                if (vm.slices_edit_mode[x] === false) {
                    return true;
                }
            }
            for (var x in vm.cores_edit_mode) {
                if (vm.cores_edit_mode[x] === false) {
                    return true;
                }
            }
            for (var x in vm.focus_regions_edit_mode) {
                if (vm.focus_regions_edit_mode[x] === false) {
                    return true;
                }
            }
            return false;
        }

        function closeAnnotation() {
            var missingSlices = 0;
            for (var x in vm.slices_edit_mode) {
                if (vm.slices_edit_mode[x] === true) {
                    missingSlices += 1;
                }
            }

            var missingFocusRegions = 0;
            for (var x in vm.focus_regions_edit_mode) {
                if (vm.focus_regions_edit_mode[x] === true) {
                    missingFocusRegions += 1;
                }
            }

            var dialogData = {
                'missing_slices': missingSlices,
                'missing_focus_regions': missingFocusRegions
            };

            ngDialog.openConfirm({
                template: '/static/templates/dialogs/accept_clinical_annotation_confirm.html',
                showClose: false,
                closeByEscape: false,
                closeByNavigation: false,
                closeByDocument: false,
                controller: 'NewScopeController',
                controllerAs: 'confirmCtrl',
                data: dialogData
            }).then(confirmFn);

            function confirmFn(confirm_obj) {
                if (confirm_obj.value === true) {
                    ClinicalAnnotationStepService.closeAnnotationStep(vm.clinical_annotation_step_label,
                        confirm_obj.notes).then(closeClinicalAnnotationStepSuccessFn,
                            closeClinicalAnnotationStepErrorFn);
                }

                function closeClinicalAnnotationStepSuccessFn(response) {
                    if (response.data.clinical_annotation_closed === true) {
                        $location.url('worklist');
                    } else {
                        $location.url('worklist/clinical_annotations/' + vm.clinical_annotation_label);
                    }
                }

                function closeClinicalAnnotationStepErrorFn(response) {
                    $log.error(response.error);
                }
            }
        }

        function clearAnnotations() {
            ngDialog.openConfirm({
                template: '/static/templates/dialogs/clear_clinical_annotations_confirm.html',
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

                    ClinicalAnnotationStepManagerService.clearAnnotations(vm.clinical_annotation_step_label)
                        .then(clearAnnotationsSuccessFn, clearAnnotationsErrorFn);
                }

                function clearAnnotationsSuccessFn(response) {
                    for (var x in vm.slices_map) {
                        $rootScope.$broadcast('slice_annotation.deleted', vm.slices_map[x], x);
                    }
                    for (var x in vm.cores_map) {
                        $rootScope.$broadcast('core_annotation.deleted', vm.cores_map[x], x);
                    }
                    for (var x in vm.focus_regions_map) {
                        $rootScope.$broadcast('focus_region_annotation.deleted',
                            vm.focus_regions_map[x], x);
                    }
                    dialog.close();
                }

                function clearAnnotationsErrorFn(response) {
                    $log.error('unable to clear existing annotations');
                    $log.error(response);
                    dialog.close();
                }
            }
        }

        function rejectAnnotation() {
            ngDialog.openConfirm({
                template: '/static/templates/dialogs/reject_annotation_confirm.html',
                closeByEscape: false,
                showClose: false,
                closeByNavigation: false,
                closeByDocument: false,
                controller: 'RejectClinicalAnnotationStepController',
                controllerAs: 'crc'
            }).then(confirmFn);

            function confirmFn(confirm_obj) {
                if (confirm_obj.value === true) {
                    ClinicalAnnotationStepService.closeAnnotationStep(vm.clinical_annotation_step_label,
                        confirm_obj.notes, true, confirm_obj.reason)
                        .then(rejectClinicalAnnotationStepSuccessFn, rejectClinicalAnnotationStepErrorFn);
                }

                function rejectClinicalAnnotationStepSuccessFn(response) {
                    if (response.data.clinical_annotation_closed === true) {
                        $location.url('worklist');
                    } else {
                        $location.url('worklist/clinical_annotations/' + vm.clinical_annotation_label);
                    }
                }

                function rejectClinicalAnnotationStepErrorFn(response) {
                    $log.error(response.error);
                }
            }
        }

        function showROIPanel(roi_type, roi_id) {
            if (!vm.roisTreeLocked) {
                var edit_mode = undefined;
                switch (roi_type) {
                    case 'slice':
                        edit_mode = roi_id in vm.slices_edit_mode ? vm.slices_edit_mode[roi_id] : false;
                        break;
                    case 'core':
                        edit_mode = roi_id in vm.cores_edit_mode ? vm.cores_edit_mode[roi_id] : false;
                        break;
                    case 'focus_region':
                        edit_mode = roi_id in vm.focus_regions_edit_mode ?
                            vm.focus_regions_edit_mode[roi_id] : false;
                        break;
                }
                vm.deselectROI(roi_type, roi_id);
                vm._focusOnShape(roi_type, roi_id);
                if (edit_mode === true) {
                    if (!vm.roisTreeLocked) {
                        switch (roi_type) {
                            case 'slice':
                                vm.activateNewSliceAnnotationMode(roi_id);
                                break;
                            case 'core':
                                vm.activateNewCoreAnnotationMode(roi_id);
                                break;
                            case 'focus_region':
                                vm.activateNewFocusRegionAnnotationMode(roi_id);
                        }
                    }
                } else {
                    switch (roi_type) {
                        case 'slice':
                            vm.activateShowSliceAnnotationMode(roi_id);
                            break;
                        case 'core':
                            vm.activateShowCoreAnnotationMode(roi_id);
                            break;
                        case 'focus_region':
                            vm.activateShowFocusRegionAnnotationMode(roi_id);
                    }
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
                    case 'gleason_pattern':
                        AnnotationsViewerService.selectShape(vm._getGleasonPatternLabel(roi_id));
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
                    case 'gleason_pattern':
                        AnnotationsViewerService.deselectShape(vm._getGleasonPatternLabel(roi_id));
                        break;
                }
            }
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

        function newClinicalAnnotationModeActive() {
            return (
                vm.ui_active_modes['annotate_slice']
                || vm.ui_active_modes['annotate_core']
                || vm.ui_active_modes['annotate_focus_region']
            );
        }

        function activateNewSliceAnnotationMode(slice_id) {
            vm.allModesOff();
            vm._lockRoisTree();
            $rootScope.$broadcast('slice_annotation.new', slice_id);
            vm.ui_active_modes['annotate_slice'] = true;
        }

        function newSliceAnnotationModeActive() {
            return vm.ui_active_modes['annotate_slice'];
        }

        function activateShowSliceAnnotationMode(slice_id) {
            vm.allModesOff();
            $rootScope.$broadcast('slice_annotation.show', slice_id);
            vm.ui_active_modes['show_slice'] = true;
        }

        function showSliceAnnotationModeActive() {
            return vm.ui_active_modes['show_slice'];
        }

        function activateNewCoreAnnotationMode(core_id) {
            vm.allModesOff();
            vm._lockRoisTree();
            $rootScope.$broadcast('core_annotation.new', core_id);
            vm.ui_active_modes['annotate_core'] = true;
        }

        function newCoreAnnotationModeActive() {
            return vm.ui_active_modes['annotate_core'];
        }

        function activateShowCoreAnnotationMode(core_id) {
            vm.allModesOff();
            $rootScope.$broadcast('core_annotation.show', core_id);
            vm.ui_active_modes['show_core'] = true;
        }

        function showCoreAnnotationModeActive() {
            return vm.ui_active_modes['show_core'];
        }

        function activateNewFocusRegionAnnotationMode(focus_region_id) {
            vm.allModesOff();
            vm._lockRoisTree();
            $rootScope.$broadcast('focus_region_annotation.new', focus_region_id);
            vm.ui_active_modes['annotate_focus_region'] = true;
        }

        function newFocusRegionAnnotationModeActive() {
            return vm.ui_active_modes['annotate_focus_region']
        }

        function activateShowFocusRegionAnnotationMode(focus_region_id) {
            vm.allModesOff();
            $rootScope.$broadcast('focus_region_annotation.show', focus_region_id);
            vm.ui_active_modes['show_focus_region'] = true;
        }

        function showFocusRegionAnnotationModeActive() {
            return vm.ui_active_modes['show_focus_region'];
        }

        function activateNewGleasonPatternAnnotationMode() {
            vm.allModesOff();
            vm._lockRoisTree();
            vm.ui_active_modes['annotate_gleason_pattern'] = true;
            $rootScope.$broadcast('gleason_pattern.creation_mode');
        }

        function newGleasonPatternAnnotationModeActive() {
            return vm.ui_active_modes['annotate_gleason_pattern'];
        }

        function activateShowGleasonPatternAnnotationMode() {
            vm.allModesOff();
            vm.ui_active_modes['show_gleason_pattern'] = true;
        }

        function showGleasonPatternAnnotationModeActive() {
            return vm.ui_active_modes['show_gleason_pattern'];
        }

        function getPositiveFocusRegionsCount() {
            return vm.positive_fr_count;
        }

        function annotationModeActive() {
            return (
                vm.ui_active_modes.annotate_slice
                || vm.ui_active_modes.annotate_core
                || vm.ui_active_modes.annotate_focus_region
                || vm.ui_active_modes.annotate_gleason_pattern
            );
        }
    }

    RejectClinicalAnnotationStepController.$inject = ['$scope', '$log', 'ClinicalAnnotationStepManagerService'];

    function RejectClinicalAnnotationStepController($scope, $log, ClinicalAnnotationStepManagerService) {
        var vm = this;
        vm.$scope = {};
        vm.rejection_reasons = undefined;
        vm.rejectionReason = undefined;
        vm.canSend = canSend;

        activate();

        function activate() {
            ClinicalAnnotationStepManagerService.fetchRejectionReasons()
                .then(fetchRejectionReasonsSuccessFn);

            function fetchRejectionReasonsSuccessFn(response) {
                vm.rejection_reasons = response.data;
            }
        }

        function canSend() {
            return (typeof vm.rejectionReason !== 'undefined') && (vm.rejectionReason !== '');
        }
    }

    NewSliceAnnotationController.$inject = ['$scope', '$routeParams', '$rootScope', '$log', 'ngDialog',
        'SlicesManagerService', 'SliceAnnotationsManagerService'];

    function NewSliceAnnotationController($scope, $routeParams, $rootScope, $log, ngDialog,
        SlicesManagerService, SliceAnnotationsManagerService) {
        var vm = this;
        vm.slice_id = undefined;
        vm.slice_label = undefined;
        vm.totalCores = undefined;
        vm.positiveCores = undefined;
        vm.highGradePin = false;
        vm.pah = false;
        vm.chronicInflammation = false;
        vm.acuteInflammation = false;
        vm.periglandularInflammation = false;
        vm.intraglandularInflammation = false;
        vm.stromalInflammation = false;

        vm.actionStartTime = undefined;

        vm.clinical_annotation_step_label = undefined;

        vm._clean = _clean;
        vm.isReadOnly = isReadOnly;
        vm.isLocked = isLocked;
        vm.formValid = formValid;
        vm.destroy = destroy;
        vm.save = save;

        activate();

        function activate() {
            vm.clinical_annotation_step_label = $routeParams.label;
            $scope.$on('slice_annotation.new',
                function (event, slice_id) {
                    vm.slice_id = slice_id;
                    SlicesManagerService.get(vm.slice_id)
                        .then(getSliceSuccessFn, getSliceErrorFn);
                }
            );

            function getSliceSuccessFn(response) {
                vm.slice_label = response.data.label;
                vm.totalCores = response.data.total_cores;
                vm.positiveCores = response.data.positive_cores_count;
                vm.actionStartTime = new Date();
            }

            function getSliceErrorFn(response) {
                $log.error('Unable to load slice data');
                $log.error(response);
            }
        }

        function _clean() {
            vm.slice_id = undefined;
            vm.slice_label = undefined;
            vm.totalCores = undefined;
            vm.positiveCores = undefined;
            vm.highGradePin = false;
            vm.pah = false;
            vm.chronicInflammation = false;
            vm.acuteInflammation = false;
            vm.periglandularInflammation = false;
            vm.intraglandularInflammation = false;
            vm.stromalInflammation = false;
            vm.actionStartTime = undefined;
        }

        function isReadOnly() {
            return false;
        }

        function isLocked() {
            return false;
        }

        function formValid() {
            return true;
        }

        function destroy() {
            vm._clean();
            $rootScope.$broadcast('annotation_panel.closed');
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
            var obj_config = {
                high_grade_pin: vm.highGradePin,
                pah: vm.pah,
                chronic_inflammation: vm.chronicInflammation,
                acute_inflammation: vm.acuteInflammation,
                periglandular_inflammation: vm.periglandularInflammation,
                intraglandular_inflammation: vm.intraglandularInflammation,
                stromal_inflammation: vm.stromalInflammation,
                action_start_time: vm.actionStartTime,
                action_complete_time: new Date()
            };
            SliceAnnotationsManagerService.createAnnotation(vm.slice_id, vm.clinical_annotation_step_label, obj_config)
                .then(createAnnotationSuccessFn, createAnnotationErrorFn);

            function createAnnotationSuccessFn(response) {
                $rootScope.$broadcast('slice_annotation.saved', vm.slice_label, vm.slice_id);
                vm._clean();
                dialog.close();
            }

            function createAnnotationErrorFn(response) {
                $log.error('Unable to save annotation');
                $log.error(response.data);
                dialog.close();
            }
        }
    }

    ShowSliceAnnotationController.$inject = ['$scope', '$routeParams', '$rootScope', '$log', 'ngDialog',
        'SliceAnnotationsManagerService'];

    function ShowSliceAnnotationController($scope, $routeParams, $rootScope, $log, ngDialog,
        SliceAnnotationsManagerService) {
        var vm = this;
        vm.slice_id = undefined;
        vm.slice_label = undefined;
        vm.totalCores = undefined;
        vm.positiveCores = undefined;
        vm.highGradePin = undefined;
        vm.pah = undefined;
        vm.chronicInflammation = undefined;
        vm.acuteInflammation = undefined;
        vm.periglandularInflammation = undefined;
        vm.intraglandularInflammation = undefined;
        vm.stromalInflammation = undefined;
        vm.gleason4Percentage = undefined;

        vm.clinical_annotation_step_label = undefined;

        vm.isReadOnly = isReadOnly;
        vm.isLocked = isLocked;
        vm.destroy = destroy;
        vm.deleteAnnotation = deleteAnnotation;

        activate();

        function activate() {
            vm.clinical_annotation_step_label = $routeParams.label;
            $scope.$on('slice_annotation.show',
                function (event, slice_id) {
                    vm.slice_id = slice_id;
                    SliceAnnotationsManagerService.getAnnotation(vm.slice_id, vm.clinical_annotation_step_label)
                        .then(getSliceAnnotationSuccessFn, getSliceAnnotationErrorFn);
                }
            );

            function getSliceAnnotationSuccessFn(response) {
                vm.slice_label = response.data.slice.label;
                vm.totalCores = response.data.slice.total_cores;
                vm.positiveCores = response.data.slice.positive_cores_count;
                vm.highGradePin = response.data.high_grade_pin;
                vm.pah = response.data.pah;
                vm.chronicInflammation = response.data.chronic_inflammation;
                vm.acuteInflammation = response.data.acute_inflammation;
                vm.periglandularInflammation = response.data.periglandular_inflammation;
                vm.intraglandularInflammation = response.data.intraglandular_inflammation;
                vm.stromalInflammation = response.data.stromal_inflammation;
                vm.gleason4Percentage = Number(parseFloat(response.data.gleason_4_percentage).toFixed(3));
            }

            function getSliceAnnotationErrorFn(response) {
                $log.error('Unable to load slice annotatin data');
                $log.error(response);
            }
        }

        function isReadOnly() {
            return true;
        }

        function isLocked() {
            return false;
        }

        function destroy() {
            $rootScope.$broadcast('annotation_panel.closed');
        }

        function deleteAnnotation() {
            ngDialog.openConfirm({
                template: '/static/templates/dialogs/delete_annotation_confirm.html',
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
                        showClose: true,
                        closeByEscape: false,
                        closeByNavigation: false,
                        closeByDocument: false
                    });
                    SliceAnnotationsManagerService.deleteAnnotation(vm.slice_id, vm.clinical_annotation_step_label)
                        .then(deleteSliceAnnotationSuccessFn, deleteSliceAnnotationErrorFn);
                }
            }

            function deleteSliceAnnotationSuccessFn(response) {
                $rootScope.$broadcast('slice_annotation.deleted', vm.slice_label, vm.slice_id);
                vm.slice_id = undefined;
                vm.slice_label = undefined;
                vm.totalCores = undefined;
                vm.positiveCores = undefined;
                vm.highGradePin = undefined;
                vm.pah = undefined;
                vm.chronicInflammation = undefined;
                vm.acuteInflammation = undefined;
                vm.periglandularInflammation = undefined;
                vm.intraglandularInflammation = undefined;
                vm.stromalInflammation = undefined;
                dialog.close();
            }

            function deleteSliceAnnotationErrorFn(response) {
                $log.error('unable to delete slice annotation');
                $log.error(response);
                dialog.close();
            }
        }
    }

    NewCoreAnnotationController.$inject = ['$scope', '$routeParams', '$rootScope', '$log', 'ngDialog',
        'CoreGleasonDetailsManagerService', 'CoreAnnotationsManagerService', 'AnnotationsViewerService'];

    function NewCoreAnnotationController($scope, $routeParams, $rootScope, $log, ngDialog,
        CoreGleasonDetailsManagerService, CoreAnnotationsManagerService, AnnotationsViewerService) {
        var vm = this;
        vm.core_id = undefined;
        vm.core_label = undefined;
        vm.coreArea = undefined;
        vm.coreLength = undefined;
        vm.tumorLength = undefined;
        // vm.primaryGleason = undefined;
        // vm.secondaryGleason = undefined;
        vm.gleasonScore = undefined;
        vm.gradeGroupWho = undefined;
        vm.gradeGroupWhoLabel = ''
        vm.gleasonDetails = undefined;
        vm.gleasonHighlighted = undefined;
        vm.predominant_rsg = undefined;
        vm.highest_rsg = undefined;
        vm.rsg_within_highest_grade_area = undefined;
        vm.rsg_in_area_of_cribriform_morphology = undefined;
        vm.perineural_invasion = undefined;
        vm.perineural_growth_with_cribriform_patterns = undefined;
        vm.extraprostatic_extension = undefined;
        // only if at least one cribriform pattern exists
        vm.nuclear_grade_size = undefined;
        vm.intraluminal_acinar_differentiation_grade = undefined;
        vm.intraluminal_secretions = undefined;
        vm.central_maturation = undefined;
        vm.extra_cribriform_gleason_score = undefined;

        vm.actionStartTime = undefined;

        vm.clinical_annotation_step_label = undefined;

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
            { id: 1, unit_of_measure: 'μm²' },
            { id: Math.pow(10, -6), unit_of_measure: 'mm²' }
        ];

        vm.gleasonPatternsColors = {
            "G3": "#ffcc99",
            "G4": "#ff9966",
            "G5": "#cc5200"
        }

        vm._clean = _clean;
        vm._parseGleasonScore = _parseGleasonScore;
        vm.getCoverage = getCoverage;
        vm.gleasonDetailsAvailable = gleasonDetailsAvailable;
        vm._getGleasonShapesLabels = _getGleasonShapesLabels;
        vm.gleasonHighlightSwitch = gleasonHighlightSwitch;
        vm.isHighlighted = isHighlighted;
        vm.selectGleasonPatterns = selectGleasonPatterns;
        vm.isReadOnly = isReadOnly;
        vm.isLocked = isLocked;
        vm.formValid = formValid;
        vm.destroy = destroy;
        vm.updateGradeGroupWho = updateGradeGroupWho;
        vm.containsCribriformPattern = containsCribriformPattern;
        vm.save = save;
        vm.updateTumorLength = updateTumorLength;
        vm.updateCoreLength = updateCoreLength;
        vm.updateCoreArea = updateCoreArea;

        activate();

        function activate() {
            vm.coreLengthScaleFactor = vm.lengthUOM[0];
            vm.tumorLengthScaleFactor = vm.lengthUOM[0];
            vm.coreAreaScaleFactor = vm.areaUOM[0];

            vm.clinical_annotation_step_label = $routeParams.label;
            $scope.$on('core_annotation.new',
                function (event, core_id) {
                    vm.core_id = core_id;
                    CoreGleasonDetailsManagerService.get(vm.core_id, vm.clinical_annotation_step_label)
                        .then(getCoreSuccessFn, getCoreErrorFn);
                }
            );

            function getCoreSuccessFn(response) {
                vm.core_label = response.data.label;
                vm.coreArea = response.data.area;
                vm.updateCoreArea();
                vm.coreLength = response.data.length;
                vm.updateCoreLength();
                vm.tumorLength = response.data.tumor_length;
                vm.updateTumorLength();
                vm.gleasonScore = vm._parseGleasonScore(
                    response.data.primary_gleason,
                    response.data.secondary_gleason
                )
                vm.updateGradeGroupWho(
                    response.data.primary_gleason,
                    response.data.secondary_gleason
                );
                vm.gleasonDetails = response.data.details;
                vm.gleasonHighlighted = {
                    "G3": false,
                    "G4": false,
                    "G5": false
                }
                vm.actionStartTime = new Date();
            }

            function getCoreErrorFn(response) {
                $log.error('Unable to load core data');
                $log.error(response);
            }
        }

        function _clean() {
            vm.core_id = undefined;
            vm.core_label = undefined;
            vm.coreArea = undefined;
            vm.coreLength = undefined;
            vm.tumorLength = undefined;
            vm.gleasonScore = undefined;
            vm.gradeGroupWho = undefined;
            vm.gradeGroupWhoLabel = '';
            vm.gleasonDetails = undefined;
            vm.gleasonHighlighted = {
                "G3": false,
                "G4": false,
                "G5": false
            }
            vm.predominant_rsg = undefined;
            vm.highest_rsg = undefined;
            vm.rsg_within_highest_grade_area = undefined;
            vm.rsg_in_area_of_cribriform_morphology = undefined;
            vm.perineural_invasion = undefined;
            vm.perineural_growth_with_cribriform_patterns = undefined;
            vm.extraprostatic_extension = undefined;
            vm.nuclear_grade_size = undefined;
            vm.intraluminal_acinar_differentiation_grade = undefined;
            vm.intraluminal_secretions = undefined;
            vm.central_maturation = undefined;
            vm.extra_cribriform_gleason_score = undefined;

            vm.actionStartTime = undefined;
        }

        function _parseGleasonScore(primary_gleason, secondary_gleason) {
            if((primary_gleason !== null) && (secondary_gleason !== null)){
                return parseInt(primary_gleason.replace(/\D/g, '')) + "+" + parseInt(secondary_gleason.replace(/\D/g, ''));
            } else {
                return undefined;
            }
        }

        function getCoverage(gleason_pattern) {
            if (vm.gleasonDetails !== undefined) {
                var pattern_data = vm.gleasonDetails[gleason_pattern];
                if (pattern_data !== undefined) {
                    return pattern_data.total_coverage + " %";
                } else {
                    return "0 %";
                }
            }
        }

        function gleasonDetailsAvailable(gleason_pattern) {
            if (vm.gleasonDetails !== undefined) {
                return vm.gleasonDetails.hasOwnProperty(gleason_pattern);
            } else {
                return false;
            }
        }

        function _getGleasonShapesLabels(gleason_pattern) {
            if (vm.gleasonDetails !== undefined) {
                if (vm.gleasonDetails.hasOwnProperty(gleason_pattern)) {
                    return vm.gleasonDetails[gleason_pattern].shapes;
                }
            }
            return undefined;
        }

        function gleasonHighlightSwitch(gleason_pattern) {
            if (vm.gleasonDetails !== undefined) {
                if (vm.gleasonDetails.hasOwnProperty(gleason_pattern)) {
                    var gleason_shapes = vm._getGleasonShapesLabels(gleason_pattern);
                    var pattern_highlighted = vm.gleasonHighlighted[gleason_pattern];
                    if (pattern_highlighted) {
                        var shape_color = "#ffffff";
                        var shape_alpha = "0";
                    } else {
                        var shape_color = vm.gleasonPatternsColors[gleason_pattern];
                        var shape_alpha = "0.35";
                    }
                    for (const shape of gleason_shapes) {
                        AnnotationsViewerService.setShapeFillColor(shape, shape_color, shape_alpha);
                    }
                    vm.gleasonHighlighted[gleason_pattern] = !vm.gleasonHighlighted[gleason_pattern];
                }
            }
        }

        function isHighlighted(gleason_pattern) {
            if (vm.gleasonDetails !== undefined && vm.gleasonDetails.hasOwnProperty(gleason_pattern)) {
                return vm.gleasonHighlighted[gleason_pattern];
            } else {
                return false;
            }

        }

        function selectGleasonPatterns(gleason_pattern, activate) {
            if (vm.gleasonDetails !== undefined) {
                if (vm.gleasonDetails.hasOwnProperty(gleason_pattern)) {
                    var gleason_shapes = vm._getGleasonShapesLabels(gleason_pattern);
                    if (activate) {
                        AnnotationsViewerService.selectShapes(gleason_shapes);
                    } else {
                        AnnotationsViewerService.deselectShapes(gleason_shapes);
                    }
                }
            }
        }

        function isReadOnly() {
            return false;
        }

        function isLocked() {
            return false;
        }

        function formValid() {
            return ((typeof vm.primaryGleason !== 'undefined') &&
                (typeof vm.secondaryGleason !== 'undefined'));
        }

        function destroy() {
            vm._clean();
            $rootScope.$broadcast('annotation_panel.closed');
        }

        function updateGradeGroupWho(primary_gleason, secondary_gleason) {
            if((primary_gleason !== null) && (secondary_gleason !== null)) {
                var gleason_score = parseInt(primary_gleason.replace(/\D/g, '')) + parseInt(secondary_gleason.replace(/\D/g, ''));
                if (gleason_score <= 6) {
                    vm.gradeGroupWho = 'GG1';
                    vm.gradeGroupWhoLabel = 'Group 1'
                } else if (gleason_score == 7) {
                    if (vm.primaryGleason == 3) {
                        vm.gradeGroupWho = 'GG2';
                        vm.gradeGroupWhoLabel = 'Group 2';
                    } else {
                        vm.gradeGroupWho = 'GG3';
                        vm.gradeGroupWhoLabel = 'Group 3';
                    }
                } else if (gleason_score == 8) {
                    vm.gradeGroupWho = 'GG4';
                    vm.gradeGroupWhoLabel = 'Group 4';
                } else {
                    vm.gradeGroupWho = 'GG5';
                    vm.gradeGroupWhoLabel = 'Group 5';
                }
            } else {
                vm.gradeGroupWho = undefined;
                vm.gradeGroupWhoLabel = '';
            }
        }

        function containsCribriformPattern() {
            // TODO: implement this function to check if at least one cribriform pattern exists (using a service?)
            return false;
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
            var obj_config = {
                primary_gleason: Number(vm.primaryGleason),
                secondary_gleason: Number(vm.secondaryGleason),
                gleason_group: vm.gradeGroupWho,
                action_start_time: vm.actionStartTime,
                action_complete_time: new Date(),
                predominant_rsg: vm.predominant_rsg,
                highest_rsg: vm.highest_rsg,
                rsg_within_highest_grade_area: vm.rsg_within_highest_grade_area,
                rsg_in_area_of_cribriform_morphology: vm.rsg_in_area_of_cribriform_morphology,
                perineural_invasion: typeof (vm.perineural_invasion) == "undefined" ? false : vm.perineural_invasion,
                perineural_growth_with_cribriform_patterns: typeof (vm.perineural_growth_with_cribriform_patterns) == "undefined" ? false : vm.perineural_growth_with_cribriform_patterns,
                extraprostatic_extension: typeof (vm.extraprostatic_extension) == "undefined" ? false : vm.extraprostatic_extension
            }
            if (vm.containsCribriformPattern()) {
                obj_config.nuclear_grade_size = vm.nuclear_grade_size;
                obj_config.intraluminal_acinar_differentiation_grade = vm.intraluminal_acinar_differentiation_grade;
                obj_config.intraluminal_secretions = typeof (vm.intraluminal_secretions) == "undefined" ? false : vm.intraluminal_secretions;
                obj_config.central_maturation = typeof (vm.central_maturation) == "undefined" ? false : vm.central_maturation;
                obj_config.extra_cribriform_gleason_score = vm.extra_cribriform_gleason_score;
            }
            console.log(obj_config);
            CoreAnnotationsManagerService.createAnnotation(vm.core_id, vm.clinical_annotation_step_label, obj_config)
                .then(createAnnotationSuccessFn, createAnnotationErrorFn);

            function createAnnotationSuccessFn(response) {
                $rootScope.$broadcast('core_annotation.saved', vm.core_label, vm.core_id);
                vm._clean();
                dialog.close();
            }

            function createAnnotationErrorFn(response) {
                $log.error('Unable to save annotation');
                $log.error(response.data);
                dialog.close();
            }
        }

        function updateCoreLength() {
            vm.scaledCoreLength = formatDecimalNumber(
                (vm.coreLength * vm.coreLengthScaleFactor.id), 3
            )
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

    ShowCoreAnnotationController.$inject = ['$scope', '$routeParams', '$rootScope', '$log', 'ngDialog',
        'CoreAnnotationsManagerService', 'CoresManagerService'];

    function ShowCoreAnnotationController($scope, $routeParams, $rootScope, $log, ngDialog,
        CoreAnnotationsManagerService, CoresManagerService) {
        var vm = this;
        vm.core_id = undefined;
        vm.core_label = undefined;
        vm.coreArea = undefined;
        vm.coreLength = undefined;
        vm.tumorLength = undefined;
        vm.normalTissuePercentage = undefined;
        vm.gleasonScore = undefined;
        vm.gradeGroupWhoLabel = undefined;
        vm.gleason4Percentage = undefined;
        vm.predominant_rsg = undefined;
        vm.highest_rsg = undefined;
        vm.rsg_within_highest_grade_area = undefined;
        vm.rsg_in_area_of_cribriform_morphology = undefined;
        vm.perineural_invasion = undefined;
        vm.perineural_growth_with_cribriform_patterns = undefined;
        vm.extraprostatic_extension = undefined;
        // only if at least one cribriform pattern exists
        vm.nuclear_grade_size = undefined;
        vm.intraluminal_acinar_differentiation_grade = undefined;
        vm.intraluminal_secretions = undefined;
        vm.central_maturation = undefined;
        vm.extra_cribriform_gleason_score = undefined;

        vm.clinical_annotation_step_label = undefined;

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
            { id: 1, unit_of_measure: 'μm²' },
            { id: Math.pow(10, -6), unit_of_measure: 'mm²' }
        ];

        vm.locked = undefined;

        vm.isReadOnly = isReadOnly;
        vm.isLocked = isLocked;
        vm.destroy = destroy;
        vm.deleteAnnotation = deleteAnnotation;
        vm.updateTumorLength = updateTumorLength;
        vm.updateCoreLength = updateCoreLength;
        vm.updateCoreArea = updateCoreArea;

        activate();

        function activate() {
            vm.coreLengthScaleFactor = vm.lengthUOM[0];
            vm.tumorLengthScaleFactor = vm.lengthUOM[0];
            vm.coreAreaScaleFactor = vm.areaUOM[0];

            vm.clinical_annotation_step_label = $routeParams.label;
            $scope.$on('core_annotation.show',
                function (event, core_id) {
                    vm.locked = false;
                    vm.core_id = core_id;
                    CoreAnnotationsManagerService.getAnnotation(vm.core_id, vm.clinical_annotation_step_label)
                        .then(getCoreAnnotationSuccessFn, getCoreAnnotationErrorFn);
                }
            );

            function getCoreAnnotationSuccessFn(response) {
                vm.core_label = response.data.core.label;
                vm.coreArea = response.data.core.area;
                vm.updateCoreArea();
                vm.coreLength = response.data.core.length;
                vm.updateCoreLength();
                vm.tumorLength = response.data.core.tumor_length;
                vm.updateTumorLength();
                vm.normalTissuePercentage = Number(parseFloat(response.data.core.normal_tissue_percentage).toFixed(3));
                vm.gleasonScore = response.data.gleason_score;
                vm.gleason4Percentage = Number(parseFloat(response.data.gleason_4_percentage).toFixed(3));
                switch (response.data.gleason_group) {
                    case 'GG1':
                        vm.gradeGroupWhoLabel = 'Group 1';
                        break;
                    case 'GG2':
                        vm.gradeGroupWhoLabel = 'Group 2';
                        break;
                    case 'GG3':
                        vm.gradeGroupWhoLabel = 'Group 3';
                        break;
                    case 'GG4':
                        vm.gradeGroupWhoLabel = 'Group 4';
                        break;
                    case 'GG5':
                        vm.gradeGroupWhoLabel = 'Group 5';
                        break
                }
                vm.predominant_rsg = response.data.predominant_rsg;
                vm.highest_rsg = response.data.highest_rsg;
                vm.rsg_within_highest_grade_area = response.data.rsg_within_highest_grade_area;
                vm.rsg_in_area_of_cribriform_morphology = response.data.rsg_in_area_of_cribriform_morphology;
                vm.perineural_invasion = response.data.perineural_invasion;
                vm.perineural_growth_with_cribriform_patterns = response.data.perineural_growth_with_cribriform_patterns;
                vm.extraprostatic_extension = response.data.extraprostatic_extension;
                // only if at least one cribriform pattern exists
                vm.nuclear_grade_size = response.data.nuclear_grade_size;
                vm.intraluminal_acinar_differentiation_grade = response.data.intraluminal_acinar_differentiation_grade;
                vm.intraluminal_secretions = response.data.intraluminal_secretions;
                vm.central_maturation = response.data.central_maturation;
                vm.extra_cribriform_gleason_score = response.data.extra_cribriform_gleason_score;
            }

            function getCoreAnnotationErrorFn(response) {
                if (response.status === 404) {
                    CoresManagerService.get(vm.core_id)
                        .then(getCoreSuccessFn, getCoreErrorFn);
                }
                else {
                    $log.error('Unable to load core annotation data');
                    $log.error(response);
                }

                function getCoreSuccessFn(response) {
                    vm.core_label = response.data.label;
                    vm.coreArea = response.data.area;
                    vm.updateCoreArea();
                    vm.coreLength = response.data.length;
                    vm.updateCoreLength();
                    vm.tumorLength = response.data.tumor_length;
                    vm.updateTumorLength();
                    vm.normalTissuePercentage = response.data.normal_tissue_percentage;
                    vm.locked = true;
                }

                function getCoreErrorFn(response) {
                    $log.error('Unable to load core data');
                    $log.error(response);
                }
            }
        }

        function isReadOnly() {
            return true;
        }

        function isLocked() {
            return vm.locked;
        }

        function destroy() {
            $rootScope.$broadcast('annotation_panel.closed');
        }

        function deleteAnnotation() {
            ngDialog.openConfirm({
                template: '/static/templates/dialogs/delete_annotation_confirm.html',
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
                        showClose: true,
                        closeByEscape: false,
                        closeByNavigation: false,
                        closeByDocument: false
                    });
                    CoreAnnotationsManagerService.deleteAnnotation(vm.core_id, vm.clinical_annotation_step_label)
                        .then(deleteCoreAnnotationSuccessFn, deleteCoreAnnotationErrorFn);
                }
            }

            function deleteCoreAnnotationSuccessFn(response) {
                $rootScope.$broadcast('core_annotation.deleted', vm.core_label, vm.core_id);
                vm.core_id = undefined;
                vm.core_label = undefined;
                vm.coreArea = undefined;
                vm.coreLength = undefined;
                vm.tumorLength = undefined;
                vm.normalTissuePercentage = undefined;
                vm.gleasonScore = undefined;
                vm.gradeGroupWhoLabel = undefined;
                vm.gleason4Percentage = undefined;
                vm.predominant_rsg = undefined;
                vm.highest_rsg = undefined;
                vm.rsg_within_highest_grade_area = undefined;
                vm.rsg_in_area_of_cribriform_morphology = undefined;
                vm.perineural_invasion = undefined;
                vm.perineural_growth_with_cribriform_patterns = undefined;
                vm.extraprostatic_extension = undefined;
                vm.nuclear_grade_size = undefined;
                vm.intraluminal_acinar_differentiation_grade = undefined;
                vm.intraluminal_secretions = undefined;
                vm.central_maturation = undefined;
                vm.extra_cribriform_gleason_score = undefined;
                dialog.close();
            }

            function deleteCoreAnnotationErrorFn(response) {
                $log.error('unable to delete core annotation');
                $log.error(response);
                dialog.close();
            }
        }

        function updateCoreLength() {
            vm.scaledCoreLength = formatDecimalNumber(
                (vm.coreLength * vm.coreLengthScaleFactor.id), 3
            )
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

    NewFocusRegionAnnotationController.$inject = ['$scope', '$routeParams', '$rootScope', '$log', 'ngDialog',
        'FocusRegionsManagerService', 'FocusRegionAnnotationsManagerService', 'AnnotationsViewerService',
        'ClinicalAnnotationStepManagerService'];

    function NewFocusRegionAnnotationController($scope, $routeParams, $rootScope, $log, ngDialog,
        FocusRegionsManagerService, FocusRegionAnnotationsManagerService,
        AnnotationsViewerService, ClinicalAnnotationStepManagerService) {
        var vm = this;
        vm.focus_region_id = undefined;
        vm.focus_region_label = undefined;
        vm.focusRegionArea = undefined;
        vm.coreCoveragePercentage = undefined;
        vm.focusRegionTissueStatus = undefined;
        vm.focusRegionLength = undefined;
        vm.perineuralInvolvement = false;
        vm.intraductalCarcinoma = false;
        vm.ductalCarcinoma = false;
        vm.poorlyFormedGlands = false;
        vm.cribriformPattern = false;
        vm.smallCellSignetRing = false;
        vm.hypernephroidPattern = false;
        vm.mucinous = false;
        vm.comedoNecrosis = false;
        vm.inflammation = false;
        vm.pah = false;
        vm.atrophicLesions = false;
        vm.adenosis = false;
        vm.cellularDensityHelperShape = undefined;
        vm.cellularDensity = undefined;
        vm.cellsCount = undefined;

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
            { id: 1, unit_of_measure: 'μm²' },
            { id: Math.pow(10, -6), unit_of_measure: 'mm²' }
        ];

        vm.gleason_element_types = undefined;
        vm.gleason_types_map = undefined;

        vm.gleasonModeActive = false;

        vm.tmpGleasonShape = undefined;
        vm.tmpGleasonShapeArea = undefined;
        vm.tmpGleasonCellularDensityHelperShape = undefined;
        vm.tmpGleasonCellularDensity = undefined;
        vm.tmpGleasonType = undefined;
        vm.tmpGleasonCellsCount = undefined;

        vm.tmpGleasonActionStartTime = undefined;

        vm.gleasonElements = undefined;
        vm.gleasonElementsLabels = undefined;
        vm.displayedGleasonElementsLabels = undefined;

        vm.clinical_annotation_step_label = undefined;

        vm.ruler_tool_active = false;
        vm.ruler_hidden = true;
        vm.area_ruler_tool_paused = false;

        vm._clean = _clean;
        vm.isReadOnly = isReadOnly;
        vm.isLocked = isLocked;
        vm.isCancerousRegion = isCancerousRegion;
        vm.isStressedRegion = isStressedRegion;
        vm.formValid = formValid;
        vm.destroy = destroy;
        vm.save = save;
        vm.startGleasonTool = startGleasonTool;
        vm.stopGleasonTool = stopGleasonTool;
        vm.abortGleasonTool = abortGleasonTool;
        vm.gleasonToolActive = gleasonToolActive;
        vm.gleasonDataValid = gleasonDataValid;
        vm.initializeRuler = initializeRuler;
        vm.startRuler = startRuler;
        vm.rulerToolActive = rulerToolActive;
        vm.rulerExists = rulerExists;
        vm.temporaryRulerExists = temporaryRulerExists;
        vm.temporaryRulerValid = temporaryRulerValid;
        vm.confirmRuler = confirmRuler;
        vm.pauseRuler = pauseRuler;
        vm.unpauseRuler = unpauseRuler;
        vm.isRulerPaused = isRulerPaused;
        vm.rulerRollbackPossible = rulerRollbackPossible;
        vm.rulerRestorePossible = rulerRestorePossible;
        vm.rollbackRuler = rollbackRuler;
        vm.restoreRuler = restoreRuler;
        vm.abortRuler = abortRuler;
        vm.clearRuler = clearRuler;
        vm.showRuler = showRuler;
        vm.hideRuler = hideRuler;
        vm.showHideRuler = showHideRuler;
        vm.selectRuler = selectRuler;
        vm.deselectRuler = deselectRuler;
        vm._getGleasonElementIndexLabel = _getGleasonElementIndexLabel;
        vm.acceptTemporaryGleason = acceptTemporaryGleason;
        vm._hideGleasonElement = _hideGleasonElement;
        vm._showGleasonElement = _showGleasonElement;
        vm._showExistingGleasonElements = _showExistingGleasonElements;
        vm._restoreGleasonElementsVisibility = _restoreGleasonElementsVisibility;
        vm.gleasonElementVisible = gleasonElementVisible;
        vm.showHideGleasonElement = showHideGleasonElement;
        vm.deleteGleasonElement = deleteGleasonElement;
        vm.updateRegionLength = updateRegionLength;
        vm.updateRegionArea = updateRegionArea;

        activate();

        function activate() {
            vm.regionAreaScaleFactor = vm.areaUOM[0];
            vm.regionLengthScaleFactor = vm.lengthUOM[0];

            vm.clinical_annotation_step_label = $routeParams.label;

            vm.gleasonElements = {};
            vm.gleasonElementsLabels = [];
            vm.displayedGleasonElementsLabels = [];

            $scope.$on('focus_region_annotation.new',
                function (event, focus_region_id) {
                    vm.focus_region_id = focus_region_id;
                    FocusRegionsManagerService.get(vm.focus_region_id)
                        .then(getFocusRegionSuccessFn, getFocusRegionErrorFn);
                }
            );

            function getFocusRegionSuccessFn(response) {
                vm.focus_region_label = response.data.label;
                vm.focusRegionArea = response.data.area;
                vm.updateRegionArea();
                vm.focusRegionLength = response.data.length;
                vm.updateRegionLength();
                vm.coreCoveragePercentage = Number(parseFloat(response.data.core_coverage_percentage).toFixed(3));
                vm.focusRegionTissueStatus = response.data.tissue_status;
                vm.actionStartTime = new Date();

                ClinicalAnnotationStepManagerService.fetchGleasonElementTypes()
                    .then(fetchGleasonElementTypesSuccessFn);
                // initialize Gleason element labels
                function fetchGleasonElementTypesSuccessFn(response) {
                    vm.gleason_element_types = response.data;
                    vm.gleason_types_map = {};
                    for (var i = 0; i < vm.gleason_element_types.length; i++) {
                        vm.gleason_types_map[vm.gleason_element_types[i].value] = vm.gleason_element_types[i].text;
                    }
                }
            }

            function getFocusRegionErrorFn(response) {
                $log.error('Unable to load focus region data');
                $log.error(response);
            }

            $scope.$on('viewerctrl.components.registered',
                function () {
                    vm.initializeRuler();
                }
            );
        }

        function _clean() {
            vm.clearRuler();

            for (var el in vm.gleasonElementsLabels) {
                vm._hideGleasonElement(vm.gleasonElementsLabels[el]);
            }

            vm.focus_region_id = undefined;
            vm.focus_region_label = undefined;
            vm.focusRegionArea = undefined;
            vm.coreCoveragePercentage = undefined;
            vm.focusRegionTissueStatus = undefined;
            vm.focusRegionLength = undefined;
            vm.perineuralInvolvement = false;
            vm.intraductalCarcinoma = false;
            vm.ductalCarcinoma = false;
            vm.poorlyFormedGlands = false;
            vm.cribriformPattern = false;
            vm.smallCellSignetRing = false;
            vm.hypernephroidPattern = false;
            vm.mucinous = false;
            vm.comedoNecrosis = false;
            vm.inflammation = false;
            vm.pah = false;
            vm.atrophicLesions = false;
            vm.adenosis = false;
            vm.cellsCount = undefined;

            vm.actionStartTime = undefined;

            vm.gleasonElements = {};
            vm.gleasonElementsLabels = [];
            vm.displayedGleasonElementsLabels = [];

            AnnotationsViewerService.disableActiveTool();
            vm.ruler_tool_active = false;
            vm.ruler_hidden = true;
            vm.stopGleasonTool();
        }

        function startGleasonTool() {
            vm.gleasonModeActive = true;
            vm._showExistingGleasonElements();
        }

        function stopGleasonTool() {
            vm.gleasonModeActive = false;
            vm.tmpGleasonCellsCount = undefined;
            vm._restoreGleasonElementsVisibility();
        }

        function abortGleasonTool(g4_shape_id) {
            vm.abortRuler();
            vm.clearRuler(g4_shape_id);
            vm.stopGleasonTool();
        }

        function gleasonToolActive() {
            return vm.gleasonModeActive;
        }

        function gleasonDataValid() {
            return (typeof (vm.tmpGleasonShape) !== 'undefined' && typeof (vm.tmpGleasonType) !== 'undefined');
        }

        function initializeRuler() {
            AnnotationsViewerService.createAreaRulerBindings('area_ruler_switch_on',
                'gleason_area_output');
        }

        function showRuler() {
            AnnotationsViewerService.drawShape(vm.tmpGleasonShape);
            $(".show_ruler").removeClass('prm-pale-icon');
            vm.ruler_hidden = false;
        }

        function hideRuler(shape_id) {
            var g_ruler_id = typeof (shape_id) === 'undefined' ? vm.tmpGleasonShape.shape_id : shape_id;
            AnnotationsViewerService.deleteShape(g_ruler_id);
            $(".show_ruler").addClass('prm-pale-icon');
            vm.ruler_hidden = true;
        }

        function showHideRuler() {
            if (vm.ruler_hidden === true) {
                vm.showRuler();
            } else {
                vm.hideRuler();
            }
        }

        function selectRuler(shape_id) {
            AnnotationsViewerService.selectShape(shape_id);
        }

        function deselectRuler(shape_id) {
            AnnotationsViewerService.deselectShape(shape_id);
        }

        function startRuler() {
            var $ruler_out = $("#gleason_area_output");
            AnnotationsViewerService.bindAreaRulerToShape(vm.focus_region_label);
            $ruler_out
                .on('area_ruler_paused',
                    function () {
                        AnnotationsViewerService.disableActiveTool();
                        vm.area_ruler_tool_paused = true;
                        $scope.$apply();
                    }
                )
                .on('area_ruler_updated',
                    function () {
                        vm.tmpGleasonShapeArea = $ruler_out.data('measure');
                        vm.tmpGleasonShape = $ruler_out.data('ruler_json');
                    }
                )
                .on('area_ruler_empty_intersection',
                    function () {
                        vm.ruler_tool_active = false;
                        $ruler_out.unbind('area_ruler_cleared')
                            .unbind('area_ruler_updated')
                            .unbind('area_ruler_empty_intersection')
                            .unbind('area_ruler_paused');
                        vm.tmpGleasonShape = undefined;
                        vm.tmpGleasonShapeArea = undefined;
                        vm.area_ruler_tool_paused = false;
                        AnnotationsViewerService.disableActiveTool();
                        $scope.$apply();
                        ngDialog.open({
                            template: '/static/templates/dialogs/invalid_gleason_4.html'
                        });
                    }
                )
                .on('area_ruler_cleared',
                    function (event, ruler_saved) {
                        $ruler_out.unbind('area_ruler_cleared')
                            .unbind('area_ruler_updated')
                            .unbind('area_ruler_empty_intersection')
                            .unbind('area_ruler_paused');
                        vm.ruler_tool_active = false;
                        vm.area_ruler_tool_paused = false;
                        AnnotationsViewerService.disableActiveTool();
                        if (ruler_saved) {
                            vm.showRuler();
                        }
                    }
                );
            vm.ruler_tool_active = true;
            vm.tmpGleasonActionStartTime = new Date();
        }

        function temporaryRulerExists() {
            return AnnotationsViewerService.tmpAreaRulerExists();
        }

        function temporaryRulerValid() {
            $log.debug('TEMPORARY GLEASON SHAPE VALID: ' + AnnotationsViewerService.tmpAreaRulerValid());
            return AnnotationsViewerService.tmpAreaRulerValid();
        }

        function confirmRuler() {
            AnnotationsViewerService.saveAreaRuler();
        }

        function pauseRuler() {
            $log.debug('Gleason ruler paused');
            AnnotationsViewerService.disableActiveTool();
            if (vm.temporaryRulerExists()) {
                AnnotationsViewerService.deactivateAreaRulerPreviewMode();
            }
            vm.area_ruler_tool_paused = true;
        }

        function unpauseRuler() {
            $log.debug('Gleason ruler unpaused');
            AnnotationsViewerService.startAreaRulerTool();
            if (vm.temporaryRulerExists()) {
                AnnotationsViewerService.activateAreaRulerPreviewMode();
            }
            vm.area_ruler_tool_paused = false;
        }

        function isRulerPaused() {
            return vm.area_ruler_tool_paused;
        }

        function rulerRollbackPossible() {
            return (AnnotationsViewerService.tmpAreaRulerExists() ||
                AnnotationsViewerService.areaRulerUndoHistoryExists());
        }

        function rulerRestorePossible() {
            return AnnotationsViewerService.areaRulerRedoHistoryExists();
        }

        function rollbackRuler() {
            AnnotationsViewerService.rollbackAreaRuler();
        }

        function restoreRuler() {
            AnnotationsViewerService.restoreAreaRuler();
        }

        function abortRuler() {
            AnnotationsViewerService.clearAreaRuler();
            var $ruler_out = $("#gleason_area_output");
            $ruler_out
                .unbind('area_ruler_updated')
                .unbind('area_ruler_empty_intersection')
                .unbind('area_ruler_cleared');
            vm.ruler_tool_active = false;
            vm.tmpGleasonActionStartTime = undefined;
            AnnotationsViewerService.disableActiveTool();
        }

        function clearRuler(ruler_shape_id) {
            if (vm.tmpGleasonShape) {
                vm.hideRuler(ruler_shape_id);
            }
            vm.tmpGleasonShape = undefined;
            vm.tmpGleasonShapeArea = undefined;
            vm.tmpGleasonType = undefined;
        }

        function rulerToolActive() {
            return vm.ruler_tool_active;
        }

        function rulerExists() {
            return (typeof vm.tmpGleasonShape !== 'undefined');
        }

        function _getGleasonElementIndexLabel() {
            var index = 1;
            var valid_label = false;
            while (!valid_label) {
                if (vm.gleasonElementsLabels.indexOf('GL_item_' + index) !== -1) {
                    index += 1;
                } else {
                    valid_label = true;
                }
            }
            return index;
        }

        function acceptTemporaryGleason() {
            var old_gleason_shape_id = vm.tmpGleasonShape.shape_id;
            var gleason_shape_id = 'GL_item_' + vm._getGleasonElementIndexLabel();
            vm.tmpGleasonShape.shape_id = gleason_shape_id;
            var tmp_g_object = {
                json_path: vm.tmpGleasonShape,
                area: vm.tmpGleasonShapeArea,
                cells_count: vm.tmpGleasonCellsCount,
                gleason_type: vm.tmpGleasonType,
                gleason_label: vm.gleason_types_map[vm.tmpGleasonType],
                action_start_time: vm.tmpGleasonActionStartTime,
                action_complete_time: new Date()
            };
            vm.gleasonElementsLabels.push(gleason_shape_id);
            vm.gleasonElements[gleason_shape_id] = tmp_g_object;
            vm.abortGleasonTool(old_gleason_shape_id);
            vm._showGleasonElement(gleason_shape_id, true);
        }

        function isReadOnly() {
            return false;
        }

        function isLocked() {
            return false;
        }

        function isCancerousRegion() {
            return vm.focusRegionTissueStatus === 'TUMOR';
        }

        function isStressedRegion() {
            return vm.focusRegionTissueStatus === 'STRESSED';
        }

        function formValid() {
            return !vm.gleasonToolActive();
        }

        function destroy() {
            vm._clean();
            $rootScope.$broadcast('annotation_panel.closed');
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
            // build the list with Gleason 4 elements
            var gleason_elements = Object.keys(vm.gleasonElements).map(
                function (key) {
                    return vm.gleasonElements[key];
                }
            );
            var obj_config = {
                perineural_involvement: vm.perineuralInvolvement,
                intraductal_carcinoma: vm.intraductalCarcinoma,
                ductal_carcinoma: vm.ductalCarcinoma,
                poorly_formed_glands: vm.poorlyFormedGlands,
                cribriform_pattern: vm.cribriformPattern,
                small_cell_signet_ring: vm.smallCellSignetRing,
                hypernephroid_pattern: vm.hypernephroidPattern,
                mucinous: vm.mucinous,
                comedo_necrosis: vm.comedoNecrosis,
                inflammation: vm.inflammation,
                pah: vm.pah,
                atrophic_lesions: vm.atrophicLesions,
                adenosis: vm.adenosis,
                cells_count: vm.cellsCount,
                gleason_elements: gleason_elements,
                action_start_time: vm.actionStartTime,
                action_complete_time: new Date()
            };
            FocusRegionAnnotationsManagerService.createAnnotation(vm.focus_region_id,
                vm.clinical_annotation_step_label, obj_config)
                .then(createAnnotationSuccessFn, createAnnotationErrorFn);

            function createAnnotationSuccessFn(response) {
                $rootScope.$broadcast('focus_region_annotation.saved',
                    vm.focus_region_label, vm.focus_region_id);
                vm._clean();
                dialog.close();
            }

            function createAnnotationErrorFn(response) {
                $log.error('Unable to save annotation');
                $log.error(response.data);
                dialog.close();
            }
        }

        function gleasonElementVisible(element_id) {
            return (vm.displayedGleasonElementsLabels.indexOf(element_id) !== -1);
        }

        function _hideGleasonElement(element_id, record_status) {
            AnnotationsViewerService.deleteShape(
                vm.gleasonElements[element_id].json_path.shape_id
            );
            if (record_status) {
                removeItemFromArray(element_id, vm.displayedGleasonElementsLabels);
            }
        }

        function _showGleasonElement(element_id, record_status) {

            AnnotationsViewerService.drawShape(
                vm.gleasonElements[element_id].json_path
            );
            if (record_status) {
                vm.displayedGleasonElementsLabels.push(element_id);
            }
        }

        function _showExistingGleasonElements() {
            for (var i = 0; i < vm.gleasonElementsLabels.length; i++) {
                vm._showGleasonElement(vm.gleasonElementsLabels[i], false);
            }
        }

        function _restoreGleasonElementsVisibility() {
            for (var i = 0; i < vm.gleasonElementsLabels.length; i++) {
                if (vm.displayedGleasonElementsLabels.indexOf(vm.gleasonElementsLabels[i]) === -1) {
                    vm._hideGleasonElement(vm.gleasonElementsLabels[i], false);
                }
            }
        }

        function showHideGleasonElement(element_id) {
            if (vm.displayedGleasonElementsLabels.indexOf(element_id) !== -1) {
                // hide element
                vm._hideGleasonElement(element_id, true);
            } else {
                // show element
                vm._showGleasonElement(element_id, true);
            }
        }

        function deleteGleasonElement(element_id) {
            if (vm.displayedGleasonElementsLabels.indexOf(element_id) !== -1) {
                // hide element
                vm._hideGleasonElement(element_id);
            }
            removeItemFromArray(element_id, vm.gleasonElementsLabels);
            delete (vm.gleasonElements[element_id]);
        }

        function updateRegionArea() {
            vm.scaledRegionArea = formatDecimalNumber(
                (vm.focusRegionArea * vm.regionAreaScaleFactor.id), 3
            );
        }

        function updateRegionLength() {
            vm.scaledRegionLength = formatDecimalNumber(
                (vm.focusRegionLength * vm.regionLengthScaleFactor.id), 3
            );
        }
    }

    ShowFocusRegionAnnotationController.$inject = ['$scope', '$routeParams', '$rootScope', '$log', 'ngDialog',
        'FocusRegionAnnotationsManagerService', 'FocusRegionsManagerService', 'AnnotationsViewerService'];

    function ShowFocusRegionAnnotationController($scope, $routeParams, $rootScope, $log, ngDialog,
        FocusRegionAnnotationsManagerService, FocusRegionsManagerService,
        AnnotationsViewerService) {
        var vm = this;
        vm.focus_region_id = undefined;
        vm.focus_region_label = undefined;
        vm.focusRegionArea = undefined;
        vm.coreCoveragePercentage = undefined;
        vm.focusRegionTissueStatus = undefined;
        vm.focusRegionLength = undefined;
        vm.perineuralInvolvement = false;
        vm.intraductalCarcinoma = false;
        vm.ductalCarcinoma = false;
        vm.poorlyFormedGlands = false;
        vm.cribriformPattern = false;
        vm.smallCellSignetRing = false;
        vm.hypernephroidPattern = false;
        vm.mucinous = false;
        vm.comedoNecrosis = false;
        vm.inflammation = false;
        vm.pah = false;
        vm.atrophicLesions = false;
        vm.adenosis = false;
        vm.cellularDensityHelperShape = undefined;
        vm.cellsCount = undefined;

        vm.scaledRegionLength = undefined;
        vm.regionLengthScaleFactor = undefined;
        vm.scaledRegionArea = undefined;
        vm.regionAreaScaleFactor = undefined;

        vm.lengthUOM = [
            { id: 1, unit_of_measure: 'μm' },
            { id: Math.pow(10, -3), unit_of_measure: 'mm' }
        ];

        vm.areaUOM = [
            { id: 1, unit_of_measure: 'μm²' },
            { id: Math.pow(10, -6), unit_of_measure: 'mm²' }
        ];

        vm.gleasonElements = undefined;
        vm.gleasonElementsLabels = undefined;
        vm.displayedGleasonElementsLabels = undefined;

        vm.clinical_annotation_step_label = undefined;

        vm.ruler_hidden = true;
        vm.locked = undefined;

        vm.isReadOnly = isReadOnly;
        vm.isCancerousRegion = isCancerousRegion;
        vm.isStressedRegion = isStressedRegion;
        vm.isLocked = isLocked;
        vm.destroy = destroy;
        vm.deleteAnnotation = deleteAnnotation;
        vm._hideGleasonElement = _hideGleasonElement;
        vm._showGleasonElement = _showGleasonElement;
        vm.showHideGleasonElement = showHideGleasonElement;
        vm.selectRuler = selectRuler;
        vm.deselectRuler = deselectRuler;
        vm.updateRegionLength = updateRegionLength;
        vm.updateRegionArea = updateRegionArea;

        activate();

        function activate() {
            vm.regionAreaScaleFactor = vm.areaUOM[0];
            vm.regionLengthScaleFactor = vm.lengthUOM[0];

            vm.clinical_annotation_step_label = $routeParams.label;
            $scope.$on('focus_region_annotation.show',
                function (event, focus_region_id) {
                    vm.locked = false;
                    vm.focus_region_id = focus_region_id;
                    FocusRegionAnnotationsManagerService.getAnnotation(vm.focus_region_id,
                        vm.clinical_annotation_step_label)
                        .then(getFocusRegionAnnotationSuccessFn, getFocusRegionAnnotationErrorFn);
                }
            );

            function getFocusRegionAnnotationSuccessFn(response) {
                vm.focus_region_label = response.data.focus_region.label;
                vm.focusRegionArea = response.data.focus_region.area;
                vm.updateRegionArea();
                vm.coreCoveragePercentage = Number(parseFloat(response.data.focus_region.core_coverage_percentage)
                    .toFixed(3));
                vm.focusRegionTissueStatus = response.data.focus_region.tissue_status;
                vm.focusRegionLength = response.data.focus_region.length;
                vm.updateRegionLength();
                vm.perineuralInvolvement = response.data.perineural_involvement;
                vm.intraductalCarcinoma = response.data.intraductal_carcinoma;
                vm.ductalCarcinoma = response.data.ductal_carcinoma;
                vm.poorlyFormedGlands = response.data.poorly_formed_glands;
                vm.cribriformPattern = response.data.cribriform_pattern;
                vm.smallCellSignetRing = response.data.small_cell_signet_ring;
                vm.hypernephroidPattern = response.data.hypernephroid_pattern;
                vm.mucinous = response.data.mucinous;
                vm.comedoNecrosis = response.data.comedo_necrosis;
                vm.inflammation = response.data.inflammation;
                vm.pah = response.data.pah;
                vm.atrophicLesions = response.data.atrophic_lesions;
                vm.adenosis = response.data.adenosis;
                vm.cellsCount = response.data.cells_count;

                vm.gleasonElements = {};
                vm.gleasonElementsLabels = [];
                vm.displayedGleasonElementsLabels = [];
                // load Gleason elements
                var gleason_elements = response.data.gleason_elements;
                for (var g_el in gleason_elements) {
                    var ge = gleason_elements[g_el];
                    ge.json_path = $.parseJSON(ge.json_path);
                    vm.gleasonElementsLabels.push(ge.json_path.shape_id);
                    vm.gleasonElements[ge.json_path.shape_id] = ge;
                }

                $(".show_ruler").addClass('prm-pale-icon');
                $(".show_cc_helper_addon").addClass('prm-pale-icon');
                $(".g_show_cc_helper_addon").addClass('prm-pale-icon');
            }

            function getFocusRegionAnnotationErrorFn(response) {
                if (response.status === 404) {
                    FocusRegionsManagerService.get(vm.focus_region_id)
                        .then(getFocusRegionSuccessFn, getFocusRegionErrorFn);
                } else {
                    $log.error('Unable to load focus region annotation data');
                    $log.error(response);
                }

                function getFocusRegionSuccessFn(response) {
                    vm.focus_region_label = response.data.label;
                    vm.focusRegionArea = response.data.area;
                    vm.updateRegionArea();
                    vm.coreCoveragePercentage = Number(parseFloat(response.data.core_coverage_percentage)
                        .toFixed(3));
                    vm.focusRegionTissueStatus = response.data.tissue_status;
                    vm.focusRegionLength = response.data.length;
                    vm.updateRegionLength();
                    vm.locked = true;
                }

                function getFocusRegionErrorFn(response) {
                    $log.error('Unable to load focus region data');
                    $log.error(response);
                }
            }
        }

        function isReadOnly() {
            return true;
        }

        function isCancerousRegion() {
            return vm.focusRegionTissueStatus === 'TUMOR';
        }

        function isStressedRegion() {
            return vm.focusRegionTissueStatus === 'STRESSED';
        }

        function isLocked() {
            return vm.locked;
        }

        function destroy() {
            $rootScope.$broadcast('annotation_panel.closed');
        }

        function deleteAnnotation() {
            ngDialog.openConfirm({
                template: '/static/templates/dialogs/delete_annotation_confirm.html',
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
                        showClose: true,
                        closeByEscape: false,
                        closeByNavigation: false,
                        closeByDocument: false
                    });
                    FocusRegionAnnotationsManagerService.deleteAnnotation(vm.focus_region_id,
                        vm.clinical_annotation_step_label)
                        .then(deleteFocusRegionAnnotationSuccessFn, deleteFocusRegionAnnotationErrorFn);
                }
            }

            function deleteFocusRegionAnnotationSuccessFn(response) {
                $rootScope.$broadcast('focus_region_annotation.deleted', vm.focus_region_label, vm.focus_region_id);

                // if (vm.ruler_hidden === false) {
                //     AnnotationsViewerService.deleteShape(vm.gleasonShape.shape_id);
                // }

                vm.focus_region_id = undefined;
                vm.focus_region_label = undefined;
                vm.focusRegionArea = undefined;
                vm.coreCoveragePercentage = undefined;
                vm.focusRegionTissueStatus = undefined;
                vm.focusRegionLength = undefined;
                vm.perineuralInvolvement = false;
                vm.intraductalCarcinoma = false;
                vm.ductalCarcinoma = false;
                vm.poorlyFormedGlands = false;
                vm.cribriformPattern = false;
                vm.smallCellSignetRing = false;
                vm.hypernephroidPattern = false;
                vm.mucinous = false;
                vm.comedoNecrosis = false;
                vm.inflammation = false;
                vm.pah = false;
                vm.atrophicLesions = false;
                vm.adenosis = false;
                vm.cellsCount = undefined;

                for (var el in vm.gleasonElementsLabels) {
                    vm._hideGleasonElement(vm.gleasonElementsLabels[el]);
                }

                // vm.ruler_hidden = true;

                dialog.close();
            }

            function deleteFocusRegionAnnotationErrorFn(response) {
                $log.error('unable to delete focus region annotation');
                $log.error('response');
                dialog.close();
            }
        }

        function _hideGleasonElement(element_id) {
            AnnotationsViewerService.deleteShape(
                vm.gleasonElements[element_id].json_path.shape_id
            );
            $("#" + element_id + "_ro").addClass('prm-pale-icon');
            removeItemFromArray(element_id, vm.displayedGleasonElementsLabels);
        }

        function _showGleasonElement(element_id) {
            AnnotationsViewerService.drawShape(
                vm.gleasonElements[element_id].json_path
            );
            $("#" + element_id + "_ro").removeClass('prm-pale-icon');
            vm.displayedGleasonElementsLabels.push(element_id);
        }

        function showHideGleasonElement(element_id) {
            if (vm.displayedGleasonElementsLabels.indexOf(element_id) !== -1) {
                // hide element
                vm._hideGleasonElement(element_id);
            } else {
                // show element
                vm._showGleasonElement(element_id);
            }
        }

        function selectRuler(shape_id) {
            AnnotationsViewerService.selectShape(shape_id);
        }

        function deselectRuler(shape_id) {
            AnnotationsViewerService.deselectShape(shape_id);
        }

        function updateRegionArea() {
            vm.scaledRegionArea = formatDecimalNumber(
                (vm.focusRegionArea * vm.regionAreaScaleFactor.id), 3
            );
        }

        function updateRegionLength() {
            vm.scaledRegionLength = formatDecimalNumber(
                (vm.focusRegionLength * vm.regionLengthScaleFactor.id), 3
            );
        }
    }

    NewGleasonPatternAnnotationController.$inject = ['$scope', '$rootScope', '$routeParams', '$log', 'ngDialog',
        'AnnotationsViewerService', 'CurrentSlideDetailsService', 'GleasonPatternAnnotationsManagerService'];

    function NewGleasonPatternAnnotationController($scope, $rootScope, $routeParams, $log, ngDialog, AnnotationsViewerService,
        CurrentSlideDetailsService, GleasonPatternAnnotationsManagerService) {
        var vm = this;
        vm.clinical_annotation_step_label = undefined;
        vm.slide_id = undefined;
        vm.case_id = undefined;
        vm.parentFocusRegion = undefined;
        vm.default_shape_label = undefined;
        vm.shape_label = undefined;
        vm.shape = undefined;
        vm.gleasonPatternArea = undefined;
        vm.pattern_type = undefined;
        vm.pattern_type_confirmed = undefined;

        vm.subregionCreationModeActive = undefined;
        vm.subregions_list = undefined;
        vm.tmp_subregion_label = undefined;
        vm.tmp_subregion = undefined;
        vm.tmp_subregion_type = undefined;

        vm.actionStartTime = undefined;

        vm.active_tool = undefined;
        vm.polygon_tool_paused = false;
        vm.freehand_tool_paused = false;
        vm.subregion_tool_paused = false;

        vm.POLYGON_TOOL = 'polygon_drawing_tool';
        vm.FREEHAND_TOOL = 'freehand_drawing_tool';
        vm.SUBREGION_TOOL = 'subregion_drawing_tool';

        vm.shape_config = {
            'stroke_color': '#FFB533',
            'stroke_width': 20
        };

        vm.isReadOnly = isReadOnly;
        vm.isEditMode = isEditMode;
        vm.isEditLabelModeActive = isEditLabelModeActive;
        vm.newPolygon = newPolygon;
        vm._startFreehandDrawingTool = _startFreehandDrawingTool;
        vm.newFreehand = newFreehand;
        vm.newSubregion = newSubregion;
        vm._updateGleasonPatternData = _updateGleasonPatternData;
        vm.isPolygonToolActive = isPolygonToolActive;
        vm.isPolygonToolPaused = isPolygonToolPaused;
        vm.isFreehandToolActive = isFreehandToolActive;
        vm.isFreehandToolPaused = isFreehandToolPaused;
        vm.isSubregionDrawingToolActive = isSubregionDrawingToolActive;
        vm.isSubregionDrawingToolPaused = isSubregionDrawingToolPaused;
        vm.temporaryPolygonExists = temporaryPolygonExists;
        vm.temporaryPolygonValid = temporaryPolygonValid;
        vm.temporaryShapeExists = temporaryShapeExists;
        vm.temporaryShapeValid = temporaryShapeValid;
        vm.drawInProgress = drawInProgress;
        vm.subregionCreationInProgress = subregionCreationInProgress;
        vm.activateSubregionCreationMode = activateSubregionCreationMode;
        vm.deactivateSubregionCreationMode = deactivateSubregionCreationMode;
        vm.shapeExists = shapeExists;
        vm.temporarySubregionExists = temporarySubregionExists;
        vm.subregionsExist = subregionsExist;
        vm.pausePolygonTool = pausePolygonTool;
        vm.unpausePolygonTool = unpausePolygonTool;
        vm.pauseFreehandTool = pauseFreehandTool;
        vm.unpauseFreehandTool = unpauseFreehandTool;
        vm.pauseSubregionDrawingTool = pauseSubregionDrawingTool;
        vm.unpauseSubregionDrawingTool = unpauseSubregionDrawingTool;
        vm.confirmPolygon = confirmPolygon;
        vm.confirmFreehandShape = confirmFreehandShape;
        vm.confirmTemporarySubregionShape = confirmTemporarySubregionShape;
        vm.polygonRollbackPossible = polygonRollbackPossible;
        vm.polygonRestorePossible = polygonRestorePossible;
        vm.rollbackPolygon = rollbackPolygon;
        vm.restorePolygon = restorePolygon;
        vm.shapeRollbackPossible = shapeRollbackPossible;
        vm.shapeRestorePossible = shapeRestorePossible;
        vm.rollbackFreehandShape = rollbackFreehandShape;
        vm.restoreFreehandShape = restoreFreehandShape;
        vm.clear = clear;
        vm.abortTool = abortTool;
        vm.deleteTemporaryGleasonPattern = deleteTemporaryGleasonPattern;
        vm.deleteShape = deleteShape;
        vm.deleteTemporarySubregion = deleteTemporarySubregion;
        vm.deleteSubregion = deleteSubregion;
        vm.deleteSubregions = deleteSubregions;
        vm.selectShape = selectShape;
        vm.deselectShape = deselectShape;
        vm.focusOnShape = focusOnShape;
        vm.updateGleasonPatternArea = updateGleasonPatternArea;
        vm.patternTypeSelected = patternTypeSelected;
        vm.subregionTypeSelected = subregionTypeSelected;
        vm.confirmPatternType = confirmPatternType;
        vm.acceptTemporarySubregion = acceptTemporarySubregion;
        vm.resetPatternType = resetPatternType;
        vm.resetTemporarySubregion = resetTemporarySubregion;
        vm.patternTypeConfirmed = patternTypeConfirmed;
        vm.checkPatternType = checkPatternType;
        vm.formValid = formValid;
        vm.isLocked = isLocked;
        vm.destroy = destroy;
        vm._prepareSubregionsData = _prepareSubregionsData;
        vm.save = save;

        activate();

        function activate() {
            vm.slide_id = CurrentSlideDetailsService.getSlideId();
            vm.case_id = CurrentSlideDetailsService.getCaseId();

            vm.clinical_annotation_step_label = $routeParams.label;

            vm.subregionCreationModeActive = false;
            vm.pattern_type_confirmed = false;
            vm.subregions_list = {};

            $scope.$on('gleason_pattern.creation_mode',
                function () {
                    vm.default_shape_label = AnnotationsViewerService.getFirstAvailableLabel('gleason_pattern');
                    console.log(vm.default_shape_label);
                    vm.shape_label = vm.default_shape_label;
                    vm.actionStartTime = new Date();
                }
            );
        }

        function isReadOnly() {
            return false;
        }

        function isEditMode() {
            return false;
        }

        function isEditLabelModeActive() {
            return false;
        }

        function newPolygon() {
            AnnotationsViewerService.extendPolygonConfig(vm.shape_config);
            AnnotationsViewerService.startPolygonsTool();
            vm.active_tool = vm.POLYGON_TOOL;
            var canvas_label = AnnotationsViewerService.getCanvasLabel();
            var $canvas = $("#" + canvas_label);
            $canvas.on('polygon_created',
                function () {
                    $canvas.unbind('polygon_created');
                    $scope.$apply();
                }
            )
                .on('polygon_add_point',
                    function () {
                        $scope.$apply();
                    }
                );
        }

        function newFreehand() {
            vm._startFreehandDrawingTool('gleason_pattern', 'freehand_gleason_tool');
        }

        function newSubregion() {
            vm.activateSubregionCreationMode();
            vm._startFreehandDrawingTool('gp_sub', 'subregion_tool');
        }

        function _startFreehandDrawingTool(label, tool_type) {
            AnnotationsViewerService.setFreehandToolLabelPrefix(label);
            AnnotationsViewerService.extendPathConfig(vm.shape_config);
            AnnotationsViewerService.startFreehandDrawingTool();
            var canvas_label = AnnotationsViewerService.getCanvasLabel();
            var $canvas = $("#" + canvas_label);
            $canvas.on('freehand_polygon_paused',
                function (event, polygon_label) {
                    AnnotationsViewerService.disableActiveTool();
                    switch (vm.active_tool) {
                        case vm.FREEHAND_TOOL:
                            vm.freehand_tool_paused = true;
                            break;
                        case vm.SUBREGION_TOOL:
                            console.log('Pausing subregion drawing tool');
                            vm.subregion_tool_paused = true;
                            break;
                    }
                    $scope.$apply();
                }
            );
            switch (tool_type) {
                case 'freehand_gleason_tool':
                    vm.active_tool = vm.FREEHAND_TOOL;
                    break;
                case 'subregion_tool':
                    vm.active_tool = vm.SUBREGION_TOOL;
                    break;
            }
        }

        function _updateGleasonPatternData(polygon_label, parent_focus_region) {
            vm.parentFocusRegion = parent_focus_region;
            vm.gleasonPatternArea = AnnotationsViewerService.getShapeArea(polygon_label);
            vm.updateGleasonPatternArea();
        }

        function isPolygonToolActive() {
            return vm.active_tool == vm.POLYGON_TOOL;
        }

        function isPolygonToolPaused() {
            return vm.polygon_tool_paused;
        }

        function isFreehandToolActive() {
            return vm.active_tool == vm.FREEHAND_TOOL;
        }

        function isFreehandToolPaused() {
            return vm.freehand_tool_paused;
        }

        function isSubregionDrawingToolActive() {
            return vm.active_tool == vm.SUBREGION_TOOL;
        }

        function isSubregionDrawingToolPaused() {
            return vm.subregion_tool_paused;
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
                vm.isFreehandToolPaused();
        }

        function subregionCreationInProgress() {
            return vm.subregionCreationModeActive;
        }

        function activateSubregionCreationMode() {
            vm.subregionCreationModeActive = true;
        }

        function deactivateSubregionCreationMode() {
            vm.subregionCreationModeActive = false;
        }

        function shapeExists() {
            return vm.shape !== undefined;
        }

        function temporarySubregionExists() {
            return vm.tmp_subregion !== undefined;
        }

        function subregionsExist() {
            return (Object.keys(vm.subregions_list).length > 0);
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

        function pauseSubregionDrawingTool() {
            AnnotationsViewerService.disableActiveTool();
            if (vm.temporaryShapeExists()) {
                AnnotationsViewerService.deactivatePreviewMode();
            }
            vm.subregion_tool_paused = true;
        }

        function unpauseSubregionDrawingTool() {
            AnnotationsViewerService.startFreehandDrawingTool();
            if (vm.temporaryShapeExists()) {
                AnnotationsViewerService.activatePreviewMode();
            }
            vm.subregion_tool_paused = false;
        }

        function confirmPolygon() {
            ngDialog.open({
                template: '/static/templates/dialogs/rois_check.html',
                showClose: false,
                closeByEscape: false,
                closeByNavigation: false,
                closeByDocument: false,
                name: 'checkGleasonPattern',
                onOpenCallback: function () {
                    var canvas_label = AnnotationsViewerService.getCanvasLabel();
                    var $canvas = $("#" + canvas_label);
                    $canvas.on('polygon_saved',
                        function (event, polygon_label) {
                            var focus_regions = $rootScope.focus_regions;
                            for (var fr in focus_regions) {
                                if (AnnotationsViewerService.checkContainment(focus_regions[fr].label, polygon_label) ||
                                    AnnotationsViewerService.checkContainment(polygon_label, focus_regions[fr].label)) {
                                    AnnotationsViewerService.adaptToContainer(focus_regions[fr].label, polygon_label);
                                    if (vm.shape_label !== polygon_label) {
                                        AnnotationsViewerService.changeShapeId(polygon_label, vm.shape_label);
                                        vm.shape = AnnotationsViewerService.getShapeJSON(vm.shape_label);
                                    } else {
                                        vm.shape = AnnotationsViewerService.getShapeJSON(polygon_label);
                                    }
                                    vm._updateGleasonPatternData(vm.shape.shape_id, focus_regions[fr]);
                                    break;
                                }
                            }
                            ngDialog.close('checkGleasonPattern');
                            if (typeof vm.shape === 'undefined') {
                                AnnotationsViewerService.deleteShape(polygon_label);
                                ngDialog.open({
                                    'template': '/static/templates/dialogs/invalid_gleason_pattern.html'
                                });
                            }
                            vm.abortTool();
                            $scope.$apply();
                        }
                    );
                    setTimeout(function () {
                        AnnotationsViewerService.saveTemporaryPolygon('gleason_pattern');
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
                name: 'checkGleasonPattern',
                onOpenCallback: function () {
                    var canvas_label = AnnotationsViewerService.getCanvasLabel();
                    var $canvas = $("#" + canvas_label);
                    $canvas.on('freehand_polygon_saved',
                        function (event, polygon_label) {
                            if (vm.active_tool = vm.FREEHAND_TOOL) {
                                var focus_regions = $rootScope.focus_regions;
                                for (var fr in focus_regions) {
                                    if (AnnotationsViewerService.checkContainment(focus_regions[fr].label, polygon_label) ||
                                        AnnotationsViewerService.checkContainment(polygon_label, focus_regions[fr].label)) {
                                        AnnotationsViewerService.adaptToContainer(focus_regions[fr].label, polygon_label);
                                        if (vm.shape_label !== polygon_label) {
                                            AnnotationsViewerService.changeShapeId(polygon_label, vm.shape_label);
                                            vm.shape = AnnotationsViewerService.getShapeJSON(vm.shape_label);
                                        } else {
                                            vm.shape = AnnotationsViewerService.getShapeJSON(polygon_label);
                                        }
                                        vm._updateGleasonPatternData(vm.shape.shape_id, focus_regions[fr]);
                                        break;
                                    }
                                }
                                ngDialog.close('checkGleasonPattern');
                                if (typeof vm.shape === 'undefined') {
                                    AnnotationsViewerService.delete_shape(polygon_label);
                                    ngDialog.open({
                                        'template': '/static/templates/dialogs/invalid_gleason_pattern.html'
                                    });
                                }
                                vm.abortTool();
                                $scope.$apply();
                            }
                        }
                    );
                    setTimeout(function () {
                        AnnotationsViewerService.saveTemporaryFreehandShape();
                    }, 10)
                }
            });
        }

        function confirmTemporarySubregionShape() {
            ngDialog.open({
                template: '/static/templates/dialogs/rois_check.html',
                showClose: false,
                closeByEscape: false,
                closeByNavigation: false,
                closeByDocument: false,
                name: 'checkTemporarySubregion',
                onOpenCallback: function () {
                    var canvas_label = AnnotationsViewerService.getCanvasLabel();
                    var $canvas = $("#" + canvas_label);
                    $canvas.on("freehand_polygon_saved",
                        function (event, polygon_label) {
                            if (vm.active_tool == vm.SUBREGION_TOOL) {
                                console.log('freehand shape saved');
                                if (AnnotationsViewerService.checkContainment(vm.shape_label, polygon_label) ||
                                    AnnotationsViewerService.checkContainment(polygon_label, vm.shape_label)) {
                                    AnnotationsViewerService.adaptToContainer(vm.shape_label, polygon_label);
                                    vm.tmp_subregion_label = polygon_label;
                                    vm.tmp_subregion = AnnotationsViewerService.getShapeJSON(polygon_label);
                                }
                                ngDialog.close('checkTemporarySubregion');
                                vm.abortTool(true);
                                $scope.$apply();
                            }
                        }
                    );
                    setTimeout(function () {
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

        function rollbackPolygon() {
            AnnotationsViewerService.rollbackPolygon();
        }

        function restorePolygon() {
            AnnotationsViewerService.restorePolygon();
        }

        function shapeRollbackPossible() {
            return (AnnotationsViewerService.tmpFreehandPathExists() ||
                AnnotationsViewerService.shapeUndoHistoryExists());
        }

        function shapeRestorePossible() {
            return AnnotationsViewerService.shapeRestoreHistoryExists();
        }

        function rollbackFreehandShape() {
            AnnotationsViewerService.rollbackTemporaryFreehandShape();
        }

        function restoreFreehandShape() {
            AnnotationsViewerService.restoreTemporaryFreehandShape();
        }

        function clear(destroy_shape) {
            vm.deleteShape(destroy_shape);
            if (vm.subregionCreationInProgress()) {
                vm.deleteTemporarySubregion();
            }
            vm.deleteSubregions();
            vm.shape_label = undefined;
            vm.default_shape_label = undefined;
            vm.actionStartTime = undefined;
        }

        function abortTool(keep_subregion_tool_active = false) {
            if (vm.active_tool === vm.POLYGON_TOOL) {
                AnnotationsViewerService.clearTemporaryPolygon();
                $("#" + AnnotationsViewerService.getCanvasLabel()).unbind('polygon_saved');
            }
            if (vm.active_tool === vm.FREEHAND_TOOL || vm.active_tool === vm.SUBREGION_TOOL) {
                AnnotationsViewerService.clearTemporaryFreehandShape();
                $("#" + AnnotationsViewerService.getCanvasLabel())
                    .unbind('freehand_polygon_saved')
                    .unbind('freehand_polygon_paused');
                if (vm.active_tool === vm.SUBREGION_TOOL && !keep_subregion_tool_active) {
                    vm.deactivateSubregionCreationMode();
                }
            }
            AnnotationsViewerService.disableActiveTool();
            vm.active_tool = undefined;
            vm.polygon_tool_paused = false;
            vm.freehand_tool_paused = false;
            vm.subregion_tool_paused = false;
        }

        function deleteTemporaryGleasonPattern(destroy_shape) {
            if (Object.keys(vm.subregions_list).length > 0) {
                vm.deleteSubregions();
            }
            vm.deleteShape(destroy_shape);
        }

        function deleteShape(destroy_shape) {
            if (typeof vm.shape !== 'undefined') {
                if (destroy_shape === true) {
                    AnnotationsViewerService.deleteShape(vm.shape.shape_id);
                }
                vm.shape = undefined;
                vm.gleasonPatternArea = undefined;
                vm.parentFocusRegion = undefined;
                vm.pattern_type = undefined;
                vm.pattern_type_confirmed = false;
            }
        }

        function deleteTemporarySubregion() {
            AnnotationsViewerService.deleteShape(vm.tmp_subregion_label);
            vm.resetTemporarySubregion();
        }

        function deleteSubregion(shape_label) {
            if (vm.subregions_list.hasOwnProperty(shape_label)) {
                AnnotationsViewerService.deleteShape(shape_label);
                delete (vm.subregions_list[shape_label]);
            } else {
                $log.error(shape_label + ' is not a valid subregion label');
            }
        }

        function deleteSubregions() {
            for (var label in vm.subregions_list) {
                vm.deleteSubregion(label);
            }
        }

        function selectShape(shape_id) {
            AnnotationsViewerService.selectShape(shape_id);
        }

        function deselectShape(shape_id) {
            AnnotationsViewerService.deselectShape(shape_id);
        }

        function focusOnShape(shape_id) {
            AnnotationsViewerService.focusOnShape(shape_id);
        }

        function updateGleasonPatternArea() {

        }

        function patternTypeSelected() {
            return typeof (vm.pattern_type) != 'undefined';
        }

        function subregionTypeSelected() {
            return typeof (vm.tmp_subregion_type) != 'undefined';
        }

        function confirmPatternType() {
            vm.pattern_type_confirmed = true;
        }

        function acceptTemporarySubregion() {
            vm.subregions_list[vm.tmp_subregion_label] = {
                "label": vm.tmp_subregion_label,
                "roi_json": AnnotationsViewerService.getShapeJSON(vm.tmp_subregion_label),
                "area": AnnotationsViewerService.getShapeArea(vm.tmp_subregion_label),
                "details_json": { "type": vm.tmp_subregion_type }
            };
            vm.abortTool();
            vm.resetTemporarySubregion();
        }

        function checkPatternType(pattern_type) {
            return vm.pattern_type === pattern_type;
        }

        function resetPatternType() {
            vm.pattern_type = undefined;
            vm.pattern_type_confirmed = false;
        }

        function resetTemporarySubregion() {
            vm.tmp_subregion_label = undefined;
            vm.tmp_subregion_type = undefined;
            vm.tmp_subregion = undefined;
            vm.deactivateSubregionCreationMode();
        }

        function patternTypeConfirmed() {
            return vm.pattern_type_confirmed;
        }

        function formValid() {
            return vm.patternTypeConfirmed() && !vm.subregionCreationInProgress();
        }

        function isLocked() {

        }

        function destroy() {
            vm.clear(true);
            vm.abortTool();
            $rootScope.$broadcast('tool.destroyed');
        }

        function _prepareSubregionsData() {
            var subregions_data = []
            for (var x in vm.subregions_list) {
                subregions_data.push({
                    "label": vm.subregions_list[x]["label"],
                    "roi_json": JSON.stringify(vm.subregions_list[x]["roi_json"]),
                    "area": vm.subregions_list[x]["area"],
                    "details_json": JSON.stringify(vm.subregions_list[x]["details_json"])
                });
            }
            return subregions_data;
        }

        function save() {
            var dialog = ngDialog.open({
                template: '/static/templates/dialogs/saving_data.html',
                showClose: false,
                closeByEscape: false,
                closeByNavigation: false,
                closeByDocument: false
            });

            var gleason_pattern_config = {
                "label": vm.shape_label,
                "gleason_type": vm.pattern_type,
                "roi_json": JSON.stringify(vm.shape),
                "area": vm.gleasonPatternArea,
                "subregions": vm._prepareSubregionsData(),
                "action_start_time": vm.actionStartTime,
                "action_complete_time": new Date()
            }
            GleasonPatternAnnotationsManagerService.createAnnotation(
                vm.parentFocusRegion.id,
                vm.clinical_annotation_step_label,
                gleason_pattern_config
            ).then(createGleasonPatternSuccessFn, createGleasonPatternErrorFn);

            function createGleasonPatternSuccessFn(response) {
                var gleason_pattern_info = {
                    'id': response.data.id,
                    'label': response.data.label,
                    'focus_region': response.data.focus_region,
                    'annotated': true
                };
                vm.clear(false);
                $rootScope.$broadcast('gleason_pattern.new', gleason_pattern_info);
                dialog.close();
            }

            function createGleasonPatternErrorFn(response) {
                $log.error('Unable to save gleason pattern');
                $log.error(response.data);
                dialog.close();
            }
        }
    }

    ShowGleasonPatternAnnotationController.$inject = [];

    function ShowGleasonPatternAnnotationController() {

    }
})();