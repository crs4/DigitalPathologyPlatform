(function () {
    'use strict';

    angular
        .module('promort.viewer.directives')
        .directive('viewerNavigationPanel', viewerNavigationPanel)
        .directive('simpleViewer', simpleViewer)
        .directive('annotationsViewer', annotationsViewer);

    function viewerNavigationPanel() {
        var directive = {
            replace: true,
            restrict: 'E',
            templateUrl: '/static/templates/viewer/navigation_panel.html'
        };
        return directive;
    }

    function simpleViewer() {
        var directive = {
            replace: true,
            controller: 'SimpleViewerController',
            controllerAs: 'svc',
            restrict: 'E',
            templateUrl: '/static/templates/viewer/simple_viewer.html',
            link: function(scope, element, attrs) {
                function setViewerHeight() {
                    var used_v_space = $("#pg_header").height() + $("#pg_footer").height()
                        + $("#index_navbar").height() + 100;

                    var available_v_space = $(window).height() - used_v_space;

                    $('#simple_viewer').height(available_v_space);
                }

                setViewerHeight();
                $(window).resize(setViewerHeight);
                $(window).bind('resize_simple_viewer', setViewerHeight);

                scope.$on('viewer.controller_initialized', function() {
                    // clean navigator div
                    $('#navi').empty();

                    var viewer_config = {
                        'showNavigator': true,
                        'showFullPageControl': false,
                        'navigatorId': 'navi',
                        'zoomInButton': 'navi_zoom_in',
                        'zoomOutButton': 'navi_zoom_out',
                        'homeButton': 'navi_home'
                    };

                    var ome_seadragon_viewer = new ViewerController(
                        'simple_viewer',
                        scope.svc.getStaticFilesURL(),
                        scope.svc.getDZIURL(),
                        viewer_config
                    );
                    ome_seadragon_viewer.buildViewer();

                    ome_seadragon_viewer.viewer.addHandler('open', function() {
                        ome_seadragon_viewer.setMinDZILevel(8);
                    });

                    var scalebar_config = {
                        'xOffset': 10,
                        'yOffset': 10,
                        'barThickness': 5,
                        'color': '#777',
                        'fontColor': '#000',
                        'backgroundColor': 'rgba(255, 255, 255, 0.5)'
                    };
                    ome_seadragon_viewer.enableScalebar(
                        scope.svc.getSlideMicronsPerPixel(), scalebar_config
                    );
                });
            }
        };
        return directive;
    }

    function annotationsViewer() {
        var directive = {
            replace: true,
            controller: 'AnnotationsViewerController',
            controllerAs: 'avc',
            restrict: 'E',
            templateUrl: '/static/templates/viewer/rois_viewer.html',
            link: function(scope, element, attrs) {
                function setViewerHeight() {
                    var used_v_space = $("#pg_header").height() + $("#pg_footer").height()
                        + $("#index_navbar").height() + 100;

                    var available_v_space = $(window).height() - used_v_space;

                    $("#rois_viewer").height(available_v_space);
                    $("#rois_viewer_containter").height(available_v_space);
                }

                setViewerHeight();
                $(window).resize(setViewerHeight);
                $(window).bind('resize_annotated_viewer', setViewerHeight);

                scope.$on('viewer.controller_initialized', function() {
                    // clean navigator div
                    $('#navi').empty();

                    var viewer_config = {
                        'showNavigator': true,
                        'showFullPageControl': false,
                        'animationTime': 0.01,
                        'navigatorId': 'navi',
                        'zoomInButton': 'navi_zoom_in',
                        'zoomOutButton': 'navi_zoom_out',
                        'homeButton': 'navi_home'
                    };
                    var ome_seadragon_viewer = new ViewerController(
                        'rois_viewer',
                        scope.avc.getStaticFilesURL(),
                        scope.avc.getDZIURL(),
                        viewer_config
                    );
                    ome_seadragon_viewer.buildViewer();

                    var scalebar_config = {
                        'xOffset': 10,
                        'yOffset': 10,
                        'barThickness': 5,
                        'color': '#777',
                        'fontColor': '#000',
                        'backgroundColor': 'rgba(255, 255, 255, 0.5)'
                    };
                    ome_seadragon_viewer.enableScalebar(
                        scope.avc.getSlideMicronsPerPixel(), scalebar_config
                    );

                    ome_seadragon_viewer.viewer.addHandler('open', function() {
                        ome_seadragon_viewer.setMinDZILevel(8);

                        var annotations_canvas = new AnnotationsController('rois_canvas');
                        annotations_canvas.buildAnnotationsCanvas(ome_seadragon_viewer);
                        ome_seadragon_viewer.addAnnotationsController(annotations_canvas, true);

                        var tools_manager = new AnnotationsEventsController(annotations_canvas);
                        // initialize polygon, freehand drawing and measuring tools
                        var shape_config = {'fill_alpha': 0.01, 'stroke_width': 40};
                        tools_manager.initializePolygonDrawingTool(shape_config);
                        tools_manager.initializeFreehandDrawingTool(shape_config);
                        tools_manager.initializeMeasuringTool();

                        console.log('Registering components');
                        scope.avc.registerComponents(ome_seadragon_viewer,
                            annotations_canvas, tools_manager);
                    });
                });
            }
        };
        return directive;
    }
})();