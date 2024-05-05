# Arbitrary Waveform Generator for Raspberry Pi Pico

![AWG1](https://github.com/favict/pico-waveform-generator/assets/45994341/214f8207-6e9a-46ef-97db-b80b4f082a4b)

## Introduction

This project implements a menu control to [Rolf Oldeman's AWG design](https://www.instructables.com/Arbitrary-Wave-Generator-With-the-Raspberry-Pi-Pic/).

It uses 3 buttons and a 2x16 LCD display.

## Usage

1. Clone the repository.
2. Match the parameters for buttons and display to your implementation in `control/control.py`:

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

3. Copy the project onto the Raspberry Pi Pico using your preferred method.
4. The generation will start automatically.

## Next steps

- [ ] Make the display update regularly while setting numeric parameters, so the user can get feedback in real-time;
- [ ] Improve main screen real state usage to fit all permutations of possible parameters.
