/* jshint node: true */

module.exports = function(grunt) {

    var sources = [
        "promort/src/js/promort.js",
        "promort/src/js/promort.config.js",
        "promort/src/js/promort.routes.js",
        "promort/src/js/authentication/authentication.module.js",
        "promort/src/js/authentication/authentication.services.js",
        "promort/src/js/authentication/authentication.controllers.js",
        "promort/src/js/layout/layout.modules.js",
        "promort/src/js/layout/layout.controllers.js",
        "promort/src/js/worklist/worklist.module.js",
        "promort/src/js/worklist/worklist.services.js",
        "promort/src/js/worklist/worklist.controllers.js"
    ];

    grunt.initConfig({
        clean: {
            dist: [
                'build/js/promort.js'
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
                   "promort/static/js/promort.min.js" : ["build/js/promort.js"]
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