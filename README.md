# Arbitrary Waveform Generator for Raspberry Pi Pico

## Introduction

This project implements Rolf Oldeman's [Arbitrary Wave Generator With the Raspberry Pi Pico](https://www.instructables.com/Arbitrary-Wave-Generator-With-the-Raspberry-Pi-Pic/) design, adding a menu to control it with 3 buttons and a 2x16 matrix LCD display.

## Usage

1. Clone the repository.
2. Update the parameters for buttons and display in `control/control.py`, if necessary to match your implementation:

```python
...
        if buttons_on:
            main_button = ButtonControl(pin=19)
            increase_button = ButtonControl(pin=18)
            decrease_button = ButtonControl(pin=20)

        if display_on:
            display = Display(
                i2c_bus=1,
                sda_pin=26,
                scl_pin=27,
                i2c_frequency=400000,
                i2c_address=0x3F,
                line_count=2,
                column_count=16,
            )
...
```

3. Connect your Raspberry Pi Pico to your computer via USB.
4. Copy the project onto the Raspberry Pi Pico using your preferred method.
5. The generator will start automatically.

## Limitations/Next steps

- Make the display update regularly while setting numeric parameters, so the user can get feedback in real-time;
- Improve main screen real state usage to fit all permutations of possible parameters.
