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
        self.isDetecting = ko.observable(false);
        self.isErrorDetected = ko.observable(false);

        self.onBeforeBinding = function() {
        }

        self.toggleDetection = function() {
            self.isDetecting(!self.isDetecting());

            if (self.isDetecting()) {
                $("#detection").text("Stop Error Detection");
                $.ajax({
                    url: "/plugin/ARPrintVisualizer/detection/start",
                    type: "GET",
                    dataType: "json",
                    contentType: "application/json; charset=utf-8",
                    success: function(data) {
                        console.log(data);
                    },
                    error: function(error) {
                        console.log(error);
                    }
                });
            } else {
                $("#detection").text("Start Error Detection");
                $.ajax({
                    url: "/plugin/ARPrintVisualizer/detection/stop",
                    type: "GET",
                    dataType: "json",
                    contentType: "application/json; charset=utf-8",
                    success: function(data) {
                        console.log(data);
                    },
                    error: function(error) {
                        console.log(error);
                    }
                });
            }
        }
        
        self.onDataUpdaterPluginMessage = function(plugin, data) {
            if (plugin != "ARPrintVisualizer") {
                return;
            }

            if (data.type == "error") {
                new PNotify({
                    title: 'Error Detected',
                    text: data.error,
                    type: 'error',
                    hide: false
                });

                $("#detection").text("Start Error Detection");
                self.isDetecting(false);
                self.isErrorDetected(true);
            }

        }
              
           
    }
        
  
    OCTOPRINT_VIEWMODELS.push({
        construct: ArprintvisualizerViewModel,
        dependencies: [ "settingsViewModel"],
        elements: [ "#settings_plugin_ARPrintVisualizer", "#tab_plugin_ARPrintVisualizer"]
    });
});
