/**
* DatasetRelationViewController
* @namespace idsApp.datasets.controllers
*/

(function() {
	'use strict';

	angular
		.module('idsApp.datasets.controllers')
		.controller('DatasetRelationViewController', DatasetRelationViewController);

	DatasetRelationViewController.$inject = ['$scope', 'djangoUrl', 'DatasetRelations'];

	/**
	* @namespace DatasetRelationViewController
	*/

	function DatasetRelationViewController($scope, djangoUrl, DatasetRelations) {
		console.log("dataset relation view controller");		

		var dataset_uuid = '2512897196004601370-242ac1111-0001-012';
		DatasetRelations.getRelatedEntities(dataset_uuid).then(function(response) {
			console.log(response);
			$scope.identifiers = response.data.identifiers;
			$scope.data = response.data.data;
		});

	}

})();