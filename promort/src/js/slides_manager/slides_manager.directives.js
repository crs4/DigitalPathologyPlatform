(function () {
    'use strict';

    angular
        .module('promort.slides_manager.directives')
        .directive('simpleViewer', simpleViewer);
    
    function simpleViewer() {
        var directive = {
            replace: true,
            controller: 'SimpleViewerController',
            controllerAs: 'svc',
            restrict: 'E',
            templateUrl: '/static/templates/viewer/simple_viewer.html',
            link: function(scope, element, attrs) {
                function setViewerHeight() {
                    // set viewer's height to maximize page's vertical space
                    var used_v_space = $('#index_navbar').height() + $('#qc_header').height();
                    var $vcont = $('#viewer_container');
                    var bottom_border = parseInt($vcont.css('marginBottom')) +
                            parseInt($vcont.css('marginTop')) +
                            parseInt($vcont.css('paddingTop')) +
                            parseInt($vcont.css('paddingBottom')) + 20;
                    console.log(bottom_border);

                    var available_v_space = $(window).height() - (used_v_space + bottom_border);
                    var $qfc = $('#qc_form_container');
                    if (available_v_space < $qfc.height()) {
                        available_v_space = $qfc.height();
                    }

                    $('#simple_viewer').height(available_v_space);
                }

                setViewerHeight();
                $(window).resize(setViewerHeight);
                $('#goodQuality').click(setViewerHeight);
                $('#badQuality').click(setViewerHeight);

                scope.$on('viewer.controller_initialized', function() {
                    var viewer_config = {
                        'showNavigator': true,
                        'showFullPageControl': false
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
                        'barThickness' :5,
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
})();