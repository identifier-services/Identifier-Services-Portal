/**
* ProbeRelationViewController
* @namespace idsApp.probes.controllers
*/

(function() {
	'use strict';

	angular
		.module('idsApp.probes.controllers')
		.controller('ProbeRelationViewController', ProbeRelationViewController);

	ProbeRelationViewController.$inject = ['$scope'];

	/**
	* @namespace ProbeRelationViewController
	*/

	function ProbeRelationViewController($scope) {
		console.log("probe relation view controller");		
	}

})();