/**
* DataRelationViewController
* @namespace idsApp.data.controllers
*/

(function() {
	'use strict';

	angular
		.module('idsApp.data.controllers')
		.controller('DataRelationViewController', DataRelationViewController);

	DataRelationViewController.$inject = ['$scope'];

	/**
	* @namespace DataRelationViewController
	*/

	function DataRelationViewController($scope) {
		console.log("Data relation view controller");		
	}

})();