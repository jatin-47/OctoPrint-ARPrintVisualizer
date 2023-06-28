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
        
        
        function convertImageToGray(img) {
            let dst = new cv.Mat();
            cv.cvtColor(img, dst, cv.COLOR_RGBA2GRAY, 0);
            return dst;
        }

        self.onBeforeBinding = function() {
            self.cam_url(self.settingsViewModel.settings.plugins.ARPrintVisualizer.stream());
            self.flipH = self.settingsViewModel.settings.plugins.ARPrintVisualizer.flipH();
        }
              
           
    }
        
  
    OCTOPRINT_VIEWMODELS.push({
        construct: ArprintvisualizerViewModel,
        dependencies: [ "settingsViewModel"],
        elements: [ "#mjpg_container"]
    });
});
