(function() {
	'use strict';

	angular
		.module('idsApp.probes.services')
		.factory('ProbeRelations', ProbeRelations);

	ProbeRelations.$inject = ['$http', 'djangoUrl'];

	function ProbeRelations($http, djangoUrl) {
		var services = {};

		services.getRelatedInputsTo = function(uuid, offset) {			
			return $http.get(djangoUrl.reverse('ids_projects:get-inputs-to-api', [uuid, offset]), {
				params: {'object_id': uuid}
			});
		}

		return services;
	};

})();