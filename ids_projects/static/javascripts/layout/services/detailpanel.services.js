(function(){
	'use strict';
	
	angular
		.module('idsApp.layout.services')
		.factory('Details', Details);

	Details.$inject = ['$http', 'djangoUrl'];

	function Details($http, djangoUrl) {
		var services = {};

		services.get = function(uuid) {
			return $http.get(djangoUrl.reverse('ids_projects:entity-detail-api', [uuid]), {
				params: {'object_id': uuid}
			});
		};

		return services;
	}

})();