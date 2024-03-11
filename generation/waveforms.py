from control.signal import WaveformControl
from generation.constants import (
    ParamNames,
    ParamShortNames,
    WaveformEntries,
    WaveformNames,
)

from generation.functions import (
    sine,
    square,
    triangle,
    sawtooth,
    pulse,
    sinc,
    gaussian,
    exponential,
    white_noise,
)


class WaveformParams:
    FREQUENCY = WaveformControl(
        ParamNames.FREQUENCY,
        ParamShortNames.FREQUENCY,
        min=20,
        default=15e4,
        max=20e6,
        step=1000,
        dynamic_step=True,
        unit="Hz",
    )
    AMPLITUDE = WaveformControl(
        ParamNames.AMPLITUDE,
        ParamShortNames.AMPLITUDE,
        min=0.1,
        default=0.5,
        max=5.0,
        step=0.1,
    )
    DUTY_CYCLE = WaveformControl(
        ParamNames.DUTY_CYCLE,
        ParamShortNames.DUTY_CYCLE,
        min=1,
        default=50,
        max=100,
        step=1,
        unit="%",
    )
    BANDWIDTH = WaveformControl(
        ParamNames.BANDWIDTH,
        ParamShortNames.BANDWIDTH,
        min=0.020,
        max=0.020,
        step=0.005,
        dynamic_step=True,
        unit="Hz",
    )
    STANDARD_DEVIATION = WaveformControl(
        ParamNames.STANDARD_DEVIATION,
        ParamShortNames.STANDARD_DEVIATION,
        min=0.01,
        max=10.0,
        step=0.01,
    )
    TIME_CONSTANT = WaveformControl(
        ParamNames.TIME_CONSTANT,
        ParamShortNames.TIME_CONSTANT,
        min=0.1,
        max=10.0,
        step=0.01,
    )
    OFFSET = WaveformControl(
        ParamNames.OFFSET,
        ParamShortNames.OFFSET,
        min=-5.0,
        max=5.0,
        step=0.1,
    )
    QUALITY = WaveformControl(
        ParamNames.QUALITY,
        ParamShortNames.QUALITY,
        min=1,
        max=100,
        step=1,
    )
    RISE_TIME = WaveformControl(
        ParamNames.RISE_TIME,
        ParamShortNames.RISE_TIME,
        min=0.2,
        max=1,
        step=0.1,
    )
    UP_TIME = WaveformControl(
        ParamNames.UP_TIME,
        ParamShortNames.UP_TIME,
        min=0.2,
        max=1,
        step=0.1,
    )
    FALL_TIME = WaveformControl(
        ParamNames.FALL_TIME,
        ParamShortNames.FALL_TIME,
        min=0.2,
        max=1,
        step=0.1,
    )


WAVEFORMS = [
    {
        WaveformEntries.NAME: WaveformNames.SINE,
        WaveformEntries.PARAMS: [WaveformParams.FREQUENCY, WaveformParams.AMPLITUDE],
        WaveformEntries.FUNCTION: sine,
    },
    {
        WaveformEntries.NAME: WaveformNames.SQUARE,
        WaveformEntries.PARAMS: [
            WaveformParams.FREQUENCY,
            WaveformParams.AMPLITUDE,
            WaveformParams.DUTY_CYCLE,
        ],
        WaveformEntries.FUNCTION: square,
    },
    {
        WaveformEntries.NAME: WaveformNames.TRIANGLE,
        WaveformEntries.PARAMS: [WaveformParams.FREQUENCY, WaveformParams.AMPLITUDE],
        WaveformEntries.FUNCTION: triangle,
    },
    {
        WaveformEntries.NAME: WaveformNames.SAWTOOTH,
        WaveformEntries.PARAMS: [WaveformParams.FREQUENCY, WaveformParams.AMPLITUDE],
        WaveformEntries.FUNCTION: sawtooth,
    },
    {
        WaveformEntries.NAME: WaveformNames.PULSE,
        WaveformEntries.PARAMS: [
            WaveformParams.RISE_TIME,
            WaveformParams.UP_TIME,
            WaveformParams.FALL_TIME,
        ],
        WaveformEntries.FUNCTION: pulse,
    },
    {
        WaveformEntries.NAME: WaveformNames.SINC,
        WaveformEntries.PARAMS: [
            WaveformParams.BANDWIDTH,
            WaveformParams.AMPLITUDE,
            WaveformParams.OFFSET,
        ],
        WaveformEntries.FUNCTION: sinc,
    },
    {
        WaveformEntries.NAME: WaveformNames.GAUSSIAN,
        WaveformEntries.PARAMS: [
            WaveformParams.STANDARD_DEVIATION,
            WaveformParams.AMPLITUDE,
            WaveformParams.OFFSET,
        ],
        WaveformEntries.FUNCTION: gaussian,
    },
    {
        WaveformEntries.NAME: WaveformNames.EXPONENTIAL,
        WaveformEntries.PARAMS: [
            WaveformParams.TIME_CONSTANT,
            WaveformParams.AMPLITUDE,
            WaveformParams.OFFSET,
        ],
        WaveformEntries.FUNCTION: exponential,
    },
    {
        WaveformEntries.NAME: WaveformNames.WHITE_NOISE,
        WaveformEntries.PARAMS: [WaveformParams.AMPLITUDE, WaveformParams.QUALITY],
        WaveformEntries.FUNCTION: white_noise,
    },
]
