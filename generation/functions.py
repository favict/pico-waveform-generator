from generation.waveforms import ParamNames
from math import sin, pi, sqrt, exp
from random import random
from generation.waveforms import ParamNames


def sine(x: float, params: dict) -> float:
    return sin(2 * pi * x)


def square(x: float, params: dict) -> float:
    duty_cycle = params[ParamNames.DUTY_CYCLE]
    if x < duty_cycle / 100.0:
        return 1
    else:
        return -1


def triangle(x: float, params: dict) -> float:
    x = x % 1  # Normalize x to ensure it's within a 0 to 1 range for the cycle
    if x < 0.5:
        return 4 * x - 1  # Linearly increase from -1 to 1 in the first half
    else:
        return -4 * x + 3


def sawtooth(x: float, params: dict) -> float:
    return 2 * (x - round(x))


def sinc(x: float, params: dict) -> float:
    bandwidth = params[ParamNames.BANDWIDTH]
    center_shift = 0.5
    if x == center_shift:
        return 1.0
    else:
        return sin((x - center_shift) / bandwidth) / ((x - center_shift) / bandwidth)


def gaussian(x: float, params: dict) -> float:
    standard_deviation = params[ParamNames.STANDARD_DEVIATION]
    center_shift = 0.5
    return exp(-((x - center_shift) ** 2) / (2 * standard_deviation**2))


def exponential(x: float, params: dict) -> float:
    time_constant = params[ParamNames.TIME_CONSTANT]
    return exp(-x / time_constant)


def pulse(x: float, params: dict) -> float:
    rise_time = params[ParamNames.RISE_TIME]
    up_time = params[ParamNames.UP_TIME]
    fall_time = params[ParamNames.FALL_TIME]
    total_time = rise_time + up_time + fall_time
    if x < rise_time:
        return x / rise_time
    if x < rise_time + up_time:
        return 1.0
    if x < total_time:
        return 1.0 - (x - rise_time - up_time) / fall_time
    return 0.0


def white_noise(x: float, params: dict) -> float:
    quality = params[ParamNames.QUALITY]
    balance_factor = 0.5  # random() output is by default uniformly distributed in the range [0, 1], this shifts it to [-0.5, 0.5]
    normalization_factor = sqrt(12 / quality)

    return (
        sum([random() - balance_factor for _ in range(quality)]) * normalization_factor
    )
