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
        .module('promort.viewer.services')
        .factory('CurrentAnnotationStepsDetailsService', CurrentAnnotationStepsDetailsService)
        .factory('ViewerService', ViewerService)
        .factory('HeatmapViewerService', HeatmapViewerService)
        .factory('AnnotationsViewerService', AnnotationsViewerService)
        .factory('SlidesSequenceViewerService', SlidesSequenceViewerService);

    CurrentAnnotationStepsDetailsService.$inject = ['$http', '$log'];

    function CurrentAnnotationStepsDetailsService($http, $log) {
        var roisAnnotationStepLabel = undefined;
        var clinicalAnnotationStepLabel = undefined;

        var CurrentAnnotationStepsDetailsService = {
            setROIsAnnotationStepLabel: setROIsAnnotationStepLabel,
            setClinicalAnnotationStepLabel: setClinicalAnnotationStepLabel,
            findROIsAnnotationStepLabelByClinicalStep: findROIsAnnotationStepLabelByClinicalStep,
            getROIsAnnotationStepLabel: getROIsAnnotationStepLabel,
            getClinicalAnnotationStepLabel: getClinicalAnnotationStepLabel
        };

        return CurrentAnnotationStepsDetailsService;

        function setROIsAnnotationStepLabel(step_label) {
            roisAnnotationStepLabel = step_label;
        }

        function setClinicalAnnotationStepLabel(step_label) {
            clinicalAnnotationStepLabel = step_label;
        }

        function findROIsAnnotationStepLabelByClinicalStep(clinical_step_label) {
            return $http.get('api/clinical_annotations/steps/' + clinical_step_label + '/');
        }

        function getROIsAnnotationStepLabel() {
            return roisAnnotationStepLabel;
        }

        function getClinicalAnnotationStepLabel() {
            return clinicalAnnotationStepLabel;
        }
    }

    ViewerService.$inject = ['$http', '$log'];

    function ViewerService($http, $log) {
        var ViewerService = {
            getOMEBaseURLs: getOMEBaseURLs,
            getSlideInfo: getSlideInfo
        };

        return ViewerService;

        function getOMEBaseURLs() {
            return $http.get('api/utils/omeseadragon_base_urls/');
        }

        function getSlideInfo(slide_id) {
            return $http.get('api/slides/' + slide_id + '/');
        }
    }

    HeatmapViewerService.$inject = ['$http', '$rootScope', '$log'];

    function HeatmapViewerService($http, $rootScope, $log) {
        var HeatmapViewerService = {
            registerComponents: registerComponents,
            getPredictionInfo: getPredictionInfo,
            setOverlay: setOverlay,
            setOverlayOpacity: setOverlayOpacity
        };

        return HeatmapViewerService;

        function registerComponents(viewer_manager, dataset_base_url) {
            this.viewerManager = viewer_manager;
            this.dataset_base_url = dataset_base_url;
            $rootScope.$broadcast('viewerctrl.components.registered');
        }

        function getPredictionInfo(prediction_id) {
            return $http.get('api/predictions/' + prediction_id + '/');
        }

        function setOverlay(palette, threshold) {
            this.viewerManager.setOverlay(this.dataset_base_url, palette, threshold);
        }

        function setOverlayOpacity(opacity) {
            this.viewerManager.setOverlayOpacity(opacity);
        }
    }
    
    AnnotationsViewerService.$inject = ['$log'];

    function AnnotationsViewerService($log) {
        var AnnotationsViewerService = {
            registerComponents: registerComponents,
            checkComponents: checkComponents,
            drawShape: drawShape,
            selectShape: selectShape,
            deselectShape: deselectShape,
            extendPolygonConfig: extendPolygonConfig,
            extendPathConfig: extendPathConfig,
            extendRulerConfig: extendRulerConfig,
            startPolygonsTool: startPolygonsTool,
            disableActiveTool: disableActiveTool,
            shapeIdAvailable: shapeIdAvailable,
            getFirstAvailableLabel: getFirstAvailableLabel,
            changeShapeId: changeShapeId,
            saveTemporaryPolygon: saveTemporaryPolygon,
            clearTemporaryPolygon: clearTemporaryPolygon,
            temporaryPolygonExists: temporaryPolygonExists,
            temporaryPolygonValid: temporaryPolygonValid,
            polygonRestoreHistoryExists: polygonRestoreHistoryExists,
            rollbackPolygon: rollbackPolygon,
            restorePolygon: restorePolygon,
            startFreehandDrawingTool: startFreehandDrawingTool,
            activatePreviewMode: activatePreviewMode,
            deactivatePreviewMode: deactivatePreviewMode,
            isPreviewModeActive: isPreviewModeActive,
            saveTemporaryFreehandShape: saveTemporaryFreehandShape,
            clearTemporaryFreehandShape: clearTemporaryFreehandShape,
            tmpFreehandPathExists: tmpFreehandPathExists,
            tmpFreehandPathValid: tmpFreehandPathValid,
            shapeUndoHistoryExists: shapeUndoHistoryExists,
            shapeRestoreHistoryExists: shapeRestoreHistoryExists,
            rollbackTemporaryFreehandShape: rollbackTemporaryFreehandShape,
            restoreTemporaryFreehandShape: restoreTemporaryFreehandShape,
            setFreehandToolLabelPrefix: setFreehandToolLabelPrefix,
            deleteShape: deleteShape,
            clear: clear,
            deleteShapes: deleteShapes,
            getCanvasLabel: getCanvasLabel,
            getShapeJSON: getShapeJSON,
            getShapeArea: getShapeArea,
            focusOnShape: focusOnShape,
            checkContainment: checkContainment,
            adaptToContainer: adaptToContainer,
            createRulerBindings: createRulerBindings,
            startRuler: startRuler,
            clearRuler: clearRuler,
            tmpAreaRulerExists: tmpAreaRulerExists,
            tmpAreaRulerValid: tmpAreaRulerValid,
            areaRulerUndoHistoryExists: areaRulerUndoHistoryExists,
            areaRulerRedoHistoryExists: areaRulerRedoHistoryExists,
            createAreaRulerBindings: createAreaRulerBindings,
            clearAreaRuler: clearAreaRuler,
            bindAreaRulerToShape: bindAreaRulerToShape,
            startAreaRulerTool: startAreaRulerTool,
            activateAreaRulerPreviewMode: activateAreaRulerPreviewMode,
            deactivateAreaRulerPreviewMode: deactivateAreaRulerPreviewMode,
            isAreaRulerPreviewModeActive: isAreaRulerPreviewModeActive,
            rollbackAreaRuler: rollbackAreaRuler,
            restoreAreaRuler: restoreAreaRuler,
            saveAreaRuler: saveAreaRuler,
            getAreaCoverage: getAreaCoverage,
            setShapeStrokeColor: setShapeStrokeColor
        };

        return AnnotationsViewerService;

        function registerComponents(viewer_manager, rois_manager, tools_manager) {
            this.viewerManager = viewer_manager;
            this.roisManager = rois_manager;
            this.toolsManager = tools_manager;
        }

        function checkComponents() {
            $log.debug('Viewer Manager: ' + this.viewerManager);
            $log.debug('ROIs Manager: ' + this.roisManager);
            $log.debug('Tools Manager: ' + this.toolsManager);
        }

        function drawShape(shape_json) {
            this.roisManager.drawShapeFromJSON(shape_json);
        }

        function selectShape(shape_id) {
            this.roisManager.selectShape(shape_id, true, true);
        }

        function deselectShape(shape_id) {
            this.roisManager.deselectShape(shape_id, true);
        }

        function extendPolygonConfig(polygon_config) {
            this.roisManager.extendPolygonConfig(polygon_config);
        }

        function extendPathConfig(path_config) {
            this.roisManager.extendPathConfig(path_config);
        }

        function extendRulerConfig(ruler_config) {
            this.roisManager.extendRulerConfig(ruler_config);
        }

        function startPolygonsTool() {
            this.toolsManager.activateTool(AnnotationsEventsController.POLYGON_DRAWING_TOOL);
        }

        function disableActiveTool() {
            this.roisManager.disableMouseEvents();
        }

        function shapeIdAvailable(shape_label) {
            return this.roisManager.shapeIdAvailable(shape_label);
        }

        function getFirstAvailableLabel(shape_label_prefix) {
            return this.roisManager.getFirstAvailableLabel(shape_label_prefix);
        }

        function changeShapeId(shape_id, new_shape_id) {
            this.roisManager.changeShapeId(shape_id, new_shape_id);
        }

        function saveTemporaryPolygon(label_prefix) {
            this.roisManager.saveTemporaryPolygon(label_prefix);
        }

        function clearTemporaryPolygon() {
            this.roisManager.clearTemporaryPolygon();
        }

        function temporaryPolygonExists() {
            if (typeof this.roisManager !== 'undefined') {
                return this.roisManager.temporaryPolygonExists();
            }
        }

        function temporaryPolygonValid() {
            if (typeof this.roisManager !== 'undefined') {
                return this.roisManager.temporaryPolygonValid();
            }
        }

        function polygonRestoreHistoryExists() {
            if (typeof this.roisManager !== 'undefined') {
                return this.roisManager.polygonRedoHistoryExists();
            }
        }

        function rollbackPolygon() {
            this.roisManager.rollbackPolygon();
        }

        function restorePolygon() {
            this.roisManager.restorePolygon();
        }

        function startFreehandDrawingTool() {
            this.toolsManager.activateTool(AnnotationsEventsController.FREEHAND_DRAWING_TOOL);
        }

        function activatePreviewMode() {
            this.roisManager.activatePreviewMode();
        }

        function deactivatePreviewMode() {
            this.roisManager.deactivatePreviewMode();
        }

        function isPreviewModeActive() {
            return this.roisManager.previewModeActive();
        }

        function saveTemporaryFreehandShape() {
            this.roisManager.saveTemporaryFreehandPath();
        }

        function clearTemporaryFreehandShape() {
            this.roisManager.clearTemporaryFreehandPath();
        }

        function tmpFreehandPathExists() {
            if (typeof this.roisManager !== 'undefined') {
                return this.roisManager.tmpFreehandPathExists();
            }
        }

        function tmpFreehandPathValid() {
            if (typeof this.roisManager !== 'undefined') {
                return this.roisManager.tmpFreehandPathValid();
            }
        }

        function shapeUndoHistoryExists() {
            if (typeof this.roisManager !== 'undefined') {
                return this.roisManager.shapeUndoHistoryExists();
            }
        }

        function shapeRestoreHistoryExists() {
            if (typeof this.roisManager !== 'undefined') {
                return this.roisManager.shapeRedoHistoryExists();
            }
        }

        function rollbackTemporaryFreehandShape() {
            this.roisManager.rollbackFreehandPath();
        }

        function restoreTemporaryFreehandShape() {
            this.roisManager.restoreFreehandPath();
        }

        function setFreehandToolLabelPrefix(label_prefix) {
            this.roisManager.setFreehandPathLabelPrefix(label_prefix);
        }

        function deleteShape(shape_id) {
            this.roisManager.deleteShape(shape_id);
        }

        function clear() {
            this.roisManager.clear();
        }

        function deleteShapes(shapes_id) {
            this.roisManager.deleteShapes(shapes_id);
        }

        function getCanvasLabel() {
            return this.roisManager.canvas_id;
        }

        function getShapeJSON(shape_id) {
            return this.roisManager.getShapeJSON(shape_id);
        }

        function getShapeArea(shape_id) {
            return this.roisManager.getShapeDimensions(shape_id).area;
        }

        function focusOnShape(shape_id) {
            this.viewerManager.jumpToShape(shape_id, true);
        }

        function checkContainment(container_label, contained_label) {
            var container = this.roisManager.getShape(container_label);
            var contained = this.roisManager.getShape(contained_label);
            return (container.containsShape(contained) || container.intersectsShape(contained));
        }

        function adaptToContainer(container_label, contained_label) {
            var container = this.roisManager.getShape(container_label);
            var contained = this.roisManager.getShape(contained_label);
            this.roisManager.intersectShapes(container, contained, false, true, true, true);
        }

        function createRulerBindings(on_switch, off_switch, output) {
            this.roisManager.bindToRuler(on_switch, off_switch, output);
        }

        function startRuler() {
            this.toolsManager.activateTool(AnnotationsEventsController.MEASURING_TOOL);
        }

        function clearRuler() {
            this.roisManager.clearRuler(true);
        }

        function tmpAreaRulerExists() {
            if (typeof this.roisManager !== 'undefined') {
                return this.roisManager.tmpAreaRulerExists();
            }
        }

        function tmpAreaRulerValid() {
            if (typeof this.roisManager !== 'undefined') {
                return this.roisManager.tmpAreaRulerValid();
            }
        }

        function areaRulerUndoHistoryExists() {
            if (typeof this.roisManager !== 'undefined') {
                return this.roisManager.areaRulerUndoHistoryExists();
            }
        }

        function areaRulerRedoHistoryExists() {
            if (typeof this.roisManager !== 'undefined') {
                return this.roisManager.areaRulerRedoHistoryExists();
            }
        }

        function createAreaRulerBindings(on_switch, output) {
            this.roisManager.bindToAreaRuler(on_switch, output);
        }

        function bindAreaRulerToShape(shape_id) {
            this.roisManager.bindAreaRulerToShape(shape_id);
        }

        function startAreaRulerTool() {
            this.toolsManager.activateTool(AnnotationsEventsController.AREA_MEASURING_TOOL);
        }

        function activateAreaRulerPreviewMode() {
            this.roisManager.activateAreaRulerPreviewMode();
        }

        function deactivateAreaRulerPreviewMode() {
            this.roisManager.deactivateAreaRulerPreviewMode();
        }

        function isAreaRulerPreviewModeActive() {
            return this.roisManager.areaRulerPreviewModeActive();
        }

        function rollbackAreaRuler() {
            this.roisManager.rollbackAreaRulerPath();
        }

        function restoreAreaRuler() {
            this.roisManager.restoreAreaRulerPath();
        }

        function saveAreaRuler() {
            this.roisManager.saveAreaRuler();
        }

        function clearAreaRuler() {
            this.roisManager.clearAreaRuler(false);
        }

        function getAreaCoverage(shape_1_label, shape_2_label) {
            var shape_1 = this.roisManager.getShape(shape_1_label);
            var shape_2 = this.roisManager.getShape(shape_2_label);
            return Number(shape_1.getCoveragePercentage(shape_2).toFixed(2));
        }

        function setShapeStrokeColor(shape_id, color, alpha) {
            var shape = this.roisManager.getShape(shape_id);
            shape.setStrokeColor(color, alpha);
        }
    }

    SlidesSequenceViewerService.$inject = ['$log'];

    function SlidesSequenceViewerService($log) {
        var SlidesSequenceViewerService = {
            initialize: initialize,
            registerViewer: registerViewer,
            getCurrentPage: getCurrentPage,
            getPagesCount: getPagesCount,
            goToPage: goToPage,
            getNaviItemID: getNaviItemID
        };

        return SlidesSequenceViewerService;

        function initialize() {
            this.slidesSetViewers = {};
        }

        function registerViewer(label, viewer) {
            this.slidesSetViewers[label] = viewer;
        }

        function getCurrentPage(viewer_label) {
            return this.slidesSetViewers[viewer_label].getCurrentPage();
        }

        function getPagesCount(viewer_label) {
            return this.slidesSetViewers[viewer_label].getPagesCount();
        }

        function goToPage(viewer_label, page) {
            return this.slidesSetViewers[viewer_label].goToPage(page);
        }

        function getNaviItemID(panel_id, item_label) {
            return panel_id + '_' + item_label;
        }
    }
})();