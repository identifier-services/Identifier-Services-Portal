angular
    .module('MyApp', ['ngResource', 'ngMessages', 'ngAnimate', 'ui.bootstrap', 'toastr', 'ui.router', 'satellizer'])
    .run(function($log) {
        $log.debug("MyApp is running...");
    })
    .config(function($stateProvider, $urlRouterProvider, $authProvider, SatellizerConfig) {
        $stateProvider
            .state('home',{
                url: '/',
                views: {
                    nav: {
                        templateUrl: 'partials/navbar.html',
                        controller: 'LoginCtrl'
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
            .state('login',{
                url: '/login',
                controller: 'LoginCtrl',
                templateUrl: 'partials/login.html',
                resolve: {
                    skipIfLoggedIn: skipIfLoggedIn
                }
            })
            .state('logout',{
                url: '/logout',
                controller: 'LogoutCtrl',
                template: null,
            })
            .state('profile',{
                url: '/profile',
                controller: 'ProfileCtrl',
                templateUrl: 'partials/profile.html',
                resolve: {
                    loginRequired: loginRequired
                }
            });

        $urlRouterProvider.otherwise('/');

        $authProvider.twitch({
          // don't know how to extend authprovider, so reusing twitch
          name: 'agave',
          //url: '/auth/agave',
          url: '/callback', // just for now
          clientId: 'rzbYuZsaiKRMcUlZWUA0wQXEpUka',
          redirectUri: 'http://localhost:5000/callback',
          authorizationEndpoint: 'https://agave.iplantc.org/oauth2/authorize',
          defaultUrlParams: ['response_type', 'client_id', 'redirect_uri'],
          requiredUrlParams: null,
          optionalUrlParams: null,
          scope: null, //("PRODUCTION",)
          scopePrefix: null,
          scopeDelimiter: '',
          state: null,
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
                $location.path('/login');
            }
            return deferred.promise;
        }
    })
    .factory('Account', function($http) {
        return {
            getProfile: function() {
                return $http.get('/api/me');
            },
            updateProfile: function(profileData) {
                return $http.put('/api/me', profileData);
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
    .controller('LoginCtrl', function($scope, $location, $auth, toastr) {
        $scope.login = function() {
            $auth.login($scope.user)
                .then(function() {
                    toastr.success('You have successfully signed in!')
                    $location.path('/');
                })
                .catch(function(error) {
                    toastr.error(error.data.message, error.status)
                });
        };
        $scope.authenticate = function(provider) {
            $auth.authenticate(provider)
                .then(function() {
                    toastr.success('You have successfully signed in with ' + provider + '!');
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
    })
    .controller('ProfileCtrl', function($scope, $auth, toastr, Account) {
        $scope.getProfile = function() {
            Account.getProfile()
                .then(function(response) {
                    $scope.user = response.data;
                })
                .catch(function(response) {
                    toastr.error(response.data.message, response.status);
                });
        };
        $scope.updateProfile = function() {
            Account.updateProfile($scope.user)
                .then(function() {
                    toastr.success('Profile has been updated');
                })
                .catch(function(response) {
                    toastr.error(response.data.message, response.status);
                });
        };
        $scope.link = function(provider) {
            $auth.link(provider)
                .then(function() {
                    toastr.success('You have successfully linked a ' + provider + ' account');
                    $scope.getProfile();
                })
                .catch(function(response) {
                    toastr.error(response.data.message, response.status);
                });
        };
        $scope.unlink = function(provider) {
            Account.unlink(provider)
                .then(function() {
                    toastr.success('You have unlinked a ' + provider + ' account');
                    $scope.getProfile();
                })
                .catch(function(response) {
                    toastr.error(response.data.message, response.status);
                });
        };

        $scope.getProfile();
    })
    .controller('LogoutCtrl', function($location, $auth, toastr) {
        if (!$auth.isAuthenticated()) { return; }
        $auth.logout()
            .then(function() {
                toastr.info('You have been logged out');
                $location.path('/');
            });
    })
    .controller('NavbarCtrl', function($scope, $auth) {
        $scope.isAuthenticated = function() {
            return $auth.isAuthenticated();
        };
    });
