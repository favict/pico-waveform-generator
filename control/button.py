import utime
from machine import Pin


def switch_power_supply_to_pwm():
    # set GP23 to high to switch Pico power supply from PFM to PWM to reduce noise
    Pin(23, Pin.OUT).value(1)


class ButtonControl:
    def __init__(self, pin, mode=Pin.IN, pull=Pin.PULL_UP):
        self.pin = Pin(pin, mode=mode, pull=pull)
        self.button_press_start = None
        self.press_detected = False

    def check_pressed(self):
        current_state = self.pin.value()
        current_time = utime.ticks_ms()

        # If the button is currently pressed and wasn't already in the pressed state
        if current_state == 0 and self.button_press_start is None:
            self.button_press_start = current_time
            self.press_detected = True

        # If the button is released and was previously detected as pressed
        elif current_state == 1 and self.press_detected:
            if self.button_press_start is not None:
                press_duration = current_time - self.button_press_start
                self.button_press_start = None
                self.press_detected = False
                return True, press_duration
            else:
                # Reset for next press detection
                self.press_detected = False

        # Default return when no press/release detected
        return False, 0
