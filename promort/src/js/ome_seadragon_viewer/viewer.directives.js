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
        .module('promort.viewer.directives')
        .directive('viewerNavigationPanel', viewerNavigationPanel)
        .directive('miniViewerNavigationPanel', miniViewerNavigationPanel)
        .directive('simpleViewer', simpleViewer)
        .directive('simpleHeatmapViewer', simpleHeatmapViewer)
        .directive('roiAnnotationsViewer', roiAnnotationsViewer)
        .directive('clinicalAnnotationsViewer', clinicalAnnotationsViewer)
        .directive('slidesSequenceViewer', slidesSequenceViewer);

    function viewerNavigationPanel() {
        var directive = {
            replace: true,
            restrict: 'E',
            templateUrl: '/static/templates/viewer/navigation_panel.html'
        };
        return directive;
    }

    function miniViewerNavigationPanel() {
        var directive = {
            replace: true,
            restrict: 'E',
            templateUrl: '/static/templates/viewer/navigation_panel_mini.html',
            controller: 'MiniViewerNavigationController',
            controllerAs: 'mvnCtrl',
            scope: {
                'viewerPanelId': '@'
            }
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
                        ome_seadragon_viewer.setMinDZILevel(11);
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

    function simpleHeatmapViewer() {
        var directive = {
            replace: true,
            controller: 'SimpleHeatmapViewerController',
            controllerAs: 'shvc',
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
                        scope.shvc.getStaticFilesURL(),
                        scope.shvc.getDZIURL(),
                        viewer_config
                    );
                    ome_seadragon_viewer.buildViewer();

                    ome_seadragon_viewer.viewer.world.addHandler('add-item', function(data) {
                        scope.$broadcast('viewer.tiledimage.added');

                        data.item.addHandler('fully-loaded-change', function(data) {
                            if (data.fullyLoaded === true) {
                                scope.$broadcast('viewer.tiledimage.loaded');
                            }
                        });
                    });

                    ome_seadragon_viewer.viewer.addHandler('open', function(data) {
                        ome_seadragon_viewer.setMinDZILevel(8);

                        ome_seadragon_viewer.initOverlaysLayer(
                            {
                                'green': scope.shvc.getDatasetDZIURL('Greens_9')
                            }, 0.5
                        );
                        scope.shvc.registerComponents(ome_seadragon_viewer, scope.shvc.dataset_dzi_url);
                        scope.shvc.setOverlayOpacity(0.5);

                        ome_seadragon_viewer.activateOverlay('green');
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
                        scope.shvc.getSlideMicronsPerPixel(), scalebar_config
                    );
                });
            }
        };
        return directive;
    }

    function roiAnnotationsViewer() {
        var directive = {
            replace: true,
            controller: 'AnnotationsViewerController',
            controllerAs: 'avc',
            restrict: 'E',
            templateUrl: '/static/templates/viewer/rois_viewer.html',
            link: function(scope, element, attrs) {
                function setViewerHeight() {
                    var used_v_space = $("#pg_header").height() + $("#pg_footer").height()
                        + $("#index_navbar").height() + $("#heatmap_controls").height() + 115;

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

                    ome_seadragon_viewer.viewer.world.addHandler('add-item', function(data) {
                        scope.$broadcast('viewer.tiledimage.added');

                        data.item.addHandler('fully-loaded-change', function(data) {
                            if (data.fullyLoaded === true) {
                                scope.$broadcast('viewer.tiledimage.loaded');
                            }
                        });
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
                        scope.avc.getSlideMicronsPerPixel(), scalebar_config
                    );

                    ome_seadragon_viewer.viewer.addHandler('open', function() {
                        ome_seadragon_viewer.setMinDZILevel(8);

                        if(scope.avc.enableHeatmapLayer()) {
                            scope.avc.registerHeatmapComponents(ome_seadragon_viewer);
                            ome_seadragon_viewer.initOverlaysLayer(
                                {
                                    'red': scope.avc.getDatasetDZIURL('Reds_9')
                                }, 0.5
                            );
                            scope.avc.setOverlayOpacity(0.5);

                            ome_seadragon_viewer.activateOverlay('red', '0.5');
                        }

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
                            annotations_canvas, tools_manager, false);
                    });
                });
            }
        };
        return directive;
    }

    function clinicalAnnotationsViewer() {
        var directive = {
            replace:true,
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
                        //initialize area measuring tools
                        var shape_config = {
                            fill_alpha: 0.2,
                            fill_color: '#ff0000',
                            stroke_width: 5,
                            stroke_color: '#ff0000'
                        };
                        tools_manager.initializeAreaMeasuringTool(shape_config);
                        // initialize cellular count helper tool
                        var helper_box_config = {
                            fill_alpha: 0.01,
                            stroke_width: 5,
                            stroke_color: '#0000ff'
                        };
                        // box size in microns
                        var box_size = 50;
                        tools_manager.initializeCellularCountHelperTool(box_size, helper_box_config);
                        tools_manager.bindControllers('cell_counter_activate',
                            'cell_counter_save');
                        tools_manager.bindControllers('g4_cell_counter_activate',
                            'g4_cell_counter_save');

                        scope.avc.registerComponents(ome_seadragon_viewer,
                            annotations_canvas, tools_manager, true);
                    });
                });
            }
        };
        return directive;
    }

    function slidesSequenceViewer() {
        var directive = {
            replace: true,
            controller: 'SlidesSequenceViewerController',
            controllerAs: 'ssvc',
            restrict: 'E',
            templateUrl: '/static/templates/viewer/sequence_viewer.html',
            scope: {
                svWaitForIt: '@',
                viewerReady: '@',
                viewerIdentifier: '@',
                compactViewer: '@'
            },
            link: function(scope, element, attrs) {
                scope.$on(scope.viewerReady, function(event, args) {
                    if (!scope.ssvc.enableCompactViewer()) {
                        function setViewerHeight() {
                            var used_v_space = $("#pg_header").height() + $("#pg_footer").height()
                                + $("#index_navbar").height() + 200;
        
                            var available_v_space = $(window).height() - used_v_space;
                            
                            console.log(scope.ssvc.getViewerID());
                            $('#' + scope.ssvc.getViewerID()).height(available_v_space);
                        }
        
                        setViewerHeight();
                        $(window).resize(setViewerHeight);
                        $(window).bind('resize_simple_viewer', setViewerHeight);
                    }

                    var viewer_config = {
                        'showNavigator': false,
                        'showFullPageControl': false,
                        'showSequenceControl': false,
                        'zoomInButton': scope.ssvc.getNaviItemID('navi_zoom_in'),
                        'zoomOutButton': scope.ssvc.getNaviItemID('navi_zoom_out'),
                        'homeButton': scope.ssvc.getNaviItemID('navi_home')
                    };

                    var ome_seadragon_viewer = new ViewerController(
                        args.viewer_label,
                        scope.ssvc.getStaticFilesURL(),
                        scope.ssvc.getDZIURLs(),
                        viewer_config
                    );
                    ome_seadragon_viewer.buildViewer();

                    ome_seadragon_viewer.viewer.addHandler('open', function() {
                        ome_seadragon_viewer.setMinDZILevel(8);
                    });

                    // Register viewer in SlidesSetService
                    scope.ssvc.registerViewer(ome_seadragon_viewer);
                });
            }
        };
        return directive;
    }
})();