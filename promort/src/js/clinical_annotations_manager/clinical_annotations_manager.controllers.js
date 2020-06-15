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
        .controller('ShowFocusRegionAnnotationController', ShowFocusRegionAnnotationController);

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
        vm.clinial_annotation_label = undefined;
        vm.clinical_annotation_step_label = undefined;

        vm.slices_map = undefined;
        vm.cores_map = undefined;
        vm.focus_regions_map = undefined;


        vm.ui_active_modes = {
            'annotate_slice': false,
            'annotate_core': false,
            'annotate_focus_region': false,
            'show_slice': false,
            'show_core': false,
            'show_focus_region': false
        };
        vm.roisTreeLocked = false;

        vm._registreSlice = _registerSlice;
        vm._registerCore = _registerCore;
        vm._registerFocusRegion = _registerFocusRegion;
        vm._getSliceLabel = _getSliceLabel;
        vm._getCoreLabel = _getCoreLabel;
        vm._getFocusRegionLabel = _getFocusRegionLabel;
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
        vm.activateNewCoreAnnoationMode = activateNewCoreAnnotationMode;
        vm.newCoreAnnotationModeActive = newCoreAnnotationModeActive;
        vm.activateShowCoreAnnotationMode = activateShowCoreAnnotationMode;
        vm.showCoreAnnotationModeActive = showCoreAnnotationModeActive;
        vm.activateNewFocusRegionAnnotationMode = activateNewFocusRegionAnnotationMode;
        vm.newFocusRegionAnnotationModeActive = newFocusRegionAnnotationModeActive;
        vm.activateShowFocusRegionAnnotationMode = activateShowFocusRegionAnnotationMode;
        vm.showFocusRegionAnnotationModeActive = showFocusRegionAnnotationModeActive;

        activate();

        function activate() {
            vm.slide_id = CurrentSlideDetailsService.getSlideId();
            vm.case_id = CurrentSlideDetailsService.getCaseId();
            vm.clinical_annotation_step_label = $routeParams.label;
            vm.clinical_annotation_label = vm.clinical_annotation_step_label.split('-')[0];
            $log.debug('clinical annotation label is ' + vm.clinical_annotation_label);
            vm.slide_index = vm.clinical_annotation_step_label.split('-')[1];

            vm.slices_map = [];
            vm.cores_map = [];
            vm.focus_regions_map = [];

            vm.slices_edit_mode = [];
            vm.cores_edit_mode = [];
            vm.focus_regions_edit_mode = [];

            $rootScope.slices = [];
            $rootScope.cores = [];
            $rootScope.focus_regions = [];

            ClinicalAnnotationStepService.getDetails(vm.clinical_annotation_step_label)
                .then(getClinicalAnnotationStepSuccessFn, getClinicalAnnotationStepErrorFn);

            function getClinicalAnnotationStepSuccessFn(response) {
                if (response.data.completed === true || response.data.can_be_started === false) {
                    $location.url('worklist/clinical_annotations/' + vm.clinical_annotation_label);
                }

                $scope.$on('annotation_panel.closed',
                    function() {
                        vm.allModesOff();
                    }
                );

                $scope.$on('slice.new',
                    function(event, slice_info) {
                        vm._registreSlice(slice_info);
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
                    function(event, core_info) {
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
                    function(event, focus_region_info) {
                        vm._registerFocusRegion(focus_region_info);
                        vm.allModesOff();
                        var $tree = $("#" + vm._getCoreLabel(focus_region_info.core) + "_tree");
                        var $new_focus_region_item = $(vm._createListItem(focus_region_info.label,
                            vm.focus_regions_edit_mode[focus_region_info.id], false));
                        var $anchor = $new_focus_region_item.find('a');
                        $anchor.attr('ng-click', 'cmc.showROIPanel("focus_region", ' + focus_region_info.id + ')')
                            .attr('ng-mouseenter', 'cmc.selectROI("focus_region", ' + focus_region_info.id + ')')
                            .attr('ng-mouseleave', 'cmc.deselectROI("focus_region", ' + focus_region_info.id + ')');
                        $compile($anchor)($scope);
                        $tree.append($new_focus_region_item);
                    }
                );

                $scope.$on('slice_annotation.saved',
                    function(event, slice_label, slice_id) {
                        var $icon = $("#" + slice_label).find('i');
                        $icon.removeClass("icon-black_question");
                        $icon.addClass("icon-check_circle");
                        vm.allModesOff();
                        vm.slices_edit_mode[slice_id] = false;
                    }
                );

                $scope.$on('slice_annotation.deleted',
                    function(event, slice_label, slice_id) {
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
                    function(event, core_label, core_id) {
                        var $icon = $("#" + core_label).find('i');
                        $icon.removeClass("icon-black_question");
                        $icon.addClass("icon-check_circle");
                        vm.allModesOff();
                        vm.cores_edit_mode[core_id] = false;
                    }
                );

                $scope.$on('core_annotation.deleted',
                    function(event, core_label, core_id) {
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
                    function(event, focus_region_label, focus_region_id) {
                        var $icon = $("#" + focus_region_label).find('i');
                        $icon.removeClass("icon-black_question");
                        $icon.addClass("icon-check_circle");
                        vm.allModesOff();
                        vm.focus_regions_edit_mode[focus_region_id] = false;
                    }
                );

                $scope.$on('focus_region_annotation.deleted',
                    function(event, focus_region_label, focus_region_id) {
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
            var html = '<ul id="' + roi_label +'_tree" class="list-group"></ul>';
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
                                vm.activateNewCoreAnnoationMode(roi_id);
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
                function(event, slice_id) {
                    vm.slice_id = slice_id;
                    SlicesManagerService.get(vm.slice_id)
                        .then(getSliceSuccessFn, getSliceErrorFn);
                }
            );

            function getSliceSuccessFn(response) {
                vm.slice_label = response.data.label;
                vm.totalCores = response.data.total_cores;
                vm.positiveCores = response.data.positive_cores_count;
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
                stromal_inflammation: vm.stromalInflammation
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

        vm.clinical_annotation_step_label = undefined;

        vm.isReadOnly = isReadOnly;
        vm.isLocked = isLocked;
        vm.destroy = destroy;
        vm.deleteAnnotation = deleteAnnotation;

        activate();

        function activate() {
            vm.clinical_annotation_step_label = $routeParams.label;
            $scope.$on('slice_annotation.show',
                function(event, slice_id) {
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
        'CoresManagerService', 'CoreAnnotationsManagerService'];

    function NewCoreAnnotationController($scope, $routeParams, $rootScope, $log, ngDialog,
                                         CoresManagerService, CoreAnnotationsManagerService) {
        var vm = this;
        vm.core_id = undefined;
        vm.core_label = undefined;
        vm.coreArea = undefined;
        vm.coreLength = undefined;
        vm.tumorLength = undefined;
        vm.primaryGleason = undefined;
        vm.secondaryGleason = undefined;
        vm.gradeGroupWho = undefined;
        vm.gradeGroupWhoLabel = '';

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
            { id: 1, unit_of_measure: 'μm²'},
            { id: Math.pow(10, -6), unit_of_measure: 'mm²'}
        ];

        vm._clean = _clean;
        vm.isReadOnly = isReadOnly;
        vm.isLocked = isLocked;
        vm.formValid = formValid;
        vm.destroy = destroy;
        vm.upgradeGradeGroupWho = updateGradeGroupWho;
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
                function(event, core_id) {
                    vm.core_id = core_id;
                    CoresManagerService.get(vm.core_id)
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
            vm.primaryGleason = undefined;
            vm.secondaryGleason = undefined;
            vm.gradeGroupWho = undefined;
            vm.gradeGroupWhoLabel = '';
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

        function updateGradeGroupWho() {
            if ((typeof vm.primaryGleason !== 'undefined') && (typeof vm.secondaryGleason !== 'undefined')) {
                var gleason_score = Number(vm.primaryGleason) + Number(vm.secondaryGleason);
                if (gleason_score <= 6) {
                    vm.gradeGroupWho = 'GG1';
                    vm.gradeGroupWhoLabel = 'Group 1'
                } else  if (gleason_score == 7) {
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
                gleason_group: vm.gradeGroupWho
            };
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
            { id: 1, unit_of_measure: 'μm²'},
            { id: Math.pow(10, -6), unit_of_measure: 'mm²'}
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
            }

            function getCoreAnnotationErrorFn(response) {
                if (response.status === 404) {
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

        vm.gleason_element_types = undefined;
        vm.gleason_types_map = undefined;

        vm.gleason4ModeActive = false;

        vm.tmpG4Shape = undefined;
        vm.tmpG4ShapeArea = undefined;
        vm.tmpG4CellularDensityHelperShape = undefined;
        vm.tmpG4CellularDensity = undefined;
        vm.tmpGType = undefined;
        vm.tmpG4CellsCount = undefined;

        vm.gleason4Elements = undefined;
        vm.gleason4ElementsLabels = undefined;
        vm.displayedGleason4ElementsLabels = undefined;

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
        vm.startGleason4Tool = startGleason4Tool;
        vm.stopGleason4Tool = stopGleason4Tool;
        vm.abortGleason4Tool = abortGleason4Tool;
        vm.gleason4ToolActive = gleason4ToolActive;
        vm.gleason4DataValid = gleason4DataValid;
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
        vm._getG4ElementIndexLabel = _getG4ElementIndexLabel;
        vm.acceptTemporaryGleason4 = acceptTemporaryGleason4;
        vm._hideGleason4Element = _hideGleason4Element;
        vm._showGleason4Element = _showGleason4Element;
        vm._showExistingGleason4Elements = _showExistingGleason4Elements;
        vm._restoreGleasonElementsVisibility = _restoreGleasonElementsVisibility;
        vm.gleasonElementVisible = gleasonElementVisible;
        vm.showHideGleason4Element = showHideGleason4Element;
        vm.deleteGleason4Element = deleteGleason4Element;
        vm.updateRegionLength = updateRegionLength;
        vm.updateRegionArea = updateRegionArea;

        activate();

        function activate() {
            vm.regionAreaScaleFactor = vm.areaUOM[0];
            vm.regionLengthScaleFactor = vm.lengthUOM[0];

            vm.clinical_annotation_step_label = $routeParams.label;

            vm.gleason4Elements = {};
            vm.gleason4ElementsLabels = [];
            vm.displayedGleason4ElementsLabels = [];

            $scope.$on('focus_region_annotation.new',
                function(event, focus_region_id) {
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

                ClinicalAnnotationStepManagerService.fetchGleasonElementTypes()
                    .then(fetchGleasonElementTypesSuccessFn);
                // initialize Gleason element labels
                function fetchGleasonElementTypesSuccessFn(response) {
                    vm.gleason_element_types = response.data;
                    vm.gleason_types_map = {};
                    for (var i=0; i<vm.gleason_element_types.length; i++) {
                        vm.gleason_types_map[vm.gleason_element_types[i].value] = vm.gleason_element_types[i].text;
                    }
                }
            }

            function getFocusRegionErrorFn(response) {
                $log.error('Unable to load focus region data');
                $log.error(response);
            }

            $scope.$on('viewerctrl.components.registered',
                function() {
                    vm.initializeRuler();
                }
            );
        }

        function _clean() {
            vm.clearRuler();

            for (var el in vm.gleason4ElementsLabels) {
                vm._hideGleason4Element(vm.gleason4ElementsLabels[el]);
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

            vm.gleason4Elements = {};
            vm.gleason4ElementsLabels = [];
            vm.displayedGleason4ElementsLabels = [];

            AnnotationsViewerService.disableActiveTool();
            vm.ruler_tool_active = false;
            vm.ruler_hidden = true;
            vm.stopGleason4Tool();
        }

        function startGleason4Tool() {
            vm.gleason4ModeActive = true;
            vm._showExistingGleason4Elements();
        }

        function stopGleason4Tool() {
            vm.gleason4ModeActive = false;
            vm.tmpG4CellsCount = undefined;
            vm._restoreGleasonElementsVisibility();
        }

        function abortGleason4Tool(g4_shape_id) {
            vm.abortRuler();
            vm.clearRuler(g4_shape_id);
            vm.stopGleason4Tool();
        }

        function gleason4ToolActive() {
            return vm.gleason4ModeActive;
        }

        function gleason4DataValid() {
            return (typeof(vm.tmpG4Shape) !== 'undefined' && typeof(vm.tmpGType) !== 'undefined');
        }

        function initializeRuler() {
            AnnotationsViewerService.createAreaRulerBindings('area_ruler_switch_on',
                'gleason_4_area_output');
        }

        function showRuler() {
            AnnotationsViewerService.drawShape(vm.tmpG4Shape);
            $(".show_ruler").removeClass('prm-pale-icon');
            vm.ruler_hidden = false;
        }

        function hideRuler(shape_id) {
            var g4_ruler_id = typeof (shape_id) === 'undefined' ? vm.tmpG4Shape.shape_id : shape_id;
            AnnotationsViewerService.deleteShape(g4_ruler_id);
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
            var $ruler_out = $("#gleason_4_area_output");
            AnnotationsViewerService.bindAreaRulerToShape(vm.focus_region_label);
            $ruler_out
                .on('area_ruler_paused',
                    function() {
                        AnnotationsViewerService.disableActiveTool();
                        vm.area_ruler_tool_paused = true;
                        $scope.$apply();
                    }
                )
                .on('area_ruler_updated',
                    function() {
                        vm.tmpG4ShapeArea = $ruler_out.data('measure');
                        vm.tmpG4Shape = $ruler_out.data('ruler_json');
                    }
                )
                .on('area_ruler_empty_intersection',
                    function() {
                        vm.ruler_tool_active = false;
                        $ruler_out.unbind('area_ruler_cleared')
                            .unbind('area_ruler_updated')
                            .unbind('area_ruler_empty_intersection')
                            .unbind('area_ruler_paused');
                        vm.tmpG4Shape = undefined;
                        vm.tmpG4ShapeArea = undefined;
                        vm.area_ruler_tool_paused = false;
                        AnnotationsViewerService.disableActiveTool();
                        $scope.$apply();
                        ngDialog.open({
                            template: '/static/templates/dialogs/invalid_gleason_4.html'
                        });
                    }
                )
                .on('area_ruler_cleared',
                    function(event, ruler_saved) {
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
        }

        function temporaryRulerExists() {
            return AnnotationsViewerService.tmpAreaRulerExists();
        }

        function temporaryRulerValid() {
            $log.debug('TEMPORARY G4 SHAPE VALID: ' + AnnotationsViewerService.tmpAreaRulerValid());
            return AnnotationsViewerService.tmpAreaRulerValid();
        }

        function confirmRuler() {
            AnnotationsViewerService.saveAreaRuler();
        }

        function pauseRuler() {
            $log.debug('G4 ruler paused');
            AnnotationsViewerService.disableActiveTool();
            if (vm.temporaryRulerExists()) {
                AnnotationsViewerService.deactivateAreaRulerPreviewMode();
            }
            vm.area_ruler_tool_paused = true;
        }

        function unpauseRuler() {
            $log.debug('G4 ruler unpaused');
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
            var $ruler_out = $("#gleason_4_area_output");
            $ruler_out
                .unbind('area_ruler_updated')
                .unbind('area_ruler_empty_intersection')
                .unbind('area_ruler_cleared');
            vm.ruler_tool_active = false;
            AnnotationsViewerService.disableActiveTool();
        }

        function clearRuler(ruler_shape_id) {
            if (vm.tmpG4Shape) {
                vm.hideRuler(ruler_shape_id);
            }
            vm.tmpG4Shape = undefined;
            vm.tmpG4ShapeArea = undefined;
            vm.tmpGType = undefined;
        }

        function rulerToolActive() {
            return vm.ruler_tool_active;
        }

        function rulerExists() {
            return (typeof vm.tmpG4Shape !== 'undefined');
        }

        function _getG4ElementIndexLabel() {
            var index = 1;
            var valid_label = false;
            while (!valid_label) {
                if (vm.gleason4ElementsLabels.indexOf('GL_item_' + index) !== -1) {
                    index += 1;
                } else {
                    valid_label = true;
                }
            }
            return index;
        }

        function acceptTemporaryGleason4() {
            var old_gleason_4_shape_id = vm.tmpG4Shape.shape_id;
            var gleason_4_shape_id = 'GL_item_' + vm._getG4ElementIndexLabel();
            vm.tmpG4Shape.shape_id = gleason_4_shape_id;
            var tmp_g4_object = {
                json_path: vm.tmpG4Shape,
                area: vm.tmpG4ShapeArea,
                cells_count: vm.tmpG4CellsCount,
                gleason_type: vm.tmpGType,
                gleason_label: vm.gleason_types_map[vm.tmpGType],
                creation_date: new Date()
            };
            vm.gleason4ElementsLabels.push(gleason_4_shape_id);
            vm.gleason4Elements[gleason_4_shape_id] = tmp_g4_object;
            vm.abortGleason4Tool(old_gleason_4_shape_id);
            vm._showGleason4Element(gleason_4_shape_id, true);
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
            return !vm.gleason4ToolActive();
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
            var gleason_4_elements = Object.keys(vm.gleason4Elements).map(
                function(key) {
                    return vm.gleason4Elements[key];
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
                gleason_elements: gleason_4_elements
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
            return (vm.displayedGleason4ElementsLabels.indexOf(element_id) !== -1);
        }

        function _hideGleason4Element(element_id, record_status) {
            AnnotationsViewerService.deleteShape(
                vm.gleason4Elements[element_id].json_path.shape_id
            );
            if (record_status) {
                removeItemFromArray(element_id, vm.displayedGleason4ElementsLabels);
            }
        }

        function _showGleason4Element(element_id, record_status) {

            AnnotationsViewerService.drawShape(
                vm.gleason4Elements[element_id].json_path
            );
            if (record_status) {
                vm.displayedGleason4ElementsLabels.push(element_id);
            }
        }

        function _showExistingGleason4Elements() {
            for (var i=0; i<vm.gleason4ElementsLabels.length; i++) {
                vm._showGleason4Element(vm.gleason4ElementsLabels[i], false);
            }
        }

        function _restoreGleasonElementsVisibility() {
            for (var i=0; i<vm.gleason4ElementsLabels.length; i++) {
                if (vm.displayedGleason4ElementsLabels.indexOf(vm.gleason4ElementsLabels[i]) === -1) {
                    vm._hideGleason4Element(vm.gleason4ElementsLabels[i], false);
                }
            }
        }

        function showHideGleason4Element(element_id) {
            if (vm.displayedGleason4ElementsLabels.indexOf(element_id) !== -1) {
                // hide element
                vm._hideGleason4Element(element_id, true);
            } else {
                // show element
                vm._showGleason4Element(element_id, true);
            }
        }

        function deleteGleason4Element(element_id) {
            if (vm.displayedGleason4ElementsLabels.indexOf(element_id) !== -1) {
                // hide element
                vm._hideGleason4Element(element_id);
            }
            removeItemFromArray(element_id, vm.gleason4ElementsLabels);
            delete(vm.gleason4Elements[element_id]);
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
            { id: 1, unit_of_measure: 'μm²'},
            { id: Math.pow(10, -6), unit_of_measure: 'mm²'}
        ];

        vm.gleason4Elements = undefined;
        vm.gleason4ElementsLabels = undefined;
        vm.displayedGleason4ElementsLabels = undefined;

        vm.clinical_annotation_step_label = undefined;

        vm.ruler_hidden = true;
        vm.locked = undefined;

        vm.isReadOnly = isReadOnly;
        vm.isCancerousRegion = isCancerousRegion;
        vm.isStressedRegion = isStressedRegion;
        vm.isLocked = isLocked;
        vm.destroy = destroy;
        vm.deleteAnnotation = deleteAnnotation;
        vm._hideGleason4Element = _hideGleason4Element;
        vm._showGleason4Element = _showGleason4Element;
        vm.showHideGleason4Element = showHideGleason4Element;
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
                vm.focusRegionArea  = response.data.focus_region.area;
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

                vm.gleason4Elements = {};
                vm.gleason4ElementsLabels = [];
                vm.displayedGleason4ElementsLabels = [];
                // load Gleason 4 elements
                var gleason_4_elements = response.data.gleason_elements;
                for (var g4_el in gleason_4_elements) {
                    var g4e = gleason_4_elements[g4_el];
                    g4e.json_path = $.parseJSON(g4e.json_path);
                    vm.gleason4ElementsLabels.push(g4e.json_path.shape_id);
                    vm.gleason4Elements[g4e.json_path.shape_id] = g4e;
                }

                $(".show_ruler").addClass('prm-pale-icon');
                $(".show_cc_helper_addon").addClass('prm-pale-icon');
                $(".g4_show_cc_helper_addon").addClass('prm-pale-icon');
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

                if (vm.ruler_hidden === false) {
                    AnnotationsViewerService.deleteShape(vm.gleason4Shape.shape_id);
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

                for (var el in vm.gleason4ElementsLabels) {
                    vm._hideGleason4Element(vm.gleason4ElementsLabels[el]);
                }

                vm.ruler_hidden = true;

                dialog.close();
            }

            function deleteFocusRegionAnnotationErrorFn(response) {
                $log.error('unable to delete focus region annotation');
                $log.error('response');
                dialog.close();
            }
        }

        function _hideGleason4Element(element_id) {
            AnnotationsViewerService.deleteShape(
                vm.gleason4Elements[element_id].json_path.shape_id
            );
            $("#" + element_id + "_ro").addClass('prm-pale-icon');
            removeItemFromArray(element_id, vm.displayedGleason4ElementsLabels);
        }

        function _showGleason4Element(element_id) {
            AnnotationsViewerService.drawShape(
                vm.gleason4Elements[element_id].json_path
            );
            $("#" + element_id + "_ro").removeClass('prm-pale-icon');
            vm.displayedGleason4ElementsLabels.push(element_id);
        }

        function showHideGleason4Element(element_id) {
            if (vm.displayedGleason4ElementsLabels.indexOf(element_id) !== -1) {
                // hide element
                vm._hideGleason4Element(element_id);
            } else {
                // show element
                vm._showGleason4Element(element_id);
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
})();