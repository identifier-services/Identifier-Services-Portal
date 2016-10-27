/**
* SpecimenRelationViewController
* @namespace idsApp.specimens.controllers
*/

(function() {
	'use strict';

	angular
		.module('idsApp.specimens.controllers')
		.controller('SpecimenRelationViewController', SpecimenRelationViewController);

	SpecimenRelationViewController.$inject = ['$scope'];

	/**
	* @namespace SpecimenRelationViewController
	*/

	function SpecimenRelationViewController($scope) {
		console.log("Specimen relation view controller");		
	}

})();