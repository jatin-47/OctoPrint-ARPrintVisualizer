# coding=utf-8
from __future__ import absolute_import
import threading
import subprocess
import os
import time
import requests
import flask
import cv2
import octoprint.plugin
from octoprint.schema.webcam import Webcam, WebcamCompatibility
from octoprint.webcams import WebcamNotAbleToTakeSnapshotException

class ARPrintVisualizerPlugin(octoprint.plugin.StartupPlugin,
                              octoprint.plugin.ShutdownPlugin,
                              octoprint.plugin.SettingsPlugin,
                              octoprint.plugin.TemplatePlugin,
                              octoprint.plugin.AssetPlugin,
                            #   octoprint.plugin.BlueprintPlugin,
                            #   octoprint.plugin.WebcamProviderPlugin
                              ):
    
    def __init__(self):
        # self._capture_mutex = threading.Lock()
        self._process = None
        self._cam_server_path = "\OctoCam\\ar_cam.py"

    ##########################################################################################################

    ##~~ StartupPlugin mixin
    def on_startup(self, host, port):
        """
        Starts the AR Cam Flask server on octoprint server startup
        """
        try:
            log_file = open("flask_log.txt", "w")            
            script_abs_path = os.path.dirname(__file__) + self._cam_server_path
            self._process = subprocess.Popen(["python", script_abs_path], stdout=log_file, stderr=log_file)

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

    # ##~~ SettingsPlugin mixin
    # def get_settings_defaults(self):
    #     """
    #     Returns the default settings for the plugin
    #     """
    #     return dict(
    #         stream=""
    #     )

    def on_settings_save(self, data):
        """
        If you wanna do something when a particular setting is updated
        """
        old_stream=self._settings.get(["stream"])
        
        octoprint.plugin.SettingsPlugin.on_settings_save(self,data)
        new_stream=self._settings.get(["stream"])


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

__plugin_name__ = "ARPrintVisualizer"
__plugin_pythoncompat__ = ">=3,<4"  # Only Python 3

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = ARPrintVisualizerPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
