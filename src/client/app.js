'use strict'

angular
    .module('MyApp', ['ngResource', 'ngMessages', 'ngAnimate', 'ui.bootstrap', 'toastr', 'ui.router', 'satellizer'])
    .config(function($stateProvider, $urlRouterProvider, $authProvider, SatellizerConfig) {
        $stateProvider
            .state('home',{
                url: '/',
                views: {
                    nav: {
                        templateUrl: 'partials/navbar.html',
                        controller: 'NavbarCtrl'
                    },
                    content: {
                        templateUrl: 'partials/home.html',
                        controller: 'HomeCtrl'
                    },
                    footer: {
                        templateUrl: 'partials/footer.html'
                    },
                }
            })
            .state('profile',{
                url: '/profile',
                resolve: {
                    loginRequired: loginRequired
                },
                views: {
                    nav: {
                        templateUrl: 'partials/navbar.html',
                        controller: 'NavbarCtrl'
                    },
                    content: {
                        templateUrl: 'partials/profile.html',
                        controller: 'ProfileCtrl'
                    },
                    footer: {
                        templateUrl: 'partials/footer.html'
                    },
                }
            });

        $urlRouterProvider.otherwise('/');

        $authProvider.twitch({
            // don't know how to extend authprovider, so reusing twitch
            name: 'iplant',
            url: '/auth/iplant',
            clientId: 'p7PCPnW_fH1xQr3Udpnktfz0lika',
            redirectUri: 'http://localhost:5000/auth/iplant',
            authorizationEndpoint: 'https://agave.iplantc.org/oauth2/authorize',
            defaultUrlParams: ['response_type', 'client_id', 'redirect_uri'],
            type: '2.0',
            popupOptions: { width: 559, height: 519 },
            responseType: 'code',
            responseParams: {
                code: 'code',
                clientId: 'clientId',
                redirectUri: 'redirectUri'
            }
        });

        function skipIfLoggedIn($q, $auth) {
            var deferred = $q.defer();
            if ($auth.isAuthenticated()) {
                deferred.reject();
            } else {
                deferred.resolve();
            }
            return deferred.promise;
        }

        function loginRequired($q, $location, $auth) {
            var deferred = $q.defer();
            if ($auth.isAuthenticated()) {
                deferred.resolve();
            } else {
                $location.path('/');
            }
            return deferred.promise;
        }
    })
    .directive('gravatar', function() {
        // thank you Cheyne Wallace
        // http://www.cheynewallace.com/using-gravatar-with-angularjs/
        return {
            restrict: 'AE',
            replace: true,
            scope: {
                name: '@',
                height: '@',
                width: '@',
                emailHash: '@'
            },
            link: function(scope, el, attr) {
                //scope.defaultImage = 'https://somedomain.com/images/avatar.png';
                scope.defaultImage = 'mm';
            },
            template: '<img class="gravatar-nav-sm" alt="{{ name }}" height="{{ height }}"  width="{{ width }}" src="https://secure.gravatar.com/avatar/{{ emailHash }}.jpg?s={{ width }}&d={{ defaultImage }}">'
        };
    })
    .factory('User', function($auth) {
        return {
            firstName: function() {
                if (!$auth.isAuthenticated()) { return; }
                return $auth.getPayload()['firstname'];
            },
            lastName: function() {
                if (!$auth.isAuthenticated()) { return; }
                return $auth.getPayload()['lastname'];
            },
            username: function() {
                if (!$auth.isAuthenticated()) { return; }
                return $auth.getPayload()['username'];
            },
            email: function() {
                if (!$auth.isAuthenticated()) { return; }
                return $auth.getPayload()['email'];
            },
            gravatarHash: function() {
                if (!$auth.isAuthenticated()) { return; }
                return $auth.getPayload()['gravatar_hash'];
            },
            city: function() {
                if (!$auth.isAuthenticated()) { return; }
                return 'some town';
            }
        };
    })
    .controller('HomeCtrl', function($scope, $http) {
        $http.jsonp('https://api.github.com/repos/sahat/satellizer?callback=JSON_CALLBACK')
            .success(function(data) {
                if (data) {
                    if (data.data.stargazers_cout) {
                        $scope.stars = data.data.stargazers_cout;
                    }
                    if (data.data.forks) {
                        $scope.forks = data.data.forks;
                    }
                    if (data.data.open_issues) {
                        $scope.issues = data.data.open_issues;
                    }
                }
            });
    })
    .controller('ProfileCtrl', function($scope, $auth, toastr, User) {
        $scope.user = function() {
            return User;
        };
    })
    .controller('NavbarCtrl', function($scope, $auth, $location, toastr, User) {
        $scope.user = function() {
            return User;
        };

        $scope.isAuthenticated = function() {
            return $auth.isAuthenticated();
        };

        $scope.authenticate = function(provider) {
            $auth.authenticate(provider)
                .then(function() {
                    if (provider == 'twitch')
                        provider = 'iPlant'
                    toastr.success('You have successfully signed in with ' + provider + '!');

                    console.log("nav bar controller, authenticate, $auth.getPayload()", $auth.getPayload());

                    $location.path('/');
                })
                .catch(function(error) {
                    if (error.error) {
                        // popup error - invalid redirect_uri, pressed cancel button, etc.
                        toastr.error(error.error);
                    } else if (error.data) {
                        // HTTP response error from server
                        toastr.error(error.data.message, error.status)
                    } else {
                        toastr.error(error);
                    }
                });
        };

        $scope.logout = function() {
            if (!$auth.isAuthenticated()) { return; }
            $auth.logout()
                .then(function() {
                    toastr.info('You have been logged out');
                    $location.path('/');
            });
        };
    });
