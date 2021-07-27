# coding=utf-8
from __future__ import absolute_import

from enum import Enum, auto

import octoprint.plugin
import octoprint.printer

from octoprint_gpio_button_box.button_handler import ButtonHandler
from octoprint_gpio_button_box.led import LedManager


class PrinterState(Enum):
    Disconnected = auto()
    Operational = auto()
    Printing = auto()
    Paused = auto()
    Pausing = auto()
    Cancelling = auto()
    Error = auto()


class GPIOButtonBox(octoprint.plugin.EventHandlerPlugin):
    def __init__(self):
        super().__init__()
        self.start_button = None
        self.pause_button = None
        self.power_button = None
        self.led_manager = None

    @property
    def psucontrol_helpers(self):
        return self._plugin_manager.get_helpers("psucontrol")

    def on_plugin_enabled(self):
        self.start_button = ButtonHandler(2, on_short_click=self.on_resume_click)
        self.pause_button = ButtonHandler(3, on_short_click=self.on_pause_click, on_long_click=self.on_cancel_click)
        self.power_button = ButtonHandler(4, on_short_click=self.on_power_toggle, on_long_click=self.on_power_stop)
        self.led_manager = LedManager(self)

    def on_plugin_disabled(self):
        self.start_button.close()
        self.pause_button.close()

    def on_event(self, event, payload):
        if event == "plugin_psucontrol_psu_state_changed":
            if payload["isPSUOn"]:
                self._logger.info("PSU enabled")
            else:
                self._logger.info("PSU disabled")
        elif event == "PrinterStateChanged":
            self.led_manager.update_printer_state()

    def on_resume_click(self):
        self._printer.resume_print()

    def on_pause_click(self):
        if self._printer.is_paused() or self._printer.is_pausing():
            return
        self._printer.pause_print()

    def on_cancel_click(self):
        self._printer.cancel_print()

    def on_power_toggle(self):
        if self.get_psu_on():
            if self._printer.is_paused() or self._printer.is_pausing() or self._printer.is_printing() or self._printer.is_cancelling():
                return
            self.psucontrol_helpers["turn_psu_off"]()
        else:
            self.psucontrol_helpers["turn_psu_on"]()

    def on_power_stop(self):
        self.psucontrol_helpers["turn_psu_off"]()

    def get_psu_on(self):
        self.psucontrol_helpers["get_psu_state"]()

    def get_state(self) -> PrinterState:
        if self._printer.is_error(): return PrinterState.Error
        if self._printer.is_paused(): return PrinterState.Paused
        if self._printer.is_pausing(): return PrinterState.Pausing
        if self._printer.is_cancelling(): return PrinterState.Cancelling
        if self._printer.is_printing(): return PrinterState.Printing
        if self._printer.is_operational(): return PrinterState.Operational
        return PrinterState.Disconnected

    ##~~ Softwareupdate hook

    def get_update_information(self):
        # Define the configuration for your plugin to use with the Software Update
        # Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
        # for details.
        return {
            "gpio_button_box": {
                "displayName": "GPIO Button Box Plugin",
                "displayVersion": self._plugin_version,

                # version check: github repository
                "type": "github_release",
                "user": "dominik-korsa",
                "repo": "OctoPrint-GPIO-Button-Box",
                "current": self._plugin_version,

                # update method: pip
                "pip": "https://github.com/dominik-korsa/OctoPrint-GPIO-Button-Box/archive/{target_version}.zip",
            }
        }


# Starting with OctoPrint 1.4.0 OctoPrint will also support to run under Python 3 in addition to the deprecated
# Python 2. New plugins should make sure to run under both versions for now. Uncomment one of the following
# compatibility flags according to what Python versions your plugin supports!
# __plugin_pythoncompat__ = ">=2.7,<3" # only python 2
__plugin_pythoncompat__ = ">=3,<4"  # only python 3


# __plugin_pythoncompat__ = ">=2.7,<4" # python 2 and 3


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = GPIOButtonBox()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
