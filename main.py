from control.button import switch_power_supply_to_pwm
from generation.constants import SYSTEM_FREQUENCY
from generation.generation import WaveformGenerator
from utils.helpers import menu_state_tracker
import utime
import gc
from machine import freq
from control.control import Control


def main():
    control = Control(display_on=True, buttons_on=True)
    control.update_display()
    wave = control.menu.current_waveform

    generator = WaveformGenerator()
    generator.start(wave)

    has_menu_changed = menu_state_tracker(control.menu)

    while True:
        try:
            control.check_buttons()
            if control.menu.current_page_index == 0 and has_menu_changed():
                new_wave = control.menu.current_waveform
                generator.stop()
                gc.collect()
                generator.start(new_wave)
            utime.sleep_ms(100)
        except KeyboardInterrupt:
            generator.stop()
            break

    generator.stop()


if __name__ == "__main__":
    freq(SYSTEM_FREQUENCY)
    switch_power_supply_to_pwm()
    gc.collect()
    main()
