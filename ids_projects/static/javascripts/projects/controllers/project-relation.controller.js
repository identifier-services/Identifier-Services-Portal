/**
* ProjectRelationViewController
* @namespace idsApp.projects.controllers
*/

(function() {
	'use strict';

	angular
		.module('idsApp.projects.controllers', ['ngAnimate', 'ngSanitize','ui.bootstrap'])
		.controller('ProjectRelationViewController', ProjectRelationViewController);

	ProjectRelationViewController.$inject = ['$scope','$log','djangoUrl','Relationships'];

	/**
	* @namespace ProjectRelationViewController
	*/

	function ProjectRelationViewController($scope, $log, djangoUrl, Relationships) {
		
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

		// pagination
		// an object is necessary to avoid scope conflict
		// http://stackoverflow.com/questions/12618342/ng-model-does-not-update-controller-value
		$scope.pagination = {}
		$scope.pagination.maxSize = 5;
		$scope.pagination.totalItems = 100;		

		$scope.setPage = function (pageNo) {
		    $scope.pagination.currentPage = pageNo;
		};

		$scope.pageChanged = function() {		    
		    console.log($scope.pagination.currentPage);
		};					
		
	}

})();