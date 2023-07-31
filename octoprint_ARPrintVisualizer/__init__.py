# coding=utf-8
from __future__ import absolute_import
import os
import sys
import requests
import time
import flask
import threading
import subprocess
import octoprint.plugin

class ARPrintVisualizerPlugin(octoprint.plugin.StartupPlugin,
                              octoprint.plugin.ShutdownPlugin,
                              octoprint.plugin.SettingsPlugin,
                              octoprint.plugin.TemplatePlugin,
                              octoprint.plugin.AssetPlugin,
                              octoprint.plugin.BlueprintPlugin,
                              ):
    
    def __init__(self):
        self._process = None
        self._thread = None
        self._thread_stop = threading.Event()
        self._cam_server_path = "\OctoAR\\ar_cam.py"

    ##########################################################################################################

    ##~~ StartupPlugin mixin
    def on_startup(self, host, port):
        """
        Starts the AR Cam Flask server on octoprint server startup
        """
        try:
            log_file = open("flask_log.txt", "w")            
            script_abs_path = os.path.dirname(__file__) + self._cam_server_path
            self._process = subprocess.Popen([sys.executable, script_abs_path], stdout=log_file, stderr=log_file)

            time.sleep(2)
            if self._process.poll() is None:
                print("Cam server started successfully.")
            else:
                print("Error while starting the Flask server. Check the log file for details.")
            log_file.close()
        except Exception as e:
            self._logger.info("ARPrintVisualizer failed to start")
            self._logger.info(e)
        return

    ##~~ ShutdownPlugin mixin
    def on_shutdown(self):
        """
        Stops the AR Cam Flask server on octoprint server shutdown
        """
        if self._process is not None and self._process.poll() is None:
            self._logger.info("Stopping the cam server...")
            self._process.terminate()
            self._process.wait()
    
    ##########################################################################################################
    
    ##~~ TemplatePlugin mixin
    def get_template_configs(self):
        return [
            {
                "type": "settings",
                "template": "ARPrintVisualizer_settings.jinja2",
                "custom_bindings": True
            },
            {
                "type": "tab",
                "template": "ARPrintVisualizer_tab.jinja2",
                "custom_bindings": True
            }
        ]
    
    ##~~ AssetPlugin mixin
    def get_assets(self):
        return {
            "js": ["js/ARPrintVisualizer.js"],
            "css": ["css/ARPrintVisualizer.css"],
            "less": ["less/ARPrintVisualizer.less"]
        }
    
    ##########################################################################################################

    ##~~ SettingsPlugin mixin
    def get_settings_defaults(self):
        """
        Returns the initial default settings for the plugin. Can't skip it!
        """
        return dict(
            stream="",
            aruco_dict="DICT_6X6_250",
        )
    
    ##########################################################################################################

    ##~~ BlueprintPlugin mixin
    @octoprint.plugin.BlueprintPlugin.route("/detection/start", methods=["GET"])
    def start_detection(self):
        """
        Starts the error detection process
        """
        self._logger.info("Starting the error detection process...")
        
        self._thread_stop.clear()
        if not self._thread or not self._thread.is_alive():
            self._thread = threading.Thread(target=self.error_detection, daemon=True)
            self._thread.start()

        return flask.jsonify("Evaluation started!")


    @octoprint.plugin.BlueprintPlugin.route("/detection/stop", methods=["GET"])
    def stop_detection(self):
        """
        Stops the error detection process
        """
        self._logger.info("Stopping the error detection process...")
        if self._thread is not None and self._thread.is_alive() and not self._thread_stop.is_set():
            self._thread_stop.set()
            self._thread.join()

        return flask.jsonify("Evaluation stopped!") 
    
    @octoprint.plugin.BlueprintPlugin.route("/correct", methods=["GET"])
    def correct_print(self):
        """
        Corrects the print by inserting a patch
        """
        self._logger.info("Correcting the print...")
        #get the current x,y,z position of the print head
        data = self._printer.get_current_data()
        self._logger.info(data)




        self._printer.resume_print()
        return flask.jsonify("Print corrected!")

    ##########################################################################################################
    
    ##~~ Main logic
    def error_detection(self):
        """
        Detects errors in the print and returns the error type
        """
        while not self._thread_stop.is_set():
            r = requests.get(f'http://127.0.0.1:27100/snapshot/{self._settings.get(["stream"])}')
            if r.status_code == 200:
                self._logger.info("Snapshot received")
                img = r.content
                with open("snapshot.jpg", "wb") as f:
                    f.write(img)

                prediciton = self.algo_error_detection(img)
                if prediciton is True:
                    self._logger.info("Error detected!")
                    self._printer.pause_print()
                    self._plugin_manager.send_plugin_message(self._identifier, dict(type="error", error="THIS error was detected and the printer is paused! Take necessary action and resume the print."))
                    self._thread_stop.set()

                time.sleep(2)
            else:
                break
            
    def algo_error_detection(self, img):
        """
        Runs the error detection algorithm on the image
        """



        return True


    ##########################################################################################################

    ##~~ Softwareupdate hook
    def get_update_information(self):
        """
        Define the configuration for your plugin to use with the Software Update
        Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
        for details.
        """
        return {
            "ARPrintVisualizer": {
                "displayName": "ARPrintVisualizer",
                "displayVersion": self._plugin_version,

                # version check: github repository
                "type": "github_release",
                "user": "jatin-47",
                "repo": "OctoPrint-ARPrintVisualizer",
                "current": self._plugin_version,

                # update method: pip
                #"pip": "https://github.com/jatin-47/OctoPrint-ARPrintVisualizer/archive/{target_version}.zip",
            }
        }

__plugin_name__ = "AR Print Visualizer"
__plugin_pythoncompat__ = ">=3,<4"  # Only Python 3

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = ARPrintVisualizerPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
