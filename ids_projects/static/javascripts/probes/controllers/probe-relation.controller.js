/**
* ProbeRelationViewController
* @namespace idsApp.probes.controllers
*/

(function() {
	'use strict';

	angular
		.module('idsApp.probes.controllers')
		.controller('ProbeRelationViewController', ProbeRelationViewController);

	ProbeRelationViewController.$inject = ['$scope', 'djangoUrl', 'ProbeRelations'];

	/**
	* @namespace ProbeRelationViewController
	*/

	function ProbeRelationViewController($scope, djangoUrl, ProbeRelations) {
		console.log("probe relation view controller");		
		var probe_uuid = '2842383520227267046-242ac1111-0001-012';

		ProbeRelations.getRelatedEntities(probe_uuid).then(function(response) {
			console.log(response);
			$scope.is_input_to = response.data.is_input_to;
		});
	}

})();