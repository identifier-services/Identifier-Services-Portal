/**
* ProejctRelationViewController
* @namespace idsApp.projects.controllers
*/

(function() {
	'use strict';

	angular
		.module('idsApp.projects.controllers')
		.controller('ProejctRelationViewController', ProejctRelationViewController);

	ProejctRelationViewController.$inject = ['$scope'];

	/**
	* @namespace ProejctRelationViewController
	*/

	function ProejctRelationViewController($scope) {
		console.log("project relation view controller");		
	}

})();