# coding=utf-8
from __future__ import absolute_import
import threading
import requests
import octoprint.plugin
from octoprint.schema.webcam import Webcam, WebcamCompatibility
from octoprint.webcams import WebcamNotAbleToTakeSnapshotException

class ARPrintVisualizerPlugin(octoprint.plugin.SettingsPlugin,
                              octoprint.plugin.TemplatePlugin,
                              octoprint.plugin.AssetPlugin,
                              octoprint.plugin.WebcamProviderPlugin):
    
    def __init__(self):
        self._capture_mutex = threading.Lock()

    ##~~ AssetPlugin mixin
    def get_assets(self):
        return {
            "js": ["js/ARPrintVisualizer.js",
                   "js/opencv.js"],
            "css": ["css/ARPrintVisualizer.css"],
            "less": ["less/ARPrintVisualizer.less"]
        }
    
    ##~~ TemplatePlugin mixin
    def get_template_configs(self):
        return [
            {
                "type": "webcam",
                "template": "ARPrintVisualizer_webcam.jinja2",
                "custom_bindings": True,
                "suffix": "_real"
            }
        ]
    ##~~ SettingsPlugin mixin
    def get_settings_version(self):
        return 1
    
    def get_settings_defaults(self):
        return dict(
            stream="http://172.30.250.143:8081/video.mjpg",
            snapshot="http://localhost:8888/out.jpg",
            flipH=True,
            cacheBuster=True,
            snapshotSslValidation=True,
            snapshotTimeout=5
        )

    ##~~ WebcamProviderPlugin mixin
    def get_webcam_configurations(self):
        stream = self._settings.get(["stream"])
        snapshot = self._settings.get(["snapshot"])
        flipH = self._settings.get_boolean(["flipH"])
        cacheBuster = self._settings.get_boolean(["cacheBuster"])
        snapshotSslValidation = self._settings.get_boolean(["snapshotSslValidation"])

        try:
            streamTimeout = int(self._settings.get(["streamTimeout"]))
        except Exception:
            streamTimeout = 5

        try:
            snapshotTimeout = int(self._settings.get(["snapshotTimeout"]))
        except Exception:
            snapshotTimeout = 5

        return [
            Webcam(
                name="ARCam",
                displayName="AR Webcam",
                flipH=flipH,
                snapshotDisplay=snapshot,
                canSnapshot=self._can_snapshot(),
                compat=WebcamCompatibility(
                    stream=stream,
                    streamTimeout=streamTimeout,
                    cacheBuster=cacheBuster,
                    snapshot=snapshot,
                    snapshotTimeout=snapshotTimeout,
                    snapshotSslValidation=snapshotSslValidation,
                ),
                extras=dict(
                    stream=stream,
                    streamTimeout=streamTimeout,
                    cacheBuster=cacheBuster,
                ),
            ),
        ]

    def _can_snapshot(self):
        snapshot = self._settings.get(["snapshot"])
        return snapshot is not None and snapshot.strip() != ""

    def take_webcam_snapshot(self, _):
        snapshot_url = self._settings.get(["snapshot"])
        if not self._can_snapshot():
            raise WebcamNotAbleToTakeSnapshotException("ARCam")

        with self._capture_mutex:
            self._logger.debug(f"Capturing image from {snapshot_url}")
            r = requests.get(
                snapshot_url,
                stream=True,
                timeout=self._settings.get_int(["snapshotTimeout"]),
                verify=self._settings.get_boolean(["snapshotSslValidation"]),
            )
            r.raise_for_status()
            return r.iter_content(chunk_size=1024)


    ##~~ Softwareupdate hook
    def get_update_information(self):
        # Define the configuration for your plugin to use with the Software Update
        # Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
        # for details.
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
                "pip": "https://github.com/jatin-47/OctoPrint-ARPrintVisualizer/archive/{target_version}.zip",
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
