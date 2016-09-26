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
            saveTemporaryShape: saveTemporaryShape,
            deleteShape: deleteShape,
            clear: clear,
            deleteShapes: deleteShapes
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

        function saveTemporaryShape() {

        }

        function deleteShape(shape_id) {

        }

        function clear() {

        }

        function deleteShapes(shapes_id) {

        }
    }
})();