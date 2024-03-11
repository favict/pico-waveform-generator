class WaveformControl:
    def __init__(
        self,
        name,
        short_name,
        min=0.0,
        default=0.0,
        max=0.0,
        step=0.0,
        unit="",
        options=None,
        dynamic_step=False,
        check_interval=300,
    ):
        self.name = name
        self.short_name = short_name
        self.min = min
        self.default = default
        self.max = max
        self.step = step
        self.unit = unit
        self.options = options if options else []
        self.current_value = options[0] if options else default if default else min
        self.dynamic_step = dynamic_step
        self.check_interval = check_interval

    def _update_value(self, direction, press_duration):
        """Update the current value in a specified direction ('increase' or 'decrease') based on press duration."""
        if self.options:
            index = self.options.index(self.current_value)
            new_index = (
                (index + 1) % len(self.options)
                if direction == "increase"
                else (index - 1) % len(self.options)
            )
            self.current_value = self.options[new_index]
        else:
            while press_duration >= 0:
                dynamic_step = self.update_step_size(press_duration)
                if direction == "increase":
                    self.current_value = min(
                        self.current_value + dynamic_step, self.max
                    )
                else:  # direction == 'decrease'
                    self.current_value = max(
                        self.current_value - dynamic_step, self.min
                    )
                self.current_value = round(self.current_value, 1)
                press_duration -= self.check_interval

    def update_step_size(self, press_duration):
        """Determine the step size based on the press duration, ensuring it does not exceed one order of magnitude less than max."""
        max_dynamic_step = int(max(1, self.max / 10))
        dynamic_step = self.step * 10 ** (press_duration // 1000)
        return min(dynamic_step, max_dynamic_step)

    def increase(self, press_duration=0):
        """Increase the current value based on press duration."""
        self._update_value("increase", press_duration)

    def decrease(self, press_duration=0):
        """Decrease the current value based on press duration."""
        self._update_value("decrease", press_duration)
