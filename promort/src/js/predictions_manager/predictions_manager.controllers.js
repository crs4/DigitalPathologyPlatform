/*
 * Copyright (c) 2021, CRS4
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
        .module('promort.predictions_manager.controllers')
        .controller('PredictionsManagerController', PredictionsManagerController);

    PredictionsManagerController.$inject = ['$scope', '$routeParams', '$location', '$log',
        'PredictionsManagerService', 'CurrentPredictionDetailsService', 'HeatmapViewerService'];

    function PredictionsManagerController($scope, $routerParams, $location, $log, PredictionsManagerService,
                                          CurrentPredictionDetailsService, HeatmapViewerService) {
        var vm = this;
        vm.prediction_review_label = undefined;
        vm.slide_id = undefined;
        vm.prediction_id = undefined;
        vm.overlay_palette = undefined;
        vm.overlay_opacity = undefined;
        vm.overlay_threshold = undefined;

        vm.oo_percentage = undefined;
        vm.ot_percentage = undefined;
        vm.threshold_update = undefined;

        vm.updateOverlayOpacity = updateOverlayOpacity;
        vm.updateOverlayThreshold = updateOverlayThreshold;
        vm.updateOverlayThresholdPercentage = updateOverlayThresholdPercentage;
        vm.updateOverlayPalette = updateOverlayPalette;
        vm.isThresholdUpdate = isThresholdUpdate;

        activate();

        function activate() {
            vm.prediction_review_label = $routerParams.label;
            
            vm.slide_id = CurrentPredictionDetailsService.getSlideId();
            vm.prediction_id = CurrentPredictionDetailsService.getPredictionId();

            vm.overlay_palette = 'Greens_9';
            vm.overlay_opacity = 0.5;
            vm.overlay_threshold = 0;

            vm.oo_percentage = Math.floor(vm.overlay_opacity * 100);
            vm.ot_percentage = Math.floor(vm.overlay_threshold * 100);
            vm.threshold_update = false;
        }

        function updateOverlayOpacity() {
            HeatmapViewerService.setOverlayOpacity(vm.overlay_opacity);
            vm.oo_percentage = Math.floor(vm.overlay_opacity * 100);
        }

        function updateOverlayThreshold() {
            HeatmapViewerService.setOverlay(vm.overlay_palette, vm.overlay_threshold);
            vm.threshold_update = false;
        }

        function updateOverlayThresholdPercentage() {
            vm.ot_percentage = Math.floor(vm.overlay_threshold * 100);
            vm.threshold_update = true;
        }

        function updateOverlayPalette() {
            console.log('Current overlay palette is: ' + vm.overlay_palette);
            HeatmapViewerService.setOverlay(vm.overlay_palette, vm.overlay_threshold);
        }

        function isThresholdUpdate() {
            return vm.threshold_update;
        }
    }
})();