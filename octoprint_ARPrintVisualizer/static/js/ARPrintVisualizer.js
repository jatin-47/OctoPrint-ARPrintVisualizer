/*
 * View model for OctoPrint-Arprintvisualizer
 *
 * Author: Jatin Saini
 * License: AGPLv3
 */
$(function() {
    function ArprintvisualizerViewModel(parameters) {
        var self = this;

        self.settingsViewModel = parameters[0];

        self.onBeforeBinding = function() {
        }

        self.onEventSettingsUpdated = function(payload) {
        }
              
           
    }
        
  
    OCTOPRINT_VIEWMODELS.push({
        construct: ArprintvisualizerViewModel,
        dependencies: [ "settingsViewModel"],
        elements: [ "#settings_plugin_ARPrintVisualizer", "#tab_plugin_ARPrintVisualizer"]
    });
});
