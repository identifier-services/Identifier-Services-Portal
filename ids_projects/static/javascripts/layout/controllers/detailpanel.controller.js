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
		$scope.title = "this is a test title";		
		$scope.object = {};
		
		Details.get('1862119081942979046-242ac1111-0001-012').then(function(response){			
			for (var key in response.data) {
				var leading = key.substring(0,1);
				if (leading != '_') {
					$scope.object[key] = response.data[key];					
				}
			}			
		});				
	}

})();