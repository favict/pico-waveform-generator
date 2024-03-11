import utime


def get_params_values_string(current_params):
    return " ".join(
        [
            f"{param.short_name}{format_numeric_value(param.current_value, param.unit if hasattr(param, 'unit') else '')}"
            for param in current_params
        ]
    )


def format_numeric_value(number_string, unit=None):
    # Convert the input to a float and handle rounding/integer conversion
    number = float(number_string)
    if number % 1 == 0:
        number = int(number)
    else:
        number = round(number, 1)

    # Determine the appropriate magnitude and unit
    suffix = ""
    if number >= 1_000_000:
        number /= 1_000_000
        suffix = "M"
    elif number >= 1_000:
        number /= 1_000
        suffix = "K"

    # Adjust formatting for the new number
    if isinstance(number, int) or number % 1 == 0:
        formatted_number = f"{number}"
    else:
        formatted_number = f"{number:.1f}"

    # Add commas for the integer part if necessary
    integer_part, _, decimal_part = formatted_number.partition(".")
    integer_part_with_commas = "{:,}".format(int(integer_part)).replace(",", ",")

    # Reconstruct the number with the decimal part if it exists
    if decimal_part:
        formatted_number = f"{integer_part_with_commas}.{decimal_part}"
    else:
        formatted_number = integer_part_with_commas

    # Append the unit if provided
    print(formatted_number, unit, suffix)
    if unit:
        formatted_number += suffix
        formatted_number += unit

    return formatted_number


def menu_state_tracker(menu):
    debounce_time_ms = 5000

    previous_state = {
        "current_waveform_name": menu.current_waveform["name"],
        "current_params": {
            param.name: param.current_value for param in menu.current_params
        },
        "last_change_time": utime.ticks_ms(),
    }

    def has_changed():
        nonlocal previous_state

        current_time = utime.ticks_ms()
        if (
            utime.ticks_diff(current_time, previous_state["last_change_time"])
            < debounce_time_ms
        ):
            return False

        current_waveform_name = menu.current_waveform["name"]
        waveform_changed = (
            current_waveform_name != previous_state["current_waveform_name"]
        )

        current_params_state = {
            param.name: param.current_value for param in menu.current_params
        }
        params_changed = current_params_state != previous_state["current_params"]

        if waveform_changed or params_changed:
            previous_state["current_waveform_name"] = current_waveform_name
            previous_state["current_params"] = current_params_state
            previous_state["last_change_time"] = current_time
            return True
        return False

    return has_changed
