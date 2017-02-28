(function () {
    'use strict';

    angular
        .module('promort.clinical_annotations_manager.controllers')
        .controller('ClinicalAnnotationsManagerController', ClinicalAnnotationsManagerController)
        .controller('NewSliceAnnotationController', NewSliceAnnotationController)
        .controller('ShowSliceAnnotationController', ShowSliceAnnotationController);

    ClinicalAnnotationsManagerController.$inject = ['$scope', '$rootScope', '$routeParams', '$compile', '$location',
        'ngDialog', 'Authentication', 'AnnotationsViewerService', 'ClinicalAnnotationStepService'];

    function ClinicalAnnotationsManagerController($scope, $rootScope, $routeParams, $compile, $location, ngDialog,
                                                  Authentication, AnnotationsViewerService,
                                                  ClinicalannotationStepService) {
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
        vm.allModesOff = allModesOff;
        vm.activateNewSliceAnnotationMode = activateNewSliceAnnotationMode;
        vm.newSliceAnnotationModeActive = newSliceAnnotationModeActive;
        vm.activateShowSliceAnnotationMode = activateShowSliceAnnotationMode;
        vm.showSliceAnnotationModeActive = showSliceAnnotationModeActive;

        activate();

        function activate() {
            vm.slide_id = $routeParams.slide;
            vm.case_id = $routeParams.case;
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

            ClinicalannotationStepService.getDetails(vm.case_id, Authentication.getCurrentUser(),
                vm.rois_annotation_step_id, vm.slide_id)
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
                        var $icon = $("#" + slice_label).find('i');
                        $icon.removeClass("icon-check_circle");
                        $icon.addClass("icon-black_question");
                        vm.allModesOff();
                        vm.slices_edit_mode[slice_id] = true;
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
            vm.cores_edit_mode[core_info.id] = !core_info.annotated;
        }

        function _getCoreLabel(core_id) {
            return vm.cores_map[core_id];
        }

        function _registerFocusRegion(focus_region_info) {
            $rootScope.focus_regions.push(focus_region_info);
            vm.focus_regions_map[focus_region_info.id] = focus_region_info.label;
            vm.focus_regions_edit_mode[focus_region_info.id] = !focus_region_info.annotated;
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

        function showROIPanel(roi_type, roi_id) {
            var edit_mode = undefined;
            switch (roi_type) {
                case 'slice':
                    edit_mode = vm.slices_edit_mode[roi_id];
                    break;
                case 'core':
                    edit_mode = vm.cores_edit_mode[roi_id];
                    break;
                case 'focus_region':
                    edit_mode = vm.focus_regions_edit_mode[roi_id];
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
                            break;
                        case 'focus_region':
                            break;
                    }
                }
            } else {
                switch(roi_type) {
                    case 'slice':
                        vm.activateShowSliceAnnotationMode(roi_id);
                        break;
                    case 'core':
                        break;
                    case 'focus_region':
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

        function showSliceAnnotationModeActive(slice_id) {
            return vm.ui_active_modes['show_slice'];
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
            }).then(confirmFm);

            var dialog = undefined;
            function confirmFm(confirm_value) {
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
})();