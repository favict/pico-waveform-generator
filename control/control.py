from control.signal import WaveformControl
from generation.constants import WaveformEntries
from generation.waveforms import WAVEFORMS, WaveformParams
from utils.helpers import get_params_values_string

from control.button import ButtonControl

class ControlType:
    NONE = 0
    BUTTONS = 1

class Page:
    def __init__(self, name, setting):
        self.name = name
        self.setting = setting


class Menu:
    def __init__(self, default_pages, optional_pages, waveforms, default_waveform=None):
        self.default_pages = default_pages
        self.optional_pages = optional_pages
        self.active_pages = default_pages
        self.current_page_index = 0
        self.current_page = self.active_pages[self.current_page_index]
        self.waveforms = waveforms
        self.default_waveform = default_waveform or waveforms[0]
        self.current_waveform = self.default_waveform
        self.current_params = self.current_waveform[WaveformEntries.PARAMS]

    def get_current_waveform(self):
        for page in self.default_pages:
            if page.name == "Waveform":
                waveform = self.default_waveform
                for waveform in WAVEFORMS:
                    if waveform["name"] == page.setting.current_value:
                        break
                return waveform
        return self.default_waveform

    def update_pages_list(self):
        self.current_waveform = self.get_current_waveform()
        self.current_params = self.current_waveform["params"]
        signal_params_names = [param.name for param in self.current_waveform["params"]]
        params_pages = [
            page for page in self.optional_pages if page.name in signal_params_names
        ]
        self.active_pages = self.default_pages + params_pages

    def go_to_next_page(self):
        self.update_pages_list()
        self.current_page_index = (self.current_page_index + 1) % len(self.active_pages)
        self.current_page = self.active_pages[self.current_page_index]


class Control:
    def __init__(self, display=None, control_type=ControlType.NONE):

        self.display = display

        if control_type == ControlType.BUTTONS:
            self.main_button = ButtonControl(pin=19)
            self.increase_button = ButtonControl(pin=18)
            self.decrease_button = ButtonControl(pin=20)
        else:
            self.main_button = None
            self.increase_button = None
            self.decrease_button = None

        self.main_page = Page("Main", setting=None)
        self.waveform_page = Page(
            "Waveform",
            setting=WaveformControl(
                "Waveform",
                short_name="Wf",
                options=[waveform["name"] for waveform in WAVEFORMS],
            ),
        )
        self.menu = self.setup_menu()

    def update_display(self):
        if not self.display:
            return

        lines = []
        if self.menu.current_page.name == self.main_page.name:
            lines = [
                f"{self.menu.current_waveform['name']} wave",
                get_params_values_string(self.menu.current_params),
            ]
        else:
            lines = [
                f"{self.menu.current_page.setting.name}:",
                f"> {self.menu.current_page.setting.current_value}",
            ]
        self.display.render(lines)
        return

    def check_buttons(self):
        if self.main_button:
            default_value = (False, 0)
            main_pressed, _ = (
                self.main_button.check_pressed() if self.main_button else default_value
            )
            increase_pressed, increase_duration = (
                self.increase_button.check_pressed()
                if self.increase_button
                else default_value
            )
            decrease_pressed, decrease_duration = (
                self.decrease_button.check_pressed()
                if self.decrease_button
                else default_value
            )

            if not (main_pressed or increase_pressed or decrease_pressed):
                return

            if increase_pressed and decrease_pressed:
                self.display.toggle_backlight() if self.display else None
                return

            if main_pressed:
                self.menu.go_to_next_page()
                self.update_display()
                return

            if increase_pressed and self.menu.current_page.setting:
                self.menu.current_page.setting.increase(
                    press_duration=increase_duration
                )
                self.update_display()
                return

            if decrease_pressed and self.menu.current_page.setting:
                self.menu.current_page.setting.decrease(
                    press_duration=decrease_duration
                )
                self.update_display()
                return

    def setup_menu(self):
        default_pages = [self.main_page, self.waveform_page]
        optional_pages = list(
            Page(signal_param.name, setting=signal_param)
            for signal_param in list(WaveformParams.__dict__.values())
            if isinstance(signal_param, WaveformControl)
        )
        menu = Menu(default_pages, optional_pages, WAVEFORMS)
        return menu
