(function () {
    'use strict';
    
    angular
        .module('promort.worklist.controllers')
        .controller('WorkListController', WorkListController)
        .controller('ROIsAnnotationController', ROIsAnnotationController)
        .controller('ClinicalAnnotationController', ClinicalAnnotationController);
    
    WorkListController.$inject = ['$scope', 'Authentication', 'WorkListService'];
    
    function WorkListController($scope, Authentication, WorkListService) {
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
            } else {
                return undefined;
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
                return 'worklist/rois_annotations/' + annotation.label;
            } else if (vm.isClinicalAnnotation(annotation)) {
                return 'worklist/clinical_annotations/' + annotation.label;
            }
        }
        
        function startROIsAnnotation(annotation) {
            WorkListService.startROIsAnnotation(annotation.label);
        }

        function closeROIsAnnotation(annotation) {
            WorkListService.closeROIsAnnotation(annotation.label);
        }

        function startClinicalAnnotation(annotation) {
            WorkListService.startClinicalAnnotation(annotation.label);
        }

        function closeClinicalAnnotation(annotation) {
            WorkListService.closeClinicalAnnotation(annotation.label);
        }
    }
    
    ROIsAnnotationController.$inject = ['$scope', '$routeParams', '$location', 'ROIsAnnotationStepService',
        'CurrentSlideDetailsService', 'CurrentAnnotationStepsDetailsService'];

    function ROIsAnnotationController($scope, $routeParams, $location, ROIsAnnotationStepService,
                                      CurrentSlideDetailsService, CurrentAnnotationStepsDetailsService) {
        var vm = this;
        vm.annotationSteps = [];
        vm.label = undefined;
        vm.annotationStepPending = annotationStepPending;
        vm.annotationStepInProgress = annotationStepInProgress;
        vm.annotationStepCompleted = annotationStepCompleted;
        vm.startAnnotation = startAnnotation;

        activate();

        function activate() {
            vm.label = $routeParams.label;
            ROIsAnnotationStepService.get(vm.label)
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

        function startAnnotation(annotationStep) {
            CurrentAnnotationStepsDetailsService.setROIsAnnotationStepLabel(annotationStep.label);

            CurrentSlideDetailsService.getSlideByAnnotationStep(annotationStep.label, 'ROIS_ANNOTATION')
                .then(getSlideByAnnotationStepSuccessFn, getSlideByAnnotationStepErrorFn);

            function getSlideByAnnotationStepSuccessFn(response) {
                CurrentSlideDetailsService.registerCurrentSlide(
                    response.data.slide.id, response.data.slide.case
                );
                $location.url('worklist/' + annotationStep.label + '/quality_control');
            }

            function getSlideByAnnotationStepErrorFn(response) {
                console.log(response.error);
                $location.url('404');
            }
        }
    }

    ClinicalAnnotationController.$inject = ['$scope', '$routeParams', '$location', 'ClinicalAnnotationStepService',
        'CurrentSlideDetailsService', 'CurrentAnnotationStepsDetailsService'];

    function ClinicalAnnotationController($scope, $routeParams, $location, ClinicalAnnotationStepService,
                                          CurrentSlideDetailsService, CurrentAnnotationStepsDetailsService) {
        var vm = this;
        vm.annotationSteps = [];
        vm.label = undefined;
        vm.annotationStepPending = annotationStepPending;
        vm.annotationStepInProgress = annotationStepInProgress;
        vm.annotationStepCompleted = annotationStepCompleted;
        vm.getAnnotationStepLink = getAnnotationStepLink;
        vm._goToAnnotationStep = _goToAnnotationStep;
        vm.startAnnotationStep = startAnnotationStep;
        vm.continueAnnotationStep = continueAnnotationStep;

        activate();

        function activate() {
            vm.label = $routeParams.label;
            ClinicalAnnotationStepService.get(vm.label)
                .then(AnnotationStepSuccessFn, AnnotationStepErrorFn);

            function AnnotationStepSuccessFn(response) {
                vm.annotationSteps = response.data;
            }

            function AnnotationStepErrorFn(response) {
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
            return 'worklist/' + annotationStep.label + '/annotations_manager';
        }

        function _goToAnnotationStep(annotationStep) {
            CurrentAnnotationStepsDetailsService.findROIsAnnotationStepLabelByClinicalStep(annotationStep.label)
                .then(findROIsAnnotationLabelSuccessFn, findROIsAnnotationLabelErrorFn);

            function findROIsAnnotationLabelSuccessFn(response) {
                CurrentAnnotationStepsDetailsService.setROIsAnnotationStepLabel(response.data.rois_review_step_label);
                CurrentAnnotationStepsDetailsService.setClinicalAnnotationStepLabel(annotationStep.label);

                CurrentSlideDetailsService.getSlideByAnnotationStep(annotationStep.label, 'CLINICAL_ANNOTATION')
                    .then(getSlideByAnnotationStepSuccessFn, getSlideByAnnotationStepErrorFn);

                function getSlideByAnnotationStepSuccessFn(response) {
                    console.log(response.data);
                    CurrentSlideDetailsService.registerCurrentSlide(
                        response.data.slide, response.data.case
                    );
                    var url = vm.getAnnotationStepLink(annotationStep);
                    $location.url(url);
                }

            function getSlideByAnnotationStepErrorFn(response) {
                console.log(response.error);
                $location.url('404');
            }
            }

            function findROIsAnnotationLabelErrorFn(response) {
                console.error('Cannot load slide info');
                console.error(response);
            }
        }

        function startAnnotationStep(annotationStep) {
            ClinicalAnnotationStepService.startAnnotationStep(annotationStep.label);
            vm._goToAnnotationStep(annotationStep);
        }

        function continueAnnotationStep(annotationStep) {
            vm._goToAnnotationStep(annotationStep);
        }
    }
})();