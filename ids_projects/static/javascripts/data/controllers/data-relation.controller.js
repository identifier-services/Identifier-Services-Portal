/**
* DataRelationViewController
* @namespace idsApp.data.controllers
*/

(function() {
	'use strict';

	angular
		.module('idsApp.data.controllers')
		.controller('DataRelationViewController', DataRelationViewController);

	DataRelationViewController.$inject = ['$scope', 'djangoUrl', 'DataRelations'];

	/**
	* @namespace DataRelationViewController
	*/

	function DataRelationViewController($scope, djangoUrl, DataRelations) {
		console.log("Data relation view controller");

		var data_uuid = '4322106814629932570-242ac1111-0001-012';
		DataRelations.getRelatedEntities(data_uuid).then(function(response) {
			console.log(response);
			$scope.is_input_to = response.data.is_input_to;
			$scope.is_output_of = response.data.is_output_of;
		});
	}

})();