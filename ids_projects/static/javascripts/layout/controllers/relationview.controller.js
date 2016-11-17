/**
* RelationViewController
* @namespace idsApp.layout.controllers
*/

(function() {
	'use strict';

	angular
		.module('idsApp.layout.controllers')
		.controller('RelationViewController', RelationViewController);

	RelationViewController.$inject = ['$scope'];

	/**
	* @namespace RelationViewController
	*/

	function RelationViewController($scope) {				
		$scope.$watch('entity', function () {			
			console.log("Entity type: " + $scope.entity);					
		});		
	}

})();