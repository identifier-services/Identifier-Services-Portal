(function(){
	'use strict';

	angular
		.module('idsApp.processes.services')
		.factory('ProcessRelations', ProcessRelations);

	ProcessRelations.$inject = ['$http', 'djangoUrl'];
	
	function ProcessRelations($http, djangoUrl) {
		var services = {};

		services.getRelatedInputs = function(uuid, offset) {			
			return $http.get(djangoUrl.reverse('ids_projects:get-inputs-api', [uuid, offset]), {
				params: {'object_id': uuid}
			});
		};

		services.getRelatedOutputs = function(uuid, offset) {
			return $http.get(djangoUrl.reverse('ids_projects:get-outputs-api', [uuid, offset]), {
				params: {'object_id': uuid}
			});
		}

		return services;
	}

})();