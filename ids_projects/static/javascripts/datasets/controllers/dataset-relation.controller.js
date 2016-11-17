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

		// var dataset_uuid = '2512897196004601370-242ac1111-0001-012';
		$scope.$watch('dataset_uuid', function() {
			DatasetRelations.getRelatedParts('idsvc.identifier', $scope.dataset_uuid, 0).then(function(response) {						
				$scope.identifiers = response.data;			
			});

			DatasetRelations.getRelatedParts('idsvc.data', $scope.dataset_uuid, 0).then(function(response) {
				$scope.data = response.data;
			});
		});		
	}

})();