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
        self.cam_url=ko.observable();

        

        self.onBeforeBinding = function() {
            self.cam_url(self.settingsViewModel.settings.plugins.ARPrintVisualizer.stream());
        }

        self.onEventSettingsUpdated = function(payload) {
            self.cam_url(self.settingsViewModel.settings.plugins.ARPrintVisualizer.stream());
        }
              
           
    }
        
  
    OCTOPRINT_VIEWMODELS.push({
        construct: ArprintvisualizerViewModel,
        dependencies: [ "settingsViewModel"],
        elements: [ "#settings_plugin_ARPrintVisualizer"]
    });
});
