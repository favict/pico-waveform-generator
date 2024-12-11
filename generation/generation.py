# Arbitrary waveform generator for Rasberry Pi Pico
# Requires 8-bit R2R DAC on pins 0-7. Works for R=1kOhm
# Achieves 125Msps when running 125MHz clock
# Rolf Oldeman, 13/2/2021. CC BY-NC-SA 4.0 licence
# Sourced from: https://www.instructables.com/Arbitrary-Wave-Generator-With-the-Raspberry-Pi-Pic/
# Modified by Fabio Vione, March 2024

from generation.constants import ParamNames, WaveformEntries
from generation.waveforms import WaveformParams
from machine import Pin, mem32, freq
from rp2 import PIO, StateMachine, asm_pio
from array import array
from math import floor
from uctypes import addressof

DMA_BASE = 0x50000000
CH0_READ_ADDR = DMA_BASE + 0x000
CH0_WRITE_ADDR = DMA_BASE + 0x004
CH0_TRANS_COUNT = DMA_BASE + 0x008
CH0_CTRL_TRIG = DMA_BASE + 0x00C
CH0_AL1_CTRL = DMA_BASE + 0x010
CH1_READ_ADDR = DMA_BASE + 0x040
CH1_WRITE_ADDR = DMA_BASE + 0x044
CH1_TRANS_COUNT = DMA_BASE + 0x048
CH1_CTRL_TRIG = DMA_BASE + 0x04C
CH1_AL1_CTRL = DMA_BASE + 0x050

PIO0_BASE = 0x50200000
PIO0_TXF0 = PIO0_BASE + 0x10
PIO0_SM0_CLKDIV = PIO0_BASE + 0xC8


# state machine that just pushes bytes to the pins
@asm_pio(
    out_init=(
        PIO.OUT_HIGH,
        PIO.OUT_HIGH,
        PIO.OUT_HIGH,
        PIO.OUT_HIGH,
        PIO.OUT_HIGH,
        PIO.OUT_HIGH,
        PIO.OUT_HIGH,
        PIO.OUT_HIGH,
    ),
    out_shiftdir=PIO.SHIFT_RIGHT,
    autopull=True,
    pull_thresh=32,
)
def stream():
    out(pins, 8)


def stop_dma_transfer():
    mem32[CH0_AL1_CTRL] = 0
    mem32[CH1_AL1_CTRL] = 0


def start_dma_transfer(data_array, word_count):
    # disable the DMAs to prevent corruption while writing
    stop_dma_transfer()
    # setup first DMA which does the actual transfer
    mem32[CH0_READ_ADDR] = addressof(data_array)
    mem32[CH0_WRITE_ADDR] = PIO0_TXF0
    mem32[CH0_TRANS_COUNT] = word_count
    IRQ_QUIET = 0x1  # do not generate an interrupt
    TREQ_SEL = 0x00  # wait for PIO0_TX0
    CHAIN_TO = 1  # start channel 1 when done
    RING_SEL = 0
    RING_SIZE = 0  # no wrapping
    INCR_WRITE = 0  # for write to array
    INCR_READ = 1  # for read from array
    DATA_SIZE = 2  # 32-bit word transfer
    HIGH_PRIORITY = 1
    EN = 1
    CTRL0 = (
        (IRQ_QUIET << 21)
        | (TREQ_SEL << 15)
        | (CHAIN_TO << 11)
        | (RING_SEL << 10)
        | (RING_SIZE << 9)
        | (INCR_WRITE << 5)
        | (INCR_READ << 4)
        | (DATA_SIZE << 2)
        | (HIGH_PRIORITY << 1)
        | (EN << 0)
    )
    mem32[CH0_AL1_CTRL] = CTRL0

    # setup second DMA which reconfigures the first channel
    p = array("I", [0])
    p[0] = addressof(data_array)
    mem32[CH1_READ_ADDR] = addressof(p)
    mem32[CH1_WRITE_ADDR] = CH0_READ_ADDR
    mem32[CH1_TRANS_COUNT] = 1
    IRQ_QUIET = 0x1  # do not generate an interrupt
    TREQ_SEL = 0x3F  # no pacing
    CHAIN_TO = 0  # start channel 0 when done
    RING_SEL = 0
    RING_SIZE = 0  # no wrapping
    INCR_WRITE = 0  # single write
    INCR_READ = 0  # single read
    DATA_SIZE = 2  # 32-bit word transfer
    HIGH_PRIORITY = 1
    EN = 1
    CTRL1 = (
        (IRQ_QUIET << 21)
        | (TREQ_SEL << 15)
        | (CHAIN_TO << 11)
        | (RING_SEL << 10)
        | (RING_SIZE << 9)
        | (INCR_WRITE << 5)
        | (INCR_READ << 4)
        | (DATA_SIZE << 2)
        | (HIGH_PRIORITY << 1)
        | (EN << 0)
    )
    mem32[CH1_CTRL_TRIG] = CTRL1


def evaluate_waveform(waveform, parameters, position):
    amplitude_multiplier, sum_offset, phase_modulation = (
        1.0,
        0.5,  # 0.5 to center the waveform around
        0.0,
    )

    if "phasemod" in waveform:
        phase_modulation = evaluate_waveform(waveform["phasemod"], parameters, position)

    if "mult" in waveform:
        amplitude_multiplier = evaluate_waveform(waveform["mult"], parameters, position)

    if "sum" in waveform:
        sum_offset = evaluate_waveform(waveform["sum"], parameters, position)

    position = (
        position * parameters.get("replicate", 1)
        - parameters.get("phase", 0)
        - phase_modulation
    )
    position = position - floor(position)  # reduce position to 0.0-1.0 range

    base_amplitude = parameters.get(ParamNames.AMPLITUDE, 1.0)

    value = waveform["function"](position, parameters)
    value = value * base_amplitude * amplitude_multiplier
    value = value + parameters.get("offset", 0) + sum_offset
    return value


def start_waveform_generation(buffer, waveform_type, parameters, max_sample_count):
    MIN_VALUE = 0
    MAX_VALUE = 255
    RESOLUTION = 256
    MAX_CLOCK_DIVIDER = 65535
    CLOCK_DIVIDER_BASE_SHIFT_AMOUNT = 16
    FRACTIONAL_CLOCK_DIVIDER_SHIFT_AMOUNT = 8
    SAMPLE_ALIGNMENT_FACTOR = 4
    FRACTIONAL_ROUNDING_OFFSET = 0.5

    target_frequency = parameters.get(
        ParamNames.FREQUENCY, WaveformParams.FREQUENCY.min
    )
    # Determine clock division to accommodate the waveform frequency within the buffer capacity
    clock_division_factor = freq() / (target_frequency * max_sample_count)

    if clock_division_factor < 1.0:
        # If the clock cannot be sped up, increase the number of waveform cycles in the buffer
        waveform_duplication_factor = int(1.0 / clock_division_factor)
        effective_sample_count = (
            int(
                (
                    max_sample_count
                    * clock_division_factor
                    * waveform_duplication_factor
                    + FRACTIONAL_ROUNDING_OFFSET
                )
                / SAMPLE_ALIGNMENT_FACTOR
            )
            * SAMPLE_ALIGNMENT_FACTOR
        )
        clock_divider_setting = 1
    else:
        # Apply integer clock division to match the waveform frequency and buffer capacity
        clock_divider_setting = int(clock_division_factor) + 1
        effective_sample_count = (
            int(
                (
                    max_sample_count * clock_division_factor / clock_divider_setting
                    + FRACTIONAL_ROUNDING_OFFSET
                )
                / SAMPLE_ALIGNMENT_FACTOR
            )
            * SAMPLE_ALIGNMENT_FACTOR
        )
        waveform_duplication_factor = 1

    # Populate the buffer with the generated waveform data
    for sample_index in range(effective_sample_count):
        normalized_sample_position = (
            waveform_duplication_factor
            * (sample_index + FRACTIONAL_ROUNDING_OFFSET)
            / effective_sample_count
        )
        sample_value = evaluate_waveform(
            waveform_type, parameters, normalized_sample_position
        )
        sample_scaled = int(RESOLUTION * sample_value)
        sample_clamped = max(MIN_VALUE, min(MAX_VALUE, sample_scaled))
        buffer[sample_index] = sample_clamped

    # Set the clock divider for the Programmable I/O to match the required waveform generation rate
    clock_divider_integer_part = min(clock_divider_setting, MAX_CLOCK_DIVIDER)
    clock_divider_fractional_part = 0  # Use integer division for stability

    shifted_clock_divider_integer = (
        clock_divider_integer_part << CLOCK_DIVIDER_BASE_SHIFT_AMOUNT
    )
    shifted_clock_divider_fractional = (
        clock_divider_fractional_part << FRACTIONAL_CLOCK_DIVIDER_SHIFT_AMOUNT
    )

    mem32[PIO0_SM0_CLKDIV] = (
        shifted_clock_divider_integer | shifted_clock_divider_fractional
    )

    # Initiate the transfer of the generated waveform to the output device
    word_count = int(effective_sample_count / SAMPLE_ALIGNMENT_FACTOR)
    start_dma_transfer(buffer, word_count)


class WaveformGenerator:
    def __init__(self, maxnsamp=4096):
        self.maxnsamp = maxnsamp
        self.current_buffer_index = 0
        self.buffer = {}
        self.buffer[0] = bytearray(self.maxnsamp)
        self.buffer[1] = bytearray(self.maxnsamp)
        self.state_machine = StateMachine(0, stream, out_base=Pin(0))
        self.state_machine.active(1)

    def _switch_buffer(self):
        self.current_buffer_index = (self.current_buffer_index + 1) % 2

    def start(self, waveform):
        parameters = {
            param.name: param.current_value
            for param in waveform[WaveformEntries.PARAMS]
        }
        self._switch_buffer()
        start_waveform_generation(
            self.buffer[self.current_buffer_index], waveform, parameters, self.maxnsamp
        )

    def stop(self):
        stop_dma_transfer()
