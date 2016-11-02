(function(){
	'use strict';

	angular
		.module('idsApp.datasets.services')
		.factory('DatasetRelations', DatasetRelations);

	DatasetRelations.$inject = ['$http', 'djangoUrl'];

	function DatasetRelations($http, djangoUrl) {
		var services = {};

		services.getRelatedEntities = function(uuid) {
			console.log('in the dataset services');

			return $http.get(djangoUrl.reverse('ids_projects:dataset-api', [uuid]), {
				params: {'object_id': uuid}
			});
		};

		return services;
	}

})();