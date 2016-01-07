'use strict'

angular
    .module('MyApp', ['ngResource', 'ngMessages', 'ngAnimate', 'ui.bootstrap', 'toastr', 'ui.router', 'satellizer'])
    .config(function($stateProvider, $urlRouterProvider, $authProvider, SatellizerConfig) {
        console.log("app config");

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
            .state('login',{ // not using this state right now
                url: '/login',
                controller: 'LoginCtrl',
                templateUrl: 'partials/login.html',
                resolve: {
                    skipIfLoggedIn: skipIfLoggedIn
                }
            })
            .state('logout',{ // not using this state right now
                url: '/logout',
                controller: 'LogoutCtrl',
                template: null,
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
                //$location.path('/login');
                $location.path('/');
            }
            return deferred.promise;
        }
    })
    .run(function($log, $http) {
        //$log.debug("app run");
        console.log("app run");

        $http.get('/auth/iplant/config').then(function(result) {
            $log.debug(result);
        });
    })
    .directive('gravatar', function() {
        console.log("Gravatar directive");

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
            template: '<img class="gravatar-nav" alt="{{ name }}" height="{{ height }}"  width="{{ width }}" src="https://secure.gravatar.com/avatar/{{ emailHash }}.jpg?s={{ width }}&d={{ defaultImage }}">'
        };
    })
    .factory('Account', function($http) {
        console.log("Account factory");

        return {
            getProfile: function() {
                return $http.get('/api/me');
            },
            updateProfile: function(profileData) {
                return $http.put('/api/me', profileData);
            }
        };
    })/*
    .factory('Session', function() {
        console.log("Session factory");

        var Session = {
            data: {'key':'value'},
            updateSession: function(p) {
                console.debug(p);
                Session.data['firstName'] = p['firstname'];
                Session.data['lastName'] = p['lastname'];
                Session.data['username'] = p['username'];
                Session.data['email'] = p['email'];
                Session.data['gravatarHash'] = p['gravatar_hash'];
            }
        }
        return Session;
    })*/
    .controller('HomeCtrl', function($scope, $http) {
        console.log("Home controller");

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
        // so i'm not actually using this controller at the moment
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
                    if (provider == 'twitch')
                        provider = 'iPlant'
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
        // not using this controller, fyi
    })
    .controller('ProfileCtrl', function($scope, $auth, toastr, Account) {
        /*
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
        */
    })
    .controller('LogoutCtrl', function($location, $auth, toastr) {
        // not using this right now
        if (!$auth.isAuthenticated()) { return; }
        $auth.logout()
            .then(function() {
                toastr.info('You have been logged out');
                $location.path('/');
            });
        // not using this right now
    })
    .controller('NavbarCtrl', function($scope, $auth, $location, toastr) {
        console.log("NavBar controller");

        /*
        if ($auth.isAuthenticated()) {
            Session.updateSession($auth.Payload);
        };
        */
        $scope.isAuthenticated = function() {
            return $auth.isAuthenticated();
        };/*
        $scope.session = function() {
            return Session;
        };*/
        $scope.authenticate = function(provider) {
            $auth.authenticate(provider)
                .then(function() {
                    if (provider == 'twitch')
                        provider = 'iPlant'
                    toastr.success('You have successfully signed in with ' + provider + '!');

                    //Session.updateSession($auth.Payload);

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
        $scope.firstName = function() {
            if (!$auth.isAuthenticated()) { return; }
            return $auth.getPayload()['firstname'];
        };
        $scope.lastName = function() {
            if (!$auth.isAuthenticated()) { return; }
            return $auth.getPayload()['lastname'];
        };
        $scope.username = function() {
            if (!$auth.isAuthenticated()) { return; }
            return $auth.getPayload()['username'];
        };
        $scope.email = function() {
            if (!$auth.isAuthenticated()) { return; }
            return $auth.getPayload()['email'];
        };
        $scope.gravatarHash = function() {
            if (!$auth.isAuthenticated()) { return; }
            return $auth.getPayload()['gravatar_hash'];
        }
    });
