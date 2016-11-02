(function(){
	'use strict';
	
	angular
		.module('idsApp.projects.services')
		.factory('Relationships', Relationships);

	Relationships.$inject = ['$http', 'djangoUrl'];

	function Relationships($http, djangoUrl) {
		var services = {};

		services.getRelatedEntities = function(uuid) {
			return $http.get(djangoUrl.reverse('ids_projects:project-api', [uuid]), {
				params: {'object_id': uuid}
			});
		};

		return services;
	}

})();