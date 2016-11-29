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
		// pagination
		// an object is necessary to avoid scope conflict
		// http://stackoverflow.com/questions/12618342/ng-model-does-not-update-controller-value
		$scope.pagination = {};
		$scope.pagination.maxSize = 5;
		$scope.pagination.totalItems = 0;		
		$scope.pagination.maxPage = 1;
		$scope.pagination.currentPage = 1;
		$scope.pagination.offset = 0;		
		$scope.pagination.end = false;
		$scope.probes = [];

		$scope.updateTotalItems = function(increment) {
			if (increment == 0) {
				$scope.pagination.end = true;
			}

		    $scope.pagination.totalItems += increment;		    

		    if ($scope.pagination.totalItems % 10 == 0) {		    	
				$scope.pagination.maxPage = $scope.pagination.totalItems / 10;	
			}
			else {				
				$scope.pagination.maxPage = $scope.pagination.totalItems / 10 + 1;
			}
	
			$scope.pagination.offset += increment;
		};

		$scope.pageChanged = function() {					    		    
		    if ($scope.pagination.currentPage == $scope.pagination.maxPage && !$scope.pagination.end)  {
		    	// request more data
		    	Relationships.getRelatedEntities('idsvc.probe', $scope.project_uuid, $scope.pagination.offset).then(function(response){
		    		console.log("requesting more data...");
		    		$scope.probes = $scope.probes.concat(response.data);
					$scope.updateTotalItems(response.data.length);
		    	});
		    }

		    var start = ($scope.pagination.currentPage - 1) * 10;
		    var end = $scope.pagination.currentPage * 10 ;		    
		    $scope.list = $scope.probes.slice(start, end);
		};			


		// data pagination
		// NOTE: NEEDS TO CONSIDER BETTER WAY TO RESUE PAGINATION 		
		
		$scope.$watch('project_uuid', function () {
		    console.log($scope.project_uuid); 

		    // probes
			Relationships.getRelatedEntities('idsvc.probe', $scope.project_uuid, $scope.pagination.offset).then(function(response){
	    		console.log("requesting more data...");
	    		$scope.probes = $scope.probes.concat(response.data);
				$scope.updateTotalItems(response.data.length);

				var start = ($scope.pagination.currentPage - 1) * 10;
			    var end = $scope.pagination.currentPage * 10 ;
			    console.log("start: " + start + " end: " + end);
			    $scope.list = $scope.probes.slice(start, end);
	    	});

			// specimens
			Relationships.getRelatedEntities('idsvc.specimen', $scope.project_uuid, 0).then(function(response){
				$scope.specimens = response.data;			
			});

			Relationships.getRelatedEntities('idsvc.process', $scope.project_uuid, 0).then(function(response){
				$scope.processes = response.data;			
			});

			// datasets
			Relationships.getRelatedEntities('idsvc.dataset', $scope.project_uuid, 0).then(function(response){
				$scope.datasets = response.data;		
			});

			// data
			Relationships.getRelatedEntities('idsvc.data', $scope.project_uuid, 0).then(function(response){
				$scope.data = response.data;			
			});
		});
	}

})();