/* jshint node: true */

module.exports = function(grunt) {

    var sources = [
        "promort/src/js/promort.js",
        "promort/src/js/promort.config.js",
        "promort/src/js/promort.routes.js",
        "promort/src/js/utils/utils.js",
        "promort/src/js/authentication/authentication.module.js",
        "promort/src/js/authentication/authentication.services.js",
        "promort/src/js/authentication/authentication.controllers.js",
        "promort/src/js/window_manager/window_manager.module.js",
        "promort/src/js/window_manager/window_manager.controllers.js",
        "promort/src/js/layout/layout.modules.js",
        "promort/src/js/layout/layout.controllers.js",
        "promort/src/js/worklist/worklist.module.js",
        "promort/src/js/worklist/worklist.services.js",
        "promort/src/js/worklist/worklist.controllers.js",
        "promort/src/js/worklist/worklist.directives.js",
        "promort/src/js/slides_manager/slides_manager.module.js",
        "promort/src/js/slides_manager/slides_manager.services.js",
        "promort/src/js/slides_manager/slides_manager.controllers.js",
        "promort/src/js/slides_manager/slides_manager.directives.js",
        "promort/src/js/ome_seadragon_viewer/viewer.module.js",
        "promort/src/js/ome_seadragon_viewer/viewer.services.js",
        "promort/src/js/ome_seadragon_viewer/viewer.controllers.js",
        "promort/src/js/ome_seadragon_viewer/viewer.directives.js",
        "promort/src/js/user_report/user_report.module.js",
        "promort/src/js/user_report/user_report.services.js",
        "promort/src/js/user_report/user_report.controllers.js",
        "promort/src/js/rois_manager/rois_manager.module.js",
        "promort/src/js/rois_manager/rois_manager.services.js",
        "promort/src/js/rois_manager/rois_manager.controllers.js",
        "promort/src/js/rois_manager/rois_manager.directives.js",
        "promort/src/js/clinical_annotations_manager/clinical_annotations_manager.module.js",
        "promort/src/js/clinical_annotations_manager/clinical_annotations_manager.services.js",
        "promort/src/js/clinical_annotations_manager/clinical_annotations_manager.controllers.js",
        "promort/src/js/clinical_annotations_manager/clinical_annotations_manager.directives.js",
        "promort/src/js/ome_seadragon_tools/cell_count_guide.js",
        "promort/src/js/questionnaires_manager/questionnaires_manager.module.js",
        "promort/src/js/questionnaires_manager/questionnaires_manager.services.js",
        "promort/src/js/questionnaires_manager/questionnaires_manager.controllers.js",
        "promort/src/js/questionnaires_manager/questionnaires_manager.directives.js",
        "promort/src/js/shared_datasets_manager/shared_datasets_manager.module.js",
        "promort/src/js/shared_datasets_manager/shared_datasets_manager.services.js",
        "promort/src/js/shared_datasets_manager/shared_datasets_manager.controllers.js",
        "promort/src/js/predictions_manager/predictions_manager.module.js",
        "promort/src/js/predictions_manager/predictions_manager.services.js",
        "promort/src/js/predictions_manager/predictions_manager.controllers.js",
        "promort/src/js/predictions_manager/predictions_manager.directives.js"
    ];

    grunt.initConfig({
        clean: {
            dist: [
                "build/js/promort.js",
                "promort/static_src/js/promort.min.js"
            ]
        },
        concat: {
            options: {
                banner: "//! Built on <%= grunt.template.today('yyyy-mm-dd') %>\n" +
                    "//! GPL License.\n\n" +
                    "//!  DO NOT EDIT THIS FILE! - Edit under src/js/*.js\n\n",
                process: true,
                stripBanners: true
            },
            dist: {
                src:  [ "<banner>" ].concat(sources),
                dest: "build/js/promort.js"
            }
        },
        uglify: {
            options: {
                mangle: true
            },
            my_target: {
                files: {
                   "promort/static_src/js/promort.min.js" : ["build/js/promort.js"]
                }
            }
        }
    });

    // Load tasks
    grunt.loadNpmTasks('grunt-contrib-clean');
    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-uglify');

    // Register tasks
    grunt.registerTask('default', [
        'clean', 'concat', 'uglify'
    ]);

};