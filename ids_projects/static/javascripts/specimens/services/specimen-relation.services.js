(function(){
	'use strict';

	angular
		.module('idsApp.specimens.services')
		.factory('SpecimenRelations', SpecimenRelations);


	SpecimenRelations.$inject = ['$http', 'djangoUrl'];

	function SpecimenRelations($http, djangoUrl) {
		var services = {};

		services.getRelatedInputsTo = function(uuid, offset) {			
			return $http.get(djangoUrl.reverse('ids_projects:get-inputs-to-api', [uuid, offset]), {
				params: {'object_id': uuid}
			});
		};

		services.getRelatedOutputsOf = function(uuid, offset) {
			return $http.get(djangoUrl.reverse('ids_projects:get-outputs-of-api', [uuid, offset]), {
				params: {'object_id': uuid}
			});
		}

		return services;
	}
})();