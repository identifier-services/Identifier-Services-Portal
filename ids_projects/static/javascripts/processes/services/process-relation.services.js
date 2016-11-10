(function(){
	'use strict';

	angular
		.module('idsApp.processes.services')
		.factory('ProcessRelations', ProcessRelations);

	ProcessRelations.$inject = ['$http', 'djangoUrl'];
	
	function ProcessRelations($http, djangoUrl) {
		var services = {};

		services.getRelatedEntities = function(uuid) {
			console.log('in the process services');
			return $http.get(djangoUrl.reverse('ids_projects:process-api', [uuid]), {
				params: {'object_id': uuid}
			});
		};

		return services;
	}

})();