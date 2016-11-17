(function(){
	'use strict';

	angular
		.module('idsApp.datasets.services')
		.factory('DatasetRelations', DatasetRelations);

	DatasetRelations.$inject = ['$http', 'djangoUrl'];

	function DatasetRelations($http, djangoUrl) {
		var services = {};

		services.getRelatedParts = function(name, uuid, offset) {			
			return $http.get(djangoUrl.reverse('ids_projects:get-parts-api', [name, uuid, offset]), {
				params: {'object_id': uuid}
			});
		};

		return services;
	}

})();