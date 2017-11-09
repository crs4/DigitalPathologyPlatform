(function () {
    'use strict';

    angular
        .module('promort.viewer.services')
        .factory('CurrentAnnotationStepsDetailsService', CurrentAnnotationStepsDetailsService)
        .factory('ViewerService', ViewerService)
        .factory('AnnotationsViewerService', AnnotationsViewerService);

    CurrentAnnotationStepsDetailsService.$inject = ['$http'];

    function CurrentAnnotationStepsDetailsService($http) {
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

    ViewerService.$inject = ['$http'];

    function ViewerService($http) {
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

    function AnnotationsViewerService() {
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
            saveTemporaryPolygon: saveTemporaryPolygon,
            clearTemporaryPolygon: clearTemporaryPolygon,
            startFreehandDrawingTool: startFreehandDrawingTool,
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
            clearRuler: clearRuler,
            createAreaRulerBindings: createAreaRulerBindings,
            clearAreaRuler: clearAreaRuler,
            bindAreaRulerToShape: bindAreaRulerToShape,
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
            console.log('Viewer Manager: ' + this.viewerManager);
            console.log('ROIs Manager: ' + this.roisManager);
            console.log('Tools Manager: ' + this.toolsManager);
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
        function saveTemporaryPolygon(label_prefix) {
            console.log('Saving temporary polygon');
            this.roisManager.saveTemporaryPolygon(label_prefix);
        }

        function clearTemporaryPolygon() {
            this.roisManager.clearTemporaryPolygon();
        }

        function startFreehandDrawingTool() {
            this.toolsManager.activateTool(AnnotationsEventsController.FREEHAND_DRAWING_TOOL);
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

        function clearRuler() {
            this.roisManager.clearRuler(true);
        }

        function createAreaRulerBindings(on_switch, output) {
            this.roisManager.bindToAreaRuler(on_switch, output);
        }

        function bindAreaRulerToShape(shape_id) {
            this.roisManager.bindAreaRulerToShape(shape_id);
        }

        function clearAreaRuler() {
            this.roisManager.clearAreaRuler(true);
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
})();