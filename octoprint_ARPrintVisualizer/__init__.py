# coding=utf-8
from __future__ import absolute_import
import octoprint.plugin

class ARPrintVisualizerPlugin(octoprint.plugin.SettingsPlugin,
                              octoprint.plugin.TemplatePlugin,
                              octoprint.plugin.AssetPlugin):

    ##~~ SettingsPlugin mixin
    def get_settings_defaults(self):
        return {
            # put your plugin's default settings here
        }

    ##~~ TemplatePlugin mixin
    def get_template_configs(self):
        return [
            dict(type="navbar", custom_bindings=False),
            dict(type="settings", custom_bindings=False)
        ]

    ##~~ AssetPlugin mixin
    def get_assets(self):
        return {
            "js": ["js/ARPrintVisualizer.js"],
            "css": ["css/ARPrintVisualizer.css"],
            "less": ["less/ARPrintVisualizer.less"]
        }

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
