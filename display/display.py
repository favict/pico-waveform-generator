from machine import I2C, Pin
from display.lcd_driver import I2cLcd
from display.ssd1306 import SSD1306_I2C

class DisplayLCD:
    def __init__(
        self,
        i2c_bus,
        sda_pin,
        scl_pin,
        i2c_frequency,
        i2c_address,
        line_count,
        column_count,
    ):
        self.i2c_lcd = I2C(
            i2c_bus, sda=Pin(sda_pin), scl=Pin(scl_pin), freq=i2c_frequency
        )
        self.lcd = I2cLcd(self.i2c_lcd, i2c_address, line_count, column_count)
        self.backlight_on = True
        self.line_count = line_count
        self.column_count = column_count

        self.lcd.backlight_on() if self.backlight_on else self.lcd.backlight_off()

    def render(self, lines):
        self.lcd.clear()
        for i, line in enumerate(lines[: self.line_count]):
            cropped_line = line[: self.column_count]
            self.lcd.move_to(0, i)
            self.lcd.putstr(cropped_line)

    def toggle_backlight(self):
        self.backlight_on = not self.backlight_on
        if self.backlight_on:
            self.lcd.backlight_on()
        else:
            self.lcd.backlight_off()

class DisplayOLED:
    def __init__(self, width, height, i2c_bus, sda_pin, scl_pin):
        i2c = I2C(i2c_bus, sda=Pin(sda_pin), scl=Pin(scl_pin))
        self.oled = SSD1306_I2C(width, height, i2c)

    def render(self, lines):
        self.oled.fill(0)
        for i, line in enumerate(lines):
            self.oled.text(line, 0, i * 11)
        self.oled.show()
