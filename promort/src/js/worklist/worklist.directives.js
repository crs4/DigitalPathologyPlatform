(function() {
   'use strict';

   angular
       .module('promort.worklist.directives')
       .directive('tooltipNotes', tooltipNotes);

   function tooltipNotes() {
        var directive = {
            restrict: 'A',
            link: function(scope, element, attrs) {
                $(element).hover(
                    function() {
                        $(element).tooltip('show');
                    },
                    function() {
                        $(element).tooltip('hide');
                    }
                );
            }
        };
        return directive;
   }
})();