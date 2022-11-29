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
        .module('promort.clinical_annotations_manager.directives')
        .directive('newSliceAnnotationForm', newSliceAnnotationForm)
        .directive('newSliceAnnotationButtons', newSliceAnnotationButtons)
        .directive('showSliceAnnotationForm', showSliceAnnotationForm)
        .directive('showSliceAnnotationButtons', showSliceAnnotationButtons)
        .directive('newCoreAnnotationForm', newCoreAnnotationForm)
        .directive('newCoreAnnotationButtons', newCoreAnnotationButtons)
        .directive('showCoreAnnotationForm', showCoreAnnotationForm)
        .directive('showCoreAnnotationButtons', showCoreAnnotationButtons)
        .directive('newFocusRegionAnnotationForm', newFocusRegionAnnotationForm)
        .directive('newFocusRegionAnnotationButtons', newFocusRegionAnnotationButtons)
        .directive('showFocusRegionAnnotationController', showFocusRegionAnnotationForm)
        .directive('showFocusRegionAnnotationButtons', showFocusRegionAnnotationButtons)
        .directive('newGleasonPatternAnnotationForm', newGleasonPatternAnnotationForm)
        .directive('newGleasonPatternAnnotationButtons', newGleasonPatternAnnotationButtons)
        .directive('showGleasonPatternAnnotationForm', showGleasonPatternAnnotationForm);

    function newSliceAnnotationForm() {
        var directive = {
            replace: true,
            restrict: 'E',
            templateUrl: '/static/templates/clinical_annotations_manager/slice_annotation.html',
            controller: 'NewSliceAnnotationController',
            controllerAs: 'cmCtrl'
        };
        return directive;
    }

    function newSliceAnnotationButtons() {
        var directive = {
            replace: true,
            restrict: 'E',
            templateUrl: '/static/templates/clinical_annotations_manager/buttons_ctrl_group.html',
            controller: 'NewSliceAnnotationController',
            controllerAs: 'cmCtrl'
        };
        return directive;
    }

    function showSliceAnnotationForm() {
        var directive = {
            replace: true,
            restricted: 'E',
            templateUrl: '/static/templates/clinical_annotations_manager/slice_annotation.html',
            controller: 'ShowSliceAnnotationController',
            controllerAs: 'cmCtrl'
        };
        return directive;
    }

    function showSliceAnnotationButtons() {
        var directive = {
            replace: true,
            restrict: 'E',
            templateUrl: '/static/templates/clinical_annotations_manager/buttons_ctrl_group.html',
            controller: 'ShowSliceAnnotationController',
            controllerAs: 'cmCtrl'
        };
        return directive;
    }

    function newCoreAnnotationForm() {
        var directive = {
            replace: true,
            restrict: 'E',
            templateUrl: '/static/templates/clinical_annotations_manager/core_annotation.html',
            controller: 'NewCoreAnnotationController',
            controllerAs: 'cmCtrl',
            link: function(scope, element, attrs) {
                $(".selectpicker").selectpicker({
                    style: 'btn-default input-group-addon prm-selectpicker'
                });
            }
        };
        return directive;
    }

    function newCoreAnnotationButtons() {
        var directive = {
            replace: true,
            restrict: 'E',
            templateUrl: '/static/templates/clinical_annotations_manager/buttons_ctrl_group.html',
            controller: 'NewCoreAnnotationController',
            controllerAs: 'cmCtrl'
        };
        return directive;
    }

    function showCoreAnnotationForm() {
        var directive = {
            replace: true,
            restrict: 'E',
            templateUrl: '/static/templates/clinical_annotations_manager/core_annotation.html',
            controller: 'ShowCoreAnnotationController',
            controllerAs: 'cmCtrl',
            link: function(scope, element, attrs) {
                $(".selectpicker").selectpicker({
                    style: 'btn-default input-group-addon prm-selectpicker'
                });
            }
        };
        return directive;
    }

    function showCoreAnnotationButtons() {
        var directive = {
            replace: true,
            restrict: 'E',
            templateUrl: '/static/templates/clinical_annotations_manager/buttons_ctrl_group.html',
            controller: 'ShowCoreAnnotationController',
            controllerAs: 'cmCtrl'
        };
        return directive;
    }

    function newFocusRegionAnnotationForm() {
        var directive = {
            replace: true,
            restrict: 'E',
            templateUrl: '/static/templates/clinical_annotations_manager/focus_region_annotation.html',
            controller: 'NewFocusRegionAnnotationController',
            controllerAs: 'cmCtrl',
            link: function(scope, element, attrs) {
                $(".selectpicker").selectpicker({
                    style: 'btn-default input-group-addon prm-selectpicker'
                });
                $("#spinner").TouchSpin({
                    min: 0,
                    step: 1,
                    booster: false,
                    mousewheel: false
                });
                $("#g4_spinner").TouchSpin({
                    min: 0,
                    step: 1,
                    booster: false,
                    mousewheel: false
                });
            }
        };
        return directive;
    }

    function newFocusRegionAnnotationButtons() {
        var directive = {
            replace: true,
            restrict: 'E',
            templateUrl: '/static/templates/clinical_annotations_manager/buttons_ctrl_group.html',
            controller: 'NewFocusRegionAnnotationController',
            controllerAs: 'cmCtrl'
        };
        return directive;
    }

    function showFocusRegionAnnotationForm() {
        var directive = {
            replace: true,
            restrict: 'E',
            templateUrl: '/static/templates/clinical_annotations_manager/focus_region_annotation.html',
            controller: 'ShowFocusRegionAnnotationController',
            controllerAs: 'cmCtrl',
            link: function(scope, element, attrs) {
                $(".selectpicker").selectpicker({
                    style: 'btn-default input-group-addon prm-selectpicker'
                });
            }
        };
        return directive;
    }

    function showFocusRegionAnnotationButtons() {
        var directive = {
            replace: true,
            restrict: 'E',
            templateUrl: '/static/templates/clinical_annotations_manager/buttons_ctrl_group.html',
            controller: 'ShowFocusRegionAnnotationController',
            controllerAs: 'cmCtrl'
        };
        return directive;
    }

    function newGleasonPatternAnnotationForm() {
        var directive = {
            replace: true,
            restrict: 'E',
            templateUrl: '/static/templates/clinical_annotations_manager/gleason_pattern_annotation.html',
            controller: 'NewGleasonPatternAnnotationController',
            controllerAs: 'cmCtrl'
        };
        return directive;
    }

    function newGleasonPatternAnnotationButtons() {
        var directive = {
            replace: true,
            restrict: 'E',
            templateUrl: '/static/templates/clinical_annotations_manager/buttons_ctrl_group.html',
            controller: 'NewGleasonPatternAnnotationController',
            controllerAs: 'cmCtrl'
        };
        return directive;
    }

    function showGleasonPatternAnnotationForm() {
        var directive = {
            replace: true,
            restrict: 'E',
            templateUrl: '/static/templates/clinical_annotations_manager/gleason_pattern_annotation.html',
            controller: 'ShowGleasonPatternAnnotationController',
            controllerAs: 'cmCtrl'
        };
        return directive;
    }
})();