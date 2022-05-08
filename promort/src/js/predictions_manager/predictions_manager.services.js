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
        .module('promort.predictions_manager.services')
        .factory('CurrentPredictionDetailsService', CurrentPredictionDetailsService)
        .factory('PredictionsManagerService', PredictionsManagerService);

    CurrentPredictionDetailsService.$inject = ['$http', '$log'];

    function CurrentPredictionDetailsService($http, $log) {
        var predictionID = undefined;
        var slideID = undefined;
        var caseID = undefined;

        var CurrentPredictionDetailsService = {
            getPredictionByReviewStep: getPredictionByReviewStep,
            getLatestPredictionBySlide: getLatestPredictionBySlide,
            registerCurrentPrediction: registerCurrentPrediction,
            getPredictionId: getPredictionId,
            getSlideId: getSlideId,
            getCaseId: getCaseId
        }

        return CurrentPredictionDetailsService;

        function getPredictionByReviewStep(review_step_label) {
            predictionID = undefined;
            slideID = undefined;
            caseID = undefined;

            return $http.get('api/prediction_review/' + review_step_label + '/prediction/');
        }

        function getLatestPredictionBySlide(slide_id, type) {
            predictionID = undefined;
            slideID = undefined;
            caseID = undefined;

            return $http.get('api/slides/' + slide_id + '/predictions/',
                             {'params': {'latest': true, 'type': type}});
        }

        function registerCurrentPrediction(prediction_id, slide_id, case_id) {
            predictionID = prediction_id;
            slideID = slide_id;
            caseID = case_id;
        }

        function getPredictionId() {
            return predictionID;
        }

        function getSlideId() {
            return slideID;
        }

        function getCaseId() {
            return caseID;
        }
    }

    PredictionsManagerService.$inject = ['$http', '$log'];

    function PredictionsManagerService($http, $log) {
        var PredictionsManagerService = {
            getDetails: getDetails
        };

        return PredictionsManagerService;

        function getDetails(prediction_label) {
            return $http.get('api/prediction_review/' + prediction_label + '/');
        }
    }
})();