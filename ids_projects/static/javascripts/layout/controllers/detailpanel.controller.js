(function(){
	'use strict';
		
	angular
		.module('idsApp.layout.controllers')
		.controller('DetailPanelController', DetailPanelController);

	DetailPanelController.$inject = ['$scope','djangoUrl','Details'];

	/*
	* @namespace DetailPanelController
	*/
	function DetailPanelController($scope, djangoUrl, Details) {
		
		// $scope.title = "Specimen";
		$scope.object = {};
		
		$scope.$watch('uuid', function (){
			Details.get($scope.uuid).then(function(response){
				console.log(response);
				$scope.title = response.data.name;
				
				for (var key in response.data.value) {
					var leading = key.substring(0,1);
					if (leading != '_') {
						$scope.object[key] = response.data.value[key];					
					}
				}			
			});				
		});

		
	}

})();