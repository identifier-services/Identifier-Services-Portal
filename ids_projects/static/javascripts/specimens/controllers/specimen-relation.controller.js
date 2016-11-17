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
		// var specimen_uuid = '3539497870490791450-242ac1111-0001-012';

		$scope.$watch('specimen_uuid', function() {
			SpecimenRelations.getRelatedInputsTo($scope.specimen_uuid, 0).then(function(response) {				
				$scope.is_input_to = response.data;
			});

			SpecimenRelations.getRelatedOutputsOf($scope.specimen_uuid, 0).then(function(response) {
				$scope.is_output_of = response.data;
			});
		});
		

	}

})();