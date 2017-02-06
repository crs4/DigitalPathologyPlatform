(function () {
    'use strict';
    
    angular
        .module('promort.worklist.controllers')
        .controller('WorkListController', WorkListController)
        .controller('ROIsAnnotationController', ROIsAnnotationController);
    
    WorkListController.$inject = ['$scope', '$rootScope', 'WorkListService'];
    
    function WorkListController($scope, $rootScope, WorkListService) {
        var vm = this;
        vm.pendingAnnotations = [];
        vm.annotationInProgress = annotationInProgress;
        vm.annotationClosed = annotationClosed;
        vm.checkPendingAnnotations = checkPendingAnnotations;
        vm.isROIsAnnotation = isROIsAnnotation;
        vm.isClinicalAnnotation = isClinicalAnnotation;
        vm.canStartClinicalAnnotation = canStartClinicalAnnotation;
        vm.getAnnotationLink = getAnnotationLink;
        vm.startROIsAnnotation = startROIsAnnotation;
        vm.closeROIsAnnotation = closeROIsAnnotation;
        vm.startClinicalAnnotation = startClinicalAnnotation;
        vm.closeClinicalAnnotation = closeClinicalAnnotation;
        
        activate();
        
        function activate() {
            WorkListService.get().then(workListSuccessFn, workListErrorFn);
            
            function workListSuccessFn(response) {
                vm.pendingAnnotations = response.data;
            }
            
            function workListErrorFn(response) {
                console.error(response.error);
            }
        }

        function annotationInProgress(annotation) {
            return (annotation.started && !annotation.completed );
        }

        function annotationClosed(annotation) {
            return annotation.completed;
        }

        function checkPendingAnnotations() {
            for (var i in vm.pendingAnnotations) {
                if (vm.annotationInProgress(vm.pendingAnnotations[i])) {
                    return true;
                }
            }
            return false;
        }

        function isROIsAnnotation(annotation) {
            return annotation.annotation_type === 'ROIS_ANNOTATION';
        }

        function isClinicalAnnotation(annotation) {
            return annotation.annotation_type === 'CLINICAL_ANNOTATION';
        }

        function canStartClinicalAnnotation(annotation) {
            if (vm.isClinicalAnnotation(annotation)) {
                return annotation.can_be_started;
            }
        }
        
        function getAnnotationLink(annotation) {
            // ========================================
            // disabled until all the steps for the
            // annotations workflow are completed
            // ========================================
            // if (vm.checkPendingAnnotations()) {
            //     if (!vm.annotationsInProgress(annotation)) {
            //         return '';
            //     }
            // }
            if (vm.isROIsAnnotation(annotation)) {
                return 'worklist/' + annotation.case;
            } else if (vm.isClinicalAnnotation(annotation)) {
                return 'worklist/ ' + annotation.case + '/' + annotation.rois_reviews;
            }
        }
        
        function startROIsAnnotation(annotation) {
            WorkListService.startROIsAnnotation(annotation.case, $rootScope.current_user);
        }

        function closeROIsAnnotation(annotation) {
            WorkListService.closeROIsAnnotation(annotation.case, $rootScope.current_user);
        }

        function startClinicalAnnotation(annotation) {
            WorkListService.startClinicalAnnotation(annotation.case, $rootScope.current_user,
                annotation.rois_review);
        }

        function closeClinicalAnnotation(annotation) {
            WorkListService.closeClinicalAnnotation(annotation.case, $rootScope.current_user,
                annotation.rois_review);
        }
    }
    
    ROIsAnnotationController.$inject = ['$scope', '$rootScope', '$routeParams',
        '$location', 'ROIsAnnotationStepService'];

    function ROIsAnnotationController($scope, $rootScope, $routeParams, $location,
                                      ROIsAnnotationStepService) {
        var vm = this;
        vm.annotationSteps = [];
        vm.case_id = undefined;
        vm.annotationStepPending = annotationStepPending;
        vm.annotationStepInProgress = annotationStepInProgress;
        vm.annotationStepCompleted = annotationStepCompleted;
        vm.getAnnotationStepLink = getAnnotationStepLink;
        vm.startAnnotationStep = startAnnotationStep;
        vm.closeAnnotationStep = closeAnnotationStep;

        activate();

        function activate() {
            vm.case_id = $routeParams.case;
            ROIsAnnotationStepService.get(vm.case_id)
                .then(AnnotationStepsSuccessFn, AnnotationStepsErrorFn);

            function AnnotationStepsSuccessFn(response) {
                vm.annotationSteps = response.data;
            }

            function AnnotationStepsErrorFn(response) {
                console.error(response.error);
                $location.url('404');
            }
        }

        function annotationStepPending(annotationStep) {
            return (!annotationStep.started && !annotationStep.completed);
        }

        function annotationStepInProgress(annotationStep) {
            return (annotationStep.started && !annotationStep.completed);
        }

        function annotationStepCompleted(annotationStep) {
            return annotationStep.completed;
        }

        function getAnnotationStepLink(annotationStep) {
            return 'worklist/' + vm.case_id + '/' + annotationStep.slide + '/quality_control';
        }

        function startAnnotationStep(annotationStep) {
            ROIsAnnotationStepService.startAnnotationStep(vm.case_id, $rootScope.current_user,
                annotationStep.slide);
        }

        function closeAnnotationStep(annotationStep) {
            ROIsAnnotationStepService.closeAnnotationStep(vm.case_id, $rootScope.current_user,
                annotationStep.slide);
        }
    }
})();