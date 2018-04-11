(function() {
    'use strict';
    
    angular
        .module('promort.user_report.services')
        .factory('UserReportService', UserReportService);
    
    UserReportService.$inject = ['$http', '$log'];
    
    function UserReportService($http, $log) {
        var UserReportservice = {
            send: send
        };
        
        return UserReportservice;
        
        function send(subject, message, page, browser) {
            return $http.post('api/utils/send_report/',
                {
                    page_url: page,
                    message: message,
                    subject: subject,
                    browser: browser
                }
            );
        }
    }
})();