/**
* ProcessRelationViewController
* @namespace idsApp.processes.controllers
*/

(function() {
	'use strict';

	angular
		.module('idsApp.processes.controllers')
		.controller('ProcessRelationViewController', ProcessRelationViewController);

	ProcessRelationViewController.$inject = ['$scope', 'djangoUrl', 'ProcessRelations'];

	/**
	* @namespace ProcessRelationViewController
	*/

	function ProcessRelationViewController($scope, djangoUrl, ProcessRelations) {

		console.log("process relation view controller");		
		// var process_uuid = '8000958787788739046-242ac1111-0001-012';

		$scope.$watch('process_uuid', function() {
			ProcessRelations.getRelatedInputs($scope.process_uuid, 0).then(function(response) {			
				$scope.inputs = response.data;			
			});

			ProcessRelations.getRelatedOutputs($scope.process_uuid, 0).then(function(response) {			
				$scope.outputs = response.data;
			});
		});
		

	}

})();