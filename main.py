import gc
import utime
from machine import freq

from control.button import switch_power_supply_to_pwm
from control.control import Control, ControlType
from display.display import DisplayLCD, DisplayOLED
from generation.constants import SYSTEM_FREQUENCY
from generation.generation import WaveformGenerator
from utils.helpers import menu_state_tracker


def main():
    lcd_display = DisplayLCD(
        i2c_bus=1,
        sda_pin=26,
        scl_pin=27,
        i2c_frequency=400000,
        i2c_address=0x3F,
        line_count=2,
        column_count=16,
    )
    # oled_display = DisplayOLED(
    #     width=128,
    #     height=32,
    #     rotate_180=True,
    #     i2c_bus=0,
    #     sda_pin=8,
    #     scl_pin=9,
    # )
    control = Control(lcd_display, ControlType.BUTTONS)
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
