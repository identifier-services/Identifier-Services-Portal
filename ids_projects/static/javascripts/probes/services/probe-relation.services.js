(function() {
	'use strict';

	angular
		.module('idsApp.probes.services')
		.factory('ProbeRelations', ProbeRelations);

	ProbeRelations.$inject = ['$http', 'djangoUrl'];

	function ProbeRelations($http, djangoUrl) {
		var services = {};

		services.getRelatedEntities = function(uuid) {
			console.log('in the probe services');
			return $http.get(djangoUrl.reverse('ids_projects:data-api', [uuid]), {
				params: {'object_id': uuid}
			});
		}

		return services;
	};

})();