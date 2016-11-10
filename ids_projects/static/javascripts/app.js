(function() {
	'use strict';
	
	angular.module('idsApp', [
		'idsApp.layout',
		'idsApp.data',
		'idsApp.datasets',
		'idsApp.probes',
		'idsApp.processes',
		'idsApp.projects',
		'idsApp.specimens',
		'djng.urls'		
		]);

	angular.module('idsApp').run(run);

	function run($http) {
		$http.defaults.xsrfHeaderName = 'X-CSRFToken';
		$http.defaults.xsrfCookieName = 'csrftoken';
	}

})();