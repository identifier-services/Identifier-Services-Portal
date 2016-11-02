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
		var project_uuid = '3176432264224379366-242ac1111-0001-012';
		Relationships.getRelatedEntities(project_uuid).then(function(response){
			console.log(response);
			$scope.specimens = response.data.specimens;
			$scope.probes = response.data.probes;
			$scope.processes = response.data.processes;
			$scope.data = response.data.data;
			$scope.datasets = response.data.datasets;	
		});		
	}

})();