(function(){
	'use strict';
	
	angular
		.module('idsApp.projects.services')
		.factory('Relationships', Relationships);

	Relationships.$inject = ['$http', 'djangoUrl'];

	function Relationships($http, djangoUrl) {
		var services = {};

		services.getRelatedEntities = function(name, uuid, offset) {
			return $http.get(djangoUrl.reverse('ids_projects:get-parts-api', [name, uuid, offset]), {
				params: {'object_id': uuid}
			});
		};

		return services;
	}

})();