(function(){
	'use strict';

	angular
		.module('idsApp.specimens.services')
		.factory('SpecimenRelations', SpecimenRelations);


	SpecimenRelations.$inject = ['$http', 'djangoUrl'];

	function SpecimenRelations($http, djangoUrl) {
		var services = {};

		services.getRelatedEntities = function(uuid) {
			console.log('in the specimen service');
			return $http.get(djangoUrl.reverse('ids_projects:specimen-api', [uuid]), {
				params: {'object_id': uuid}
			});
		};

		return services;
	}
})();