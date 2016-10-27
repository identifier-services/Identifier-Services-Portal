/**
* DatasetRelationViewController
* @namespace idsApp.datasets.controllers
*/

(function() {
	'use strict';

	angular
		.module('idsApp.datasets.controllers')
		.controller('DatasetRelationViewController', DatasetRelationViewController);

	DatasetRelationViewController.$inject = ['$scope'];

	/**
	* @namespace DatasetRelationViewController
	*/

	function DatasetRelationViewController($scope) {
		console.log("dataset relation view controller");		
	}

})();