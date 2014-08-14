AcsApp.directive('scroller', function ($window) {
    return {
        restrict: 'A',
        scope: {
            onScrollBottom: "&",
            scrollerActive: "="
        },
        link: function (scope, elem, attrs) {
            rawElement = elem[0];
            angular.element($window).bind('scroll', function () {
                var documentHeight = $(document).height() || document.body.scrollHeight;
                var bottomPosition = $window.innerHeight + $window.pageYOffset;
                var bufferSpace = 240;
                if( documentHeight - bottomPosition < bufferSpace && scope.scrollerActive ) {
                    scope.$apply(scope.onScrollBottom);
                }
            });
        }
    };
});