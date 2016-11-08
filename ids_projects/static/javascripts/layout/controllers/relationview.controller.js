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
		$scope.text = 'This is relation view.';
		$scope.entity = 'project';		
	}

})();