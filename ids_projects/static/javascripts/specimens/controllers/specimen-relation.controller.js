/**
* SpecimenRelationViewController
* @namespace idsApp.specimens.controllers
*/

(function() {
	'use strict';

	angular
		.module('idsApp.specimens.controllers')
		.controller('SpecimenRelationViewController', SpecimenRelationViewController);

	SpecimenRelationViewController.$inject = ['$scope', 'djangoUrl', 'SpecimenRelations'];

	/**
	* @namespace SpecimenRelationViewController
	*/

	function SpecimenRelationViewController($scope, djangoUrl, SpecimenRelations) {

		console.log("Specimen relation view controller");		
		var specimen_uuid = '1862119081942979046-242ac1111-0001-012';
		SpecimenRelations.getRelatedEntities(specimen_uuid).then(function(response) {
			console.log(response);
			$scope.is_input_of = response.data.is_input_of;
		});

	}

})();