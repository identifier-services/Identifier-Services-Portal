/**
* ProjectRelationViewController
* @namespace idsApp.projects.controllers
*/

(function() {
	'use strict';

	angular
		.module('idsApp.projects.controllers')
		.controller('ProjectRelationViewController', ProjectRelationViewController);

	ProjectRelationViewController.$inject = ['$scope', 'djangoUrl','Relationships'];

	/**
	* @namespace ProjectRelationViewController
	*/

	function ProjectRelationViewController($scope, djangoUrl, Relationships) {
		
		console.log("project relation view controller");
		Relationships.getRelatedEntities('3176432264224379366-242ac1111-0001-012').then(function(response){
			console.log(response);
			$scope.specimens = response.data.specimens;
			$scope.probes = response.data.probes;
			$scope.processes = response.data.processes;
			$scope.data = response.data.data;
			$scope.datasets = response.data.datasets;	
		});		
	}

})();