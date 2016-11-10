(function(){
	'use strict';

	angular
		.module('idsApp.data.services')
		.factory('DataRelations', DataRelations);

	DataRelations.$inject = ['$http', 'djangoUrl'];

	function DataRelations($http, djangoUrl) {
		var services = {};

		services.getRelatedEntities = function(uuid) {
			console.log("in the data services");
			return $http.get(djangoUrl.reverse('ids_projects:data-api', [uuid]), {
				params: {'object_id': uuid}
			});

		};

		return services;
	}

})();