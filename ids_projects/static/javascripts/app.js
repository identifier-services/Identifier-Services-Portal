(function() {
	'use strict';
	
	angular.module('idsApp', [
		'idsApp.layout',
		'djng.urls'
		]);

	angular.module('idsApp').run(run);

	function run($http) {
		$http.defaults.xsrfHeaderName = 'X-CSRFToken';
		$http.defaults.xsrfCookieName = 'csrftoken';
	}

})();