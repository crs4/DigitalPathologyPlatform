(function () {
    'use strict';

    angular
        .module('promort.clinical_annotations_manager.controllers')
        .controller('ClinicalAnnotationsManagerController', ClinicalAnnotationsManagerController)
        .controller('NewSliceAnnotationController', NewSliceAnnotationController)
        .controller('ShowSliceAnnotationController', ShowSliceAnnotationController)
        .controller('NewCoreAnnotationController', NewCoreAnnotationController)
        .controller('ShowCoreAnnotationController', ShowCoreAnnotationController)
        .controller('NewFocusRegionAnnotationController', NewFocusRegionAnnotationController)
        .controller('ShowFocusRegionAnnotationController', ShowFocusRegionAnnotationController);

    ClinicalAnnotationsManagerController.$inject = ['$scope', '$rootScope', '$routeParams', '$compile', '$location',
        'ngDialog', 'Authentication', 'AnnotationsViewerService', 'ClinicalAnnotationStepService',
        'ClinicalAnnotationStepManagerService'];

    function ClinicalAnnotationsManagerController($scope, $rootScope, $routeParams, $compile, $location, ngDialog,
                                                  Authentication, AnnotationsViewerService,
                                                  ClinicalAnnotationStepService, ClinicalAnnotationStepManagerService) {
        var vm = this;
        vm.slide_id = undefined;
        vm.case_id = undefined;
        vm.rois_annotation_step_id = undefined;
        vm.clinical_annotation_step_id = undefined;

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
        vm.allModesOff = allModesOff;
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
            vm.slide_id = $routeParams.slide;
            vm.case_id = $routeParams.case;
            vm.rois_annotation_id = $routeParams.rois_annotation;
            vm.rois_annotation_step_id = $routeParams.annotation_step;
            vm.clinical_annotation_step_id = $routeParams.clinical_annotation_step;

            vm.slices_map = [];
            vm.cores_map = [];
            vm.focus_regions_map = [];

            vm.slices_edit_mode = [];
            vm.cores_edit_mode = [];
            vm.focus_regions_edit_mode = [];

            $rootScope.slices = [];
            $rootScope.cores = [];
            $rootScope.focus_regions = [];

            ClinicalAnnotationStepService.getDetails(vm.case_id, Authentication.getCurrentUser(),
                vm.rois_annotation_id, vm.slide_id)
                .then(getClinicalAnnotationStepSuccessFn, getClinicalAnnotationStepErrorFn);

            function getClinicalAnnotationStepSuccessFn(response) {
                if (response.data.completed === true || response.data.can_be_started === false) {
                    $location.url('worklist/' + vm.case_id);
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
                console.error('Cannot load slide info');
                console.error(response);
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
            if (focus_region_info.tumor === true) {
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
            for (var x in vm.slices_edit_mode) {
                if (vm.slices_edit_mode[x] === true) {
                    return false;
                }
            }
            for (var x in vm.cores_edit_mode) {
                if (vm.cores_edit_mode[x] === true) {
                    return false;
                }
            }
            for (var x in vm.focus_regions_edit_mode) {
                if (vm.focus_regions_edit_mode[x] === true) {
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
            ngDialog.openConfirm({
                template: '/static/templates/dialogs/accept_clinical_annotation_confirm.html',
                showClose: false,
                closeByEscape: false,
                closeByNavigation: false,
                closeByDocument: false,
                controller: 'NewScopeController',
                controllerAs: 'confirmCtrl'
            }).then(confirmFn);

            function confirmFn(confirm_obj) {
                if (confirm_obj.value === true) {
                    ClinicalAnnotationStepService.closeAnnotationStep(vm.case_id, Authentication.getCurrentUser(),
                        vm.rois_annotation_id, vm.slide_id, confirm_obj.notes)
                        .then(closeClinicalAnnotationStepSuccessFn, closeClinicalAnnotationStepErrorFn);
                }

                function closeClinicalAnnotationStepSuccessFn(response) {
                    if (response.data.clinical_annotation_closed === true) {
                        $location.url('worklist');
                    } else {
                        $location.url('worklist/' + vm.case_id + '/' + vm.rois_annotation_id);
                    }
                }

                function closeClinicalAnnotationStepErrorFn(response) {
                    console.error(response.error);
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

                    ClinicalAnnotationStepManagerService.clearAnnotations(vm.clinical_annotation_step_id)
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
                    console.error('unable to clear existing annotations');
                    console.error(response);
                    dialog.close();
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

    NewSliceAnnotationController.$inject = ['$scope', '$routeParams', '$rootScope', 'ngDialog',
        'SlicesManagerService', 'SliceAnnotationsManagerService'];

    function NewSliceAnnotationController($scope, $routeParams, $rootScope, ngDialog,
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

        vm.clinical_annotation_step_id = undefined;

        vm._clean = _clean;
        vm.isReadOnly = isReadOnly;
        vm.isLocked = isLocked;
        vm.formValid = formValid;
        vm.destroy = destroy;
        vm.save = save;

        activate();

        function activate() {
            vm.clinical_annotation_step_id = $routeParams.clinical_annotation_step;
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
                console.error('Unable to load slice data');
                console.error(response);
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
            SliceAnnotationsManagerService.createAnnotation(vm.slice_id, vm.clinical_annotation_step_id, obj_config)
                .then(createAnnotationSuccessFn, createAnnotationErrorFn);

            function createAnnotationSuccessFn(response) {
                $rootScope.$broadcast('slice_annotation.saved', vm.slice_label, vm.slice_id);
                vm._clean();
                dialog.close();
            }

            function createAnnotationErrorFn(response) {
                console.error('Unable to save annotation');
                console.error(response.data);
                dialog.close();
            }
        }
    }

    ShowSliceAnnotationController.$inject = ['$scope', '$routeParams', '$rootScope', 'ngDialog',
        'SliceAnnotationsManagerService'];

    function ShowSliceAnnotationController($scope, $routeParams, $rootScope, ngDialog,
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

        vm.clinical_annotation_step_id = undefined;

        vm.isReadOnly = isReadOnly;
        vm.isLocked = isLocked;
        vm.destroy = destroy;
        vm.deleteAnnotation = deleteAnnotation;

        activate();

        function activate() {
            vm.clinical_annotation_step_id = $routeParams.clinical_annotation_step;
            $scope.$on('slice_annotation.show',
                function(event, slice_id) {
                    vm.slice_id = slice_id;
                    SliceAnnotationsManagerService.getAnnotation(vm.slice_id, vm.clinical_annotation_step_id)
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
                console.error('Unable to load slice annotatin data');
                console.error(response);
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
                    SliceAnnotationsManagerService.deleteAnnotation(vm.slice_id, vm.clinical_annotation_step_id)
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
                console.error('unable to delete slice annotation');
                console.error(response);
                dialog.close();
            }
        }
    }

    NewCoreAnnotationController.$inject = ['$scope', '$routeParams', '$rootScope', 'ngDialog',
        'CoresManagerService', 'CoreAnnotationsManagerService'];

    function NewCoreAnnotationController($scope, $routeParams, $rootScope, ngDialog,
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

        vm.clinical_annotation_step_id = undefined;

        vm._clean = _clean;
        vm.isReadOnly = isReadOnly;
        vm.isLocked = isLocked;
        vm.formValid = formValid;
        vm.destroy = destroy;
        vm.upgradeGradeGroupWho = updateGradeGroupWho;
        vm.save = save;

        activate();

        function activate() {
            vm.clinical_annotation_step_id = $routeParams.clinical_annotation_step;
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
                vm.coreLength = response.data.length;
                vm.tumorLength = response.data.tumor_length;
            }

            function getCoreErrorFn(response) {
                console.error('Unable to load core data');
                console.error(response);
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
            CoreAnnotationsManagerService.createAnnotation(vm.core_id, vm.clinical_annotation_step_id, obj_config)
                .then(createAnnotationSuccessFn, createAnnotationErrorFn);

            function createAnnotationSuccessFn(response) {
                $rootScope.$broadcast('core_annotation.saved', vm.core_label, vm.core_id);
                vm._clean();
                dialog.close();
            }

            function createAnnotationErrorFn(response) {
                console.error('Unable to save annotation');
                console.error(response.data);
                dialog.close();
            }
        }
    }

    ShowCoreAnnotationController.$inject = ['$scope', '$routeParams', '$rootScope', 'ngDialog',
        'CoreAnnotationsManagerService', 'CoresManagerService'];

    function ShowCoreAnnotationController($scope, $routeParams, $rootScope, ngDialog,
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

        vm.clinical_annotation_step_id = undefined;

        vm.locked = undefined;

        vm.isReadOnly = isReadOnly;
        vm.isLocked = isLocked;
        vm.destroy = destroy;
        vm.deleteAnnotation = deleteAnnotation;

        activate();

        function activate() {
            vm.clinical_annotation_step_id = $routeParams.clinical_annotation_step;
            $scope.$on('core_annotation.show',
                function (event, core_id) {
                    vm.locked = false;
                    vm.core_id = core_id;
                    CoreAnnotationsManagerService.getAnnotation(vm.core_id, vm.clinical_annotation_step_id)
                        .then(getCoreAnnotationSuccessFn, getCoreAnnotationErrorFn);
                }
            );

            function getCoreAnnotationSuccessFn(response) {
                vm.core_label = response.data.core.label;
                vm.coreArea = response.data.core.area;
                vm.coreLength = response.data.core.length;
                vm.tumorLength = response.data.core.tumor_length;
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
                    console.error('Unable to load core annotation data');
                    console.error(response);
                }

                function getCoreSuccessFn(response) {
                    vm.core_label = response.data.label;
                    vm.coreArea = response.data.area;
                    vm.coreLength = response.data.length;
                    vm.tumorLength = response.data.tumor_length;
                    vm.normalTissuePercentage = response.data.normal_tissue_percentage;
                    vm.locked = true;
                }

                function getCoreErrorFn(response) {
                    console.error('Unable to load core data');
                    console.error(response);
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
                    CoreAnnotationsManagerService.deleteAnnotation(vm.core_id, vm.clinical_annotation_step_id)
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
                console.error('unable to delete core annotation');
                console.error(response);
                dialog.close();
            }
        }
    }

    NewFocusRegionAnnotationController.$inject = ['$scope', '$routeParams', '$rootScope', 'ngDialog',
        'FocusRegionsManagerService', 'FocusRegionAnnotationsManagerService', 'AnnotationsViewerService'];

    function NewFocusRegionAnnotationController($scope, $routeParams, $rootScope, ngDialog, FocusRegionsManagerService,
                                                FocusRegionAnnotationsManagerService, AnnotationsViewerService) {
        var vm = this;
        vm.focus_region_id = undefined;
        vm.focus_region_label = undefined;
        vm.focusRegionArea = undefined;
        vm.coreCoveragePercentage = undefined;
        vm.cancerousRegion = false;
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
        vm.gleason4Shape = undefined;
        vm.gleason4ShapeArea = undefined;
        vm.cellularDensityHelperShape = undefined;
        vm.cellularDensity = undefined;
        vm.cellsCount = undefined;
        vm.g4CellularDensityHelperShape = undefined;
        vm.g4CellularDensity = undefined;
        vm.g4CellsCount = undefined;

        vm.clinical_annotation_step_id = undefined;

        vm.ruler_tool_active = false;
        vm.ruler_hidden = true;

        vm.cellular_density_helper_active = false;
        vm.g4_cellular_density_helper_active = false;
        vm.tmp_cellular_density_helper_id = undefined;
        vm.tmp_cellular_density_helper_exists = false;
        vm.cellular_density_helper_hidden = true;
        vm.g4_cellular_density_helper_hidden = true;

        vm._clean = _clean;
        vm.isReadOnly = isReadOnly;
        vm.isLocked = isLocked;
        vm.formValid = formValid;
        vm.destroy = destroy;
        vm.save = save;
        vm.initializeRuler = initializeRuler;
        vm.startRuler = startRuler;
        vm.rulerToolActive = rulerToolActive;
        vm.rulerExists = rulerExists;
        vm.abortRuler = abortRuler;
        vm.clearRuler = clearRuler;
        vm.showRuler = showRuler;
        vm.hideRuler = hideRuler;
        vm.showHideRuler = showHideRuler;
        vm.startCellularDensityHelper = startCellularDensityHelper;
        vm.startG4CellularDensityHelper = startG4CellularDensityHelper;
        vm.abortCellularDensityHelper = abortCellularDensityHelper;
        vm.abortG4CellularDensityHelper = abortG4CellularDensityHelper;
        vm.clearCellularDensityHelper = clearCellularDensityHelper;
        vm.clearG4CellularDensityHelper = clearG4CellularDensityHelper;
        vm.cellularDensityHelperActive = cellularDensityHelperActive;
        vm.g4CellularDensityHelperActive = g4CellularDensityHelperActive;
        vm.validCellularDensity = validCellularDensity;
        vm.validG4CellularDensity = validG4CellularDensity;
        vm.showCellularDensityHelper = showCellularDensityHelper;
        vm.showG4CellularDensityHelper = showG4CellularDensityHelper;
        vm.hideCellularDensityHelper = hideCellularDensityHelper;
        vm.hideG4CellularDensityHelper = hideG4CellularDensityHelper;
        vm.cellularDensityExists = cellularDensityExists;
        vm.g4CellularDensityExists = g4CellularDensityExists;
        vm.showHideCellularDensityHelper = showHideCeullularDensityHelper;
        vm.showHideG4CellularDensityHelper = showHideG4CellularDensityHelper;

        activate();

        function activate() {
            vm.clinical_annotation_step_id = $routeParams.clinical_annotation_step;

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
                vm.focusRegionLength = response.data.length;
                vm.coreCoveragePercentage = Number(parseFloat(response.data.core_coverage_percentage).toFixed(3));
                vm.cancerousRegion = response.data.cancerous_region;
            }

            function getFocusRegionErrorFn(response) {
                console.error('Unable to load focus region data');
                console.error(response);
            }

            $scope.$on('viewerctrl.components.registered',
                function() {
                    vm.initializeRuler();
                }
            );
        }

        function _clean() {
            vm.clearRuler();
            vm.clearCellularDensityHelper();
            vm.clearG4CellularDensityHelper();

            vm.focus_region_id = undefined;
            vm.focus_region_label = undefined;
            vm.focusRegionArea = undefined;
            vm.coreCoveragePercentage = undefined;
            vm.cancerousRegion = false;
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

            AnnotationsViewerService.disableActiveTool();
            vm.ruler_tool_active = false;
            vm.ruler_hidden = true;
        }

        function initializeRuler() {
            AnnotationsViewerService.createAreaRulerBindings('area_ruler_switch_on',
                'gleason_4_area_output');
        }

        function showRuler() {
            AnnotationsViewerService.drawShape(vm.gleason4Shape);
            $(".show_ruler").removeClass('prm-pale-icon');
            vm.ruler_hidden = false;
        }

        function hideRuler() {
            AnnotationsViewerService.deleteShape(vm.gleason4Shape.shape_id);
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

        function startRuler() {
            var $ruler_out = $("#gleason_4_area_output");
            AnnotationsViewerService.bindAreaRulerToShape(vm.focus_region_label);
            $ruler_out
                .on('area_ruler_updated',
                    function() {
                        vm.gleason4ShapeArea = $ruler_out.data('measure');
                        vm.gleason4Shape = $ruler_out.data('ruler_json');
                    }
                )
                .on('area_ruler_empty_intersection',
                    function() {
                        vm.ruler_tool_active = false;
                        $ruler_out.unbind('area_ruler_cleared')
                            .unbind('area_ruler_updated')
                            .unbind('area_ruler_empty_intersection');
                        vm.gleason4Shape = undefined;
                        vm.gleason4ShapeArea = undefined;
                        AnnotationsViewerService.disableActiveTool();
                        $scope.$apply();
                        ngDialog.open({
                            template: '/static/templates/dialogs/invalid_gleason_4.html'
                        });
                    }
                )
                .on('area_ruler_cleared',
                    function() {
                        $ruler_out.unbind('area_ruler_cleared')
                            .unbind('area_ruler_updated')
                            .unbind('area_ruler_empty_intersection');
                        vm.ruler_tool_active = false;
                        AnnotationsViewerService.disableActiveTool();
                        vm.showRuler();
                        $scope.$apply();
                    }
                );
            vm.ruler_tool_active = true;
        }

        function abortRuler() {
            var $ruler_out = $("#gleason_4_area_output");
            $ruler_out
                .unbind('area_ruler_updated')
                .unbind('area_ruler_empty_intersection')
                .unbind('area_ruler_cleared');
            vm.ruler_tool_active = false;
            AnnotationsViewerService.disableActiveTool();
        }

        function clearRuler() {
            if (vm.gleason4Shape) {
                vm.hideRuler();
            }
            vm.gleason4Shape = undefined;
            vm.gleason4ShapeArea = undefined;
            if (vm.g4CellularDensityExists()) {
                vm.clearG4CellularDensityHelper();
            }
        }

        function rulerToolActive() {
            return vm.ruler_tool_active;
        }

        function rulerExists() {
            return (typeof vm.gleason4Shape !== 'undefined');
        }

        function startCellularDensityHelper() {
            vm.cellular_density_helper_active = true;
            var canvas_label = AnnotationsViewerService.getCanvasLabel();
            var $canvas = $("#" + canvas_label);
            $canvas
                .on('cellular_count_helper.created',
                    function(event, helper_id) {
                        vm.tmp_cellular_density_helper_id = helper_id;
                        $canvas.unbind('cellular_count_helper.created');
                    }
                )
                .on('cellular_count_helper.saved',
                    function(event, helper_json) {
                        AnnotationsViewerService.disableActiveTool();
                        vm.tmp_cellular_density_helper_exists = false;
                        vm.tmp_cellular_density_helper_id = undefined;
                        vm.cellular_density_helper_active = false;
                        vm.cellularDensityHelperShape = helper_json;
                        vm.showCellularDensityHelper();
                        var helper_area = AnnotationsViewerService.getShapeArea(vm.cellularDensityHelperShape.shape_id);
                        vm.cellsCount = Math.round((vm.focusRegionArea / helper_area) * vm.cellularDensity);
                        $scope.$apply();
                        $canvas
                            .unbind('cellular_count_helper.saved')
                            .unbind('cellular_count_helper.placed')
                    }
                )
                .on('cellular_count_helper.placed',
                    function() {
                        vm.tmp_cellular_density_helper_exists = true;
                        $scope.$apply();
                    }
                );
        }

        function startG4CellularDensityHelper() {
            vm.g4_cellular_density_helper_active = true;
            var canvas_label = AnnotationsViewerService.getCanvasLabel();
            var $canvas = $("#" + canvas_label);
            $canvas
                .on('cellular_count_helper.created',
                    function(event, helper_id) {
                        vm.tmp_cellular_density_helper_id = helper_id;
                        $canvas.unbind('cellular_count_helper.created');
                    }
                )
                .on('cellular_count_helper.saved',
                    function(event, helper_json) {
                        AnnotationsViewerService.disableActiveTool();
                        vm.tmp_cellular_density_helper_exists = false;
                        vm.tmp_cellular_density_helper_id = undefined;
                        vm.g4_cellular_density_helper_active = false;
                        vm.g4CellularDensityHelperShape = helper_json;
                        vm.g4CellularDensityHelperShape.shape_id = 'G4_' + vm.g4CellularDensityHelperShape.shape_id;
                        vm.showG4CellularDensityHelper();
                        var helper_area = AnnotationsViewerService.getShapeArea(
                            vm.g4CellularDensityHelperShape.shape_id);
                        vm.g4CellsCount = Math.round((vm.gleason4ShapeArea / helper_area) * vm.g4CellularDensity);
                        $scope.$apply();
                        $canvas
                            .unbind('cellular_count_helper.saved')
                            .unbind('cellular_count_helper.placed')
                    }
                )
                .on('cellular_count_helper.placed',
                    function() {
                        vm.tmp_cellular_density_helper_exists = true;
                        $scope.$apply();
                    }
                )
        }

        function abortCellularDensityHelper() {
            if (vm.tmp_cellular_density_helper_exists) {
                AnnotationsViewerService.deleteShape(vm.tmp_cellular_density_helper_id);
            }
            var canvas_label = AnnotationsViewerService.getCanvasLabel();
            var $canvas = $("#" + canvas_label);
            $canvas
                .unbind('cellular_count_helper.saved')
                .unbind('cellular_count_helper.placed');
            vm.tmp_cellular_density_helper_exists = false;
            vm.tmp_cellular_density_helper_id = undefined;
            vm.cellular_density_helper_active = false;
            vm.cellular_density_helper_hidden = true;
            vm.cellularDensity = undefined;
            AnnotationsViewerService.disableActiveTool();
        }

        function abortG4CellularDensityHelper() {
            if (vm.tmp_cellular_density_helper_exists) {
                AnnotationsViewerService.deleteShape(vm.tmp_cellular_density_helper_id);
            }
            var canvas_label = AnnotationsViewerService.getCanvasLabel();
            var $canvas = $("#" + canvas_label);
            $canvas
                .unbind('cellular_count_helper.saved')
                .unbind('cellular_count_helper.placed');
            vm.tmp_cellular_density_helper_exists = false;
            vm.tmp_cellular_density_helper_id = undefined;
            vm.g4_cellular_density_helper_active = false;
            vm.g4_cellular_density_helper_hidden = true;
            vm.g4CellularDensity = undefined;
            AnnotationsViewerService.disableActiveTool();
        }

        function clearCellularDensityHelper() {
            if (!vm.cellular_density_helper_hidden) {
                vm.hideCellularDensityHelper();
            }
            vm.abortCellularDensityHelper();
            vm.cellularDensity = undefined;
            vm.cellularDensityHelperShape = undefined;
            vm.cellsCount = undefined;
        }

        function clearG4CellularDensityHelper() {
            if (!vm.g4_cellular_density_helper_hidden) {
                vm.hideG4CellularDensityHelper();
            }
            vm.abortG4CellularDensityHelper();
            vm.g4CellularDensity = undefined;
            vm.g4CellularDensityHelperShape = undefined;
            vm.g4CellsCount = undefined;
        }

        function cellularDensityHelperActive() {
            return vm.cellular_density_helper_active;
        }

        function g4CellularDensityHelperActive() {
            return vm.g4_cellular_density_helper_active;
        }

        function validCellularDensity() {
            return (vm.tmp_cellular_density_helper_exists && vm.cellularDensity > 0);
        }

        function validG4CellularDensity() {
            return (vm.tmp_cellular_density_helper_exists && vm.g4CellularDensity > 0);
        }

        function showCellularDensityHelper() {
            AnnotationsViewerService.drawShape(vm.cellularDensityHelperShape);
            $(".show_cc_helper").removeClass('prm-pale-icon');
            vm.cellular_density_helper_hidden = false;
        }

        function showG4CellularDensityHelper() {
            AnnotationsViewerService.drawShape(vm.g4CellularDensityHelperShape);
            $(".show_g4_cc_helper").removeClass('prm-pale-icon');
            vm.g4_cellular_density_helper_hidden = false;
        }

        function hideCellularDensityHelper() {
            AnnotationsViewerService.deleteShape(vm.cellularDensityHelperShape.shape_id);
            $(".show_cc_helper").addClass('prm-pale-icon');
            vm.cellular_density_helper_hidden = true;
        }

        function hideG4CellularDensityHelper() {
            AnnotationsViewerService.deleteShape(vm.g4CellularDensityHelperShape.shape_id);
            $(".show_g4_cc_helper").addClass('prm-pale-icon');
            vm.g4_cellular_density_helper_hidden = true;
        }

        function showHideCeullularDensityHelper() {
            if (vm.cellular_density_helper_hidden === true) {
                vm.showCellularDensityHelper();
            } else {
                vm.hideCellularDensityHelper();
            }
        }

        function showHideG4CellularDensityHelper() {
            if (vm.g4_cellular_density_helper_hidden === true) {
                vm.showG4CellularDensityHelper();
            } else {
                vm.hideG4CellularDensityHelper();
            }
        }

        function cellularDensityExists() {
            return (typeof vm.cellsCount !== 'undefined');
        }

        function g4CellularDensityExists() {
            return (typeof vm.g4CellsCount !== 'undefined');
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
            console.log('CELLS COUNT: ' + vm.cellsCount);
            console.log('CELL SHAPE ' + vm.cellularDensityHelperShape);
            var dialog = undefined;
            dialog = ngDialog.open({
                template: '/static/templates/dialogs/saving_data.html',
                showClose: false,
                closeByEscape: false,
                closeByNavigation: false,
                closeByDocument: false
            });
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
                gleason_4_path_json: vm.gleason4Shape,
                gleason_4_area: vm.gleason4ShapeArea,
                cellular_density_helper_json: vm.cellularDensityHelperShape,
                cellular_density: vm.cellularDensity,
                cells_count: vm.cellsCount,
                gleason_4_cellular_density_helper_json: vm.g4CellularDensityHelperShape,
                gleason_4_cellular_density: vm.g4CellularDensity,
                gleason_4_cells_count: vm.g4CellsCount
            };
            FocusRegionAnnotationsManagerService.createAnnotation(vm.focus_region_id,
                vm.clinical_annotation_step_id, obj_config)
                .then(createAnnotationSuccessFn, createAnnotationErrorFn);

            function createAnnotationSuccessFn(response) {
                $rootScope.$broadcast('focus_region_annotation.saved',
                    vm.focus_region_label, vm.focus_region_id);
                vm._clean();
                dialog.close();
            }

            function createAnnotationErrorFn(response) {
                console.error('Unable to save annotation');
                console.error(response.data);
                dialog.close();
            }
        }
    }

    ShowFocusRegionAnnotationController.$inject = ['$scope', '$routeParams', '$rootScope', 'ngDialog',
        'FocusRegionAnnotationsManagerService', 'FocusRegionsManagerService', 'AnnotationsViewerService'];

    function ShowFocusRegionAnnotationController($scope, $routeParams, $rootScope, ngDialog,
                                                 FocusRegionAnnotationsManagerService, FocusRegionsManagerService,
                                                 AnnotationsViewerService) {
        var vm = this;
        vm.focus_region_id = undefined;
        vm.focus_region_label = undefined;
        vm.focusRegionArea = undefined;
        vm.coreCoveragePercentage = undefined;
        vm.cancerousRegion = false;
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
        vm.gleason4Shape = undefined;
        vm.gleason4ShapeArea = undefined;
        vm.cellularDensityHelperShape = undefined;
        vm.cellsCount = undefined;
        vm.g4CellularDensityHelperShape = undefined;
        vm.g4CellularDensity = undefined;
        vm.g4CellsCount = undefined;

        vm.clinical_annotation_step_id = undefined;

        vm.ruler_hidden = true;
        vm.cellular_density_helper_hidden = true;
        vm.g4_cellular_density_helper_hidden = true;
        vm.locked = undefined;

        vm.isReadOnly = isReadOnly;
        vm.isLocked = isLocked;
        vm.destroy = destroy;
        vm.deleteAnnotation = deleteAnnotation;
        vm.showHideRuler = showHideRuler;
        vm.showHideCellularDensityHelper = showHideCellularDensityHelper;
        vm.showHideG4CellularDensityHelper = showHideG4CellularDensityHelper;
        vm.cellularDensityExists = cellularDensityExists;
        vm.g4CellularDensityExists = g4CellularDensityExists;
        vm.rulerExists = rulerExists;

        activate();

        function activate() {
            vm.clinical_annotation_step_id = $routeParams.clinical_annotation_step;
            $scope.$on('focus_region_annotation.show',
                function (event, focus_region_id) {
                    vm.locked = false;
                    vm.focus_region_id = focus_region_id;
                    FocusRegionAnnotationsManagerService.getAnnotation(vm.focus_region_id,
                        vm.clinical_annotation_step_id)
                        .then(getFocusRegionAnnotationSuccessFn, getFocusRegionAnnotationErrorFn);
                }
            );

            function getFocusRegionAnnotationSuccessFn(response) {
                vm.focus_region_label = response.data.focus_region.label;
                vm.focusRegionArea  = response.data.focus_region.area;
                vm.coreCoveragePercentage = Number(parseFloat(response.data.focus_region.core_coverage_percentage)
                    .toFixed(3));
                vm.cancerousRegion = response.data.focus_region.cancerous_region;
                vm.focusRegionLength = response.data.focus_region.length;
                vm.perineuralInvolvement = response.data.perineural_involvement;
                vm.intraductalCarcinoma = response.data.intraductal_carcinoma;
                vm.ductalCarcinoma = response.data.ductal_carcinoma;
                vm.poorlyFormedGlands = response.data.poorly_formed_glands;
                vm.cribriformPattern = response.data.cribriform_pattern;
                vm.smallCellSignetRing = response.data.small_cell_signet_ring;
                vm.hypernephroidPattern = response.data.hypernephroid_pattern;
                vm.mucinous = response.data.mucinous;
                vm.comedoNecrosis = response.data.comedo_necrosis;
                vm.gleason4Shape = $.parseJSON(response.data.gleason_4_path_json);
                vm.gleason4ShapeArea = response.data.gleason_4_area;
                vm.cellularDensityHelperShape = $.parseJSON(response.data.cellular_density_helper_json);
                vm.cellsCount = response.data.cells_count;
                vm.g4CellularDensityHelperShape = $.parseJSON(response.data.gleason_4_cellular_density_helper_json);
                vm.g4CellularDensity = response.data.gleason_4_cellular_density;
                vm.g4CellsCount = response.data.gleason_4_cells_count;

                $(".show_ruler").addClass('prm-pale-icon');
                $(".show_cc_helper_addon").addClass('prm-pale-icon');
                $(".g4_show_cc_helper_addon").addClass('prm-pale-icon');
            }

            function getFocusRegionAnnotationErrorFn(response) {
                if (response.status === 404) {
                    FocusRegionsManagerService.get(vm.focus_region_id)
                        .then(getFocusRegionSuccessFn, getFocusRegionErrorFn);
                } else {
                    console.error('Unable to load focus region annotation data');
                    console.error(response);
                }

                function getFocusRegionSuccessFn(response) {
                    vm.focus_region_label = response.data.label;
                    vm.focusRegionArea = response.data.area;
                    vm.coreCoveragePercentage = response.data.core_coverage_percentage;
                    vm.cancerousRegion = response.data.cancerous_region;
                    vm.focusRegionLength = response.data.length;
                    vm.locked = true;
                }

                function getFocusRegionErrorFn(response) {
                    console.error('Unable to load focus region data');
                    console.error(response);
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
                    FocusRegionAnnotationsManagerService.deleteAnnotation(vm.focus_region_id,
                        vm.clinical_annotation_step_id)
                        .then(deleteFocusRegionAnnotationSuccessFn, deleteFocusRegionAnnotationErrorFn);
                }
            }

            function deleteFocusRegionAnnotationSuccessFn(response) {
                $rootScope.$broadcast('focus_region_annotation.deleted', vm.focus_region_label, vm.focus_region_id);

                if (vm.ruler_hidden === false) {
                    AnnotationsViewerService.deleteShape(vm.gleason4Shape.shape_id);
                }
                if (vm.cellular_density_helper_hidden === false) {
                    AnnotationsViewerService.deleteShape(vm.cellularDensityHelperShape.shape_id);
                }
                if (vm.g4_cellular_density_helper_hidden === false) {
                    AnnotationsViewerService.deleteShape(vm.g4CellularDensityHelperShape.shape_id);
                }

                vm.focus_region_id = undefined;
                vm.focus_region_label = undefined;
                vm.focusRegionArea = undefined;
                vm.coreCoveragePercentage = undefined;
                vm.cancerousRegion = false;
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
                vm.gleason4Shape = undefined;
                vm.gleason4ShapeArea = undefined;
                vm.cellularDensityHelperShape = undefined;
                vm.cellsCount = undefined;
                vm.g4CellularDensityHelperShape = undefined;
                vm.g4CellularDensity = undefined;
                vm.g4CellsCount = undefined;

                vm.ruler_hidden = true;
                vm.cellular_density_helper_hidden = true;
                vm.g4_cellular_density_helper_hidden = true;


                dialog.close();
            }

            function deleteFocusRegionAnnotationErrorFn(response) {
                console.error('unable to delete focus region annotation');
                console.error('response');
                dialog.close();
            }
        }

        function showHideRuler() {
            if (vm.gleason4Shape) {
                if (vm.ruler_hidden === true) {
                    console.log(vm.gleason4Shape);
                    AnnotationsViewerService.drawShape(vm.gleason4Shape);
                    $(".show_ruler").removeClass('prm-pale-icon');
                    vm.ruler_hidden = false;
                } else {
                    AnnotationsViewerService.deleteShape(vm.gleason4Shape.shape_id);
                    $(".show_ruler").addClass('prm-pale-icon');
                    vm.ruler_hidden = true;
                }
            }
        }

        function rulerExists() {
            return (vm.gleason4Shape !== null && typeof vm.gleason4Shape !== 'undefined');
        }

        function showHideCellularDensityHelper() {
            if (vm.cellularDensityHelperShape) {
                if (vm.cellular_density_helper_hidden === true) {
                    AnnotationsViewerService.drawShape(vm.cellularDensityHelperShape);
                    $(".show_cc_helper_addon").removeClass('prm-pale-icon');
                    vm.cellular_density_helper_hidden = false;
                } else {
                    AnnotationsViewerService.deleteShape(vm.cellularDensityHelperShape.shape_id);
                    $(".show_cc_helper_addon").addClass('prm-pale-icon');
                    vm.cellular_density_helper_hidden = true;
                }
            }
        }

        function showHideG4CellularDensityHelper() {
            if (vm.g4CellularDensityHelperShape) {
                if (vm.g4_cellular_density_helper_hidden === true) {
                    AnnotationsViewerService.drawShape(vm.g4CellularDensityHelperShape);
                    $(".g4_show_cc_helper_addon").removeClass('prm-pale-icon');
                    vm.g4_cellular_density_helper_hidden = false;
                } else {
                    AnnotationsViewerService.deleteShape(vm.g4CellularDensityHelperShape.shape_id);
                    $(".g4_show_cc_helper_addon").addClass('prm-pale-icon');
                    vm.g4_cellular_density_helper_hidden = true;
                }
            }
        }

        function cellularDensityExists() {
            return (vm.cellularDensityHelperShape !== null && typeof vm.cellularDensityHelperShape !== 'undefined');
        }

        function g4CellularDensityExists() {
            return (vm.g4CellularDensityHelperShape !== null && typeof vm.cellularDensityHelperShape !== 'undefined');
        }
    }
})();