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
        self.onAfterBinding = function() {
        let imgElement = document.getElementById('ARCam');
        let src = new cv.Mat(height, width, cv.CV_8UC4);
        let dst = new cv.Mat(height, width, cv.CV_8UC1);
        let cap = new cv.VideoCapture(imgElement);
        const FPS = 30;
        function processVideo() {
            try {
                if (!streaming) {
                    // clean and stop.
                    src.delete();
                    dst.delete();
                    return;
                }
                let begin = Date.now();
                // start processing.
                cap.read(src);
                cv.cvtColor(src, dst, cv.COLOR_RGBA2GRAY);
                cv.imshow('outcanvas', dst);
                // schedule the next one.
                let delay = 1000/FPS - (Date.now() - begin);
                setTimeout(processVideo, delay);
            } catch (err) {
                utils.printError(err);
            }
            // schedule the first one.
        }
        setTimeout(processVideo, 0);
        
        };

          
           
    }
        
  
    OCTOPRINT_VIEWMODELS.push({
        construct: ArprintvisualizerViewModel,
        dependencies: [ "settingsViewModel"],
        elements: [ "#mjpg_container"]
    });
});
