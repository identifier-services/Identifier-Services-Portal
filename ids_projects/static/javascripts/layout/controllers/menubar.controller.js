/**
* MenubarController
* @namespace idsApp.layout.controllers
*/

(function() {
	'use strict';

	angular
		.module('idsApp.layout.controllers')
		.controller('MenuBarController', MenubarController);


	MenubarController.$inject = ['$scope'];

	/**
	* @namespace MenuBarController
	*/

	function MenubarController($scope) {		
		$scope.actions = {
			select_data: true,
			add_data: false,
			create_dataset: true,
			define_specimen: true,
			define_sequencing: true,
			define_assembly: false,
			define_analysis: false,
			relate_to_speicmen: true,
			relate_to_process: true,
			add_input_data: true,
			add_output_data: false,
			request_doi: true,
			request_ark: false,
			define_ish: true,
			define_probe: true,
			add_images: false
		};		
	}


})();