/**
* ProcessRelationViewController
* @namespace idsApp.processes.controllers
*/

(function() {
	'use strict';

	angular
		.module('idsApp.processes.controllers')
		.controller('ProcessRelationViewController', ProcessRelationViewController);

	ProcessRelationViewController.$inject = ['$scope'];

	/**
	* @namespace ProcessRelationViewController
	*/

	function ProcessRelationViewController($scope) {
		console.log("process relation view controller");		
	}

})();