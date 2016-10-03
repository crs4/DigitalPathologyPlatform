(function () {
    'use strict';

    angular
        .module('promort.viewer.services')
        .factory('ViewerService', ViewerService)
        .factory('AnnotationsViewerService', AnnotationsViewerService);

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
            extendPolygonConfig: extendPolygonConfig,
            startPolygonsTool: startPolygonsTool,
            pausePolygonTool: pausePolygonTool,
            saveTemporaryPolygon: saveTemporaryPolygon,
            clearTemporaryPolygon: clearTemporaryPolygon,
            deleteShape: deleteShape,
            clear: clear,
            deleteShapes: deleteShapes,
            getCanvasLabel: getCanvasLabel,
            getShapeJSON: getShapeJSON
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

        }

        function extendPolygonConfig(polygon_config) {
            this.roisManager.extendPolygonConfig(polygon_config);
        }

        function startPolygonsTool() {
            this.toolsManager.activateTool(AnnotationsEventsController.POLYGON_DRAWING_TOOL);
        }

        function pausePolygonTool() {
            this.roisManager.disableMouseEvents();
        }

        function saveTemporaryPolygon(label_prefix) {
            console.log('Saving temporary polygon');
            this.roisManager.saveTemporaryPolygon(label_prefix);
        }

        function clearTemporaryPolygon() {
            this.roisManager.clearTemporaryPolygon();
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
    }
})();